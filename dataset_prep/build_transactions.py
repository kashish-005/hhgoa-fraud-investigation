import argparse, os, pandas as pd

def norm(v):
    if pd.isna(v):
        return ""
    s = str(v).strip()
    return s[:-2] if s.endswith(".0") else s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", default="data/raw/HHGOA_IEEE")
    ap.add_argument("--prepared-dir", default="data/prepared")
    args = ap.parse_args()
    os.makedirs(args.prepared_dir, exist_ok=True)

    tx = os.path.join(args.raw_dir, "transactions.csv")
    cards = pd.read_csv(os.path.join(args.prepared_dir, "cards.csv"), dtype="string")
    identity = pd.read_csv(
        os.path.join(args.raw_dir, "identity.csv"),
        usecols=["TransactionID","id_15","id_23","id_30","id_31","id_33","id_34","DeviceType","DeviceInfo"],
        dtype="string"
    )

    def device_key(r):
        vals = [(r[c] or "UNK").strip() if isinstance(r[c], str) else "UNK"
                for c in ["DeviceInfo","id_30","id_31","id_33"]]
        return "" if all(x == "UNK" for x in vals) else "|".join(vals)

    for c in identity.columns[1:]:
        identity[c] = identity[c].fillna("").astype("string").str.strip()
    identity["device_profile_id"] = identity.apply(device_key, axis=1)
    devmap = identity[["TransactionID","device_profile_id"]].drop_duplicates()

    core_cols = [
        "TransactionID","TransactionDT","TransactionAmt","ProductCD","card2","card3",
        "card4","card5","card6","customer_id","ts","channel","risk_score",
        "addr1","addr2","dist1","dist2","P_emaildomain","R_emaildomain"
    ]
    sig_cols = ["TransactionID"] + [f"C{i}" for i in range(1,15)] + \
               [f"D{i}" for i in range(1,16)] + [f"M{i}" for i in range(1,10)]

    core_out = os.path.join(args.prepared_dir, "transactions_core.csv")
    sig_out = os.path.join(args.prepared_dir, "transactions_signals.csv")
    first_core = first_sig = True

    for ch in pd.read_csv(tx, usecols=sorted(set(core_cols + sig_cols)), chunksize=100000):
        for c in ["card2","card3","card4","card5","card6"]:
            ch[c] = ch[c].astype("string").fillna("").str.replace(r"\.0$", "", regex=True)

        m = ch.merge(
            cards[["customer_id","card_id","card2","card3","card4","card5","card6"]],
            on=["customer_id","card2","card3","card4","card5","card6"],
            how="left",
            validate="many_to_one"
        ).merge(devmap, on="TransactionID", how="left", validate="many_to_one")

        core = m[[
            "TransactionID","customer_id","card_id","ts","TransactionDT","TransactionAmt",
            "ProductCD","channel","risk_score","addr1","addr2","dist1","dist2",
            "P_emaildomain","R_emaildomain","device_profile_id"
        ]].copy()
        core["has_device_record"] = core["device_profile_id"].fillna("").ne("")
        core.to_csv(core_out, mode="w" if first_core else "a", header=first_core, index=False)

        m[sig_cols].to_csv(sig_out, mode="w" if first_sig else "a", header=first_sig, index=False)
        first_core = first_sig = False

    print("Transaction data prepared.")

if __name__ == "__main__":
    main()
