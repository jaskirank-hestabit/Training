# src/memory/memory_store.py
import json, os
from datetime import datetime

class MemoryStore:
    def __init__(self, max_turns=5, log_path="logs/chat_logs.json"):
        self.max_turns = max_turns
        self.log_path  = log_path
        self.history   = []   # [{"role": ..., "content": ..., "timestamp": ...}]
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def add(self, role: str, content: str):
        entry = {"role": role, "content": content,
                 "timestamp": datetime.now().isoformat()}
        self.history.append(entry)
        # Keep last N full turns (user + assistant = 2 msgs per turn)
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-(self.max_turns * 2):]
        self._persist(entry)

    def get_history_text(self) -> str:
        """Formatted history for prompt injection (excludes current message)."""
        lines = []
        for msg in self.history[:-1]:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def get_messages(self):
        return list(self.history)

    def clear(self):
        self.history = []

    def _persist(self, entry):
        try:
            logs = []
            if os.path.exists(self.log_path):
                with open(self.log_path) as f:
                    logs = json.load(f)
            logs.append(entry)
            with open(self.log_path, "w") as f:
                json.dump(logs, f, indent=2)
        except Exception:
            pass