"""A bounded, failure-reporting process pipeline using explicit messages."""

from __future__ import annotations

import multiprocessing as mp
from dataclasses import dataclass
from queue import Empty
from typing import Any


@dataclass(frozen=True)
class Job:
    job_id: str
    value: int


@dataclass(frozen=True)
class Outcome:
    job_id: str
    value: int | None = None
    error: str | None = None


def process_jobs(jobs: Any, outcomes: Any) -> None:
    """Consume jobs until a sentinel arrives and report every accepted job."""

    while True:
        job = jobs.get()
        try:
            if job is None:
                return
            if job.value < 0:
                raise ValueError("synthetic negative input")
            outcomes.put(Outcome(job_id=job.job_id, value=job.value * job.value))
        except Exception as error:  # The process boundary needs an explicit error message.
            outcomes.put(Outcome(job_id=job.job_id, error=f"{type(error).__name__}: {error}"))
        finally:
            jobs.task_done()


def run_demo() -> tuple[list[Outcome], tuple[int, ...]]:
    """Run two workers under spawn and return ordered outcomes and exit codes."""

    context = mp.get_context("spawn")
    jobs = context.JoinableQueue(maxsize=4)
    outcomes = context.Queue()
    workers = [
        context.Process(target=process_jobs, args=(jobs, outcomes), name=f"pipeline-{index}")
        for index in range(2)
    ]
    submitted = [Job("job-a", 3), Job("job-b", -1), Job("job-c", 5)]

    for worker in workers:
        worker.start()
    try:
        for job in submitted:
            jobs.put(job, timeout=5)
        for _ in workers:
            jobs.put(None, timeout=5)

        jobs.join()
        received: list[Outcome] = []
        for _ in submitted:
            try:
                received.append(outcomes.get(timeout=5))
            except Empty as error:
                raise RuntimeError("an accepted job produced no outcome") from error

        for worker in workers:
            worker.join(timeout=10)
        if any(worker.is_alive() for worker in workers):
            raise TimeoutError("a pipeline worker did not exit")
        exitcodes = tuple(worker.exitcode for worker in workers)
        if any(code != 0 for code in exitcodes):
            raise RuntimeError(f"worker exit codes were {exitcodes}")
    finally:
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=5)
            if not worker.is_alive():
                worker.close()
        jobs.close()
        jobs.join_thread()
        outcomes.close()
        outcomes.join_thread()

    return sorted(received, key=lambda outcome: outcome.job_id), exitcodes


if __name__ == "__main__":
    demo_outcomes, demo_exitcodes = run_demo()
    for demo_outcome in demo_outcomes:
        print(demo_outcome)
    print(f"exitcodes={demo_exitcodes}")
