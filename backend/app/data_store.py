from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "prepared"

class LocalStore:
    def __init__(self):
        self.cases = pd.read_csv(DATA / "case_pack_prepared.csv", dtype="string")
        self.tx = pd.read_csv(DATA / "transactions_core.csv", dtype="string")
        self.cards = pd.read_csv(DATA / "cards.csv", dtype="string")
        self.customers = pd.read_csv(DATA / "customers.csv", dtype="string")
        self.devices = pd.read_csv(DATA / "device_profiles.csv", dtype="string")
        self.closed = pd.read_csv(DATA / "closed_cases_core.csv", dtype="string")
        self.closed_tx = pd.read_csv(DATA / "closed_case_transactions.csv", dtype="string")

    def case_list(self):
        return self.cases.fillna("").to_dict(orient="records")

    def case(self, case_id):
        x = self.cases[self.cases.case_id == case_id]
        return None if x.empty else x.iloc[0].fillna("").to_dict()

    def transaction(self, tid):
        x = self.tx[self.tx.TransactionID == str(tid)]
        return None if x.empty else x.iloc[0].fillna("").to_dict()

    def customer_history(self, customer_id, limit=100):
        x = self.tx[self.tx.customer_id == str(customer_id)].copy()
        x = x.sort_values("ts", ascending=False).head(limit)
        return x.fillna("").to_dict(orient="records")

    def card_transactions(self, card_id, limit=200):
        x = self.tx[self.tx.card_id == str(card_id)].copy()
        x = x.sort_values("ts", ascending=False).head(limit)
        return x.fillna("").to_dict(orient="records")

    def device_neighbors(self, device_id, limit=200):
        x = self.tx[self.tx.device_profile_id == str(device_id)].copy()
        x = x.sort_values("ts", ascending=False).head(limit)
        return x.fillna("").to_dict(orient="records")

    def region_neighbors(self, region_id, limit=200):
        x = self.tx[self.tx.addr1 == str(region_id)].copy()
        x = x.sort_values("ts", ascending=False).head(limit)
        return x.fillna("").to_dict(orient="records")
