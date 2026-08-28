"""Expose running, cancelled, successful, and failed future outcomes deterministically.

Events control the only worker without using sleeps. The bounded waits are test
guards, not scheduling assumptions or application cancellation.
"""

from concurrent.futures import CancelledError, ThreadPoolExecutor
from dataclasses import dataclass
from threading import Event


GUARD_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class LifecycleReport:
    """Owner-visible outcomes from one controlled executor lifecycle."""

    running_cancel_succeeded: bool
    queued_cancel_succeeded: bool
    running_result: int
    queued_result_category: str
    failure_type: str
    failure_message: str


def controlled_value(started: Event, release: Event, value: int) -> int:
    """Announce that execution started, then return only after owner release."""
    started.set()
    if not release.wait(GUARD_TIMEOUT_SECONDS):
        raise TimeoutError("owner did not release the controlled worker")
    return value


def identity(value: int) -> int:
    """Return a value; cancellation prevents this call from starting."""
    return value


def raise_synthetic_failure() -> None:
    """Raise one predictable application exception inside a healthy worker."""
    raise ValueError("synthetic worker failure")


def run_demo() -> LifecycleReport:
    """Run a single-worker lifecycle and return every terminal classification."""
    started = Event()
    release = Event()

    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="future-demo") as executor:
        running = executor.submit(controlled_value, started, release, 21)
        if not started.wait(GUARD_TIMEOUT_SECONDS):
            release.set()
            raise TimeoutError("controlled worker did not start")

        queued = executor.submit(identity, 99)
        failed = executor.submit(raise_synthetic_failure)

        running_cancel_succeeded = running.cancel()
        queued_cancel_succeeded = queued.cancel()
        release.set()

        running_result = running.result(timeout=GUARD_TIMEOUT_SECONDS)

        try:
            queued.result(timeout=GUARD_TIMEOUT_SECONDS)
        except CancelledError as error:
            queued_result_category = type(error).__name__
        else:
            raise AssertionError("queued future unexpectedly ran")

        try:
            failed.result(timeout=GUARD_TIMEOUT_SECONDS)
        except ValueError as error:
            failure_type = type(error).__name__
            failure_message = str(error)
        else:
            raise AssertionError("failing future unexpectedly returned")

    return LifecycleReport(
        running_cancel_succeeded=running_cancel_succeeded,
        queued_cancel_succeeded=queued_cancel_succeeded,
        running_result=running_result,
        queued_result_category=queued_result_category,
        failure_type=failure_type,
        failure_message=failure_message,
    )


def main() -> None:
    """Print the deterministic owner-visible lifecycle."""
    report = run_demo()
    print(f"running cancel succeeded: {report.running_cancel_succeeded}")
    print(f"queued cancel succeeded: {report.queued_cancel_succeeded}")
    print(f"running result: {report.running_result}")
    print(f"queued result category: {report.queued_result_category}")
    print(f"failure: {report.failure_type}: {report.failure_message}")


if __name__ == "__main__":
    main()
