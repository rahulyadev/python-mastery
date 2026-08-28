"""Deterministic checks for the initialized PY-CON-030 runnable artifacts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))
sys.path.insert(
    0,
    str(UNIT_ROOT / "experiments" / "EXP-01-controlled-race-window"),
)

import bounded_queue_pipeline  # noqa: E402
import condition_buffer  # noqa: E402
import controlled_race  # noqa: E402
import deadlock_avoidance  # noqa: E402
import locked_invariant  # noqa: E402
import primitive_roles  # noqa: E402


class ExampleTests(unittest.TestCase):
    def test_locked_inventory_preserves_non_negative_stock(self) -> None:
        inventory, records = locked_invariant.run_demo()

        self.assertEqual(inventory.available, 0)
        self.assertEqual(sum(record.accepted for record in records), 1)

    def test_condition_buffer_drains_before_end_of_stream(self) -> None:
        processed, closed, workers_alive = condition_buffer.run_demo()

        self.assertEqual(processed, [2, 4, 6])
        self.assertTrue(closed)
        self.assertFalse(workers_alive)

    def test_bounded_queue_reports_every_accepted_job(self) -> None:
        protocol, outcomes, workers_alive = bounded_queue_pipeline.run_demo()

        self.assertIn(protocol, {"Queue.shutdown", "sentinels"})
        self.assertEqual([outcome.job_id for outcome in outcomes], [
            "invoice-1",
            "invoice-2",
            "invoice-3",
        ])
        self.assertEqual(outcomes[0].value, "ready")
        self.assertIn("synthetic invalid payload", outcomes[1].error or "")
        self.assertEqual(outcomes[2].value, "paid")
        self.assertFalse(workers_alive)

    def test_primitives_represent_distinct_state(self) -> None:
        total, maximum_active, event_is_set, tokens = primitive_roles.run_demo()

        self.assertEqual(total, 7)
        self.assertEqual(maximum_active, 2)
        self.assertTrue(event_is_set)
        self.assertEqual(tokens, [0, 1, 2])

    def test_global_lock_order_terminates_opposing_transfers(self) -> None:
        alpha, beta, outcomes, workers_alive = deadlock_avoidance.run_demo()

        self.assertEqual(alpha.balance + beta.balance, 200)
        self.assertTrue(all(outcome.accepted for outcome in outcomes))
        self.assertFalse(workers_alive)

    def test_controlled_race_and_locked_repair(self) -> None:
        self.assertEqual(controlled_race.controlled_lost_update(), 1)
        self.assertEqual(controlled_race.locked_updates(), 2)


if __name__ == "__main__":
    unittest.main()
