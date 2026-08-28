"""Contrast the state represented by several threading primitives."""

from __future__ import annotations

from queue import Queue
from threading import (
    Barrier,
    BoundedSemaphore,
    Condition,
    Event,
    RLock,
    Thread,
)


class ReentrantLedger:
    """A deliberate public-to-public call graph protected by one RLock."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._values: list[int] = []

    def add_and_total(self, value: int) -> int:
        with self._lock:
            self._values.append(value)
            return self.total()

    def total(self) -> int:
        with self._lock:
            return sum(self._values)


def demonstrate_capacity_and_event() -> tuple[int, bool]:
    capacity = BoundedSemaphore(2)
    start_gate = Barrier(4, timeout=2.0)
    release = Event()
    state_changed = Condition()
    failures: Queue[BaseException] = Queue()
    active = 0
    maximum_active = 0

    def use_permit() -> None:
        nonlocal active, maximum_active
        try:
            start_gate.wait()
            with capacity:
                with state_changed:
                    active += 1
                    maximum_active = max(maximum_active, active)
                    state_changed.notify_all()
                try:
                    if not release.wait(timeout=2.0):
                        raise TimeoutError("release event was not set")
                finally:
                    with state_changed:
                        active -= 1
                        state_changed.notify_all()
        except BaseException as exc:
            failures.put(exc)

    workers = [
        Thread(name=f"permit-user-{index}", target=use_permit)
        for index in range(3)
    ]
    for worker in workers:
        worker.start()

    start_gate.wait()
    with state_changed:
        reached_capacity = state_changed.wait_for(
            lambda: maximum_active == 2,
            timeout=2.0,
        )
    if not reached_capacity:
        raise RuntimeError("workers did not fill the two available permits")

    release.set()
    for worker in workers:
        worker.join(timeout=2.0)
    if any(worker.is_alive() for worker in workers):
        raise RuntimeError("a permit worker did not terminate")
    if not failures.empty():
        raise failures.get_nowait()
    return maximum_active, release.is_set()


def demonstrate_barrier_tokens() -> list[int]:
    phase = Barrier(3, timeout=2.0)
    tokens: Queue[int] = Queue()

    def rendezvous() -> None:
        tokens.put(phase.wait())

    workers = [
        Thread(name=f"phase-worker-{index}", target=rendezvous)
        for index in range(3)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=2.0)
    if any(worker.is_alive() for worker in workers):
        raise RuntimeError("a barrier worker did not terminate")
    return sorted(tokens.get_nowait() for _ in workers)


def run_demo() -> tuple[int, int, bool, list[int]]:
    ledger = ReentrantLedger()
    rlock_total = ledger.add_and_total(7)
    maximum_active, event_is_set = demonstrate_capacity_and_event()
    barrier_tokens = demonstrate_barrier_tokens()
    assert maximum_active == 2
    assert barrier_tokens == [0, 1, 2]
    return rlock_total, maximum_active, event_is_set, barrier_tokens


def main() -> None:
    rlock_total, maximum_active, event_is_set, barrier_tokens = run_demo()
    print(f"rlock_total={rlock_total}")
    print(f"semaphore_max_active={maximum_active}")
    print(f"event_is_set={event_is_set}")
    print(f"barrier_tokens={barrier_tokens}")


if __name__ == "__main__":
    main()
