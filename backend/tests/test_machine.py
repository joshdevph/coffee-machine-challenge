import pytest

from app.errors import ContainerEmptyError, ContainerOverflowError, InvalidFillAmountError
from app.machine import CoffeeMachine, Container, default_machine


def test_brew_reduces_resources():
    machine = default_machine(200, 100)

    usage = machine.brew("espresso")

    assert usage == {"water_ml": 24, "coffee_g": 8}
    assert machine.water_container.level == 176
    assert machine.coffee_container.level == 92


def test_brew_errors_when_containers_are_low():
    machine = default_machine(200, 100)
    machine.water_container.level = 10

    with pytest.raises(ContainerEmptyError):
        machine.brew("espresso")


def test_fill_water_prevents_overflow():
    machine = default_machine(200, 100)
    machine.water_container.level = 190

    with pytest.raises(ContainerOverflowError):
        machine.fill_water(20)


def test_invalid_fill_amount():
    machine = default_machine(200, 100)

    with pytest.raises(InvalidFillAmountError):
        machine.fill_coffee(0)


def test_ristretto_recipe():
    machine = default_machine(200, 100)

    usage = machine.brew("ristretto")

    assert usage == {"water_ml": 16, "coffee_g": 8}
    assert machine.water_container.level == 184
    assert machine.coffee_container.level == 92
