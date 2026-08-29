"""Conversion and validation boundaries for PY-BLT-010."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation


def require_nonnegative_plain_int(value: object, *, field: str) -> int:
    """Validate an API integer while deliberately rejecting ``bool``."""
    if type(value) is not int:
        raise TypeError(f"{field} must be a plain integer")
    if value < 0:
        raise ValueError(f"{field} cannot be negative")
    return value


def parse_optional_retry_count(raw: str | None) -> int | None:
    """Parse a decimal retry count while preserving the missing state."""
    if raw is None:
        return None
    if not raw.strip():
        raise ValueError("retry count cannot be blank")

    count = int(raw, 10)
    if count < 0:
        raise ValueError("retry count cannot be negative")
    return count


def resolve_batch_size(provided: int | None, *, default: int = 100) -> int:
    """Use the default only for absence; zero remains an explicit value."""
    checked_default = require_nonnegative_plain_int(default, field="default")
    if provided is None:
        return checked_default
    return require_nonnegative_plain_int(provided, field="provided")


def parse_cents(text: str) -> int:
    """Convert a finite, nonnegative decimal amount with at most two places."""
    try:
        amount = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError("amount must be decimal text") from exc

    if not amount.is_finite():
        raise ValueError("amount must be finite")
    if amount < 0:
        raise ValueError("amount cannot be negative")

    cents = amount * 100
    integral_cents = cents.to_integral_value()
    if cents != integral_cents:
        raise ValueError("amount cannot contain fractions of a cent")
    return int(integral_cents)


def main() -> None:
    """Print representative boundary decisions for direct execution."""
    print(f"retry missing: {parse_optional_retry_count(None)!r}")
    print(f"retry zero: {parse_optional_retry_count('0')!r}")
    print(f"batch default: {resolve_batch_size(None, default=50)!r}")
    print(f"batch explicit zero: {resolve_batch_size(0, default=50)!r}")
    print(f"decimal cents: {parse_cents('19.90')!r}")


if __name__ == "__main__":
    main()
