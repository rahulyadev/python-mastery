"""Count Python equality calls, not elapsed time or internal hash-table probes."""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, eq=False)
class ProbeKey:
    label: int
    collide: bool
    comparisons: ClassVar[int] = 0

    def __hash__(self) -> int:
        return 0 if self.collide else self.label

    def __eq__(self, other: object) -> bool:
        ProbeKey.comparisons += 1
        if not isinstance(other, ProbeKey):
            return NotImplemented
        return (self.label, self.collide) == (other.label, other.collide)


def main() -> None:
    for size in (8, 32, 128):
        for collide in (False, True):
            mapping = {ProbeKey(i, collide): i for i in range(size)}
            ProbeKey.comparisons = 0
            missing = ProbeKey(size, collide) in mapping
            miss_calls = ProbeKey.comparisons
            ProbeKey.comparisons = 0
            hit = mapping[ProbeKey(size - 1, collide)]
            hit_calls = ProbeKey.comparisons
            mode = "constant" if collide else "distinct"
            print(
                f"n={size} hashes={mode} len={len(mapping)} "
                f"missing_found={missing} miss_eq={miss_calls} "
                f"hit={hit} hit_eq={hit_calls}"
            )

    mapping = {ProbeKey(10, True): "first", ProbeKey(11, True): "second"}
    mapping[ProbeKey(10, True)] = "replacement"
    print("equal-key replacement:", len(mapping), mapping[ProbeKey(10, True)])
    print("unequal colliding key survives:", mapping[ProbeKey(11, True)])


if __name__ == "__main__":
    main()
