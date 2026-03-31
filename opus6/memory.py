"""Persistent memory system for Opus 6.0."""

import json
import os
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path.home() / ".opus6" / "memory"


class Memory:
    """Long-term memory that persists across conversations."""

    def __init__(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self.index_path = MEMORY_DIR / "index.json"
        self.index = self._load_index()

    def _load_index(self) -> list[dict]:
        if self.index_path.exists():
            return json.loads(self.index_path.read_text())
        return []

    def _save_index(self):
        self.index_path.write_text(json.dumps(self.index, indent=2))

    def store(self, content: str, tags: list[str] | None = None):
        """Store a memory with optional tags."""
        entry = {
            "id": len(self.index),
            "content": content,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
        }
        # Save content to file
        path = MEMORY_DIR / f"{entry['id']}.txt"
        path.write_text(content)
        self.index.append(entry)
        self._save_index()
        return entry["id"]

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search memories by keyword matching."""
        query_lower = query.lower()
        scored = []
        for entry in self.index:
            content = (MEMORY_DIR / f"{entry['id']}.txt").read_text()
            score = 0
            for word in query_lower.split():
                if word in content.lower():
                    score += 1
                if word in [t.lower() for t in entry["tags"]]:
                    score += 2
            if score > 0:
                scored.append((score, {**entry, "content": content}))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def get_recent(self, limit: int = 10) -> list[dict]:
        """Get most recent memories."""
        recent = self.index[-limit:]
        results = []
        for entry in reversed(recent):
            path = MEMORY_DIR / f"{entry['id']}.txt"
            if path.exists():
                results.append({**entry, "content": path.read_text()})
        return results
