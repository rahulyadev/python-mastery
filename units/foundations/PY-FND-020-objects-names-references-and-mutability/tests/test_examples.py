"""Deterministic checks for the initialized PY-FND-020 examples."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))

import copy_graphs  # noqa: E402
import reference_model  # noqa: E402


class BindingTests(unittest.TestCase):
    def test_mutation_reaches_caller_but_rebinding_does_not(self) -> None:
        caller = ["queued"]

        report = reference_model.mutate_then_rebind(caller)

        self.assertTrue(report.same_object_before)
        self.assertEqual(caller, ["queued", "running"])
        self.assertEqual(report.caller_after_mutation, ("queued", "running"))
        self.assertEqual(
            report.local_after_rebinding,
            ("queued", "running", "done"),
        )
        self.assertFalse(report.same_object_after)

    def test_augmented_assignment_depends_on_operand_behavior(self) -> None:
        report = reference_model.compare_augmented_assignment()

        self.assertTrue(report.list_kept_identity)
        self.assertEqual(report.list_alias_observed, ("queued", "running"))
        self.assertFalse(report.tuple_kept_identity)
        self.assertEqual(report.tuple_alias_observed, ("queued",))
        self.assertEqual(report.rebound_tuple, ("queued", "running"))


class CopyTests(unittest.TestCase):
    def test_shallow_copy_reuses_descendants(self) -> None:
        report = copy_graphs.compare_copy_depths()

        self.assertTrue(report.shallow_root_is_new)
        self.assertTrue(report.shallow_roles_are_shared)
        self.assertEqual(report.original_roles, ("reader", "writer"))
        self.assertEqual(report.shallow_roles, ("reader", "writer"))

    def test_deep_copy_recursively_copies_mutable_descendants(self) -> None:
        report = copy_graphs.compare_copy_depths()

        self.assertTrue(report.deep_roles_are_new)
        self.assertEqual(report.deep_roles, ("reader", "auditor"))
        self.assertNotIn("auditor", report.original_roles)

    def test_deepcopy_preserves_recursive_graph_shape(self) -> None:
        clone_is_new, clone_kept_cycle = copy_graphs.deepcopy_preserves_cycle_shape()

        self.assertTrue(clone_is_new)
        self.assertTrue(clone_kept_cycle)

    def test_schema_copy_establishes_two_level_ownership(self) -> None:
        incoming: copy_graphs.Request = {
            "roles": ["reader"],
            "regions": ["ap-south"],
        }

        owned = copy_graphs.own_request(incoming)
        incoming["roles"].append("writer")
        owned["regions"].append("eu-west")

        self.assertEqual(owned["roles"], ["reader"])
        self.assertEqual(incoming["regions"], ["ap-south"])


if __name__ == "__main__":
    unittest.main()
