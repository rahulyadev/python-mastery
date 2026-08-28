"""Expose a lost update with barriers, then protect the same transition."""

from __future__ import annotations

import platform
import sys
import sysconfig
from queue import Queue
from threading import Barrier, Lock, Thread
from typing import Callable


def run_threads(target: Callable[[], None], count: int) -> None:
    failures: Queue[BaseException] = Queue()

    def guarded_target() -> None:
        try:
            target()
        except BaseException as exc:
            failures.put(exc)

    workers = [
        Thread(name=f"increment-{index}", target=guarded_target)
        for index in range(count)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=2.0)
    if any(worker.is_alive() for worker in workers):
        raise RuntimeError("an experiment worker did not terminate")
    if not failures.empty():
        raise failures.get_nowait()


def controlled_lost_update() -> int:
    shared = [0]
    both_have_read = Barrier(2, timeout=2.0)

    def increment() -> None:
        snapshot = shared[0]
        both_have_read.wait()
        shared[0] = snapshot + 1

    run_threads(increment, count=2)
    return shared[0]


def locked_updates() -> int:
    shared = [0]
    transition_lock = Lock()

    def increment() -> None:
        with transition_lock:
            shared[0] += 1

    run_threads(increment, count=2)
    return shared[0]


def main() -> None:
    unsafe_final = controlled_lost_update()
    locked_final = locked_updates()
    is_gil_enabled = getattr(sys, "_is_gil_enabled", None)
    gil_enabled = is_gil_enabled() if is_gil_enabled is not None else "unavailable"
    free_threaded_build = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))

    print(f"implementation={sys.implementation.name}")
    print(f"version={platform.python_version()}")
    print(f"free_threaded_build={free_threaded_build}")
    print(f"gil_enabled={gil_enabled}")
    print("attempted_updates=2")
    print(f"controlled_unsafe_final={unsafe_final}")
    print(f"controlled_lost_updates={2 - unsafe_final}")
    print(f"locked_final={locked_final}")
    print(f"locked_invariant_preserved={locked_final == 2}")


if __name__ == "__main__":
    main()
