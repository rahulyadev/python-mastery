"""Demonstrate TaskGroup ownership, sibling cancellation, and failure routing."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


class RecordRejected(Exception):
    """An expected synthetic domain failure from one child task."""


@dataclass(frozen=True)
class TaskGroupReport:
    """Owner-visible outcomes after the structured scope has closed."""

    failures: tuple[str, ...]
    cancelled_tasks: tuple[str, ...]
    events: tuple[str, ...]


async def _waiting_worker(
    name: str,
    started: asyncio.Event,
    release: asyncio.Event,
    events: list[str],
) -> str:
    """Wait for work while recording cancellation-safe cleanup."""
    events.append(f"{name}:start")
    started.set()
    try:
        await release.wait()
        events.append(f"{name}:finish")
        return name
    except asyncio.CancelledError:
        events.append(f"{name}:cancelled")
        raise
    finally:
        events.append(f"{name}:cleanup")


async def _reject_after_siblings_start(
    first_started: asyncio.Event,
    second_started: asyncio.Event,
    events: list[str],
) -> None:
    """Raise only after both siblings have reached their wait points."""
    events.append("validator:start")
    await first_started.wait()
    await second_started.wait()
    events.append("validator:raise")
    raise RecordRejected("synthetic record rejected")


async def observe_taskgroup_failure() -> TaskGroupReport:
    """Run one failing child and observe the fully closed group."""
    events: list[str] = []
    first_started = asyncio.Event()
    second_started = asyncio.Event()
    never_release = asyncio.Event()
    sibling_tasks: list[asyncio.Task[str]] = []
    failures: tuple[str, ...] = ()

    try:
        async with asyncio.TaskGroup() as group:
            sibling_tasks.append(
                group.create_task(
                    _waiting_worker(
                        "cache", first_started, never_release, events
                    ),
                    name="cache",
                )
            )
            sibling_tasks.append(
                group.create_task(
                    _waiting_worker(
                        "profile", second_started, never_release, events
                    ),
                    name="profile",
                )
            )
            group.create_task(
                _reject_after_siblings_start(
                    first_started, second_started, events
                ),
                name="validator",
            )
            events.append("owner:tasks-created")
    except* RecordRejected as group:
        failures = tuple(str(error) for error in group.exceptions)
        events.append("owner:caught-rejection")

    cancelled_tasks = tuple(
        task.get_name() for task in sibling_tasks if task.cancelled()
    )
    events.append("owner:after-group")
    return TaskGroupReport(failures, cancelled_tasks, tuple(events))


def run_demo() -> TaskGroupReport:
    """Run the example under a fresh event loop."""
    return asyncio.run(observe_taskgroup_failure())


def main() -> None:
    """Print the structured outcome and event trace."""
    report = run_demo()
    print(f"failures: {report.failures}")
    print(f"cancelled tasks: {report.cancelled_tasks}")
    for event in report.events:
        print(event)


if __name__ == "__main__":
    main()
