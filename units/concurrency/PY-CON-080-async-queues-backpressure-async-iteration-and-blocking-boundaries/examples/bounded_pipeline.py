"""Demonstrate bounded admission, queue accounting, and graceful shutdown."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from typing import TypeVar


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


@dataclass(frozen=True)
class BackpressureReport:
    """Observable state from one deterministically gated bounded pipeline."""

    third_put_blocked: bool
    processed: tuple[str, ...]
    queue_empty: bool
    events: tuple[str, ...]


async def map_bounded(
    items: Iterable[InputT],
    transform: Callable[[InputT], Awaitable[OutputT]],
    *,
    maxsize: int,
    worker_count: int,
) -> list[OutputT]:
    """Transform items with bounded queue storage and worker concurrency.

    Results preserve input order even though workers may complete out of order.
    Python 3.13 or newer is required because workers terminate through
    ``Queue.shutdown()`` and ``QueueShutDown``.
    """
    if maxsize < 1:
        raise ValueError("maxsize must be at least 1")
    if worker_count < 1:
        raise ValueError("worker_count must be at least 1")

    queue: asyncio.Queue[tuple[int, InputT]] = asyncio.Queue(maxsize=maxsize)
    results: dict[int, OutputT] = {}
    item_count = 0

    async def worker() -> None:
        while True:
            try:
                index, item = await queue.get()
            except asyncio.QueueShutDown:
                return

            try:
                results[index] = await transform(item)
            finally:
                # One successful get owns exactly one task_done call, including
                # when transformation fails or this worker is cancelled.
                queue.task_done()

    async with asyncio.TaskGroup() as group:
        for index in range(worker_count):
            group.create_task(worker(), name=f"bounded-worker-{index}")

        for item_count, item in enumerate(items, start=1):
            await queue.put((item_count - 1, item))

        queue.shutdown()
        await queue.join()

    return [results[index] for index in range(item_count)]


async def observe_backpressure() -> BackpressureReport:
    """Prove that a third put waits while a one-slot queue is full."""
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=1)
    first_started = asyncio.Event()
    release_first = asyncio.Event()
    third_attempted = asyncio.Event()
    events: list[str] = []
    processed: list[str] = []

    async def worker() -> None:
        while True:
            try:
                item = await queue.get()
            except asyncio.QueueShutDown:
                events.append("worker:queue-shutdown")
                return

            events.append(f"worker:get:{item}")
            try:
                if item == "alpha":
                    first_started.set()
                    await release_first.wait()
                processed.append(item)
                events.append(f"worker:done:{item}")
            finally:
                queue.task_done()

    async def put_third() -> None:
        events.append("producer:attempt:gamma")
        third_attempted.set()
        await queue.put("gamma")
        events.append("producer:accepted:gamma")

    queue.put_nowait("alpha")
    events.append("producer:accepted:alpha")

    async with asyncio.TaskGroup() as group:
        group.create_task(worker(), name="gated-worker")
        await first_started.wait()

        await queue.put("beta")
        events.append("producer:accepted:beta")

        third_put = group.create_task(put_third(), name="third-put")
        await third_attempted.wait()
        third_put_blocked = not third_put.done()
        events.append(f"owner:third-put-blocked:{third_put_blocked}")

        release_first.set()
        events.append("owner:released-alpha")
        await third_put

        queue.shutdown()
        events.append("owner:shutdown")
        await queue.join()
        events.append("owner:joined")

    return BackpressureReport(
        third_put_blocked=third_put_blocked,
        processed=tuple(processed),
        queue_empty=queue.empty(),
        events=tuple(events),
    )


def run_demo() -> BackpressureReport:
    """Run the deterministic demonstration on a fresh event loop."""
    return asyncio.run(observe_backpressure())


def main() -> None:
    """Print the bounded-admission result and event trace."""
    report = run_demo()
    print(f"third put blocked: {report.third_put_blocked}")
    print(f"processed: {report.processed}")
    print(f"queue empty: {report.queue_empty}")
    for event in report.events:
        print(event)


if __name__ == "__main__":
    main()
