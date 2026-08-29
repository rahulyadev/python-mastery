"""Runnable control-flow examples for PY-FND-060."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    """A small queue item used to make loop decisions observable."""

    job_id: str
    state: str
    priority: int


@dataclass(frozen=True)
class SearchReport:
    """The result and path taken by ``select_first_ready_job``."""

    selected_job_id: str | None
    inspected_job_ids: tuple[str, ...]
    skipped_reasons: tuple[str, ...]
    exhausted_without_break: bool


def workload_band(pending: int) -> str:
    """Select exactly one branch after validating the domain."""
    if pending < 0:
        raise ValueError("pending cannot be negative")
    if pending == 0:
        return "idle"
    if pending < 10:
        return "normal"
    return "busy"


def select_first_ready_job(jobs: Iterable[Job]) -> SearchReport:
    """Select the first valid ready job and expose how the loop terminated."""
    inspected: list[str] = []
    skipped: list[str] = []

    for job in jobs:
        inspected.append(job.job_id)

        if job.state != "ready":
            skipped.append(f"{job.job_id}:state={job.state}")
            continue

        if job.priority < 0:
            skipped.append(f"{job.job_id}:negative-priority")
            continue

        selected_job_id = job.job_id
        break
    else:
        return SearchReport(
            selected_job_id=None,
            inspected_job_ids=tuple(inspected),
            skipped_reasons=tuple(skipped),
            exhausted_without_break=True,
        )

    return SearchReport(
        selected_job_id=selected_job_id,
        inspected_job_ids=tuple(inspected),
        skipped_reasons=tuple(skipped),
        exhausted_without_break=False,
    )


def bounded_poll_trace(states: tuple[str, ...], limit: int) -> tuple[str, ...]:
    """Trace ``while``, ``continue``, ``break``, and natural loop completion."""
    if limit < 0:
        raise ValueError("limit cannot be negative")

    events: list[str] = []
    index = 0

    while index < limit and index < len(states):
        state = states[index]
        events.append(f"visit:{index}:{state}")
        index += 1

        if state == "ignore":
            events.append("continue")
            continue

        if state == "ready":
            events.append("break")
            break

        events.append("body-tail")
    else:
        events.append("loop-else:natural-stop")

    events.append("after-loop")
    return tuple(events)


def main() -> None:
    """Print stable example results for direct execution."""
    jobs = (
        Job("job-1", "blocked", 3),
        Job("job-2", "ready", -1),
        Job("job-3", "ready", 5),
        Job("job-4", "ready", 9),
    )
    print(f"workload bands: {[workload_band(value) for value in (0, 3, 12)]}")
    print(f"search with hit: {select_first_ready_job(jobs)!r}")
    print(f"search without hit: {select_first_ready_job(jobs[:2])!r}")
    print(f"poll with break: {bounded_poll_trace(('ignore', 'waiting', 'ready'), 5)!r}")
    print(f"poll without break: {bounded_poll_trace(('ignore', 'waiting'), 5)!r}")


if __name__ == "__main__":
    main()
