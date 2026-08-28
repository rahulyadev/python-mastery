"""Observe whether a child sees a parent mutation of module-level state."""

from __future__ import annotations

import multiprocessing as mp
import os
from dataclasses import dataclass
from multiprocessing.connection import Connection


MODULE_TOKEN = "import-default"


@dataclass(frozen=True)
class Observation:
    method: str
    parent_pid: int
    child_pid: int
    child_token: str
    exitcode: int


def observe_token(sender: Connection) -> None:
    """Report module state as observed inside the child."""

    try:
        sender.send((os.getpid(), MODULE_TOKEN))
    finally:
        sender.close()


def observe_method(method: str) -> Observation:
    """Run one child using the requested available start method."""

    context = mp.get_context(method)
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=observe_token, args=(sender,), name=f"observe-{method}")
    process.start()
    sender.close()
    try:
        if not receiver.poll(10):
            raise TimeoutError(f"{method} child did not report")
        child_pid, child_token = receiver.recv()
        process.join(timeout=10)
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
            raise TimeoutError(f"{method} child did not exit")
        exitcode = process.exitcode
        if exitcode != 0:
            raise RuntimeError(f"{method} child exited with code {exitcode}")
    finally:
        receiver.close()
        if not process.is_alive():
            process.close()
    return Observation(method, os.getpid(), child_pid, child_token, exitcode)


def run_experiment() -> list[Observation]:
    """Mutate parent state and observe every start method on this platform."""

    global MODULE_TOKEN
    MODULE_TOKEN = "parent-mutated"
    return [observe_method(method) for method in mp.get_all_start_methods()]


if __name__ == "__main__":
    for observation in run_experiment():
        print(
            f"method={observation.method} "
            f"parent={observation.parent_pid} child={observation.child_pid} "
            f"token={observation.child_token!r} exitcode={observation.exitcode}"
        )
