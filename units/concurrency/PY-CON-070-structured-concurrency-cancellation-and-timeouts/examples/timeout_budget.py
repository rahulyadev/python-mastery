"""Show a request-wide timeout budget and its cancellation boundary."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


class BatchDeadlineExceeded(TimeoutError):
    """The synthetic batch did not finish inside its owned budget."""

    def __init__(self, record_ids: Sequence[str]) -> None:
        self.record_ids = tuple(record_ids)
        super().__init__(
            f"batch deadline exceeded for {len(self.record_ids)} record(s)"
        )


@dataclass(frozen=True)
class TimeoutReport:
    """Trace how timeout-owned cancellation is translated at scope exit."""

    timed_out: bool
    cancellation_count_before: int
    cancellation_count_after: int
    events: tuple[str, ...]


async def fetch_batch(
    fetch_one: Callable[[str], Awaitable[T]],
    record_ids: Sequence[str],
    *,
    timeout_seconds: float,
) -> dict[str, T]:
    """Fetch unique records concurrently within one end-to-end budget."""
    identifiers = tuple(record_ids)
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("record_ids must be unique")

    tasks: dict[str, asyncio.Task[T]] = {}
    try:
        async with asyncio.timeout(timeout_seconds):
            async with asyncio.TaskGroup() as group:
                for record_id in identifiers:
                    tasks[record_id] = group.create_task(
                        fetch_one(record_id), name=f"fetch:{record_id}"
                    )
    except TimeoutError as error:
        raise BatchDeadlineExceeded(identifiers) from error

    return {record_id: task.result() for record_id, task in tasks.items()}


async def observe_timeout_transformation() -> TimeoutReport:
    """Use a zero-duration budget to expose the exact exception boundary."""
    events: list[str] = []
    task = asyncio.current_task()
    if task is None:  # pragma: no cover - this coroutine always needs a Task
        raise RuntimeError("no current task")

    cancellation_count_before = task.cancelling()
    timed_out = False
    try:
        async with asyncio.timeout(0):
            events.append("scope:entered")
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                events.append("scope:cancelled")
                raise
            finally:
                events.append("scope:cleanup")
    except TimeoutError:
        timed_out = True
        events.append("owner:timeout")

    return TimeoutReport(
        timed_out=timed_out,
        cancellation_count_before=cancellation_count_before,
        cancellation_count_after=task.cancelling(),
        events=tuple(events),
    )


def run_demo() -> TimeoutReport:
    """Run the timeout trace under a fresh event loop."""
    return asyncio.run(observe_timeout_transformation())


def main() -> None:
    """Print the timeout trace."""
    report = run_demo()
    print(f"timed out: {report.timed_out}")
    print(
        "cancellation count: "
        f"{report.cancellation_count_before} -> "
        f"{report.cancellation_count_after}"
    )
    for event in report.events:
        print(event)


if __name__ == "__main__":
    main()
