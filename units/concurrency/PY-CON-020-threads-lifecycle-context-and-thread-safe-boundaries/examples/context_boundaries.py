"""Contrast explicit Context propagation with thread-local isolation."""

from __future__ import annotations

import sys
from contextvars import Context, ContextVar, copy_context
from dataclasses import dataclass
from queue import Queue
from threading import Thread, local
from typing import Callable


REQUEST_ID: ContextVar[str] = ContextVar("request_id", default="UNSET")
THREAD_STATE = local()


@dataclass(frozen=True, slots=True)
class Observation:
    label: str
    context_value: str
    thread_local_before: str
    thread_local_after: str


def launch_in_context(*, name: str, context: Context, target: Callable[[], None]) -> Thread:
    """Use Python 3.14's API, with the explicit Python 3.11 equivalent."""

    if sys.version_info >= (3, 14):
        return Thread(name=name, target=target, context=context)
    return Thread(name=name, target=context.run, args=(target,))


def main() -> None:
    observations: Queue[Observation] = Queue()
    THREAD_STATE.label = "main"

    def observe(label: str) -> None:
        before = getattr(THREAD_STATE, "label", "UNSET")
        THREAD_STATE.label = f"worker:{label}"
        observations.put(
            Observation(
                label=label,
                context_value=REQUEST_ID.get(),
                thread_local_before=before,
                thread_local_after=THREAD_STATE.label,
            )
        )

    first_token = REQUEST_ID.set("request-at-snapshot")
    snapshot = copy_context()
    second_token = REQUEST_ID.set("request-in-main-after-snapshot")
    try:
        workers = [
            launch_in_context(
                name="snapshot-worker",
                context=snapshot,
                target=lambda: observe("snapshot"),
            ),
            launch_in_context(
                name="empty-worker",
                context=Context(),
                target=lambda: observe("empty"),
            ),
        ]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()

        records = sorted(
            (observations.get_nowait() for _ in workers),
            key=lambda observation: observation.label,
        )
        for record in records:
            print(
                f"{record.label}: context={record.context_value}, "
                f"tls_before={record.thread_local_before}, "
                f"tls_after={record.thread_local_after}"
            )
        print(f"main: context={REQUEST_ID.get()}, tls={THREAD_STATE.label}")
    finally:
        REQUEST_ID.reset(second_token)
        REQUEST_ID.reset(first_token)


if __name__ == "__main__":
    main()
