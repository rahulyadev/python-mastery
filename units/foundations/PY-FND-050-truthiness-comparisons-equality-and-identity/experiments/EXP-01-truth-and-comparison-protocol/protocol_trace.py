"""Run the controlled PY-FND-050 truth and comparison experiment."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(UNIT_ROOT / "examples"))

from comparisons import (  # noqa: E402
    ChainTrace,
    EqualityIdentityReport,
    NanReport,
    equality_identity_report,
    nan_report,
    short_circuited_chain_trace,
    successful_chain_trace,
)
from truthiness import (  # noqa: E402
    NotImplementedTruthReport,
    TruthProtocolReport,
    invalid_truth_hook_errors,
    not_implemented_truth_report,
    sentinel_report,
    truth_protocol_report,
)


@dataclass(frozen=True)
class ExperimentReport:
    """All deterministic observations gathered by the experiment."""

    truth_protocol: TruthProtocolReport
    invalid_truth_errors: tuple[str, str]
    sentinel_values: tuple[object, object, object, object]
    successful_chain: ChainTrace
    short_circuited_chain: ChainTrace
    equality_identity: EqualityIdentityReport
    nan: NanReport
    not_implemented_truth: NotImplementedTruthReport


def run_experiment() -> ExperimentReport:
    """Collect protocol traces without filesystem, network, or clock input."""
    return ExperimentReport(
        truth_protocol=truth_protocol_report(),
        invalid_truth_errors=invalid_truth_hook_errors(),
        sentinel_values=sentinel_report(),
        successful_chain=successful_chain_trace(),
        short_circuited_chain=short_circuited_chain_trace(),
        equality_identity=equality_identity_report(),
        nan=nan_report(),
        not_implemented_truth=not_implemented_truth_report(),
    )


def format_report(report: ExperimentReport) -> str:
    """Render a stable, human-readable experiment report."""
    truth = report.truth_protocol
    equality = report.equality_identity
    nan = report.nan
    not_implemented = report.not_implemented_truth

    return "\n".join(
        (
            "truth bool-first: "
            f"value={truth.bool_first_value}; "
            f"events={' -> '.join(truth.bool_first_events)}",
            "truth len-only: "
            f"value={truth.len_only_value}; "
            f"events={' -> '.join(truth.len_only_events)}",
            f"truth default: value={truth.plain_value}; events=none",
            f"invalid truth hooks: errors={report.invalid_truth_errors!r}",
            f"sentinel values: {report.sentinel_values!r}",
            "chain success: "
            f"result={report.successful_chain.result}; "
            f"events={' → '.join(report.successful_chain.events)}",
            "chain short-circuit: "
            f"result={report.short_circuited_chain.result}; "
            f"events={' → '.join(report.short_circuited_chain.events)}",
            "equality and identity: "
            f"distinct=(equal={equality.distinct_equal}, "
            f"identical={equality.distinct_identical}); "
            f"alias=(equal={equality.alias_equal}, "
            f"identical={equality.alias_identical}); "
            f"unsupported-equal={equality.unsupported_equal}; "
            "direct-unsupported-is-NotImplemented="
            f"{equality.direct_unsupported_is_not_implemented}",
            "NaN: "
            f"equal-to-self={nan.equal_to_self}; "
            f"unequal-to-self={nan.unequal_to_self}; "
            f"identical-to-self={nan.identical_to_self}",
            "NotImplemented truth: "
            f"python={sys.version_info.major}.{sys.version_info.minor}; "
            f"outcome={not_implemented.outcome}; "
            f"warning={not_implemented.warning or 'none'}",
        )
    )


def main() -> None:
    """Execute and print the experiment."""
    print(format_report(run_experiment()))


if __name__ == "__main__":
    main()
