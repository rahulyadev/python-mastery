"""Contract and boundary checks for authored teaching code, not learner solutions."""

import sys
import unittest
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
sys.path.insert(0, str(EXAMPLES))

from mapping_operations import MissingLabel, describe_lookup, eager_defaults  # noqa: E402
from settings_overlay import merge_known_settings  # noqa: E402


class ReadOnlySettings(Mapping[str, object]):
    """Exercise the mapping contract without inheriting dict or supporting |."""

    def __init__(self, values: dict[str, object]) -> None:
        self._values = values

    def __getitem__(self, key: str) -> object:
        return self._values[key]

    def __iter__(self):
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)


class LookupTests(unittest.TestCase):
    def test_absence_is_not_none(self) -> None:
        self.assertEqual(describe_lookup({}, "quota"), "missing")
        self.assertEqual(describe_lookup({"quota": None}, "quota"), "present: None")

    def test_falsey_values_remain_present(self) -> None:
        for value in (False, 0, "", [], {}):
            with self.subTest(value=value):
                self.assertEqual(describe_lookup({"x": value}, "x"), f"present: {value!r}")

    def test_lookup_does_not_insert(self) -> None:
        data: dict[str, object] = {}
        describe_lookup(data, "absent")
        self.assertEqual(data, {})

    def test_defaults_are_evaluated_on_hits(self) -> None:
        self.assertEqual(eager_defaults(), (0, 0, ["built", "built"]))

    def test_missing_hook_does_not_insert_by_itself(self) -> None:
        labels = MissingLabel()
        self.assertEqual(labels["west"], "unknown:west")
        self.assertNotIn("west", labels)

    def test_get_bypasses_missing_hook(self) -> None:
        labels = MissingLabel()
        self.assertIsNone(labels.get("west"))
        self.assertEqual(labels.get("west", "fallback"), "fallback")

    def test_stored_value_bypasses_missing_hook(self) -> None:
        labels = MissingLabel(west="ready")
        self.assertEqual(labels["west"], "ready")


class OverlayTests(unittest.TestCase):
    def test_empty_inputs(self) -> None:
        self.assertEqual(merge_known_settings({}, {}), {})

    def test_no_overrides_still_makes_an_outer_copy(self) -> None:
        defaults = {"retries": 3}
        result = merge_known_settings(defaults, {})
        self.assertEqual(result, defaults)
        self.assertIsNot(result, defaults)

    def test_falsey_overrides_are_not_discarded(self) -> None:
        for value in (0, False, None, "", [], {}):
            with self.subTest(value=value):
                self.assertEqual(merge_known_settings({"x": 7}, {"x": value}), {"x": value})

    def test_unknown_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown settings: 'retry'"):
            merge_known_settings({"retries": 3}, {"retry": 5})

    def test_unknown_key_does_not_partially_mutate_either_input(self) -> None:
        defaults = {"retries": 3}
        overrides = {"retries": 0, "typo": 1}
        with self.assertRaises(ValueError):
            merge_known_settings(defaults, overrides)
        self.assertEqual(defaults, {"retries": 3})
        self.assertEqual(overrides, {"retries": 0, "typo": 1})

    def test_override_iteration_order_does_not_reorder_existing_names(self) -> None:
        result = merge_known_settings({"a": 1, "b": 2, "c": 3}, {"c": 30, "a": 10})
        self.assertEqual(list(result.items()), [("a", 10), ("b", 2), ("c", 30)])

    def test_accepts_read_only_mapping_inputs(self) -> None:
        defaults = ReadOnlySettings({"quota": 3})
        overrides = MappingProxyType({"quota": 0})
        self.assertEqual(merge_known_settings(defaults, overrides), {"quota": 0})

    def test_overridden_nested_mapping_is_replaced_as_a_whole(self) -> None:
        default_options = {"connect": 3, "read": 10}
        override_options = {"connect": 1}
        result = merge_known_settings(
            {"options": default_options}, {"options": override_options}
        )
        self.assertEqual(result["options"], {"connect": 1})
        self.assertIs(result["options"], override_options)
        self.assertEqual(default_options, {"connect": 3, "read": 10})

    def test_unoverridden_mutable_child_remains_shared(self) -> None:
        tags = ["base"]
        defaults = {"tags": tags}
        result = merge_known_settings(defaults, {})
        tags.append("canary")
        self.assertIs(result["tags"], tags)
        self.assertEqual(result["tags"], ["base", "canary"])

    def test_rebinding_result_leaves_input_mapping_unchanged(self) -> None:
        defaults = {"retries": 3}
        result = merge_known_settings(defaults, {})
        result["retries"] = 1
        self.assertEqual(defaults["retries"], 3)


