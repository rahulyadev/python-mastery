"""Expose the exact binary-float neighborhood behind decimal spellings."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
import math


@dataclass(frozen=True)
class FloatProbe:
    """Deterministic observations for one binary floating-point run."""

    value_repr: str
    exact_ratio: tuple[int, int]
    hexadecimal: str
    lower_neighbor: str
    upper_neighbor: str
    ulp: str
    sum_repr: str
    sum_ratio: tuple[int, int]
    exact_sum_matches: bool
    approximate_sum_matches: bool
    decimal_from_text: str
    decimal_from_float: str
    fraction_from_text: str
    fraction_from_float: str


def run_experiment() -> FloatProbe:
    """Capture exact public representations around ``float('0.1')``."""
    value = float("0.1")
    total = float("0.1") + float("0.2")

    return FloatProbe(
        value_repr=repr(value),
        exact_ratio=value.as_integer_ratio(),
        hexadecimal=value.hex(),
        lower_neighbor=math.nextafter(value, -math.inf).hex(),
        upper_neighbor=math.nextafter(value, math.inf).hex(),
        ulp=math.ulp(value).hex(),
        sum_repr=repr(total),
        sum_ratio=total.as_integer_ratio(),
        exact_sum_matches=total == float("0.3"),
        approximate_sum_matches=math.isclose(total, float("0.3")),
        decimal_from_text=str(Decimal("0.1")),
        decimal_from_float=str(Decimal.from_float(value)),
        fraction_from_text=str(Fraction("0.1")),
        fraction_from_float=str(Fraction.from_float(value)),
    )


def format_report(probe: FloatProbe) -> str:
    """Format the observation without addresses, timing, or private state."""
    numerator, denominator = probe.exact_ratio
    sum_numerator, sum_denominator = probe.sum_ratio
    return "\n".join(
        (
            f"0.1: repr={probe.value_repr}; ratio={numerator}/{denominator}; "
            f"hex={probe.hexadecimal}",
            f"neighbors: lower={probe.lower_neighbor}; chosen={probe.hexadecimal}; "
            f"upper={probe.upper_neighbor}; ulp={probe.ulp}",
            f"0.1 + 0.2: repr={probe.sum_repr}; "
            f"ratio={sum_numerator}/{sum_denominator}",
            f"comparison: exact={probe.exact_sum_matches}; "
            f"isclose={probe.approximate_sum_matches}",
            f"Decimal: text={probe.decimal_from_text}; "
            f"from-float={probe.decimal_from_float}",
            f"Fraction: text={probe.fraction_from_text}; "
            f"from-float={probe.fraction_from_float}",
        )
    )


def main() -> None:
    """Run and print the experiment."""
    print(format_report(run_experiment()))


if __name__ == "__main__":
    main()
