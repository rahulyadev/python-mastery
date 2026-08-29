"""Run the controlled PY-FND-040 expression-order experiment."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(UNIT_ROOT / "examples"))

from assignment_expressions import (  # noqa: E402
    AssignmentTrace,
    assignment_trace,
    power_and_unary_results,
)
from evaluation_order import (  # noqa: E402
    ShortCircuitTrace,
    ValueTrace,
    call_trace,
    power_trace,
    precedence_trace,
    short_circuit_trace,
)


@dataclass(frozen=True)
class ExperimentReport:
    """All deterministic observations gathered by the experiment."""

    precedence: ValueTrace
    power: ValueTrace
    short_circuit: ShortCircuitTrace
    call: ValueTrace
    assignment: AssignmentTrace
    power_and_unary: tuple[int, int, int, int, float]


def run_experiment() -> ExperimentReport:
    """Collect every trace without filesystem, network, or clock input."""
    return ExperimentReport(
        precedence=precedence_trace(),
        power=power_trace(),
        short_circuit=short_circuit_trace(),
        call=call_trace(),
        assignment=assignment_trace(),
        power_and_unary=power_and_unary_results(),
    )


def format_report(report: ExperimentReport) -> str:
    """Render a stable, human-readable experiment report."""
    return "\n".join(
        (
            "precedence: "
            f"value={report.precedence.value!r}; "
            f"events={' -> '.join(report.precedence.events)}",
            "power: "
            f"value={report.power.value!r}; "
            f"events={' -> '.join(report.power.events)}",
            "short-circuit: "
            f"values={report.short_circuit.values!r}; "
            f"events={' -> '.join(report.short_circuit.events)}",
            "call: "
            f"value={report.call.value!r}; "
            f"events={' -> '.join(report.call.events)}",
            "normal assignment: "
            f"value={report.assignment.normal_value}; "
            f"events={' -> '.join(report.assignment.normal_events)}",
            "augmented assignment: "
            f"value={report.assignment.augmented_value}; "
            f"events={' -> '.join(report.assignment.augmented_events)}",
            f"power and unary: {report.power_and_unary!r}",
        )
    )


def main() -> None:
    """Execute and print the experiment."""
    print(format_report(run_experiment()))


if __name__ == "__main__":
    main()
