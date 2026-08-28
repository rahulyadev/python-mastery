# Practice — PY-CON-060 Asyncio event loop, coroutines, tasks, and context

| Field | Value |
|---|---|
| Unit note | [`PY-CON-060`](../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../CURRICULUM.md#py-con-060) |
| Topic branch | `topic/PY-CON-060` |
| Evidence target | E+C+D+X |
| Attempt required before solution | Yes |
| Test command | Define a narrow deterministic command with the first code attempt. |
| Status | Not attempted |

## Practice rules

1. Identify the coroutine owner, Task owner, pending dependency, loop thread, and Context before choosing an API.
2. Predict the event trace and every possible suspension before execution.
3. Preserve the first attempt and first failing deterministic test.
4. Request one progressive hint at a time; hints and comparison solutions are intentionally absent.
5. Do not use arbitrary wall-clock sleeps to establish order; use loop callbacks, Events, Futures, and explicit cooperative checkpoints.
6. Keep a strong reference to every created Task and observe every terminal outcome.
7. Do not inspect private loop queues, Task fields, Future fields, or `_run_once()` for application correctness.
8. Label Python 3.14 eager-start behavior and CPython observations; keep the main implementation Python 3.11-compatible unless the exercise says otherwise.
9. Use only synthetic request IDs, records, callbacks, and failures.
10. Do not push later attempts automatically; keep the topic worktree pinned until publication.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Suggested files | Status |
|---|---|---:|---|---|---|
| `PY-CON-060-P01` | Predict | 2 | Derive direct-await, Task, and completed-Future ordering. | `practice/p01_prediction.md` | Not attempted |
| `PY-CON-060-P02` | Implement | 3 | Adapt a callback source into one loop-owned Future safely. | `practice/p02_callback_adapter.py` and focused tests | Not attempted |
| `PY-CON-060-P03` | Debug | 3 | Separate forgotten coroutine, blocking call, and unobserved Task failure. | `practice/p03_debugging.md` and guarded reproduction | Not attempted |
| `PY-CON-060-P04` | Implement | 3 | Prove request-context capture, isolation, and reset. | `practice/p04_request_context.py` and focused tests | Not attempted |
| `PY-CON-060-P05` | Design / Review | 4 | Define an owned background-task and loop-health boundary. | `practice/p05_design.md` | Not attempted |

## PY-CON-060-P01 — Predict three kinds of await

### Problem

Without executing the program, predict the final `events` tuple. For each `await`, state whether it must suspend, may suspend, or cannot suspend in this particular trace.

```python
import asyncio


async def child(label, events):
    events.append(f"{label}:start")
    await asyncio.sleep(0)
    events.append(f"{label}:resume")
    return label.upper()


async def main():
    events = []

    direct_coroutine = child("direct", events)
    events.append("owner:called-direct")
    direct_result = await direct_coroutine
    events.append(f"owner:direct={direct_result}")

    sibling = asyncio.create_task(child("task", events), name="task-child")
    events.append(f"owner:created-task done={sibling.done()}")
    await asyncio.sleep(0)
    events.append(f"owner:after-turn done={sibling.done()}")
    task_result = await sibling
    events.append(f"owner:task={task_result}")

    loop = asyncio.get_running_loop()
    done = loop.create_future()
    done.set_result("READY")
    loop.call_soon(events.append, "callback:queued")
    events.append(f"owner:future={await done}")
    events.append("owner:after-done-await")
    await asyncio.sleep(0)

    print(tuple(events))


asyncio.run(main())
```

### Learning evidence

- Distinguish coroutine creation from coroutine advancement.
- Explain why direct await uses the current Task.
- Track the sibling Task through two cooperative checkpoints.
- Explain why the completed Future and queued callback have a specific relative order.
- Identify which ordering would change under an eager task factory.

### Constraints

- Do not execute until the complete trace and suspension table are written.
- Do not use private state or disassembly as the first explanation.
- Assume the default non-eager Task factory on CPython 3.14.4.
- After the first prediction, mark which parts are public contracts and which exact interleavings are implementation observations.

### Required edge cases

- Replace the done Future with one completed by `call_soon()`.
- Directly await a coroutine that returns before reaching any await.
- Create the sibling under Python 3.14 `eager_start=True`.
- Have the child raise before its first suspension.
- Attempt to await the already-completed coroutine object a second time.

### Acceptance criteria

- [ ] Every event is ordered before execution.
- [ ] “Contains `await`” is not treated as “must switch Tasks.”
- [ ] Direct composition and independent task lifetime are distinguished.
- [ ] The completed Future's repeated outcome is explained.
- [ ] Version-specific eager behavior is labelled.
- [ ] Actual output is recorded only after the prediction.

### Learner attempt

- Predicted event tuple:
- Suspension table:
- Current Task at each child call:
- Public contracts:
- CPython/default-loop assumptions:
- Command:
- Observed output:
- First incorrect assumption after review:

## PY-CON-060-P02 — Implement a callback-to-Future adapter

### Problem

Implement a Python 3.11-compatible adapter:

```python
async def lookup_record(register, key: str) -> Record:
    ...
```

`register(key, on_value, on_error)` belongs to a supplied synthetic callback library. It returns an `unsubscribe()` callable. The library may invoke exactly one callback normally, but the test double can expose library bugs: duplicate value, value followed by error, callback after unsubscribe, or callback from a foreign thread.

The adapter must create its Future through the running loop, return one immutable `Record`, translate one expected source error without losing its cause, and ensure every callback that touches loop-owned state runs on the loop thread. It must unregister on every exit path. A late or duplicate signal must not turn into `InvalidStateError` in the loop's exception handler.

### Learning evidence

- Show why a Future is appropriate at this low-level boundary but should not escape the public API.
- Separate producer completion from consumer awaiting.
- Define exactly-once terminal ownership despite a buggy callback source.
- Cross a foreign-thread boundary through a documented loop API.
- Prove cleanup and terminal observation with deterministic tests.

### Constraints

- Standard library only; main path runs on Python 3.11 and 3.14.
- Use `asyncio.get_running_loop()` and `loop.create_future()`.
- No `time.sleep()`, polling, global loop, private Future state, or raw cross-thread `set_result()`.
- Do not expose the Future from `lookup_record()`.
- Preserve a stable synthetic key but do not log record payloads.
- Keep cancellation semantics limited to cleanup and classification; detailed cancellation policy belongs to `PY-CON-070`.

### Required edge cases

- Synchronous callback during `register()` before it returns.
- Callback scheduled later on the loop thread.
- Callback from one foreign thread.
- Expected source error.
- Unexpected exception raised by `register()`.
- Duplicate value callback.
- Value followed by error.
- Awaiting owner exits before a late callback.
- `unsubscribe()` itself raises during cleanup.

### Acceptance criteria

- [ ] Every Future mutation occurs on the owning loop thread.
- [ ] Exactly one terminal value or exception reaches the awaiter.
- [ ] Duplicate/late callbacks are safely classified and do not corrupt the loop.
- [ ] Unsubscribe is attempted exactly once on every relevant path.
- [ ] The public result is a domain value, not a Future.
- [ ] Tests use Events/callback control rather than timing guesses.
- [ ] The learner explains the remaining cancellation limitation.

### Learner attempt

- Adapter state model:
- Loop-thread boundary:
- Duplicate-signal policy:
- Cleanup invariant:
- Attempt files:
- Test command:
- Observed result:
- Remaining uncertainty:

## PY-CON-060-P03 — Debug three independent async failures

### Problem

Find the first observable symptom and the underlying ownership error for each marked line before proposing changes:

```python
import asyncio
import time


async def audit(event: str) -> None:
    await asyncio.sleep(0)
    raise ValueError(f"audit rejected: {event}")


def blocking_read(record_id: str) -> str:
    time.sleep(1)
    return f"record:{record_id}"


async def handle(record_id: str) -> str:
    audit("request-started")                         # A
    background = asyncio.create_task(audit("done")) # B
    del background
    value = blocking_read(record_id)                # C
    return value


asyncio.run(handle("synthetic-7"), debug=True)
```

### Learning evidence

- Distinguish a never-awaited coroutine object from a scheduled Task.
- Explain how the blocking call affects the loop and when the scheduled Task can first run.
- Trace who could observe the background exception and why deleting the local name is not a policy.
- Separate diagnostic warnings from correctness repairs.
- Propose the smallest owned design before choosing an offload mechanism.

### Constraints

- The first response contains diagnosis and a timeline only, not replacement code.
- Do not suppress warnings, catch `Exception` broadly, add sleeps, or keep a meaningless global list forever.
- Do not assume `asyncio.run()` waits for arbitrary background Tasks as successful work.
- If reproducing, use synthetic data and a bounded outer test process.
- Keep structured cancellation and shutdown details as an explicit handoff to `PY-CON-070`.

### Required edge cases

- `audit()` succeeds instead of failing.
- `blocking_read()` raises immediately.
- `blocking_read()` returns only after the background Task becomes ready.
- A strong reference is retained but the Task is never awaited.
- The process has a long-lived runner instead of exiting after one request.
- Debug mode is disabled.

### Acceptance criteria

- [ ] A, B, and C are three distinct defects rather than one “async issue.”
- [ ] Warning timing is not confused with defect creation time.
- [ ] The loop-thread stall is explained without claiming CPU parallelism.
- [ ] Task lifetime and exception ownership are explicit.
- [ ] The proposed API boundary remains testable and bounded.

### Learner attempt

- Timeline before execution:
- Defect A:
- Defect B:
- Defect C:
- First warning or exception expected:
- Repair ownership model:
- Reproduction command:
- Observed diagnostics:

## PY-CON-060-P04 — Implement isolated request context

### Problem

Implement:

```python
async def run_request(
    request_id: str,
    steps: tuple[AsyncStep, ...],
) -> tuple[StepObservation, ...]:
    ...
```

A module-level `ContextVar[str]` stores the current request ID for logging. `run_request()` binds one synthetic ID, creates one owned Task per supplied step, collects observations in input order, and restores the caller's previous binding on every exit. Each step sets a temporary span ID, suspends through a test-controlled Event, and reports the request/span bindings before and after suspension.

Run two `run_request()` calls concurrently under different IDs. Neither request nor span binding may bleed into the other request or into the test Task after completion.

### Learning evidence

- Identify the exact task-creation point at which Context is captured.
- Use Token reset as a lexical cleanup invariant.
- Prove bindings survive suspension but child changes do not rewrite the parent.
- Demonstrate the shallow-copy limitation with a separate mutable-value test.
- Keep security/business arguments explicit rather than reading them from ambient context.

### Constraints

- Standard library only and Python 3.11-compatible main implementation.
- Declare ContextVar keys at module scope.
- Use `try/finally` with `reset()`; do not rely on Python 3.14 Token context-manager syntax in the main path.
- No global mutable “current request” dictionary, `threading.local()`, or private Task context fields.
- Use Events to control suspension and interleaving.
- Do not place secrets, user data, or authorization results in the synthetic context.

### Required edge cases

- No prior request binding.
- An outer caller already has a binding.
- Empty steps.
- Two requests with identical step names.
- One step changes its span binding twice.
- One step raises after suspension.
- A child Task is created before the parent updates the binding.
- A ContextVar value is a shared mutable list.
- An explicit empty `contextvars.Context()` is passed to one Task.

### Acceptance criteria

- [ ] Both concurrent request IDs remain isolated across controlled interleavings.
- [ ] Every Token is reset in the Context where it was created.
- [ ] Caller context is identical before and after the operation.
- [ ] Input ordering is explicit and not inferred from completion order.
- [ ] The mutable-value test explains binding isolation versus object sharing.
- [ ] Failure evidence remains observable to the Task owner.

### Learner attempt

- Context tree before execution:
- Binding/reset invariant:
- Task creation points:
- Attempt files:
- Test command:
- Observed result:
- Mutable-value conclusion:
- Remaining uncertainty:

## PY-CON-060-P05 — Review a background refresh boundary

### Scenario

A backend process owns one asyncio loop. Each request checks a cache. On a miss, the handler launches `asyncio.create_task(refresh(key))` and returns stale data. `refresh()` calls a synchronous SDK, uses a ContextVar containing a mutable request metadata dictionary, and emits completion through a library callback that may originate on a worker thread. No Task reference is retained. During deployment shutdown, the runner closes immediately after the server stops accepting requests.

Review the design before writing code. Produce:

1. an ownership table for the loop, request Task, refresh Task, SDK call, callback registration, Context binding, result, exception, and shutdown action;
2. a timeline for cache miss, response return, refresh success/failure, and process shutdown;
3. the first boundary that can block the loop;
4. the exact strong-reference and exception-observation design;
5. a Context policy that keeps safe tracing metadata without sharing the mutable request dictionary;
6. a thread-to-loop callback handoff;
7. the questions deferred to `PY-CON-070` and `PY-CON-080`.

### Learning evidence

- Explain why returning the request response does not settle the refresh Task.
- Separate loop scheduling, blocking offload, callback adaptation, Context, and durable side-effect policy.
- Define observability for queueing, execution, result category, and shutdown.
- State what can be guaranteed before structured cancellation/backpressure is designed.
- Reject “fire and forget” as an ownership description.

### Constraints

- Do not solve overload by creating one thread or executor per refresh.
- Do not claim that cancelling an asyncio waiter kills a running SDK call.
- Do not mutate a loop Future directly from the SDK callback thread.
- Do not keep entire request/customer objects in Context.
- Do not assume a done callback automatically makes exceptions handled.
- Keep all example data synthetic.

### Required edge cases

- Refresh completes before the handler returns.
- Refresh fails after the handler returns.
- Two requests miss the same key.
- The SDK blocks longer than the deployment grace period.
- Callback arrives after the Future/Task owner has exited.
- Callback fires twice.
- Task registry cleanup callback itself fails.
- Process receives shutdown with no refreshes, one pending refresh, and many refreshes.

### Acceptance criteria

- [ ] Every accepted refresh has one named owner and terminal record.
- [ ] Loop-thread blocking and foreign-thread mutation are both removed from the design.
- [ ] Context data is immutable/minimal or copied by an explicit policy.
- [ ] Duplicate refresh and duplicate callback policies are explicit.
- [ ] Shutdown questions are honest rather than hidden behind runner close.
- [ ] Follow-up work is routed to the correct canonical units.

### Learner attempt

- Ownership table:
- Timeline:
- First invalid assumption:
- Task registry and failure policy:
- Context policy:
- Thread-to-loop handoff:
- Deferred `PY-CON-070` questions:
- Deferred `PY-CON-080` questions:
- Remaining uncertainty:

## Evidence record

Update only after real attempts and review.

| Exercise | Attempt artifact | Deterministic command | Observed result | Review date | Weakest point | State evidence |
|---|---|---|---|---|---|---|
| `PY-CON-060-P01` | — | — | — | — | — | — |
| `PY-CON-060-P02` | — | — | — | — | — | — |
| `PY-CON-060-P03` | — | — | — | — | — | — |
| `PY-CON-060-P04` | — | — | — | — | — | — |
| `PY-CON-060-P05` | — | — | — | — | — | — |
