# Practice — PY-CON-070 Structured concurrency, cancellation, and timeouts

| Field | Value |
|---|---|
| Unit note | [`PY-CON-070`](../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../CURRICULUM.md#py-con-070) |
| Topic branch | `topic/PY-CON-070` |
| Evidence target | E+C+D+X |
| Attempt required before solution | Yes |
| Test command | Define one narrow deterministic command with the first code attempt. |
| Status | Not attempted |

## Practice rules

1. Name the owner, child tasks, structured scope, cancellation source, timeout boundary, and cleanup obligations before choosing an API.
2. Predict the terminal state of every task and every escaping exception before execution.
3. Preserve the first attempt and first failing deterministic test.
4. Request one progressive hint at a time; hints and comparison solutions are intentionally absent.
5. Use `asyncio.Event`, controlled callbacks, and zero-delay checkpoints instead of arbitrary wall-clock sleeps for ordering tests.
6. Re-raise `CancelledError` after cleanup unless the exercise explicitly establishes a rare suppression policy and explains `uncancel()`.
7. Keep a strong reference to every task outside a `TaskGroup`, and observe every terminal outcome.
8. Do not use `shield()` to detach work whose owner, result observer, or shutdown path is undefined.
9. Use synthetic identifiers and failures only; do not copy production data or incidents.
10. Do not push later attempts automatically; keep the topic worktree pinned until publication.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Suggested files | Status |
|---|---|---:|---|---|---|
| `PY-CON-070-P01` | Predict | 3 | Trace TaskGroup failure, sibling cancellation, cleanup, and group exit. | `practice/p01_prediction.md` | Not attempted |
| `PY-CON-070-P02` | Implement | 4 | Build a request-wide deadline around a structured fan-out. | `practice/p02_deadline_batch.py` and focused tests | Not attempted |
| `PY-CON-070-P03` | Debug | 4 | Repair swallowed cancellation and unowned shielding. | `practice/p03_debugging.md` and guarded reproduction | Not attempted |
| `PY-CON-070-P04` | Implement / Classify | 4 | Route expected leaves from nested exception groups without losing unexpected failures. | `practice/p04_exception_routing.py` and focused tests | Not attempted |
| `PY-CON-070-P05` | Design / Review | 5 | Define graceful async-service shutdown and bounded cleanup ownership. | `practice/p05_shutdown_review.md` | Not attempted |

## PY-CON-070-P01 — Predict one failing structured scope

### Problem

Without running this program, write the event partial order, the terminal state of each task, and the exception observed outside the `TaskGroup`:

```python
import asyncio


class Rejected(Exception):
    pass


async def wait_forever(label, started, events):
    events.append(f"{label}:start")
    started.set()
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        events.append(f"{label}:cancel")
        raise
    finally:
        events.append(f"{label}:cleanup")


async def reject(a_started, b_started, events):
    await a_started.wait()
    await b_started.wait()
    events.append("reject:raise")
    raise Rejected("synthetic")


async def main():
    events = []
    a_started = asyncio.Event()
    b_started = asyncio.Event()
    try:
        async with asyncio.TaskGroup() as group:
            a = group.create_task(wait_forever("a", a_started, events))
            b = group.create_task(wait_forever("b", b_started, events))
            failed = group.create_task(reject(a_started, b_started, events))
            events.append("owner:created")
    except* Rejected as errors:
        events.append(f"owner:handled={len(errors.exceptions)}")

    print(tuple(events))
    print(a.cancelled(), b.cancelled(), failed.cancelled())


asyncio.run(main())
```

### Learning evidence

- Distinguish a required partial order from an incidental sibling-cancellation order.
- Explain why group exit cannot finish before both sibling cleanup blocks finish.
- Explain why the failing task is done-with-exception rather than cancelled.
- Explain why the owner receives an exception group even with one matching failure leaf.
- Identify what changes if either sibling suppresses `CancelledError` and never terminates.

### Required edge cases

- A sibling raises a different exception while processing cancellation.
- The `async with` body itself raises before all children start.
- The owner task is externally cancelled while a child fails.
- Both failure tasks raise before TaskGroup processes either completion.
- One child returns successfully before the failure.

### Acceptance criteria

- [ ] Every task has a named owner and terminal state.
- [ ] Only documented ordering is asserted by tests.
- [ ] `CancelledError` leaves are not treated as ordinary group failures.
- [ ] Cleanup completion precedes the event after the group.
- [ ] The learner distinguishes task failure from owner cancellation.

### Learner attempt

- Required partial order:
- Incidental order:
- Task terminal states:
- Escaping exception shape:
- First incorrect assumption after review:
- Command and observed result, only after prediction:

## PY-CON-070-P02 — Implement one end-to-end deadline

### Problem

Implement:

```python
async def load_dashboard(
    load_profile,
    load_permissions,
    load_messages,
    *,
    deadline: float,
) -> Dashboard:
    ...
```

`deadline` is an absolute value from the running event loop's monotonic clock. The three supplied asynchronous callables must run concurrently as one owned operation. If the deadline expires, incomplete siblings must be cancelled and awaited, cleanup must finish, and the public boundary must raise one domain-specific `DashboardDeadlineExceeded` chained from `TimeoutError`. If a child fails normally, preserve the structured failure rather than mislabelling it as a deadline.

### Learning evidence

- Use `asyncio.timeout_at()` as one scope budget rather than resetting a full relative timeout for each child.
- Use `TaskGroup` so child lifetime cannot outlive the function.
- Collect successful task results only after the group exits.
- Translate only the timeout owned by this API boundary.
- Prove cleanup and absence of leaked tasks with deterministic tests.

### Constraints

- Python 3.11-compatible standard library only.
- No `asyncio.gather(..., return_exceptions=True)`, polling, arbitrary sleeps, or private Task state.
- Do not catch `BaseException` or flatten unexpected exception groups into strings.
- Do not retry inside the same expired budget.
- Task names must reveal role but contain no sensitive data.

### Required edge cases

- All three children succeed before the deadline.
- Deadline is already in the past.
- One child raises an expected domain error.
- One child raises unexpectedly while another is in cleanup.
- The owner is externally cancelled before the deadline.
- Cleanup itself fails.
- Empty messages result is valid and must not be confused with timeout.

### Acceptance criteria

- [ ] One absolute deadline bounds the whole operation.
- [ ] No child remains live after return or raise.
- [ ] External cancellation remains cancellation.
- [ ] Timeout translation preserves `__cause__`.
- [ ] Child failure is not converted to a timeout.
- [ ] Tests control readiness through Events or Futures.
- [ ] The result assembly order is explicit.

### Learner attempt

- Scope tree:
- Deadline owner:
- Exception translation table:
- Cleanup invariant:
- Attempt files:
- Test command and result:
- Remaining uncertainty:

## PY-CON-070-P03 — Debug swallowed cancellation and shielding

### Problem

Diagnose before editing:

```python
import asyncio


async def persist_audit(record):
    await send_to_remote_service(record)


async def worker(queue):
    while True:
        try:
            record = await queue.get()
            await handle(record)
        except asyncio.CancelledError:
            continue
        finally:
            queue.task_done()


async def handler(record):
    asyncio.create_task(asyncio.shield(persist_audit(record)))
    return {"accepted": True}
```

Find the first missing reasoning step for each defect. Define intended delivery semantics before proposing replacement code.

### Learning evidence

- Explain why continuing after `CancelledError` can prevent a `TaskGroup` or shutdown owner from finishing.
- Separate the queue accounting bug from cancellation handling.
- Explain why `shield()` does not provide ownership, a strong reference, exception observation, or process-lifetime durability.
- Distinguish “finish this cleanup before propagating cancellation” from “ignore shutdown forever.”
- Choose a bounded owner appropriate to best-effort or durable audit delivery.

### Required edge cases

- Cancellation arrives while blocked in `queue.get()`.
- Cancellation arrives after `get()` but before `handle()` completes.
- `handle()` raises before acknowledgement.
- The audit coroutine fails after the response is returned.
- A second cancellation arrives during cleanup.
- Process shutdown begins immediately after handler return.

### Acceptance criteria

- [ ] Every acquired queue item has exactly one acknowledgement policy.
- [ ] Cancellation reaches the owning scope after bounded cleanup.
- [ ] Audit lifetime, result observation, retry, and shutdown are explicit.
- [ ] `shield()` is used only if its narrow propagation semantics are required.
- [ ] No infinite loop or broad handler erases cancellation state.

### Learner attempt

- Defect timeline:
- Cancellation owner:
- Queue invariant:
- Audit delivery contract:
- Why shield is or is not required:
- Smallest repair after diagnosis:

## PY-CON-070-P04 — Route exception-group leaves

### Problem

Build a classifier for a structured fan-out in which children may raise `MissingRecord`, `InvalidRecord`, or unexpected exceptions. Handle the two expected domain types separately with `except*`, preserve nested group structure for diagnostics, and let every unhandled leaf continue to propagate.

Your tests must construct both a real TaskGroup failure and a deliberately nested `ExceptionGroup`. They must not depend on two event-loop tasks failing in one particular scheduling order.

### Learning evidence

- Treat an exception group as a tree whose leaves are matched by type.
- Explain how each `except*` clause receives a matching subgroup rather than one ordinary exception.
- Preserve traceback, cause, context, and unhandled subgroups.
- Avoid assuming a flat `.exceptions` tuple.
- Define which domain failures can be combined into one public response and which must abort it.

### Required edge cases

- One naked expected exception handled by `except*`.
- A nested group with both expected types.
- An unexpected `RuntimeError` leaf.
- A group containing only one expected leaf.
- A handler that raises a new exception.
- Attempting to mix `except` and `except*` in one `try` statement.

### Acceptance criteria

- [ ] Expected leaves are classified without string parsing.
- [ ] Unhandled leaves still propagate.
- [ ] Nested structure is not destructively flattened.
- [ ] Tests do not rely on a race to manufacture multiple failures.
- [ ] Syntax and control-flow limits of `except*` are explained.

### Learner attempt

- Exception tree:
- Matching table:
- Public error policy:
- Attempt files:
- Test command and result:
- Unexpected leaf proof:

## PY-CON-070-P05 — Review graceful shutdown ownership

### Scenario

A synthetic service accepts requests, starts per-request child tasks, consumes a queue, writes telemetry, and holds database connections. On shutdown it stops accepting work, waits for some operations, cancels others, and closes resources. The current design stores all Tasks in one global set and calls `cancel()` without awaiting them.

Write a design review and a small state machine. Do not write the full service.

### Learning evidence

- Define nested ownership scopes for service, worker pool, request, and resource lifetime.
- Separate admission stop, drain deadline, cancellation request, cleanup wait, and terminal reporting.
- Define which failures become exception groups and where they are classified.
- Bound cleanup without silently abandoning task exceptions.
- Identify what survives process loss and therefore needs durable infrastructure rather than an in-memory Task.

### Required decisions

- What stops accepting new work?
- Which owner cancels request tasks and queue workers?
- Which clock/deadline is propagated?
- How are repeated shutdown signals handled?
- What happens when cleanup raises?
- Which telemetry is best-effort, and which data must be durably persisted?
- How is shutdown tested without wall-clock guesses?

### Acceptance criteria

- [ ] Every Task belongs to exactly one meaningful lifetime owner.
- [ ] Every cancellation request is followed by terminal observation.
- [ ] Drain and hard-stop deadlines are distinct.
- [ ] Resource closure follows child termination in the correct direction.
- [ ] Failure reporting retains grouped causes.
- [ ] The design states its durability limit.
- [ ] The test plan covers simultaneous failure and cancellation.

### Learner attempt

- Ownership tree:
- Shutdown state machine:
- Deadline propagation:
- Failure policy:
- Cleanup order:
- Durability boundary:
- Test plan:
