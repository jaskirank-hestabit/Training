import os
from datetime import datetime
from nexus_ai.config import NEXUS_CONFIG


class NexusLogger:
    def __init__(self, session: str = "default"):
        self.session  = session
        self.logs_dir = NEXUS_CONFIG["logs_dir"]
        os.makedirs(self.logs_dir, exist_ok=True)
        self.log_path = os.path.join(self.logs_dir, f"{session}.log")

    def log(self, agent: str, event: str, message: str = "") -> None:
        ts    = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        entry = f"[{ts}] [{agent}] [{event}] {message}\n"
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass  # never crash the pipeline over logging

    def read(self) -> str:
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""