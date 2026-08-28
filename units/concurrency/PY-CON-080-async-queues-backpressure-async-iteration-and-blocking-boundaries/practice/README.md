# PY-CON-080 practice — Async queues, backpressure, async iteration, and blocking boundaries

[Unit note](../README.md) · [Curriculum](../../../../CURRICULUM.md#py-con-080) · [Progress](../../../../PROGRESS.md)

## Practice contract

These exercises begin unsolved. Preserve the first attempt, including predictions and mistakes, before requesting a hint or review. Do not replace an attempt with a polished answer.

For each exercise:

1. write the prediction or design before execution;
2. identify the capacity, lifetime, completion, and cancellation owners;
3. use synthetic data only;
4. run the narrowest deterministic command that can test the claim;
5. record actual output rather than an expected paraphrase;
6. explain the first incorrect reasoning step when a prediction fails.

Ask for hints one at a time. A hint should expose only the next missing reasoning step, not a full implementation.

## Prerequisite assumptions

The tracker does not record learning evidence for the three hard prerequisites. Use these minimum assumptions without treating them as prerequisite completion:

- `PY-CON-060`: an event loop advances ready Tasks cooperatively; any synchronous blocking call on the loop thread prevents other Tasks from advancing;
- `PY-CON-070`: a `TaskGroup` owns child lifetimes and cancellation is a cooperative stop request, not a synchronous kill;
- `PY-FIT-090`: a lazy producer computes values on demand, but any internal prefetch or buffer has its own capacity and lifetime.

## Evidence map

| Exercise | Type | Primary evidence | Required before review |
|---|---|---|---|
| `PY-CON-080-P01` | Predict | Queue state and accounting explanation | Event trace plus `B`, `A`, and `U` after each marked event |
| `PY-CON-080-P02` | Implement | Bounded pipeline code | Tests for pressure, order, failure, and graceful shutdown |
| `PY-CON-080-P03` | Debug | Completion-accounting diagnosis | Minimal reproduction and corrected invariant in words |
| `PY-CON-080-P04` | Implement | Async-iterator protocol | Protocol tests including terminal behavior |
| `PY-CON-080-P05` | Debug | Async-generator cleanup | Early-exit trace before and after repair |
| `PY-CON-080-P06` | Implement | Blocking-boundary adapter | Capacity, context, cancellation, and shutdown tests |
| `PY-CON-080-P07` | Review | Senior code review | Prioritized findings with concrete failure scenarios |
| `PY-CON-080-P08` | Design | Production transfer | Capacity budget, overload policy, shutdown sequence, and observability |

`B` means buffered queue items, `A` means actively processing items, and `U` means the queue's unfinished-work count.

## PY-CON-080-P01 — Predict the three queue counters

Difficulty: 3/5

Do not run this until the prediction is written.

```python
import asyncio


async def main() -> None:
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=1)
    release = asyncio.Event()

    async def worker() -> None:
        item = await queue.get()
        print("worker got", item)          # Event C
        try:
            await release.wait()
            print("worker finished", item) # Event E
        finally:
            queue.task_done()              # Event F

    await queue.put("alpha")
    print("alpha admitted")                # Event A
    task = asyncio.create_task(worker())
    await asyncio.sleep(0)
    await queue.put("beta")
    print("beta admitted")                 # Event D
    release.set()
    await queue.join()
    print("joined")                        # Event G
    await task


asyncio.run(main())
```

Before execution:

1. predict the complete output order;
2. record `(B, A, U)` immediately after Events A, C, D, E, F, and G;
3. explain why the second `put()` succeeds even though the first item is not finished;
4. explain why `queue.empty()` could be true while `queue.join()` is still waiting;
5. predict which event disappears if `task_done()` is removed.

Evidence to preserve:

```text
Prediction:
Counter table:
Observed output:
First mismatch:
Corrected invariant:
```

## PY-CON-080-P02 — Implement a bounded ordered pipeline

Difficulty: 4/5

Implement this Python 3.13+ API without copying the initialized example:

```python
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


async def ordered_map(
    items: Iterable[InputT],
    transform: Callable[[InputT], Awaitable[OutputT]],
    *,
    queue_capacity: int,
    workers: int,
) -> list[OutputT]:
    raise NotImplementedError
```

Requirements:

- reject non-positive capacities and worker counts;
- bound buffered items independently from active worker count;
- preserve input order without forcing completion order;
- pair every successful `get()` with exactly one `task_done()`, including failure and cancellation paths;
- use `TaskGroup` to own worker lifetimes;
- use graceful `Queue.shutdown()` rather than a forever-loop leak;
- do not poll `qsize()` or sleep to coordinate correctness;
- propagate transform failures without hanging `join()` or losing the traceback.

Write deterministic tests for:

1. a producer suspended by a full queue;
2. out-of-order worker completion with input-ordered results;
3. one transform failure while other workers are active;
4. cancellation during a transform;
5. an empty input;
6. graceful shutdown after every accepted item is accounted for.

Then sketch, but do not necessarily implement, the Python 3.11 sentinel variant. State how many sentinels are required, who enqueues them, and how they participate in unfinished-work accounting.

## PY-CON-080-P03 — Debug the join that never returns

Difficulty: 3/5

```python
async def worker(queue: asyncio.Queue[str]) -> None:
    while True:
        item = await queue.get()
        if item.startswith("invalid"):
            raise ValueError(item)
        await persist(item)
        queue.task_done()
```

The owner sometimes waits forever in `queue.join()` after a validation failure or cancellation.

Before editing:

1. identify the exact counter transition that is lost;
2. explain why moving `task_done()` immediately after `get()` would make `join()` lie;
3. identify which exception path a broad `except Exception` would still not cover;
4. state whether retrying the item should occur before or after `task_done()` and why;
5. design a deterministic failing test without wall-clock sleeps.

Preserve the broken reproduction and its observed trace. Request a review only after the invariant is stated in one sentence.

## PY-CON-080-P04 — Implement an asynchronous page iterator

Difficulty: 3/5

Create a class whose `__aiter__()` returns an asynchronous iterator and whose `__anext__()` retrieves one synthetic page at a time from an injected awaitable loader.

Contract:

- no network access;
- `__aiter__()` returns the iterator directly, not an awaitable;
- empty-page termination raises `StopAsyncIteration`;
- loader failures propagate unchanged;
- a second `async for` over the same iterator has explicitly documented single-use behavior;
- the class does not prefetch unless a finite prefetch capacity is part of the API.

Tests must manually call `aiter()` and `anext()` at least once so the protocol is visible, then test ordinary `async for` consumption.

Explain whether this iterator supplies backpressure. Your answer must name any buffer between the external source and `__anext__()`; “it is lazy” is not sufficient.

## PY-CON-080-P05 — Repair early async-generator cleanup

Difficulty: 3/5

Start with a synthetic async generator that records `open`, `yield`, and `close` events and has awaited cleanup in `finally`. Consume one value and break.

Tasks:

1. record when cleanup occurs without an explicit close boundary;
2. wrap the generator in `contextlib.aclosing()`;
3. prove that `close` occurs before the owner continues beyond the context;
4. repeat with an exception in the loop body;
5. state why relying on event-loop shutdown or garbage collection is the wrong ownership model;
6. state what changes if the async iterable is a custom iterator with no `aclose()` method.

Do not turn the result into a universal timing claim about garbage collection. Classify only the explicit `aclosing()` behavior as the designed guarantee.

## PY-CON-080-P06 — Build a bounded blocking adapter

Difficulty: 5/5

Design an adapter for a legacy blocking client.

Required decisions:

- `asyncio.to_thread()` versus a specifically owned executor;
- admission capacity before submission, not merely executor worker count;
- `contextvars` propagation;
- native timeout passed into the blocking library;
- behavior when the awaiting Task is cancelled after the callable has started;
- cooperative stop support when the library offers it;
- executor shutdown ownership;
- retry and idempotency policy for an outcome that completes after its caller has stopped waiting.

Tests must establish, without sleeping for guessed durations:

1. no more than the configured number of calls enter the blocking function;
2. excess callers wait before submission;
3. request context is visible in the worker thread;
4. a running executor call cannot be cancelled through `Future.cancel()`;
5. all owned threads terminate after adapter shutdown.

Do not claim that cancellation kills an OS thread. If the legacy library cannot stop a running call, say exactly how its lifetime is bounded.

## PY-CON-080-P07 — Review an overload-prone service

Difficulty: 4/5

Review this sketch without running it:

```python
async def ingest(records, client) -> None:
    queue = asyncio.Queue()

    async def worker() -> None:
        while True:
            record = await queue.get()
            time.sleep(0.05)
            await client.send(record)
            queue.task_done()

    for _ in range(100):
        asyncio.create_task(worker())

    async for record in records:
        asyncio.create_task(queue.put(record))

    while queue.qsize():
        await asyncio.sleep(0.1)
```

Produce prioritized findings. For each finding include:

- the violated invariant;
- a concrete load, failure, cancellation, or shutdown scenario;
- the smallest safe design change;
- a deterministic test or observable metric.

Your review should cover at least:

- unbounded queue storage;
- unbounded pending `put()` Tasks;
- unowned worker lifetimes and failures;
- loop-thread blocking;
- missing `task_done()` protection;
- false completion based on `qsize()`;
- missing downstream flow control and deadline;
- undefined shutdown and rejected-work policy.

Do not submit a full rewrite before the findings are reviewed.

## PY-CON-080-P08 — Design a production ingestion boundary

Difficulty: 5/5

Design a service that accepts synthetic events, performs blocking enrichment through a legacy client, and writes batches to an async stream.

Your design must state:

1. maximum ingress queue size and the reason for that unit;
2. maximum active enrichments and maximum submitted-but-not-started blocking calls;
3. batch size and maximum batch residence time;
4. whether overload waits, rejects, sheds, coalesces, or persists work;
5. one absolute deadline's propagation across admission, enrichment, and write drain;
6. graceful-shutdown order and an emergency-abort order;
7. retry ownership and idempotency boundary;
8. metrics for queue occupancy, admission wait, active workers, oldest-item age, executor saturation, processing latency, rejections, and shutdown drain time;
9. what a successful `join()` proves and what it does not prove;
10. how Python 3.11 and Python 3.14 implementations differ.

Include one failure-injection plan for each of:

- producer cancellation while waiting to put;
- worker failure after `get()` but before completion;
- async-generator consumer break;
- blocking call finishing after its awaiter is cancelled;
- slow stream receiver keeping `drain()` blocked;
- shutdown with buffered and active work.

## Review rubric

| Dimension | Incomplete | Review-ready |
|---|---|---|
| Capacity | Names a queue size only | Bounds buffered, active, submitted, downstream, and retry state |
| Completion | Uses `empty()` or `qsize()` | Accounts for every accepted item and defines terminal success |
| Lifetimes | Leaves background Tasks or threads implicit | Assigns every Task, iterator, executor, and shutdown phase an owner |
| Cancellation | Treats cancellation as a kill | Separates async wait cancellation from underlying work termination |
| Async iteration | Uses syntax without protocol reasoning | Explains demand, termination, buffering, and deterministic close |
| Compatibility | Assumes latest runtime | Gives an honest Python 3.11 alternative for queue shutdown |
| Testing | Sleeps and hopes | Uses Events, gates, injected failures, and asserted state transitions |
| Production transfer | Says “add backpressure” | Defines overload policy, deadlines, metrics, and shutdown invariants |

## Evidence record

Copy this block after each attempted exercise:

```text
Exercise ID:
Date and runtime:
First prediction or design:
Command actually run:
Observed output:
Tests passed and failed:
First missing reasoning step:
Correction made:
Remaining weakness:
Reviewer evidence link:
```

Completing the generated prompts is not evidence by itself. Preserve the learner's attempt, actual test output, and reviewed reasoning before proposing a progress-state change.
