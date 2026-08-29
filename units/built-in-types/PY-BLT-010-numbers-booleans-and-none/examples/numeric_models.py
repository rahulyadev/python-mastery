"""Runnable numeric-domain examples for PY-BLT-010."""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Iterable


@dataclass(frozen=True)
class DivisionResult:
    """Expose every value in Python's floor-division invariant."""

    dividend: int
    divisor: int
    quotient: int
    remainder: int

    @property
    def reconstructs_dividend(self) -> bool:
        """Return whether ``dividend == divisor * quotient + remainder``."""
        return self.dividend == self.divisor * self.quotient + self.remainder


def floor_division(dividend: int, divisor: int) -> DivisionResult:
    """Return a checked floor-division result for two plain integers."""
    if type(dividend) is not int or type(divisor) is not int:
        raise TypeError("dividend and divisor must be plain integers")
    if divisor == 0:
        raise ZeroDivisionError("integer division or modulo by zero")

    quotient, remainder = divmod(dividend, divisor)
    result = DivisionResult(dividend, divisor, quotient, remainder)
    if not result.reconstructs_dividend:
        raise AssertionError("Python's division invariant was violated")
    return result


def scalar_kind(value: object) -> str:
    """Classify exact built-in scalar domains without conflating bool and int."""
    if value is None:
        return "missing"
    if type(value) is bool:
        return "boolean"
    if type(value) is int:
        return "integer"
    if type(value) is float:
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "infinite-float"
        return "finite-float"
    if type(value) is complex:
        return "complex"
    return "unsupported"


def finite_measurements_close(
    measured: float,
    expected: float,
    *,
    relative_tolerance: float = 1e-9,
    absolute_tolerance: float = 0.0,
) -> bool:
    """Compare finite measurements under an explicit tolerance policy."""
    if not math.isfinite(measured) or not math.isfinite(expected):
        return False
    return math.isclose(
        measured,
        expected,
        rel_tol=relative_tolerance,
        abs_tol=absolute_tolerance,
    )


def accurate_float_total(values: Iterable[float]) -> float:
    """Sum binary floats with ``math.fsum`` while rejecting non-finite data."""
    finite_values: list[float] = []
    for value in values:
        if not math.isfinite(value):
            raise ValueError("measurements must be finite")
        finite_values.append(value)
    return math.fsum(finite_values)


def main() -> None:
    """Print stable results for direct execution."""
    for operands in ((7, 3), (-7, 3), (7, -3), (-7, -3)):
        print(f"division {operands}: {floor_division(*operands)!r}")

    values: tuple[object, ...] = (None, False, 0, 0.0, float("nan"), 3 + 4j)
    print(f"kinds: {tuple(scalar_kind(value) for value in values)!r}")
    print(
        "float comparison: "
        f"exact={0.1 + 0.2 == 0.3}, "
        f"close={finite_measurements_close(0.1 + 0.2, 0.3)}"
    )
    print(f"accurate total: {accurate_float_total([0.1] * 10)!r}")


if __name__ == "__main__":
    main()
