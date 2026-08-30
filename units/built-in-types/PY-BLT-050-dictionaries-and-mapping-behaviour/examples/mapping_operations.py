"""Small mapping demonstrations, separate from the unsolved practice tasks."""

from collections import defaultdict


class MissingLabel(dict[str, str]):
    """Compute a fallback without storing it; get() does not call this hook."""

    def __missing__(self, key: object) -> str:
        return f"unknown:{key}"


def describe_lookup(data: dict[str, object], key: str) -> str:
    """Distinguish absence from every stored value, including None and zero."""
    missing = object()
    value = data.get(key, missing)
    if value is missing:
        return "missing"
    return f"present: {value!r}"


def eager_defaults() -> tuple[int, int, list[str]]:
    """Observe argument evaluation even when the dictionary already has a key."""
    calls: list[str] = []

    def make_default() -> int:
        calls.append("built")
        return 99

    limits = {"quota": 0}
    first = limits.get("quota", make_default())
    second = limits.setdefault("quota", make_default())
    return first, second, calls


def main() -> None:
    pairs = [("blue", 1), ("green", 2), ("blue", 3)]
    data = dict(pairs)
    print("constructed:", list(data.items()))
    data["blue"] = 4
    print("overwritten:", list(data.items()))
    del data["blue"]
    data["blue"] = 5
    print("reinserted:", list(data.items()))
    print("last inserted:", data.popitem())

    numeric = {1: "integer", True: "boolean", 1.0: "float"}
    print("equal numeric keys:", len(numeric), numeric[True])
    payload: dict[str, object] = {"quota": 0, "label": None}
    print("lookup states:", *(describe_lookup(payload, key) for key in ("quota", "label", "x")))
    print("eager defaults:", eager_defaults())

    labels = MissingLabel()
    print("missing hook:", labels["west"], labels.get("west"), "west" in labels)
    buckets: defaultdict[str, list[str]] = defaultdict(list)
    print("defaultdict get:", buckets.get("west"), list(buckets))
    buckets["west"].append("event")
    print("defaultdict subscription:", dict(buckets))

    left = {"workers": 2, "options": {"connect": 3, "read": 10}}
    right = {"options": {"connect": 1}, "enabled": False}
    result = left | right
    print("union:", result)
    print("union shares right value:", result["options"] is right["options"])
    original = result
    result |= [("workers", 4)]
    print("in-place union:", result is original, result["workers"])


if __name__ == "__main__":
    main()
