"""State persistence helpers."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class StateStorage(Protocol):
    """Minimal interface for persisting machine state."""

    def load(self) -> Optional[Dict[str, Any]]:
        ...

    def save(self, data: Dict[str, Any]) -> None:
        ...


class JSONStateStorage:
    """Persists the machine state to a JSON file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Optional[Dict[str, Any]]:
        if not self.path.exists():
            return None
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, data: Dict[str, Any]) -> None:
        tmp_path = self.path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        tmp_path.replace(self.path)


class MemoryStateStorage:
    """In-memory storage, useful for tests or ephemeral runs."""

    def __init__(self) -> None:
        self._state: Optional[Dict[str, Any]] = None

    def load(self) -> Optional[Dict[str, Any]]:
        return self._state

    def save(self, data: Dict[str, Any]) -> None:
        # Copy to avoid shared mutation from callers
        self._state = json.loads(json.dumps(data))


class SQLiteStateStorage:
    """SQLite-backed storage for more durability."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS machine_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    payload TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def load(self) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM machine_state WHERE id = 1").fetchone()
            if not row:
                return None
            return json.loads(row[0])

    def save(self, data: Dict[str, Any]) -> None:
        serialized = json.dumps(data)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO machine_state (id, payload) VALUES (1, ?)",
                (serialized,),
            )
            conn.commit()


def build_storage(backend: str, path: Path) -> StateStorage:
    """Factory to easily switch storage engines."""
    backend = backend.lower()
    if backend == "json":
        return JSONStateStorage(path)
    if backend == "sqlite":
        return SQLiteStateStorage(path)
    if backend == "memory":
        return MemoryStateStorage()
    raise ValueError(f"Unsupported storage backend '{backend}'")
