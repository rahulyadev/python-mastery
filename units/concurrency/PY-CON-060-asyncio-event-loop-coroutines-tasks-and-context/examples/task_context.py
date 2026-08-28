"""Demonstrate ContextVar snapshots and task-local binding changes."""

from __future__ import annotations

import asyncio
from contextvars import ContextVar
from dataclasses import dataclass


request_id: ContextVar[str] = ContextVar("request_id", default="unset")


@dataclass(frozen=True)
class ContextObservation:
    """Context values seen within one child task."""

    task_name: str
    inherited: str
    local_after_await: str


@dataclass(frozen=True)
class ContextReport:
    """Two task snapshots plus the unchanged parent binding."""

    observations: tuple[ContextObservation, ...]
    parent_after_children: str


async def observe_child(task_name: str) -> ContextObservation:
    """Change one task's binding and verify it survives a suspension."""
    inherited = request_id.get()
    token = request_id.set(f"{inherited}/{task_name}")
    try:
        await asyncio.sleep(0)
        local_after_await = request_id.get()
    finally:
        request_id.reset(token)

    return ContextObservation(task_name, inherited, local_after_await)


async def observe_contexts() -> ContextReport:
    """Create children under different parent bindings and collect them."""
    initial_token = request_id.set("request-a")
    try:
        first = asyncio.create_task(observe_child("child-a"), name="child-a")

        updated_token = request_id.set("request-b")
        try:
            second = asyncio.create_task(observe_child("child-b"), name="child-b")
            observations = await asyncio.gather(first, second)
            parent_after_children = request_id.get()
        finally:
            request_id.reset(updated_token)
    finally:
        request_id.reset(initial_token)

    return ContextReport(tuple(observations), parent_after_children)


def run_demo() -> ContextReport:
    """Run the context observation under a fresh event loop."""
    return asyncio.run(observe_contexts())


def main() -> None:
    """Print task snapshots and the parent value."""
    report = run_demo()
    for observation in report.observations:
        print(
            f"{observation.task_name}: inherited={observation.inherited!r} "
            f"local_after_await={observation.local_after_await!r}"
        )
    print(f"parent after children: {report.parent_after_children!r}")


if __name__ == "__main__":
    main()
