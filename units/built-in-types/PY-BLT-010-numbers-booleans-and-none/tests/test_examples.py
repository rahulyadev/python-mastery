"""Deterministic checks for the PY-BLT-010 learning artifacts."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import math
import sys
import unittest


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))
sys.path.insert(
    0,
    str(UNIT_ROOT / "experiments" / "EXP-01-binary-float-neighborhood"),
)

import binary_float_probe  # noqa: E402
import conversion_boundaries  # noqa: E402
import numeric_models  # noqa: E402


class FloorDivisionTests(unittest.TestCase):
    def test_all_sign_combinations_reconstruct_the_dividend(self) -> None:
        expected = {
            (7, 3): (2, 1),
            (-7, 3): (-3, 2),
            (7, -3): (-3, -2),
            (-7, -3): (2, -1),
        }

        for operands, quotient_and_remainder in expected.items():
            with self.subTest(operands=operands):
                result = numeric_models.floor_division(*operands)
                self.assertEqual(
                    (result.quotient, result.remainder),
                    quotient_and_remainder,
                )
                self.assertTrue(result.reconstructs_dividend)

    def test_zero_divisor_is_rejected(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            numeric_models.floor_division(4, 0)

    def test_bool_is_not_silently_accepted_as_a_plain_integer(self) -> None:
        with self.assertRaisesRegex(TypeError, "plain integers"):
            numeric_models.floor_division(True, 1)


class ScalarClassificationTests(unittest.TestCase):
    def test_none_bool_and_zero_remain_distinct_domains(self) -> None:
        self.assertEqual(numeric_models.scalar_kind(None), "missing")
        self.assertEqual(numeric_models.scalar_kind(False), "boolean")
        self.assertEqual(numeric_models.scalar_kind(0), "integer")
        self.assertEqual(numeric_models.scalar_kind(0.0), "finite-float")

    def test_float_special_values_are_explicit(self) -> None:
        self.assertEqual(numeric_models.scalar_kind(float("nan")), "nan")
        self.assertEqual(
            numeric_models.scalar_kind(float("-inf")),
            "infinite-float",
        )

    def test_complex_and_unsupported_values_are_explicit(self) -> None:
        self.assertEqual(numeric_models.scalar_kind(3 + 4j), "complex")
        self.assertEqual(numeric_models.scalar_kind("3"), "unsupported")


class FloatPolicyTests(unittest.TestCase):
    def test_approximate_comparison_uses_an_explicit_policy(self) -> None:
        self.assertFalse(0.1 + 0.2 == 0.3)
        self.assertTrue(numeric_models.finite_measurements_close(0.1 + 0.2, 0.3))

    def test_comparison_near_zero_requires_absolute_tolerance(self) -> None:
        self.assertFalse(numeric_models.finite_measurements_close(1e-12, 0.0))
        self.assertTrue(
            numeric_models.finite_measurements_close(
                1e-12,
                0.0,
                absolute_tolerance=1e-11,
            )
        )

    def test_non_finite_measurements_are_rejected(self) -> None:
        self.assertFalse(
            numeric_models.finite_measurements_close(math.inf, math.inf)
        )
        with self.assertRaisesRegex(ValueError, "finite"):
            numeric_models.accurate_float_total([1.0, math.nan])

    def test_fsum_reduces_error_for_the_representative_total(self) -> None:
        self.assertEqual(numeric_models.accurate_float_total([0.1] * 10), 1.0)


class ConversionBoundaryTests(unittest.TestCase):
    def test_missing_and_explicit_zero_are_preserved(self) -> None:
        self.assertIsNone(conversion_boundaries.parse_optional_retry_count(None))
        self.assertEqual(conversion_boundaries.parse_optional_retry_count("0"), 0)
        self.assertEqual(conversion_boundaries.resolve_batch_size(None, default=50), 50)
        self.assertEqual(conversion_boundaries.resolve_batch_size(0, default=50), 0)

    def test_retry_parser_validates_text_and_domain(self) -> None:
        self.assertEqual(conversion_boundaries.parse_optional_retry_count(" 12 "), 12)
        for raw in ("", "   ", "2.5", "false", "-1"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                conversion_boundaries.parse_optional_retry_count(raw)

    def test_plain_integer_validator_rejects_bool_float_and_negative_int(self) -> None:
        for value in (True, False, 3.0):
            with self.subTest(value=value), self.assertRaises(TypeError):
                conversion_boundaries.require_nonnegative_plain_int(
                    value,
                    field="limit",
                )

        with self.assertRaises(ValueError):
            conversion_boundaries.require_nonnegative_plain_int(-1, field="limit")
        huge = 10**200
        self.assertEqual(
            conversion_boundaries.require_nonnegative_plain_int(huge, field="limit"),
            huge,
        )

    def test_decimal_text_converts_to_exact_cents(self) -> None:
        self.assertEqual(conversion_boundaries.parse_cents("0"), 0)
        self.assertEqual(conversion_boundaries.parse_cents("19.90"), 1990)
        self.assertEqual(conversion_boundaries.parse_cents("1.230"), 123)
        self.assertEqual(Decimal("19.90") * 100, Decimal(1990))

    def test_invalid_money_states_are_rejected(self) -> None:
        for text in ("0.001", "-1.00", "NaN", "Infinity", "not-a-number"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                conversion_boundaries.parse_cents(text)


class ExperimentTests(unittest.TestCase):
    def test_float_probe_exposes_exact_public_representations(self) -> None:
        probe = binary_float_probe.run_experiment()

        self.assertEqual(
            probe.exact_ratio,
            (3602879701896397, 36028797018963968),
        )
        self.assertEqual(probe.hexadecimal, "0x1.999999999999ap-4")
        self.assertNotEqual(probe.lower_neighbor, probe.hexadecimal)
        self.assertNotEqual(probe.upper_neighbor, probe.hexadecimal)
        self.assertFalse(probe.exact_sum_matches)
        self.assertTrue(probe.approximate_sum_matches)
        self.assertEqual(probe.decimal_from_text, "0.1")
        self.assertEqual(probe.fraction_from_text, "1/10")

    def test_float_probe_report_is_stable(self) -> None:
        output = binary_float_probe.format_report(binary_float_probe.run_experiment())
        self.assertEqual(len(output.splitlines()), 6)
        self.assertIn("comparison: exact=False; isclose=True", output)
        self.assertIn("Fraction: text=1/10; from-float=", output)


if __name__ == "__main__":
    unittest.main()
