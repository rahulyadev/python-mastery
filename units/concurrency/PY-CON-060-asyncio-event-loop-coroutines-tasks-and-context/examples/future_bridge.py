"""Adapt one callback-style operation into an awaitable asyncio Future."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class BridgeReport:
    """Results and event order observed by the future owner."""

    first_result: str
    repeated_result: str
    future_done: bool
    events: tuple[str, ...]


def begin_lookup(
    loop: asyncio.AbstractEventLoop,
    key: str,
    events: list[str],
) -> asyncio.Future[str]:
    """Return a loop-owned Future completed by a scheduled callback."""
    future: asyncio.Future[str] = loop.create_future()
    events.append("adapter:scheduled")

    def complete() -> None:
        events.append("adapter:completed")
        if not future.cancelled():
            future.set_result(key.casefold())

    loop.call_soon(complete)
    return future


async def observe_bridge() -> BridgeReport:
    """Await a pending Future, then show that a done Future need not suspend."""
    events: list[str] = []
    loop = asyncio.get_running_loop()
    future = begin_lookup(loop, "READY", events)

    events.append("owner:before-first-await")
    first_result = await future
    events.append("owner:after-first-await")

    loop.call_soon(events.append, "callback:queued-before-second-await")
    repeated_result = await future
    events.append("owner:after-second-await")

    await asyncio.sleep(0)
    events.append("owner:after-explicit-yield")

    return BridgeReport(
        first_result=first_result,
        repeated_result=repeated_result,
        future_done=future.done(),
        events=tuple(events),
    )


def run_demo() -> BridgeReport:
    """Run the adapter under a fresh event loop."""
    return asyncio.run(observe_bridge())


def main() -> None:
    """Print the future results and ordered trace."""
    report = run_demo()
    print(f"first result: {report.first_result!r}")
    print(f"repeated result: {report.repeated_result!r}")
    print(f"future done: {report.future_done}")
    print(f"events: {report.events}")


if __name__ == "__main__":
    main()
