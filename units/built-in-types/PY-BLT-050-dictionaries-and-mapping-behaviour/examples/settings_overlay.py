"""A small internal configuration API with explicit merge and ownership rules."""

from collections.abc import Mapping
from types import MappingProxyType


def merge_known_settings(
    defaults: Mapping[str, object], overrides: Mapping[str, object]
) -> dict[str, object]:
    """Overlay known names into a new, shallow dictionary.

    Explicit values, including None and falsey values, replace defaults.
    Unknown names raise ValueError. Neither input mapping is written to.
    Nested objects remain shared; this function does not validate a schema,
    deep-merge values, or provide a snapshot across concurrent input changes.
    Callers must provide stable mappings with string keys during the call.
    """
    unknown = [name for name in overrides if name not in defaults]
    if unknown:
        raise ValueError(f"unknown settings: {', '.join(repr(name) for name in unknown)}")
    merged = dict(defaults)
    merged.update(overrides)
    return merged


def main() -> None:
    defaults = {"retries": 3, "enabled": True, "tags": ["base"]}
    result = merge_known_settings(defaults, {"retries": 0, "enabled": False})
    print("resolved:", result)
    print("defaults:", defaults)
    print("new outer dictionary:", result is not defaults)
    print("shared tags:", result["tags"] is defaults["tags"])
    public_view = MappingProxyType(result)
    result["retries"] = 1
    print("read-only view stays live:", public_view["retries"])
    try:
        merge_known_settings(defaults, {"retry": 5})
    except ValueError as exc:
        print("unknown name:", exc)


if __name__ == "__main__":
    main()
