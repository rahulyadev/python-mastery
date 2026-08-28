"""Capture an uncaught thread failure without pretending that join re-raises it."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from queue import Queue


@dataclass(frozen=True, slots=True)
class FailureSummary:
    """A small immutable report that does not retain traceback or thread objects."""

    thread_name: str
    exception_type: str
    message: str


def fail_payment() -> None:
    raise RuntimeError("synthetic payment failure")


def main() -> None:
    failures: Queue[FailureSummary] = Queue()

    def record_failure(args: threading.ExceptHookArgs) -> None:
        thread_name = args.thread.name if args.thread is not None else "<unknown>"
        exception_type = args.exc_type.__name__
        failures.put(
            FailureSummary(
                thread_name=thread_name,
                exception_type=exception_type,
                message=str(args.exc_value),
            )
        )

    original_hook = threading.excepthook
    threading.excepthook = record_failure
    try:
        worker = threading.Thread(name="payment-worker", target=fail_payment)
        worker.start()
        worker.join()
    finally:
        threading.excepthook = original_hook

    print("join returned normally")
    print(f"worker alive: {worker.is_alive()}")
    failure = failures.get_nowait()
    print(
        "captured: "
        f"{failure.thread_name} {failure.exception_type}: {failure.message}"
    )


if __name__ == "__main__":
    main()
