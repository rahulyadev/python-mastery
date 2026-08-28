"""Use the Python 3.14 interpreter-pool transfer boundary explicitly."""

from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass


class InterpreterPoolUnavailable(RuntimeError):
    """Raised when InterpreterPoolExecutor is unavailable."""


@dataclass(frozen=True)
class PoolReport:
    """Input batches and copied results from interpreter workers."""

    batches: tuple[tuple[int, ...], ...]
    partial_sums: tuple[int, ...]

    @property
    def total(self) -> int:
        return sum(self.partial_sums)


def sum_batches(
    batches: tuple[tuple[int, ...], ...],
) -> PoolReport:
    """Submit immutable batches and collect immutable integer results."""
    if not batches:
        return PoolReport(batches=(), partial_sums=())

    executor_type = getattr(
        concurrent.futures,
        "InterpreterPoolExecutor",
        None,
    )
    if executor_type is None:
        raise InterpreterPoolUnavailable(
            "InterpreterPoolExecutor requires Python 3.14+"
        )

    with executor_type(max_workers=min(2, len(batches))) as executor:
        partial_sums = tuple(executor.map(sum, batches))

    return PoolReport(batches=batches, partial_sums=partial_sums)


def run_demo() -> PoolReport:
    """Run a tiny boundary example; this is intentionally not a benchmark."""
    return sum_batches(((1, 2, 3), (4, 5)))


def main() -> None:
    """Print copied results in submission order."""
    report = run_demo()
    print(f"interpreter pool partials: {report.partial_sums}")
    print(f"interpreter pool total: {report.total}")


if __name__ == "__main__":
    main()
