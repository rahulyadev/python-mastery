"""Deterministic checks for the initialized PY-CON-070 artifacts."""

from __future__ import annotations

import asyncio
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
        / "EXP-01-timeout-cancellation-provenance"
    ),
)

import cancellation_cleanup  # noqa: E402
import taskgroup_failure  # noqa: E402
import timeout_budget  # noqa: E402
import timeout_cancellation  # noqa: E402


class ExampleTests(unittest.TestCase):
    def test_taskgroup_cancels_waiting_siblings_and_waits_for_cleanup(self) -> None:
        report = taskgroup_failure.run_demo()

        self.assertEqual(report.failures, ("synthetic record rejected",))
        self.assertEqual(set(report.cancelled_tasks), {"cache", "profile"})
        self.assertNotIn("cache:finish", report.events)
        self.assertNotIn("profile:finish", report.events)

        for name in ("cache", "profile"):
            self.assertLess(
                report.events.index(f"{name}:start"),
                report.events.index("validator:raise"),
            )
            self.assertLess(
                report.events.index("validator:raise"),
                report.events.index(f"{name}:cancelled"),
            )
            self.assertLess(
                report.events.index(f"{name}:cancelled"),
                report.events.index(f"{name}:cleanup"),
            )
            self.assertLess(
                report.events.index(f"{name}:cleanup"),
                report.events.index("owner:caught-rejection"),
            )

        self.assertEqual(report.events[-1], "owner:after-group")

    def test_timeout_transforms_its_own_cancellation_after_cleanup(self) -> None:
        report = timeout_budget.run_demo()

        self.assertTrue(report.timed_out)
        self.assertEqual(report.cancellation_count_before, 0)
        self.assertEqual(report.cancellation_count_after, 0)
        self.assertEqual(
            report.events,
            (
                "scope:entered",
                "scope:cancelled",
                "scope:cleanup",
                "owner:timeout",
            ),
        )

    def test_fetch_batch_returns_results_in_input_order(self) -> None:
        async def fetch(record_id: str) -> str:
            await asyncio.sleep(0)
            return record_id.upper()

        result = asyncio.run(
            timeout_budget.fetch_batch(
                fetch,
                ("alpha", "beta"),
                timeout_seconds=1.0,
            )
        )

        self.assertEqual(result, {"alpha": "ALPHA", "beta": "BETA"})

    def test_fetch_batch_translates_only_the_owned_timeout(self) -> None:
        async def never_finishes(record_id: str) -> str:
            del record_id
            await asyncio.Event().wait()
            raise AssertionError("unreachable")

        with self.assertRaises(timeout_budget.BatchDeadlineExceeded) as caught:
            asyncio.run(
                timeout_budget.fetch_batch(
                    never_finishes,
                    ("synthetic-1",),
                    timeout_seconds=0,
                )
            )

        self.assertEqual(caught.exception.record_ids, ("synthetic-1",))
        self.assertIsInstance(caught.exception.__cause__, TimeoutError)

    def test_explicit_cancellation_propagates_after_cleanup(self) -> None:
        report = cancellation_cleanup.run_demo()

        self.assertTrue(report.cancel_request_accepted)
        self.assertEqual(report.cancellation_message, "synthetic shutdown")
        self.assertTrue(report.cleanup_completed)
        self.assertTrue(report.task_cancelled)
        self.assertEqual(report.cancellation_count, 1)
        self.assertEqual(
            report.events,
            (
                "worker:start",
                "owner:cancel-requested",
                "worker:cancelled",
                "worker:cleanup-start",
                "worker:cleanup-done",
                "owner:cancel-observed",
            ),
        )

    def test_timeout_and_external_cancellation_keep_distinct_outcomes(self) -> None:
        report = timeout_cancellation.run_experiment()

        self.assertEqual(
            report.timeout_trace,
            (
                "timeout:entered",
                "timeout:inside-cancelled",
                "timeout:cleanup",
                "timeout:outside-timeout-error",
            ),
        )
        self.assertEqual(report.timeout_count_before, 0)
        self.assertEqual(report.timeout_count_after, 0)
        self.assertEqual(
            report.external_trace,
            (
                "external:entered",
                "external:cancel-requested",
                "external:inside-cancelled",
                "external:cleanup",
                "external:owner-observed-cancelled",
            ),
        )
        self.assertTrue(report.externally_cancelled_task)


if __name__ == "__main__":
    unittest.main()
