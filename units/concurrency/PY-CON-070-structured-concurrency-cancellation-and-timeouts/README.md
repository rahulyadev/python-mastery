# PY-CON-070 — Structured concurrency, cancellation, and timeouts

[Curriculum entry](../../../CURRICULUM.md#py-con-070) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-CON-070`

## Physical Notebook Core

### Problem this concept solves

Concurrent child tasks can otherwise outlive the operation that created them, fail without an observer, keep resources open, or continue after their result is useless. An asynchronous operation needs one visible lifetime boundary that owns its children, stops siblings when the operation can no longer succeed, waits for cleanup, and reports every relevant failure.

### One-sentence mental model

> A structured async scope is a parent-owned nursery: every child finishes inside the scope, while failure, cancellation, and deadlines flow down as stop requests and return up only after child cleanup reaches a terminal state.

### One important visual

```text
owner Task enters scope
        |
        +-- child A ---------------------- success --------+
        +-- child B ---- raises Error ----X                 |
        +-- child C ---- waits -------- cancel -> cleanup --+
        |                                                   |
        +<-- scope requests sibling cancellation -----------+
        +<-- scope awaits every child terminal state --------+
        |
        +-- exit raises ExceptionGroup(Error)

scope exit invariant: no child created by this scope is still running
```

#### How to read this visual

Start at the owner and follow the three child lifetimes from left to right. Child B fails first. The structured scope then asks unfinished siblings to stop, but it does not jump directly to the owner. It waits while child C processes cancellation and cleanup. Only after every child is terminal does the owner cross the scope boundary and receive the grouped failure.

#### Key insight

Cancellation is part of failure containment, not an instant kill. The scope's safety comes from owning both the cancellation request and the subsequent wait for terminal cleanup.

#### Simplification or limitation

The picture shows one ordinary child failure and one cancellation wave. It omits body exceptions, external owner cancellation, simultaneous or nested failures, `KeyboardInterrupt`/`SystemExit`, repeated cancellation, eager task start, cleanup failure, and timeout translation. Sibling cleanup order is deliberately unspecified.

### Governing rules or invariants

1. Every concurrent Task needs a lifetime owner that retains it and observes its terminal value, exception, or cancellation.
2. A successfully exited `TaskGroup` has awaited every child created in that group; no group child remains live beyond the boundary.
3. The first non-cancellation child failure prevents normal group success: unfinished siblings are cancelled, awaited, and relevant failures are raised together.
4. `Task.cancel()` requests cancellation; `CancelledError` is delivered at a later opportunity, so blocked loop-thread code and non-cooperative cleanup can delay termination.
5. Cleanup normally belongs in `finally` or an asynchronous context manager; if `CancelledError` is caught, propagate it again after cleanup unless a rare, explicit suppression contract also repairs cancellation state.
6. `asyncio.timeout()` cancels its current Task and translates the cancellation it owns into `TimeoutError` only outside the timeout context.
7. A deadline is an absolute end-to-end budget. Reapplying a fresh relative timeout at every nested operation can accidentally exceed the caller's intended budget.
8. `shield()` changes one cancellation-propagation edge; it does not invent ownership, retain a Task, observe failures, or make work durable across process exit.

### Minimal example

```python
import asyncio


class InvalidRecord(Exception):
    pass


async def validate() -> None:
    await asyncio.sleep(0)
    raise InvalidRecord("synthetic record")


async def wait_for_dependency() -> None:
    try:
        await asyncio.Event().wait()
    finally:
        print("dependency cleanup")


async def main() -> None:
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(validate())
            group.create_task(wait_for_dependency())
    except* InvalidRecord as failures:
        print(f"handled leaves: {len(failures.exceptions)}")


asyncio.run(main())
```

Expected reasoning:

1. Both children belong to the lexical `TaskGroup`; leaving the `async with` body begins a wait for their terminal outcomes.
2. `validate()` raises a non-cancellation exception, so the group cancels the waiting sibling.
3. The sibling's `finally` runs before the group can finish closing.
4. The owner handles a matching subgroup with `except*`; it does not receive a naked `InvalidRecord` merely because there is one leaf.
5. No Task created by the group remains running after the handler executes.

### One failure or misconception

**Mistake:** “A timeout raises `TimeoutError` inside the slow coroutine, and cancellation immediately stops it.”

**Correction:** `asyncio.timeout()` first cancels the current Task. Inner code encounters `CancelledError` at a cooperative boundary and unwinds through cleanup. The timeout manager recognizes its own cancellation at context exit and then exposes `TimeoutError` outside the scope. Slow or cancellation-suppressing code can delay that outcome.

### Important trade-offs

- `TaskGroup` gives failure containment and bounded child lifetime, but one ordinary child failure cancels siblings even when partial success might have business value.
- Exception groups preserve concurrent failures and tracebacks, but callers must classify a tree of leaves rather than assume one flat exception.
- End-to-end deadlines bound obsolete work, but aggressive budgets can trigger expensive cancellation and cleanup under load.
- `shield()` can protect a narrowly owned cleanup or commit step from one caller's cancellation, but it can also make shutdown and latency harder to bound.
- Cooperative cancellation makes cleanup possible, but it cannot preempt blocking code running on the event-loop thread.

### Interview-revision cues

- Reconstruct: owner scope → child failure → sibling cancellation request → cleanup → grouped failure.
- Distinguish: failure, cancellation, timeout, deadline, and process termination.
- Predict: `TaskGroup` versus `gather()`, `timeout()` versus `wait_for()`, and ordinary await versus `shield()`.
- Diagnose: swallowed `CancelledError`, fresh nested timeouts, unawaited cancelled Tasks, indefinite cleanup, and flattened exception groups.
- Design: propagate one absolute deadline, name the cancellation owner, and define which cleanup is bounded, retryable, idempotent, or durable.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Concurrency, parallelism, and asynchronous Python |
| Canonical ID | `PY-CON-070` |
| Learning outcome | Apply structured concurrency, `TaskGroup`, cancellation, timeouts, exception groups, and cancellation-safe cleanup. |
| Hard prerequisites | `PY-CON-060`, `PY-ERR-020` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D3 |
| Scope | Standard library |
| Size | L |
| Evidence profile | E+C+D+X |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4, regular GIL-enabled build, Linux x86_64 |
| Last source audit | 2026-08-28 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. draw a lifetime tree for an asynchronous operation and assign every Task to one owner;
2. use `asyncio.TaskGroup` for structured fan-out and predict success, child-failure, body-failure, and external-cancellation exit behavior;
3. explain cancellation as a cooperative request, preserve `CancelledError`, and implement cleanup whose ownership and termination policy are explicit;
4. apply `asyncio.timeout()` and `timeout_at()` as scope budgets while distinguishing them from `wait_for()` and from independent external cancellation;
5. classify `ExceptionGroup` and `BaseExceptionGroup` leaves with `except*` without discarding unexpected failures or nested structure;
6. decide when `gather()` or `shield()` has the required narrower semantics and state the ownership they do not provide;
7. test failure and cancellation deterministically without depending on wall-clock races or private event-loop state.

Required evidence:

- reconstruct the core visual and narrate failure/cancellation propagation without reading;
- complete the prediction, deadline, debugging, exception-routing, and shutdown-design practice while preserving first attempts;
- run and explain the TaskGroup, timeout-budget, and cancellation-cleanup examples with deterministic tests;
- reproduce and classify the timeout-cancellation provenance experiment on a recorded runtime;
- review one backend async boundary for task ownership, deadline propagation, failure grouping, cleanup bounds, observability, and durability.

Initialization created source-audited material, runnable examples, deterministic tests, and one interpreted experiment. It did not create learner attempts, recall, or transfer evidence, so the learning state remains `Not started` and the artifact remains `Draft`.

## 2. Prerequisite bridge

The tracker records both hard prerequisites as `Not started`; the `PY-ERR-020` artifact is absent. These minimum bridges make this unit usable without pretending either prerequisite is complete.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-CON-060` — Asyncio event loop, coroutines, tasks, and context | Cancellation is delivered through Task advancement, and structured concurrency owns Tasks rather than abstract background work. | A coroutine runs inside a Task until it returns, raises, or suspends on an awaitable. One event-loop thread advances ready Tasks cooperatively. Creating a Task creates a lifetime and terminal outcome that some owner must retain and observe. |
| Hard | `PY-ERR-020` — Custom exceptions, chaining, warnings, and exception groups | Concurrent children can fail independently, so one control-flow boundary may need to preserve more than one exception. | Exceptions propagate with traceback, cause, and context. `ExceptionGroup` is a tree of exception leaves. `except* SomeType` receives the matching subgroup, while unmatched leaves continue to propagate. |

Recommended follow-up: study both prerequisites in their dedicated topic chats. Continue here by treating the bridges as explicit assumptions rather than evidence of completion.

## 3. Vocabulary and professional English

### Structured

| Item | Content |
|---|---|
| Pronunciation | STRUK-cherd |
| Simple English meaning | Organized so relationships and boundaries are visible. |
| Hindi cue | स्पष्ट ढाँचे और सीमा वाला |
| Meaning in this Python context | Child Task lifetimes are nested inside an owner scope that waits for their terminal states. |

Natural examples:

1. The structured scope owns all three lookups.
2. The child cannot silently outlive its request boundary.
3. Structured lifetime does not mean every child must return the same type.
4. **Interview:** A TaskGroup is structured because group exit joins the children it owns.
5. **Engineering discussion:** Move this fan-out under the request's structured scope so shutdown has one place to observe it.

### Cancellation

| Item | Content |
|---|---|
| Pronunciation | kan-suh-LAY-shun |
| Simple English meaning | A request to stop work that is no longer wanted. |
| Hindi cue | काम रोकने का अनुरोध |
| Meaning in this Python context | A Task receives `CancelledError` at a cooperative execution opportunity and may run cleanup before terminating. |

Natural examples:

1. Cancellation arrived while the worker awaited the queue.
2. The owner waited for cancellation cleanup to finish.
3. Blocking code delayed cancellation delivery.
4. **Interview:** `cancel()` requests cancellation; it does not prove that the Task is already cancelled.
5. **Engineering discussion:** Preserve external cancellation instead of converting every exit into a service timeout.

### Deadline

| Item | Content |
|---|---|
| Pronunciation | DED-line |
| Simple English meaning | The absolute time by which work must stop waiting. |
| Hindi cue | अंतिम समय-सीमा |
| Meaning in this Python context | A value on the event loop's monotonic clock that lets nested work share one remaining time budget. |

Natural examples:

1. The request deadline is earlier than the database client's default timeout.
2. Each child receives the same absolute deadline.
3. The remaining budget shrinks while upstream work runs.
4. **Interview:** Resetting a five-second timeout in three layers can violate one five-second request deadline.
5. **Engineering discussion:** Propagate the deadline, then derive a smaller local limit only when the dependency needs one.

### Propagate

| Item | Content |
|---|---|
| Pronunciation | PROP-uh-gayt |
| Simple English meaning | Pass an effect onward through connected layers. |
| Hindi cue | आगे पहुँचाना |
| Meaning in this Python context | Allow a value, exception, cancellation, or deadline to cross the correct ownership boundary without being erased or misclassified. |

Natural examples:

1. The child propagates cancellation after closing its resource.
2. Unhandled leaves propagate out of the `except*` statement.
3. The API propagates one absolute deadline to nested calls.
4. **Interview:** Catching `CancelledError` for cleanup does not justify preventing it from propagating.
5. **Engineering discussion:** Translate the owned timeout here, but propagate shutdown cancellation to the service runner.

## 4. Deep explanation

### 4.1 Why structured concurrency exists

Unstructured task creation splits control flow from lifetime. A function can create a Task, return, lose the handle, and leave later failure or cleanup to an unrelated loop shutdown. The code that starts concurrent work no longer visibly owns when it ends.

Structured concurrency restores a tree: a parent operation opens a scope, starts related children inside it, and cannot successfully leave until those children are terminal. This is analogous to ordinary function calls staying inside a call stack, but it supports concurrent child lifetimes and grouped failures.

The standard library describes `TaskGroup` as an asynchronous context manager that retains related tasks and awaits all of them on exit. This lifetime guarantee—not shorter syntax—is the central feature. See [`asyncio.TaskGroup`](https://docs.python.org/3.14/library/asyncio-task.html#task-groups).

### 4.2 TaskGroup entry, success, and failure

An entered TaskGroup is active. `group.create_task()` schedules a child and returns its Task handle. Code may pass the group to an active child and add further tasks while the group is still open. After the last child finishes and `__aexit__()` completes, new children cannot be added.

On normal exit, the group waits for every child and returns only when all completed successfully. Task results can then be read from retained handles with `result()` because their terminal success is established.

On the first child exception other than `CancelledError`, the group:

1. stops accepting new tasks;
2. requests cancellation of unfinished siblings;
3. if necessary, interrupts the Task still executing the `async with` body so it reaches group exit;
4. waits for all children, including their cleanup;
5. raises remaining non-cancellation failures in `ExceptionGroup` or `BaseExceptionGroup` as appropriate.

If the `async with` body itself raises, the body exception participates in the same shutdown and grouping rules unless it is cancellation. `KeyboardInterrupt` and `SystemExit` receive special treatment: siblings are still cancelled and awaited, then the original base exception is re-raised rather than wrapped as an ordinary group. Nested TaskGroups distinguish their internal wake-up cancellation from external requests, and Python 3.13 improved simultaneous-cancellation handling and preservation of `Task.cancelling()` counts. See the exact [TaskGroup failure contract](https://docs.python.org/3.14/library/asyncio-task.html#task-groups).

Do not infer a deterministic order among sibling cancellation handlers. The contract is terminal containment, not a global ordering of every ready callback.

### 4.3 Cancellation is a protocol, not termination

`Task.cancel(message)` returns whether the request was accepted. It arranges for `CancelledError` to be thrown into the coroutine at a later loop opportunity. If the Task is awaiting a Future, that dependency is also cancelled through the Task machinery. A coroutine running blocking or CPU-heavy code on the loop thread cannot receive cancellation until control returns to the loop.

`CancelledError` has directly inherited from `BaseException` since Python 3.8. Therefore an ordinary `except Exception` normally does not swallow it. The documentation recommends `try/finally` for cleanup and says that an explicitly caught cancellation should almost always be re-raised when cleanup finishes. Structured components such as TaskGroup and timeout scopes use cancellation internally and can misbehave when application code erases it. See [Task cancellation](https://docs.python.org/3.14/library/asyncio-task.html#task-cancellation) and [`asyncio.CancelledError`](https://docs.python.org/3.14/library/asyncio-exceptions.html#asyncio.CancelledError).

These Task states are distinct:

| Observation | Meaning |
|---|---|
| `task.cancel()` returned `True` | A cancellation request was scheduled; the Task may still be running. |
| `task.cancelling() > 0` | The Task has outstanding cancellation requests minus `uncancel()` calls. |
| Awaiting the Task raised `CancelledError` | Cancellation propagated to this observer. |
| `task.cancelled() is True` | The wrapped coroutine did not suppress cancellation and the Task terminated as cancelled. |
| Task returned a value after catching cancellation | The coroutine suppressed cancellation; this needs an explicit, rare contract. |

`Task.uncancel()` is not a routine cleanup tool. If code truly suppresses `CancelledError`, the documentation requires removal of the associated cancellation state as well, but ordinary application design should propagate instead. A loop that catches cancellation and continues can keep its TaskGroup, timeout manager, or shutdown owner waiting indefinitely.

### 4.4 Timeout scopes and absolute deadlines

`asyncio.timeout(delay)` and `asyncio.timeout_at(when)` were added in Python 3.11. Both return asynchronous context managers. The relative form computes a local duration; the absolute form uses the running loop's monotonic clock. Timeout objects can be inspected, rescheduled, and safely nested.

When a timeout expires, it cancels the current Task. Inner code therefore encounters `CancelledError`. At context exit, the manager recognizes the cancellation associated with its own scope and translates it to built-in `TimeoutError`. That exception can be caught outside, not inside, the context. See the [`asyncio` timeout contract](https://docs.python.org/3.14/library/asyncio-task.html#timeouts).

```python
loop = asyncio.get_running_loop()
deadline = loop.time() + 0.250

try:
    async with asyncio.timeout_at(deadline):
        await perform_owned_operation()
except TimeoutError:
    handle_owned_deadline_expiry()
```

An absolute deadline composes better across layers:

```text
request starts with deadline D
  authentication consumes time
  service receives the same D
  database adapter computes max(0, D - loop.time())
  response serialization still shares D
```

If every layer instead grants itself a fresh 250 milliseconds, a nominal 250-millisecond request can wait several multiples of that amount. A local dependency timeout can still be smaller than the remaining request budget, but it should not extend the parent deadline.

`asyncio.wait_for(awaitable, seconds)` places a timeout around one awaitable. On expiry it cancels that awaitable and waits until cancellation completes, so elapsed time may exceed the requested duration. Wrapping the awaitable in `shield()` prevents that particular cancellation propagation. Since Python 3.11, `wait_for()` raises built-in `TimeoutError`. Scope timeouts are usually clearer when several awaits and child tasks form one operation. See [`asyncio.wait_for()`](https://docs.python.org/3.14/library/asyncio-task.html#asyncio.wait_for).

### 4.5 Exception groups and `except*`

Concurrent operations can produce multiple failures before containment completes: two children may fail close together, or a child failure may be followed by cleanup failure. Losing all but one exception hides causality. Python 3.11 added exception groups to carry a tree of independent failures with their tracebacks.

`ExceptionGroup` inherits from `Exception` and can contain only `Exception` instances. `BaseExceptionGroup` inherits from `BaseException` and can also contain base exceptions; its constructor automatically yields the narrower `ExceptionGroup` when all leaves are ordinary exceptions. See [built-in exception groups](https://docs.python.org/3.14/library/exceptions.html#exception-groups).

`except* SomeError` recursively selects the matching subgroup. Unmatched leaves continue to later `except*` clauses and ultimately propagate if unhandled. The handler receives a group even when only one leaf matches. Treat it as a tree rather than flattening messages or assuming `.exceptions` contains only leaf exceptions.

```python
try:
    async with asyncio.TaskGroup() as group:
        ...
except* MissingRecord as missing_group:
    record_expected_absence(missing_group)
except* InvalidRecord as invalid_group:
    record_validation_failures(invalid_group)
```

A single `try` statement may use `except` clauses or `except*` clauses, not both. `except*` requires an exception type; it cannot target `ExceptionGroup` itself; and `break`, `continue`, and `return` cannot appear in its handler suite. See the [`except*` language reference](https://docs.python.org/3.14/reference/compound_stmts.html#except-star) and [PEP 654](https://peps.python.org/pep-0654/).

Avoid converting a whole group to one generic HTTP error without policy. First classify which leaves are expected domain outcomes, which indicate dependency failure, which are bugs, and which must propagate to crash or restart the owning component.

### 4.6 TaskGroup, `gather()`, and `shield()` solve different problems

`asyncio.gather()` concurrently awaits a fixed collection and returns results in input order. With default `return_exceptions=False`, it propagates the first observed exception immediately but does not cancel the other submitted awaitables; they continue. Cancelling the gather object itself cancels unfinished submitted awaitables. TaskGroup instead makes sibling cancellation and terminal containment part of its child-failure contract. See [`asyncio.gather()`](https://docs.python.org/3.14/library/asyncio-task.html#asyncio.gather).

Use gather when its exact result aggregation and non-fail-fast sibling semantics are intentional and every continuing Task remains owned. Do not choose it merely because it is familiar.

`asyncio.shield(awaitable)` prevents cancellation of the caller from being forwarded through that await edge to the shielded Task. The caller still receives `CancelledError`. Direct cancellation of the inner Task still cancels it. The caller must retain a strong Task reference, define who later awaits it, and decide what shutdown does with it. See [`asyncio.shield()`](https://docs.python.org/3.14/library/asyncio-task.html#shielding-from-cancellation).

Shielding is sometimes useful for a short, already-owned operation whose interruption would violate an invariant. It is not a durability mechanism: process exit, interpreter failure, or host termination still destroys in-memory work.

### 4.7 Cancellation-safe cleanup

The smallest correct pattern is usually ordinary exception-safe cleanup:

```python
async def use_connection(pool):
    connection = await pool.acquire()
    try:
        return await query(connection)
    finally:
        await pool.release(connection)
```

When the awaited query receives cancellation, the `finally` suite begins before the saved `CancelledError` is re-raised. An await inside cleanup can itself be interrupted by another cancellation request or fail normally. Therefore production cleanup should have explicit properties:

- bounded: it cannot wait forever during shutdown;
- idempotent where retry or repeated shutdown is possible;
- ordered: children stop using a resource before its owner closes it;
- observable: cleanup failure is recorded without silently replacing every original cause;
- honest about durability: remote commit uncertainty may require reconciliation, not shielding alone.

Asynchronous context managers are often clearer because acquisition and release share one lexical owner. TaskGroup should usually be nested inside the resource scope when children use that resource, so group exit joins children before the outer resource closes.

```python
async with connection_pool() as pool:
    async with asyncio.TaskGroup() as group:
        for item in items:
            group.create_task(process(pool, item))
# all children terminal before pool.__aexit__ completes
```

Do not indiscriminately wrap cleanup in an unbounded shield. If cleanup must continue after caller cancellation, create and retain an owned Task, shield only the necessary await edge, await or otherwise observe the Task through a defined shutdown path, and impose a deliberate bound. Repeated cancellation and process loss remain separate risks.

### 4.8 Execution sequence

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Owner enters TaskGroup | Group active; no children yet |
| 2 | Owner creates children | Group retains Task handles; children scheduled |
| 3 | One child raises a non-cancellation exception | Failing child done; group begins failure containment |
| 4 | Group calls `cancel()` on unfinished siblings | Cancellation requested; siblings may still be running |
| 5 | Siblings receive `CancelledError` at cooperative boundaries | Cleanup and propagation execute inside each Task |
| 6 | Every child reaches a terminal state | Group has success, failure, and cancellation outcomes |
| 7 | Group forms the applicable exception group | Non-cancellation failures and possibly body failure retained |
| 8 | Owner crosses `async with` boundary | No group child remains live; grouped failure propagates |
| 9 | Matching `except*` clauses split the failure tree | Handled leaves consumed; unmatched leaves continue outward |

## 5. Additional visual models

### Ownership tree and resource direction

```text
service scope
├── database-pool resource
│   └── request TaskGroup
│       ├── profile child
│       ├── permissions child
│       └── messages child
└── shutdown controller

shutdown direction: controller -> request owner -> children
cleanup direction: children terminal -> request exits -> pool closes
```

#### How to read this visual

Read downward to see ownership and cancellation authority. Then read the cleanup line from left to right: a parent resource stays available until all children that use it are terminal.

#### Key insight

The nesting order of context managers encodes resource lifetime. Closing the pool before joining children reverses the dependency and creates cleanup races.

#### Simplification or limitation

The tree shows one request and one process-local pool. Real services have many requests, admission control, queues, signals, multiple pools, durable work, and hard-stop policies. Those capacity and backpressure details continue in `PY-CON-080` and `PY-SEC-070`.

### Timeout translation boundary

```text
outside timeout scope
        |
        v
async with timeout_at(D):
    inner await -----------------------------+
        ^                                    |
        |                                    v
        +--- CancelledError <--- deadline cancels current Task
                 |
                 +--- finally / __aexit__ cleanup
                 |
scope exit recognizes owned cancellation
        |
        +--- raises TimeoutError outside
```

#### How to read this visual

Follow the deadline arrow into the current Task, then follow `CancelledError` through inner cleanup toward context exit. The exception name changes only after the timeout manager handles the cancellation associated with its own deadline.

#### Key insight

Timeout is implemented through cancellation but has a distinct public meaning at the owning boundary.

#### Simplification or limitation

The picture omits external cancellation racing with the deadline, nested timeout ownership, cancellation suppression, repeated `cancel()`, cleanup failure, and `wait_for()` cancelling a separate awaited Task.

## 6. Worked examples

### 6.1 Small example — child failure closes the whole group

[`examples/taskgroup_failure.py`](examples/taskgroup_failure.py) starts two waiting siblings, lets a validator fail only after both have reached their wait points, and records cleanup before the owner handles the failure.

Prediction before execution:

- `owner:tasks-created` appears before child code because default task creation schedules the children for later execution;
- both waiting workers start before the validator raises;
- neither worker reaches its normal finish event;
- each worker records cancellation before its own cleanup;
- both cleanup events precede `owner:caught-rejection`;
- relative cancellation order between `cache` and `profile` is not a correctness requirement.

Observed result on CPython 3.14.4:

```text
failures: ('synthetic record rejected',)
cancelled tasks: ('cache', 'profile')
owner:tasks-created
cache:start
profile:start
validator:start
validator:raise
profile:cancelled
profile:cleanup
cache:cancelled
cache:cleanup
owner:caught-rejection
owner:after-group
```

The focused tests assert only required partial-order relationships, not the observed sibling cancellation order.

### 6.2 Realistic backend example — one budget for a fan-out

[`examples/timeout_budget.py`](examples/timeout_budget.py) exposes a reusable boundary:

```python
async def fetch_batch(fetch_one, record_ids, *, timeout_seconds):
    tasks = {}
    try:
        async with asyncio.timeout(timeout_seconds):
            async with asyncio.TaskGroup() as group:
                for record_id in record_ids:
                    tasks[record_id] = group.create_task(
                        fetch_one(record_id), name=f"fetch:{record_id}"
                    )
    except TimeoutError as error:
        raise BatchDeadlineExceeded(record_ids) from error

    return {key: task.result() for key, task in tasks.items()}
```

Why this design fits:

- the timeout owns the entire fan-out rather than granting a full new duration to every child;
- TaskGroup prevents any fetch from outliving `fetch_batch()`;
- results are read only after successful group exit;
- the public exception identifies the domain boundary and preserves `TimeoutError` as its cause;
- ordinary child failures are not caught by the timeout handler unless the timeout scope itself produced the `TimeoutError` outcome.

Production refinements include passing an absolute deadline, reserving cleanup time, defining partial-result policy, bounding concurrency, redacting Task names, and mapping exception groups without hiding unexpected failures. Backpressure and capacity limits belong to `PY-CON-080`.

### 6.3 Explicit cancellation and cleanup

[`examples/cancellation_cleanup.py`](examples/cancellation_cleanup.py) starts one owned worker, waits until it reaches a controlled suspension point, requests cancellation with a synthetic message, and awaits the Task.

Observed result on CPython 3.14.4:

```text
cancel request accepted: True
cancellation message: 'synthetic shutdown'
cleanup completed: True
task cancelled: True
cancellation count: 1
worker:start
owner:cancel-requested
worker:cancelled
worker:cleanup-start
worker:cleanup-done
owner:cancel-observed
```

The trace proves that accepted request, delivered exception, cleanup completion, owner observation, and terminal cancelled state are separate events. The single awaited cleanup checkpoint completes because no second cancellation arrives; this is not a guarantee against repeated shutdown requests.

### 6.4 Debugging example

Keep the correction hidden until the learner attempts it:

```python
async def worker():
    while True:
        try:
            await next_job()
        except asyncio.CancelledError:
            log.info("shutdown requested")
            continue


async def run():
    async with asyncio.TaskGroup() as group:
        group.create_task(worker())
        group.create_task(failing_child())
```

Before editing, answer:

1. Which Task owns `worker()`?
2. What action does the group take after `failing_child()` raises?
3. Which exact line prevents the worker from reaching a cancelled terminal state?
4. Why can group exit now wait forever?
5. What cleanup must occur before cancellation is propagated?

### 6.5 Runtime experiment

[`EXP-01 — Timeout cancellation provenance`](experiments/EXP-01-timeout-cancellation-provenance/README.md) compares an expired zero-duration timeout with an external cancellation inside `timeout(None)`. On CPython 3.14.4, the owned timeout restored the pre-scope cancellation count and exposed `TimeoutError` only after cleanup; external cancellation remained `CancelledError` and left its child Task cancelled.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| Treating `cancel()` as synchronous termination | The method name sounds imperative | It requests later `CancelledError` delivery and returns before cleanup necessarily finishes | Gate the worker with an Event; inspect state before and after awaiting it |
| Swallowing `CancelledError` in a broad retry loop | Cancellation resembles a transient operation failure | Cancellation is an ownership signal; cleanup then propagate unless suppression is explicitly designed | Put the worker in a TaskGroup with a failing sibling and prove group exit hangs |
| Catching `TimeoutError` inside `asyncio.timeout()` | The public outcome is called a timeout | Inner code initially sees cancellation; translation occurs at context exit | Record exception types inside and outside a zero-duration scope |
| Converting external cancellation to a domain timeout | Both paths use Task cancellation internally | Translate only the timeout owned by this boundary; external cancellation must stay cancellation | Cancel a Task inside `timeout(None)` and inspect the owner outcome |
| Giving every nested call a fresh relative timeout | Each call appears independently bounded | Repeated budgets can add up; propagate one absolute deadline | Use a fake loop clock or injected deadline calculation across three layers |
| Assuming TaskGroup raises the first naked child error | Only one failure is common | Non-cancellation failures cross the group as `ExceptionGroup`/`BaseExceptionGroup` | Fail one child and inspect the caught `except*` target type |
| Flattening `.exceptions` into strings | Logging a list feels simple | Groups can be nested and carry tracebacks, cause, context, and notes | Construct a nested ExceptionGroup and route by leaf type |
| Assuming sibling cancellation order | One observed loop trace looks stable | TaskGroup promises containment, not application-level ordering among cleanup handlers | Assert partial orders only and vary task creation/readiness |
| Using `gather()` as a drop-in TaskGroup | Both run awaitables concurrently | Default gather propagates one failure without cancelling other awaitables | Gate two gather children and fail a third; observe continuing work under an owner |
| Using `shield()` as fire-and-forget | The inner Task survives caller cancellation | Shield alters propagation only; ownership, reference, observation, and durability remain unsolved | Drop the strong reference or let the inner task fail after caller cancellation |
| Closing a resource before children stop | Parent shutdown feels urgent | Children must become terminal before their shared resource closes | Make child cleanup access a synthetic resource that records close order |
| Assuming cleanup always completes after first cancellation | `finally` has started | A second cancellation or cleanup exception can interrupt or replace the outcome | Inject another `cancel()` after a cleanup-start Event |
| Treating timeout as precise wall-clock completion | A duration looks like a hard stopwatch | Cancellation delivery and cleanup can make observed return later than the deadline | Make cancellation cleanup wait on a controlled Event |
| Catching `Exception` to handle shutdown | Most failures inherit from Exception | `CancelledError` inherits directly from BaseException | Assert exception hierarchy and run an ordinary broad handler |
| Calling `uncancel()` after every caught cancellation | It appears to reset the Task | It is for rare intentional suppression; routine code should re-raise | Compare `cancelling()` and terminal state with propagation versus suppression |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| Create one TaskGroup child | O(1) bookkeeping plus Task allocation | Implementation constants and custom task factories vary |
| Retain `n` group children | O(n) live Task references | Child coroutine frames and referenced application state usually dominate memory |
| Normal group exit | O(n) terminal observation | Actual time is bounded by the slowest unfinished child and its cleanup |
| Failure cancellation wave | O(k) cancellation requests for `k` unfinished children | Termination latency depends on cooperative suspension and cleanup, not only request count |
| Build/format a group with `e` failure leaves | O(e) traversal, plus nested structure and traceback cost | Do not flatten merely to reduce apparent complexity |
| `except*` type routing | Proportional to visited group nodes/leaves | Exact implementation is version-dependent; reason about tree traversal, not bytecode |
| Deadline calculation with `loop.time()` | O(1) | Clock lookup cost is negligible relative to I/O but not a latency guarantee |
| Timeout expiry | Timer scheduling plus cancellation and cleanup | End-to-end return may occur after the nominal deadline |
| `shield()` | One wrapper/await relationship | Inner Task lifetime and memory continue until another owner observes it |

These are structural cost models, not measured benchmarks. This unit records no throughput, latency, allocation, or cancellation-speed claim.

## 9. Production relevance and trade-offs

### API boundaries

Translate only errors owned by the boundary. A request handler may convert its own expired budget to a domain deadline error, but it should not mislabel service shutdown cancellation or an unexpected child failure. Preserve causes when translating.

### Observability

Name Tasks by role using synthetic or non-sensitive identifiers. Log scope, deadline, cancellation source, cleanup duration, and grouped failure types without dumping payloads. Do not log every sibling `CancelledError` as an independent incident when it is the expected consequence of one root failure.

### Graceful shutdown

A safe shutdown sequence normally stops admission, establishes a drain deadline, waits for accepted work, requests cancellation of the remainder, observes all terminal outcomes, and then closes shared resources. Repeated signals need an explicit escalation policy rather than arbitrary repeated `cancel()` calls.

### Database and remote side effects

Cancellation does not roll back an external side effect automatically. A database driver, HTTP request, or message broker may have committed remotely even when the local Task is cancelled. Use transactions, idempotency keys, reconciliation, or durable queues based on the system contract. Shielding cannot prove remote outcome.

### Partial success

TaskGroup is fail-fast for ordinary child failures. If the business operation accepts partial results, encode expected absence or rejection as values, or catch narrowly inside children and return typed outcomes. Do not erase programmer errors by turning every exception into a result.

### Testing

Use Events and Futures to place tasks at exact lifecycle points. Assert ownership, terminal state, cleanup, propagated exception types, cause chains, and absence of live children. Treat sibling trace ordering as incidental unless the program introduces an explicit synchronization relation.

### Security and resource exhaustion

Structured lifetime prevents forgotten children but does not limit how many children are created. Pair TaskGroup with admission control, bounded queues, semaphores, pools, payload limits, and propagated deadlines. Those backpressure mechanisms continue in `PY-CON-080` and `PY-SEC-070`.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| `asyncio.TaskGroup` | Standard library | 3.11 | Same API | Core structured-scope code in this unit is 3.11-compatible |
| `asyncio.timeout()`, `Timeout`, and `timeout_at()` | Standard library | 3.11 | Same API | Timeout scopes safely nest and use the event loop clock |
| `ExceptionGroup`, `BaseExceptionGroup`, and `except*` | Language / built-ins | 3.11 | Same syntax and types | `except*` changes grammar and matches subgroups by leaf type |
| `wait_for()` raises built-in `TimeoutError` | Standard library version change | 3.11 | On older versions account for `asyncio.TimeoutError` | `asyncio.TimeoutError` is an alias of built-in `TimeoutError` from 3.11 |
| `CancelledError` directly subclasses `BaseException` | Standard library hierarchy | 3.8 | Same on Python 3.11 | Ordinary `except Exception` does not catch it |
| Inactive `TaskGroup.create_task()` closes the supplied coroutine | Standard library version change | 3.13 | Avoid creating for an inactive group; close explicitly if ownership was already acquired | Do not depend on 3.13 cleanup behavior in 3.11-only code |
| Improved simultaneous internal/external cancellation handling and correct count preservation in TaskGroup | Standard library version change | 3.13 | Keep designs simple and test 3.11 cancellation races explicitly | Public change note; do not infer identical edge traces across versions |
| TaskGroup forwards all `create_task()` keyword arguments to the loop; `eager_start` is accepted | Standard library version change | 3.14 | Use only `name` and `context` on 3.11 | Eager entry can change reentrancy and event order |
| Observed sibling cancellation order in the example | CPython/default-loop observation | CPython 3.14.4 run | Do not require any exact sibling order | Tests assert only synchronization-derived partial order |
| Timeout experiment restored cancellation count `0 -> 0` | CPython runtime observation consistent with public timeout behavior | CPython 3.14.4 run | Re-run on Python 3.11 and with nested/external cancellation | Not a universal claim for every simultaneous-cancellation scenario |

> **Python 3.14 canonical form**
> TaskGroup may accept current task-creation keyword options such as `eager_start`, but prefer the simplest structured creation compatible with the intended deployment range.

> **Python 3.11-compatible form**
> The central APIs—TaskGroup, timeout scopes, exception groups, and `except*`—are already present. Avoid 3.13 inactive-group cleanup assumptions and 3.14 task-creation keyword forwarding.

## 11. Practice brief

The unsolved work area is [`practice/README.md`](practice/README.md).

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-CON-070-P01` | Predict | 3 | TaskGroup partial order, cancellation, cleanup, and grouped failure | `practice/p01_prediction.md` |
| `PY-CON-070-P02` | Implement | 4 | Absolute deadline, structured fan-out, translation, and deterministic tests | `practice/p02_deadline_batch.py` |
| `PY-CON-070-P03` | Debug | 4 | Swallowed cancellation, queue invariants, and shield ownership | `practice/p03_debugging.md` |
| `PY-CON-070-P04` | Implement / Classify | 4 | Nested exception-group routing with unexpected-leaf propagation | `practice/p04_exception_routing.py` |
| `PY-CON-070-P05` | Design / Review | 5 | Graceful shutdown ownership, bounds, observability, and durability | `practice/p05_shutdown_review.md` |

No solution files are initialized. Preserve the first attempt and reveal hints one at a time.

## 12. Interview prompts

Ask one at a time and require prediction before repair:

1. What guarantee does TaskGroup provide that a set of Tasks plus `gather()` does not automatically provide?
2. A child fails while its sibling is in `finally`. When may the owner receive the exception group?
3. Why is `task.cancel()` not proof that `task.cancelled()` is already true?
4. Where can `TimeoutError` from `asyncio.timeout()` be caught, and what exception does inner cleanup see?
5. Why should a request propagate an absolute deadline rather than give every dependency a fresh relative timeout?
6. How does `except* ValueError` behave when a nested ExceptionGroup contains both `ValueError` and `RuntimeError` leaves?
7. When is gather's decision not to cancel siblings after one failure useful rather than dangerous?
8. What exactly does shield protect, and which ownership problems remain?
9. How would you test a second cancellation arriving during asynchronous cleanup?
10. Design shutdown order for request Tasks sharing a connection pool.

A strong answer should eventually demonstrate:

- a lifetime tree with explicit owner and terminal containment;
- cancellation request, delivery, cleanup, propagation, and terminal-state distinctions;
- timeout provenance and deadline composition;
- exception-group tree routing without loss of unexpected leaves;
- production trade-offs involving partial results, bounded cleanup, remote side effects, observability, and durability.

## 13. Closed-book revision cues

Without reading the note:

1. Draw the owner/three-child failure visual and label the scope-exit invariant.
2. List TaskGroup behavior for normal exit, child failure, body failure, owner cancellation, and `KeyboardInterrupt`.
3. Explain five distinct moments from `cancel()` call to `task.cancelled() is True`.
4. Draw the timeout translation boundary and say where each exception type appears.
5. Compare `timeout()`, `timeout_at()`, and `wait_for()` in one sentence each.
6. Explain why exception groups are trees and what happens to unmatched leaves after `except*`.
7. State two valid reasons to choose gather and two ownership duties it does not remove.
8. State the narrow promise of shield and four things it does not provide.
9. Reconstruct correct resource nesting when children share a pool.
10. Review a synthetic request fan-out for deadline reset, cancellation suppression, cleanup bounds, and leaked Tasks.

## 14. Authoritative sources

Important claims are cited near their explanations. Sources actually read for this initialization:

1. [Python 3.14 Coroutines and Tasks](https://docs.python.org/3.14/library/asyncio-task.html), Task cancellation, Task groups, gather, shield, timeouts, wait-for, and Task state; Python 3.14.7 documentation, accessed 2026-08-28.
2. [`asyncio.CancelledError`](https://docs.python.org/3.14/library/asyncio-exceptions.html#asyncio.CancelledError), hierarchy and propagation guidance; Python 3.14.7 documentation, accessed 2026-08-28.
3. [Built-in exception groups](https://docs.python.org/3.14/library/exceptions.html#exception-groups), `ExceptionGroup`/`BaseExceptionGroup` contracts and hierarchy; Python 3.14.7 documentation, accessed 2026-08-28.
4. [`except*` clause](https://docs.python.org/3.14/reference/compound_stmts.html#except-star), subgroup matching and syntax/control-flow restrictions; Python 3.14.7 Language Reference, accessed 2026-08-28.
5. [PEP 654 — Exception Groups and `except*`](https://peps.python.org/pep-0654/), rationale, tree model, matching, and forbidden combinations; accessed 2026-08-28.
6. [Python 3.11 Coroutines and Tasks](https://docs.python.org/3.11/library/asyncio-task.html), interview-compatibility baseline for TaskGroup, cancellation, timeouts, and waiting primitives; Python 3.11.15 documentation, accessed 2026-08-28.

## 15. Durable clarification log

| Date | Clarification | Why it belongs in canonical notes | Source or evidence |
|---|---|---|---|
| 2026-08-28 | `asyncio.timeout()` exposes `TimeoutError` only after its context handles the cancellation it owns; inner code sees `CancelledError`. | Prevents incorrect catch placement and prevents external shutdown cancellation from being mislabelled as timeout. | Official timeout contract and [`EXP-01`](experiments/EXP-01-timeout-cancellation-provenance/README.md) |
| 2026-08-28 | TaskGroup safety includes waiting for cancelled siblings to finish cleanup before group failure crosses the boundary. | The missing wait step is the source of many leaked-task and premature-resource-close designs. | Official TaskGroup contract and [`taskgroup_failure.py`](examples/taskgroup_failure.py) |
| 2026-08-28 | Shield changes cancellation propagation through one await; it does not establish Task ownership or durability. | Prevents “fire-and-forget” misuse during request completion and shutdown. | Official shield contract |
