"""Observe slice normalization, compact ranges, and length limits; no benchmark."""

from __future__ import annotations

import sys


def main() -> None:
    values = list("ABCDEF")
    selections = [
        ("[::-1]", slice(None, None, -1)),
        ("[:-1:-1]", slice(None, -1, -1)),
        ("[50:-50:-2]", slice(50, -50, -2)),
        ("[1:5:2]", slice(1, 5, 2)),
        ("[1:1]", slice(1, 1)),
    ]
    for label, selection in selections:
        normalized = selection.indices(len(values))
        print(f"{label}: bounds={normalized}; positions={list(range(*normalized))}; "
              f"values={values[selection]}")

    normalized_reverse = slice(None, None, -1).indices(len(values))
    print(f"normalized bounds reused as a raw slice: {values[slice(*normalized_reverse)]}")
    try:
        values[::0]
    except ValueError as error:
        print(f"zero slice step: {type(error).__name__}")

    progression = range(3, 24, 4)
    selected = progression[1::2]
    print(f"range slice: {selected}; values={list(selected)}")
    print(f"equal sequences, different stops: {range(0, 4, 2) == range(0, 3, 2)}")
    first = iter(progression)
    second = iter(progression)
    print(f"two fresh iterators: {next(first)}, {next(first)}; {next(second)}")

    huge = range(0, 10**40, 3)
    print(f"huge range first three: {list(huge[:3])}")
    print(f"huge range integer membership: {3 * 10**30 in huge}")
    try:
        print(f"huge range length: {len(huge)}")
    except OverflowError as error:
        print(f"huge range length: {type(error).__name__}")
    print(f"shallow range sizes in bytes: small={sys.getsizeof(range(10))}; "
          f"large={sys.getsizeof(range(10**12))}")


if __name__ == "__main__":
    main()
