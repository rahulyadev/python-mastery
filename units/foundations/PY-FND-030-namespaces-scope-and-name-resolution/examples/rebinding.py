"""Demonstrate global, nonlocal, class, and comprehension scope rules."""

from __future__ import annotations

from collections.abc import Callable


MODULE_LABEL = "module"
MODULE_EVENTS = 0


def record_module_event() -> int:
    """Rebind a module-global counter and return its new value."""
    global MODULE_EVENTS
    MODULE_EVENTS += 1
    return MODULE_EVENTS


def make_counter(start: int = 0) -> Callable[[], int]:
    """Create a counter whose calls rebind one enclosing-function name."""
    count = start

    def increment() -> int:
        nonlocal count
        count += 1
        return count

    return increment


class Policy:
    """Show that a method's bare-name lookup skips the class namespace."""

    MODULE_LABEL = "class"

    def bare_label(self) -> str:
        """Resolve the bare name in the defining module."""
        return MODULE_LABEL

    def attribute_label(self) -> str:
        """Resolve the class attribute through normal attribute lookup."""
        return self.MODULE_LABEL


def comprehension_report(values: list[int]) -> tuple[str, tuple[int, ...]]:
    """Show that a comprehension target does not leak into its outer scope."""
    item = "outer"
    doubled = [item * 2 for item in values]
    return item, tuple(doubled)


def main() -> None:
    """Print deterministic rebinding and scope observations."""
    first = make_counter(10)
    second = make_counter(100)
    policy = Policy()
    outer_item, doubled = comprehension_report([1, 2, 3])

    print(f"module event counts: {record_module_event()}, {record_module_event()}")
    print(f"first closure: {first()}, {first()}")
    print(f"second closure: {second()}")
    print(f"bare method name: {policy.bare_label()}")
    print(f"class attribute: {policy.attribute_label()}")
    print(f"outer item after comprehension: {outer_item}")
    print(f"comprehension values: {doubled}")


if __name__ == "__main__":
    main()
