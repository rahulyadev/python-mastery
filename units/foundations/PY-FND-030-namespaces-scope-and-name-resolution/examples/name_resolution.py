"""Demonstrate lexical name classification and lookup deterministically."""

from __future__ import annotations

import builtins
from dataclasses import dataclass


SERVICE = "payments"
DEFAULT_TIMEOUT = 30


@dataclass(frozen=True)
class ResolutionReport:
    """Values found through local, enclosing, global, and built-in scopes."""

    local_value: str
    enclosing_value: str
    global_value: str
    builtin_value: int


def resolve_request(request_id: str) -> ResolutionReport:
    """Return one stable observation from every part of the LEGB mnemonic."""
    prefix = "worker"

    def build_report() -> ResolutionReport:
        local_label = request_id.upper()
        return ResolutionReport(
            local_value=local_label,
            enclosing_value=prefix,
            global_value=SERVICE,
            builtin_value=len(local_label),
        )

    return build_report()


def compare_builtin_shadowing(values: list[str]) -> tuple[int, int]:
    """Contrast a shadowing local binding with explicit builtins access."""
    len = lambda items: -1  # noqa: E731,A001 - deliberate teaching example
    return len(values), builtins.len(values)


def unbound_local_error_name() -> str:
    """Expose static local classification without leaking an exception."""
    try:
        current = DEFAULT_TIMEOUT
    except UnboundLocalError as error:
        return type(error).__name__

    DEFAULT_TIMEOUT = current + 5  # noqa: F841 - makes the name local
    return "no error"


def main() -> None:
    """Print stable observations for direct execution."""
    report = resolve_request("req-7")
    shadowed, actual = compare_builtin_shadowing(["a", "b", "c"])

    print(f"local: {report.local_value}")
    print(f"enclosing: {report.enclosing_value}")
    print(f"global: {report.global_value}")
    print(f"builtin len: {report.builtin_value}")
    print(f"shadowed len: {shadowed}")
    print(f"builtins.len: {actual}")
    print(f"read-before-bind failure: {unbound_local_error_name()}")


if __name__ == "__main__":
    main()
