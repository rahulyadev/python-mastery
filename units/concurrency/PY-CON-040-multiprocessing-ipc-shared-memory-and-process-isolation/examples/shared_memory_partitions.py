"""Partition a shared-memory integer buffer so workers never write the same slot."""

from __future__ import annotations

import multiprocessing as mp
import struct
from multiprocessing import shared_memory
from typing import Any


INTEGER = struct.Struct("!q")


def write_integer(buffer: memoryview, index: int, value: int) -> None:
    INTEGER.pack_into(buffer, index * INTEGER.size, value)


def read_integer(buffer: memoryview, index: int) -> int:
    return INTEGER.unpack_from(buffer, index * INTEGER.size)[0]


def scale_partition(
    name: str,
    start: int,
    stop: int,
    factor: int,
    completion_queue: Any,
) -> None:
    """Attach by name and mutate only the assigned half-open index range."""

    block = shared_memory.SharedMemory(name=name)
    try:
        for index in range(start, stop):
            write_integer(block.buf, index, read_integer(block.buf, index) * factor)
        completion_queue.put((start, stop))
    finally:
        block.close()


def run_demo() -> tuple[list[int], list[tuple[int, int]], tuple[int, ...]]:
    """Scale disjoint partitions and release the shared-memory block exactly once."""

    context = mp.get_context("spawn")
    initial = [1, 2, 3, 4, 5, 6]
    block = shared_memory.SharedMemory(create=True, size=len(initial) * INTEGER.size)
    completion_queue = context.Queue()
    workers: list[mp.Process] = []
    try:
        for index, value in enumerate(initial):
            write_integer(block.buf, index, value)

        partitions = [(0, 3), (3, len(initial))]
        workers = [
            context.Process(
                target=scale_partition,
                args=(block.name, start, stop, 10, completion_queue),
                name=f"shared-{start}-{stop}",
            )
            for start, stop in partitions
        ]
        for worker in workers:
            worker.start()

        completed = sorted(completion_queue.get(timeout=10) for _ in workers)
        for worker in workers:
            worker.join(timeout=10)
        if any(worker.is_alive() for worker in workers):
            raise TimeoutError("a shared-memory worker did not exit")
        exitcodes = tuple(worker.exitcode for worker in workers)
        if any(code != 0 for code in exitcodes):
            raise RuntimeError(f"worker exit codes were {exitcodes}")

        values = [read_integer(block.buf, index) for index in range(len(initial))]
    finally:
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=5)
            if not worker.is_alive():
                worker.close()
        completion_queue.close()
        completion_queue.join_thread()
        block.close()
        block.unlink()

    return values, completed, exitcodes


if __name__ == "__main__":
    demo_values, demo_partitions, demo_exitcodes = run_demo()
    print(f"values={demo_values}")
    print(f"partitions={demo_partitions}")
    print(f"exitcodes={demo_exitcodes}")
