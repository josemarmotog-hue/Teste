from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class TurnstileEvent:
    badge_id: str
    gate_id: str
    direction: str
    timestamp: datetime = field(default_factory=datetime.now)


class TurnstileSystem:
    """Sistema para registrar e consultar leituras de catracas."""

    GATES = tuple(f"CATRACA-{index:02d}" for index in range(1, 9))
    VALID_DIRECTIONS = {"entrada", "saida"}

    def __init__(self) -> None:
        self._events: List[TurnstileEvent] = []
        self._inside: Dict[str, datetime] = {}

    def register_read(
        self,
        badge_id: str,
        gate_id: str,
        direction: str,
        timestamp: Optional[datetime] = None,
    ) -> TurnstileEvent:
        if not badge_id.strip():
            raise ValueError("Informe um crachá válido.")
        if gate_id not in self.GATES:
            raise ValueError("Catraca inválida.")
        if direction not in self.VALID_DIRECTIONS:
            raise ValueError("Direção inválida. Use 'entrada' ou 'saida'.")

        event = TurnstileEvent(
            badge_id=badge_id.strip().upper(),
            gate_id=gate_id,
            direction=direction,
            timestamp=timestamp or datetime.now(),
        )

        if direction == "entrada":
            self._inside[event.badge_id] = event.timestamp
        else:
            self._inside.pop(event.badge_id, None)

        self._events.append(event)
        return event

    def current_occupancy(self) -> int:
        return len(self._inside)

    def is_inside(self, badge_id: str) -> bool:
        return badge_id.strip().upper() in self._inside

    def history(self, badge_id: Optional[str] = None) -> List[TurnstileEvent]:
        if badge_id is None:
            return list(self._events)
        normalized_badge = badge_id.strip().upper()
        return [event for event in self._events if event.badge_id == normalized_badge]


if __name__ == "__main__":
    system = TurnstileSystem()

    system.register_read("A123", "CATRACA-01", "entrada")
    system.register_read("B456", "CATRACA-02", "entrada")
    system.register_read("A123", "CATRACA-01", "saida")

    print(f"Pessoas no ambiente: {system.current_occupancy()}")
    for event in system.history():
        print(
            f"[{event.timestamp:%Y-%m-%d %H:%M:%S}] "
            f"Crachá {event.badge_id} | {event.gate_id} | {event.direction}"
        )
