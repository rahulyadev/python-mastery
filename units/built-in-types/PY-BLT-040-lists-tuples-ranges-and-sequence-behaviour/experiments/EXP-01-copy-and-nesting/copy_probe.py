"""Observe sharing and partial mutation without using addresses or timings."""

from __future__ import annotations

from copy import deepcopy


def main() -> None:
    child = ["queued"]
    source = [child, child]
    shallow = source.copy()
    frozen = tuple(source)
    deep = deepcopy(source)

    print(f"shallow outer is source: {shallow is source}")
    print(f"shallow child is source child: {shallow[0] is source[0]}")
    print(f"tuple child is source child: {frozen[0] is source[0]}")
    print(f"deep child is source child: {deep[0] is source[0]}")
    print(f"deep children share with each other: {deep[0] is deep[1]}")

    child.append("sent")
    print(f"source after child mutation: {source}")
    print(f"shallow after child mutation: {shallow}")
    print(f"tuple after child mutation: {frozen}")
    print(f"deep after child mutation: {deep}")

    shallow[0] = ["local"]
    print(f"source after shallow slot replacement: {source}")
    print(f"shallow after slot replacement: {shallow}")

    repeated = [[0]] * 2
    repeated[0].append(1)
    print(f"repeated children share: {repeated[0] is repeated[1]}")
    print(f"repeated after mutation: {repeated}")

    boxed: tuple[list[int]] = ([],)
    try:
        boxed[0] += [7]  # Intentional: mutation succeeds before tuple assignment fails.
    except TypeError as error:
        print(f"tuple augmented assignment: {type(error).__name__}")
    print(f"tuple child after failed assignment: {boxed[0]}")


if __name__ == "__main__":
    main()
