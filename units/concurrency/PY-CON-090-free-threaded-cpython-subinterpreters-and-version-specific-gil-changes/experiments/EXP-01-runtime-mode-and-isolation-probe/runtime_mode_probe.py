"""Probe runtime mode, logical race safety, and interpreter isolation."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(UNIT_ROOT / "examples"))

import interpreter_isolation  # noqa: E402
import interpreter_pool  # noqa: E402
import runtime_modes  # noqa: E402
import shared_state_race  # noqa: E402


@dataclass(frozen=True)
class ProbeReport:
    """All observations collected by the experiment."""

    capabilities: runtime_modes.RuntimeCapabilities
    race: shared_state_race.RaceReport
    isolation: interpreter_isolation.IsolationReport
    pool: interpreter_pool.PoolReport


def run_experiment() -> ProbeReport:
    """Collect standard-library observations without benchmarking."""
    return ProbeReport(
        capabilities=runtime_modes.detect_runtime_capabilities(),
        race=shared_state_race.run_demo(),
        isolation=interpreter_isolation.run_demo(),
        pool=interpreter_pool.run_demo(),
    )


def main() -> None:
    """Print stable observations and retain version/build facts."""
    report = run_experiment()
    for line in runtime_modes.format_capabilities(report.capabilities):
        print(line)
    print(
        "unsafe controlled result: "
        f"{report.race.unsafe_result}/{report.race.expected}"
    )
    print(
        f"locked result: {report.race.locked_result}/{report.race.expected}"
    )
    print(
        "subinterpreter IDs distinct: "
        f"{report.isolation.interpreter_ids_are_distinct}"
    )
    print(
        "subinterpreters share main PID: "
        f"{report.isolation.all_share_main_process}"
    )
    print(
        "isolated states: "
        f"{tuple(item.state for item in report.isolation.observations)}"
    )
    print(f"interpreter pool partials: {report.pool.partial_sums}")
    print(f"interpreter pool total: {report.pool.total}")


if __name__ == "__main__":
    main()
