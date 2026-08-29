"""Demonstrate expression grouping and evaluation order deterministically."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


def mark(events: list[str], label: str, value: T) -> T:
    """Record one evaluation event and return the supplied value unchanged."""
    events.append(label)
    return value


@dataclass(frozen=True)
class ValueTrace:
    """A resulting value paired with the events that produced it."""

    value: object
    events: tuple[str, ...]


@dataclass(frozen=True)
class ShortCircuitTrace:
    """Values and events from three Boolean and one conditional expression."""

    values: tuple[object, ...]
    events: tuple[str, ...]


def precedence_trace() -> ValueTrace:
    """Separate multiplication grouping from left-to-right operand evaluation."""
    events: list[str] = []
    value = (
        mark(events, "left", 10)
        + mark(events, "factor", 3) * mark(events, "count", 4)
    )
    return ValueTrace(value=value, events=tuple(events))


def power_trace() -> ValueTrace:
    """Show right-grouped exponentiation with left-to-right operand evaluation."""
    events: list[str] = []
    value = (
        mark(events, "base", 2)
        ** mark(events, "inner-exponent", 3)
        ** mark(events, "outer-exponent", 2)
    )
    return ValueTrace(value=value, events=tuple(events))


def short_circuit_trace() -> ShortCircuitTrace:
    """Expose which operands and conditional branches are actually evaluated."""
    events: list[str] = []

    and_value = mark(events, "and-left", 0) and mark(
        events,
        "and-right-skipped",
        "unreachable",
    )
    cached_value = mark(events, "or-left", "cached") or mark(
        events,
        "or-right-skipped",
        "unreachable",
    )
    fallback_value = mark(events, "fallback-left", "") or mark(
        events,
        "fallback-right",
        "loaded",
    )
    conditional_value = (
        mark(events, "if-branch", "ready")
        if mark(events, "condition", True)
        else mark(events, "else-branch-skipped", "fallback")
    )

    return ShortCircuitTrace(
        values=(and_value, cached_value, fallback_value, conditional_value),
        events=tuple(events),
    )


def call_trace() -> ValueTrace:
    """Show that the callable and arguments are evaluated before invocation."""
    events: list[str] = []

    def build_handler():
        events.append("callee")

        def handler(left: int, *, right: int) -> int:
            events.append("invoke")
            return left + right

        return handler

    value = build_handler()(
        mark(events, "positional", 3),
        right=mark(events, "keyword", 4),
    )
    return ValueTrace(value=value, events=tuple(events))


def main() -> None:
    """Print stable traces for direct execution."""
    for label, report in (
        ("precedence", precedence_trace()),
        ("power", power_trace()),
        ("call", call_trace()),
    ):
        print(f"{label}: value={report.value!r}; events={' -> '.join(report.events)}")

    short = short_circuit_trace()
    print(
        "short-circuit: "
        f"values={short.values!r}; events={' -> '.join(short.events)}"
    )


if __name__ == "__main__":
    main()
