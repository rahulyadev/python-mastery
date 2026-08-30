"""Compare the offline explorer's JavaScript with Python's actual slice behavior.

Node.js is optional for a reader using only the Python materials. It is required
for validating edits to the explorer; skipped checks do not verify that visual.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest


VISUAL = Path(__file__).resolve().parents[1] / "visuals" / "slice-explorer.html"
NODE = shutil.which("node")
RUNNER = """
const fs = require('node:fs');
const vm = require('node:vm');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const context = vm.createContext({});
vm.runInContext(payload.source, context);
const model = vm.runInContext('({normalizeSlice, parseSliceBound})', context);
const results = payload.cases.map(item => {
  try { return {value: model[item.operation](...item.args)}; }
  catch (error) { return {error: error.name}; }
});
process.stdout.write(JSON.stringify(results));
"""


@unittest.skipUnless(NODE, "Node.js is needed to verify the optional slice explorer")
class SliceExplorerTests(unittest.TestCase):
    def run_model(self, cases: list[dict]) -> list[dict]:
        match = re.search(
            r'<script id="slice-model">(.*?)</script>',
            VISUAL.read_text(encoding="utf-8"),
            re.DOTALL,
        )
        self.assertIsNotNone(match, "The standalone visual must contain its tested model")
        assert match is not None
        completed = subprocess.run(
            [NODE, "-e", RUNNER],
            input=json.dumps({"source": match.group(1), "cases": cases}),
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
        return json.loads(completed.stdout)

    def test_normalized_bounds_and_positions_match_9100_python_slices(self) -> None:
        bounds = (None, -100, -12, -7, -1, 0, 1, 6, 12, 100)
        steps = (None, -20, -3, -1, 1, 2, 20)
        cases = [
            {"operation": "normalizeSlice", "args": [length, start, stop, step]}
            for length, start, stop, step in itertools.product(range(13), bounds, bounds, steps)
        ]
        self.assertEqual(len(cases), 9100)
        for case, result in zip(cases, self.run_model(cases), strict=True):
            length, start, stop, step = case["args"]
            selection = slice(start, stop, step)
            with self.subTest(args=case["args"]):
                self.assertEqual(
                    result,
                    {"value": {
                        "bounds": list(selection.indices(length)),
                        "positions": list(range(length))[selection],
                    }},
                )

    def test_input_parser_handles_omission_and_rejects_nonintegers(self) -> None:
        samples = [
            ("", {"value": None}),
            (" None ", {"value": None}),
            ("-0", {"value": 0}),
            (" +12 ", {"value": 12}),
            ("-9007199254740991", {"value": -9007199254740991}),
            ("9007199254740992", {"error": "TypeError"}),
            ("1.5", {"error": "TypeError"}),
            ("1e2", {"error": "TypeError"}),
            ("NaN", {"error": "TypeError"}),
            ("Infinity", {"error": "TypeError"}),
            ("--1", {"error": "TypeError"}),
        ]
        cases = [{"operation": "parseSliceBound", "args": [raw, "Start"]} for raw, _ in samples]
        self.assertEqual(self.run_model(cases), [expected for _, expected in samples])

    def test_model_rejects_zero_step_and_out_of_scope_lengths(self) -> None:
        cases = [
            {"operation": "normalizeSlice", "args": [6, None, None, 0]},
            {"operation": "normalizeSlice", "args": [-1, None, None, 1]},
            {"operation": "normalizeSlice", "args": [13, None, None, 1]},
            {"operation": "normalizeSlice", "args": [2.5, None, None, 1]},
            {"operation": "normalizeSlice", "args": [6, 1.5, None, 1]},
        ]
        self.assertEqual(self.run_model(cases), [{"error": "RangeError"}] * 4 + [
            {"error": "TypeError"},
        ])


if __name__ == "__main__":
    unittest.main()
