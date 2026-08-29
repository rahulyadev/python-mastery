"""Maintainable text-boundary examples for PY-BLT-020."""

from __future__ import annotations

from dataclasses import dataclass
import unicodedata

from unicode_models import comparison_key


@dataclass(frozen=True)
class PreparedLabel:
    """Keep user-facing text separate from its search-only comparison key."""

    display: str
    search_key: str


def prepare_label(raw: str) -> PreparedLabel:
    """Validate, trim, and canonically compose a user-facing label."""
    if not isinstance(raw, str):
        raise TypeError("raw must be str")

    display = unicodedata.normalize("NFC", raw.strip())
    if not display:
        raise ValueError("label cannot be blank")
    if not display.isprintable():
        raise ValueError("label cannot contain control characters")

    return PreparedLabel(
        display=display,
        search_key=comparison_key(display, form="NFC", caseless=True),
    )


def parse_pipe_record(record: str, *, expected_fields: int = 3) -> tuple[str, ...]:
    """Split a deliberately simple record while preserving empty fields."""
    if not isinstance(record, str):
        raise TypeError("record must be str")
    if type(expected_fields) is not int:
        raise TypeError("expected_fields must be a plain integer")
    if expected_fields < 1:
        raise ValueError("expected_fields must be positive")

    fields = tuple(record.split("|"))
    if len(fields) != expected_fields:
        raise ValueError(f"expected {expected_fields} fields, received {len(fields)}")
    return fields


def remove_route_prefix(route: str, prefix: str = "/api/") -> str:
    """Remove one literal prefix rather than stripping a set of characters."""
    if not isinstance(route, str) or not isinstance(prefix, str):
        raise TypeError("route and prefix must be str")
    return route.removeprefix(prefix)


def format_request_summary(
    request_id: str,
    label: PreparedLabel,
    *,
    latency_ms: float,
) -> str:
    """Render a deterministic diagnostic string with explicit conversions."""
    if not isinstance(request_id, str):
        raise TypeError("request_id must be str")
    if not isinstance(label, PreparedLabel):
        raise TypeError("label must be PreparedLabel")
    if type(latency_ms) not in {int, float}:
        raise TypeError("latency_ms must be a plain int or float")
    if latency_ms < 0:
        raise ValueError("latency_ms cannot be negative")

    return (
        f"request={request_id!r} "
        f"label={label.display!r} "
        f"latency_ms={latency_ms:,.2f}"
    )


def main() -> None:
    """Print representative boundary results for direct execution."""
    label = prepare_label("  Cafe\u0301  ")
    print(f"label: {label!r}")
    print(f"record: {parse_pipe_record('evt-7||ready')!r}")
    print(f"route: {remove_route_prefix('/api/ping')!r}")
    print(format_request_summary("req-7", label, latency_ms=1234.5))


if __name__ == "__main__":
    main()
