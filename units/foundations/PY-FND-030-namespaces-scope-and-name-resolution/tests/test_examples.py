"""Deterministic checks for the initialized PY-FND-030 examples."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))

import name_resolution  # noqa: E402
import rebinding  # noqa: E402


class ResolutionTests(unittest.TestCase):
    def test_local_enclosing_global_and_builtin_lookup(self) -> None:
        report = name_resolution.resolve_request("req-7")

        self.assertEqual(report.local_value, "REQ-7")
        self.assertEqual(report.enclosing_value, "worker")
        self.assertEqual(report.global_value, "payments")
        self.assertEqual(report.builtin_value, 5)

    def test_local_binding_can_shadow_a_builtin(self) -> None:
        shadowed, actual = name_resolution.compare_builtin_shadowing(
            ["a", "b", "c"]
        )

        self.assertEqual(shadowed, -1)
        self.assertEqual(actual, 3)

    def test_later_assignment_classifies_the_name_as_local(self) -> None:
        self.assertEqual(
            name_resolution.unbound_local_error_name(),
            "UnboundLocalError",
        )


class RebindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_module_events = rebinding.MODULE_EVENTS
        rebinding.MODULE_EVENTS = 0

    def tearDown(self) -> None:
        rebinding.MODULE_EVENTS = self.original_module_events

    def test_global_rebinds_the_module_namespace(self) -> None:
        self.assertEqual(rebinding.record_module_event(), 1)
        self.assertEqual(rebinding.record_module_event(), 2)
        self.assertEqual(rebinding.MODULE_EVENTS, 2)

    def test_nonlocal_rebinds_the_nearest_enclosing_function_name(self) -> None:
        first = rebinding.make_counter(10)
        second = rebinding.make_counter(100)

        self.assertEqual((first(), first()), (11, 12))
        self.assertEqual(second(), 101)
        self.assertEqual(first(), 13)

    def test_method_bare_name_skips_the_class_namespace(self) -> None:
        policy = rebinding.Policy()

        self.assertEqual(policy.bare_label(), "module")
        self.assertEqual(policy.attribute_label(), "class")

    def test_comprehension_target_does_not_leak(self) -> None:
        outer_item, doubled = rebinding.comprehension_report([1, 2, 3])

        self.assertEqual(outer_item, "outer")
        self.assertEqual(doubled, (2, 4, 6))

    def test_nonlocal_requires_an_enclosing_function_binding(self) -> None:
        invalid_source = "def f():\n    nonlocal missing\n"

        with self.assertRaises(SyntaxError):
            compile(invalid_source, "<scope-test>", "exec")


if __name__ == "__main__":
    unittest.main()
