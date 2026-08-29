"""Expose hidden control-transfer and match-dispatch decisions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


UNIT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(UNIT_ROOT / "examples"))

from pattern_matching import successful_binding_outlives_case  # noqa: E402


@dataclass(frozen=True)
class LoopTrace:
    """One loop result and its ordered observable events."""

    result: str
    events: tuple[str, ...]


@dataclass(frozen=True)
class MatchTrace:
    """One match result and its ordered observable events."""

    result: str
    events: tuple[str, ...]


@dataclass(frozen=True)
class ExperimentReport:
    """All deterministic observations in this experiment."""

    loop_break: LoopTrace
    loop_exhaustion: LoopTrace
    guarded_match: MatchTrace
    unmatched_subject: MatchTrace
    binding_after_case: str | None


def trace_search(values: tuple[int, ...], target: int) -> LoopTrace:
    """Trace the distinct edges produced by continue, break, and exhaustion."""
    events: list[str] = []
    result = "not-found"

    for value in values:
        events.append(f"visit:{value}")

        if value < 0:
            events.append(f"continue:{value}")
            continue

        if value == target:
            result = f"found:{value}"
            events.append(f"break:{value}")
            break

        events.append(f"body-tail:{value}")
    else:
        events.append("loop-else")

    events.append("after-loop")
    return LoopTrace(result=result, events=tuple(events))


def make_subject(events: list[str], value: object) -> object:
    """Record exactly when the match subject expression runs."""
    events.append("subject")
    return value


def trace_guard(events: list[str], label: str, result: bool) -> bool:
    """Record an ordered guard evaluation and return its fixed result."""
    events.append(f"guard:{label}={result}")
    return result


def trace_priority_match(subject: object) -> MatchTrace:
    """Trace pattern success, failed guards, case order, and fallback."""
    events: list[str] = []

    match make_subject(events, subject):
        case ("job", str(job_id), int(score)) if trace_guard(
            events,
            "urgent",
            score >= 10,
        ):
            result = f"urgent:{job_id}"
            events.append("case:urgent")

        case ("job", str(job_id), int(score)) if trace_guard(
            events,
            "valid",
            score >= 0,
        ):
            result = f"normal:{job_id}"
            events.append("case:normal")

        case _:
            result = "unsupported"
            events.append("case:fallback")

    return MatchTrace(result=result, events=tuple(events))


def run_experiment() -> ExperimentReport:
    """Return a deterministic report for tests and direct reproduction."""
    return ExperimentReport(
        loop_break=trace_search((-1, 2, 3), target=2),
        loop_exhaustion=trace_search((-1, 2, 3), target=9),
        guarded_match=trace_priority_match(("job", "job-7", 5)),
        unmatched_subject=trace_priority_match(("other", "job-7", 5)),
        binding_after_case=successful_binding_outlives_case(("job", "job-8")),
    )


def format_events(events: tuple[str, ...]) -> str:
    """Render an event tuple without implementation-specific addresses."""
    return " → ".join(events)


def format_report(report: ExperimentReport) -> str:
    """Format the report as stable, line-oriented evidence."""
    return "\n".join(
        (
            "loop break: "
            f"result={report.loop_break.result}; "
            f"events={format_events(report.loop_break.events)}",
            "loop exhaustion: "
            f"result={report.loop_exhaustion.result}; "
            f"events={format_events(report.loop_exhaustion.events)}",
            "guarded match: "
            f"result={report.guarded_match.result}; "
            f"events={format_events(report.guarded_match.events)}",
            "unmatched subject: "
            f"result={report.unmatched_subject.result}; "
            f"events={format_events(report.unmatched_subject.events)}",
            f"binding after case: {report.binding_after_case}",
        )
    )


def main() -> None:
    """Print the complete deterministic observation."""
    print(format_report(run_experiment()))


if __name__ == "__main__":
    main()
