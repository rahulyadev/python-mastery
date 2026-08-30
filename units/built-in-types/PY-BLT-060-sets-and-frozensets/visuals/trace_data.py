"""Compute the explorer's finite replay states in Python, not JavaScript."""

import json


def build_traces() -> list[dict[str, object]]:
    scenarios = [
        ("overlap", "Partial overlap", ["api", "cache", "worker"], ["cache", "cron"]),
        ("subset", "A is a proper subset", ["cache"], ["api", "cache"]),
        ("disjoint", "Disjoint sets", ["api"], ["cron"]),
        ("empty", "A is empty", [], ["cache"]),
        ("equal", "Equal members", ["api", "cache"], ["cache", "api"]),
    ]
    traces = []
    for key, label, left, right in scenarios:
        a, b = set(left), set(right)
        traces.append(
            {
                "id": key,
                "label": label,
                "a": sorted(a),
                "b": sorted(b),
                "left_only": sorted(a - b),
                "both": sorted(a & b),
                "right_only": sorted(b - a),
                "subset": a <= b,
                "proper_subset": a < b,
                "disjoint": a.isdisjoint(b),
                "results": {
                    "union": sorted(a | b),
                    "intersection": sorted(a & b),
                    "difference": sorted(a - b),
                    "reverse_difference": sorted(b - a),
                    "symmetric_difference": sorted(a ^ b),
                },
            }
        )
    return traces


if __name__ == "__main__":
    print(json.dumps(build_traces(), indent=2, ensure_ascii=False))
