"""Refresh or verify the explorer's embedded observations using real Python dicts."""

import argparse
import json
import platform
import re
from collections.abc import Iterable, Mapping
from pathlib import Path

HTML = Path(__file__).with_name("dictionary-explorer.html")
DATA_BLOCK = re.compile(
    r'(<script id="dict-trace-data" type="application/json">\n)(.*?)(\n</script>)', re.DOTALL
)


def rows(
    data: Mapping[str, object], references: tuple[tuple[object, str], ...]
) -> list[dict[str, str]]:
    return [
        {
            "key": repr(key),
            "value": repr(value),
            "reference": next((label for obj, label in references if obj is value), ""),
        }
        for key, value in data.items()
    ]


def capture(
    operation: str,
    detail: str,
    data: Mapping[str, object],
    keys: Iterable[str],
    saved: tuple[str, ...],
    companion: Mapping[str, object] | None = None,
    references: tuple[tuple[object, str], ...] = (),
) -> dict[str, object]:
    """Serialize now, so later mutations cannot edit an earlier visual state."""
    return {
        "operation": operation,
        "detail": detail,
        "entries": rows(data, references),
        "live_keys": repr(list(keys)),
        "saved_keys": repr(saved),
        "copy_entries": None if companion is None else rows(companion, references),
    }


def build_traces() -> list[dict[str, object]]:
    data: dict[str, object] = {"queue": 3, "workers": 2}
    keys, saved = data.keys(), tuple(data)
    order = [capture(
        "d = {'queue': 3, 'workers': 2}; keys = d.keys(); saved = tuple(d)",
        "The keys view and the saved tuple initially show the same names.", data, keys, saved
    )]
    data["queue"] = 7
    order.append(capture("d['queue'] = 7", "Replacing a value keeps its key's position.",
                         data, keys, saved))
    data["limit"] = 0
    order.append(capture("d['limit'] = 0", "A new key appears last; the saved tuple is unchanged.",
                         data, keys, saved))
    del data["workers"]
    order.append(capture("del d['workers']", "The live view loses the deleted key.",
                         data, keys, saved))
    data["workers"] = 4
    order.append(capture("d['workers'] = 4", "Reinsertion gives the key a new position at the end.",
                         data, keys, saved))
    removed = data.popitem()
    order.append(capture("d.popitem()", f"Removed the last inserted entry: {removed!r}.",
                         data, keys, saved))

    tags = ["base"]
    replacement = ["replacement"]
    data = {"tags": tags, "timeout": 10}
    copied = data.copy()
    keys, saved = data.keys(), tuple(data)
    references = ((tags, "list A"), (replacement, "list B"))
    ownership = [capture(
        "d = {'tags': ['base'], 'timeout': 10}; copied = d.copy(); "
        "keys = d.keys(); saved = tuple(d)",
        "Two outer dictionaries point to the same list A.", data, keys, saved, copied, references
    )]
    data["region"] = "west"
    ownership.append(capture(
        "d['region'] = 'west'", "A new binding changes d and its live view, not copied.",
        data, keys, saved, copied, references
    ))
    tags.append("canary")
    ownership.append(capture(
        "d['tags'].append('canary')", "Both dictionaries still reach the same edited list A.",
        data, keys, saved, copied, references
    ))
    data["tags"] = replacement
    ownership.append(capture(
        "d['tags'] = ['replacement']", "Only d is rebound to list B; copied still reaches list A.",
        data, keys, saved, copied, references
    ))
    tags.append("copy-edit")
    ownership.append(capture(
        "copied['tags'].append('copy-edit')", "Editing list A now leaves d's list B unchanged.",
        data, keys, saved, copied, references
    ))
    return [
        {"id": "order", "title": "Insertion order", "steps": order},
        {"id": "ownership", "title": "Views and shallow copies", "steps": ownership},
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    text = HTML.read_text(encoding="utf-8")
    match = DATA_BLOCK.search(text)
    if match is None:
        raise SystemExit("Missing dictionary trace data block")
    actual = build_traces()
    if args.refresh:
        payload = json.dumps(actual, ensure_ascii=True, indent=2)
        replacement = match.group(1) + payload + match.group(3)
        HTML.write_text(text[:match.start()] + replacement + text[match.end():], encoding="utf-8")
        print("Refreshed dictionary observations")
    elif json.loads(match.group(2)) != actual:
        raise SystemExit(
            "Embedded observations differ from this Python run; inspect before refreshing"
        )
    else:
        count = sum(len(trace["steps"]) for trace in actual)
        print(f"Verified {count} dictionary states against {platform.python_implementation()} "
              f"{platform.python_version()}")


if __name__ == "__main__":
    main()
