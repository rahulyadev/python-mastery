"""Report catalog membership changes without applying infrastructure changes."""

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogDiff:
    added: frozenset[str]
    removed: frozenset[str]
    unchanged: frozenset[str]


def _names(values: Iterable[str]) -> frozenset[str]:
    """Consume once; require nonempty names without implicit normalization."""
    if isinstance(values, (str, bytes)):
        raise TypeError("pass an iterable of names, not one string or bytes object")
    names: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            raise TypeError("every catalog name must be a string")
        if not value or value != value.strip():
            raise ValueError("catalog names must be nonempty with no outer whitespace")
        names.add(value)
    return frozenset(names)


def compare_catalogs(before: Iterable[str], after: Iterable[str]) -> CatalogDiff:
    """Compare finite inputs. Duplicates collapse; case remains significant.

    Caller-owned containers are not mutated, but iterator inputs are consumed.
    This is a membership report, not a snapshot across concurrent writers.
    """
    old = _names(before)
    new = _names(after)
    return CatalogDiff(added=new - old, removed=old - new, unchanged=old & new)


def main() -> None:
    diff = compare_catalogs(["search", "billing", "search"], ["billing", "profile"])
    print(f"added: {sorted(diff.added)}")
    print(f"removed: {sorted(diff.removed)}")
    print(f"unchanged: {sorted(diff.unchanged)}")


if __name__ == "__main__":
    main()
