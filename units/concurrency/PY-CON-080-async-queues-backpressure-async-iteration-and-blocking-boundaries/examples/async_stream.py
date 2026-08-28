"""Demonstrate the async-iteration protocol and deterministic early cleanup."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable
from contextlib import aclosing
from dataclasses import dataclass


@dataclass(frozen=True)
class StreamReport:
    """Values and lifecycle events visible to the stream owner."""

    accepted: tuple[str, ...]
    events: tuple[str, ...]


class AsyncCountdown:
    """A small explicit asynchronous iterator for protocol inspection."""

    def __init__(self, start: int) -> None:
        if start < 0:
            raise ValueError("start must be non-negative")
        self._next = start

    def __aiter__(self) -> AsyncCountdown:
        return self

    async def __anext__(self) -> int:
        await asyncio.sleep(0)
        if self._next == 0:
            raise StopAsyncIteration
        value = self._next
        self._next -= 1
        return value


async def record_stream(
    records: Iterable[str], events: list[str]
) -> AsyncIterator[str]:
    """Yield synthetic records while exposing generator finalization."""
    events.append("stream:open")
    try:
        for record in records:
            await asyncio.sleep(0)
            events.append(f"stream:yield:{record}")
            yield record
    finally:
        events.append("stream:close")


async def consume_prefix(
    records: Iterable[str], *, limit: int
) -> StreamReport:
    """Consume at most limit values and close the generator before returning."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    events: list[str] = []
    accepted: list[str] = []

    async with aclosing(record_stream(records, events)) as stream:
        events.append("owner:entered-context")
        async for record in stream:
            accepted.append(record)
            events.append(f"owner:accepted:{record}")
            if len(accepted) == limit:
                events.append("owner:break")
                break
        events.append("owner:leaving-context")

    events.append("owner:after-context")
    return StreamReport(tuple(accepted), tuple(events))


def run_demo() -> StreamReport:
    """Run the early-exit example on a fresh event loop."""
    return asyncio.run(
        consume_prefix(("alpha", "beta", "gamma"), limit=2)
    )


def main() -> None:
    """Print values and generator-lifecycle events."""
    report = run_demo()
    print(f"accepted: {report.accepted}")
    for event in report.events:
        print(event)


if __name__ == "__main__":
    main()
