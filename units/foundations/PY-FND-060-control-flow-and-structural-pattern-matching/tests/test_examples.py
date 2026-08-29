"""Deterministic checks for the PY-FND-060 learning artifacts."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))
sys.path.insert(
    0,
    str(UNIT_ROOT / "experiments" / "EXP-01-control-flow-dispatch-trace"),
)

import control_flow  # noqa: E402
import control_flow_trace  # noqa: E402
import pattern_matching  # noqa: E402


class ConditionalFlowTests(unittest.TestCase):
    def test_if_elif_else_selects_one_workload_band(self) -> None:
        self.assertEqual(control_flow.workload_band(0), "idle")
        self.assertEqual(control_flow.workload_band(1), "normal")
        self.assertEqual(control_flow.workload_band(9), "normal")
        self.assertEqual(control_flow.workload_band(10), "busy")

    def test_invalid_workload_is_rejected_before_classification(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            control_flow.workload_band(-1)


class LoopFlowTests(unittest.TestCase):
    def test_continue_skips_invalid_candidates_and_break_selects_first_hit(self) -> None:
        jobs = (
            control_flow.Job("job-1", "blocked", 3),
            control_flow.Job("job-2", "ready", -1),
            control_flow.Job("job-3", "ready", 5),
            control_flow.Job("job-4", "ready", 9),
        )

        report = control_flow.select_first_ready_job(jobs)

        self.assertEqual(report.selected_job_id, "job-3")
        self.assertEqual(report.inspected_job_ids, ("job-1", "job-2", "job-3"))
        self.assertEqual(
            report.skipped_reasons,
            ("job-1:state=blocked", "job-2:negative-priority"),
        )
        self.assertFalse(report.exhausted_without_break)

    def test_for_else_represents_exhaustion_without_break(self) -> None:
        jobs = (
            control_flow.Job("job-1", "blocked", 3),
            control_flow.Job("job-2", "ready", -1),
        )

        report = control_flow.select_first_ready_job(jobs)

        self.assertIsNone(report.selected_job_id)
        self.assertTrue(report.exhausted_without_break)

    def test_empty_iterable_reaches_for_else_without_assigning_a_target(self) -> None:
        report = control_flow.select_first_ready_job(())

        self.assertIsNone(report.selected_job_id)
        self.assertEqual(report.inspected_job_ids, ())
        self.assertTrue(report.exhausted_without_break)

    def test_continue_can_still_end_in_while_else(self) -> None:
        self.assertEqual(
            control_flow.bounded_poll_trace(("ignore",), limit=3),
            (
                "visit:0:ignore",
                "continue",
                "loop-else:natural-stop",
                "after-loop",
            ),
        )

    def test_break_skips_while_else(self) -> None:
        self.assertEqual(
            control_flow.bounded_poll_trace(("waiting", "ready"), limit=3),
            (
                "visit:0:waiting",
                "body-tail",
                "visit:1:ready",
                "break",
                "after-loop",
            ),
        )


class StructuralPatternTests(unittest.TestCase):
    def test_mapping_pattern_accepts_extra_keys_and_captures_rest(self) -> None:
        result = pattern_matching.dispatch_event(
            {
                "kind": "job.created",
                "job_id": "job-7",
                "tenant": "acme",
                "trace_id": "trace-1",
            }
        )

        self.assertEqual(
            result,
            pattern_matching.DispatchResult("create", "job-7", "extra-fields=2"),
        )

    def test_class_pattern_guard_can_fall_through_to_later_case(self) -> None:
        accepted = pattern_matching.dispatch_event(
            pattern_matching.RetryCommand("job-8", 2)
        )
        rejected = pattern_matching.dispatch_event(
            pattern_matching.RetryCommand("job-8", 0)
        )

        self.assertEqual(accepted.route, "retry")
        self.assertEqual(rejected.route, "reject")

    def test_or_and_as_patterns_preserve_the_selected_operation(self) -> None:
        cancel = pattern_matching.dispatch_event(("cancel", "job-9"))
        delete = pattern_matching.dispatch_event(["delete", "job-10"])

        self.assertEqual(cancel.note, "operation=cancel")
        self.assertEqual(delete.note, "operation=delete")

    def test_string_is_not_treated_as_a_sequence_pattern_subject(self) -> None:
        result = pattern_matching.dispatch_event("cancel")

        self.assertEqual(result.route, "unsupported")

    def test_qualified_name_is_a_value_pattern(self) -> None:
        result = pattern_matching.dispatch_event(pattern_matching.Signal.STOP)

        self.assertEqual(result.route, "stop")

    def test_successful_capture_remains_bound_after_case_suite(self) -> None:
        self.assertEqual(
            pattern_matching.successful_binding_outlives_case(("job", "job-11")),
            "job-11",
        )
        self.assertIsNone(
            pattern_matching.successful_binding_outlives_case(("other", "job-11"))
        )


class ExperimentTests(unittest.TestCase):
    def test_control_flow_experiment_report_is_stable(self) -> None:
        output = control_flow_trace.format_report(control_flow_trace.run_experiment())

        self.assertEqual(
            output,
            "\n".join(
                (
                    "loop break: result=found:2; events=visit:-1 → continue:-1 "
                    "→ visit:2 → break:2 → after-loop",
                    "loop exhaustion: result=not-found; events=visit:-1 → "
                    "continue:-1 → visit:2 → body-tail:2 → visit:3 → "
                    "body-tail:3 → loop-else → after-loop",
                    "guarded match: result=normal:job-7; events=subject → "
                    "guard:urgent=False → guard:valid=True → case:normal",
                    "unmatched subject: result=unsupported; events=subject → "
                    "case:fallback",
                    "binding after case: job-8",
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
