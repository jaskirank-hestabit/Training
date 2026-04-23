import os
import json
import time
from datetime import datetime
from nexus_ai.config import NEXUS_CONFIG


class NexusTracer:
    def __init__(self, session: str = "default"):
        self.session    = session
        self.logs_dir   = NEXUS_CONFIG["logs_dir"]
        os.makedirs(self.logs_dir, exist_ok=True)
        self.trace_path = os.path.join(self.logs_dir, f"{session}_trace.json")
        self._trace     = {"session": session, "steps": [], "pipeline": {}}
        self._timers    = {}

    def start(self, name: str) -> None:
        self._timers[name] = time.time()
        self._trace["pipeline"]["start"] = datetime.utcnow().isoformat()
        self._trace["pipeline"]["name"]  = name
        self._save()

    def step(self, agent: str, event: str, meta: dict = None) -> None:
        elapsed = round(time.time() - self._timers.get(agent, time.time()), 3)
        entry = {
            "agent":   agent,
            "event":   event,
            "ts":      datetime.utcnow().isoformat(),
            "elapsed": elapsed,
        }
        if meta:
            entry["meta"] = meta
        if event == "start":
            self._timers[agent] = time.time()
        self._trace["steps"].append(entry)
        self._save()

    def end(self, name: str) -> None:
        if name in self._timers:
            total = round(time.time() - self._timers[name], 3)
            self._trace["pipeline"]["total_seconds"] = total
            self._trace["pipeline"]["end"] = datetime.utcnow().isoformat()
        self._save()
        print(f"\n  [Tracer] Trace saved → {os.path.abspath(self.trace_path)}")

    def _save(self) -> None:
        try:
            with open(self.trace_path, "w", encoding="utf-8") as f:
                json.dump(self._trace, f, indent=2)
        except Exception:
            pass