"""Structural pattern-matching examples for PY-FND-060."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Signal(Enum):
    """Qualified enum members are value patterns rather than captures."""

    START = "start"
    STOP = "stop"


@dataclass(frozen=True)
class RetryCommand:
    """A domain object that supports positional and keyword class patterns."""

    job_id: str
    attempts: int


@dataclass(frozen=True)
class DispatchResult:
    """A stable result from the example event router."""

    route: str
    identifier: str | None
    note: str


def dispatch_event(event: object) -> DispatchResult:
    """Route by data shape, captured values, guards, and source-order priority."""
    match event:
        case {
            "kind": "job.created",
            "job_id": str(job_id),
            **remaining,
        }:
            return DispatchResult(
                route="create",
                identifier=job_id,
                note=f"extra-fields={len(remaining)}",
            )

        case RetryCommand(job_id, attempts) if attempts > 0:
            return DispatchResult(
                route="retry",
                identifier=job_id,
                note=f"attempts={attempts}",
            )

        case RetryCommand(job_id, _):
            return DispatchResult(
                route="reject",
                identifier=job_id,
                note="attempts must be positive",
            )

        case (("cancel" | "delete") as operation, str(job_id)):
            return DispatchResult(
                route="remove",
                identifier=job_id,
                note=f"operation={operation}",
            )

        case Signal.STOP:
            return DispatchResult(
                route="stop",
                identifier=None,
                note="qualified value pattern",
            )

        case _:
            return DispatchResult(
                route="unsupported",
                identifier=None,
                note=f"subject-type={type(event).__name__}",
            )


def successful_binding_outlives_case(subject: object) -> str | None:
    """Show that a successful capture is not scoped to the case suite."""
    match subject:
        case ("job", str(job_id)):
            pass
        case _:
            return None

    return job_id


def main() -> None:
    """Print representative dispatch decisions for direct execution."""
    events: tuple[object, ...] = (
        {"kind": "job.created", "job_id": "job-7", "tenant": "acme"},
        RetryCommand("job-8", 2),
        RetryCommand("job-9", 0),
        ("cancel", "job-10"),
        Signal.STOP,
        "cancel",
    )
    for event in events:
        print(dispatch_event(event))


if __name__ == "__main__":
    main()
