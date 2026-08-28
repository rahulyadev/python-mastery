"""Expose cooperative cancellation and cleanup before owner observation."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class CancellationReport:
    """Observable state after a cancelled worker has terminated."""

    cancel_request_accepted: bool
    cancellation_message: str
    cleanup_completed: bool
    task_cancelled: bool
    cancellation_count: int
    events: tuple[str, ...]


async def _managed_worker(
    started: asyncio.Event,
    never_release: asyncio.Event,
    events: list[str],
) -> None:
    """Wait until cancelled and finish one cooperative cleanup step."""
    events.append("worker:start")
    started.set()
    try:
        await never_release.wait()
    except asyncio.CancelledError:
        events.append("worker:cancelled")
        raise
    finally:
        events.append("worker:cleanup-start")
        await asyncio.sleep(0)
        events.append("worker:cleanup-done")


async def observe_cancellation_cleanup() -> CancellationReport:
    """Cancel one owned worker and await its terminal state."""
    events: list[str] = []
    started = asyncio.Event()
    never_release = asyncio.Event()
    worker = asyncio.create_task(
        _managed_worker(started, never_release, events),
        name="managed-worker",
    )

    await started.wait()
    request_accepted = worker.cancel("synthetic shutdown")
    events.append("owner:cancel-requested")

    cancellation_message = ""
    try:
        await worker
    except asyncio.CancelledError as error:
        cancellation_message = str(error)
        events.append("owner:cancel-observed")

    return CancellationReport(
        cancel_request_accepted=request_accepted,
        cancellation_message=cancellation_message,
        cleanup_completed="worker:cleanup-done" in events,
        task_cancelled=worker.cancelled(),
        cancellation_count=worker.cancelling(),
        events=tuple(events),
    )


def run_demo() -> CancellationReport:
    """Run the cancellation trace under a fresh event loop."""
    return asyncio.run(observe_cancellation_cleanup())


def main() -> None:
    """Print the terminal cancellation state and trace."""
    report = run_demo()
    print(f"cancel request accepted: {report.cancel_request_accepted}")
    print(f"cancellation message: {report.cancellation_message!r}")
    print(f"cleanup completed: {report.cleanup_completed}")
    print(f"task cancelled: {report.task_cancelled}")
    print(f"cancellation count: {report.cancellation_count}")
    for event in report.events:
        print(event)


if __name__ == "__main__":
    main()
