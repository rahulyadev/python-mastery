"""Author-artifact checks; these do not execute or solve learner exercises."""

import contextlib
import io
import json
import operator
import re
import runpy
import subprocess
import sys
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
OPERATIONS = runpy.run_path(str(UNIT / "examples/set_operations.py"))
CATALOG = runpy.run_path(str(UNIT / "examples/catalog_diff.py"))
ALIASES = runpy.run_path(
    str(UNIT / "experiments/EXP-01-aliases-and-frozen-members/probe_aliases.py")
)
HASHING = runpy.run_path(
    str(UNIT / "experiments/EXP-02-hash-seeds-and-collisions/probe_hashing.py")
)
TRACES = runpy.run_path(str(UNIT / "visuals/trace_data.py"))


class SetContractTests(unittest.TestCase):
    def test_empty_constructors_and_truth(self):
        self.assertIsInstance({}, dict)
        self.assertIsInstance(set(), set)
        self.assertFalse(set())
        self.assertFalse(frozenset())
        self.assertTrue({0})

    def test_constructors_consume_members_not_a_whole_string(self):
        self.assertEqual(set("queue"), {"q", "u", "e"})
        self.assertEqual(set(["queue"]), {"queue"})
        self.assertEqual(frozenset([2, 2, 3]), {2, 3})

    def test_numeric_equality_collapses_members(self):
        values = [1, True, 1.0]
        self.assertEqual(len(set(values)), 1)
        self.assertEqual(set(values), {1})
        self.assertEqual(hash(True), hash(1.0))

    def test_unhashable_members_are_rejected(self):
        for item in ([], {}, set(), ([],)):
            for constructor in (set, frozenset):
                with (
                    self.subTest(item=type(item).__name__, constructor=constructor),
                    self.assertRaises(TypeError),
                ):
                    constructor([item])

    def test_containers_with_hashable_members(self):
        self.assertEqual(len({("api", 1), frozenset(["api"])}), 2)

    def test_sets_do_not_support_indexing(self):
        with self.assertRaises(TypeError):
            operator.getitem({"api"}, 0)

    def test_worked_algebra(self):
        self.assertEqual(
            OPERATIONS["algebra"](),
            {
                "union": ["api", "cache", "cron", "worker"],
                "intersection": ["cache"],
                "current_only": ["api", "worker"],
                "desired_only": ["cron"],
                "symmetric_difference": ["api", "cron", "worker"],
            },
        )

    def test_algebra_leaves_operands_unchanged(self):
        a, b = {1, 2}, {2, 3}
        for operation in (operator.or_, operator.and_, operator.sub, operator.xor):
            result = operation(a, b)
            self.assertIsNot(result, a)
            self.assertEqual(a, {1, 2})
            self.assertEqual(b, {2, 3})

    def test_methods_accept_iterables(self):
        a = {1, 2, 3}
        self.assertEqual(a.union([4], (5,)), {1, 2, 3, 4, 5})
        self.assertEqual(a.intersection([2, 3], (3, 4)), {3})
        self.assertEqual(a.difference([1], (2,)), {3})
        self.assertEqual(a.symmetric_difference([3, 4, 4]), {1, 2, 4})
        self.assertTrue(a.issubset([1, 2, 3, 4]))
        self.assertTrue(a.issuperset(iter([1, 2])))
        self.assertTrue(a.isdisjoint([4]))

    def test_builtin_operators_reject_lists(self):
        for operation in (
            operator.or_,
            operator.and_,
            operator.sub,
            operator.xor,
            operator.ior,
            operator.iand,
            operator.isub,
            operator.ixor,
        ):
            with self.subTest(operation=operation.__name__), self.assertRaises(TypeError):
                operation({1, 2}, [2])

    def test_comparisons_are_partial_not_total(self):
        self.assertTrue({1} < {1, 2})
        self.assertTrue({1} <= {1})
        self.assertFalse({1} < {1})
        self.assertFalse({1} < {2})
        self.assertFalse({1} > {2})
        self.assertNotEqual({1}, {2})

    def test_empty_set_relationships(self):
        self.assertTrue(set().issubset(set()))
        self.assertFalse(set() < set())
        self.assertTrue(set() < {1})
        self.assertTrue(set().isdisjoint(set()))

    def test_mixed_frozen_result_type(self):
        for operation in (operator.or_, operator.and_, operator.sub, operator.xor):
            with self.subTest(operation=operation.__name__):
                self.assertIs(type(operation(frozenset([1, 2]), {2, 3})), frozenset)
                self.assertIs(type(operation({1, 2}, frozenset([2, 3]))), set)

    def test_frozen_key_ignores_order_and_duplicates(self):
        self.assertEqual(OPERATIONS["frozen_key"](), ("compressed-json", True))
        self.assertEqual(hash(frozenset([1, 2])), hash(frozenset([2, 1, 1])))

    def test_frozen_has_no_membership_mutators(self):
        for method in ("add", "remove", "discard", "clear", "update", "pop"):
            self.assertFalse(hasattr(frozenset(), method))
        with self.assertRaises(TypeError):
            hash(set())

    def test_mutation_and_return_values(self):
        self.assertEqual(
            OPERATIONS["mutation"](),
            {
                "members": ["api", "cache", "worker"],
                "same_object": True,
                "add_return": None,
                "update_return": None,
            },
        )

    def test_add_and_update_are_different(self):
        added, updated = set(), set()
        added.add("api")
        updated.update("api")
        self.assertEqual(added, {"api"})
        self.assertEqual(updated, {"a", "p", "i"})

    def test_remove_discard_and_pop_contracts(self):
        members = {"api", "worker"}
        self.assertIsNone(members.discard("missing"))
        with self.assertRaises(KeyError):
            members.remove("missing")
        before = members.copy()
        removed = members.pop()
        self.assertIn(removed, before)
        self.assertEqual(members, before - {removed})
        self.assertIsNone(members.clear())
        with self.assertRaises(KeyError):
            members.pop()

    def test_all_update_methods(self):
        cases = [
            ("update", {1, 2, 3}),
            ("intersection_update", {2}),
            ("difference_update", {1}),
            ("symmetric_difference_update", {1, 3}),
        ]
        for name, expected in cases:
            members = {1, 2}
            alias = members
            self.assertIsNone(getattr(members, name)([2, 3]))
            self.assertIs(members, alias)
            self.assertEqual(members, expected)

    def test_augmented_set_union_mutates_alias(self):
        members = {1}
        alias = members
        members |= {2}
        self.assertIs(members, alias)
        self.assertEqual(alias, {1, 2})

    def test_copy_freeze_and_rebinding(self):
        members = {1}
        alias = members
        copied = members.copy()
        frozen = frozenset(members)
        members.add(2)
        self.assertEqual(alias, {1, 2})
        self.assertEqual(copied, {1})
        self.assertEqual(frozen, {1})
        previous = frozen
        frozen |= {3}
        self.assertEqual(previous, {1})
        self.assertEqual(frozen, {1, 3})
        self.assertIsNot(frozen, previous)

    def test_frozen_members_can_have_mutable_non_key_state(self):
        job = ALIASES["Job"]("queued")
        members = frozenset([job])
        original_hash = hash(job)
        job.status = "done"
        self.assertIn(job, members)
        self.assertEqual(hash(job), original_hash)
        self.assertEqual(next(iter(members)).status, "done")

    def test_mutable_set_lookup_convenience_does_not_allow_insertion(self):
        nested = {frozenset([1, 2])}
        self.assertIn({1, 2}, nested)
        with self.assertRaises(TypeError):
            nested.add({1, 2})
        nested.remove({1, 2})
        self.assertEqual(nested, set())
        self.assertIsNone(nested.discard({1, 2}))

    def test_collisions_do_not_merge_unequal_objects(self):
        key_type = HASHING["CollidingKey"]
        members = {key_type(1), key_type(2), key_type(1)}
        self.assertEqual(len(members), 2)
        self.assertIn(key_type(1), members)
        self.assertNotIn(key_type(3), members)


