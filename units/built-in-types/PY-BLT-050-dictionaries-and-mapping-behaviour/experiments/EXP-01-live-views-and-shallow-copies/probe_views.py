"""Observe live observations and preserved references without using addresses."""

from types import MappingProxyType


def main() -> None:
    tags = ["base"]
    source = {"tags": tags, "timeout": 10}
    keys_view = source.keys()
    items_view = source.items()
    key_snapshot = tuple(source)
    item_snapshot = tuple(source.items())
    copied = source.copy()
    proxy = MappingProxyType(source)

    source["region"] = "west"
    print("live keys:", list(keys_view))
    print("key snapshot:", key_snapshot)
    tags.append("canary")
    print("snapshot items after child edit:", item_snapshot)
    print("copy after child edit:", copied)
    print("same child:", copied["tags"] is tags)

    source["tags"] = ["replacement"]
    print("live items after rebinding:", list(items_view))
    print("copy after rebinding:", copied)
    print("proxy follows rebinding:", proxy["tags"] is source["tags"])
    try:
        proxy["region"] = "east"
    except TypeError as exc:
        print("proxy assignment:", type(exc).__name__)

    cursor = iter(source)
    print("iterator first:", next(cursor))
    source["added"] = 1
    try:
        print("iterator next:", next(cursor))
    except RuntimeError as exc:
        print("iterator after insertion:", type(exc).__name__)


if __name__ == "__main__":
    main()
