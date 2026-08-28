"""Use an explicit spawn process pool for an input-ordered CPU batch."""

import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass


@dataclass(frozen=True)
class Batch:
    """One immutable, picklable unit of synthetic work."""

    batch_id: str
    values: tuple[int, ...]


@dataclass(frozen=True)
class BatchSummary:
    """One immutable, picklable process-pool result."""

    batch_id: str
    count: int
    sum_of_squares: int


def summarize(batch: Batch) -> BatchSummary:
    """Compute a small CPU result in a worker process."""
    return BatchSummary(
        batch_id=batch.batch_id,
        count=len(batch.values),
        sum_of_squares=sum(value * value for value in batch.values),
    )


def run_demo() -> tuple[BatchSummary, ...]:
    """Run importable work through an explicitly spawned process pool."""
    batches = (
        Batch("batch-a", (1, 2, 3)),
        Batch("batch-b", (4, 5)),
        Batch("batch-c", (6,)),
    )
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=2, mp_context=context) as executor:
        return tuple(executor.map(summarize, batches))


def main() -> None:
    """Print input-ordered process results."""
    for summary in run_demo():
        print(
            f"{summary.batch_id}: count={summary.count}, "
            f"sum_of_squares={summary.sum_of_squares}"
        )


if __name__ == "__main__":
    main()
