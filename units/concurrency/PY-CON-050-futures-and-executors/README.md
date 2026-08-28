# PY-CON-050 — Futures and executors

[Curriculum entry](../../../CURRICULUM.md#py-con-050) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-CON-050`

## Physical Notebook Core

### Problem this concept solves

Submitting work is easy; retaining control of every accepted job is harder. A caller needs one uniform way to observe completion, retrieve a value, receive an exception, attempt cancellation, enforce a waiting deadline, and shut down a bounded set of thread, process, or interpreter workers.

### One-sentence mental model

> An executor owns where and when callables run; each returned future is the caller's handle to one eventual terminal outcome—not the worker itself and not a promise that the work can still be stopped.

### One important visual

```text
caller                    executor                         worker
  | submit(call) ---------->|                               |
  |<---------- Future F ----|  PENDING queue                |
  |                         |------ claim F ---------------->|
  |                         |       RUNNING                  |
  |                         |<----- value or exception ------|
  | result()/exception() <--|       FINISHED                 |

Future state:

                         worker claims
PENDING ----------------------------------------------> RUNNING
   |                                                       |
   | cancel() succeeds                                     | return
   v                                                       v
CANCELLED                                               FINISHED(value)
                                                           |
                                                           | raise
                                                           v
                                                        FINISHED(exception)

done() is true for CANCELLED and either FINISHED outcome.
```

#### How to read this visual

Read the message flow from top to bottom, then read the state graph from left to right. `submit()` returns before the callable necessarily starts. Cancellation has one successful path from pending work; after a worker claims the call, the owner can wait, time out, or cooperate through an application protocol, but `Future.cancel()` cannot forcibly stop that running call.

#### Key insight

A future separates *submission* from *outcome ownership*. It records one call's state and eventual value or exception while the executor owns workers, admission, and shutdown.

#### Simplification or limitation

This is a conceptual public-API model, not the private CPython state machine or queue layout. It omits races at the pending/running boundary, callbacks, broken pools, process serialization, interpreter isolation, application-level cooperative cancellation, and external side effects that may outlive the caller's wait.

### Governing rules or invariants

1. Preserve a future or another explicit record for every accepted job until its value, exception, cancellation, or indeterminate pool failure has been handled.
2. A timeout limits how long the caller waits; it does not cancel or roll back the callable. `cancel()` succeeds only before execution begins.
3. Never make a saturated executor's worker block on new work that only the same executor can run; task dependencies must fit the available capacity or be coordinated outside the pool.
4. The component that creates an executor owns bounded admission, result collection, failure policy, and shutdown.

### Minimal example

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def normalize(job_id: str, value: str) -> tuple[str, str]:
    if not value.strip():
        raise ValueError(f"{job_id}: empty value")
    return job_id, value.strip().casefold()


jobs = {"job-a": " Ready ", "job-b": "", "job-c": "PAID"}

with ThreadPoolExecutor(max_workers=2) as executor:
    future_to_id = {
        executor.submit(normalize, job_id, value): job_id
        for job_id, value in jobs.items()
    }
    for future in as_completed(future_to_id):
        job_id = future_to_id[future]
        try:
            print("ok", future.result())
        except ValueError as error:
            print("failed", job_id, str(error))
```

Expected reasoning:

1. `submit()` returns one `Future` per job, and the reverse mapping preserves job identity independently of completion order.
2. `as_completed()` yields whichever future reaches a terminal state next; calling `result()` either returns that call's value or re-raises its exception in the collecting thread.
3. Leaving the `with` block performs waiting shutdown, but production code must still choose capacity, deadlines, accepted-work policy, and application-level cancellation deliberately.

### One failure or misconception

**Mistake:** “`future.result(timeout=1)` stops the job after one second, and `future.cancel()` can kill it if it is still slow.”

**Correction:** A result timeout stops only that wait. The job can continue and produce side effects. `cancel()` returns `False` once the future is running or finished; stopping running work requires a cooperative application protocol or, for process containment, an explicitly destructive pool-level action with weaker cleanup guarantees.

### Important trade-offs

- `ThreadPoolExecutor` has cheap shared-memory calls and suits bounded blocking I/O, but shared-state safety, context propagation, library thread-safety, and the regular CPython GIL remain relevant.
- `ProcessPoolExecutor` offers process isolation and ordinary multi-core pure-Python execution, but startup, pickling, import safety, memory, and worker-loss handling cost more.
- `InterpreterPoolExecutor` adds isolated-interpreter parallelism in Python 3.14, but serialization, mutable-data isolation, extension compatibility, and operational maturity require explicit evaluation.
- `submit()` gives per-job identity and flexible collection; `map()` is compact and input-ordered but can hide per-item identity, defer an exception until its position is consumed, and create head-of-line waiting.

### Interview-revision cues

- Reconstruct: submit → pending → running → value/exception, with cancellation only before running.
- Compare: `submit`, `map`, `wait`, `as_completed`, `result`, and `exception`.
- Diagnose: result timeout mistaken for cancellation, nested-future deadlock, unbounded submission, lost exceptions, and shutdown that abandons accepted work.
- Choose: thread, process, or interpreter workers from workload, data boundary, dependency graph, and deployment constraints.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Concurrency, parallelism, and asynchronous Python |
| Canonical ID | `PY-CON-050` |
| Learning outcome | Coordinate work with `concurrent.futures`, executors, futures, completion, exceptions, and shutdown. |
| Hard prerequisites | `PY-CON-020`, `PY-CON-040` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | Medium |
| Backend relevance | High |
| Depth | D2 |
| Scope | Standard library |
| Size | M |
| Evidence profile | E+C+D |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4, regular GIL-enabled build, Linux x86_64 |
| Last source audit | 2026-08-28 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. submit independent callables, retain job identity, and collect values and exceptions with `Future`, `wait()`, `as_completed()`, and `Executor.map()` while explaining their ordering and timeout contracts;
2. choose deliberately among thread, process, and interpreter executors from workload shape, isolation, serialization, dependency, portability, and capacity requirements;
3. design bounded admission, cooperative cancellation, exception handling, and shutdown without deadlocking a pool, losing accepted outcomes, or claiming that a timed-out wait stopped running work;
4. diagnose task failure, cancellation, caller timeout, initializer failure, abrupt worker loss, and executor shutdown as distinct states.

Required evidence:

- reconstruct the executor/future visual and explain every public state transition without reading;
- complete prediction, implementation, and debugging practice while preserving the first attempt and deterministic tests;
- run and explain the lifecycle, completion-order, bounded-map, and process-pool examples, including their Python-version and execution-boundary limitations;
- review a backend fan-out design for bounded capacity, job identity, deadlines, failure ownership, side effects, and graceful shutdown.

Initialization created source-checked material and runnable examples. It did not provide learner attempts or review evidence, so the learning state remains `Not started` and the artifact remains `Draft`.

## 2. Prerequisite bridge

The two hard-prerequisite artifacts exist, but the tracker records no learner evidence for either. These minimum bridges support entry into this unit without completing those prerequisites.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-CON-020` — Threads, lifecycle, context, and thread-safe boundaries | A thread executor reuses threads, shares process memory, and inherits thread-safety, failure, context, and shutdown concerns. | A thread is an owned execution resource: shared mutable invariants need an explicit safe boundary, uncaught worker failure must reach the result owner, request context is not ordinary shared state, and non-daemon lifecycle must be shut down deliberately. |
| Hard | `PY-CON-040` — Multiprocessing, IPC, shared memory, and process isolation | A process executor is a higher-level process pool, not an escape from import, serialization, start-method, failure, or cleanup rules. | Worker processes have separate ordinary heaps; callables, arguments, and results must cross a pickling/import boundary; the parent owns process-pool shutdown; and abnormal worker exit is different from an application exception returned by a healthy worker. |

Recommended follow-up: study both prerequisites in their dedicated topic chats. Continue here by treating the bridges as explicit assumptions.

## 3. Vocabulary and professional English

### Future

| Item | Content |
|---|---|
| Pronunciation | FYOO-cher |
| Simple English meaning | A handle for a result that may become available later. |
| Hindi cue | भविष्य का परिणाम / बाद में मिलने वाला परिणाम |
| Meaning in this Python context | An object representing one submitted callable's progress and eventual value, exception, or successful pre-run cancellation. |

Natural examples:

1. Keep the future until the job's outcome has been recorded.
2. This future is complete, but its result contains an exception.
3. A cancelled future is done even though its callable never ran.
4. **Interview:** A `concurrent.futures.Future` is not awaitable like an `asyncio.Future`.
5. **Engineering discussion:** We map each future back to a stable job ID before collecting completions.

### Executor

| Item | Content |
|---|---|
| Pronunciation | ig-ZEK-yuh-ter |
| Simple English meaning | Something responsible for carrying out submitted work. |
| Hindi cue | काम चलाने वाला प्रबंधक |
| Meaning in this Python context | A pool abstraction that accepts callables, schedules them on a concrete worker mechanism, creates futures, and owns resource shutdown. |

Natural examples:

1. The request handler does not create a new executor for every item.
2. The executor owns four workers and a bounded admission policy.
3. Shutdown rejects new submissions.
4. **Interview:** The `Executor` interface separates outcome handling from thread or process selection.
5. **Engineering discussion:** We inject the executor so one service owns capacity instead of creating nested pools.

### Propagate

| Item | Content |
|---|---|
| Pronunciation | PROP-uh-gayt |
| Simple English meaning | Carry information or an effect from one place to another. |
| Hindi cue | आगे पहुँचाना |
| Meaning in this Python context | Preserve a worker's exception or a cancellation signal so the component responsible for the job can observe and act on it. |

Natural examples:

1. The worker propagates validation failure through its future.
2. A timeout does not propagate a stop request automatically.
3. Preserve the original exception while adding the job identifier.
4. **Interview:** `Future.result()` propagates the callable's exception to the waiting caller.
5. **Engineering discussion:** Our aggregation layer propagates the request deadline but not the raw request object.

### Saturation

| Item | Content |
|---|---|
| Pronunciation | sat-yuh-RAY-shuhn |
| Simple English meaning | A state in which all available capacity is occupied. |
| Hindi cue | पूरी क्षमता भर जाना |
| Meaning in this Python context | All workers or admission slots are busy, so new work queues, blocks, or is rejected according to policy. |

Natural examples:

1. Pool saturation increased queueing latency.
2. The dashboard reports both worker use and submission backlog.
3. A bounded queue makes saturation visible to callers.
4. **Interview:** Nested waits can turn pool saturation into deadlock.
5. **Engineering discussion:** We reject optional enrichment before saturation consumes the request deadline.

## 4. Deep explanation

### 4.1 Why executors and futures exist

Threads and processes provide execution mechanisms, but application code would otherwise repeat worker creation, work queues, result queues, exception capture, completion notification, and teardown. PEP 3148 introduced two linked abstractions: an executor receives callables and a future represents the progress and outcome of each accepted computation. The future intentionally makes only a small commitment about *how* the work runs, allowing thread and process pools to share the same caller-facing control surface. See [PEP 3148 — Motivation and Rationale](https://peps.python.org/pep-3148/).

The abstraction is high-level, not magical. It does not decide whether tasks are independent, make a client thread-safe, add backpressure to `submit()`, turn a timeout into cancellation, make side effects idempotent, or prove that concurrency improves the workload. Those remain application design decisions.

### 4.2 The public `Future` contract

Application code normally receives futures from `Executor.submit()` and does not instantiate or mutate them directly. The public inspection and collection methods expose these meanings:

| Method | Owner-visible meaning | Important boundary |
|---|---|---|
| `cancel()` | Attempt to prevent a pending call from starting. | Returns `False` if the call is already running or finished. |
| `cancelled()` | Cancellation succeeded before execution. | It does not mean a running callable cooperatively stopped. |
| `running()` | The executor has begun the call and it cannot be cancelled through `cancel()`. | It says nothing about useful progress or whether the worker is blocked. |
| `done()` | The future was cancelled or finished with a value or exception. | Always inspect the terminal category before treating it as success. |
| `result(timeout)` | Wait up to the caller's limit, then return the value or raise cancellation, timeout, or the callable's exception. | Timeout leaves the computation running unless another protocol stops it. |
| `exception(timeout)` | Wait, then return the callable's exception or `None` for a successful call. | It raises for timeout or cancellation; it does not consume or clear the failure. |
| `add_done_callback(fn)` | Run `fn(future)` after cancellation or completion. | Keep callbacks small, non-blocking, exception-safe, and independent of pool capacity. |

The Python 3.14 reference specifies that `result()` re-raises the callable's exception and that successful cancellation makes `result()` and `exception()` raise `CancelledError`. A future may finish before the collector asks for it; result retrieval is observation, not what causes execution. See [`Future` objects](https://docs.python.org/3.14/library/concurrent.futures.html#future-objects).

`concurrent.futures.Future` and `asyncio.Future` are different types. The former blocks in `result(timeout)` and is not directly awaitable; an event-loop integration must wrap it through an appropriate API. Detailed event-loop futures belong to `PY-CON-060`. See [asyncio Future differences](https://docs.python.org/3.14/library/asyncio-future.html#future-object).

### 4.3 Submission and collection are separate choices

`submit(fn, *args, **kwargs)` schedules one call and immediately returns its future. It is the most explicit form when the caller needs job metadata, heterogeneous callables, individual cancellation, or per-job failure policy.

`map(fn, *iterables, timeout=None, chunksize=1, buffersize=None)` presents a compact input-ordered result iterator. Calls may run concurrently, but values are yielded in input order, so a slow early item can delay access to later completed items. An exception is raised when iteration reaches that item's position. With `ProcessPoolExecutor`, `chunksize` groups input items for transfer; it has no effect for thread or interpreter pools. Python 3.14 added `buffersize` to limit submitted tasks whose results have not yet been yielded; without it, input iterables are collected eagerly. See [`Executor.map()`](https://docs.python.org/3.14/library/concurrent.futures.html#concurrent.futures.Executor.map).

Collection APIs answer different questions:

| API | Returns or yields | Use when | Does not do |
|---|---|---|---|
| `future.result(timeout)` | One value or one terminal exception | A dependency is intentional and sufficient capacity exists | Stop work when the wait expires |
| `wait(fs, return_when=...)` | Sets named `done` and `not_done` | The caller needs a batch barrier or a first-completion/first-exception trigger | Retrieve values, preserve order, or cancel remaining work |
| `as_completed(fs, timeout)` | Futures in terminal-completion order | Results should be handled promptly with per-job identity | Return input order |
| `executor.map(...)` | Values in input order | Calls are homogeneous and per-future control is unnecessary | Expose each future or completion order |

`FIRST_COMPLETED` includes cancellation. `FIRST_EXCEPTION` returns when one future raises, but becomes equivalent to `ALL_COMPLETED` when none raises. Neither mode cancels siblings. Duplicate futures passed to `wait()` or `as_completed()` are returned only once. See [`wait()` and `as_completed()`](https://docs.python.org/3.14/library/concurrent.futures.html#module-functions).

### 4.4 Choosing the worker boundary

All three concrete Python 3.14 executors implement the same broad interface, but they do not provide equivalent semantics or costs.

| Executor | Worker boundary | Strong initial fit | Data and failure boundary | First questions |
|---|---|---|---|---|
| `ThreadPoolExecutor` | Threads in one interpreter and process | Bounded blocking I/O; native work documented to release the GIL | Ordinary objects can be shared; task exceptions stay on futures; initializer failure breaks the pool | Is every shared client safe? How is context propagated? What bounds pending work? |
| `ProcessPoolExecutor` | Separate OS processes | CPU-heavy pure-Python calls; address-space isolation | Callables, arguments, and results must be picklable; `__main__` must be importable; abrupt worker loss can break the pool | Is transfer cost amortized? Which start context? Is the environment process-safe? |
| `InterpreterPoolExecutor` | Threads, each owning an isolated interpreter | Selected CPU work needing multi-core execution without separate processes | Calls and results are serialized with pickle; mutable objects are isolated; exception preservation can include `ExecutionFailed` | Are dependencies multi-interpreter compatible? How will isolated state communicate? |

On a regular CPython build, thread workers do not make CPU-bound Python bytecode run simultaneously, though they remain useful for waiting-heavy work and native code with a documented GIL boundary. Process workers have separate interpreters and heaps. Python 3.14's interpreter pool gives each worker interpreter its own GIL and isolated runtime state. See [`ThreadPoolExecutor`](https://docs.python.org/3.14/library/concurrent.futures.html#threadpoolexecutor), [`ProcessPoolExecutor`](https://docs.python.org/3.14/library/concurrent.futures.html#processpoolexecutor), and [`InterpreterPoolExecutor`](https://docs.python.org/3.14/library/concurrent.futures.html#interpreterpoolexecutor).

The interface makes migration syntactically approachable, but not semantically automatic. A callable that closes over a mutable thread-safe client may be unpicklable for a process, meaningless in an isolated interpreter, or too small to amortize serialization. Treat executor selection as an architectural boundary, not a constructor swap.

### 4.5 Cancellation, deadlines, and side effects

Three events are often confused:

1. **The owner stops waiting.** `result(timeout)` or `as_completed(..., timeout)` raises `TimeoutError`; the work may continue.
2. **A pending future is cancelled.** `cancel()` returns `True`; its callable will not start.
3. **Running application work stops cooperatively.** The callable observes an event, deadline, closed resource, or application token and exits at a safe point.

Cancellation of a future is intentionally conservative because threads cannot be safely killed at arbitrary Python instructions, and process termination can leave external writes, locks, pipes, transactions, or temporary resources in uncertain state. If a running call can exceed its usefulness, pass a monotonic deadline or a mechanism appropriate to the worker boundary, check it at defined safe points, and make side effects idempotent or transactional where required.

`shutdown(cancel_futures=True)` cancels pending calls that have not started; running and completed calls are unaffected. With both `wait=True` and `cancel_futures=True`, running calls finish before shutdown returns while pending calls are cancelled. Using an executor as a context manager performs waiting shutdown. `wait=False` returns from the shutdown call early, but Python still does not exit until pending futures finish. See [`Executor.shutdown()`](https://docs.python.org/3.14/library/concurrent.futures.html#concurrent.futures.Executor.shutdown).

Python 3.14 adds `ProcessPoolExecutor.terminate_workers()` and `kill_workers()` for immediate containment. They also initiate executor shutdown and make further submission invalid. These are escalation tools, not equivalent to a graceful application cancellation protocol; after an abrupt stop, classify incomplete jobs and external side effects honestly.

### 4.6 Pool deadlock and dependency direction

An executor has finite capacity. If every worker waits for work that is queued behind those same workers, no worker remains to make the dependency true.

```text
ThreadPoolExecutor(max_workers=1)

worker 1: outer() ── submit(inner) ── inner is queued
                  └─ wait inner.result()

queue: [inner]        no free worker can run it

wait-for cycle:
worker 1 waits for inner → inner waits for worker 1's capacity
```

#### How to read this visual

Follow the worker from left to right. It occupies the only execution slot, submits an inner call to the same pool, and blocks on the returned future. Then follow the queue back to capacity: the queued call cannot start until that occupied worker returns.

#### Key insight

Futures make dependencies visible but do not schedule around impossible dependency graphs. A worker should normally return data to an owner that coordinates the next stage, or the executor must have a deliberately proven capacity and failure model for nested dependencies.

#### Simplification or limitation

This is the one-worker proof. Larger pools can deadlock through cycles involving several workers or merely starve unrelated work. Adding one worker may hide one reproduction without making an unbounded or recursive design safe.

The standard-library documentation explicitly warns about future-on-future waits in thread-pool callables. It also states that calling `Executor` or `Future` methods from a callable running in `ProcessPoolExecutor` results in deadlock. Avoid nested ownership and centralize orchestration outside process workers. See the executor-specific deadlock warnings in [`concurrent.futures`](https://docs.python.org/3.14/library/concurrent.futures.html).

### 4.7 Exceptions and broken executors

Keep these failure categories separate:

| Category | Example | Owner observation | Recovery question |
|---|---|---|---|
| Application exception | Callable rejects invalid synthetic input | `future.result()` raises that exception | Is this job retryable, terminal, or expected? |
| Successful pre-run cancellation | Owner withdraws queued optional work | `cancel()` is `True`; `result()` raises `CancelledError` | Was the job definitely still pending? |
| Caller wait timeout | Dependency misses a local deadline | Waiting API raises `TimeoutError`; future may remain pending/running | Will the owner keep, ignore, or cooperatively stop the outcome? |
| Initializer failure | Worker setup raises | Pending and new work can raise a broken-pool subtype | Can the executor be replaced after fixing configuration? |
| Abrupt process loss | Worker exits non-cleanly | Affected work or later operations raise `BrokenProcessPool` | Which jobs and side effects are now indeterminate? |
| Shutdown misuse | Submit after shutdown | `RuntimeError` | Which component violated executor ownership? |

Task exceptions do not automatically print in the submitting thread and do not necessarily stop sibling jobs. If code drops futures and never calls `result()` or `exception()`, application failures can be operationally lost. Collect every accepted outcome or attach a safe reporting callback plus a durable ownership record.

A broken executor is not just one failed business job: the pool cannot reliably accept or execute new work. Recreating it may be appropriate only after understanding the initializer, worker crash, resource, or deployment cause. Python exposes `BrokenExecutor` plus concrete `BrokenThreadPool`, `BrokenProcessPool`, and Python 3.14 `BrokenInterpreterPool` categories.

### 4.8 Bounded submission and backpressure

`max_workers` bounds simultaneous worker calls; it does not by itself promise a small pending queue. Repeated `submit()` can retain futures, arguments, closures, queued work items, and eventual results faster than workers drain them. A production owner should choose one of:

- a bounded producer protocol that waits for completions before submitting more;
- an application semaphore or bounded queue with explicit overload and shutdown behavior;
- Python 3.14 `Executor.map(..., buffersize=N)` for homogeneous input-ordered mapping;
- rejection or degradation before downstream and memory limits are exhausted.

`buffersize` limits submitted results not yet yielded by the map iterator. It is not the same as `max_workers`, a network connection pool, a global service concurrency limit, or a durable job queue. In Python 3.11, implement an explicit bounded window around `submit()`/`wait()` or use an application queue; do not emulate backpressure by reading private executor fields.

### 4.9 Callbacks and ownership

`add_done_callback()` is useful for metrics, wakeups, or moving a small immutable completion record into an owner-controlled channel. Registered callbacks are called in registration order and in a thread belonging to the process that registered them; a callback added after completion may run immediately. Therefore callback code must not assume a particular worker thread, hold unknown locks, block on the same executor, or raise unobserved failures.

For ordinary application flow, `as_completed()` is often easier to reason about because the result owner handles identity, value, exception, and policy in one place. Use callbacks when event-driven integration genuinely benefits from them, not to hide result ownership.

### 4.10 End-to-end execution sequence

| Step | Event | Relevant state and owner decision |
|---:|---|---|
| 1 | Owner validates a job and checks admission capacity. | Rejected work has no future; accepted work receives a stable ID. |
| 2 | Owner calls `submit()` or advances a bounded `map()` source. | Executor creates a pending future and retains the call. |
| 3 | Owner stores the future-to-job association. | Identity no longer depends on completion or input ordering. |
| 4 | A worker claims the call. | Future becomes running; `cancel()` can no longer prevent execution. |
| 5 | Callable returns or raises. | Future becomes finished with a value or exception. |
| 6 | Owner observes completion through `result`, `wait`, `as_completed`, callback, or map iteration. | A waiting timeout may occur without changing the future. |
| 7 | Owner classifies the terminal outcome and any side effects. | Success, application failure, cancelled, broken pool, or still-running-after-timeout remain distinct. |
| 8 | Owner stops admission and initiates shutdown. | New submissions fail; policy chooses drain, pending cancellation, or explicit escalation. |
| 9 | Workers and resources finish or are escalated deliberately. | No accepted future is silently forgotten; indeterminate work is reported. |

## 5. Additional visual models

### Result order versus completion order

```text
input order:       A          B          C
finish timeline:   |-----A
                   |-B
                   |---C

map() yields:      A, B, C        input order; A can block access to B and C
as_completed():    B, C, A        terminal-completion order; retain ID mapping
```

#### How to read this visual

Read the input row left to right, then compare task lengths on the finish timeline. Finally compare the two collection rows: the work schedule can be identical while the consumer observes results in different orders.

#### Key insight

Execution order, completion order, and result-consumption order are three separate properties.

#### Simplification or limitation

Durations are conceptual and do not promise a scheduler order. Equal-time completions may be observed in either order, and process-map chunking can group several inputs into one submitted unit.

### Timeout ownership

```text
owner:  wait(result, 100 ms) ── TimeoutError ── chooses next policy
worker: [---------------- callable continues ----------------] ── value/exception
side effect:                 [write may already happen]
```

#### How to read this visual

Read the owner and worker lanes over the same wall-clock time. The owner's wait ends at 100 ms; nothing in that event rewinds the worker lane or an already-started side effect.

#### Key insight

A deadline is useful only when the owner defines what happens to late work and the callable has a safe cooperation or containment boundary.

#### Simplification or limitation

The diagram omits pending cancellation, process termination, remote-system timeouts, transactions, retries, and idempotency keys. Those mechanisms change consequences but not the meaning of a future wait timeout.

## 6. Worked examples

### 6.1 Deterministic future lifecycle

The runnable file is [`examples/future_lifecycle.py`](examples/future_lifecycle.py).

```python
with ThreadPoolExecutor(max_workers=1) as executor:
    running = executor.submit(controlled_value, started, release, 21)
    started.wait(TIMEOUT)
    cancelled = executor.submit(identity, 99)
    failed = executor.submit(raise_synthetic_failure)

    running_cancelled = running.cancel()
    queued_cancelled = cancelled.cancel()
    release.set()
```

Prediction before execution:

- the single worker claims `running`, so `running.cancel()` is `False`;
- the second future remains queued and `cancel()` is `True`, so its callable never runs;
- after release, the first result is `21`, then the third callable runs and its `ValueError` is re-raised only when collected;
- the executor context waits for its non-cancelled calls before returning.

Observed result, run with CPython 3.14.4:

```text
running cancel succeeded: False
queued cancel succeeded: True
running result: 21
queued result category: CancelledError
failure: ValueError: synthetic worker failure
```

The example uses events and bounded guard timeouts, not sleeps, to make the pending/running distinction deterministic. It does not claim that arbitrary production scheduling is deterministic.

### 6.2 Completion order and input order

The runnable file is [`examples/completion_order.py`](examples/completion_order.py).

Two thread-pool tasks announce that they started, then wait on separate events. The owner releases `job-b` first and consumes one item from `as_completed()`, then releases `job-a`. A separate `map()` call squares `(3, 1, 2)` and yields `(9, 1, 4)` in input order.

Observed result, run with CPython 3.14.4:

```text
completion order: ('job-b', 'job-a')
map results: (9, 1, 4)
```

The controlled gates expose the collection contract without using task duration as a correctness mechanism. Production code must not assume a finish order unless the business protocol establishes it.

### 6.3 Process-pool batch

The runnable file is [`examples/process_batch.py`](examples/process_batch.py).

```python
context = multiprocessing.get_context("spawn")
with ProcessPoolExecutor(max_workers=2, mp_context=context) as executor:
    summaries = tuple(executor.map(summarize, batches))
```

The target and immutable dataclasses live at importable module scope, and executable printing is under the main guard. `map()` returns summaries in batch input order even though workers may finish in another order. The explicit `spawn` context gives this example stable Python 3.11/3.14 bootstrap semantics instead of inheriting the platform default.

Observed result, run with CPython 3.14.4:

```text
batch-a: count=3, sum_of_squares=14
batch-b: count=2, sum_of_squares=41
batch-c: count=1, sum_of_squares=36
```

This tiny workload is teaching evidence, not a performance recommendation; process startup and transfer dominate work of this size.

### 6.4 Python 3.14 bounded `map`

The runnable file is [`examples/bounded_map.py`](examples/bounded_map.py).

One thread worker blocks on an event while a source records which values the map call consumes. With `buffersize=2`, exactly the first two values are submitted before the owner yields a result and frees buffer capacity. After the release event, all four doubled values are returned in input order.

Observed result, run with CPython 3.14.4:

```text
consumed before release: (0, 1)
results: (0, 2, 4, 6)
```

This demonstrates the public buffer contract for one controlled source. It is not a memory benchmark and does not prove that two is the right production bound.

### 6.5 Debugging example: nested wait

Do not run this unbounded; first identify the wait-for cycle.

```python
from concurrent.futures import ThreadPoolExecutor


executor = ThreadPoolExecutor(max_workers=1)


def outer() -> int:
    inner = executor.submit(pow, 5, 2)
    return inner.result()


print(executor.submit(outer).result())
```

Debugging task:

1. Identify which callable owns the only worker.
2. State which future it waits for and what resource that future needs.
3. Explain why adding a timeout changes the symptom but does not make the dependency valid.
4. Propose an owner-coordinated two-stage design before changing `max_workers`.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| `done()` means success. | The work is no longer pending. | Cancelled futures and exception-bearing futures are also done. | Call `cancelled()` and `result()` on controlled terminal states. |
| A result timeout cancels the call. | The waiting API raises and returns control. | Only the wait ended; the callable may still run and create side effects. | Gate a worker, time out the owner, release it, then retrieve the late result. |
| `cancel()` stops running work. | The method name sounds imperative. | It prevents a call only while still pending and returns a boolean proving whether that succeeded. | Occupy the only worker, then compare cancellation of running and queued futures. |
| `shutdown(wait=False)` lets the program exit immediately. | The method returns immediately. | Executor resources are freed after pending work completes, and Python does not exit while pending futures remain. | Use a controlled gate and observe process lifetime without killing it. |
| `shutdown(cancel_futures=True)` cancels everything. | The flag sounds global. | Only not-yet-running futures are cancelled; running calls finish unless another protocol acts. | Submit one gated running call plus queued calls to a one-worker pool. |
| `FIRST_EXCEPTION` is fail-fast cancellation. | It returns when an exception appears. | It only changes when `wait()` returns; sibling futures continue and must be handled. | Gate siblings, release a failing call, and inspect `not_done`. |
| `as_completed()` preserves input order. | The input is an ordered list. | It yields terminal completions; identity needs a mapping. | Release event-controlled jobs in reverse order. |
| `map()` exposes completion promptly. | Calls execute concurrently. | Results are consumed in input order, so an early slow item causes head-of-line waiting. | Gate the first item while allowing later items to finish. |
| `max_workers` bounds memory. | It bounds concurrently running calls. | Submission can queue many pending calls and retain arguments/results. | Submit from a recording generator and inspect application-owned counts, not private fields. |
| A worker can safely wait on the same executor. | Futures are designed for waiting. | Finite capacity can create a wait-for cycle or starvation. | Draw the resource dependency before running a guarded reproduction. |
| Dropping a future drops the task. | The caller no longer has a handle. | The executor still owns accepted work; its exception may become operationally invisible. | Record a failing call and compare explicit collection with discarded ownership. |
| Switching thread code to a process pool is mechanical. | Both implement `Executor`. | Pickling, imports, start methods, isolation, side effects, and costs change. | Try a lambda, nested function, or non-picklable client under `spawn`. |
| A process future's task exception means the pool is broken. | Both cross a process boundary. | A healthy worker can report an application exception; abrupt worker loss creates `BrokenProcessPool`. | Compare a raised `ValueError` with a controlled abnormal worker exit in a guarded test. |
| `InterpreterPoolExecutor` shares thread globals. | Its workers use threads in one process. | Each worker has an isolated interpreter; mutable runtime state is not shared as ordinary thread state. | Import and mutate module state separately, then pass only serializable values. |
| Completion callbacks always run on a worker. | They are triggered by worker completion. | A callback added after completion can run immediately in the adding thread; the contract is process-oriented, not one specific thread. | Add callbacks before and after a manually completed test future and record thread identity. |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| `submit()` | Amortized queueing plus future allocation | Public API gives no universal queue complexity or memory bound; executor and implementation details differ. |
| `Future.result()` after completion | Constant-time-style state check and value/exception access | Exact locking and callback internals are implementation details. |
| `wait()` / `as_completed()` setup | Proportional to number of distinct futures supplied | Duplicate futures are deduplicated; wakeup and contention costs are runtime-dependent. |
| Thread task handoff | Queueing, synchronization, and context switching | Shared objects avoid mandatory serialization but add synchronization and client-safety concerns. |
| Process task handoff | Serialization, IPC, scheduling, and separate-process memory | Payload size, start method, chunks, imports, and worker reuse can dominate. |
| Interpreter task handoff | Serialization plus isolated-interpreter scheduling | Extension compatibility and interpreter-local imports/state matter; measure the deployed runtime. |
| `ProcessPoolExecutor.map(..., chunksize=k)` | Roughly one submission/transfer per chunk | Larger chunks can reduce overhead but worsen load balance, latency, and per-item failure granularity. |
| `map(..., buffersize=b)` | At most the configured submitted-not-yet-yielded window | It bounds one layer, not total application memory, running workers, or downstream concurrency. |
| Adding workers | Potential overlap or parallel capacity with added resource use | Speedup stops at serial dependencies, the GIL/native boundary, data transfer, contention, bandwidth, or downstream saturation. |

These are cost models, not measurements. A benchmark must record workload, payload distribution, runtime/build, worker count, start context, warm-up, trials, raw observations, and uncertainty.

## 9. Production relevance and trade-offs

### Ownership and API shape

- Give the executor one lifecycle owner; avoid creating a fresh pool per input item or hiding global pools inside libraries.
- Give every accepted job a stable ID and retain its future or terminal record until policy is applied.
- Return domain outcomes from a boundary rather than exposing raw futures in user-facing APIs unless caller-managed concurrency is explicitly the contract.
- Keep orchestration outside workers; workers should transform inputs into bounded values or structured failures.

### Capacity and deadlines

- Set explicit `max_workers`; defaults are version- and environment-dependent and know nothing about downstream limits.
- Bound pending submission separately from worker count and make overload visible.
- Propagate a monotonic application deadline where late work becomes useless; do not confuse that with one local `result(timeout)` call.
- Budget database connections, HTTP pools, file descriptors, memory, CPU, queues, and remote rate limits together.

### Failure and side effects

- Classify validation failure, retryable remote failure, timeout, cancellation, broken executor, and indeterminate worker loss separately.
- Do not retry merely because a caller timed out; the first call may still commit its side effect.
- Use idempotency keys or transactions for externally visible work that may be duplicated after uncertainty.
- Preserve the original exception type and causal context while avoiding sensitive payloads in logs.

### Shutdown

```text
stop admission
      ↓
decide pending policy: drain or cancel
      ↓
signal cooperative stop/deadline to running calls
      ↓
collect every reachable outcome
      ↓
executor shutdown and resource cleanup
      ↓
classify anything still indeterminate
```

Normal context-manager shutdown drains accepted non-cancelled work. Service shutdown often needs an earlier admission gate and application-level deadline so a long call does not make process exit unbounded. Abrupt process termination is a containment escalation, not proof of clean rollback.

### Observability

Record safe metadata such as job ID, executor type, worker name or PID where relevant, queued/running/completed counts, admission wait, execution duration, outcome category, cancellation result, owner timeout, and shutdown phase. Do not log secrets or full payloads merely because work crossed a pool boundary.

Track queueing separately from execution. A “slow future” may have waited for a worker, waited inside a remote call, blocked on a lock, or completed while the owner was delayed by input-ordered collection.

### Portability and maintainability

- Use importable top-level callables and an explicit multiprocessing context for portable process-pool code.
- Keep public example paths Python 3.11-compatible unless the version-specific feature is the teaching target.
- Feature-detect or version-gate `InterpreterPoolExecutor`, `map(buffersize=...)`, and immediate process-worker controls.
- Audit native extensions and clients before interpreter or process migration; a common interface does not prove semantic compatibility.
- Prefer clear owner-side loops over clever callback chains when both satisfy the requirement.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| `concurrent.futures`, `Executor`, thread/process pools, and futures | Standard library | 3.2 | Same core APIs | Not available on WebAssembly platforms documented by the module. |
| `shutdown(cancel_futures=...)` | Standard library | 3.9 | Available unchanged in 3.11 | Cancels pending, not running, futures. |
| `concurrent.futures.TimeoutError` aliases built-in `TimeoutError` | Standard library / Version | 3.11 | Same in the interview baseline | Prefer built-in `TimeoutError` in modern code when no compatibility distinction is needed. |
| `ProcessPoolExecutor(max_tasks_per_child=...)` | Standard library | 3.11 | Same API | Without explicit `mp_context`, using it selects `spawn`; incompatible with `fork`. |
| Thread/process default worker counts use `os.process_cpu_count()` | Standard library / Version | 3.13 | Specify `max_workers` intentionally in 3.11 | Defaults are not capacity planning. |
| `Executor.map(..., buffersize=...)` | Standard library | 3.14 | Maintain an explicit bounded window around `submit()` and `wait()` | Bounds submitted results not yet yielded; `chunksize` remains process-pool-specific. |
| `InterpreterPoolExecutor` and `BrokenInterpreterPool` | Standard library / Version / CPython ecosystem boundary | 3.14 | Use a thread or process pool according to the Python 3.11 workload | Calls and results are pickled; mutable interpreter state is isolated; audit extension support. |
| Process-pool default start method changed away from `fork` | Standard library / Version / Platform | 3.14 | Python 3.11 usually defaults to `fork` on POSIX; pass `mp_context` for stable behavior | Request `fork` explicitly only with a deliberate platform-safe design. |
| `ProcessPoolExecutor.terminate_workers()` and `.kill_workers()` | Standard library / Version / Platform | 3.14 | Use cooperative cancellation and managed process ownership; no direct pool equivalents in 3.11 | These are abrupt containment operations and also initiate shutdown. |
| `max_tasks_per_child` queued-work deadlock fix | CPython maintenance fix | 3.14.7 | Avoid relying on the affected lifecycle; upgrade to a fixed maintenance release | The initialized runtime is 3.14.4, so this edge was source-audited but not claimed as locally verified. |
| `concurrent.futures.Future` is not directly awaitable | Standard-library type boundary | Long-standing | Use event-loop APIs such as `asyncio.wrap_future()` where appropriate | Do not confuse it with `asyncio.Future`; detailed integration belongs to `PY-CON-060`. |

For a Python 3.11 interview, lead with `ThreadPoolExecutor`, `ProcessPoolExecutor`, `submit`, `map`, future state, completion, exceptions, cancellation, and shutdown. Label interpreter pools, map buffering, immediate process-worker controls, and the changed process-start default as Python 3.14 differences.

## 11. Practice brief

Exercises are unsolved in [`practice/README.md`](practice/README.md); hints and comparison solutions remain withheld until an attempt.

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-CON-050-P01` | Predict | 2 | E+D | Controlled future state, timeout, and cancellation trace |
| `PY-CON-050-P02` | Implement | 3 | C+D | Bounded result-owning fan-out with structured outcomes |
| `PY-CON-050-P03` | Debug | 4 | D | Nested-future deadlock and owner-side repair |
| `PY-CON-050-P04` | Implement | 4 | C+D | Input-ordered versus completion-ordered batch API |
| `PY-CON-050-P05` | Design / Review | 4 | E+D | Thread, process, or interpreter executor decision and shutdown review |

## 12. Interview prompts

Attempt one at a time; do not read or write a prepared answer first.

1. Draw the states of a future and explain exactly when `cancel()` can return `True`.
2. `future.result(timeout=0.2)` raised `TimeoutError`. What can the owner conclude, and what can it not conclude?
3. Compare `submit()`, `map()`, `wait()`, and `as_completed()` for ordering, identity, failure, and backpressure.
4. Why can a worker waiting on a future from its own executor deadlock? Give the one-worker proof.
5. A process-pool callable raises `ValueError`. Is the pool broken? How is abrupt worker loss different?
6. What does `shutdown(wait=False, cancel_futures=True)` do to pending, running, and process-exit behavior?
7. How would you bound a million-item input on Python 3.14 and on Python 3.11?
8. Compare thread, process, and interpreter pools for a CPU-heavy pure-Python transform.
9. Why is changing only the executor class insufficient when moving from threads to processes?
10. Design an executor-backed backend fan-out with a request deadline, partial failure, idempotent side effects, and graceful service shutdown.

A strong answer should eventually demonstrate:

- the future state machine, distinct outcome categories, and exact timeout/cancellation boundary;
- submission, completion, input ordering, capacity, deadlock, and shutdown mechanics;
- an executor choice grounded in workload, data ownership, serialization, portability, failure, and measured cost.

## 13. Closed-book revision cues

Without reading the note:

1. Reconstruct the submit-to-terminal-state visual and label where cancellation can succeed.
2. Explain why `done()` is not synonymous with success.
3. Draw separate owner and worker lanes for a result timeout.
4. Compare input order, execution order, completion order, and consumption order.
5. Reconstruct the one-worker nested-future deadlock.
6. State what `shutdown(wait=True, cancel_futures=True)` does to running and pending calls.
7. Give one valid and one invalid workload for each concrete Python 3.14 executor.
8. Explain the Python 3.14 `buffersize` boundary and a Python 3.11 bounded-window alternative.
9. Separate an application exception, `CancelledError`, `TimeoutError`, and `BrokenProcessPool`.
10. Review a fan-out boundary for job identity, admission, deadline, side effects, results, and shutdown.

## 14. Authoritative sources

Only official sources opened and used for this unit are listed.

1. [`concurrent.futures` — Launching parallel tasks](https://docs.python.org/3.14/library/concurrent.futures.html), executor objects, thread/interpreter/process executors, futures, module functions, exceptions, and 3.14.7 maintenance note; Python 3.14.7 documentation, accessed 2026-08-28.
2. [Python 3.11 `concurrent.futures`](https://docs.python.org/3.11/library/concurrent.futures.html), core API and compatibility comparison; Python 3.11.15 documentation, accessed 2026-08-28.
3. [PEP 3148 — futures: execute computations asynchronously](https://peps.python.org/pep-3148/), motivation, interface, and rationale; final standards-track PEP, accessed 2026-08-28.
4. [asyncio Futures](https://docs.python.org/3.14/library/asyncio-future.html), comparison with `concurrent.futures.Future` and `wrap_future()` boundary; Python 3.14.7 documentation, accessed 2026-08-28.
5. [What’s New in Python 3.14 — multiple interpreters](https://docs.python.org/3.14/whatsnew/3.14.html#whatsnew314-multiple-interpreters), interpreter isolation, ecosystem limitations, and `InterpreterPoolExecutor`; Python 3.14.7 documentation, accessed 2026-08-28.

## 15. Durable clarification log

| Date | Clarification | Why it belongs in canonical notes | Source or evidence |
|---|---|---|---|
| 2026-08-28 | A future wait timeout ends only the owner's wait; it neither changes the future to cancelled nor proves the callable stopped. | Timeout and cancellation are routinely conflated, which can duplicate side effects and misclassify late outcomes. | Python 3.14 `Future.result()` and cancellation contracts; `examples/future_lifecycle.py`. |
| 2026-08-28 | `Executor.map(buffersize=N)` bounds submitted results not yet yielded, not the executor's worker count or the application's total resource use. | Treating the new parameter as global backpressure can still overload clients, queues, memory, or downstream services. | Python 3.14 `Executor.map()` contract; `examples/bounded_map.py`. |
| 2026-08-28 | `InterpreterPoolExecutor` uses worker threads but isolated interpreters, serialized call boundaries, and one GIL per interpreter. | Calling it “just a thread pool” hides the mutable-state, import, exception, extension, and communication differences that determine correctness. | Python 3.14 `InterpreterPoolExecutor` reference and What’s New guidance. |
