"""FastAPI entry point for the coffee machine."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .errors import CoffeeMachineError
from .schemas import (
    BrewResponse,
    FillCoffeeRequest,
    FillResponse,
    FillWaterRequest,
    StatusResponse,
)
from .service import CoffeeMachineService
from .storage import build_storage

settings = get_settings()
storage = build_storage(settings.storage_backend, settings.storage_path)
service = CoffeeMachineService(storage=storage, settings=settings)

app = FastAPI(
    title="Coffee Machine API",
    description="Simple API that simulates brewing espresso-based drinks.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(CoffeeMachineError)
async def handle_machine_error(_: Request, exc: CoffeeMachineError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)},
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:  # pragma: no cover - defensive
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Unexpected error occurred", "details": str(exc)},
    )


@app.get("/", response_model=StatusResponse)
async def root_status() -> StatusResponse:
    return StatusResponse(status=await service.status())


@app.get("/status", response_model=StatusResponse)
async def status_endpoint() -> StatusResponse:
    return StatusResponse(status=await service.status())


@app.post("/coffee/espresso", response_model=BrewResponse)
async def brew_espresso() -> BrewResponse:
    return BrewResponse(**await service.brew("espresso"))


@app.post("/coffee/double-espresso", response_model=BrewResponse)
async def brew_double_espresso() -> BrewResponse:
    return BrewResponse(**await service.brew("double_espresso"))


@app.post("/coffee/americano", response_model=BrewResponse)
async def brew_americano() -> BrewResponse:
    return BrewResponse(**await service.brew("americano"))


@app.post("/coffee/ristretto", response_model=BrewResponse)
async def brew_ristretto() -> BrewResponse:
    return BrewResponse(**await service.brew("ristretto"))


@app.post("/containers/water/fill", response_model=FillResponse)
async def fill_water(request: FillWaterRequest) -> FillResponse:
    return FillResponse(**await service.fill_water(request.amount_ml))


@app.post("/containers/coffee/fill", response_model=FillResponse)
async def fill_coffee(request: FillCoffeeRequest) -> FillResponse:
    return FillResponse(**await service.fill_coffee(request.amount_g))
