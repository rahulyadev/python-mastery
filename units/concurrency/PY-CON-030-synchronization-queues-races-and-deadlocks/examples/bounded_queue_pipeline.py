"""Run a bounded worker queue with Python-version-aware graceful shutdown."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from queue import Queue
from threading import Thread


if sys.version_info >= (3, 13):
    from queue import ShutDown
else:

    class ShutDown(Exception):
        """Compatibility name; Python 3.11 workers stop via private sentinels."""


_STOP = object()


@dataclass(frozen=True, slots=True)
class Job:
    job_id: str
    payload: str


@dataclass(frozen=True, slots=True)
class Outcome:
    job_id: str
    value: str | None = None
    error: str | None = None


def normalize(job: Job) -> str:
    if job.payload == "INVALID":
        raise ValueError("synthetic invalid payload")
    return job.payload.strip().lower()


def run_demo() -> tuple[str, list[Outcome], bool]:
    tasks: Queue[Job | object] = Queue(maxsize=2)
    outcomes: Queue[Outcome] = Queue()

    def worker() -> None:
        while True:
            try:
                item = tasks.get()
            except ShutDown:
                return

            try:
                if item is _STOP:
                    return
                if not isinstance(item, Job):
                    raise TypeError("unexpected queue item")
                try:
                    value = normalize(item)
                except Exception as exc:
                    outcomes.put(
                        Outcome(
                            job_id=item.job_id,
                            error=f"{type(exc).__name__}: {exc}",
                        )
                    )
                else:
                    outcomes.put(Outcome(job_id=item.job_id, value=value))
            finally:
                tasks.task_done()

    workers = [
        Thread(name=f"normalizer-{index}", target=worker)
        for index in range(2)
    ]
    for thread in workers:
        thread.start()

    jobs = [
        Job("invoice-1", " READY "),
        Job("invoice-2", "INVALID"),
        Job("invoice-3", " PAID "),
    ]
    for job in jobs:
        tasks.put(job)

    if sys.version_info >= (3, 13):
        tasks.shutdown()
        shutdown_protocol = "Queue.shutdown"
    else:
        for _ in workers:
            tasks.put(_STOP)
        shutdown_protocol = "sentinels"

    tasks.join()
    for thread in workers:
        thread.join(timeout=2.0)
    workers_alive = any(thread.is_alive() for thread in workers)
    if workers_alive:
        raise RuntimeError("queue workers did not terminate")

    records = sorted(
        (outcomes.get_nowait() for _ in jobs),
        key=lambda outcome: outcome.job_id,
    )
    return shutdown_protocol, records, workers_alive


def main() -> None:
    shutdown_protocol, records, workers_alive = run_demo()
    print(f"shutdown_protocol={shutdown_protocol}")
    for record in records:
        result = f"ok:{record.value}" if record.error is None else f"error:{record.error}"
        print(f"{record.job_id}={result}")
    print(f"workers_alive={workers_alive}")


if __name__ == "__main__":
    main()
