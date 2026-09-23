import argparse, os, pandas as pd

def norm(v):
    if pd.isna(v):
        return ""
    s = str(v).strip()
    return s[:-2] if s.endswith(".0") else s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", default="data/raw/HHGOA_IEEE")
    ap.add_argument("--out-dir", default="data/prepared")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    tx = os.path.join(args.raw_dir, "transactions.csv")
    identity = os.path.join(args.raw_dir, "identity.csv")
    closed = os.path.join(args.raw_dir, "closed_cases_history.csv")
    cases = os.path.join(args.raw_dir, "case_pack.csv")

    # Card IDs are customer_id-K1, K2, ... using the deterministic
    # sorted card2..card6 tuple rule used for this project.
    parts = []
    use = ["customer_id","card2","card3","card4","card5","card6"]
    for ch in pd.read_csv(tx, usecols=use, dtype="string", chunksize=100000):
        for c in use[1:]:
            ch[c] = ch[c].fillna("").map(norm)
        parts.append(ch.drop_duplicates())
    cards = pd.concat(parts, ignore_index=True).drop_duplicates()
    cards = cards.sort_values(use, na_position="first").reset_index(drop=True)
    cards["k_number"] = cards.groupby("customer_id").cumcount() + 1
    cards["card_id"] = cards["customer_id"] + "-K" + cards["k_number"].astype(str)
    cards[["customer_id","card_id","card2","card3","card4","card5","card6","k_number"]].to_csv(
        os.path.join(args.out_dir, "cards.csv"), index=False
    )
    customers = cards[["customer_id"]].drop_duplicates()
    customers["n_cards"] = customers["customer_id"].map(cards.groupby("customer_id").size())
    customers.to_csv(os.path.join(args.out_dir, "customers.csv"), index=False)

    # Device profiles + identity signals.
    cols = ["TransactionID","id_15","id_23","id_30","id_31","id_33","id_34","DeviceType","DeviceInfo"]
    chunks = []
    for ch in pd.read_csv(identity, usecols=cols, chunksize=150000):
        for c in cols[1:]:
            ch[c] = ch[c].astype("string").fillna("").str.strip()
        chunks.append(ch)
    ident = pd.concat(chunks, ignore_index=True)

    def device_key(r):
        vals = [r[c] if r[c] else "UNK" for c in ["DeviceInfo","id_30","id_31","id_33"]]
        return "" if all(x == "UNK" for x in vals) else "|".join(vals)

    ident["device_profile_id"] = ident.apply(device_key, axis=1)
    ident[ident.device_profile_id != ""][[
        "device_profile_id","DeviceInfo","id_30","id_31","id_33"
    ]].drop_duplicates().to_csv(
        os.path.join(args.out_dir, "device_profiles.csv"), index=False
    )
    ident[["TransactionID","device_profile_id","id_15","id_23","id_34","DeviceType"]].to_csv(
        os.path.join(args.out_dir, "identity_signals.csv"), index=False
    )

    # Closed-case tables.
    cc = pd.read_csv(closed, dtype="string")
    cc[[
        "case_id","customer_id","card_id","opened_at","closed_at","outcome",
        "pattern","first_fraud_txn_id","n_txns","exposure_usd",
        "report_filed","analyst_notes","actions_taken"
    ]].to_csv(os.path.join(args.out_dir, "closed_cases_core.csv"), index=False)

    txn_rows, card_rows = [], []
    for _, r in cc.iterrows():
        for x in str(r.get("txn_ids", "") or "").split("|"):
            if x and x != "nan":
                txn_rows.append((r["case_id"], x))
        for x in str(r.get("connected_card_ids", "") or "").split("|"):
            if x and x != "nan":
                card_rows.append((r["case_id"], x))
    pd.DataFrame(txn_rows, columns=["case_id","transaction_id"]).drop_duplicates().to_csv(
        os.path.join(args.out_dir, "closed_case_transactions.csv"), index=False
    )
    pd.DataFrame(card_rows, columns=["case_id","card_id"]).drop_duplicates().to_csv(
        os.path.join(args.out_dir, "closed_case_connected_cards.csv"), index=False
    )

    # Case pack is kept as the 20 benchmark cases.
    pd.read_csv(cases, dtype="string").to_csv(
        os.path.join(args.out_dir, "case_pack_prepared.csv"), index=False
    )

    print("Reference data prepared.")

if __name__ == "__main__":
    main()
