"""Deterministic checks for the initialized PY-FND-050 artifacts."""

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
        / "EXP-01-truth-and-comparison-protocol"
    ),
)

import comparisons  # noqa: E402
import protocol_trace  # noqa: E402
import truthiness  # noqa: E402


class TruthProtocolTests(unittest.TestCase):
    def test_bool_takes_priority_over_len(self) -> None:
        report = truthiness.truth_protocol_report()

        self.assertFalse(report.bool_first_value)
        self.assertEqual(report.bool_first_events, ("__bool__",))
        self.assertNotIn("__len__", report.bool_first_events)

    def test_len_is_fallback_and_plain_objects_are_true(self) -> None:
        report = truthiness.truth_protocol_report()

        self.assertTrue(report.len_only_value)
        self.assertEqual(report.len_only_events, ("__len__",))
        self.assertTrue(report.plain_value)

    def test_invalid_truth_hooks_raise(self) -> None:
        self.assertEqual(
            truthiness.invalid_truth_hook_errors(),
            ("TypeError", "ValueError"),
        )

    def test_sentinel_preserves_every_present_falsy_value(self) -> None:
        self.assertEqual(
            truthiness.sentinel_report(),
            ("fallback", 0, None, ""),
        )

    def test_not_implemented_truth_is_version_aware(self) -> None:
        report = truthiness.not_implemented_truth_report()

        if sys.version_info >= (3, 14):
            self.assertEqual(report.outcome, "raises TypeError")
            self.assertIsNone(report.warning)
        else:
            self.assertEqual(report.outcome, "returns True")
            self.assertEqual(report.warning, "DeprecationWarning")


class ComparisonTests(unittest.TestCase):
    def test_chain_evaluates_middle_once_and_reuses_it(self) -> None:
        report = comparisons.successful_chain_trace()

        self.assertTrue(report.result)
        self.assertEqual(
            report.events,
            (
                "evaluate:low",
                "evaluate:middle",
                "compare:low<middle",
                "evaluate:high",
                "compare:middle<=high",
            ),
        )
        self.assertEqual(report.events.count("evaluate:middle"), 1)

    def test_false_first_comparison_skips_rightmost_expression(self) -> None:
        report = comparisons.short_circuited_chain_trace()

        self.assertFalse(report.result)
        self.assertEqual(
            report.events,
            (
                "evaluate:left",
                "evaluate:middle",
                "compare:left<middle",
            ),
        )
        self.assertNotIn("evaluate:right-skipped", report.events)

    def test_equality_identity_and_not_implemented_are_distinct(self) -> None:
        report = comparisons.equality_identity_report()

        self.assertTrue(report.distinct_equal)
        self.assertFalse(report.distinct_identical)
        self.assertTrue(report.alias_equal)
        self.assertTrue(report.alias_identical)
        self.assertFalse(report.unsupported_equal)
        self.assertTrue(report.direct_unsupported_is_not_implemented)

    def test_nan_is_identical_but_not_equal_to_itself(self) -> None:
        report = comparisons.nan_report()

        self.assertFalse(report.equal_to_self)
        self.assertTrue(report.unequal_to_self)
        self.assertTrue(report.identical_to_self)


class ExperimentTests(unittest.TestCase):
    def test_experiment_report_is_stable(self) -> None:
        output = protocol_trace.format_report(protocol_trace.run_experiment())

        expected_last_line = (
            "NotImplemented truth: "
            f"python={sys.version_info.major}.{sys.version_info.minor}; "
            + (
                "outcome=raises TypeError; warning=none"
                if sys.version_info >= (3, 14)
                else "outcome=returns True; warning=DeprecationWarning"
            )
        )
        self.assertEqual(
            output,
            "\n".join(
                (
                    "truth bool-first: value=False; events=__bool__",
                    "truth len-only: value=True; events=__len__",
                    "truth default: value=True; events=none",
                    "invalid truth hooks: errors=('TypeError', 'ValueError')",
                    "sentinel values: ('fallback', 0, None, '')",
                    "chain success: result=True; events=evaluate:low → "
                    "evaluate:middle → compare:low<middle → evaluate:high → "
                    "compare:middle<=high",
                    "chain short-circuit: result=False; events=evaluate:left → "
                    "evaluate:middle → compare:left<middle",
                    "equality and identity: distinct=(equal=True, "
                    "identical=False); alias=(equal=True, identical=True); "
                    "unsupported-equal=False; "
                    "direct-unsupported-is-NotImplemented=True",
                    "NaN: equal-to-self=False; unequal-to-self=True; "
                    "identical-to-self=True",
                    expected_last_line,
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
