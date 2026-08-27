"""Model concurrent interleaving without claiming parallel execution.

This program is intentionally deterministic. It uses generators and one Python
thread; it does not create operating-system threads, perform I/O, or run tasks
in parallel.
"""

from collections.abc import Iterable, Iterator, Sequence


def make_task(name: str, phases: Sequence[str]) -> Iterator[str]:
    """Yield one trace event per conceptual task phase."""
    for phase in phases:
        yield f"{name}: {phase}"


def round_robin(tasks: Iterable[Iterator[str]]) -> list[str]:
    """Advance each unfinished task once per round and return its event trace."""
    active = list(tasks)
    events: list[str] = []

    while active:
        next_round: list[Iterator[str]] = []
        for task in active:
            try:
                events.append(next(task))
            except StopIteration:
                continue
            next_round.append(task)
        active = next_round

    return events


def main() -> None:
    """Print a deterministic, single-lane interleaving trace."""
    api = make_task(
        "api",
        ("send request", "resume with response", "render"),
    )
    worker = make_task(
        "worker",
        ("validate job", "compute result", "persist"),
    )

    for event in round_robin((api, worker)):
        print(event)


if __name__ == "__main__":
    main()
