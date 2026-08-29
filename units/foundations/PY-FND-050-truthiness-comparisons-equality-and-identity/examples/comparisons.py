"""Demonstrate comparison chains, equality dispatch, and identity."""

from __future__ import annotations

from dataclasses import dataclass
from types import NotImplementedType


@dataclass(frozen=True)
class ChainTrace:
    """The Boolean result and observable events from one comparison chain."""

    result: bool
    events: tuple[str, ...]


@dataclass(frozen=True)
class EqualityIdentityReport:
    """Separate type-defined equality from object identity."""

    distinct_equal: bool
    distinct_identical: bool
    alias_equal: bool
    alias_identical: bool
    unsupported_equal: bool
    direct_unsupported_is_not_implemented: bool


@dataclass(frozen=True)
class NanReport:
    """Record the deliberate non-reflexive equality of one NaN object."""

    equal_to_self: bool
    unequal_to_self: bool
    identical_to_self: bool


class OrderedProbe:
    """Record rich-ordering calls while comparing integer payloads."""

    def __init__(self, label: str, value: int, events: list[str]) -> None:
        self.label = label
        self.value = value
        self.events = events

    def __lt__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, OrderedProbe):
            return NotImplemented
        self.events.append(f"compare:{self.label}<{other.label}")
        return self.value < other.value

    def __le__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, OrderedProbe):
            return NotImplemented
        self.events.append(f"compare:{self.label}<={other.label}")
        return self.value <= other.value


class ValueToken:
    """Define equality by a domain key and decline unsupported types."""

    def __init__(self, key: str) -> None:
        self.key = key

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, ValueToken):
            return NotImplemented
        return self.key == other.key


def make_probe(
    events: list[str],
    label: str,
    value: int,
) -> OrderedProbe:
    """Record expression evaluation before returning a comparable object."""
    events.append(f"evaluate:{label}")
    return OrderedProbe(label, value, events)


def successful_chain_trace() -> ChainTrace:
    """Show that the middle expression is evaluated once and then reused."""
    events: list[str] = []
    result = (
        make_probe(events, "low", 1)
        < make_probe(events, "middle", 5)
        <= make_probe(events, "high", 10)
    )
    return ChainTrace(result=result, events=tuple(events))


def short_circuited_chain_trace() -> ChainTrace:
    """Show that a false first comparison skips the rightmost expression."""
    events: list[str] = []
    result = (
        make_probe(events, "left", 9)
        < make_probe(events, "middle", 5)
        < make_probe(events, "right-skipped", 10)
    )
    return ChainTrace(result=result, events=tuple(events))


def equality_identity_report() -> EqualityIdentityReport:
    """Contrast a distinct equal value, an alias, and unsupported equality."""
    left = ValueToken("job-7")
    equal_value = ValueToken("job-7")
    alias = left

    return EqualityIdentityReport(
        distinct_equal=left == equal_value,
        distinct_identical=left is equal_value,
        alias_equal=left == alias,
        alias_identical=left is alias,
        unsupported_equal=left == "job-7",
        direct_unsupported_is_not_implemented=(
            left.__eq__("job-7") is NotImplemented
        ),
    )


def nan_report() -> NanReport:
    """Show that a value protocol can reject equality with the same object."""
    value = float("nan")
    return NanReport(
        equal_to_self=value == value,
        unequal_to_self=value != value,
        identical_to_self=value is value,
    )


def format_chain(label: str, trace: ChainTrace) -> str:
    """Format a trace without exposing object addresses."""
    return (
        f"{label}: result={trace.result}; "
        f"events={' → '.join(trace.events)}"
    )


def main() -> None:
    """Print stable observations for direct execution."""
    print(format_chain("chain success", successful_chain_trace()))
    print(format_chain("chain short-circuit", short_circuited_chain_trace()))

    equality = equality_identity_report()
    print(
        "equality and identity: "
        f"distinct=(equal={equality.distinct_equal}, "
        f"identical={equality.distinct_identical}); "
        f"alias=(equal={equality.alias_equal}, "
        f"identical={equality.alias_identical}); "
        f"unsupported-equal={equality.unsupported_equal}; "
        "direct-unsupported-is-NotImplemented="
        f"{equality.direct_unsupported_is_not_implemented}"
    )

    nan = nan_report()
    print(
        "NaN: "
        f"equal-to-self={nan.equal_to_self}; "
        f"unequal-to-self={nan.unequal_to_self}; "
        f"identical-to-self={nan.identical_to_self}"
    )


if __name__ == "__main__":
    main()
