import os
from dotenv import load_dotenv

load_dotenv()

try:
    import pyTigerGraph as tg
except Exception:
    tg = None

class TigerGraphClient:
    def __init__(self):
        self.host = os.getenv("TG_HOST", "")
        self.graph = os.getenv("TG_GRAPH", "HHGoaFraudGraph")
        self.token = os.getenv("TG_TOKEN", "")
        self.username = os.getenv("TG_USERNAME", "")
        self.password = os.getenv("TG_PASSWORD", "")
        self.conn = None

    @property
    def enabled(self):
        return bool(self.host and tg)

    def connect(self):
        if not self.enabled:
            return None
        if self.conn is None:
            kwargs = {"host": self.host, "graphname": self.graph}
            if self.token:
                kwargs["apiToken"] = self.token
            else:
                kwargs["username"] = self.username
                kwargs["password"] = self.password
            self.conn = tg.TigerGraphConnection(**kwargs)
        return self.conn

    def run_query(self, query_name, params=None):
        conn = self.connect()
        if not conn:
            return None
        return conn.runInstalledQuery(query_name, params or {})
