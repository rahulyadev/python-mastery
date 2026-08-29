"""Deterministic checks for the initialized PY-FND-040 artifacts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))
sys.path.insert(
    0,
    str(UNIT_ROOT / "experiments" / "EXP-01-expression-trace"),
)

import assignment_expressions  # noqa: E402
import evaluation_order  # noqa: E402
import expression_trace  # noqa: E402


class EvaluationOrderTests(unittest.TestCase):
    def test_precedence_groups_before_temporal_evaluation(self) -> None:
        report = evaluation_order.precedence_trace()

        self.assertEqual(report.value, 22)
        self.assertEqual(report.events, ("left", "factor", "count"))

    def test_power_groups_right_but_evaluates_operands_left_to_right(self) -> None:
        report = evaluation_order.power_trace()

        self.assertEqual(report.value, 512)
        self.assertEqual(
            report.events,
            ("base", "inner-exponent", "outer-exponent"),
        )

    def test_short_circuiting_skips_unneeded_operands_and_branch(self) -> None:
        report = evaluation_order.short_circuit_trace()

        self.assertEqual(report.values, (0, "cached", "loaded", "ready"))
        self.assertEqual(
            report.events,
            (
                "and-left",
                "or-left",
                "fallback-left",
                "fallback-right",
                "condition",
                "if-branch",
            ),
        )
        self.assertNotIn("and-right-skipped", report.events)
        self.assertNotIn("or-right-skipped", report.events)
        self.assertNotIn("else-branch-skipped", report.events)

    def test_call_arguments_finish_before_invocation(self) -> None:
        report = evaluation_order.call_trace()

        self.assertEqual(report.value, 7)
        self.assertEqual(
            report.events,
            ("callee", "positional", "keyword", "invoke"),
        )


class AssignmentTests(unittest.TestCase):
    def test_normal_and_augmented_assignment_have_distinct_target_timing(self) -> None:
        report = assignment_expressions.assignment_trace()

        self.assertEqual(report.normal_value, 5)
        self.assertEqual(
            report.normal_events,
            ("rhs", "target-container", "target-key"),
        )
        self.assertEqual(report.augmented_value, 15)
        self.assertEqual(
            report.augmented_events,
            ("target-container", "target-key", "rhs"),
        )

    def test_power_and_unary_parentheses_change_grouping(self) -> None:
        self.assertEqual(
            assignment_expressions.power_and_unary_results(),
            (-4, 4, 512, 64, 0.25),
        )

    def test_assignment_expression_reads_each_chunk_once(self) -> None:
        values = iter((b"alpha", b"beta", b""))
        calls: list[str] = []

        def read() -> bytes:
            calls.append("read")
            return next(values)

        chunks = assignment_expressions.consume_chunks(read)

        self.assertEqual(chunks, (b"alpha", b"beta"))
        self.assertEqual(calls, ["read", "read", "read"])


class ExperimentTests(unittest.TestCase):
    def test_experiment_report_is_stable(self) -> None:
        output = expression_trace.format_report(expression_trace.run_experiment())

        self.assertEqual(
            output,
            "\n".join(
                (
                    "precedence: value=22; events=left -> factor -> count",
                    "power: value=512; "
                    "events=base -> inner-exponent -> outer-exponent",
                    "short-circuit: values=(0, 'cached', 'loaded', 'ready'); "
                    "events=and-left -> or-left -> fallback-left -> "
                    "fallback-right -> condition -> if-branch",
                    "call: value=7; events=callee -> positional -> keyword -> invoke",
                    "normal assignment: value=5; "
                    "events=rhs -> target-container -> target-key",
                    "augmented assignment: value=15; "
                    "events=target-container -> target-key -> rhs",
                    "power and unary: (-4, 4, 512, 64, 0.25)",
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
