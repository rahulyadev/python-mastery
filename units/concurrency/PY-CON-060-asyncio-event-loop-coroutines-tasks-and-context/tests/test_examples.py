"""Deterministic checks for the initialized PY-CON-060 artifacts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))
sys.path.insert(0, str(UNIT_ROOT / "experiments" / "EXP-01-eager-task-start"))

import coroutine_lifecycle  # noqa: E402
import eager_task_start  # noqa: E402
import future_bridge  # noqa: E402
import task_context  # noqa: E402


class ExampleTests(unittest.TestCase):
    def test_coroutine_and_task_lifecycle(self) -> None:
        report = coroutine_lifecycle.run_demo()

        self.assertEqual(report.created_state, "CORO_CREATED")
        self.assertFalse(report.done_immediately_after_create_task)
        self.assertFalse(report.done_after_one_loop_turn)
        self.assertEqual(report.closed_state, "CORO_CLOSED")
        self.assertEqual(report.result, 42)
        self.assertEqual(
            report.events,
            (
                "owner:coroutine-created",
                "owner:task-created",
                "worker:start",
                "owner:after-one-turn",
                "worker:resume",
                "owner:collected",
            ),
        )

    def test_future_bridges_callback_completion(self) -> None:
        report = future_bridge.run_demo()

        self.assertEqual(report.first_result, "ready")
        self.assertEqual(report.repeated_result, "ready")
        self.assertTrue(report.future_done)
        self.assertEqual(
            report.events,
            (
                "adapter:scheduled",
                "owner:before-first-await",
                "adapter:completed",
                "owner:after-first-await",
                "owner:after-second-await",
                "callback:queued-before-second-await",
                "owner:after-explicit-yield",
            ),
        )

    def test_tasks_capture_context_at_creation(self) -> None:
        report = task_context.run_demo()

        self.assertEqual(
            report.observations,
            (
                task_context.ContextObservation(
                    "child-a", "request-a", "request-a/child-a"
                ),
                task_context.ContextObservation(
                    "child-b", "request-b", "request-b/child-b"
                ),
            ),
        )
        self.assertEqual(report.parent_after_children, "request-b")
        self.assertEqual(task_context.request_id.get(), "unset")

    @unittest.skipIf(sys.version_info < (3, 14), "eager_start requires Python 3.14")
    def test_python_314_eager_start_changes_entry_timing(self) -> None:
        self.assertEqual(
            eager_task_start.run_experiment(),
            (
                "after-lazy done=False",
                "eager:start",
                "after-eager done=False",
                "lazy:start",
                "eager:resume",
                "main:after-turn",
                "lazy:resume",
                "main:collected",
            ),
        )


if __name__ == "__main__":
    unittest.main()
