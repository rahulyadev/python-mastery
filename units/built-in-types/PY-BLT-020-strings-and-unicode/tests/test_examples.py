"""Deterministic checks for the PY-BLT-020 learning artifacts."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))
sys.path.insert(
    0,
    str(
        UNIT_ROOT
        / "experiments"
        / "EXP-01-code-points-normalization-and-casefold"
    ),
)

import text_boundaries  # noqa: E402
import unicode_models  # noqa: E402
import unicode_probe  # noqa: E402


class CodePointModelTests(unittest.TestCase):
    def test_indexing_and_len_follow_code_points(self) -> None:
        composed = "\u00e9"
        decomposed = "e\u0301"

        self.assertEqual(len(composed), 1)
        self.assertEqual(len(decomposed), 2)
        self.assertEqual(unicode_models.code_point_notation(composed), ("U+00E9",))
        self.assertEqual(
            unicode_models.code_point_notation(decomposed),
            ("U+0065", "U+0301"),
        )
        self.assertEqual(decomposed[1], "\u0301")

    def test_inspection_exposes_names_categories_and_combining_class(self) -> None:
        base, accent = unicode_models.inspect_code_points("e\u0301")

        self.assertEqual(base.name, "LATIN SMALL LETTER E")
        self.assertEqual(base.category, "Ll")
        self.assertEqual(base.combining_class, 0)
        self.assertEqual(accent.name, "COMBINING ACUTE ACCENT")
        self.assertEqual(accent.category, "Mn")
        self.assertGreater(accent.combining_class, 0)

    def test_one_displayed_symbol_can_span_several_code_points(self) -> None:
        india_flag = "\U0001f1ee\U0001f1f3"
        family = "\U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466"

        self.assertEqual(len(india_flag), 2)
        self.assertEqual(len(family), 7)
        self.assertEqual(family.count("\u200d"), 3)


class NormalizationTests(unittest.TestCase):
    def test_canonically_equivalent_text_is_not_exactly_equal(self) -> None:
        composed = "caf\u00e9"
        decomposed = "cafe\u0301"

        self.assertNotEqual(composed, decomposed)
        self.assertTrue(unicode_models.equal_under_policy(composed, decomposed))

    def test_compatibility_normalization_is_a_distinct_policy(self) -> None:
        circled_one = "\u2460"

        self.assertEqual(unicode_models.normalize_text(circled_one, form="NFC"), circled_one)
        self.assertEqual(unicode_models.normalize_text(circled_one, form="NFKC"), "1")

    def test_casefold_handles_a_case_lower_does_not_remove(self) -> None:
        self.assertNotEqual("Stra\u00dfe".lower(), "STRASSE".lower())
        self.assertTrue(
            unicode_models.equal_under_policy(
                "Stra\u00dfe",
                "STRASSE",
                caseless=True,
            )
        )

    def test_invalid_normalization_policy_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "form must be one of"):
            unicode_models.normalize_text("text", form="UNKNOWN")

    def test_non_string_input_is_rejected(self) -> None:
        with self.assertRaisesRegex(TypeError, "text must be str"):
            unicode_models.normalize_text(b"text")  # type: ignore[arg-type]


class TextBoundaryTests(unittest.TestCase):
    def test_display_text_and_search_key_remain_separate(self) -> None:
        label = text_boundaries.prepare_label("  Cafe\u0301  ")

        self.assertEqual(label.display, "Caf\u00e9")
        self.assertEqual(label.search_key, "caf\u00e9")

    def test_label_validation_rejects_blank_and_control_text(self) -> None:
        for raw in ("", "   ", "line\nbreak", "tab\tinside"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                text_boundaries.prepare_label(raw)

    def test_explicit_separator_preserves_empty_fields(self) -> None:
        self.assertEqual(
            text_boundaries.parse_pipe_record("evt-7||ready"),
            ("evt-7", "", "ready"),
        )
        with self.assertRaisesRegex(ValueError, "expected 3 fields"):
            text_boundaries.parse_pipe_record("evt-7|ready")

    def test_literal_prefix_removal_avoids_character_set_stripping(self) -> None:
        self.assertEqual(text_boundaries.remove_route_prefix("/api/ping"), "ping")
        self.assertEqual(text_boundaries.remove_route_prefix("/ping"), "/ping")
        self.assertNotEqual("/api/ping".lstrip("/api/"), "ping")

    def test_formatting_makes_conversion_and_precision_explicit(self) -> None:
        label = text_boundaries.prepare_label("Caf\u00e9")
        output = text_boundaries.format_request_summary(
            "req-7",
            label,
            latency_ms=1234.5,
        )

        self.assertEqual(
            output,
            "request='req-7' label='Caf\u00e9' latency_ms=1,234.50",
        )

    def test_formatting_rejects_bool_and_negative_latency(self) -> None:
        label = text_boundaries.prepare_label("ready")
        with self.assertRaises(TypeError):
            text_boundaries.format_request_summary("req", label, latency_ms=True)
        with self.assertRaises(ValueError):
            text_boundaries.format_request_summary("req", label, latency_ms=-0.1)


class ExperimentTests(unittest.TestCase):
    def test_probe_exposes_normalization_and_casefold_boundaries(self) -> None:
        probe = unicode_probe.run_experiment()

        self.assertFalse(probe.exact_equal)
        self.assertTrue(probe.nfc_equal)
        self.assertFalse(probe.lower_equal)
        self.assertTrue(probe.casefold_equal)
        self.assertEqual(probe.composed_points, ("U+00E9",))
        self.assertEqual(probe.decomposed_points, ("U+0065", "U+0301"))
        self.assertEqual(len(probe.india_flag_points), 2)
        self.assertEqual(len(probe.family_points), 7)

    def test_probe_report_is_stable(self) -> None:
        output = unicode_probe.format_report(unicode_probe.run_experiment())

        self.assertEqual(len(output.splitlines()), 9)
        self.assertIn("comparison: exact=False; NFC=True", output)
        self.assertIn("caseless: lower=False; casefold=True", output)
        self.assertIn("utf-8: composed-bytes=2; family-bytes=25", output)


if __name__ == "__main__":
    unittest.main()
