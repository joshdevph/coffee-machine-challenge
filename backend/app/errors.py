"""Domain specific exceptions for the coffee machine."""

from dataclasses import dataclass


class CoffeeMachineError(RuntimeError):
    """Base error for domain specific exceptions."""


@dataclass
class ContainerEmptyError(CoffeeMachineError):
    container_name: str
    required_amount: int
    available_amount: int

    def __str__(self) -> str:  # pragma: no cover - simple formatting
        return (
            f"Cannot make coffee because the {self.container_name} container "
            f"only has {self.available_amount} available but {self.required_amount} is required."
        )


@dataclass
class ContainerOverflowError(CoffeeMachineError):
    container_name: str
    attempted_amount: int
    free_capacity: int

    def __str__(self) -> str:  # pragma: no cover - simple formatting
        return (
            f"Adding {self.attempted_amount} to the {self.container_name} container would overflow it. "
            f"It has room for only {self.free_capacity} more."
        )


@dataclass
class InvalidFillAmountError(CoffeeMachineError):
    container_name: str
    attempted_amount: int

    def __str__(self) -> str:  # pragma: no cover - simple formatting
        return (
            f"The amount ({self.attempted_amount}) to add to the {self.container_name} container "
            "must be a positive number."
        )
