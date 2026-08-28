"""Demonstrate a bounded blocking adapter and its cancellation boundary."""

from __future__ import annotations

import asyncio
import concurrent.futures
import contextvars
import functools
import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar


ResultT = TypeVar("ResultT")
request_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="unbound"
)


@dataclass(frozen=True)
class ThreadObservation:
    """Context and identity observed inside one worker thread."""

    request_id: str
    thread_id: int


@dataclass(frozen=True)
class BlockingBoundaryReport:
    """Owner-visible facts from context propagation and cancellation limits."""

    propagated_request_id: str
    ran_off_loop_thread: bool
    running_call_cancelled: bool
    callable_running_after_cancel_attempt: bool
    callable_finished_after_release: bool


class BlockingAdapter:
    """Own a finite executor and bound admission before submitting calls."""

    def __init__(self, max_concurrency: int) -> None:
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be at least 1")
        self._slots = asyncio.Semaphore(max_concurrency)
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrency,
            thread_name_prefix="blocking-boundary",
        )
        self._closed = False

    async def __aenter__(self) -> BlockingAdapter:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object,
    ) -> None:
        del exc_type, exc, traceback
        self.close()

    def close(self) -> None:
        """Join the owned executor after callers have awaited submitted work."""
        if not self._closed:
            self._closed = True
            self._executor.shutdown(wait=True, cancel_futures=True)

    async def call(
        self, function: Callable[..., ResultT], /, *args: object
    ) -> ResultT:
        """Run a blocking callable without occupying the event-loop thread."""
        if self._closed:
            raise RuntimeError("blocking adapter is closed")

        async with self._slots:
            # run_in_executor() does not copy Context automatically, so this
            # explicit adapter captures one Context per submitted call.
            context = contextvars.copy_context()
            bound_call = functools.partial(function, *args)
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                self._executor, context.run, bound_call
            )


def _inspect_thread_context() -> ThreadObservation:
    return ThreadObservation(request_id.get(), threading.get_ident())


async def observe_blocking_boundary() -> BlockingBoundaryReport:
    """Observe Context propagation and cancellation limits of a running call."""
    loop_thread_id = threading.get_ident()

    async with BlockingAdapter(max_concurrency=1) as adapter:
        token = request_id.set("synthetic-request-080")
        try:
            context_observation = await adapter.call(_inspect_thread_context)
        finally:
            request_id.reset(token)

    loop = asyncio.get_running_loop()
    callable_started = asyncio.Event()
    release_callable = threading.Event()
    callable_finished = threading.Event()

    def gated_blocking_call() -> str:
        loop.call_soon_threadsafe(callable_started.set)
        release_callable.wait()
        callable_finished.set()
        return "finished"

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(gated_blocking_call)
        await callable_started.wait()

        # concurrent.futures documents that a call cannot be cancelled once it
        # is running. This is the underlying lifecycle boundary an async owner
        # must account for when it offloads blocking work.
        running_call_cancelled = future.cancel()
        callable_running_after_cancel_attempt = not callable_finished.is_set()
        release_callable.set()
        # The gate is now open, so the harness can join synchronously without
        # turning this wait into an application pattern.
        future.result(timeout=1.0)

    return BlockingBoundaryReport(
        propagated_request_id=context_observation.request_id,
        ran_off_loop_thread=context_observation.thread_id != loop_thread_id,
        running_call_cancelled=running_call_cancelled,
        callable_running_after_cancel_attempt=(
            callable_running_after_cancel_attempt
        ),
        callable_finished_after_release=callable_finished.is_set(),
    )


def run_demo() -> BlockingBoundaryReport:
    """Run the blocking-boundary demonstration on a fresh event loop."""
    return asyncio.run(observe_blocking_boundary())


def main() -> None:
    """Print the owner-visible boundary facts."""
    report = run_demo()
    print(f"propagated request id: {report.propagated_request_id}")
    print(f"ran off loop thread: {report.ran_off_loop_thread}")
    print(f"running call cancelled: {report.running_call_cancelled}")
    print(
        "callable running after cancel attempt: "
        f"{report.callable_running_after_cancel_attempt}"
    )
    print(
        "callable finished after release: "
        f"{report.callable_finished_after_release}"
    )


if __name__ == "__main__":
    main()
