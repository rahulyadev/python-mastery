"""Small, runnable sequence models for PY-BLT-040; Python 3.11+.

These are worked examples, not solutions to the protected practice exercises.
"""

from __future__ import annotations

from operator import itemgetter


def slice_trace(
    values: list[str], selection: slice
) -> tuple[tuple[int, int, int], list[int], list[str]]:
    """Return normalized bounds, visited positions, and the actual list slice.

    The bounds are suitable for range(), not for constructing a new raw slice:
    a normalized negative stop can be a sentinel, not an end-relative index.
    """
    normalized = selection.indices(len(values))
    positions = list(range(*normalized))
    return normalized, positions, values[selection]


def mutation_and_rebinding() -> tuple[list[int], list[int]]:
    """Keep an alias so the effects of += and + can be distinguished."""
    current = [10, 20]
    shared = current
    current += [30]
    current = current + [40]
    return current, shared


def stable_priority_order(jobs: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Return ascending priority order, preserving arrival order within ties.

    Inputs are (integer priority, string identifier) pairs. The input list is
    not reordered. This example deliberately uses immutable field values.
    """
    return sorted(jobs, key=itemgetter(0))


def main() -> None:
    values = list("ABCDEF")
    bounds, positions, selected = slice_trace(values, slice(None, None, -2))
    print(f"slice bounds: {bounds}")
    print(f"visited positions: {positions}")
    print(f"selected values: {selected}")

    current, shared = mutation_and_rebinding()
    print(f"current after += then +: {current}")
    print(f"earlier alias: {shared}")

    jobs = [(2, "job-c"), (1, "job-b"), (1, "job-a")]
    print(f"priority order: {stable_priority_order(jobs)}")
    print(f"arrival order unchanged: {jobs}")

    descending = range(17, 2, -4)
    print(f"descending range values: {list(descending)}")
    print(f"range slice: {descending[1:]} -> {list(descending[1:])}")


if __name__ == "__main__":
    main()
