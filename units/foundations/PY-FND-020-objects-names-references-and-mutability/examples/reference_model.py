"""Demonstrate binding, aliasing, mutation, and rebinding deterministically.

The reports use booleans and immutable snapshots instead of printing raw
``id()`` values, whose numeric representation is process-specific.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BindingReport:
    """Observable state around a mutation followed by a rebinding."""

    same_object_before: bool
    caller_after_mutation: tuple[str, ...]
    local_after_rebinding: tuple[str, ...]
    same_object_after: bool


@dataclass(frozen=True)
class AugmentedAssignmentReport:
    """Identity outcomes for ``+=`` on a mutable and immutable sequence."""

    list_kept_identity: bool
    list_alias_observed: tuple[str, ...]
    tuple_kept_identity: bool
    tuple_alias_observed: tuple[str, ...]
    rebound_tuple: tuple[str, ...]


def mutate_then_rebind(statuses: list[str]) -> BindingReport:
    """Mutate the caller's list, then rebind only the local name."""
    local = statuses
    same_object_before = local is statuses

    local.append("running")
    caller_after_mutation = tuple(statuses)

    local = [*local, "done"]
    return BindingReport(
        same_object_before=same_object_before,
        caller_after_mutation=caller_after_mutation,
        local_after_rebinding=tuple(local),
        same_object_after=local is statuses,
    )


def compare_augmented_assignment() -> AugmentedAssignmentReport:
    """Contrast in-place list addition with tuple rebinding."""
    mutable = ["queued"]
    mutable_alias = mutable
    mutable += ["running"]

    immutable = ("queued",)
    immutable_alias = immutable
    immutable += ("running",)

    return AugmentedAssignmentReport(
        list_kept_identity=mutable is mutable_alias,
        list_alias_observed=tuple(mutable_alias),
        tuple_kept_identity=immutable is immutable_alias,
        tuple_alias_observed=immutable_alias,
        rebound_tuple=immutable,
    )


def main() -> None:
    """Print stable observations without depending on memory addresses."""
    caller = ["queued"]
    binding = mutate_then_rebind(caller)
    augmented = compare_augmented_assignment()

    print(f"same object before mutation: {binding.same_object_before}")
    print(f"caller after mutation: {list(binding.caller_after_mutation)}")
    print(f"local after rebinding: {list(binding.local_after_rebinding)}")
    print(f"same object after rebinding: {binding.same_object_after}")
    print(f"list += kept identity: {augmented.list_kept_identity}")
    print(f"list alias observed: {list(augmented.list_alias_observed)}")
    print(f"tuple += kept identity: {augmented.tuple_kept_identity}")
    print(f"tuple alias observed: {augmented.tuple_alias_observed}")
    print(f"rebound tuple: {augmented.rebound_tuple}")


if __name__ == "__main__":
    main()
