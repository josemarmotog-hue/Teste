from datetime import datetime

import pytest

from turnstile_system import TurnstileSystem


def test_system_has_eight_turnstiles() -> None:
    assert len(TurnstileSystem.GATES) == 8
    assert TurnstileSystem.GATES[0] == "CATRACA-01"
    assert TurnstileSystem.GATES[-1] == "CATRACA-08"


def test_register_entry_and_exit_updates_occupancy() -> None:
    system = TurnstileSystem()

    system.register_read("a123", "CATRACA-01", "entrada")
    assert system.current_occupancy() == 1
    assert system.is_inside("A123")

    system.register_read("A123", "CATRACA-01", "saida")
    assert system.current_occupancy() == 0
    assert not system.is_inside("a123")


def test_history_can_filter_by_badge() -> None:
    system = TurnstileSystem()
    now = datetime(2026, 1, 1, 10, 0, 0)

    system.register_read("A123", "CATRACA-01", "entrada", now)
    system.register_read("B456", "CATRACA-02", "entrada", now)

    events = system.history("a123")

    assert len(events) == 1
    assert events[0].badge_id == "A123"
    assert events[0].gate_id == "CATRACA-01"


def test_invalid_direction_raises_error() -> None:
    system = TurnstileSystem()

    with pytest.raises(ValueError):
        system.register_read("A123", "CATRACA-01", "subida")


def test_invalid_gate_raises_error() -> None:
    system = TurnstileSystem()

    with pytest.raises(ValueError):
        system.register_read("A123", "CATRACA-99", "entrada")
