"""Deterministic checks for the initialized PY-CON-050 runnable artifacts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))

import bounded_map  # noqa: E402
import completion_order  # noqa: E402
import future_lifecycle  # noqa: E402
import process_batch  # noqa: E402


class ExampleTests(unittest.TestCase):
    def test_future_lifecycle_separates_running_cancelled_and_failed(self) -> None:
        report = future_lifecycle.run_demo()

        self.assertFalse(report.running_cancel_succeeded)
        self.assertTrue(report.queued_cancel_succeeded)
        self.assertEqual(report.running_result, 21)
        self.assertEqual(report.queued_result_category, "CancelledError")
        self.assertEqual(report.failure_type, "ValueError")
        self.assertEqual(report.failure_message, "synthetic worker failure")

    def test_as_completed_and_map_have_distinct_ordering_contracts(self) -> None:
        report = completion_order.run_demo()

        self.assertEqual(report.completion_order, ("job-b", "job-a"))
        self.assertEqual(report.map_results, (9, 1, 4))

    @unittest.skipIf(sys.version_info < (3, 14), "buffersize requires Python 3.14")
    def test_python_314_map_buffers_source_consumption(self) -> None:
        consumed, results = bounded_map.run_demo()

        self.assertEqual(consumed, (0, 1))
        self.assertEqual(results, (0, 2, 4, 6))

    def test_process_pool_returns_picklable_results_in_input_order(self) -> None:
        summaries = process_batch.run_demo()

        self.assertEqual(
            [summary.batch_id for summary in summaries],
            ["batch-a", "batch-b", "batch-c"],
        )
        self.assertEqual([summary.count for summary in summaries], [3, 2, 1])
        self.assertEqual([summary.sum_of_squares for summary in summaries], [14, 41, 36])


if __name__ == "__main__":
    unittest.main()
