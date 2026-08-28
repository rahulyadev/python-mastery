"""Contrast completion-ordered futures with input-ordered executor mapping."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from threading import Event


GUARD_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class OrderingReport:
    """The two ordering contracts demonstrated by this module."""

    completion_order: tuple[str, ...]
    map_results: tuple[int, ...]


def controlled_job(job_id: str, started: Event, release: Event) -> str:
    """Announce readiness and return only when the owner releases this job."""
    started.set()
    if not release.wait(GUARD_TIMEOUT_SECONDS):
        raise TimeoutError(f"{job_id} was not released")
    return job_id


def square(value: int) -> int:
    """Return a deterministic mapped value."""
    return value * value


def run_completion_demo() -> tuple[str, ...]:
    """Release job-b before job-a and observe that completion order."""
    started = {"job-a": Event(), "job-b": Event()}
    release = {"job-a": Event(), "job-b": Event()}

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="order-demo") as executor:
        future_to_id = {
            executor.submit(
                controlled_job,
                job_id,
                started[job_id],
                release[job_id],
            ): job_id
            for job_id in ("job-a", "job-b")
        }

        if not all(event.wait(GUARD_TIMEOUT_SECONDS) for event in started.values()):
            for event in release.values():
                event.set()
            raise TimeoutError("both controlled jobs did not start")

        completions = as_completed(future_to_id, timeout=GUARD_TIMEOUT_SECONDS)
        observed: list[str] = []
        try:
            release["job-b"].set()
            job_b = next(future for future, job_id in future_to_id.items() if job_id == "job-b")
            job_b.result(timeout=GUARD_TIMEOUT_SECONDS)
            observed.append(future_to_id[next(completions)])

            release["job-a"].set()
            job_a = next(future for future, job_id in future_to_id.items() if job_id == "job-a")
            job_a.result(timeout=GUARD_TIMEOUT_SECONDS)
            observed.append(future_to_id[next(completions)])
        finally:
            for event in release.values():
                event.set()

    return tuple(observed)


def run_demo() -> OrderingReport:
    """Return completion order and a separate input-ordered map result."""
    completion_order = run_completion_demo()
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="map-demo") as executor:
        map_results = tuple(executor.map(square, (3, 1, 2)))
    return OrderingReport(completion_order, map_results)


def main() -> None:
    """Print both ordering contracts."""
    report = run_demo()
    print(f"completion order: {report.completion_order}")
    print(f"map results: {report.map_results}")


if __name__ == "__main__":
    main()
