# Practice — PY-CON-050 Futures and executors

| Field | Value |
|---|---|
| Unit note | [`PY-CON-050`](../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../CURRICULUM.md#py-con-050) |
| Topic branch | `topic/PY-CON-050` |
| Evidence target | E+C+D |
| Attempt required before solution | Yes |
| Test command | Define a narrow deterministic command with the first code attempt. |
| Status | Not attempted |

## Practice rules

1. Record the future state, job owner, capacity owner, and expected terminal category before choosing an API.
2. Predict order and cancellation results before execution.
3. Preserve the original attempt and the first failing deterministic test.
4. Request one progressive hint at a time; hints and comparison solutions are intentionally absent.
5. Do not use arbitrary sleeps to prove ordering, pending state, timeout, cancellation, or deadlock; use events, barriers, controlled callables, or manual test futures.
6. A bounded test timeout is a guard, not proof that running work was cancelled.
7. Never inspect private executor queues, worker sets, or future state strings for application correctness.
8. Handle every accepted future; do not suppress an exception merely to make shutdown pass.
9. Use synthetic inputs and side effects only.
10. Do not push later attempts automatically; keep the topic worktree pinned until publication.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Suggested files | Status |
|---|---|---:|---|---|---|
| `PY-CON-050-P01` | Predict | 2 | Derive running, pending, timeout, cancellation, and terminal states in a controlled trace. | `practice/p01_prediction.md` | Not attempted |
| `PY-CON-050-P02` | Implement | 3 | Build bounded fan-out that owns identity, values, failures, deadlines, and shutdown. | `practice/p02_fanout.py` and focused tests | Not attempted |
| `PY-CON-050-P03` | Debug | 4 | Diagnose and repair a nested-future deadlock from the wait-for graph. | `practice/p03_deadlock.py` and focused tests | Not attempted |
| `PY-CON-050-P04` | Implement | 4 | Expose explicit input-ordered and completion-ordered batch modes. | `practice/p04_ordered_batch.py` and focused tests | Not attempted |
| `PY-CON-050-P05` | Design / Review | 4 | Select and operate a thread, process, or interpreter executor for a backend boundary. | `practice/p05_design.md` | Not attempted |

## PY-CON-050-P01 — Predict a controlled future lifecycle

### Problem

Without executing the program, predict every printed line and classify both futures immediately before and after `release.set()`.

```python
from concurrent.futures import CancelledError, ThreadPoolExecutor
from threading import Event

started = Event()
release = Event()


def controlled(value):
    started.set()
    release.wait()
    return value


with ThreadPoolExecutor(max_workers=1) as executor:
    first = executor.submit(controlled, 10)
    started.wait()
    second = executor.submit(controlled, 20)

    print(first.cancel())
    print(second.cancel())

    try:
        first.result(timeout=0)
    except TimeoutError:
        print("owner timed out")

    release.set()
    print(first.result())

    try:
        second.result()
    except CancelledError:
        print("second cancelled")
```

### Learning evidence

- Separate pending, running, cancelled, and finished-with-value states.
- Explain why the zero-duration wait is deterministic after `started` is set and before `release`.
- State which callable executes and which never begins.
- Explain why the timeout changes only the owner lane.

### Constraints

- Do not execute until the full trace and state table are recorded.
- Do not refer to a private future attribute or CPython queue implementation.
- Do not change worker count, add sleeps, or remove the timeout.
- After prediction, add one done callback and predict which thread *may* run it without assuming one exact thread identity.

### Required edge cases

- Call `cancel()` on `first` again after it returns.
- Call `done()` after the timeout but before release.
- Call `result()` twice after successful completion.
- Replace the controlled return with a deterministic `ValueError`.
- Add the callback only after the future is already complete.

### Acceptance criteria

- [ ] Both cancellation booleans are justified from public state.
- [ ] Timeout, cancellation, success, and exception are distinct categories.
- [ ] `done()` is not treated as synonymous with success.
- [ ] Repeated result retrieval is explained without rerunning the callable.
- [ ] The observed output is recorded only after the prediction.

### Learner attempt

- State table before release:
- Printed-line prediction:
- Owner timeout meaning:
- Callable execution count:
- Command:
- Observed output:
- First incorrect assumption after review:

## PY-CON-050-P02 — Implement a bounded fan-out owner

### Problem

Implement:

```python
run_checks(
    jobs,
    check,
    *,
    max_workers,
    max_in_flight,
    deadline,
) -> tuple[Outcome, ...]
```

Each synthetic job has a stable `job_id` and immutable payload. `check(job)` is a supplied blocking callable that either returns an immutable value or raises an application exception. The function must use `ThreadPoolExecutor`, never keep more than `max_in_flight` accepted but uncollected futures, and return one immutable outcome per input in input order.

The owner may collect futures in completion order internally, but it must reconstruct input order explicitly. When the monotonic deadline expires, stop accepting new jobs, attempt to cancel every still-pending future, cooperatively notify running checks through a learner-designed mechanism, collect all outcomes reachable within the cleanup budget, and mark any still-running call as late rather than claiming it stopped.

### Learning evidence

- Separate worker count from in-flight admission.
- Preserve job identity across completion order.
- Convert expected application failures into explicit outcomes without suppressing unexpected owner bugs.
- Treat a deadline, successful pending cancellation, and a late running call as different terminal reports.
- Own executor shutdown on every path.

### Constraints

- Standard library only and Python 3.11-compatible public API.
- Validate `max_workers > 0`, `max_in_flight >= max_workers`, unique IDs, and a monotonic deadline before submission.
- No arbitrary sleeps, daemon threads, private executor fields, or unbounded `list(executor.map(...))`.
- Do not create one executor per job.
- Do not retry side effects automatically.
- Tests supply event-controlled callables and a fake or injectable monotonic clock where useful.
- Preserve original exception type and safe message; never store a traceback with sensitive payload data in the domain outcome.

### Required edge cases

- Empty input.
- Fewer jobs than workers.
- More jobs than the in-flight bound.
- Duplicate job ID.
- One successful call, one `ValueError`, and later successful calls.
- Deadline before any submission.
- Deadline while one call is running and another is pending.
- Pending cancellation loses a race with worker start.
- Result arrives after the owner's original wait timed out.
- Shutdown begins while the producer still has unsubmitted input.

### Acceptance criteria

- [ ] The maximum accepted/uncollected count is proved by a deterministic test.
- [ ] Every accepted ID has exactly one owner-visible outcome.
- [ ] Returned tuple is input-ordered even when completion is reversed.
- [ ] No wait timeout is reported as successful cancellation.
- [ ] All reachable exceptions are collected and classified.
- [ ] Executor ownership and shutdown behavior are documented.
- [ ] The learner explains why `max_workers` alone is not backpressure.

### Learner attempt

- State and outcome model:
- Admission invariant:
- Deadline and cooperation protocol:
- Attempt files:
- Test command:
- Observed result:
- Remaining uncertainty:

## PY-CON-050-P03 — Debug a nested-future deadlock

### Problem

Find the first invalid capacity assumption before proposing a fix:

```python
from concurrent.futures import ThreadPoolExecutor


def enrich(record, executor):
    validated = executor.submit(validate, record)
    stored = executor.submit(store, validated.result())
    return stored.result()


def run(records):
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(enrich, record, executor)
            for record in records
        ]
        return [future.result() for future in futures]
```

Assume there are at least two records, `validate()` and `store()` terminate when they run, and no external lock is involved.

### Learning evidence

- Draw workers, queued calls, and every wait-for edge.
- Identify the first point at which owner-side orchestration was moved into a scarce worker.
- Explain why a timeout or a third worker changes one symptom without establishing a general capacity invariant.
- Design validation and storage stages whose owner collects completed validation before submitting dependent storage.

### Constraints

- The first response contains only the diagnosis and wait-for graph, not replacement code.
- Do not increase `max_workers`, use a nested executor, submit recursively, busy-wait, or add sleeps as the repair.
- Do not call an executor or future method inside a `ProcessPoolExecutor` callable.
- Keep job identity and application exceptions across both stages.
- A guarded reproduction must run in a subprocess or otherwise have an outer killable test boundary; do not hang the main test runner.

### Required edge cases

- One input with two workers accidentally succeeds.
- Two inputs consume both workers.
- Validation of one record fails.
- Storage is slower than validation.
- Shutdown begins between stages.
- A future is cancelled before its dependent stage is submitted.

### Acceptance criteria

- [ ] The wait-for cycle is complete and resource-specific.
- [ ] Accidental success at a larger worker count is not called correctness.
- [ ] Dependencies are coordinated by the executor owner.
- [ ] Failure prevents only the invalid dependent submission.
- [ ] Every accepted stage is collected before shutdown.
- [ ] The repair has an explicit in-flight bound.

### Learner attempt

- First invalid assumption:
- Wait-for graph:
- Accidental-success cases:
- Repair design:
- Attempt files:
- Test command:
- Observed result:

## PY-CON-050-P04 — Implement explicit result-order modes

### Problem

Implement a reusable Python 3.11-compatible batch function:

```python
execute_batch(jobs, operation, *, order, max_workers, max_in_flight)
```

`order` must be exactly `"input"` or `"completion"`. Each yielded item is an immutable `Outcome` containing input index, job ID, value or structured failure, and completion rank. The operation runs in a `ThreadPoolExecutor`, and the implementation may not accept more than `max_in_flight` uncollected jobs.

Input order must not be inferred from future completion. Completion order must not be implemented by sorting wall-clock timestamps. Preserve both input index and completion rank so callers can reason about the selected view.

### Learning evidence

- Use `submit()` plus explicit metadata to implement two consumer contracts.
- Explain why `map()` naturally exposes input order but is insufficient for the requested completion metadata and per-job cancellation.
- Refill the bounded window as completions are collected.
- Preserve failure as an outcome at the correct input position and completion rank.

### Constraints

- Standard library only; compatible with Python 3.11.
- No sleeps, timestamp sorting, private state, or unbounded initial submission.
- Event-controlled tests release jobs in a known non-input order.
- Iteration must close the executor even if the consumer stops early; choose and document whether the API is eager, a context-managed iterator, or another ownership-safe shape.
- Do not silently coerce unknown `order` values.

### Required edge cases

- Empty input.
- One job.
- Equal or near-simultaneous completions.
- Reverse completion order.
- A middle input raises.
- More inputs than the admission window.
- Consumer stops after the first yielded completion.
- Shutdown while work remains pending and running.

### Acceptance criteria

- [ ] Both ordering modes pass deterministic controlled tests.
- [ ] Input index and completion rank remain distinct.
- [ ] Capacity stays within the documented bound.
- [ ] Early consumer exit has an explicit cleanup policy.
- [ ] Task exceptions are not lost.
- [ ] The learner states what equal-time ordering the API does not guarantee.

### Learner attempt

- API ownership shape:
- Ordering invariants:
- Admission invariant:
- Attempt files:
- Test command:
- Observed result:
- Remaining uncertainty:

## PY-CON-050-P05 — Design and review an executor boundary

### Problem

A backend endpoint accepts up to 100 synthetic document IDs. For each ID it must load bytes from a thread-safe remote client, run a CPU-heavy pure-Python classifier, and persist an idempotent summary. The request deadline is two seconds. The service runs in Linux containers with a strict CPU and memory quota; deployment must also support a Python 3.11 interview implementation, while production is evaluating Python 3.14 isolated interpreters.

Write a design review that chooses boundaries for loading, classification, and persistence. Compare:

1. one shared thread pool;
2. a thread pool plus process pool;
3. a thread pool plus `InterpreterPoolExecutor`;
4. an external durable worker system.

Do not assume one option wins every deployment.

### Learning evidence

- Classify each stage by waiting, Python CPU, native CPU, side effects, and data size.
- State what is shared, copied, pickled, isolated, or external at each boundary.
- Bound workers, pending calls, remote connections, payload bytes, and accepted request work together.
- Define timeout, pending cancellation, running cooperation, late result, retry, and indeterminate-worker-loss policy.
- Provide a graceful service shutdown sequence.

### Required review dimensions

| Dimension | Questions |
|---|---|
| Correctness | Who owns each future and every external side effect? |
| Capacity | What prevents 100 requests from multiplying into unbounded pool work? |
| Deadline | What does the two-second owner timeout do to pending and running stages? |
| Serialization | Are callables, document bytes, clients, exceptions, and results transferable? |
| Isolation | Which mutable state exists per thread, process, or interpreter? |
| Failure | How are application failure, broken pool, cancellation, and indeterminate persistence separated? |
| Shutdown | When does admission close, what drains, what is cancelled, and when is escalation allowed? |
| Compatibility | What works on 3.11, and what Python 3.14 capability needs a guarded path? |
| Observability | Which safe job, queueing, execution, saturation, and outcome fields are recorded? |
| Measurement | Which representative benchmark could overturn the initial choice? |

### Constraints

- No production or personal data.
- No claim that threads are always for I/O or processes are always faster without qualification.
- No nested pools owned by worker callables.
- Do not serialize a live client, credential, open connection, or request object.
- Do not equate request timeout with rollback.
- State extension-compatibility uncertainty for isolated interpreters.
- State when local in-memory futures are insufficient for durability or independent retry.

### Acceptance criteria

- [ ] Every stage has a justified owner and executor boundary.
- [ ] Python 3.11 and 3.14 paths are explicit.
- [ ] Data transfer and side-effect uncertainty are addressed.
- [ ] Capacity has numeric starting bounds and an overload policy, labelled as hypotheses rather than measured optima.
- [ ] Shutdown includes admission, pending, running, collection, and escalation phases.
- [ ] At least one fact or measurement could change the recommendation.
- [ ] The design explains when an external durable system is necessary.

### Learner attempt

- Workload classification:
- Boundary and data-flow visual:
- Capacity assumptions:
- Failure taxonomy:
- Shutdown sequence:
- Compatibility note:
- Measurement plan:
- Remaining uncertainty:
