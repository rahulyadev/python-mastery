"""Expose shallow-copy, deep-copy, cycle, and ownership boundaries."""

from __future__ import annotations

from copy import copy, deepcopy
from dataclasses import dataclass
from typing import TypeAlias


Request: TypeAlias = dict[str, list[str]]


@dataclass(frozen=True)
class CopyReport:
    """Identity relationships and final values for one nested graph."""

    shallow_root_is_new: bool
    shallow_roles_are_shared: bool
    deep_roles_are_new: bool
    original_roles: tuple[str, ...]
    shallow_roles: tuple[str, ...]
    deep_roles: tuple[str, ...]


def compare_copy_depths() -> CopyReport:
    """Mutate shallow and deep descendants and report what is shared."""
    original: Request = {"roles": ["reader"]}
    shallow: Request = copy(original)
    deep: Request = deepcopy(original)

    shallow["roles"].append("writer")
    deep["roles"].append("auditor")

    return CopyReport(
        shallow_root_is_new=shallow is not original,
        shallow_roles_are_shared=shallow["roles"] is original["roles"],
        deep_roles_are_new=deep["roles"] is not original["roles"],
        original_roles=tuple(original["roles"]),
        shallow_roles=tuple(shallow["roles"]),
        deep_roles=tuple(deep["roles"]),
    )


def deepcopy_preserves_cycle_shape() -> tuple[bool, bool]:
    """Return whether a recursive clone is new and still self-referential."""
    recursive: list[object] = []
    recursive.append(recursive)

    cloned = deepcopy(recursive)
    return cloned is not recursive, cloned[0] is cloned


def own_request(payload: Request) -> Request:
    """Take an explicit two-level snapshot of the supported request schema."""
    return {field: list(values) for field, values in payload.items()}


def main() -> None:
    """Print deterministic copy and ownership observations."""
    report = compare_copy_depths()
    clone_is_new, clone_kept_cycle = deepcopy_preserves_cycle_shape()

    incoming: Request = {"roles": ["reader"], "regions": ["ap-south"]}
    owned = own_request(incoming)
    incoming["roles"].append("writer")

    print(f"shallow root is new: {report.shallow_root_is_new}")
    print(f"shallow nested list is shared: {report.shallow_roles_are_shared}")
    print(f"deep nested list is new: {report.deep_roles_are_new}")
    print(f"original roles: {list(report.original_roles)}")
    print(f"shallow roles: {list(report.shallow_roles)}")
    print(f"deep roles: {list(report.deep_roles)}")
    print(f"recursive clone is new: {clone_is_new}")
    print(f"recursive clone preserves cycle: {clone_kept_cycle}")
    print(f"owned roles after caller mutation: {owned['roles']}")


if __name__ == "__main__":
    main()