class CatalogTests(unittest.TestCase):
    def test_membership_diff(self):
        diff = CATALOG["compare_catalogs"](["search", "billing"], ["billing", "profile"])
        self.assertEqual(diff.added, {"profile"})
        self.assertEqual(diff.removed, {"search"})
        self.assertEqual(diff.unchanged, {"billing"})
        self.assertIsInstance(diff.added, frozenset)

    def test_no_caller_mutation_and_repeated_names(self):
        before, after = ["api", "api"], ["worker", "worker"]
        diff = CATALOG["compare_catalogs"](before, after)
        self.assertEqual(diff.removed, {"api"})
        self.assertEqual(diff.added, {"worker"})
        self.assertEqual(before, ["api", "api"])
        self.assertEqual(after, ["worker", "worker"])

    def test_empty_identical_and_case_sensitive_inputs(self):
        compare = CATALOG["compare_catalogs"]
        self.assertEqual(
            compare([], []), CATALOG["CatalogDiff"](frozenset(), frozenset(), frozenset())
        )
        self.assertEqual(compare(["api"], ["api"]).unchanged, {"api"})
        self.assertEqual(compare(["API"], ["api"]).added, {"api"})

    def test_one_shot_iterators_are_consumed_once(self):
        before, after = iter(["api", "cache"]), iter(["cache"])
        diff = CATALOG["compare_catalogs"](before, after)
        self.assertEqual(diff.removed, {"api"})
        self.assertEqual(list(before), [])
        self.assertEqual(list(after), [])

    def test_rejects_bare_string_and_bytes_inputs_on_either_side(self):
        for bad in ("api", b"api"):
            for before, after in ((bad, []), ([], bad)):
                with self.subTest(before=before, after=after), self.assertRaises(TypeError):
                    CATALOG["compare_catalogs"](before, after)

    def test_rejects_non_string_names(self):
        for bad in (1, True, None, [], b"api"):
            with self.subTest(value=bad), self.assertRaises(TypeError):
                CATALOG["compare_catalogs"]([], [bad])

    def test_rejects_empty_and_outer_whitespace(self):
        for bad in ("", " api", "api ", "\t"):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                CATALOG["compare_catalogs"]([bad], [])


