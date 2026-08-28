"""Compare default and eager task start on Python 3.14."""

from __future__ import annotations

import asyncio
import sys


async def probe(label: str, events: list[str]) -> str:
    """Record entry, suspend once, then record resumption."""
    events.append(f"{label}:start")
    await asyncio.sleep(0)
    events.append(f"{label}:resume")
    return label


async def observe_start_modes() -> tuple[str, ...]:
    """Return the ordered events around lazy and eager task construction."""
    if sys.version_info < (3, 14):
        raise RuntimeError("eager_start requires Python 3.14 or newer")

    events: list[str] = []

    lazy = asyncio.create_task(probe("lazy", events), name="lazy")
    events.append(f"after-lazy done={lazy.done()}")

    eager = asyncio.create_task(
        probe("eager", events),
        name="eager",
        eager_start=True,
    )
    events.append(f"after-eager done={eager.done()}")

    await asyncio.sleep(0)
    events.append("main:after-turn")

    await lazy
    await eager
    events.append("main:collected")
    return tuple(events)


def run_experiment() -> tuple[str, ...]:
    """Run the version-specific observation under a fresh event loop."""
    return asyncio.run(observe_start_modes())


def main() -> None:
    """Print one event per line for an auditable trace."""
    for event in run_experiment():
        print(event)


if __name__ == "__main__":
    main()
