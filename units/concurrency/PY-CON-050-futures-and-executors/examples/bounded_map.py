"""Demonstrate Python 3.14 Executor.map backpressure with a controlled source."""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from threading import Event


GUARD_TIMEOUT_SECONDS = 5.0


def recording_source(consumed: list[int], count: int) -> Iterator[int]:
    """Record each value when the map implementation requests it."""
    for value in range(count):
        consumed.append(value)
        yield value


def blocked_double(value: int, release: Event) -> int:
    """Wait for owner release, then double one input."""
    if not release.wait(GUARD_TIMEOUT_SECONDS):
        raise TimeoutError(f"input {value} was not released")
    return value * 2


def run_demo() -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return source consumption before release and all input-ordered results."""
    consumed: list[int] = []
    release = Event()

    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="buffer-demo") as executor:
        try:
            mapped = executor.map(
                blocked_double,
                recording_source(consumed, count=4),
                repeat(release),
                timeout=GUARD_TIMEOUT_SECONDS,
                buffersize=2,
            )
            consumed_before_release = tuple(consumed)
            release.set()
            results = tuple(mapped)
        finally:
            release.set()

    return consumed_before_release, results


def main() -> None:
    """Print the bounded source observation and results."""
    consumed, results = run_demo()
    print(f"consumed before release: {consumed}")
    print(f"results: {results}")


if __name__ == "__main__":
    main()
