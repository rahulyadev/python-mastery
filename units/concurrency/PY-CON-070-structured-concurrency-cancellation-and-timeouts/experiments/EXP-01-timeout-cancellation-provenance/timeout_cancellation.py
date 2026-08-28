"""Compare timeout-owned cancellation with external cancellation."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class ProvenanceReport:
    """Two controlled traces and their terminal cancellation state."""

    timeout_trace: tuple[str, ...]
    timeout_count_before: int
    timeout_count_after: int
    external_trace: tuple[str, ...]
    externally_cancelled_task: bool


async def _timeout_owned_trace() -> tuple[tuple[str, ...], int, int]:
    events: list[str] = []
    task = asyncio.current_task()
    if task is None:  # pragma: no cover - always invoked inside asyncio.run
        raise RuntimeError("no current task")

    count_before = task.cancelling()
    try:
        async with asyncio.timeout(0):
            events.append("timeout:entered")
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                events.append("timeout:inside-cancelled")
                raise
            finally:
                events.append("timeout:cleanup")
    except TimeoutError:
        events.append("timeout:outside-timeout-error")

    return tuple(events), count_before, task.cancelling()


async def _external_trace() -> tuple[tuple[str, ...], bool]:
    events: list[str] = []
    entered = asyncio.Event()
    never_release = asyncio.Event()

    async def victim() -> None:
        try:
            async with asyncio.timeout(None):
                events.append("external:entered")
                entered.set()
                await never_release.wait()
        except TimeoutError:
            events.append("external:wrong-timeout-error")
        except asyncio.CancelledError:
            events.append("external:inside-cancelled")
            raise
        finally:
            events.append("external:cleanup")

    task = asyncio.create_task(victim(), name="external-cancel-victim")
    await entered.wait()
    task.cancel("external shutdown")
    events.append("external:cancel-requested")
    try:
        await task
    except asyncio.CancelledError:
        events.append("external:owner-observed-cancelled")

    return tuple(events), task.cancelled()


async def observe_provenance() -> ProvenanceReport:
    """Collect both cancellation paths on one fresh event loop."""
    timeout_trace, count_before, count_after = await _timeout_owned_trace()
    external_trace, task_cancelled = await _external_trace()
    return ProvenanceReport(
        timeout_trace=timeout_trace,
        timeout_count_before=count_before,
        timeout_count_after=count_after,
        external_trace=external_trace,
        externally_cancelled_task=task_cancelled,
    )


def run_experiment() -> ProvenanceReport:
    """Run the controlled comparison."""
    return asyncio.run(observe_provenance())


def main() -> None:
    """Print both traces without editing or normalizing their order."""
    report = run_experiment()
    print("timeout-owned cancellation")
    for event in report.timeout_trace:
        print(event)
    print(
        "timeout cancellation count: "
        f"{report.timeout_count_before} -> {report.timeout_count_after}"
    )
    print("external cancellation")
    for event in report.external_trace:
        print(event)
    print(f"external task cancelled: {report.externally_cancelled_task}")


if __name__ == "__main__":
    main()
