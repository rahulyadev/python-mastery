"""Build an eager batch plan from a bounded list of synthetic job identifiers.

The list holds an editable plan, each tuple fixes one batch's membership, and
range supplies offsets without allocating an offset list. Python 3.11+.
"""

from __future__ import annotations


def build_batch_plan(job_ids: list[str], batch_size: int) -> list[tuple[str, ...]]:
    """Preserve order and duplicates; return nonempty tuples of at most batch_size.

    Policy: require a list of strings and a positive plain int batch size;
    bool is rejected even though Python itself accepts bool in range().
    No input mutation occurs. The caller must keep input stable during the call.
    Later edits to the input list cannot change the returned tuple memberships.
    This is an eager, in-memory example, not a streaming or concurrency API.
    """
    if not isinstance(job_ids, list):
        raise TypeError("job_ids must be a list of strings")
    if not all(isinstance(job_id, str) for job_id in job_ids):
        raise TypeError("every job identifier must be a string")
    if type(batch_size) is not int:
        raise TypeError("batch_size must be a plain int, not bool")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    plan: list[tuple[str, ...]] = []
    for start in range(0, len(job_ids), batch_size):
        plan.append(tuple(job_ids[start : start + batch_size]))
    return plan


def main() -> None:
    incoming = ["job-a", "job-b", "job-c", "job-d", "job-e"]
    plan = build_batch_plan(incoming, 2)
    print(f"batch plan: {plan}")
    incoming[0] = "replacement"
    incoming.append("job-f")
    print(f"input after later edits: {incoming}")
    print(f"existing batch plan: {plan}")


if __name__ == "__main__":
    main()
