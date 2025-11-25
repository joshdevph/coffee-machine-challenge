"""Domain layer for the coffee machine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .errors import ContainerEmptyError, ContainerOverflowError, InvalidFillAmountError


RECIPES: Dict[str, Dict[str, int]] = {
    "espresso": {"water_ml": 24, "coffee_g": 8},
    "double_espresso": {"water_ml": 48, "coffee_g": 16},
    "americano": {"water_ml": 148, "coffee_g": 16},
    "ristretto": {"water_ml": 16, "coffee_g": 8},
}


@dataclass
class Container:
    name: str
    capacity: int
    level: int
    unit: str

    def use(self, amount: int) -> None:
        if self.level < amount:
            raise ContainerEmptyError(self.name, amount, self.level)
        self.level -= amount

    def fill(self, amount: int) -> None:
        if amount <= 0:
            raise InvalidFillAmountError(self.name, amount)
        free_space = self.capacity - self.level
        if free_space < amount:
            raise ContainerOverflowError(self.name, amount, free_space)
        self.level += amount

    def to_dict(self) -> Dict[str, int]:
        return {
            "capacity": self.capacity,
            "level": self.level,
            "unit": self.unit,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "Container":
        return cls(
            name=data["name"],
            capacity=data["capacity"],
            level=data["level"],
            unit=data["unit"],
        )


@dataclass
class CoffeeMachine:
    water_container: Container
    coffee_container: Container
    last_message: Optional[str] = None

    def brew(self, recipe_key: str) -> Dict[str, int]:
        if recipe_key not in RECIPES:
            raise ValueError(f"Unknown recipe '{recipe_key}'")

        recipe = RECIPES[recipe_key]
        self.water_container.use(recipe["water_ml"])
        self.coffee_container.use(recipe["coffee_g"])

        self.last_message = f"{self._friendly_name(recipe_key)} is ready!"
        return recipe

    def fill_water(self, amount_ml: int) -> None:
        self.water_container.fill(amount_ml)
        self.last_message = f"Added {amount_ml} ml of water."

    def fill_coffee(self, amount_g: int) -> None:
        self.coffee_container.fill(amount_g)
        self.last_message = f"Added {amount_g} g of coffee."

    def status(self) -> Dict[str, Dict[str, int]]:
        return {
            "water": self.water_container.to_dict(),
            "coffee": self.coffee_container.to_dict(),
            "last_message": self.last_message,
        }

    def to_dict(self) -> Dict[str, Dict[str, int]]:
        return {
            "water": self.water_container.to_dict(),
            "coffee": self.coffee_container.to_dict(),
            "last_message": self.last_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, int]]) -> "CoffeeMachine":
        return cls(
            water_container=Container.from_dict(data["water"]),
            coffee_container=Container.from_dict(data["coffee"]),
            last_message=data.get("last_message"),
        )

    @staticmethod
    def _friendly_name(recipe_key: str) -> str:
        return recipe_key.replace("_", " ").title()


def default_machine(water_capacity: int, coffee_capacity: int) -> CoffeeMachine:
    return CoffeeMachine(
        water_container=Container(
            name="water",
            capacity=water_capacity,
            level=water_capacity,
            unit="ml",
        ),
        coffee_container=Container(
            name="coffee",
            capacity=coffee_capacity,
            level=coffee_capacity,
            unit="g",
        ),
    )
