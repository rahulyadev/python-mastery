"""Deterministic checks for the initialized PY-CON-090 artifacts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))
sys.path.insert(
    0,
    str(
        UNIT_ROOT
        / "experiments"
        / "EXP-01-runtime-mode-and-isolation-probe"
    ),
)

import interpreter_isolation  # noqa: E402
import interpreter_pool  # noqa: E402
import runtime_mode_probe  # noqa: E402
import runtime_modes  # noqa: E402
import shared_state_race  # noqa: E402


class RuntimeModeTests(unittest.TestCase):
    def test_capabilities_keep_build_and_runtime_state_separate(self) -> None:
        report = runtime_modes.detect_runtime_capabilities()

        self.assertTrue(report.implementation)
        self.assertTrue(report.python_version)
        self.assertIsInstance(report.free_threaded_build, bool)
        self.assertIn(report.gil_enabled, (True, False, None))
        self.assertIsInstance(report.interpreters_module_available, bool)
        self.assertIsInstance(report.interpreter_pool_available, bool)
        self.assertTrue(report.mode)

    def test_regular_cpython_is_not_reported_as_free_threaded(self) -> None:
        report = runtime_modes.RuntimeCapabilities(
            implementation="cpython",
            python_version="3.14.0",
            abi_flags="",
            free_threaded_build=False,
            gil_enabled=True,
            isolated_interpreters_supported=True,
            interpreters_module_available=True,
            interpreter_pool_available=True,
        )

        self.assertEqual(
            report.mode,
            "regular CPython build with the GIL enabled",
        )

    def test_missing_live_probe_remains_explicit(self) -> None:
        report = runtime_modes.RuntimeCapabilities(
            implementation="cpython",
            python_version="3.11.0",
            abi_flags="",
            free_threaded_build=False,
            gil_enabled=None,
            isolated_interpreters_supported=False,
            interpreters_module_available=False,
            interpreter_pool_available=False,
        )

        self.assertEqual(
            report.mode,
            "regular CPython build; live GIL probe unavailable",
        )


class SharedStateTests(unittest.TestCase):
    def test_controlled_interleaving_loses_one_logical_update(self) -> None:
        report = shared_state_race.run_demo()

        self.assertEqual(report.expected, 2)
        self.assertEqual(report.unsafe_result, 1)
        self.assertEqual(report.locked_result, 2)


@unittest.skipUnless(
    runtime_modes.detect_runtime_capabilities().interpreters_module_available,
    "requires Python 3.14 concurrent.interpreters",
)
class InterpreterIsolationTests(unittest.TestCase):
    def test_interpreters_have_distinct_state_in_one_process(self) -> None:
        report = interpreter_isolation.run_demo()

        self.assertTrue(report.interpreter_ids_are_distinct)
        self.assertTrue(report.all_share_main_process)
        self.assertEqual(
            tuple(item.state for item in report.observations),
            (("alpha", "first-only"), ("beta", "second-only")),
        )


@unittest.skipUnless(
    runtime_modes.detect_runtime_capabilities().interpreter_pool_available,
    "requires Python 3.14 InterpreterPoolExecutor",
)
class InterpreterPoolTests(unittest.TestCase):
    def test_pool_returns_copied_results_in_submission_order(self) -> None:
        report = interpreter_pool.run_demo()

        self.assertEqual(report.partial_sums, (6, 9))
        self.assertEqual(report.total, 15)

    def test_empty_input_does_not_create_an_executor(self) -> None:
        report = interpreter_pool.sum_batches(())

        self.assertEqual(report.partial_sums, ())
        self.assertEqual(report.total, 0)


@unittest.skipUnless(
    runtime_modes.detect_runtime_capabilities().interpreters_module_available
    and runtime_modes.detect_runtime_capabilities().interpreter_pool_available,
    "requires Python 3.14 interpreter APIs",
)
class ExperimentTests(unittest.TestCase):
    def test_experiment_preserves_all_four_observation_boundaries(self) -> None:
        report = runtime_mode_probe.run_experiment()

        self.assertEqual(report.race.unsafe_result, 1)
        self.assertEqual(report.race.locked_result, 2)
        self.assertTrue(report.isolation.interpreter_ids_are_distinct)
        self.assertTrue(report.isolation.all_share_main_process)
        self.assertEqual(report.pool.total, 15)


if __name__ == "__main__":
    unittest.main()
