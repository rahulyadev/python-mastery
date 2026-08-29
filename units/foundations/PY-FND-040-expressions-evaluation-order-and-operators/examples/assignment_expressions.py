"""Demonstrate assignment timing, grouping, and assignment expressions."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class AssignmentTrace:
    """Normal and augmented subscript-assignment observations."""

    normal_value: int
    normal_events: tuple[str, ...]
    augmented_value: int
    augmented_events: tuple[str, ...]


def assignment_trace() -> AssignmentTrace:
    """Contrast normal assignment with augmented-assignment target timing."""
    events: list[str] = []
    box = {"slot": 10}

    def target() -> dict[str, int]:
        events.append("target-container")
        return box

    def key() -> str:
        events.append("target-key")
        return "slot"

    def right_hand_side() -> int:
        events.append("rhs")
        return 5

    target()[key()] = right_hand_side()
    normal_value = box["slot"]
    normal_events = tuple(events)

    box["slot"] = 10
    events.clear()
    target()[key()] += right_hand_side()

    return AssignmentTrace(
        normal_value=normal_value,
        normal_events=normal_events,
        augmented_value=box["slot"],
        augmented_events=tuple(events),
    )


def power_and_unary_results() -> tuple[int, int, int, int, float]:
    """Return parenthesized counterexamples for power and unary grouping."""
    return -2**2, (-2) ** 2, 2**3**2, (2**3) ** 2, 2**-2


def consume_chunks(read: Callable[[], bytes]) -> tuple[bytes, ...]:
    """Read non-empty chunks once each by binding and testing one value."""
    chunks: list[bytes] = []
    while chunk := read():
        chunks.append(chunk)
    return tuple(chunks)


def main() -> None:
    """Print stable observations for direct execution."""
    report = assignment_trace()
    print(
        "normal assignment: "
        f"value={report.normal_value}; events={' -> '.join(report.normal_events)}"
    )
    print(
        "augmented assignment: "
        f"value={report.augmented_value}; "
        f"events={' -> '.join(report.augmented_events)}"
    )
    print(f"power and unary: {power_and_unary_results()!r}")

    source = iter((b"alpha", b"beta", b""))
    print(f"walrus chunks: {consume_chunks(lambda: next(source))!r}")


if __name__ == "__main__":
    main()
