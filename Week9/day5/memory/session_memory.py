from collections import deque
from datetime import datetime


class SessionMemory:
    """
    Each message stored as:
        {"role": str, "content": str, "agent": str, "ts": ISO str}
    """

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self._buffer: deque[dict] = deque(maxlen=window_size)

    def add(self, role: str, content: str, agent: str = "system") -> None:
        """Push a new message into the session window."""
        self._buffer.append({
            "role":    role,
            "content": content,
            "agent":   agent,
            "ts":      datetime.utcnow().isoformat(),
        })

    def get_window(self) -> list[dict]:
        """Return all messages in the current window."""
        return list(self._buffer)

    def get_context_string(self) -> str:
        """
        Format the window as a readable block for prompt injection.
        Example:
            [2026-04-17T07:00:00] User (user): What is FAISS?
            [2026-04-17T07:00:05] MemoryAgent (assistant): FAISS is ...
        """
        if not self._buffer:
            return "(no session context yet)"
        lines = []
        for msg in self._buffer:
            ts    = msg["ts"][:19]
            agent = msg["agent"]
            role  = msg["role"]
            text  = msg["content"][:200]
            lines.append(f"[{ts}] {agent} ({role}): {text}")
        return "\n".join(lines)

    def clear(self) -> None:
        """Wipe the session window."""
        self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)

    def __repr__(self) -> str:
        return f"<SessionMemory window={self.window_size} msgs={len(self._buffer)}>"


# per-session registry
_sessions: dict[str, "SessionMemory"] = {}


def get_session_memory(session: str = "default", window_size: int = 10) -> SessionMemory:
    """Return (or create) the SessionMemory for a given session ID."""
    if session not in _sessions:
        _sessions[session] = SessionMemory(window_size=window_size)
    return _sessions[session]


def clear_session(session: str = "default") -> None:
    """Clear all messages for a session."""
    if session in _sessions:
        _sessions[session].clear()