class ArtifactTests(unittest.TestCase):
    def test_embedded_visual_data_matches_python(self):
        html = (UNIT / "visuals/set-explorer.html").read_text(encoding="utf-8")
        match = re.search(
            r'<script id="python-traces" type="application/json">\s*(.*?)\s*</script>', html, re.S
        )
        self.assertIsNotNone(match)
        embedded = json.loads(match.group(1))
        self.assertEqual(embedded, TRACES["build_traces"]())
        self.assertEqual(sum(len(state["results"]) for state in embedded), 25)

    def test_visual_partitions_and_algebra_invariants(self):
        for state in TRACES["build_traces"]():
            with self.subTest(scenario=state["id"]):
                a, b = set(state["a"]), set(state["b"])
                left, common, right = (
                    set(state["left_only"]),
                    set(state["both"]),
                    set(state["right_only"]),
                )
                self.assertTrue(left.isdisjoint(common | right))
                self.assertTrue(common.isdisjoint(right))
                self.assertEqual(left | common, a)
                self.assertEqual(right | common, b)
                self.assertEqual(set(state["results"]["symmetric_difference"]), (a | b) - (a & b))

    def test_runnable_note_snippets(self):
        note = (UNIT / "README.md").read_text(encoding="utf-8")
        snippets = re.findall(r"Runnable check: ([a-z-]+)\.\n\n```python\n(.*?)\n```", note, re.S)
        expected = {
            "core": "['cron']\n['api', 'worker']\n",
            "construction": "True 1\n",
            "relations": "False False False\nTrue False\n",
            "frozen": "1 True\n",
        }
        self.assertEqual({name for name, code in snippets}, set(expected))
        for name, code in snippets:
            with self.subTest(snippet=name):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exec(compile(code, str(UNIT / "README.md"), "exec"), {})
                self.assertEqual(output.getvalue(), expected[name])

    def test_recorded_experiment_transcripts(self):
        if (sys.implementation.name, sys.version_info[:3]) not in (
            ("cpython", (3, 14, 7)),
            ("cpython", (3, 11, 16)),
        ):
            self.skipTest("Exact transcript audit is pinned; semantic tests remain portable")
        experiments = (
            ("EXP-01-aliases-and-frozen-members", "probe_aliases.py"),
            ("EXP-02-hash-seeds-and-collisions", "probe_hashing.py"),
        )
        for directory, script in experiments:
            with self.subTest(experiment=directory):
                root = UNIT / "experiments" / directory
                note = (root / "README.md").read_text(encoding="utf-8")
                match = re.search(r"Recorded stdout:\n\n```text\n(.*?)\n```", note, re.S)
                self.assertIsNotNone(match)
                result = subprocess.run(
                    [sys.executable, "-B", str(root / script)],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.stdout, match.group(1) + "\n")

    def test_seeded_probe_preserves_membership(self):
        first, second = HASHING["seeded_order"](1), HASHING["seeded_order"](2)
        self.assertEqual(first["sorted"], second["sorted"])
        self.assertEqual(set(first["iteration"]), set(second["iteration"]))

    def test_lookup_probe_preserves_unequal_members(self):
        for name in ("SpreadKey", "CollidingKey"):
            with self.subTest(kind=name):
                size, present, calls = HASHING["lookup_work"](HASHING[name])
                self.assertEqual(size, 64)
                self.assertFalse(present)
                self.assertGreaterEqual(calls, 0)
                if name == "CollidingKey":
                    self.assertGreaterEqual(calls, size)


if __name__ == "__main__":
    unittest.main()
