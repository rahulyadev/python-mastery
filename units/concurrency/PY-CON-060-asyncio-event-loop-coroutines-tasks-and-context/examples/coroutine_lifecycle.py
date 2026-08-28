"""Expose coroutine creation, task scheduling, suspension, and completion.

The demo uses ``asyncio.sleep(0)`` only as a documented cooperative
checkpoint. It does not use wall-clock timing as a scheduling assumption.
"""

from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass


@dataclass(frozen=True)
class LifecycleReport:
    """Owner-visible states and the deterministic event trace."""

    created_state: str
    done_immediately_after_create_task: bool
    done_after_one_loop_turn: bool
    closed_state: str
    result: int
    events: tuple[str, ...]


async def compute(events: list[str]) -> int:
    """Record one start, suspend once, then return a value."""
    events.append("worker:start")
    await asyncio.sleep(0)
    events.append("worker:resume")
    return 42


async def observe_lifecycle() -> LifecycleReport:
    """Create one coroutine, schedule it as a task, and collect it."""
    events: list[str] = []
    coroutine = compute(events)
    created_state = inspect.getcoroutinestate(coroutine)
    events.append("owner:coroutine-created")

    task = asyncio.create_task(coroutine, name="lifecycle-worker")
    done_immediately = task.done()
    events.append("owner:task-created")

    await asyncio.sleep(0)
    done_after_one_turn = task.done()
    events.append("owner:after-one-turn")

    result = await task
    events.append("owner:collected")
    closed_state = inspect.getcoroutinestate(coroutine)

    return LifecycleReport(
        created_state=created_state,
        done_immediately_after_create_task=done_immediately,
        done_after_one_loop_turn=done_after_one_turn,
        closed_state=closed_state,
        result=result,
        events=tuple(events),
    )


def run_demo() -> LifecycleReport:
    """Run the lifecycle under a fresh high-level event-loop runner."""
    return asyncio.run(observe_lifecycle())


def main() -> None:
    """Print the state observations and ordered trace."""
    report = run_demo()
    print(f"created state: {report.created_state}")
    print(
        "done immediately after create_task: "
        f"{report.done_immediately_after_create_task}"
    )
    print(f"done after one loop turn: {report.done_after_one_loop_turn}")
    print(f"closed state: {report.closed_state}")
    print(f"result: {report.result}")
    print(f"events: {report.events}")


if __name__ == "__main__":
    main()
