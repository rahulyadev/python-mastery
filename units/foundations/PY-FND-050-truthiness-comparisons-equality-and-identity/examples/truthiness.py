"""Demonstrate truth-testing resolution and sentinel-safe boundaries."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import sys
import warnings


MISSING = object()


@dataclass(frozen=True)
class TruthProtocolReport:
    """Results and hook events from Python's truth-testing protocol."""

    bool_first_value: bool
    bool_first_events: tuple[str, ...]
    len_only_value: bool
    len_only_events: tuple[str, ...]
    plain_value: bool


@dataclass(frozen=True)
class NotImplementedTruthReport:
    """Version-sensitive outcome of truth-testing ``NotImplemented``."""

    outcome: str
    warning: str | None


class BoolFirst:
    """Expose that ``__bool__`` takes priority over ``__len__``."""

    def __init__(self, ready: bool, events: list[str]) -> None:
        self.ready = ready
        self.events = events

    def __bool__(self) -> bool:
        self.events.append("__bool__")
        return self.ready

    def __len__(self) -> int:
        self.events.append("__len__")
        return 0


class LenOnly:
    """Use ``__len__`` as the fallback truth hook."""

    def __init__(self, size: int, events: list[str]) -> None:
        self.size = size
        self.events = events

    def __len__(self) -> int:
        self.events.append("__len__")
        return self.size


class PlainObject:
    """Define no truth hook, so instances use the default truth value."""


class InvalidBool:
    """Deliberately violate the requirement that ``__bool__`` return bool."""

    def __bool__(self) -> int:  # type: ignore[override]
        return 1


class NegativeLength:
    """Deliberately violate the non-negative ``__len__`` contract."""

    def __len__(self) -> int:
        return -1


def truth_protocol_report() -> TruthProtocolReport:
    """Trace the ``__bool__`` -> ``__len__`` -> default resolution order."""
    events: list[str] = []
    bool_first_value = bool(BoolFirst(False, events))
    bool_first_events = tuple(events)

    events.clear()
    len_only_value = bool(LenOnly(2, events))
    len_only_events = tuple(events)

    return TruthProtocolReport(
        bool_first_value=bool_first_value,
        bool_first_events=bool_first_events,
        len_only_value=len_only_value,
        len_only_events=len_only_events,
        plain_value=bool(PlainObject()),
    )


def invalid_truth_hook_errors() -> tuple[str, str]:
    """Return the exception types produced by two invalid truth hooks."""
    errors: list[str] = []
    for value in (InvalidBool(), NegativeLength()):
        try:
            bool(value)
        except (TypeError, ValueError) as error:
            errors.append(type(error).__name__)

    return errors[0], errors[1]


def setting_or_default(
    settings: Mapping[str, object],
    key: str,
    default: object,
) -> object:
    """Use a private sentinel so every present value remains valid data."""
    value = settings.get(key, MISSING)
    if value is MISSING:
        return default
    return value


def sentinel_report() -> tuple[object, object, object, object]:
    """Show that absence differs from present ``None`` and other falsy values."""
    settings: dict[str, object] = {
        "zero": 0,
        "none": None,
        "empty": "",
    }
    return (
        setting_or_default(settings, "absent", "fallback"),
        setting_or_default(settings, "zero", "fallback"),
        setting_or_default(settings, "none", "fallback"),
        setting_or_default(settings, "empty", "fallback"),
    )


def not_implemented_truth_report() -> NotImplementedTruthReport:
    """Record the 3.11-to-3.14 boundary without assuming the active runtime."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            value = bool(NotImplemented)
        except TypeError:
            return NotImplementedTruthReport(outcome="raises TypeError", warning=None)

    warning_name = type(caught[0].message).__name__ if caught else None
    return NotImplementedTruthReport(
        outcome=f"returns {value!r}",
        warning=warning_name,
    )


def main() -> None:
    """Print stable observations for direct execution."""
    protocol = truth_protocol_report()
    print(
        "truth protocol: "
        f"bool-first={protocol.bool_first_value}; "
        f"events={' -> '.join(protocol.bool_first_events)}"
    )
    print(
        "truth protocol: "
        f"len-only={protocol.len_only_value}; "
        f"events={' -> '.join(protocol.len_only_events)}"
    )
    print(f"truth protocol: plain={protocol.plain_value}; events=none")
    print(f"sentinel values: {sentinel_report()!r}")
    print(f"invalid truth hooks: {invalid_truth_hook_errors()!r}")

    not_implemented = not_implemented_truth_report()
    print(
        "NotImplemented truth: "
        f"python={sys.version_info.major}.{sys.version_info.minor}; "
        f"outcome={not_implemented.outcome}; "
        f"warning={not_implemented.warning or 'none'}"
    )


if __name__ == "__main__":
    main()