class MappingBoundaryTests(unittest.TestCase):
    def test_equal_numeric_keys_share_one_entry(self) -> None:
        data = {1: "one", True: "true", 1.0: "float"}
        self.assertEqual(len(data), 1)
        self.assertEqual(data[1], "float")

    def test_tuple_with_unhashable_child_cannot_be_a_key(self) -> None:
        with self.assertRaises(TypeError):
            dict([(("zone", []), 1)])

    def test_key_view_and_key_snapshot_diverge_after_insertion(self) -> None:
        data = {"a": 1}
        view, snapshot = data.keys(), tuple(data)
        data["b"] = 2
        self.assertEqual(list(view), ["a", "b"])
        self.assertEqual(snapshot, ("a",))

    def test_item_snapshot_keeps_mutable_value_reference(self) -> None:
        tags: list[str] = []
        data = {"tags": tags}
        snapshot = tuple(data.items())
        tags.append("edited")
        data["tags"] = ["replacement"]
        self.assertIs(snapshot[0][1], tags)
        self.assertEqual(snapshot, (("tags", ["edited"]),))

    def test_read_only_proxy_is_live_and_does_not_freeze_children(self) -> None:
        tags: list[str] = []
        data: dict[str, object] = {"tags": tags, "quota": 3}
        proxy = MappingProxyType(data)
        tags.append("edited")
        data["quota"] = 0
        self.assertEqual(proxy["quota"], 0)
        self.assertEqual(proxy["tags"], ["edited"])
        with self.assertRaises(TypeError):
            proxy["quota"] = 8

    def test_update_returns_none_and_in_place_union_preserves_alias(self) -> None:
        data = {"a": 1}
        alias = data
        self.assertIsNone(data.update({"a": 2}))
        data |= [("b", 3)]
        self.assertIs(data, alias)
        self.assertEqual(data, {"a": 2, "b": 3})

    def test_binary_union_rejects_pair_iterable(self) -> None:
        with self.assertRaises(TypeError):
            {"a": 1} | [("b", 2)]

    def test_value_replacement_keeps_order_but_reinsertion_moves_to_end(self) -> None:
        data = {"a": 1, "b": 2}
        data["a"] = 3
        self.assertEqual(list(data), ["a", "b"])
        del data["a"]
        data["a"] = 4
        self.assertEqual(list(data), ["b", "a"])
        self.assertEqual(data.popitem(), ("a", 4))

    def test_fromkeys_reuses_its_single_default_object(self) -> None:
        child: list[int] = []
        data = dict.fromkeys(("a", "b"), child)
        self.assertIs(data["a"], data["b"])
        child.append(1)
        self.assertEqual(data, {"a": [1], "b": [1]})

    def test_items_view_membership_can_compare_unhashable_values(self) -> None:
        data = {"tags": ["base"]}
        self.assertIn(("tags", ["base"]), data.items())
        with self.assertRaises(TypeError):
            set(data.items())

    def test_dictionary_equality_ignores_insertion_order(self) -> None:
        left = {"a": 1, "b": 2}
        right = {"b": 2, "a": 1}
        self.assertEqual(left, right)
        self.assertNotEqual(list(left.items()), list(right.items()))


if __name__ == "__main__":
    unittest.main()
