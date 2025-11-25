"""Pydantic schemas shared by the API."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, PositiveInt


class ContainerStatus(BaseModel):
    name: Literal["water", "coffee"]
    capacity: PositiveInt
    level: int = Field(..., ge=0)
    unit: Literal["ml", "g"]


class MachineStatus(BaseModel):
    water: ContainerStatus
    coffee: ContainerStatus
    last_message: Optional[str] = None


class FillWaterRequest(BaseModel):
    amount_ml: PositiveInt = Field(..., description="Amount of water to add in millilitres")


class FillCoffeeRequest(BaseModel):
    amount_g: PositiveInt = Field(..., description="Amount of coffee to add in grams")


class BrewUsage(BaseModel):
    water_ml: PositiveInt
    coffee_g: PositiveInt


class BrewResponse(BaseModel):
    message: str
    drink: str
    used: BrewUsage
    status: MachineStatus


class StatusResponse(BaseModel):
    status: MachineStatus


class FillResponse(BaseModel):
    message: str
    status: MachineStatus
