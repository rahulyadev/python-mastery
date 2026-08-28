"""Deterministic checks for the initialized PY-CON-080 artifacts."""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))

import async_stream  # noqa: E402
import blocking_boundary  # noqa: E402
import bounded_pipeline  # noqa: E402


class BoundedPipelineTests(unittest.TestCase):
    def test_full_queue_propagates_pressure_to_producer(self) -> None:
        report = bounded_pipeline.run_demo()

        self.assertTrue(report.third_put_blocked)
        self.assertEqual(report.processed, ("alpha", "beta", "gamma"))
        self.assertTrue(report.queue_empty)
        self.assertLess(
            report.events.index("producer:attempt:gamma"),
            report.events.index("owner:released-alpha"),
        )
        self.assertLess(
            report.events.index("owner:released-alpha"),
            report.events.index("producer:accepted:gamma"),
        )
        self.assertLess(
            report.events.index("worker:done:gamma"),
            report.events.index("owner:joined"),
        )
        self.assertEqual(report.events[-1], "worker:queue-shutdown")

    def test_map_bounded_preserves_input_order(self) -> None:
        beta_completed = asyncio.Event()

        async def scenario() -> list[str]:
            async def transform(value: str) -> str:
                if value == "alpha":
                    await beta_completed.wait()
                else:
                    beta_completed.set()
                return value.upper()

            return await bounded_pipeline.map_bounded(
                ("alpha", "beta"),
                transform,
                maxsize=1,
                worker_count=2,
            )

        self.assertEqual(asyncio.run(scenario()), ["ALPHA", "BETA"])

    def test_graceful_shutdown_drains_and_preserves_join_accounting(
        self,
    ) -> None:
        async def scenario() -> None:
            queue: asyncio.Queue[str] = asyncio.Queue(maxsize=1)
            await queue.put("alpha")
            queue.shutdown()

            with self.assertRaises(asyncio.QueueShutDown):
                await queue.put("beta")

            self.assertEqual(await queue.get(), "alpha")
            queue.task_done()
            await queue.join()

            with self.assertRaises(asyncio.QueueShutDown):
                await queue.get()

        asyncio.run(scenario())

    def test_map_bounded_rejects_unbounded_configuration(self) -> None:
        async def transform(value: str) -> str:
            return value

        with self.assertRaisesRegex(ValueError, "maxsize"):
            asyncio.run(
                bounded_pipeline.map_bounded(
                    ("alpha",),
                    transform,
                    maxsize=0,
                    worker_count=1,
                )
            )


class AsyncIterationTests(unittest.TestCase):
    def test_explicit_iterator_uses_stop_async_iteration(self) -> None:
        async def collect() -> list[int]:
            return [value async for value in async_stream.AsyncCountdown(3)]

        self.assertEqual(asyncio.run(collect()), [3, 2, 1])

    def test_aclosing_finishes_generator_cleanup_before_owner_continues(
        self,
    ) -> None:
        report = async_stream.run_demo()

        self.assertEqual(report.accepted, ("alpha", "beta"))
        self.assertNotIn("stream:yield:gamma", report.events)
        self.assertLess(
            report.events.index("owner:leaving-context"),
            report.events.index("stream:close"),
        )
        self.assertLess(
            report.events.index("stream:close"),
            report.events.index("owner:after-context"),
        )


class BlockingBoundaryTests(unittest.TestCase):
    def test_adapter_propagates_context_and_running_call_cannot_cancel(
        self,
    ) -> None:
        report = blocking_boundary.run_demo()

        self.assertEqual(
            report.propagated_request_id, "synthetic-request-080"
        )
        self.assertTrue(report.ran_off_loop_thread)
        self.assertFalse(report.running_call_cancelled)
        self.assertTrue(report.callable_running_after_cancel_attempt)
        self.assertTrue(report.callable_finished_after_release)

    def test_adapter_requires_a_positive_capacity(self) -> None:
        with self.assertRaisesRegex(ValueError, "max_concurrency"):
            blocking_boundary.BlockingAdapter(0)


if __name__ == "__main__":
    unittest.main()
