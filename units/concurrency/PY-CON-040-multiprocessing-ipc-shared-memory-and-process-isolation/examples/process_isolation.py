"""Show that ordinary mutable objects are isolated across a process boundary."""

from __future__ import annotations

import multiprocessing as mp
import os
from dataclasses import dataclass
from multiprocessing.connection import Connection


@dataclass(frozen=True)
class ChildReport:
    """A picklable snapshot sent from the child to the parent."""

    pid: int
    values: tuple[int, ...]


def mutate_child_copy(values: list[int], sender: Connection) -> None:
    """Mutate the child-visible list and report its independent state."""

    try:
        values.append(99)
        sender.send(ChildReport(pid=os.getpid(), values=tuple(values)))
    finally:
        sender.close()


def run_demo(start_method: str = "spawn") -> tuple[tuple[int, ...], ChildReport, int]:
    """Return the parent state, child state, and parent PID."""

    context = mp.get_context(start_method)
    parent_values = [1, 2, 3]
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(
        target=mutate_child_copy,
        args=(parent_values, sender),
        name="isolation-demo",
    )

    process.start()
    sender.close()
    try:
        if not receiver.poll(10):
            raise TimeoutError("child did not report its state")
        report = receiver.recv()
        process.join(timeout=10)
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
            raise TimeoutError("child did not exit")
        if process.exitcode != 0:
            raise RuntimeError(f"child exited with code {process.exitcode}")
    finally:
        receiver.close()
        if not process.is_alive():
            process.close()

    return tuple(parent_values), report, os.getpid()


if __name__ == "__main__":
    parent_state, child_state, parent_pid = run_demo()
    print(f"parent pid={parent_pid} values={parent_state}")
    print(f"child pid={child_state.pid} values={child_state.values}")
