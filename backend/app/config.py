"""Application level configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _int_from_env(var_name: str, default: int) -> int:
    raw = os.getenv(var_name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise ValueError(f"Environment variable {var_name} must be an integer") from exc


@dataclass(frozen=True)
class Settings:
    water_capacity_ml: int
    coffee_capacity_g: int
    storage_path: Path
    storage_backend: str


@lru_cache
def get_settings() -> Settings:
    storage_backend = os.getenv("STORAGE_BACKEND", "json").lower()
    supported_backends = {"json", "sqlite", "memory"}
    if storage_backend not in supported_backends:
        raise ValueError(
            f"Unsupported STORAGE_BACKEND '{storage_backend}'. "
            f"Choose one of: {', '.join(sorted(supported_backends))}"
        )

    base_dir = Path(os.getenv("STORAGE_DIR", Path(__file__).resolve().parent))
    default_filename = "machine_state.db" if storage_backend == "sqlite" else "machine_state.json"
    storage_path = Path(os.getenv("STORAGE_PATH", base_dir / default_filename))
    if storage_backend != "memory":
        storage_path.parent.mkdir(parents=True, exist_ok=True)

    return Settings(
        water_capacity_ml=_int_from_env("WATER_CAPACITY_ML", 2000),
        coffee_capacity_g=_int_from_env("COFFEE_CAPACITY_G", 500),
        storage_path=storage_path,
        storage_backend=storage_backend,
    )
