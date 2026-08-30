"""Bounded observations, not a timing benchmark or a Python ordering promise."""

import json
import os
import subprocess
import sys


class SpreadKey:
    comparisons = 0

    def __init__(self, value: int) -> None:
        self._value = value

    def __hash__(self) -> int:
        return hash(self._value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SpreadKey) or type(other) is not type(self):
            return NotImplemented
        type(self).comparisons += 1
        return self._value == other._value


class CollidingKey(SpreadKey):
    comparisons = 0

    def __hash__(self) -> int:
        return 0


def lookup_work(key_type: type[SpreadKey], count: int = 64) -> tuple[int, bool, int]:
    """Count equality callbacks for one miss, excluding construction work."""
    members = set()
    for value in range(count):
        members.add(key_type(value))
    key_type.comparisons = 0
    present = key_type(-1) in members
    return len(members), present, key_type.comparisons


CHILD_CODE = """import json
members = set(['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot'])
print(json.dumps({'iteration': list(members), 'sorted': sorted(members)}))
"""


def seeded_order(seed: int) -> dict[str, list[str]]:
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = str(seed)
    completed = subprocess.run(
        [sys.executable, "-B", "-c", CHILD_CODE],
        env=environment,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return json.loads(completed.stdout)


def main() -> None:
    first = seeded_order(1)
    repeated = seeded_order(1)
    second = seeded_order(2)
    print(f"seed 1 iteration: {first['iteration']}")
    print(f"seed 1 repeated matches: {first == repeated}")
    print(f"seed 2 iteration: {second['iteration']}")
    print(f"sorted members match: {first['sorted'] == second['sorted']}")
    print(f"different iteration observed: {first['iteration'] != second['iteration']}")
    for key_type in (SpreadKey, CollidingKey):
        size, present, calls = lookup_work(key_type)
        print(f"{key_type.__name__}: stored={size}, missing_present={present}, eq_calls={calls}")


if __name__ == "__main__":
    main()
