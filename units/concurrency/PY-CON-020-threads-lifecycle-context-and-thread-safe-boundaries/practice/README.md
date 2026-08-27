# Practice — PY-CON-020 Threads, lifecycle, context, and thread-safe boundaries

| Field | Value |
|---|---|
| Unit note | [`PY-CON-020`](../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../CURRICULUM.md#py-con-020) |
| Topic branch | `topic/PY-CON-020` |
| Evidence target | E+C+D+X |
| Attempt required before solution | Yes |
| Test command | Define the narrow deterministic command with the first code attempt. |
| Status | Not attempted |

## Practice rules

1. Record a prediction or design before running code.
2. Preserve the original attempt, even when it fails.
3. Request one progressive hint at a time; hints are intentionally absent from this initialized brief.
4. Do not use arbitrary sleeps to prove order, liveness, cancellation, or thread safety.
5. A passing test is insufficient when the lifecycle or invariant explanation is wrong.
6. Add comparison code only after the exercise is reviewed and closed.
7. Do not push later attempts automatically; keep the topic worktree pinned until publication.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Suggested files | Status |
|---|---|---:|---|---|---|
| `PY-CON-020-P01` | Predict | 2 | Predict a controlled lifecycle and every raised or non-raised exception. | `practice/p01_lifecycle.py` after the prediction | Not attempted |
| `PY-CON-020-P02` | Implement | 3 | Own a worker from construction through cooperative stop, join, failure delivery, and cleanup. | `practice/p02_owned_worker.py` and focused tests | Not attempted |
| `PY-CON-020-P03` | Debug | 3 | Repair the reasoning behind fire-and-forget persistence. | `practice/p03_review.md` | Not attempted |
| `PY-CON-020-P04` | Implement | 4 | Make copied versus empty context explicit across Python 3.14 and 3.11. | `practice/p04_context.py` and focused tests | Not attempted |
| `PY-CON-020-P05` | Design | 4 | Specify a bounded backend thread boundary without implementing synchronization internals. | `practice/p05_design.md` | Not attempted |

## PY-CON-020-P01 — Predict a controlled lifecycle

### Problem

Without executing it, predict every printed value and every exception raised by this program. State which thread executes `target` in each call.

```python
from threading import Event, Thread, current_thread

release = Event()


def target(label: str) -> None:
    print(label, current_thread().name)
    if label == "started":
        release.wait()


direct = Thread(name="direct-worker", target=target, args=("direct",))
direct.run()
print("direct-alive", direct.is_alive())

started = Thread(name="started-worker", target=target, args=("started",))
print("before", started.ident, started.is_alive())
started.start()
print("timed-join-return", started.join(0))
print("after-timeout", started.is_alive())
release.set()
started.join()
print("after-finish", started.is_alive())
started.start()
```

### Learning evidence

- Distinguish an ordinary `run()` call from `start()`.
- Explain new, alive, timed-wait, terminated, and invalid-restart observations.
- Avoid predicting a specific `ident` or an unjustified print order.

### Constraints

- Do not execute until the full prediction is recorded.
- If an output order is not guaranteed, describe a set of valid partial orders.
- Name the exact line where the final exception originates.

### Required edge cases

- `join(0)` returns before or after a scheduling opportunity, but the worker remains held by `release`.
- `direct` was never started even though its target executed.

### Acceptance criteria

- [ ] Every guaranteed value is predicted.
- [ ] Nondeterministic ordering is labelled rather than guessed.
- [ ] The timed join is not described as cancellation.
- [ ] The final lifecycle error is identified and explained.
- [ ] Actual output is recorded only after the prediction.

### Learner attempt

- Prediction:
- Partial-order reasoning:
- Expected exception:
- Command:
- Observed result:
- First incorrect assumption after review:

## PY-CON-020-P02 — Implement an owned worker

### Problem

Implement a `WorkerService` for a synthetic blocking sink. Its context manager starts one non-daemon worker, `submit` accepts immutable string jobs while the service is running, and exit requests cooperative stop, waits with a deadline, reports worker failure to the owner, and always closes the sink in its owning thread.

This is lifecycle practice, not a request to invent a queue or lock. You may use documented `queue` and `threading` primitives.

### Learning evidence

- Pair start, stop admission, signal, drain-or-reject policy, join, and cleanup.
- Separate cooperative stop from timed waiting.
- Deliver failure to the owner without relying only on stderr.

### Constraints

- Use exactly one worker and one lifecycle owner.
- Do not use daemon mode, private thread APIs, busy waiting, or arbitrary sleeps.
- Specify whether accepted jobs drain or are rejected during shutdown.
- The sink instance must never be used concurrently by two threads.
- A join timeout must leave explicit evidence that the worker may still be alive.

### Required edge cases

- Starting twice.
- Submitting before start or after shutdown begins.
- Sink failure during a job.
- Shutdown while no jobs exist.
- Shutdown deadline expires while the sink call is still blocked.
- Cleanup itself fails after a worker failure.

### Acceptance criteria

- [ ] State transitions and invalid operations have focused tests.
- [ ] No test depends on scheduler luck.
- [ ] Original failure is not silently replaced by cleanup failure.
- [ ] The owner can distinguish success, worker failure, and shutdown timeout.
- [ ] The learner explains why Python cannot forcibly cancel the blocking sink call.

### Learner attempt

- Design and state machine:
- Attempt files:
- Test command:
- Observed result:
- Remaining uncertainty:

## PY-CON-020-P03 — Debug fire-and-forget persistence

### Problem

Review this claim and code:

> “The audit write is safe because dictionary assignment is atomic under the GIL, and daemon mode ensures it finishes in the background.”

```python
pending: dict[str, dict[str, object]] = {}


def accept(event_id: str, event: dict[str, object]) -> None:
    pending[event_id] = event

    def persist() -> None:
        audit_client.write(pending.pop(event_id))

    Thread(target=persist, daemon=True).start()
```

Record the first false assumption, then enumerate the remaining failures only after that first step is precise.

### Learning evidence

- Separate one container operation from the multi-step application invariant.
- Review captured mutable input, client contracts, duplicate IDs, failure observability, capacity, and shutdown.
- Define what `accept` is allowed to promise.

### Constraints

- Do not implement a replacement in the first attempt.
- Do not use “the GIL” as a complete safety argument.
- Classify each issue as lifecycle, data ownership, synchronization, client contract, failure, capacity, or API semantics.

### Smallest scenarios to examine

- Two calls use the same `event_id`.
- The process exits immediately after `accept` returns.
- `audit_client.write` blocks or raises.
- A caller mutates `event` after `accept` returns.
- Ten thousand requests arrive together.

### Acceptance criteria

- [ ] The first invalid premise is stated exactly.
- [ ] The full invariant is written before a mechanism is chosen.
- [ ] “Accepted” has a testable durability meaning.
- [ ] At least two boundary designs are compared without revealing implementation code.

### Learner attempt

- First false assumption:
- Full invariant:
- Issue classification:
- Candidate boundaries:
- Trade-off:

## PY-CON-020-P04 — Make context policy explicit

### Problem

Write a helper that starts a target under either a copied caller `Context` or a deliberately empty `Context`. Use `Thread(context=...)` on Python 3.14 and an explicit `Context.run` target wrapper on Python 3.11. The public behavior must not change with the `thread_inherit_context` flag.

### Learning evidence

- Explain snapshot time, worker-local changes, and why bindings do not flow back automatically.
- Distinguish `ContextVar` state from `threading.local` state.
- Test both policy choices without relying on build defaults.

### Constraints

- The caller chooses `"copy"` or `"empty"`; there is no implicit mode.
- Create `ContextVar` objects at module scope.
- Do not enter one `Context` concurrently in two threads.
- Use token reset with `try/finally` for Python 3.11 compatibility.

### Required edge cases

- Caller changes the variable after the snapshot but before `start()`.
- Worker changes its binding.
- Bound value is mutable; explain that context copying does not make it independently owned.
- Target raises.
- Invalid policy string.

### Acceptance criteria

- [ ] Focused tests cover both Python-version paths at the design level.
- [ ] Flag-dependent default behavior is never used for correctness.
- [ ] Target failure remains observable.
- [ ] The learner can explain why `threading.local` is not a drop-in logical-context replacement.

### Learner attempt

- API sketch:
- Snapshot point:
- Attempt files:
- Test command:
- Observed result:

## PY-CON-020-P05 — Design a backend thread boundary

### Problem

A request needs profile, orders, and fraud-policy data from three independent blocking clients. The response deadline is 400 ms. Design a thread boundary that could support the fan-out while preserving correctness and downstream health. Do not implement locks, queues, or an executor.

### Learning evidence

- Specify ownership, capacity, context, result/failure, deadline, and shutdown contracts.
- Identify facts that must be obtained from each client library.
- Distinguish an owner timing out from a worker operation being cancelled.

### Required decisions

- Maximum live work and behavior when capacity is exhausted.
- Per-thread versus shared client ownership.
- Copied, empty, or explicit-argument request context.
- Representation of success, expected failure, unexpected failure, and partial result.
- Per-call timeout and remaining request deadline.
- Service shutdown order.
- Metrics and traces that avoid private data.

### Acceptance criteria

- [ ] A small state/timeline visual is included and explained.
- [ ] Every shared mutable object has an owner or protection contract.
- [ ] The design remains correct on regular and free-threaded CPython.
- [ ] At least one simpler sequential alternative and one higher-level future-based alternative are compared.
- [ ] Claims about each client are labelled as facts to verify, not assumptions.

### Learner attempt

- Boundary diagram:
- Contract:
- Unknown client facts:
- Failure matrix:
- Trade-off decision:

## Review and closure

Complete only after an attempt:

- What is correct:
- First incorrect assumption or missing reasoning step:
- Smallest counterexample:
- One next change:
- Actual commands and outputs:
- Final learner solution:
- Optional comparison solution:
- Remaining weakness:
- Evidence link for `PROGRESS.md`:
