"""Gracefully close and join a process pool after collecting pure results."""

from __future__ import annotations

import multiprocessing as mp
from dataclasses import dataclass


@dataclass(frozen=True)
class Batch:
    batch_id: str
    values: tuple[int, ...]


@dataclass(frozen=True)
class Summary:
    batch_id: str
    count: int
    sum_of_squares: int


def summarize(batch: Batch) -> Summary:
    """A top-level, side-effect-free worker function."""

    return Summary(
        batch_id=batch.batch_id,
        count=len(batch.values),
        sum_of_squares=sum(value * value for value in batch.values),
    )


def run_demo() -> list[Summary]:
    """Map bounded batches, then close and join every pool worker."""

    context = mp.get_context("spawn")
    batches = [
        Batch("batch-a", (1, 2, 3)),
        Batch("batch-b", (4, 5)),
        Batch("batch-c", (6,)),
    ]
    pool = context.Pool(processes=2, maxtasksperchild=2)
    try:
        summaries = pool.map(summarize, batches, chunksize=1)
    except BaseException:
        pool.terminate()
        pool.join()
        raise
    else:
        pool.close()
        pool.join()
    return summaries


if __name__ == "__main__":
    for demo_summary in run_demo():
        print(demo_summary)
