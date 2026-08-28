# PY-CON-030 — Synchronization, queues, races, and deadlocks

[Curriculum entry](../../../CURRICULUM.md#py-con-030) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-CON-030`

## Physical Notebook Core

### Problem this concept solves

Threads share memory, so a scheduler may pause one thread between the read, decision, and write that form one application rule. Synchronization makes those multi-step rules, waits, capacity limits, phase boundaries, and ownership transfers explicit.

### One-sentence mental model

> First name the invariant or state predicate, then choose the narrowest primitive that makes every valid transition explicit: exclusive ownership, recursive ownership, permits, a flag, a predicate wait, a rendezvous, or a queue.

### One important visual

```text
UNSAFE shared update                     SYNCHRONIZED transition

Thread A: read 0 ---- pause              Thread A: acquire Lock
Thread B: read 0 ---- write 1                       read 0 -> write 1
Thread A: ----------- write 1                       release Lock
final value: 1                           Thread B: acquire Lock
expected: 2                                         read 1 -> write 2
                                                    release Lock
                                         final value: 2

Alternative ownership:
producer -- put(job) --> Queue(maxsize=N) -- get(job) --> sole state owner
```

#### How to read this visual

Read the left side top to bottom: both threads capture the same old value, so the later write loses one update. On the right, the lock encloses the whole read–modify–write transition, so the second thread observes the first transition. The bottom lane replaces shared mutation with bounded message transfer.

#### Key insight

Protect an application invariant, not an isolated line. Sometimes the cleanest protection is to stop sharing the mutable object and transfer work through a queue.

#### Simplification or limitation

This is a deliberately controlled logical interleaving, not a claim about a particular CPython bytecode sequence or operating-system schedule. A lock does not make remote I/O atomic, and a queue does not automatically define retries, durability, or shutdown policy.

### Governing rules or invariants

1. State the invariant, owner, and permitted transitions before selecting a primitive; the GIL and built-in container internals are not application transactions.
2. Keep every read, validation, and write that must be indivisible under the same lock, release it with `with`, and avoid unknown callbacks or blocking I/O inside the critical section.
3. Wait for a condition predicate in a loop or with `Condition.wait_for()`; a notification means “recheck state,” not “the condition is definitely true.”
4. Treat `Event` as a level-triggered flag, `Semaphore` as capacity, `Barrier` as a fixed-party phase gate, and `Queue` as synchronized ownership transfer with optional backpressure.
5. Prevent deadlock structurally with one global lock order, smaller ownership surfaces, and explicit shutdown; timeouts can expose a stuck wait but do not repair a partially completed invariant.

### Minimal example

```python
from threading import Lock

remaining = 1
remaining_lock = Lock()


def reserve_one() -> bool:
    global remaining
    with remaining_lock:
        if remaining == 0:
            return False
        remaining -= 1
        return True
```

Expected reasoning:

1. The invariant is `remaining` never becomes negative; checking availability and decrementing belong to one transition.
2. The context manager releases the lock on every return or exception path, while callers may run concurrently outside the short critical section.

### One failure or misconception

**Mistake:** “This compound update is safe on regular CPython because the GIL lets only one thread execute Python bytecode at a time.”

**Correction:** The application transition spans several operations and may be separated by scheduling, callbacks, or blocking work. Free-threaded CPython can also run Python threads in parallel. Use a documented synchronization or ownership boundary for the complete invariant.

### Important trade-offs

- Coarse locks are easier to reason about but reduce concurrency and magnify blocking; fine-grained locks may improve overlap while multiplying ordering and deadlock risks.
- Queues clarify ownership and provide backpressure, but add latency, capacity, failure-delivery, and shutdown protocols.
- `RLock` supports legitimate recursive entry, but it can hide an unclear call graph; prefer a plain `Lock` when re-entry is not part of the design.
- Timeouts improve failure detection and deadline control, but they create an additional outcome to handle and do not roll back work.

### Interview-revision cues

- Given a shared update, write the invariant and mark the smallest complete critical section.
- Compare `Lock`, `RLock`, `Condition`, `Semaphore`, `Event`, `Barrier`, and `Queue` by the state each one represents.
- Draw a two-lock wait cycle, then remove one edge with global ordering or single-owner message passing.
- Explain `Queue.task_done()`, `Queue.join()`, bounded capacity, and Python 3.14 versus 3.11 shutdown.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Concurrency, parallelism, and asynchronous Python |
| Canonical ID | `PY-CON-030` |
| Learning outcome | Use locks, reentrant locks, semaphores, events, conditions, barriers, and `queue`; diagnose races and deadlocks |
| Hard prerequisites | `PY-CON-020`, `PY-LIB-020` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D3 |
| Scope | Standard library, CPython |
| Size | L |
| Evidence profile | E+C+D+X |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4, regular GIL-enabled build, Linux x86_64 |
| Last source audit | 2026-08-28 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Define a shared-state invariant and choose deliberately among confinement, immutable input, a lock, an `RLock`, a condition, a semaphore, an event, a barrier, and a queue.
2. Implement exception-safe critical sections, predicate-based waits, capacity limits, phased coordination, bounded producer–consumer flow, task accounting, and graceful queue shutdown.
3. Reproduce and explain a controlled race without relying on scheduler luck, then show why the repaired transition preserves the invariant.
4. Diagnose self-deadlock, inconsistent lock order, wait-for cycles, lock-held callbacks, missing queue accounting, and shutdown deadlocks.
5. Review a backend concurrency boundary for ownership, backpressure, failure delivery, deadlines, observability, CPython build differences, and Python 3.11 compatibility.

Required evidence:

- Reconstruct the core interleaving and explain why the invariant—not one bytecode or container method—is the unit of protection.
- Complete at least one predict/debug exercise, one implementation exercise, and the deadlock design exercise in [the practice brief](practice/README.md), preserving the original attempts.
- Run and interpret [EXP-01](experiments/EXP-01-controlled-race-window/README.md), including what it proves and what its controlled schedule deliberately omits.
- Explain one realistic boundary twice: once with protected shared state and once with queue-based ownership transfer, then justify the preferred design.

Initialization creates runnable examples, an interpreted experiment, and unsolved evidence prompts. It does not prove learner understanding or advance the learning state.

## 2. Prerequisite bridge

Both hard prerequisites remain unlearned on the current `main` baseline. These bridges support useful study but do not replace either unit.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-CON-020` — Threads, lifecycle, context, and thread-safe boundaries | Synchronization code is only correct when worker lifetime, failure, context, and shared-data ownership are also owned. | A `Thread` is single-use; start it once, arrange cooperative shutdown, make failure explicit, and join every non-daemon worker. Shared objects cross a boundary that needs a documented contract. |
| Hard | `PY-LIB-020` — Deque and queue-like patterns | Queue order and end-operation costs shape producer–consumer designs. | FIFO removes the oldest enqueued item, LIFO removes the newest, and priority order follows comparable keys. A container shape alone is not a thread-safety or blocking contract. |

Recommended follow-up: publish or initialize the dedicated `PY-CON-020` work before treating this unit as complete, and study `PY-LIB-020` before designing custom queue-like structures.

## 3. Vocabulary and professional English

### Invariant

| Item | Content |
|---|---|
| Pronunciation | in-VAIR-ee-unt |
| Simple English meaning | A rule that must remain true |
| Hindi cue | अटल नियम |
| Meaning in this Python context | A relationship over shared state that every concurrent transition must preserve |

Natural examples:

1. The inventory invariant says available stock never becomes negative.
2. A lock is useful only when its protected invariant is documented.
3. Immediate queue shutdown weakens the usual task-completion invariant.
4. **Interview:** “I would identify the invariant before choosing a synchronization primitive.”
5. **Engineering discussion:** “The database transaction protects one invariant; the in-process lock protects a different one.”

### Contention

| Item | Content |
|---|---|
| Pronunciation | kun-TEN-shun |
| Simple English meaning | Competition for the same limited thing |
| Hindi cue | प्रतिस्पर्धा |
| Meaning in this Python context | Threads waiting or repeatedly competing for a lock, permit, queue slot, or shared resource |

Natural examples:

1. Moving parsing outside the lock reduced contention.
2. High contention can turn a fine-grained design into serialized work.
3. Queue backpressure may be preferable to connection-pool contention.
4. **Interview:** “Lock contention affects latency, but splitting locks also increases proof complexity.”
5. **Engineering discussion:** “Measure wait duration and hold duration separately before redesigning the lock.”

### Rendezvous

| Item | Content |
|---|---|
| Pronunciation | RON-day-voo |
| Simple English meaning | A planned meeting point |
| Hindi cue | मिलने का तय बिंदु |
| Meaning in this Python context | A phase boundary at which a fixed number of threads wait for one another |

Natural examples:

1. The barrier is a rendezvous before the parallel phase begins.
2. One missing participant breaks the rendezvous.
3. A rendezvous does not transfer results by itself.
4. **Interview:** “I would use a barrier only when the participant count is fixed and owned.”
5. **Engineering discussion:** “Request workers are dynamic, so a queue fits better than a rendezvous.”

### Backpressure

| Item | Content |
|---|---|
| Pronunciation | BACK-presh-er |
| Simple English meaning | A mechanism that slows input when downstream capacity is full |
| Hindi cue | दबाव के अनुसार गति रोकना |
| Meaning in this Python context | Blocking, timing out, rejecting, or shedding producer work when a bounded queue or semaphore has no capacity |

Natural examples:

1. A bounded queue turns memory growth into explicit backpressure.
2. Backpressure needs a caller-visible timeout or rejection policy.
3. An infinite queue postpones overload rather than solving it.
4. **Interview:** “I would tie queue capacity to downstream concurrency and the request deadline.”
5. **Engineering discussion:** “The metric shows whether backpressure comes from workers, connections, or the remote service.”

## 4. Deep explanation

### 4.1 Begin with state, not primitives

A race condition exists when correctness depends on an uncontrolled relative ordering of concurrent actions. Common shapes include check-then-act, read–modify–write, duplicate initialization, stale validation, and “observe empty, then block” logic. The scheduler does not create the bug; it reveals that the application failed to define one indivisible transition or one owner.

Before adding a lock, write four statements:

1. **State:** which values can be observed or changed by more than one thread?
2. **Invariant:** which relationship must hold before and after every transition?
3. **Transition:** which reads, decisions, writes, and local cleanup belong together?
4. **Boundary:** which code may perform the transition, and how do other threads request or observe it?

This frequently leads to confinement or message transfer rather than locking. A lock is not a general “thread-safe” sticker: callers that access the same state without the same protocol can still violate the invariant.

### 4.2 `Lock`: exclusive access to one critical transition

A primitive `threading.Lock` starts unlocked. An acquire either changes it to locked or waits; release changes it back, and releasing an unlocked lock raises `RuntimeError`. A primitive lock is not owned by the acquiring thread, and the standard library does not define which waiter proceeds next. Use the context-manager form to make release exception-safe. See [`Lock` objects](https://docs.python.org/3.14/library/threading.html#lock-objects).

```python
with state_lock:
    # read, validate, and update every field in this invariant
    ...
```

Keep computation that does not touch the invariant outside the block. Avoid network calls, database calls, logging handlers, and user callbacks while holding a lock unless the design explicitly owns their duration and re-entry behavior. A Python lock cannot make an external side effect roll back if local work later fails.

### 4.3 `RLock`: exclusive access with same-thread re-entry

An `RLock` records an owning thread and recursion level. The owner may acquire it repeatedly; every successful acquisition needs a matching release, and only the outermost release makes the lock available to another thread. A different thread cannot release it. See [`RLock` objects](https://docs.python.org/3.14/library/threading.html#rlock-objects).

Use an `RLock` when a deliberately supported call graph re-enters the same protected abstraction—for example, one public method calls another public method that must also be safe alone. Do not replace a self-deadlocking `Lock` mechanically before asking whether an internal “lock already held” helper would make ownership clearer. Reentrancy prevents one deadlock shape; it does not prevent cycles across different locks.

### 4.4 `Condition`: wait for a predicate over protected state

A `Condition` combines a lock with a set of waiters. The waiter holds the associated lock, checks a predicate, and calls `wait()`. Waiting releases the lock so another thread can change the state, then reacquires it before returning. A notifier changes the state while holding the same lock and calls `notify()` or `notify_all()`; notification does not release the lock. See [`Condition` objects](https://docs.python.org/3.14/library/threading.html#condition-objects).

```python
with condition:
    condition.wait_for(lambda: item_available or closed)
    # predicate is inspected again while the lock is held
```

The loop matters because time passes between notification, scheduling, and lock reacquisition; another thread may consume or change the state first. Notification is a hint to recheck, not ownership of an item. `wait_for()` expresses the loop and timeout accounting, but the predicate and state changes still need the condition's lock.

### 4.5 `Semaphore` and `BoundedSemaphore`: represent permits

A semaphore has a non-negative counter. Successful acquire consumes one permit; release returns permits; when the counter is zero, acquirers wait or time out. Wake-up order is not a fairness contract. `BoundedSemaphore` additionally raises `ValueError` if releases would exceed the initial capacity, making over-release bugs visible. See [semaphore objects](https://docs.python.org/3.14/library/threading.html#semaphore-objects).

Semaphores fit capacity such as “at most eight calls use this legacy client at once.” They do not protect a relationship among arbitrary fields unless the permit is explicitly the state model. Acquire as near as possible to actual resource use and release in `finally` or `with`. Do not hold a scarce permit while waiting indefinitely for unrelated work.

### 4.6 `Event`: a persistent boolean signal

An `Event` stores a flag. `set()` makes it true and wakes all current waiters; later waiters also pass until `clear()` makes it false. `wait(timeout)` returns a boolean indicating whether the flag became set before timeout. See [`Event` objects](https://docs.python.org/3.14/library/threading.html#event-objects).

This is appropriate for “configuration is ready,” “shutdown requested,” or a controlled test gate. It is not a counter, result container, ownership transfer, or reliable one-notification-per-event channel. Rapid `set()` and `clear()` calls may not represent distinct work units to every waiter; use a queue or protected sequence number when each occurrence matters.

### 4.7 `Barrier`: a fixed-party phase boundary

A `Barrier(parties)` releases a phase only after exactly that many participants call `wait()`. Each receives a distinct integer from zero through `parties - 1`, which can select one housekeeping participant. A timeout, failing action, reset, or abort can put it in a broken state and cause `BrokenBarrierError`. Barriers are reusable, but recovery may be clearer with a new instance. See [`Barrier` objects](https://docs.python.org/3.14/library/threading.html#barrier-objects).

Barriers suit controlled experiments and fixed-size phase algorithms. They are usually wrong for elastic request traffic: one missing, cancelled, or unknown participant can block the entire phase.

### 4.8 `Queue`: synchronized ownership transfer and backpressure

The `queue` module provides multi-producer, multi-consumer FIFO, LIFO, and priority queues with the required locking semantics. A positive `maxsize` blocks or rejects producers when capacity is full. `qsize()`, `empty()`, and `full()` are approximate observations and cannot justify a later non-blocking assumption. Use `put` or `get` with the desired blocking and timeout contract instead. See [`queue` synchronization and capacity](https://docs.python.org/3.14/library/queue.html).

Task accounting is separate from item removal:

- every successful `put()` increments unfinished work;
- each retrieved item must eventually receive exactly one `task_done()` after processing, normally in `finally`;
- `join()` waits until unfinished work reaches zero, not merely until the container looks empty.

Python 3.13 added `Queue.shutdown()` and `queue.ShutDown`. Graceful shutdown stops growth, unblocks blocked producers, allows already queued work to drain, and makes later empty gets raise `ShutDown`. Immediate shutdown drains pending items and can unblock `join()` without work being processed, intentionally weakening its usual invariant. See [`Queue.shutdown()`](https://docs.python.org/3.14/library/queue.html#terminating-queues).

For Python 3.11, a private sentinel per consumer can request termination after accepted work, but admission must be closed by application policy before sentinels are enqueued. Sentinels consume queue capacity and unfinished-task counts like other items. A sentinel is a compatibility protocol, not a magic equivalent to shutdown in every producer topology.

### 4.9 Deadlock is a wait-for cycle

A deadlock occurs when progress requires a cycle of waits that none of the participants can break. Python examples include:

- a thread acquires a non-reentrant `Lock` twice;
- transfer A holds account 1 and waits for account 2 while transfer B holds account 2 and waits for account 1;
- code holds a lock while joining a worker that needs the same lock to terminate;
- a callback invoked under a lock re-enters the locked abstraction;
- a producer waits for queue capacity while the only consumer waits for the producer to release another resource;
- a barrier waits forever for a participant that failed before arrival.

Prefer structural prevention:

1. reduce the number of shared mutable owners;
2. use one lock for one tightly related invariant when practical;
3. impose and document one total order for acquiring multiple locks;
4. never call unknown code while holding a lock;
5. avoid joining workers or performing unbounded I/O while holding resources they may need;
6. give waits deadlines where the caller can safely handle timeout;
7. expose thread names, lock/queue wait duration, capacity, and stack dumps for diagnosis.

A timeout converts an indefinite wait into a failure path. It does not prove deadlock, guarantee another participant stopped, or restore state automatically.

### 4.10 The GIL and built-in internals are not the protocol

Regular CPython normally allows only one thread to execute Python bytecode at once, while free-threaded builds can execute Python threads in parallel. Free-threaded CPython uses internal locks for built-in containers to provide behavior broadly similar to the regular build, but the official documentation says concurrent modifications have not historically had a Python-level behavior guarantee and recommends explicit synchronization instead. See [free-threaded thread safety](https://docs.python.org/3.14/howto/free-threading-python.html#thread-safety).

Even if one low-level operation is indivisible on one runtime, an application invariant usually spans several operations and external systems. Correct code should remain explainable without depending on a particular bytecode decomposition or undocumented container lock.

### 4.11 Execution sequence for a bounded worker queue

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Owner creates a bounded queue and non-daemon consumers. | Capacity, worker count, failure channel, and shutdown owner are known. |
| 2 | A producer calls `put(job, timeout=...)`. | Job is accepted, blocks for capacity, times out, or is rejected after shutdown. |
| 3 | A consumer calls `get()`. | Queue ownership of one job transfers to that consumer. |
| 4 | Consumer processes the job and records success or failure. | External side effects follow a separate idempotency or transaction contract. |
| 5 | Consumer calls `task_done()` exactly once in `finally`. | Unfinished-task count decreases even when processing fails. |
| 6 | Owner closes admission and initiates graceful shutdown. | Accepted jobs drain; new jobs cannot enter. |
| 7 | `queue.join()` and thread joins complete. | Task accounting is zero and worker lifecycles have terminated. |

## 5. Additional visual models

### 5.1 Condition predicate protocol

```text
WAITER                                  NOTIFIER

acquire condition lock                  waits for same lock
while not predicate():
    wait() -- releases lock ----------> acquire lock
                                        change protected state
                                        notify()
                                        release lock
          <--- wake, then reacquire ---
recheck predicate while locked
consume or transition protected state
release lock
```

#### How to read this visual

Follow the waiter down to `wait()`, then cross to the notifier. The notifier changes state before notification and still owns the lock after notifying. Only after release can the waiter reacquire and test the predicate again.

#### Key insight

The shared predicate is the truth; notification only tells waiters that the truth may have changed.

#### Simplification or limitation

This conceptual timeline omits multiple waiters, timeouts, cancellation, and exceptions. It does not promise which notified waiter reacquires the lock first.

### 5.2 Two-lock deadlock and ordered repair

```text
INCONSISTENT ORDER                         ONE GLOBAL ORDER

T1 owns A -> waits B                       T1 requests A -> B
             ^                             T2 requests A -> B
             |                             only one owns A;
T2 owns B -> waits A                       no A ↔ B wait cycle
```

#### How to read this visual

On the left, follow both arrows around the cycle: each thread owns what the other needs. On the right, both operations request the same lower-key lock before the higher-key lock, so the opposing edge cannot form.

#### Key insight

Global ordering prevents the cycle; locally reasonable acquisition choices do not.

#### Simplification or limitation

Ordering only covers locks included in the order and code that obeys it. Callbacks, condition waits, queues, remote I/O, and dynamic resource sets can add other wait edges.

## 6. Worked examples

All observed outputs in the runnable artifacts were captured on CPython 3.14.4, regular GIL-enabled build, Linux x86_64, on 2026-08-28.

### 6.1 Lock the complete reservation invariant

Run [`examples/locked_invariant.py`](examples/locked_invariant.py):

```bash
python units/concurrency/PY-CON-030-synchronization-queues-races-and-deadlocks/examples/locked_invariant.py
```

Observed:

```text
accepted=1
rejected=1
remaining=0
invariant=True
```

The example aligns two reservation attempts at a `Barrier`, but protects the inventory check and decrement with one `Lock`. It reports one acceptance, one rejection, zero remaining stock, and a preserved invariant. The barrier controls the demonstration; it is not needed by the reservation abstraction.

### 6.2 Build a one-slot condition buffer

Run [`examples/condition_buffer.py`](examples/condition_buffer.py):

```bash
python units/concurrency/PY-CON-030-synchronization-queues-races-and-deadlocks/examples/condition_buffer.py
```

Observed:

```text
processed=[2, 4, 6]
buffer_closed=True
workers_alive=False
```

This educational buffer has `not full`, `not empty`, and `closed` predicates under one `Condition`. It shows why state is changed before notification and why a closed buffer may still drain one existing item. Production producer–consumer code should normally use `queue.Queue` instead of rebuilding this protocol.

### 6.3 Use a bounded queue with version-aware shutdown

Run [`examples/bounded_queue_pipeline.py`](examples/bounded_queue_pipeline.py):

```bash
python units/concurrency/PY-CON-030-synchronization-queues-races-and-deadlocks/examples/bounded_queue_pipeline.py
```

Observed:

```text
shutdown_protocol=Queue.shutdown
invoice-1=ok:ready
invoice-2=error:ValueError: synthetic invalid payload
invoice-3=ok:paid
workers_alive=False
```

The pipeline uses `Queue(maxsize=2)`, immutable jobs and results, exactly-once task accounting, explicit failure delivery, and non-daemon worker joins. Python 3.13+ uses graceful `Queue.shutdown()`; Python 3.11 uses one private sentinel per consumer after admission closes.

### 6.4 Compare `RLock`, semaphore, event, and barrier roles

Run [`examples/primitive_roles.py`](examples/primitive_roles.py):

```bash
python units/concurrency/PY-CON-030-synchronization-queues-races-and-deadlocks/examples/primitive_roles.py
```

Observed:

```text
rlock_total=7
semaphore_max_active=2
event_is_set=True
barrier_tokens=[0, 1, 2]
```

Independent, controlled demonstrations show same-thread re-entry, a maximum of two simultaneous permit holders, an event that releases current and future waiters, and unique barrier tokens for one fixed phase. The point is semantic comparison, not performance.

### 6.5 Prevent opposing-transfer deadlock

Run [`examples/deadlock_avoidance.py`](examples/deadlock_avoidance.py):

```bash
python units/concurrency/PY-CON-030-synchronization-queues-races-and-deadlocks/examples/deadlock_avoidance.py
```

Observed:

```text
accepted=2
balances=A:100,B:100
total=200
workers_alive=False
```

Two threads start opposing transfers together. Both acquire account locks in stable account-ID order, so they finish without a wait cycle and preserve the total balance. Database-backed money movement would still need database transactions, idempotency, and failure semantics; in-process locks cannot provide those guarantees.

### 6.6 Debugging example: notification without a predicate protocol

Keep the correction hidden until an attempt.

```python
from threading import Condition

condition = Condition()
items: list[str] = []


def take() -> str:
    with condition:
        if not items:
            condition.wait()
        return items.pop()


def publish(item: str) -> None:
    items.append(item)
    condition.notify()
```

Before changing code:

1. Identify the first violated `Condition` contract.
2. Write the predicate the consumer actually needs.
3. Explain why replacing `if` with `while` is necessary but not by itself sufficient.
4. Decide how timeout and permanent closure should be represented.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| Protecting only the write fixes a check-then-act race. | The write is where state visibly changes. | The earlier read and decision are part of the same transition. | Force both threads to read before either writes, as EXP-01 does. |
| The GIL is equivalent to a lock around the function. | Regular CPython serializes bytecode execution. | The function spans multiple operations and may release or yield execution; free-threaded builds may run in parallel. | Mark each read, call, possible block, and write in the invariant. |
| `Lock` remembers its owner. | Many mutex APIs are owner-released. | Python's primitive lock is not owned; any thread may release it, though doing so often signals a fragile design. | Acquire in one controlled thread and release in another, then discuss why the contract is still undesirable. |
| `RLock` solves every nested-lock deadlock. | Same-thread reacquisition succeeds. | It only handles re-entry into that same lock; cycles across locks remain. | Draw two `RLock` objects acquired in opposite order. |
| One `notify()` transfers one item to one specific waiter. | One waiter is normally awakened. | Notification only prompts rechecking; waiter choice and later state are not ownership guarantees. | Use two consumers and let another transition occur before reacquisition. |
| `Event.set()` records every occurrence. | All waiters wake when it is set. | An event stores one boolean level, not a count or payload. | Call `set()` twice before one wait and observe only a true flag. |
| A semaphore protects any shared state. | It is a synchronization primitive. | A semaphore models permits; arbitrary multi-field invariants still need a clear owner and transition protocol. | Write the capacity counter and the separate business invariant side by side. |
| Barrier timeout affects only one participant. | One call supplied the timeout. | A timeout breaks the barrier, so other active and future waiters fail too. | Omit one participant under a short controlled timeout and inspect `broken`. |
| `queue.empty()` makes `get_nowait()` safe. | The observation was false immediately before the call. | Another consumer may remove the item; state observations are approximate. | Align two consumers after one `empty()` observation and provide one item. |
| `Queue.join()` means worker threads terminated. | Both use the word join. | Queue join waits for task accounting to reach zero; thread join waits for thread termination. | Let a worker call `task_done()` and then wait at an event. |
| `task_done()` belongs immediately after `get()`. | Retrieval changed the queue. | It records completed processing and belongs in `finally` around processing. | Make processing raise and inspect whether queue join can finish. |
| Immediate queue shutdown proves accepted work completed. | It may unblock `join()`. | Immediate mode deliberately weakens the usual completion invariant by draining pending work. | Record processed job IDs separately and compare them with accepted IDs. |
| Lock acquisition timeout rolls back an operation. | The wait has a bounded result. | Timeout only reports that acquisition failed; earlier effects remain unless explicitly compensated. | Mutate one field before a timed second acquire and inspect partial state. |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| Uncontended lock acquire/release | Constant-time API operation plus runtime/OS overhead | Exact cost depends on interpreter, build, platform, and contention; no timing is claimed. |
| Contended acquire or condition wait | Blocking and scheduler coordination | Tail latency depends on hold time, wakeups, scheduling, and workload. |
| FIFO `Queue.put` / `get` | Typically constant-time container work plus synchronization | Blocking duration is unbounded without a timeout; priority queues add heap ordering cost. |
| `PriorityQueue.put` / `get` | Typically logarithmic in queued item count | Comparable priority keys and stable tie-breaking are application concerns. |
| `qsize`, `empty`, `full` | Observation only | Even a cheap observation cannot reserve a future operation. |
| One global lock | Simple proof; concurrent protected throughput is serialized | May be the correct design when the critical region is short or the invariant is truly global. |
| Multiple locks | More potential overlap | Adds metadata, acquisition protocol, failure paths, and wait-cycle risk. |
| Bounded queue | Memory proportional to capacity plus in-flight work | Capacity trades burst absorption against memory, producer latency, and overload behavior. |

Measure lock wait time separately from hold time, and queue wait separately from service time. Report workload, runtime build, machine, capacity, thread count, trial policy, and latency distribution. Do not infer a universal speedup from a sleep-based demonstration.

## 9. Production relevance and trade-offs

Review synchronized backend code in this order:

| Concern | Question |
|---|---|
| Invariant | What precise relationship must remain true across which fields or external actions? |
| Ownership | Can one worker own the mutable object instead of sharing it? |
| Critical region | Are all required reads and writes protected, with expensive independent work outside? |
| Ordering | If several resources are acquired, is there one total order followed on every path? |
| Capacity | What bounds threads, queue entries, permits, connections, memory, and downstream work? |
| Backpressure | Does overload block, time out, reject, shed, or persist, and what does the caller observe? |
| Failure | How are worker exceptions, partial side effects, retryability, and cleanup failures delivered? |
| Deadline | Does each wait respect the remaining end-to-end deadline rather than starting a fresh full timeout? |
| Shutdown | Who stops admission, drains or discards accepted work, wakes waiters, accounts tasks, and joins workers? |
| Observability | Can operators see wait duration, hold duration, queue depth, rejected work, stuck threads, and lock-order context without private data? |
| Portability | Does reasoning use public contracts rather than a regular-CPython GIL or undocumented atomic container operation? |

Prefer immutable jobs and results. Keep customer or credential data out of diagnostic traces. Treat retries and idempotency as external correctness protocols, not as properties supplied by a lock or queue. If a database can enforce the true invariant atomically, an in-memory lock may be both insufficient and misleading in a multi-process service.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| `Lock`, `RLock`, `Condition`, `Semaphore`, `BoundedSemaphore`, `Event`, and `Barrier` | Standard library | Long-standing; `Barrier` added in 3.2 | Same public primitives exist | Availability excludes WASI; fairness and scheduling are not specified. |
| `Lock` is a public class rather than a factory | Standard library, version-dependent | 3.13 | Call `threading.Lock()` without depending on its concrete type identity. | Runtime annotations or subclass assumptions may differ on older Python. |
| `RLock.locked()` | Standard library, version-dependent | 3.14 | Design through ownership and context managers; do not require the inspection method. | A snapshot of lock state cannot reserve a later acquire. |
| Signal interruption of lock acquisition on Windows | Standard library plus platform behavior | 3.14 | Earlier behavior is platform/version dependent. | Do not build portable correctness around which signal interrupts a wait. |
| `Queue.shutdown()` and `queue.ShutDown` | Standard library, version-dependent | 3.13 | Close admission, then enqueue one private sentinel per consumer and account for each sentinel. | Immediate shutdown weakens the normal `join()` invariant. |
| `Queue.qsize`, `empty`, and `full` are approximate observations | Standard-library contract | Long-standing | Same contract | Use blocking, timeout, or non-blocking operations and handle their result/exception. |
| Internal locks on free-threaded built-ins | CPython implementation detail | Optional free-threaded build in 3.13 | Explicit public synchronization | The docs recommend not relying on internal container locks as the application protocol. |
| Parallel Python execution in a free-threaded build | CPython, version-dependent | 3.13 | Regular 3.11 CPython normally uses a GIL-enabled build. | Native extensions may re-enable the GIL; synchronization remains required on both builds. |

For a Python 3.11 interview, lead with stable primitive semantics, condition predicates, queue task accounting, sentinels, lock ordering, and whole-invariant reasoning. Then label `Queue.shutdown()`, `ShutDown`, `Lock` class identity, and `RLock.locked()` as post-3.11 additions.

## 11. Practice brief

Exercises are specified without solutions in [`practice/README.md`](practice/README.md).

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-CON-030-P01` | Predict | 2 | Derive a controlled lost update and all permitted output orderings. | [Practice brief](practice/README.md#py-con-030-p01-predict-the-invariant-failure) |
| `PY-CON-030-P02` | Implement | 3 | Build an exception-safe reservation boundary around a multi-field invariant. | [Practice brief](practice/README.md#py-con-030-p02-implement-a-reservation-ledger) |
| `PY-CON-030-P03` | Debug | 4 | Repair a condition protocol without leaking a replacement solution first. | [Practice brief](practice/README.md#py-con-030-p03-debug-a-condition-buffer) |
| `PY-CON-030-P04` | Implement | 4 | Build a bounded, failure-aware queue service with compatible shutdown. | [Practice brief](practice/README.md#py-con-030-p04-build-a-bounded-worker-service) |
| `PY-CON-030-P05` | Diagnose | 4 | Find and remove a two-resource deadlock while preserving atomic transfer. | [Practice brief](practice/README.md#py-con-030-p05-diagnose-opposing-transfers) |
| `PY-CON-030-P06` | Design | 5 | Choose synchronization, backpressure, and shutdown for an audit pipeline. | [Practice brief](practice/README.md#py-con-030-p06-design-a-production-audit-boundary) |

## 12. Interview prompts

Attempt one prompt at a time. Do not write or read a prepared answer before the attempt.

1. Two threads execute `if key not in cache: cache[key] = build()`. What is the invariant, where are the race windows, and what designs preserve it?
2. Compare `Lock` and `RLock`. Give one legitimate reentrant use and one case where switching to `RLock` only hides unclear ownership.
3. Why must a condition waiter recheck a predicate after notification? Explain the associated lock on both the waiter and notifier paths.
4. Choose among `Event`, `Condition`, `Semaphore`, `Barrier`, and `Queue` for configuration readiness, a three-connection limit, a one-slot buffer, a fixed test phase, and job delivery.
5. A bounded queue's `full()` returned `False`, but `put_nowait()` raised `Full`. Is that a bug? What contract should production code use?
6. What does `Queue.join()` prove, what does `Thread.join()` prove, and how can missing or early `task_done()` corrupt the distinction?
7. Design graceful queue shutdown for Python 3.14 and a Python 3.11-compatible equivalent. Where do blocked producers, accepted work, worker failures, and sentinels fit?
8. Two transfer functions acquire account locks in opposite directions. Diagnose the wait cycle and compare global ordering, one coordinator lock, and single-owner message passing.
9. A team relies on the GIL and atomic dictionary updates. How do you move the review from implementation folklore to the actual multi-step invariant and free-threaded portability?
10. A lock timeout fired after a partial operation. What can the caller conclude, and which recovery guarantees must come from the application or external system?

A strong answer should eventually demonstrate:

- whole-invariant reasoning and deterministic race reproduction;
- exact primitive semantics, ownership, predicates, task accounting, and shutdown;
- deadlock prevention through structural ownership and ordering rather than scheduler hope;
- bounded capacity, deadlines, failure delivery, observability, and external atomicity;
- correct separation of standard-library contracts, CPython implementation details, and version-specific behavior.

## 13. Closed-book revision cues

Without reading the note:

1. Draw the controlled lost-update interleaving and the locked repair.
2. State one sentence each for `Lock`, `RLock`, `Condition`, `Semaphore`, `Event`, `Barrier`, and `Queue`.
3. Reconstruct the condition timeline and explain why notification does not transfer an item.
4. Explain why `empty()`, `full()`, and `qsize()` cannot reserve a later queue operation.
5. Draw a two-lock cycle and remove it using one total acquisition order.
6. Compare graceful queue shutdown, immediate shutdown, and Python 3.11 sentinels.
7. Review one backend worker boundary for capacity, failure, deadline, shutdown, and external side effects.

## 14. Authoritative sources

Important claims are cited near the relevant paragraphs. Sources actually opened and read for this initialization:

1. [`threading` — lock, reentrant lock, condition, semaphore, event, and barrier objects](https://docs.python.org/3.14/library/threading.html), Python 3.14.7 documentation, accessed 2026-08-28.
2. [`queue` — synchronized queue classes, task accounting, and termination](https://docs.python.org/3.14/library/queue.html), Python 3.14.7 documentation, accessed 2026-08-28.
3. [Python support for free threading — thread safety](https://docs.python.org/3.14/howto/free-threading-python.html#thread-safety), Python 3.14.7 documentation, accessed 2026-08-28.
4. [Python 3.11 `threading` reference](https://docs.python.org/3.11/library/threading.html), Python 3.11.15 documentation, accessed 2026-08-28.
5. [Python 3.11 `queue` reference](https://docs.python.org/3.11/library/queue.html), Python 3.11.15 documentation, accessed 2026-08-28.

## 15. Open technical questions

- The standard-library contracts intentionally leave waiter fairness unspecified. A production design that requires bounded starvation needs a separately verified policy or higher-level component rather than an assumption about lock, condition, semaphore, or queue wake order.
