# src/memory/memory_store.py
import json, os
from datetime import datetime

class MemoryStore:
    def __init__(self, max_turns=5, log_path="src/logs/chat_logs.json"):
        self.max_turns = max_turns
        self.log_path  = log_path
        self.history   = []
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self._load_existing()

    def _load_existing(self):
        try:
            if os.path.exists(self.log_path):
                with open(self.log_path) as f:
                    logs = json.load(f)
                self.history = logs[-(self.max_turns * 2):]
        except Exception:
            self.history = []

    def add(self, role: str, content: str, rag_type: str = "text", extra: dict = None):
        """
        role     : "user" | "assistant"
        rag_type : "text" | "image" | "sql"
        extra    : optional dict merged into the log entry (e.g. query, answer, sql)
        """
        entry = {
            "role":      role,
            "content":   content,
            "rag_type":  rag_type,
            "timestamp": datetime.now().isoformat(),
        }
        if extra:
            entry.update(extra)
        
        self.history.append(entry)
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-(self.max_turns * 2):]
        self._persist_all()

    def get_history_text(self, rag_type: str = "text") -> str:
        """Return formatted history for a specific RAG type for prompt injection."""
        lines = []
        for msg in self.history[:-1]:
            if msg.get("rag_type", "text") != rag_type:
                continue
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def get_messages(self):
        return list(self.history)

    def clear(self):
        self.history = []
        self._persist_all()

    def _persist_all(self):
        try:
            with open(self.log_path, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception:
            pass