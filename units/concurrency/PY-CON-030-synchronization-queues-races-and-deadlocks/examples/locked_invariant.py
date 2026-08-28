"""Protect a complete inventory reservation invariant with one lock."""

from __future__ import annotations

from dataclasses import dataclass, field
from queue import Queue
from threading import Barrier, Lock, Thread


@dataclass(slots=True)
class Inventory:
    """Mutable stock whose check and decrement form one transition."""

    available: int
    lock: Lock = field(default_factory=Lock, init=False, repr=False)


@dataclass(frozen=True, slots=True)
class Reservation:
    request_id: str
    accepted: bool


def reserve_one(inventory: Inventory, request_id: str) -> Reservation:
    """Reserve at most one item while preserving non-negative stock."""

    with inventory.lock:
        if inventory.available == 0:
            return Reservation(request_id=request_id, accepted=False)
        inventory.available -= 1
        return Reservation(request_id=request_id, accepted=True)


def run_demo() -> tuple[Inventory, list[Reservation]]:
    inventory = Inventory(available=1)
    start_gate = Barrier(3, timeout=2.0)
    outcomes: Queue[Reservation] = Queue()

    def attempt(request_id: str) -> None:
        start_gate.wait()
        outcomes.put(reserve_one(inventory, request_id))

    workers = [
        Thread(name=f"reservation-{request_id}", target=attempt, args=(request_id,))
        for request_id in ("A", "B")
    ]
    for worker in workers:
        worker.start()

    start_gate.wait()
    for worker in workers:
        worker.join(timeout=2.0)
    if any(worker.is_alive() for worker in workers):
        raise RuntimeError("a reservation worker did not terminate")

    records = sorted(
        (outcomes.get_nowait() for _ in workers),
        key=lambda reservation: reservation.request_id,
    )
    assert sum(record.accepted for record in records) == 1
    assert inventory.available == 0
    return inventory, records


def main() -> None:
    inventory, records = run_demo()
    accepted = sum(record.accepted for record in records)
    print(f"accepted={accepted}")
    print(f"rejected={len(records) - accepted}")
    print(f"remaining={inventory.available}")
    print(f"invariant={inventory.available >= 0}")


if __name__ == "__main__":
    main()
