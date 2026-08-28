# PY-CON-080 — Async queues, backpressure, async iteration, and blocking boundaries

[Curriculum entry](../../../CURRICULUM.md#py-con-080) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-CON-080`

## Physical Notebook Core

### Problem this concept solves

An async service can remain responsive yet still fail under load if producers admit work faster than consumers finish it. Unbounded buffers, unbounded pending Tasks, forgotten queue accounting, abandoned async generators, and blocking calls on the event-loop thread turn a temporary slowdown into memory growth, latency collapse, false completion, or unsafe shutdown.

### One-sentence mental model

> Treat an async pipeline as a chain of finite valves: every boundary has a capacity and an owner, and awaiting that boundary carries downstream pressure back toward the producer without confusing admission, active processing, or completion.

### One important visual

```text
producer
   |
   | await put(item)          full => producer waits
   v
+-------------------+     get()      +------------------+
| Queue(maxsize=N)  | -------------> | W worker slots   |
| B buffered items  |                | A active items   |
+-------------------+                +------------------+
          |                                   |
          | U unfinished items                +-- async sink:
          | (put +1, task_done -1)            |   write + await drain
          |                                   |
          +--- await join() <-----------------+
                                              |
                                              +-- blocking sink:
                                                  await finite adapter slot
                                                  -> owned executor thread

graceful stop: reject new puts -> drain B -> finish A -> U reaches 0 -> workers exit
```

#### How to read this visual

Follow one item from top to right. `put()` admits it into the queue and increases unfinished work. `get()` moves it from buffered state `B` to active state `A`; that frees a queue slot but does not mark the item complete. Only the worker's `task_done()` reduces `U`. Read the bottom branches as two additional pressure boundaries: network writes need flow control, while blocking calls need a finite admission gate before executor submission.

#### Key insight

Queue capacity bounds buffered items, not all in-flight work. Correct overload control requires separate bounds for buffered work, active workers, submitted blocking calls, downstream buffers, retries, and deadlines.

#### Simplification or limitation

The visual shows one process, one event loop, homogeneous items, and graceful shutdown. It omits per-item memory variation, priority, multiple pipeline stages, retries, durable brokers, process pools, distributed flow control, simultaneous failure and cancellation, and emergency data loss. `B`, `A`, and `U` are conceptual state dimensions, not all public queue attributes.

### Governing rules or invariants

1. Every admission path must have a finite capacity, a wait/reject/drop policy, and a caller-visible outcome; creating unbounded Tasks that each await a bounded queue is still unbounded admission.
2. One successful `queue.get()` owns exactly one later `queue.task_done()`, normally in `finally`; `task_done()` means processing is complete, not merely retrieved.
3. `queue.join()` tracks unfinished-work accounting. `queue.empty()` and `qsize()` describe buffered state only and cannot prove that active processing has finished.
4. `Queue(maxsize=N)` bounds `B`; worker count or a semaphore bounds `A`. A `get()` frees queue capacity before the item finishes.
5. `asyncio.Queue` and asyncio synchronization primitives coordinate Tasks in an event loop; they are not thread-safe OS-thread primitives.
6. Graceful queue shutdown rejects new puts, drains accepted items, preserves `join()` accounting, and lets consumers observe terminal shutdown. Immediate shutdown is an abort mode that can invalidate the usual “joined means processed” inference.
7. An asynchronous iterator's `__aiter__()` returns an async iterator; each `__anext__()` returns an awaitable and signals normal exhaustion with `StopAsyncIteration`.
8. Early exit from an async generator with resources needs an explicit owner-driven `aclose()` boundary, commonly `contextlib.aclosing()`.
9. A synchronous blocking call must not run on the event-loop thread. Offload it through a bounded, owned adapter and assume that cancelling the async wait does not preempt an already-running OS-thread call.
10. Backpressure is end-to-end only when every stage honors it: producer admission, queue, worker concurrency, blocking executor, retry buffer, and transport `drain()`.

### Minimal example

Python 3.13+:

```python
import asyncio


async def handle(item: str) -> None:
    await asyncio.sleep(0)
    print(item.upper())


async def worker(queue: asyncio.Queue[str]) -> None:
    while True:
        try:
            item = await queue.get()
        except asyncio.QueueShutDown:
            return

        try:
            await handle(item)
        finally:
            queue.task_done()


async def main() -> None:
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=2)

    async with asyncio.TaskGroup() as group:
        for index in range(2):
            group.create_task(worker(queue), name=f"worker-{index}")

        for item in ("alpha", "beta", "gamma"):
            await queue.put(item)

        queue.shutdown()
        await queue.join()


asyncio.run(main())
```

Expected reasoning:

1. Each producer `await queue.put(item)` is an admission boundary; when two buffered slots are occupied, the producer cannot outrun consumer retrieval indefinitely.
2. `get()` frees one buffer slot, so buffering and active processing have separate capacities.
3. The `finally` block balances unfinished-work accounting even if `handle()` raises or the worker is cancelled while processing.
4. `shutdown()` prevents later puts but permits already accepted items to drain.
5. After the queue is empty, each worker's next `get()` raises `QueueShutDown`, so the `TaskGroup` can close without leaked forever-loop Tasks.
6. `join()` returns only after one `task_done()` has balanced every accepted item; it does not itself prove an external side effect was durable.

### One failure or misconception

**Mistake:** “The queue has `maxsize=100`, so this service can have at most 100 requests in flight.”

**Correction:** `maxsize` bounds only items currently buffered. Items already removed by workers are active, blocked executor submissions may exist elsewhere, retry state may hold references, and downstream transports may buffer bytes. Bound and observe each state separately.

### Important trade-offs

- A small queue propagates pressure quickly and limits memory, but absorbs less burst and may increase admission waits or rejections.
- A large queue smooths short bursts, but increases worst-case residence time, stale work, shutdown drain time, and memory exposure.
- More workers can improve I/O overlap, but can overload databases, connection pools, rate limits, thread pools, or downstream services.
- Graceful drain preserves accepted work, but shutdown can take as long as the slowest active call unless deadlines and abort policy are explicit.
- Async generators express pull-based streaming clearly, but resource cleanup on partial consumption needs explicit ownership.
- Thread offload protects loop responsiveness for suitable blocking I/O, but introduces a second scheduler, finite threads, context propagation, and work that cannot be preempted safely.

### Interview-revision cues

- Reconstruct: `put +1 U` → buffered `B` → `get` moves to active `A` → processing → `task_done -1 U` → `join` at zero.
- Distinguish: admission, retrieval, completion, drain, shutdown, cancellation, and durability.
- Predict: full bounded queue, missing `task_done()`, immediate shutdown, early generator break, and cancellation during a running thread call.
- Diagnose: unbounded `create_task(queue.put(...))`, `qsize()` polling, direct blocking calls, missing `drain()`, and abandoned iterators.
- Design: name every capacity, overload outcome, lifetime owner, deadline, metric, and graceful-versus-abort transition.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Concurrency, parallelism, and asynchronous Python |
| Canonical ID | `PY-CON-080` |
| Learning outcome | Design async queues, synchronisation, backpressure, async iterators/generators, and blocking-work boundaries. |
| Hard prerequisites | `PY-CON-060`, `PY-CON-070`, `PY-FIT-090` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D3 |
| Scope | Standard library |
| Size | L |
| Evidence profile | E+C+D+R |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4, regular GIL-enabled build, Linux x86_64 |
| Last source audit | 2026-08-28 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. model an async pipeline with separate buffered, active, unfinished, submitted, retry, and downstream states;
2. choose finite queue and concurrency capacities from workload and dependency constraints rather than treating defaults as safe;
3. implement producers and consumers with balanced `put()`/`get()`/`task_done()`/`join()` accounting and deterministic failure tests;
4. design graceful and emergency queue shutdown on Python 3.14 and explain a Python 3.11 sentinel alternative;
5. select `Lock`, `Event`, `Condition`, `Semaphore`, `BoundedSemaphore`, or `Barrier` by the state transition being coordinated;
6. implement the asynchronous iteration protocol and reason about demand, hidden prefetch, exhaustion, error propagation, and single-use state;
7. use async generators with deterministic early cleanup and explain what `aclosing()` owns;
8. isolate blocking libraries behind a finite executor boundary, propagate context deliberately, and state cancellation limitations;
9. review a backend flow for overload behavior, deadlines, flow control, retry multiplication, observability, and shutdown safety.

Required evidence:

- reconstruct the finite-valves visual and explain `B`, `A`, and `U` without reading;
- complete the queue prediction, bounded implementation, accounting debug, async-iteration, cleanup, and blocking-boundary practice while preserving first attempts;
- run deterministic tests covering full-queue suspension, failure after `get()`, graceful shutdown, early iteration exit, and a running executor call's cancellation limit;
- review or design one realistic async service boundary with explicit capacities, overload outcomes, deadlines, metrics, and shutdown order.

Initialization created source-audited material, three runnable examples, eight deterministic tests, and protected unsolved practice. It did not create learner attempts, recall, debugging, or production-transfer evidence. The learning state therefore remains `Not started` and the artifact remains `Draft`.

## 2. Prerequisite bridge

The tracker records `PY-CON-060` and `PY-CON-070` as Draft artifacts with learning state `Not started`; `PY-FIT-090` has no artifact. These bridges permit accurate study without pretending any prerequisite is complete.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-CON-060` — Asyncio event loop, coroutines, tasks, and context | Queue waits, synchronization, async iteration, and executor Futures depend on cooperative Task advancement and event-loop ownership. | One loop thread advances one ready Task at a time until it suspends. `await` permits other ready work to run; a synchronous blocking call on that thread prevents the loop from advancing other Tasks. Every created Task has a terminal value, exception, or cancellation that an owner must observe. |
| Hard | `PY-CON-070` — Structured concurrency, cancellation, and timeouts | Producers and workers need bounded lifetimes, cancellation-safe accounting, and one shutdown owner. | `TaskGroup` owns child Tasks through terminal states. Cancellation requests cooperative unwinding and cleanup; it is not a kill. Put accounting changes in `finally`, and preserve `CancelledError` after cleanup. Carry one remaining deadline rather than refreshing a timeout at every stage. |
| Hard | `PY-FIT-090` — Lazy pipelines and streaming transformations | Async iteration is a demand-driven pipeline, but laziness alone does not bound hidden buffers or external sources. | An iterator produces the next value only when asked. A transformation may preserve laziness, introduce lookahead, or materialize data. Identify the owner and capacity of every prefetch, batch, cache, or retry buffer. |

Recommended follow-up: study each prerequisite in its dedicated topic chat. Continue here by treating these bridges as declared assumptions, not evidence of completion.

## 3. Vocabulary and professional English

### Backpressure

| Item | Content |
|---|---|
| Pronunciation | BAK-presh-er |
| Simple English meaning | Resistance sent backward when the next stage cannot accept more work safely. |
| Hindi cue | आगे की क्षमता कम होने पर पीछे काम धीमा करने का संकेत |
| Meaning in this Python context | An awaited finite boundary suspends or rejects a producer when downstream capacity is exhausted. |

Natural examples:

1. The bounded queue propagates backpressure to the parser.
2. Backpressure begins only when the producer awaits the admission call.
3. A second unbounded Task list can defeat queue backpressure.
4. **Interview:** `maxsize` creates a buffer boundary, but end-to-end backpressure also requires bounded workers and downstream flow control.
5. **Engineering discussion:** Record admission wait and oldest-item age so backpressure is visible before the queue remains full.

### Admission

| Item | Content |
|---|---|
| Pronunciation | ad-MISH-un |
| Simple English meaning | The decision and act of accepting new work into a system. |
| Hindi cue | नए काम को स्वीकार करने की सीमा और निर्णय |
| Meaning in this Python context | Successful `put()` means the queue accepted an item; it does not mean processing or persistence completed. |

Natural examples:

1. Admission waits when the buffer has no free slot.
2. The API rejects admission after its deadline expires.
3. Admission control should happen before allocating a large request body when possible.
4. **Interview:** A semaphore can bound active admission to a dependency without storing the work itself.
5. **Engineering discussion:** Define whether overload admission waits, rejects, sheds, coalesces, or persists the item durably.

### Drain

| Item | Content |
|---|---|
| Pronunciation | drayn |
| Simple English meaning | Allow already accepted contents to leave before stopping. |
| Hindi cue | नया काम रोककर बचा हुआ काम पूरा करना |
| Meaning in this Python context | Graceful queue drain processes accepted items; stream `drain()` is instead a transport flow-control wait. |

Natural examples:

1. Stop producers before waiting for the queue to drain.
2. The graceful drain exceeded the shutdown budget.
3. Immediate termination is different from a completed drain.
4. **Interview:** `queue.join()` waits for unfinished-work accounting, while `writer.drain()` waits for transport buffer flow control.
5. **Engineering discussion:** Alert on drain duration and define the point where graceful shutdown becomes an abort.

### Saturation

| Item | Content |
|---|---|
| Pronunciation | sat-yuh-RAY-shun |
| Simple English meaning | The state in which all available capacity is occupied. |
| Hindi cue | पूरी क्षमता का भर जाना |
| Meaning in this Python context | Queue slots, worker permits, executor threads, or downstream buffers have no immediate spare capacity. |

Natural examples:

1. Executor saturation increased admission latency.
2. Queue saturation can be healthy briefly and dangerous when sustained.
3. Saturation at one stage should not create unbounded state in the previous stage.
4. **Interview:** Worker saturation and queue saturation are different state dimensions.
5. **Engineering discussion:** Compare saturation duration with oldest-item age; occupancy alone does not reveal whether work is making progress.

## 4. Deep explanation

### 4.1 Why the mechanism exists

Cooperative scheduling protects responsiveness only while Tasks yield frequently. It does not supply overload control. A fast producer can repeatedly allocate records or Tasks, a slow consumer can retain them, and the loop can remain technically “non-blocking” while memory and tail latency grow without a bound.

Backpressure turns downstream capacity into upstream control flow. The producer must await a finite boundary or receive an explicit rejection. That wait is useful, not accidental: it prevents accepting more transient state than the system has decided it can own. If code replaces `await queue.put(item)` with an unbounded sequence of `create_task(queue.put(item))`, the queue stays bounded but the pending Tasks become the new unbounded buffer.

### 4.2 The Queue contract has three independent state dimensions

For `asyncio.Queue(maxsize=N)`, positive `maxsize` causes `put()` to wait when `N` items are buffered. `get()` removes and returns one item. Every put increments an unfinished-work counter; every `task_done()` decrements it; `join()` waits for that counter to become zero. Asyncio queues are not thread-safe and their methods do not take timeout parameters. These are standard-library contracts, not timing guesses ([Python 3.14 asyncio queues](https://docs.python.org/3.14/library/asyncio-queue.html)).

Use three symbols:

- `B`: buffered items still inside the queue;
- `A`: items removed from the queue and actively being processed;
- `U`: accepted items not yet acknowledged complete with `task_done()`.

For one simple queue stage, `U` commonly equals `B + A`, but do not promote that identity to a universal system equation. A worker can create subwork, retries can move ownership, batches can combine items, and incorrect accounting can make the queue's internal `U` disagree with reality.

Important consequences:

- `get()` changes `B`, not `U`; a full queue can accept another item as soon as a worker retrieves one.
- `empty()` means `B == 0`; active work can still make `A > 0` and `U > 0`.
- `join()` means the program issued enough `task_done()` calls to balance accepted items. It does not prove a database commit, remote acknowledgement, or durable write unless the application calls `task_done()` only after that contract is truly satisfied.
- `qsize()` is the known buffered count at the call, but it can change after the next scheduling point. Use it for observation, not polling-based completion.

### 4.3 Execution sequence

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Producer awaits `put(alpha)` and it succeeds | `B=1`, `A=0`, `U=1` |
| 2 | Worker awaits `get()` and receives `alpha` | `B=0`, `A=1`, `U=1`; one buffer slot is free |
| 3 | Producer puts `beta` | `B=1`, `A=1`, `U=2` |
| 4 | Another producer attempts `put(gamma)` into a one-slot queue | Its Task waits; no state counter changes yet |
| 5 | Worker completes `alpha` and calls `task_done()` | `B=1`, `A=0`, `U=1` |
| 6 | Worker gets `beta`; waiting `gamma` can then be admitted | `beta` becomes active, one buffer slot becomes available, then `gamma` occupies it |
| 7 | Every accepted item completes and is acknowledged | `B=0`, `A=0`, `U=0`; `join()` may return |
| 8 | Graceful shutdown with an empty queue reaches worker `get()` | `get()` raises `QueueShutDown`; worker exits |

Scheduling can interleave event messages around these transitions, but the state invariants do not depend on a guessed wall-clock order.

### 4.4 Backpressure must cross every buffer

A queue is one valve, not a whole system. Common additional buffers include:

- request bodies read before admission;
- lists of created producer Tasks;
- active worker inputs removed from the queue;
- semaphore waiters;
- executor submission queues;
- library connection pools and internal retries;
- application batches;
- socket and transport write buffers;
- durable broker partitions or consumer prefetch.

For asyncio streams, `StreamWriter.write()` may buffer data. `await writer.drain()` is the public flow-control boundary: at the high watermark it waits until the write buffer falls to the low watermark, and below the high watermark it can return immediately ([Python 3.14 streams: `StreamWriter.drain()`](https://docs.python.org/3.14/library/asyncio-stream.html#asyncio.StreamWriter.drain)). Omitting `drain()` can move unbounded pressure from a queue into transport memory.

Capacity is a budget, not a magic constant. A starting decision should name:

- acceptable memory per buffered item, including referenced payloads;
- sustainable downstream concurrency;
- burst duration the service intentionally absorbs;
- maximum queue residence time relative to the caller's deadline;
- overload outcome once the budget is exhausted;
- graceful shutdown time for buffered plus active work.

### 4.5 Graceful queue shutdown versus abort

Python 3.13 added `Queue.shutdown()` and `QueueShutDown`. With `immediate=False`, the queue rejects future puts, wakes blocked putters with `QueueShutDown`, permits existing items to be retrieved, and lets `join()` complete normally when each accepted item receives `task_done()`. Once drained, later gets raise `QueueShutDown` ([Python 3.14 queue shutdown](https://docs.python.org/3.14/library/asyncio-queue.html#asyncio.Queue.shutdown)).

With `immediate=True`, the queue is drained immediately and blocked getters are woken. The documentation explicitly warns that `join()` can unblock even though no processing occurred, violating the normal join invariant. Treat this as an emergency-abort mode and report discarded work separately; never describe it as a successful drain.

A typical graceful owner sequence is:

1. stop or cancel ingress owners so no new admission race remains;
2. call `queue.shutdown()` to reject later and currently blocked puts;
3. let consumers finish accepted items and balance `task_done()`;
4. await `queue.join()` within the remaining shutdown deadline;
5. let consumers receive `QueueShutDown` and exit their owning `TaskGroup`;
6. close downstream connections and owned executors;
7. if the deadline expires, apply the separately defined abort and durability policy.

Python 3.11 has bounded queues and `join()` but no public queue shutdown API ([Python 3.11 asyncio queues](https://docs.python.org/3.11/library/asyncio-queue.html)). A common compatibility design stops producers, enqueues one unique sentinel per worker, lets each worker acknowledge its sentinel, and joins the queue. Sentinels need a collision-proof representation and participate in capacity and unfinished-work accounting. Cancellation can be appropriate instead, but the owner must still preserve current-item accounting and define what happens to buffered work.

### 4.6 Select synchronization by state, not familiarity

Asyncio synchronization primitives are for Tasks, are not thread-safe, and have no timeout parameter; place a timeout scope around acquisition when required ([Python 3.14 asyncio synchronization primitives](https://docs.python.org/3.14/library/asyncio-sync.html)).

| Primitive | State represented | Appropriate use | What it does not provide |
|---|---|---|---|
| `Lock` | One exclusive owner | Protect a short shared-state transition across awaits | Buffering, completion accounting, or OS-thread safety |
| `Event` | One boolean flag | Broadcast that a level-triggered condition is true | Item transfer, counting, or automatic reset |
| `Condition` | Predicate plus exclusive state access | Wait for a state predicate while releasing and reacquiring its lock | Message storage; callers must re-check the predicate |
| `Semaphore` | Available permits | Bound concurrent entry to a dependency | A finite backlog; arbitrarily many Tasks may wait for permits |
| `BoundedSemaphore` | Permits with over-release detection | Catch mismatched release in a fixed-capacity design | Queue ordering or work completion |
| `Barrier` | Parties reaching one phase | Coordinate a known cohort at a phase boundary | Streaming admission or indefinite dynamic membership |
| `Queue` | Ordered items plus unfinished count | Transfer ownership, buffer finitely, and join accepted work | Protection for unrelated shared mutable state |

The Python 3.14 `Lock` contract documents first-waiter fairness, but do not infer fairness for every primitive, dependency, or end-to-end request path. Fair admission may still be defeated by retries, priorities, connection pools, or work of unequal cost.

### 4.7 Async iteration is pull-shaped, not automatically resource-safe

The language data model requires `__aiter__()` to return an asynchronous iterator. `__anext__()` returns an awaitable whose result is the next value and raises `StopAsyncIteration` at normal exhaustion ([Python 3.14 data model: asynchronous iterators](https://docs.python.org/3.14/reference/datamodel.html#asynchronous-iterators)). Conceptually:

```python
iterator = aiter(source)
while True:
    try:
        item = await anext(iterator)
    except StopAsyncIteration:
        break
    else:
        await consume(item)
```

That shape supplies pull-based pressure only to the iterator boundary: the consumer requests one next value at a time. It does not bound an internal prefetch buffer, a remote server, a broker consumer, or a background Task the iterator created.

An `async def` containing `yield` creates an asynchronous generator. Its locals and control state remain suspended across yields. If consumption ends early through `break`, cancellation, or an exception, cleanup may otherwise occur later in an unexpected context. The language reference tells callers to close early-exited async generators explicitly ([Python 3.14 expressions: asynchronous generator functions](https://docs.python.org/3.14/reference/expressions.html#asynchronous-generator-functions)).

`contextlib.aclosing(generator)` gives the caller a deterministic boundary that awaits `generator.aclose()` on context exit. It keeps async exit code in the same context and lifetime as iteration ([Python 3.14 `contextlib.aclosing`](https://docs.python.org/3.14/library/contextlib.html#contextlib.aclosing)). `aclosing()` applies to objects with `aclose()`; a custom async iterator may need its own async context-manager API.

### 4.8 Blocking work crosses into another scheduler

Calling a blocking function directly in a coroutine occupies the event-loop thread until the call returns. Other Tasks cannot usefully progress merely because the caller wrote `async def`.

`asyncio.to_thread(function, *args)` runs a callable in a separate thread, returns a coroutine for its result, and propagates the current `contextvars.Context`. Its documented primary use is blocking I/O. Under a GIL-enabled build it usually does not make pure Python CPU-bound work parallel, though extension code that releases the GIL and alternative implementations can differ ([Python 3.14 `asyncio.to_thread`](https://docs.python.org/3.14/library/asyncio-task.html#running-in-threads)).

`loop.run_in_executor()` permits an explicitly selected thread, process, or interpreter executor. The default is a lazily created thread pool; a custom executor gives an application clearer capacity and shutdown ownership ([Python 3.14 event-loop executor API](https://docs.python.org/3.14/library/asyncio-eventloop.html#executing-code-in-thread-or-process-pools)). `run_in_executor()` does not supply `to_thread()`'s automatic context-copy contract, so a custom adapter must propagate context deliberately when required.

Two bounds matter:

1. executor workers bound simultaneously running calls;
2. an admission semaphore or bounded queue before submission bounds calls waiting to enter the executor.

Thread-pool worker count alone does not promise a finite submission backlog. A service that immediately submits every request can still retain unbounded call objects and payloads.

Cancellation crosses this boundary asymmetrically. Cancelling an asyncio Task can stop waiting for a result, but an already-running thread function cannot be preempted safely by `concurrent.futures.Future.cancel()`; that method returns `False` for a running call ([Python 3.14 concurrent Future cancellation](https://docs.python.org/3.14/library/concurrent.futures.html#concurrent.futures.Future.cancel)). Therefore pass native timeouts, use cooperative stop flags when supported, make side effects idempotent, retain outcome ownership, and isolate truly killable work in a suitable process boundary.

Asyncio objects are generally not thread-safe. To cross from another OS thread into an event loop, use documented thread-safe scheduling such as `loop.call_soon_threadsafe()` for callbacks or `asyncio.run_coroutine_threadsafe()` for a coroutine; do not call `asyncio.Queue.put_nowait()` from an arbitrary worker thread ([Python 3.14 scheduling from other threads](https://docs.python.org/3.14/library/asyncio-task.html#scheduling-from-other-threads)).

### 4.9 Failure, accounting, and ownership belong together

The safest worker structure establishes ownership immediately after `get()`:

```python
item = await queue.get()
try:
    await process(item)
finally:
    queue.task_done()
```

The `finally` balances queue accounting; it does not choose business semantics. If `process()` partially commits and then fails, the retry owner must know whether the operation is idempotent and whether completion should be acknowledged, retried, dead-lettered, or escalated. A local queue cannot decide durability.

Place workers under a structured owner. If one worker fails, a `TaskGroup` cancels siblings and interrupts the owner's `join()` wait rather than leaving it to hang silently. The owner still needs a failure policy for buffered items. “The TaskGroup raised” and “every accepted work item reached a safe terminal business state” are different claims.

## 5. Additional visual models

### Queue state axes

```text
                       put(item)
                          |
                          v
buffer axis B:       [ queued item ] ---- get() ----> removed
                          |                              |
                          |                              v
activity axis A:          |                        processing
                          |                              |
                          +------------+-----------------+
                                       |
completion axis U:    +1 on put        |        -1 on task_done
                      unfinished ------+--------> complete

empty() observes B only
join() waits for U == 0
worker capacity bounds A
```

#### How to read this visual

Read horizontally for physical location and vertically for independent accounting. An item leaves the buffer at `get()` but remains unfinished while active. The bottom labels show why `empty()` and `join()` answer different questions.

#### Key insight

Retrieval transfers ownership; it does not acknowledge completion.

#### Simplification or limitation

The diagram assumes one queue stage and one acknowledgement per item. Batching, retries, fan-out, and durable messaging require a richer ownership ledger.

### Cancellation at a blocking boundary

```text
event-loop Task                    executor Future / OS thread
      |                                      |
      +-- submit callable ------------------>+-- starts blocking I/O
      |                                      |
      +-- await result                       |
      |                                      |
 owner cancels Task                          |
      |                                      |
      +-- async wait unwinds                 +-- call may keep running
                                             |
                                  native timeout / stop flag / return
                                             |
                                  outcome still needs an owner
```

#### How to read this visual

Follow the left and right lifetimes separately after submission. Cancellation can change the left-hand Task's wait state without preempting the right-hand OS-thread call. The two lifetimes converge only when the callable stops by its own supported mechanism or returns.

#### Key insight

Offloading prevents event-loop blockage; it does not make blocking code cooperatively cancellable.

#### Simplification or limitation

The visual omits calls cancelled before they start, executor shutdown modes, process termination, C-extension behavior, transactions, retries, and calls whose library supports a real cancellation API.

## 6. Worked examples

### 6.1 Bounded queue admission and graceful shutdown

Runnable source: [`examples/bounded_pipeline.py`](examples/bounded_pipeline.py)

The example gates the first worker, fills a one-slot queue with a second item, and attempts a third put. It uses Events rather than elapsed time to prove that the third producer is waiting. It then releases the worker, shuts the queue down gracefully, joins accepted work, and lets the worker observe `QueueShutDown`.

Prediction before execution:

- the third put is incomplete before `alpha` is released;
- processing order is `alpha`, `beta`, `gamma` for one FIFO consumer;
- join follows completion of `gamma`;
- worker shutdown follows the empty joined state.

Observed on CPython 3.14.4 during initialization:

```text
third put blocked: True
processed: ('alpha', 'beta', 'gamma')
queue empty: True
producer:accepted:alpha
worker:get:alpha
producer:accepted:beta
producer:attempt:gamma
owner:third-put-blocked:True
owner:released-alpha
worker:done:alpha
worker:get:beta
worker:done:beta
producer:accepted:gamma
worker:get:gamma
worker:done:gamma
owner:shutdown
owner:joined
worker:queue-shutdown
```

The same file provides `map_bounded()`, which separates positive queue capacity from positive worker count, preserves input order through indexed results, and balances `task_done()` in `finally`.

### 6.2 Early async-generator cleanup

Runnable source: [`examples/async_stream.py`](examples/async_stream.py)

The example consumes two of three synthetic values inside `aclosing()`. Its trace proves that generator cleanup occurs before the owner continues past the context.

Observed on CPython 3.14.4 during initialization:

```text
accepted: ('alpha', 'beta')
owner:entered-context
stream:open
stream:yield:alpha
owner:accepted:alpha
stream:yield:beta
owner:accepted:beta
owner:break
owner:leaving-context
stream:close
owner:after-context
```

The file also includes `AsyncCountdown`, an explicit `__aiter__()`/`__anext__()` implementation whose terminal `StopAsyncIteration` is exercised by tests.

### 6.3 An owned blocking boundary

Runnable source: [`examples/blocking_boundary.py`](examples/blocking_boundary.py)

The adapter owns a finite `ThreadPoolExecutor`, acquires a semaphore before submission, copies the current context explicitly, and joins its executor. A gated underlying Future proves that a running callable rejects `cancel()` and remains active until its own gate opens.

Observed on CPython 3.14.4 during initialization:

```text
propagated request id: synthetic-request-080
ran off loop thread: True
running call cancelled: False
callable running after cancel attempt: True
callable finished after release: True
```

The harness's synchronous `future.result()` occurs only after it opens the deterministic completion gate. Application code should await an executor Future rather than block the loop while work is outstanding.

### 6.4 Debugging example — do not solve before an attempt

```python
async def worker(queue: asyncio.Queue[str]) -> None:
    while True:
        item = await queue.get()
        result = await transform(item)
        if result is not None:
            await persist(result)
            queue.task_done()
```

Before requesting the correction:

1. enumerate every path after successful `get()`;
2. identify which paths decrement unfinished work and which do not;
3. predict what `join()` does for a filtered item, a transform exception, a persist exception, and cancellation;
4. explain why acknowledging immediately after `get()` would produce false completion;
5. write a deterministic failing test with an Event gate rather than a guessed sleep.

The protected exercise is [`PY-CON-080-P03`](practice/README.md#py-con-080-p03-debug-the-join-that-never-returns).

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| Default `Queue()` is assumed bounded | It is called a queue and has a `maxsize` parameter | `maxsize=0` means no finite queue-size bound | Inspect `queue.maxsize` and drive a synthetic producer while consumers are gated |
| `maxsize` is treated as total in-flight capacity | The queue visually contains “the work” | Removed active items and external buffers are outside `B` | Gate workers after `get()` and record `qsize()`, active count, and total accepted |
| Producer wraps every `put()` in `create_task()` | The queue itself still blocks each put | Pending put Tasks become an unbounded buffer | Gate consumers and count retained producer Tasks |
| `empty()` or `qsize()==0` is used for completion | No items appear buffered | Active items can remain and `U` can be positive | Pause a worker after `get()` and compare `empty()` with a pending `join()` |
| `task_done()` is omitted on failure or cancellation | The happy path contains it | Each successful get owns exactly one later acknowledgement | Inject an exception after `get()` and bound the test's `join()` wait |
| `task_done()` is called immediately after `get()` | It prevents join hangs | It reports completion before processing or persistence | Gate processing after early acknowledgement and show join returning first |
| `task_done()` is called twice | Cleanup and success paths both try to be safe | Over-acknowledgement raises `ValueError` | Run one item through both paths and assert the exception |
| A sentinel collides with data | A string such as `"STOP"` seems convenient | Use a unique identity token or a typed envelope | Enqueue a legitimate equal-looking payload |
| One sentinel is used for many workers | One stop message sounds global | A consumed sentinel normally stops one worker; protocol must wake every worker | Start multiple workers and observe which remain blocked |
| Immediate shutdown is called a successful drain | `join()` may unblock | Immediate mode can discard items and violate the normal join inference | Queue work, call `shutdown(immediate=True)`, and compare processed versus accepted IDs |
| A semaphore is assumed to bound backlog | It bounds concurrent holders | Arbitrarily many Tasks can wait for permits | Create gated holders and count pending acquisition Tasks |
| Async iteration is assumed to have no buffering | Consumer requests one next value | Iterator internals or upstream libraries may prefetch | Instrument source reads and compare them with `__anext__()` calls |
| `break` is assumed to close an async generator immediately | Ordinary loop syntax ended cleanly | Explicit `aclose()` ownership is needed for deterministic early cleanup | Trace `finally` with and without `aclosing()` |
| Blocking I/O is called directly in a coroutine | It is “only a small call” | It occupies the loop thread for the call's full duration | Gate the blocking call and prove an unrelated Task cannot advance |
| Cancelling the await is assumed to kill a thread | The asyncio Task becomes cancelled | A running executor call cannot be preempted by Future cancellation | Gate a started callable and assert `Future.cancel()` returns `False` |
| Executor worker count is assumed to bound submissions | Only that many calls run together | Waiting submissions can still accumulate outside active workers | Gate all workers and count submitted call objects |
| `writer.write()` is treated as completed network delivery | The method returned | Bytes may only be buffered; `drain()` supplies flow control, not remote acknowledgement | Use controlled transport watermarks or a test double that records drain waits |
| Queue objects are touched from a worker thread | Both sides are Python code | Asyncio queues are not thread-safe | Route crossing through `call_soon_threadsafe()` or `run_coroutine_threadsafe()` |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| Bounded queue storage | `O(maxsize)` item references | Payloads may retain much more memory elsewhere; active items are outside the queue |
| `await queue.put()` when full | One suspended producer plus scheduler/bookkeeping cost | Total memory is unbounded if caller creates unbounded pending put Tasks |
| `await queue.get()` when empty | One suspended consumer plus scheduler/bookkeeping cost | Wake ordering and end-to-end fairness should not be inferred beyond documented contracts |
| `task_done()` / `join()` | Counter update / wait for zero | No public asymptotic guarantee is promised; correctness depends on exact pairing |
| Async iteration | One awaited next step per yielded item | Internal prefetch, batching, and source I/O can dominate cost |
| `aclosing()` | One awaited `aclose()` at context exit | Cleanup can itself block, fail, or be cancelled; give it ownership and policy |
| Semaphore-bound dependency | At most the configured active holders | Waiting Tasks and their payloads need a separate admission bound |
| Thread offload | Context capture, submission, thread scheduling, and result handoff | Useful responsiveness boundary, not a free speedup; pool queues and thread stacks consume resources |
| Stream `drain()` | Usually immediate below watermark; waits under buffer pressure | It is local transport flow control, not proof that a peer processed the bytes |
| Graceful queue drain | Proportional to accepted remaining work and dependency latency | Worst case requires deadlines, failure policy, and possibly abort/durable handoff |

No timing, throughput, or memory benchmark is claimed. The initialized tests establish state transitions, not production sizing.

## 9. Production relevance and trade-offs

### 9.1 Capacity ledger

Maintain one ledger rather than one queue constant:

| State | Example bound | Owner | Saturation outcome |
|---|---|---|---|
| Ingress body | Bytes or records read before admission | Request handler | Stop reading, reject, or spool durably |
| Buffered queue | Item count plus estimated bytes | Pipeline owner | Wait within deadline or reject |
| Active async workers | Worker count or semaphore permits | TaskGroup owner | Queue upstream |
| Blocking submissions | Admission permits before executor submit | Adapter owner | Wait/reject before retaining executor work |
| Retry state | Attempts and bytes per item | Retry policy owner | Dead-letter, surface failure, or durable retry |
| Batch | Item count and residence deadline | Batch owner | Flush by size or time budget |
| Transport | Write-buffer watermarks | Connection owner | Await `drain()` and honor deadline |

Count and byte bounds solve different risks. Ten large payloads can be more dangerous than ten thousand small identifiers. When payload size varies, admit by weighted cost or store compact references to durable data.

### 9.2 Overload is an API decision

When capacity is exhausted, choose and expose one or more outcomes:

- wait, while the caller's remaining deadline permits;
- reject with a retryable overload signal;
- shed lowest-value or stale work;
- coalesce duplicate state updates;
- spill to a durable broker with a different acknowledgement contract;
- sample telemetry while preserving correctness-critical events.

Silent unbounded waiting is not a neutral policy. It converts overload into latency and cancellation pressure. Silent dropping is also a policy, but an unsafe one unless the product contract permits it and metrics expose it.

### 9.3 Deadlines cross admission and processing

A caller can expire while waiting to put, while queued, while acquiring a dependency permit, during a blocking call, or while awaiting `drain()`. Carry one absolute deadline or decreasing remaining budget through every stage. Remove stale queued work deliberately or let a worker reject it before performing an obsolete side effect.

Timeout of an async wait does not guarantee the underlying blocking call stopped. Pass a native library timeout that fits inside the remaining budget and design for late completion.

### 9.4 Shutdown is a state machine

Name at least these states:

```text
RUNNING -> STOPPING_ADMISSION -> DRAINING -> CLOSING_DEPENDENCIES -> STOPPED
                          \-> ABORTING -> STOPPED_WITH_LOSS_OR_HANDOFF
```

The graceful path needs one owner and a total deadline. The abort path needs explicit accounting for discarded, active, indeterminate, retried, or durably handed-off items. Never infer safe business completion solely from process exit or immediate queue join.

### 9.5 Observability should reveal residence and progress

Useful signals include:

- current and high-water queue occupancy;
- admission wait distribution and rejection/drop counts;
- oldest buffered item age;
- active workers and semaphore waiters;
- executor running calls and pre-submission waiters;
- processing latency and deadline-expiry stage;
- unfinished count exposed through application accounting rather than queue private attributes;
- generator open/close counts for resource-bearing streams;
- transport drain wait;
- graceful drain duration, abort count, and indeterminate work.

Occupancy without age can hide a stuck queue; age without throughput can hide whether recovery is happening. Correlate state, wait, and completion.

### 9.6 Testing priorities

Prefer gates and injected outcomes over real time:

- use `asyncio.Event` to hold a worker after `get()`;
- start a putter only after the queue is known full;
- assert a Task is pending before releasing capacity;
- inject transform and persistence failures;
- break iteration early and trace cleanup order;
- start a blocking call behind a `threading.Event` and test cancellation limits;
- simulate shutdown with buffered, active, blocked-put, and failed work;
- place short timeouts around tests only as deadlock guards, not as the coordination mechanism.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| `asyncio.Queue.shutdown()` and `QueueShutDown` | Standard library | 3.13 | Stop producers and use unique sentinels or structured worker cancellation with explicit buffered-work policy | Immediate mode can violate the normal join invariant |
| Positive `Queue.maxsize` blocks `put()` when full | Standard library | 3.4 | Same public API | `maxsize=0` is unbounded by item count |
| Asyncio Queue and synchronization primitives are not thread-safe | Standard library | 3.4-era asyncio APIs | Same rule | Use thread-safe loop scheduling at OS-thread boundaries |
| `TaskGroup` ownership in examples | Standard library | 3.11 | Available unchanged | Preserve child failures and cancellation-safe accounting |
| `asyncio.Barrier` | Standard library | 3.11 | Build explicit phase coordination or avoid a barrier | Barrier is not needed for ordinary queue worker pools |
| Async iterator protocol | Language | 3.5; direct `__aiter__()` return required since 3.7 | Same protocol | `__anext__()` returns an awaitable and raises `StopAsyncIteration` |
| Async generators | Language | 3.6 | Same feature | Explicit early close remains an ownership concern |
| `contextlib.aclosing()` | Standard library | 3.10 | Available unchanged | Calls and awaits `aclose()` on context exit |
| `asyncio.to_thread()` with context propagation | Standard library | 3.9 | Available unchanged | Primarily for blocking I/O; cancellation does not preempt a running thread callable |
| `loop.run_in_executor()` with a custom executor | Standard library | 3.4 | Available unchanged | Explicit adapters must decide context propagation and executor shutdown |
| `StreamWriter.drain()` flow control | Standard library | 3.4 | Available unchanged | Local buffer pressure is not remote processing acknowledgement |
| Exact executor defaults, scheduling, and queue internals | CPython/implementation detail | Version-dependent | Do not depend on exact defaults | Configure application-owned capacity and test public outcomes |

Canonical examples target Python 3.14. The bounded pipeline's shutdown path does not run unchanged on Python 3.11; the note deliberately presents the compatibility protocol rather than pretending both APIs are identical.

## 11. Practice brief

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-CON-080-P01` | Predict | 3 | Explain `B`, `A`, and `U` through a gated trace | [Practice](practice/README.md#py-con-080-p01-predict-the-three-queue-counters) |
| `PY-CON-080-P02` | Implement | 4 | Bounded ordered pipeline with failure-safe accounting | [Practice](practice/README.md#py-con-080-p02-implement-a-bounded-ordered-pipeline) |
| `PY-CON-080-P03` | Debug | 3 | Reproduce and repair a non-returning join | [Practice](practice/README.md#py-con-080-p03-debug-the-join-that-never-returns) |
| `PY-CON-080-P04` | Implement | 3 | Explicit async-iterator protocol and termination tests | [Practice](practice/README.md#py-con-080-p04-implement-an-asynchronous-page-iterator) |
| `PY-CON-080-P05` | Debug | 3 | Deterministic early async-generator cleanup | [Practice](practice/README.md#py-con-080-p05-repair-early-async-generator-cleanup) |
| `PY-CON-080-P06` | Implement | 5 | Finite blocking adapter with context and cancellation policy | [Practice](practice/README.md#py-con-080-p06-build-a-bounded-blocking-adapter) |
| `PY-CON-080-P07` | Review | 4 | Prioritized overload and lifetime findings | [Practice](practice/README.md#py-con-080-p07-review-an-overload-prone-service) |
| `PY-CON-080-P08` | Design | 5 | Production capacity, overload, deadline, shutdown, and metrics plan | [Practice](practice/README.md#py-con-080-p08-design-a-production-ingestion-boundary) |

Do not add solutions to the practice artifact before an attempt. Reveal progressive hints one at a time and preserve the learner's original reasoning.

## 12. Interview prompts

Ask and answer these one at a time during review:

1. A queue with `maxsize=10` is empty, yet `join()` is blocked. Give a valid execution state and the exact counters.
2. Why can `create_task(queue.put(item))` defeat the intended bound even though the queue is finite?
3. Where must `task_done()` live, and what business event should precede it?
4. Compare a Queue, Semaphore, and Lock for protecting a downstream API.
5. Design graceful shutdown for three workers on Python 3.14, then give the Python 3.11 alternative.
6. Why is `shutdown(immediate=True)` not evidence that accepted work completed?
7. Desugar `async for` into the relevant protocol calls and terminal exception.
8. Why can an async iterator still hide unbounded prefetch?
9. What problem does `aclosing()` solve after an early `break`?
10. What does cancelling a Task awaiting `to_thread()` fail to guarantee?
11. How would you bound both running thread calls and submitted-but-not-running calls?
12. Name the metrics needed to distinguish a healthy burst from a stuck saturated pipeline.

A strong answer should eventually demonstrate:

- exact admission, retrieval, completion, iteration, and cancellation mechanics;
- separate capacities and lifetime owners at every buffer or scheduler boundary;
- graceful and abort shutdown semantics, including Python 3.11 compatibility;
- production trade-offs involving deadlines, overload, durability, observability, and late blocking-call outcomes.

## 13. Closed-book revision cues

Without reading the note:

1. Draw the finite-valves visual and define `B`, `A`, and `U`.
2. Explain why `get()` frees capacity but does not reduce unfinished work.
3. Predict a one-slot queue trace with one gated worker and three puts.
4. State the exact `task_done()` invariant and two ways to violate it.
5. Reconstruct graceful `Queue.shutdown()` and contrast immediate mode.
6. Give the sentinel shutdown protocol for Python 3.11.
7. Write `__aiter__()` and `__anext__()` signatures and name the exhaustion exception.
8. Explain why early generator exit needs an explicit close owner.
9. Draw the two lifetimes at a blocking executor boundary after cancellation.
10. Review one real service path for hidden buffers, admission waits, deadlines, and shutdown ownership.

## 14. Authoritative sources

Only official Python sources opened and used during the 2026-08-28 audit are listed.

1. [Queues — `asyncio.Queue`, unfinished tasks, shutdown, variants, and exceptions](https://docs.python.org/3.14/library/asyncio-queue.html), Python 3.14.7 documentation, accessed 2026-08-28.
2. [Synchronization Primitives — Lock, Event, Condition, Semaphore, BoundedSemaphore, and Barrier](https://docs.python.org/3.14/library/asyncio-sync.html), Python 3.14.7 documentation, accessed 2026-08-28.
3. [Data model — Asynchronous Iterators](https://docs.python.org/3.14/reference/datamodel.html#asynchronous-iterators), Python 3.14.7 documentation, accessed 2026-08-28.
4. [Expressions — Asynchronous generator functions and methods](https://docs.python.org/3.14/reference/expressions.html#asynchronous-generator-functions), Python 3.14.7 documentation, accessed 2026-08-28.
5. [`contextlib.aclosing()`](https://docs.python.org/3.14/library/contextlib.html#contextlib.aclosing), Python 3.14.7 documentation, accessed 2026-08-28.
6. [Coroutines and Tasks — running in threads and scheduling from other threads](https://docs.python.org/3.14/library/asyncio-task.html#running-in-threads), Python 3.14.7 documentation, accessed 2026-08-28.
7. [Event loop — executing code in thread, process, or interpreter pools](https://docs.python.org/3.14/library/asyncio-eventloop.html#executing-code-in-thread-or-process-pools), Python 3.14.7 documentation, accessed 2026-08-28.
8. [`concurrent.futures.Future.cancel()`](https://docs.python.org/3.14/library/concurrent.futures.html#concurrent.futures.Future.cancel), Python 3.14.7 documentation, accessed 2026-08-28.
9. [Streams — `StreamWriter.write()`, `drain()`, and close behavior](https://docs.python.org/3.14/library/asyncio-stream.html#asyncio.StreamWriter.drain), Python 3.14.7 documentation, accessed 2026-08-28.
10. [Queues — Python 3.11 compatibility baseline](https://docs.python.org/3.11/library/asyncio-queue.html), Python 3.11.15 documentation, accessed 2026-08-28.

## 15. Durable clarification log

| Date | Clarification | Why it belongs in canonical notes | Source or evidence |
|---|---|---|---|
| 2026-08-28 | Positive queue `maxsize` bounds buffered items, not active work or pending producer Tasks. | Prevents the most common incorrect capacity claim and guides end-to-end overload review. | [Queue contract](https://docs.python.org/3.14/library/asyncio-queue.html) plus [`bounded_pipeline.py`](examples/bounded_pipeline.py) gated trace |
| 2026-08-28 | `shutdown(immediate=True)` is an abort whose join behavior can violate the ordinary processed-work invariant. | Prevents emergency termination from being reported as graceful completion. | [Queue shutdown warning](https://docs.python.org/3.14/library/asyncio-queue.html#asyncio.Queue.shutdown) |
| 2026-08-28 | Early `async for` exit and async-generator cleanup are separate ownership events; `aclosing()` makes close deterministic. | Protects resource and context lifetimes in partial-consumption paths. | [`aclosing()` contract](https://docs.python.org/3.14/library/contextlib.html#contextlib.aclosing) plus [`async_stream.py`](examples/async_stream.py) trace |
| 2026-08-28 | Cancelling an async wait does not provide preemptive termination of an already-running executor callable. | Forces designs to include native deadlines, cooperative stop, idempotency, and late-outcome ownership. | [`Future.cancel()` contract](https://docs.python.org/3.14/library/concurrent.futures.html#concurrent.futures.Future.cancel) plus [`blocking_boundary.py`](examples/blocking_boundary.py) gate |
