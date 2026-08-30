"""Behavioral checks for worked examples and important sequence boundaries.

No learner solutions or expected answers to the practice snippets live here.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))

from batch_plan import build_batch_plan  # noqa: E402
from sequence_operations import (  # noqa: E402
    mutation_and_rebinding,
    slice_trace,
    stable_priority_order,
)


class BatchPlanTests(unittest.TestCase):
    def test_order_duplicates_and_short_tail_are_preserved(self) -> None:
        incoming = ["a", "b", "a", "c", "d"]
        self.assertEqual(build_batch_plan(incoming, 2), [("a", "b"), ("a", "c"), ("d",)])
        self.assertEqual(incoming, ["a", "b", "a", "c", "d"])

    def test_empty_singleton_exact_and_oversized_batches(self) -> None:
        cases = [
            ([], 3, []),
            (["x"], 1, [("x",)]),
            (["x", "y"], 1, [("x",), ("y",)]),
            (["x", "y"], 2, [("x", "y")]),
            (["x", "y"], 10, [("x", "y")]),
        ]
        for incoming, size, expected in cases:
            with self.subTest(incoming=incoming, size=size):
                self.assertEqual(build_batch_plan(incoming, size), expected)

    def test_later_input_mutation_does_not_change_batch_membership(self) -> None:
        incoming = ["a", "b", "c"]
        plan = build_batch_plan(incoming, 2)
        incoming[0] = "changed"
        incoming.clear()
        self.assertEqual(plan, [("a", "b"), ("c",)])
        self.assertIsInstance(plan, list)
        self.assertTrue(all(isinstance(batch, tuple) for batch in plan))

    def test_reordering_plan_does_not_reorder_input(self) -> None:
        incoming = ["a", "b", "c"]
        plan = build_batch_plan(incoming, 2)
        plan.reverse()
        self.assertEqual(incoming, ["a", "b", "c"])

    def test_each_input_position_appears_once_across_many_boundaries(self) -> None:
        for count in range(15):
            incoming = [str(index) for index in range(count)]
            for size in range(1, 18):
                with self.subTest(count=count, size=size):
                    plan = build_batch_plan(incoming, size)
                    self.assertEqual([item for batch in plan for item in batch], incoming)
                    self.assertTrue(all(0 < len(batch) <= size for batch in plan))
                    self.assertTrue(all(len(batch) == size for batch in plan[:-1]))

    def test_nonpositive_batch_size_is_rejected_even_for_empty_input(self) -> None:
        for size in (0, -1, -100):
            with self.subTest(size=size), self.assertRaises(ValueError):
                build_batch_plan([], size)

    def test_bool_float_and_text_batch_sizes_are_rejected(self) -> None:
        for size in (True, False, 2.0, "2", None):
            with self.subTest(size=size), self.assertRaises(TypeError):
                build_batch_plan(["a"], size)  # type: ignore[arg-type]

    def test_wrong_container_and_mutable_identifiers_are_rejected(self) -> None:
        for incoming in ("ab", ("a", "b"), [["a"]], [1]):
            with self.subTest(incoming=incoming), self.assertRaises(TypeError):
                build_batch_plan(incoming, 2)  # type: ignore[arg-type]


class SequenceBoundaryTests(unittest.TestCase):
    def test_slice_positions_match_selection_across_bounds_and_directions(self) -> None:
        bounds = (None, -12, -1, 0, 1, 4, 12)
        for count in range(8):
            values = list("ABCDEFG")[:count]
            for start in bounds:
                for stop in bounds:
                    for step in (None, -9, -2, -1, 1, 2, 9):
                        with self.subTest(count=count, start=start, stop=stop, step=step):
                            normalized, positions, result = slice_trace(
                                values, slice(start, stop, step)
                            )
                            self.assertEqual(result, [values[index] for index in positions])
                            self.assertEqual(positions, list(range(*normalized)))

    def test_omitted_negative_stop_differs_from_explicit_minus_one(self) -> None:
        values = list("ABCDEF")
        self.assertEqual(slice_trace(values, slice(None, None, -1))[2], list("FEDCBA"))
        self.assertEqual(slice_trace(values, slice(None, -1, -1))[2], [])
        normalized = slice(None, None, -1).indices(len(values))
        self.assertEqual(values[slice(*normalized)], [])

    def test_bad_index_fails_but_slice_clips(self) -> None:
        values = [10, 20]
        with self.assertRaises(IndexError):
            _ = values[9]
        self.assertEqual(values[9:99], [])
        self.assertEqual(values[-99:99], values)
        self.assertIsNot(values[-99:99], values)

    def test_zero_step_and_non_integer_index_fail(self) -> None:
        with self.assertRaises(ValueError):
            slice_trace(["a"], slice(None, None, 0))
        values = [10, 20]
        with self.assertRaises(TypeError):
            _ = values[1.0]  # type: ignore[call-overload]

    def test_slice_assignment_preserves_list_identity_and_can_resize(self) -> None:
        values = [0, 1, 2, 3]
        alias = values
        values[1:3] = [8, 9, 10]
        self.assertIs(values, alias)
        self.assertEqual(alias, [0, 8, 9, 10, 3])
        values[2:2] = [7]
        self.assertEqual(alias, [0, 8, 7, 9, 10, 3])

    def test_extended_assignment_requires_matching_size_but_deletion_does_not(self) -> None:
        values = [0, 1, 2, 3, 4]
        with self.assertRaises(ValueError):
            values[::2] = [8]
        self.assertEqual(values, [0, 1, 2, 3, 4])
        values[::2] = [8, 9, 10]
        self.assertEqual(values, [8, 1, 9, 3, 10])
        del values[::2]
        self.assertEqual(values, [1, 3])

    def test_rebinding_after_in_place_addition_leaves_alias_on_old_list(self) -> None:
        current, shared = mutation_and_rebinding()
        self.assertEqual(current, [10, 20, 30, 40])
        self.assertEqual(shared, [10, 20, 30])
        self.assertIsNot(current, shared)

    def test_shallow_and_deep_copy_have_different_sharing_boundaries(self) -> None:
        child = [1]
        original = [child, child]
        shallow, deep = original.copy(), deepcopy(original)
        child.append(2)
        self.assertIsNot(original, shallow)
        self.assertIs(shallow[0], original[0])
        self.assertEqual(deep, [[1], [1]])
        self.assertIs(deep[0], deep[1])
        self.assertIsNot(deep[0], child)

    def test_tuple_is_not_deeply_immutable_or_automatically_hashable(self) -> None:
        value = ([1],)
        value[0].append(2)
        self.assertEqual(value, ([1, 2],))
        with self.assertRaises(TypeError):
            hash(value)

    def test_failed_tuple_augmented_assignment_does_not_roll_back_child_mutation(self) -> None:
        value = ([],)
        with self.assertRaises(TypeError):
            value[0] += [7]
        self.assertEqual(value[0], [7])

    def test_priority_sort_preserves_ties_without_reordering_input(self) -> None:
        jobs = [(2, "c"), (1, "b"), (1, "a")]
        ordered = stable_priority_order(jobs)
        self.assertEqual(ordered, [(1, "b"), (1, "a"), (2, "c")])
        self.assertEqual(jobs, [(2, "c"), (1, "b"), (1, "a")])
        self.assertIsNot(ordered, jobs)

    def test_append_and_extend_have_distinct_nesting(self) -> None:
        nested, flat = [], []
        self.assertIsNone(nested.append([1, 2]))
        self.assertIsNone(flat.extend([1, 2]))
        self.assertEqual(nested, [[1, 2]])
        self.assertEqual(flat, [1, 2])

    def test_list_tuple_comparison_does_not_implicitly_convert(self) -> None:
        self.assertNotEqual([1, 2], (1, 2))
        self.assertLess((1, 9), (2, 0))
        with self.assertRaises(TypeError):
            _ = [1] < (2,)


class RangeTests(unittest.TestCase):
    def test_negative_step_and_slice_preserve_arithmetic_progression(self) -> None:
        values = range(17, 2, -4)
        self.assertEqual(list(values), [17, 13, 9, 5])
        self.assertEqual(values[-1], 5)
        self.assertIsInstance(values[1::2], range)
        self.assertEqual(list(values[1::2]), [13, 5])

    def test_equality_depends_on_values_not_constructor_arguments(self) -> None:
        self.assertEqual(range(0, 4, 2), range(0, 3, 2))
        self.assertEqual(range(5, 5, -3), range(0))
        self.assertNotEqual(range(3), [0, 1, 2])

    def test_range_is_reiterable_but_not_itself_an_iterator(self) -> None:
        values = range(2, 8, 2)
        first, second = iter(values), iter(values)
        self.assertEqual((next(first), next(first), next(second)), (2, 4, 2))
        with self.assertRaises(TypeError):
            next(values)

    def test_membership_uses_values_not_only_integer_types(self) -> None:
        self.assertIn(4, range(0, 10, 2))
        self.assertIn(4.0, range(0, 10, 2))
        self.assertNotIn(4.5, range(0, 10, 2))
        self.assertNotIn("4", range(0, 10, 2))

    def test_huge_range_is_usable_when_len_overflows(self) -> None:
        values = range(0, 10**40, 3)
        self.assertEqual(list(values[:3]), [0, 3, 6])
        self.assertIn(3 * 10**30, values)
        with self.assertRaises(OverflowError):
            len(values)

    def test_invalid_range_step_and_unsupported_operations_fail(self) -> None:
        with self.assertRaises(ValueError):
            range(0, 3, 0)
        with self.assertRaises(TypeError):
            _ = range(3) + range(3)
        with self.assertRaises(TypeError):
            _ = range(3) * 2


if __name__ == "__main__":
    unittest.main()
