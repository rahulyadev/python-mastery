"""Deterministic checks for the initialized PY-CON-040 runnable artifacts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))
sys.path.insert(0, str(UNIT_ROOT / "experiments" / "EXP-01-start-method-state"))

import ipc_protocol  # noqa: E402
import pool_batch  # noqa: E402
import process_isolation  # noqa: E402
import queue_pipeline  # noqa: E402
import shared_memory_partitions  # noqa: E402
import start_method_state  # noqa: E402


class ExampleTests(unittest.TestCase):
    def test_ordinary_list_is_isolated_from_child_mutation(self) -> None:
        parent_values, child_report, parent_pid = process_isolation.run_demo()

        self.assertEqual(parent_values, (1, 2, 3))
        self.assertEqual(child_report.values, (1, 2, 3, 99))
        self.assertNotEqual(child_report.pid, parent_pid)

    def test_pipeline_reports_success_failure_and_clean_exit(self) -> None:
        outcomes, exitcodes = queue_pipeline.run_demo()

        self.assertEqual([outcome.job_id for outcome in outcomes], ["job-a", "job-b", "job-c"])
        self.assertEqual(outcomes[0].value, 9)
        self.assertIn("synthetic negative input", outcomes[1].error or "")
        self.assertEqual(outcomes[2].value, 25)
        self.assertEqual(exitcodes, (0, 0))

    def test_byte_protocol_validates_accepted_and_rejected_messages(self) -> None:
        accepted, rejected = ipc_protocol.run_demo()

        self.assertEqual(accepted, {"ok": True, "result": 29})
        self.assertFalse(rejected["ok"])
        self.assertIn("values must be", rejected["error"])

    def test_disjoint_shared_memory_partitions_are_visible_to_parent(self) -> None:
        values, partitions, exitcodes = shared_memory_partitions.run_demo()

        self.assertEqual(values, [10, 20, 30, 40, 50, 60])
        self.assertEqual(partitions, [(0, 3), (3, 6)])
        self.assertEqual(exitcodes, (0, 0))

    def test_pool_returns_input_order_and_gracefully_finishes(self) -> None:
        summaries = pool_batch.run_demo()

        self.assertEqual([summary.batch_id for summary in summaries], [
            "batch-a",
            "batch-b",
            "batch-c",
        ])
        self.assertEqual([summary.sum_of_squares for summary in summaries], [14, 41, 36])

    def test_spawn_imports_fresh_module_state(self) -> None:
        original = start_method_state.MODULE_TOKEN
        try:
            start_method_state.MODULE_TOKEN = "parent-mutated"
            observation = start_method_state.observe_method("spawn")
        finally:
            start_method_state.MODULE_TOKEN = original

        self.assertEqual(observation.child_token, "import-default")
        self.assertEqual(observation.exitcode, 0)


if __name__ == "__main__":
    unittest.main()
