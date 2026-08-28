"""Expose a logical race deterministically on both GIL and no-GIL builds."""

from __future__ import annotations

import threading
from dataclasses import dataclass


@dataclass
class Counter:
    """Small mutable object whose invariant is owned by the application."""

    value: int = 0


@dataclass(frozen=True)
class RaceReport:
    """Results of controlled unsafe and locked updates."""

    expected: int
    unsafe_result: int
    locked_result: int


def _join_threads(threads: tuple[threading.Thread, ...]) -> None:
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5.0)
    if any(thread.is_alive() for thread in threads):
        raise RuntimeError("controlled worker did not terminate")


def controlled_lost_update() -> int:
    """Force two threads to read the same value before either writes."""
    counter = Counter()
    both_read = threading.Barrier(2, timeout=5.0)

    def increment() -> None:
        observed = counter.value
        both_read.wait()
        counter.value = observed + 1

    threads = (
        threading.Thread(target=increment, name="unsafe-a"),
        threading.Thread(target=increment, name="unsafe-b"),
    )
    _join_threads(threads)
    return counter.value


def locked_updates() -> int:
    """Protect the complete read-modify-write invariant."""
    counter = Counter()
    lock = threading.Lock()

    def increment() -> None:
        with lock:
            counter.value += 1

    threads = (
        threading.Thread(target=increment, name="locked-a"),
        threading.Thread(target=increment, name="locked-b"),
    )
    _join_threads(threads)
    return counter.value


def run_demo() -> RaceReport:
    """Compare the controlled race with explicit synchronization."""
    return RaceReport(
        expected=2,
        unsafe_result=controlled_lost_update(),
        locked_result=locked_updates(),
    )


def main() -> None:
    """Print the two outcomes."""
    report = run_demo()
    print(f"unsafe controlled result: {report.unsafe_result}/{report.expected}")
    print(f"locked result: {report.locked_result}/{report.expected}")


if __name__ == "__main__":
    main()
