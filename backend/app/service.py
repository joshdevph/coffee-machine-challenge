"""Application service orchestrating the machine and persistence."""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from .config import Settings
from .machine import CoffeeMachine, default_machine
from .storage import StateStorage


class CoffeeMachineService:
    def __init__(self, storage: StateStorage, settings: Settings) -> None:
        self._storage = storage
        self._settings = settings
        self._lock = asyncio.Lock()
        self._machine = self._load_machine()

    def _load_machine(self) -> CoffeeMachine:
        state = self._storage.load()
        if state:
            return CoffeeMachine.from_dict(state)
        return default_machine(
            self._settings.water_capacity_ml,
            self._settings.coffee_capacity_g,
        )

    def _persist(self) -> None:
        self._storage.save(self._machine.to_dict())

    async def brew(self, recipe_key: str) -> Dict[str, Any]:
        async with self._lock:
            usage = self._machine.brew(recipe_key)
            self._persist()
            return {
                "message": self._machine.last_message,
                "drink": recipe_key,
                "used": usage,
                "status": self._machine.status(),
            }

    async def fill_water(self, amount_ml: int) -> Dict[str, Any]:
        async with self._lock:
            self._machine.fill_water(amount_ml)
            self._persist()
            return {
                "message": self._machine.last_message,
                "status": self._machine.status(),
            }

    async def fill_coffee(self, amount_g: int) -> Dict[str, Any]:
        async with self._lock:
            self._machine.fill_coffee(amount_g)
            self._persist()
            return {
                "message": self._machine.last_message,
                "status": self._machine.status(),
            }

    async def status(self) -> Dict[str, Any]:
        async with self._lock:
            return self._machine.status()
