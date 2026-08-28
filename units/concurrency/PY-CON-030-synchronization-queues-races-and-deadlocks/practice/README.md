# Practice — PY-CON-030 Synchronization, queues, races, and deadlocks

| Field | Value |
|---|---|
| Unit note | [`PY-CON-030`](../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../CURRICULUM.md#py-con-030) |
| Topic branch | `topic/PY-CON-030` |
| Evidence target | E+C+D+X |
| Attempt required before solution | Yes |
| Test command | Define the narrow deterministic command with the first code attempt. |
| Status | Not attempted |

## Practice rules

1. Write the invariant, predicate, ownership rule, or capacity rule before choosing a primitive.
2. Record a prediction before running any output exercise.
3. Preserve the original attempt and the first failing deterministic test.
4. Request one progressive hint at a time; hints are intentionally absent from this initialized brief.
5. Do not use arbitrary sleeps to make a race, ordering, wakeup, or deadlock test pass.
6. A timeout is acceptable as a test guard, but timeout itself is not proof of deadlock.
7. Keep comparison solutions hidden until the learner closes the exercise.
8. Do not push later attempts automatically; keep the topic worktree pinned until publication.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Suggested files | Status |
|---|---|---:|---|---|---|
| `PY-CON-030-P01` | Predict | 2 | Derive every state transition in a barrier-controlled oversell. | `practice/p01_prediction.md` | Not attempted |
| `PY-CON-030-P02` | Implement | 3 | Preserve a multi-field reservation invariant with exception-safe synchronization. | `practice/p02_reservation.py` and focused tests | Not attempted |
| `PY-CON-030-P03` | Debug | 4 | Repair a broken condition protocol from the first invalid assumption. | `practice/p03_condition.py` and focused tests | Not attempted |
| `PY-CON-030-P04` | Implement | 4 | Build a bounded, failure-aware worker service with graceful shutdown. | `practice/p04_worker_service.py` and focused tests | Not attempted |
| `PY-CON-030-P05` | Diagnose | 4 | Prove and remove an opposing-transfer deadlock without weakening atomicity. | `practice/p05_deadlock.md` and focused test | Not attempted |
| `PY-CON-030-P06` | Design | 5 | Specify synchronization and backpressure for an audit boundary. | `practice/p06_design.md` | Not attempted |

## PY-CON-030-P01 — Predict the invariant failure

### Problem

Without executing the program, predict both values read by each worker, the two values written, final `available`, the contents of `accepted`, which ordering is not guaranteed, and whether any exception occurs.

```python
from threading import Barrier, Thread

available = 1
accepted: list[str] = []
both_checked = Barrier(2)


def reserve(request_id: str) -> None:
    global available
    if available > 0:
        both_checked.wait()
        available -= 1
        accepted.append(request_id)


workers = [
    Thread(target=reserve, args=(request_id,))
    for request_id in ("A", "B")
]
for worker in workers:
    worker.start()
for worker in workers:
    worker.join()

print(available, accepted)
```

### Learning evidence

- Identify the complete `available >= 0` and “at most one acceptance” invariant.
- Separate deterministic state from nondeterministic list ordering.
- Explain why the barrier exposes the window rather than creating the missing synchronization contract.

### Constraints

- Do not execute until every read, barrier arrival, write, and append is placed in a partial order.
- Do not cite a particular CPython bytecode sequence.
- Do not propose a fix in the prediction phase.

### Required edge cases

- Predict what changes if the initial value is zero.
- Explain what happens to the other worker if one fails before reaching the barrier.
- State why a barrier timeout changes failure behavior but not the inventory invariant.

### Acceptance criteria

- [ ] Both guaranteed state observations are correct.
- [ ] Unspecified acceptance ordering is labelled rather than guessed.
- [ ] The two separate invariant violations are named.
- [ ] The GIL is not treated as a transaction.
- [ ] Actual output is recorded only after the prediction.

### Learner attempt

- Partial-order trace:
- Final-state prediction:
- Invariant:
- Uncertainty:
- Command:
- Observed result:
- First incorrect assumption after review:

## PY-CON-030-P02 — Implement a reservation ledger

### Problem

Implement a thread-safe in-memory reservation ledger for synthetic stock. Each SKU has total stock, available stock, a mapping from idempotency key to one immutable reservation result, and a monotonically increasing revision.

`reserve(sku, quantity, idempotency_key)` must return the existing result for a duplicate key, reject invalid or unavailable quantities, and otherwise decrement available stock, store one result, and increment the revision as one transition. `snapshot(sku)` returns a coherent immutable view.

### Learning evidence

- Define and preserve all relationships among total, available, reservation quantities, idempotency keys, and revision.
- Choose lock granularity deliberately and release locks on every failure path.
- Test simultaneous duplicate keys and competing reservations without sleeps.

### Constraints

- Standard library only; Python 3.11-compatible public code.
- Do not hold a lock while parsing input, logging, or calling an external service.
- Do not expose internal mutable dictionaries in results or snapshots.
- Do not change a plain `Lock` to `RLock` unless same-thread re-entry is explicitly part of the API design.
- A test may use barriers or events to control entry, but production code must not depend on them.

### Required edge cases

- Zero and negative quantity.
- Unknown SKU.
- Two threads use the same idempotency key.
- Two different keys compete for the last item.
- A snapshot races with a successful reservation.
- A validation exception occurs before mutation.

### Acceptance criteria

- [ ] Every invariant is written above the implementation.
- [ ] Exactly one synchronization protocol protects every related field.
- [ ] Deterministic tests cover duplicate and last-item races.
- [ ] Returned values are immutable and do not alias ledger internals.
- [ ] Complexity and lock-contention trade-offs are explained.
- [ ] The learner explains why the chosen critical section is neither smaller nor larger.

### Learner attempt

- Invariants:
- Lock ownership and granularity:
- Attempt files:
- Test command:
- Observed result:
- Remaining uncertainty:

## PY-CON-030-P03 — Debug a condition buffer

### Problem

Find the first violated synchronization contract in this buffer. Record that first issue before listing any later problems or changing code.

```python
from threading import Condition


class Buffer:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.items: list[str] = []
        self.changed = Condition()
        self.closed = False

    def put(self, item: str) -> None:
        if len(self.items) == self.capacity:
            self.changed.wait()
        self.items.append(item)
        self.changed.notify()

    def get(self) -> str | None:
        with self.changed:
            if not self.items:
                self.changed.wait()
            if self.closed:
                return None
            item = self.items.pop(0)
        self.changed.notify()
        return item

    def close(self) -> None:
        self.closed = True
        self.changed.notify_all()
```

After the contract review, repair it with explicit “not empty or closed” and “not full or closed” predicates. Decide whether already buffered items drain after close.

### Learning evidence

- Apply the associated-lock requirement to predicate reads, state writes, waits, and notifications.
- Explain looped predicate checks, notification timing, closure, timeouts, and multiple waiters.
- Build deterministic tests for producer, consumer, and shutdown paths.

### Constraints

- The first review response contains no replacement implementation.
- Do not use `sleep` or inspect private waiter lists.
- Preserve the learner's broken first attempt.
- Compare the finished teaching buffer with `queue.Queue`; do not claim a custom buffer is preferable in production.

### Required edge cases

- Two consumers and one item.
- Close while consumers wait.
- Close while one item remains.
- Put after close.
- A producer waits for capacity and close occurs.
- Timeout expires while the predicate remains false.

### Acceptance criteria

- [ ] The first invalid contract is precise.
- [ ] Every predicate is read and changed under the associated lock.
- [ ] Waiters recheck state after wakeup.
- [ ] The closure and drain policy is explicit and tested.
- [ ] Notifications occur only after relevant state transitions.
- [ ] Remaining fairness limits are acknowledged.

### Learner attempt

- First invalid contract:
- Predicate table:
- Closure policy:
- Attempt files:
- Test command:
- Observed result:

## PY-CON-030-P04 — Build a bounded worker service

### Problem

Build a `ThumbnailService` around a synthetic blocking transformer. The service owns three non-daemon workers and a bounded input queue of five jobs.

The public API must reject submit before start and after shutdown begins; provide a caller-selected submit timeout and distinct overload outcome; deliver one immutable success or failure outcome per accepted job; close admission before graceful drain; use Python 3.13+ queue shutdown when available and a correct Python 3.11 sentinel protocol otherwise; join queue work and worker lifecycles without confusing the two; and report a shutdown timeout without pretending live workers were cancelled.

### Learning evidence

- Connect bounded capacity to backpressure rather than unbounded memory growth.
- Account for every retrieved job exactly once even when transformation raises.
- Separate admission, processing, result delivery, task completion, and worker termination.

### Constraints

- Standard library only and compatible with Python 3.11.
- Do not poll `qsize()`, `empty()`, or `full()` to make correctness decisions.
- Do not use daemon workers, busy waiting, arbitrary sleeps, or private queue fields.
- The synthetic transformer may be controlled with events in tests.
- Do not hold the service lifecycle lock while a blocking `put`, queue join, or thread join waits.

### Required edge cases

- Queue capacity is exhausted.
- A blocked producer observes shutdown.
- A worker reports a synthetic transformation failure.
- Shutdown begins with no jobs and with five accepted jobs.
- A Python 3.11 sentinel competes for bounded capacity.
- Shutdown deadline expires while a controlled transformer remains blocked.
- Immediate shutdown is requested; explain which completion guarantee is weakened.

### Acceptance criteria

- [ ] A state machine defines new, running, closing, and terminated behavior.
- [ ] Accepted, rejected, successful, failed, and timed-out outcomes are distinguishable.
- [ ] Task accounting remains balanced on every retrieved-item path.
- [ ] Worker failures cannot silently kill capacity.
- [ ] Both shutdown protocols have focused tests.
- [ ] The learner explains why queue join and thread joins are both required.

### Learner attempt

- Service state machine:
- Backpressure contract:
- Shutdown protocols:
- Attempt files:
- Test command:
- Observed result:
- Remaining uncertainty:

## PY-CON-030-P05 — Diagnose opposing transfers

### Problem

Two threads sometimes stop forever:

```python
def transfer(source: Account, target: Account, amount: int) -> None:
    with source.lock:
        validate(source, amount)
        with target.lock:
            source.balance -= amount
            target.balance += amount
```

Create a deterministic test that proves the wait cycle without leaving test threads stuck in the process. Draw the wait-for graph before proposing a repair. Then compare one global account lock, stable lock ordering by an immutable account key, and a single-owner transfer coordinator using message passing.

### Learning evidence

- Identify hold-and-wait edges and the exact cycle.
- Distinguish deadlock prevention from timeout detection.
- Preserve total balance and all-or-nothing local transfer semantics in the selected repair.

### Constraints

- Do not rely on repeated random execution or `sleep`.
- Do not leave a permanently deadlocked pair in the main test process; use a safely terminable subprocess or a protocol whose acquisition attempts have controlled timeouts.
- Do not release an arbitrary lock from a non-owner merely to make the test finish.
- Treat database-backed transfer atomicity as a separate external-system contract.

### Required edge cases

- Opposing transfers.
- Self-transfer.
- Insufficient balance.
- Equal or mutable ordering keys.
- An exception after the first local balance mutation.
- More than two accounts in one operation.

### Acceptance criteria

- [ ] The wait-for cycle is drawn precisely.
- [ ] The reproducer terminates deterministically.
- [ ] The repair removes the cycle rather than only adding a timeout.
- [ ] The ordering key is immutable and total.
- [ ] Local total balance is preserved on every completed path.
- [ ] Trade-offs among all three designs are explicit.

### Learner attempt

- Wait-for graph:
- Controlled reproduction design:
- Candidate repairs:
- Selected invariant and ordering:
- Test command:
- Observed result:

## PY-CON-030-P06 — Design a production audit boundary

### Problem

An API accepts audit events and currently starts one daemon thread per request. The audit client permits only eight concurrent calls, can block for ten seconds, and sometimes fails after partially sending a batch. Traffic can burst to 5,000 requests per second; the API deadline is 300 ms.

Design the in-process boundary. Do not write implementation code on the first attempt.

### Required decisions

- Exact meaning of “accepted” and whether in-process memory can satisfy it.
- Immutable event shape and sensitive-field policy.
- Worker count, semaphore or client-pool capacity, queue capacity, and memory bound.
- Blocking, timeout, rejection, load shedding, or durable handoff under overload.
- Result and failure delivery when the request may already have returned.
- Retry and idempotency contract for partial sends.
- Graceful and immediate shutdown behavior.
- Metrics, traces, alerts, and stuck-thread evidence.
- Why a durable broker or transactional outbox may be required instead of only Python synchronization.

### Learning evidence

- Choose primitives from state and ownership requirements rather than familiarity.
- Separate in-process coordination from durability and external atomicity.
- Reason from one end-to-end deadline and bounded resources.

### Constraints

- Use synthetic data only.
- Do not assume the client is thread-safe beyond the stated eight-call limit.
- Do not call an unbounded queue a buffer strategy.
- Do not treat daemon exit, logging, retry, or timeout as delivery proof.
- Label every unknown production fact that needs verification.

### Acceptance criteria

- [ ] A small ownership and capacity visual is included and explained.
- [ ] Every mutable object has one owner or synchronization contract.
- [ ] Overload produces a caller-visible or durably recorded outcome.
- [ ] Partial delivery and idempotency are treated explicitly.
- [ ] Shutdown order covers admission, drain/discard, task accounting, worker termination, and client cleanup.
- [ ] A simpler synchronous alternative and a durable external alternative are compared.

### Learner attempt

- Acceptance contract:
- Boundary visual:
- Capacity calculation inputs:
- Failure and retry matrix:
- Shutdown state machine:
- Unknown facts:
- Trade-off decision:

## Review and closure

Complete only after an attempt:

- What is correct:
- First incorrect assumption or missing reasoning step:
- Smallest deterministic counterexample:
- One next change:
- Actual commands and outputs:
- Final learner solution:
- Optional comparison solution:
- Remaining weakness:
- Evidence link for `PROGRESS.md`:
