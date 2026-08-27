"""Observe default, empty, and copied context behavior for Python 3.14 threads."""

from __future__ import annotations

import sys
import sysconfig
from contextvars import Context, ContextVar, copy_context
from dataclasses import dataclass
from queue import Queue
from threading import Thread, local


REQUEST_ID: ContextVar[str] = ContextVar("request_id", default="UNSET")
THREAD_STATE = local()


@dataclass(frozen=True, slots=True)
class Observation:
    label: str
    context_before: str
    context_after: str
    thread_local_before: str
    thread_local_after: str


def main() -> None:
    if sys.version_info < (3, 14):
        raise RuntimeError("this experiment requires Thread(context=...), added in Python 3.14")

    observations: Queue[Observation] = Queue()
    THREAD_STATE.label = "main-thread"

    def observe(label: str) -> None:
        context_before = REQUEST_ID.get()
        thread_local_before = getattr(THREAD_STATE, "label", "UNSET")
        REQUEST_ID.set(f"worker-context:{label}")
        THREAD_STATE.label = f"worker-thread-local:{label}"
        observations.put(
            Observation(
                label=label,
                context_before=context_before,
                context_after=REQUEST_ID.get(),
                thread_local_before=thread_local_before,
                thread_local_after=THREAD_STATE.label,
            )
        )

    first_token = REQUEST_ID.set("request-at-snapshot")
    snapshot = copy_context()
    second_token = REQUEST_ID.set("request-at-start")
    try:
        workers = [
            Thread(name="default-context", target=lambda: observe("default")),
            Thread(name="empty-context", target=lambda: observe("empty"), context=Context()),
            Thread(name="copied-context", target=lambda: observe("copied"), context=snapshot),
        ]

        # Sequential start/join removes scheduling order as a variable. The experiment is
        # about initial context, not simultaneous execution.
        for worker in workers:
            worker.start()
            worker.join()

        gil_probe = getattr(sys, "_is_gil_enabled", None)
        gil_enabled = gil_probe() if callable(gil_probe) else "unavailable"
        print(f"implementation={sys.implementation.name}")
        print(f"version={sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print(f"free_threaded_build={bool(sysconfig.get_config_var('Py_GIL_DISABLED'))}")
        print(f"gil_enabled={gil_enabled}")
        print(f"thread_inherit_context={sys.flags.thread_inherit_context}")

        records = sorted(
            (observations.get_nowait() for _ in workers),
            key=lambda observation: observation.label,
        )
        for record in records:
            print(
                f"{record.label}: context_before={record.context_before}, "
                f"context_after={record.context_after}, "
                f"tls_before={record.thread_local_before}, "
                f"tls_after={record.thread_local_after}"
            )
        print(f"main: context={REQUEST_ID.get()}, tls={THREAD_STATE.label}")
    finally:
        REQUEST_ID.reset(second_token)
        REQUEST_ID.reset(first_token)


if __name__ == "__main__":
    main()
