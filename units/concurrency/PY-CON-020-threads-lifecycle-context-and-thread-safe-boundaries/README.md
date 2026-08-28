# PY-CON-020 — Threads, lifecycle, context, and thread-safe boundaries

[Curriculum entry](../../../CURRICULUM.md#py-con-020) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-CON-020`

## Physical Notebook Core

### Problem this concept solves

A thread lets one process overlap several activities, but creating one also creates obligations: somebody must own its lifetime, observe its failure, decide what context it receives, and define how data may cross the shared-memory boundary.

### One-sentence mental model

> A `Thread` is a single-use activity handle: `start()` transfers control to a new thread, `join()` waits for termination, and correctness depends on explicit lifecycle, context, failure, and data-ownership boundaries.

### One important visual

```text
owner thread                                      worker thread

Thread(...) = NEW
     |
     +-- start() -------------------------------> ALIVE: run(target)
     |                                               |
     +-- join() waits -------------------------------+
     |                                               |
     +<------------------------------------------ TERMINATED

request Context -- copy or empty --> worker Context
owned input ------> worker ------> Result | Failure ------> owner
shared mutable state -------- requires a documented safe boundary
```

#### How to read this visual

Read the lifecycle from top to bottom. `start()` may occur once and begins a separate thread of control. `join()` is an action by an owner; it waits for termination but does not itself transport a return value or re-raise a worker exception. Then read the lower arrows as three separate boundary decisions: initial context, data/result transfer, and shared mutation.

#### Key insight

Starting work is only the first transition. A complete thread design also makes termination, failure, context propagation, and ownership observable to the code responsible for the worker.

#### Simplification or limitation

This is a conceptual state and ownership diagram, not an operating-system schedule or a CPython memory layout. It omits synchronization mechanics, memory-order details, interpreter shutdown phases, and native extension behavior. Locks, queues, races, and deadlocks receive full treatment in `PY-CON-030`.

### Governing rules or invariants

1. One `Thread` object may be started at most once; Python provides no safe general-purpose API to destroy, suspend, resume, interrupt, or forcibly stop it.
2. `join(timeout)` always returns `None`, so timeout detection requires `is_alive()`; joining does not collect a target return value or replace an explicit failure channel.
3. Context is a policy decision: thread-local attributes are per thread, while a `ContextVar` starts from an empty, copied, or build/flag-dependent `Context`.
4. Shared memory is not automatically a thread-safe API. Define who owns mutation, which invariant must remain whole, and how results and failures cross the boundary.

### Minimal example

```python
from queue import SimpleQueue
from threading import Thread

results: SimpleQueue[str] = SimpleQueue()


def load_name(user_id: int) -> None:
    results.put(f"user-{user_id}")


worker = Thread(name="profile-loader", target=load_name, args=(42,))
worker.start()
worker.join()
print(results.get())
```

Expected reasoning:

1. `start()`, not `run()`, creates the separate thread of control, and the non-daemon worker terminates when `load_name` returns.
2. `join()` establishes that the worker has terminated; `SimpleQueue` is the explicit result-transfer boundary instead of an undocumented shared mutation.

The [`queue` module](https://docs.python.org/3.14/library/queue.html) provides synchronized queues specifically for safe information exchange between threads. This unit uses that public boundary without teaching its synchronization mechanics, which belong to `PY-CON-030`.

### One failure or misconception

**Mistake:** “If a worker fails, `join()` raises that exception in the joining thread.”

**Correction:** An uncaught exception terminates the worker and is sent to `threading.excepthook()`. `join()` waits for termination and returns `None`. A caller that must react needs an explicit result/failure channel or a higher-level abstraction.

### Important trade-offs

- Direct threads expose lifecycle and naming clearly, but they provide no built-in result future, cancellation protocol, or worker-count bound.
- Thread-local or contextual state reduces parameter plumbing, but hidden inputs complicate testing and propagation across execution boundaries.
- Sharing objects avoids serialization, but ownership, synchronization, library contracts, and shutdown become part of correctness.

### Interview-revision cues

- Draw `NEW -> ALIVE -> TERMINATED` and explain the roles of `start()`, `run()`, `join()`, and `is_alive()`.
- Predict what the owner observes after a timed join and after an uncaught worker exception.
- Compare `threading.local()`, `ContextVar`, explicit arguments, and shared mutable state at a request-to-thread boundary.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Concurrency, parallelism, and asynchronous Python |
| Canonical ID | `PY-CON-020` |
| Learning outcome | Use `threading`, thread lifecycle, thread-local/context state, failure handling, and thread-safe boundaries |
| Hard prerequisites | `PY-CON-010`, `PY-ERR-030` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | Medium |
| Backend relevance | High |
| Depth | D3 |
| Scope | Standard library, CPython |
| Size | M |
| Evidence profile | E+C+D+X |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4, regular GIL-enabled build, Linux x86_64 |
| Last source audit | 2026-08-28 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Construct and manage a named `Thread` through creation, one-time start, liveness checks, timed or unbounded join, cooperative shutdown, and resource cleanup.
2. Make worker failure observable and distinguish `threading.excepthook()` from application-level result and error delivery.
3. Choose deliberately among explicit arguments, `threading.local()`, `ContextVar` with explicit `Context` propagation, immutable snapshots, message transfer, and synchronized shared state.
4. Review a backend thread boundary for lifecycle ownership, bounded capacity, client thread-safety, context leakage, failure handling, and graceful shutdown.

Required evidence:

- Reconstruct the lifecycle and boundary visual, then explain every transition and non-transition without treating `join()` as result retrieval or cancellation.
- Complete at least one predict/debug exercise and one implementation/design exercise in [the practice brief](practice/README.md), preserving the initial attempt.
- Run and interpret [EXP-01](experiments/EXP-01-thread-context-boundaries/README.md), including why omitted context is not a portable propagation policy in Python 3.14.
- Diagnose one unsafe thread boundary and state the smallest invariant, ownership transfer, or documented thread-safe API needed to repair it.

Initialization creates the scaffold and records source/runtime observations. It does not satisfy learner evidence or advance the learning state.

## 2. Prerequisite bridge

Both hard prerequisites are currently unlearned. These bridges permit useful study but do not replace their dedicated units.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-CON-010` — Concurrency, parallelism, scheduling, and the GIL model | Thread usefulness and safety depend on workload, scheduling, and the interpreter build. | Concurrency means overlapping progress, not necessarily simultaneous execution. Regular CPython serializes Python-bytecode execution with the GIL but releases it around blocking operations; neither fact protects a multi-step application invariant. |
| Hard | `PY-ERR-030` — Context managers and resource safety | Threads often own sockets, files, transactions, and shutdown signals whose cleanup must survive errors. | A resource owner pairs acquisition with cleanup using `try/finally` or a context manager. Cleanup must be driven by the owning code; daemon shutdown is not a cleanup protocol. |

Recommended follow-up: initialize dedicated chats for both prerequisites, especially `PY-ERR-030` before implementing a reusable worker context manager.

## 3. Vocabulary and professional English

### Lifecycle

| Item | Content |
|---|---|
| Pronunciation | LYFE-sy-kul |
| Simple English meaning | The stages something passes through from creation to end |
| Hindi cue | जीवन-चक्र |
| Meaning in this Python context | The states and transitions of a `Thread` from construction through termination |

Natural examples:

1. The worker lifecycle begins before its target runs.
2. A lifecycle owner waits for shutdown and releases resources.
3. The test records the thread before start, while alive, and after termination.
4. **Interview:** “I would define lifecycle ownership before discussing worker code.”
5. **Engineering discussion:** “The service lifecycle must stop accepting work before joining its workers.”

### Propagate

| Item | Content |
|---|---|
| Pronunciation | PROP-uh-gayt |
| Simple English meaning | Carry information from one place or layer to another |
| Hindi cue | आगे पहुँचाना |
| Meaning in this Python context | Deliberately make context, results, or failures visible across a thread boundary |

Natural examples:

1. The adapter propagates the request identifier to the worker.
2. The error did not propagate to the joining thread automatically.
3. An explicit `Context` makes the propagation rule testable.
4. **Interview:** “In Python 3.14 I would not assume `ContextVar` propagation when `context` is omitted.”
5. **Engineering discussion:** “We propagate a correlation ID, not an entire mutable request object.”

### Boundary

| Item | Content |
|---|---|
| Pronunciation | BOWN-duh-ree |
| Simple English meaning | A line that defines where responsibility or rules change |
| Hindi cue | सीमा |
| Meaning in this Python context | The API through which ownership, state, results, failures, or context cross between threads |

Natural examples:

1. The queue forms a result-transfer boundary.
2. The database client is not documented as safe across that boundary.
3. Immutable input narrows the shared-state surface.
4. **Interview:** “Thread safety is a property of the whole boundary and invariant, not just one list operation.”
5. **Engineering discussion:** “The boundary owns timeout reporting even though Python cannot forcibly cancel the call.”

## 4. Deep explanation

### 4.1 Why the mechanism exists

Operating-system threads let a process host multiple independently scheduled flows that share the same address space. In backend Python, that can overlap blocking database, socket, file, or legacy-client calls without serializing every object across a process boundary. The benefit is most plausible when useful work can run while another thread waits; `PY-CON-010` owns the workload and GIL model.

The shared address space removes a communication barrier, not a correctness barrier. A worker can see the same objects, module globals, clients, file descriptors, and process state as its creator. That convenience expands the surface where lifetime, mutation, failure, and hidden context can escape their intended owner.

### 4.2 Thread construction and the single-use lifecycle

`threading.Thread` accepts a target, positional and keyword arguments, a diagnostic name, a daemon policy, and—since Python 3.14—an initial `context`. Calling `start()` arranges for `run()` to execute in a separate thread. Calling `run()` directly is just an ordinary method call in the current thread. A `Thread` may be started at most once; a second `start()` raises `RuntimeError`. The object is alive from just before `run()` begins until just after it returns or ends with an uncaught exception. See [`Thread` objects and lifecycle](https://docs.python.org/3.14/library/threading.html#thread-objects).

Python's high-level `Thread` API intentionally has no general operation to destroy, stop, suspend, resume, or interrupt another thread. Cooperative termination therefore needs a protocol the target checks, normally with a signal such as an `Event` and cleanup in `finally`. A signal requests termination; it cannot undo a blocking call whose library exposes no timeout or cancellation facility.

### 4.3 Joining is completion observation, not result transport

`join()` blocks the caller until the target thread terminates or the optional timeout elapses. It always returns `None`, so the correct timeout test is `worker.is_alive()` after the call. Joining the current thread or a thread that has not started raises `RuntimeError`; joining an already terminated thread and joining a thread more than once are allowed. In Python 3.14, joining a running daemon thread during late interpreter finalization may raise `PythonFinalizationError`. See [`Thread.join()`](https://docs.python.org/3.14/library/threading.html#threading.Thread.join).

The wait tells the owner about termination. It does not expose the target's return value, turn timeout into cancellation, or automatically raise a worker exception in the owner. Use a documented thread-safe result/failure channel, a deliberately owned result object, or a higher-level future abstraction when callers need those semantics.

### 4.4 Failure has two audiences

When `Thread.run()` ends with an uncaught exception, Python invokes `threading.excepthook(args)`. The default hook ignores `SystemExit` and prints other uncaught failures to standard error. A custom hook can add logging or metrics, but retaining `exc_value` can create a reference cycle and retaining the `thread` object can resurrect an object being finalized. Prefer copying a small immutable summary and returning from the hook. See [`threading.excepthook()`](https://docs.python.org/3.14/library/threading.html#threading.excepthook).

An exception hook serves process-level observability. Application control flow still needs a result contract: which operation failed, whether partial data exists, whether the caller should retry, and how the owner decides success. Logging a failure is not the same as delivering it to the request that depends on it.

### 4.5 Daemon is an exit rule, not a service design

The process exits when no alive non-daemon threads remain. A thread created by the main thread defaults to non-daemon; a child otherwise inherits the creating thread's daemon flag unless explicitly set. Daemon threads can be stopped abruptly during interpreter shutdown, so open files, transactions, and other resources may not be released properly. The standard-library guidance is to use non-daemon workers and an explicit signal for graceful stopping when cleanup matters. See [daemon-thread behavior](https://docs.python.org/3.14/library/threading.html#thread-objects).

Therefore “background” and “daemon” are not synonyms. Long-lived background work can be non-daemon and explicitly owned. Short-lived daemon work can still corrupt an external operation if abrupt exit splits its invariant.

### 4.6 Thread-local state and logical context

`threading.local()` gives each accessing thread a separate attribute dictionary. It is useful for state whose lifetime and identity truly follow one OS thread, such as an adapter-managed per-thread client. Saving one thread's `__dict__` for use elsewhere is unsafe because the view belongs to the thread current at access time. A subtle exception is subclass `__slots__`: slot attributes are shared rather than thread-local. See [thread-local data](https://docs.python.org/3.14/library/threading.html#thread-local-data).

A `ContextVar` belongs to the currently entered `Context` rather than directly to the `Thread` object. Each thread has a stack of entered contexts. `copy_context()` returns a copy of the current bindings in O(1), while `Context()` is empty. A `Context` cannot be entered simultaneously in two threads; attempting that raises `RuntimeError`. See [manual context management](https://docs.python.org/3.14/library/contextvars.html#manual-context-management).

Python 3.14 added `Thread(context=...)`:

- pass `copy_context()` to start from an explicit snapshot;
- pass `Context()` to start empty;
- omit `context` to follow `sys.flags.thread_inherit_context`.

The flag defaults to false on regular GIL-enabled builds and true on free-threaded builds, and it can be changed at interpreter startup. Thus omission makes behavior depend on runtime configuration. Explicit context is the maintainable boundary for code that must behave the same in tests and deployment. See [the `Thread` constructor](https://docs.python.org/3.14/library/threading.html#threading.Thread) and [free-threaded context behavior](https://docs.python.org/3.14/howto/free-threading-python.html#context-variables).

Python 3.11 has `ContextVar`, `Context`, and `copy_context()` but no `Thread(context=...)` parameter. Its explicit equivalent is to make the target `copied_context.run(worker)`. The worked example uses a compatibility helper for exactly that reason.

### 4.7 What makes a boundary thread-safe

Thread safety is not proved by showing that one low-level operation happened to be indivisible on one CPython build. The boundary must preserve the application invariant across every read, decision, blocking call, mutation, cleanup step, and failure path that belongs together.

Useful boundary shapes include:

1. **Confinement:** one thread owns a mutable client or object; other threads never touch it.
2. **Immutable snapshot:** workers receive values that do not change while in use.
3. **Message transfer:** a documented thread-safe channel moves jobs, results, and failures.
4. **Synchronized invariant:** a deliberately small critical region protects all shared state that must change together.
5. **External atomic operation:** the database or service enforces the invariant through a transaction, conditional update, or idempotency key.

The regular CPython GIL is an implementation mechanism around Python execution, not an application transaction. CPython can switch between bytecode instructions and releases the GIL around blocking I/O; an attached thread state remains necessary even on free-threaded builds. See [CPython thread states and the GIL](https://docs.python.org/3.14/c-api/threads.html#thread-states-and-the-global-interpreter-lock).

Free-threaded CPython uses internal locks for built-in containers to provide behavior similar to the regular build, but the documentation explicitly says concurrent-modification behavior has not historically been a Python guarantee and recommends synchronization rather than reliance on internal locks. See [free-threaded Python thread safety](https://docs.python.org/3.14/howto/free-threading-python.html#thread-safety). `PY-CON-030` develops synchronization, queues, races, and deadlocks in depth.

### 4.8 Execution sequence

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Owner constructs `Thread` with target, name, daemon policy, arguments, and context policy. | Thread exists, is not alive, and has no `ident` yet. |
| 2 | Owner calls `start()` exactly once. | Runtime arranges a new thread of control; target may begin at any later scheduling opportunity. |
| 3 | Worker runs using its initial `Context` and per-thread local view. | Worker is alive; shared-object access follows the boundary's safety contract. |
| 4 | Target returns or raises an uncaught exception. | On uncaught failure, `threading.excepthook()` runs; then the worker ceases to be alive. |
| 5 | Owner's `join()` returns, or a timed join returns while the worker is still alive. | Owner must inspect `is_alive()` and retrieve any result/failure through its explicit channel. |
| 6 | Owner performs downstream use and cleanup. | Lifecycle is complete only when owned resources and failure policy are resolved. |

## 5. Additional visual model

### Three planes of a thread boundary

```text
CONTROL PLANE: owner -- start --> worker -- terminate --> owner observes with join

DATA PLANE:    immutable job --> worker --> Result | Failure message --> owner

CONTEXT PLANE: request bindings -- explicit snapshot/empty policy --> worker bindings

Unsafe shortcut: owner ====== arbitrary shared mutable object ====== worker
                                  no owner, no whole invariant
```

#### How to read this visual

Read each horizontal lane independently. Control answers who owns lifetime. Data answers how useful outcomes move. Context answers which ambient bindings are visible. The bottom line shows a shared object crossing without an ownership or synchronization contract.

#### Key insight

`join()` solves only one control-plane question. It cannot substitute for a data-plane error contract or a context-propagation policy.

#### Simplification or limitation

The lanes are conceptual. Real APIs may combine them—for example, a higher-level future combines completion and result delivery—and immutable values can still reference mutable objects. The visual does not prescribe a particular queue or lock.

## 6. Worked examples

All observed outputs below were captured on CPython 3.14.4, regular GIL-enabled build, Linux x86_64, on 2026-08-28.

### 6.1 Controlled lifecycle

Run [`examples/thread_lifecycle.py`](examples/thread_lifecycle.py):

```bash
python units/concurrency/PY-CON-020-threads-lifecycle-context-and-thread-safe-boundaries/examples/thread_lifecycle.py
```

Observed:

```text
new: alive=False, ident=None
running: alive=True
terminated: alive=False
outcome: profile-loader -> profile-42
```

The two `Event` objects are test controls: one proves the worker reached an alive waiting point and the other allows termination. The `Queue` transfers one immutable outcome. This example demonstrates lifecycle; it does not teach the synchronization primitives owned by `PY-CON-030`.

### 6.2 Uncaught failure reporting

Run [`examples/failure_reporting.py`](examples/failure_reporting.py):

```bash
python units/concurrency/PY-CON-020-threads-lifecycle-context-and-thread-safe-boundaries/examples/failure_reporting.py
```

Observed:

```text
join returned normally
worker alive: False
captured: payment-worker RuntimeError: synthetic payment failure
```

The temporary hook copies only a thread name, exception type, and message into an immutable summary, then the original process-wide hook is restored in `finally`. The trace demonstrates that termination and failure delivery are different contracts. A production hook must also be installed centrally because `threading.excepthook` is process-wide mutable state.

### 6.3 Explicit context and thread-local isolation

Run [`examples/context_boundaries.py`](examples/context_boundaries.py):

```bash
python units/concurrency/PY-CON-020-threads-lifecycle-context-and-thread-safe-boundaries/examples/context_boundaries.py
```

Observed:

```text
empty: context=UNSET, tls_before=UNSET, tls_after=worker:empty
snapshot: context=request-at-snapshot, tls_before=UNSET, tls_after=worker:snapshot
main: context=request-in-main-after-snapshot, tls=main
```

The copied context contains the binding from copy time, not the later main-thread binding. The empty context contains neither. Both workers begin without the main thread's `threading.local` attribute, and their assignments do not replace the main thread's value. The compatibility helper uses `Thread(context=...)` on 3.14 and `context.run(target)` on 3.11.

### 6.4 Realistic backend boundary

```python
from dataclasses import dataclass
from queue import Queue
from threading import Thread


@dataclass(frozen=True)
class LookupResult:
    key: str
    value: str | None = None
    error: str | None = None


def lookup(key: str, results: Queue[LookupResult]) -> None:
    try:
        value = blocking_client_lookup(key)
    except Exception as exc:
        results.put(LookupResult(key=key, error=f"{type(exc).__name__}: {exc}"))
    else:
        results.put(LookupResult(key=key, value=value))


results: Queue[LookupResult] = Queue()
workers = [
    Thread(name=f"lookup-{key}", target=lookup, args=(key, results))
    for key in ("profile", "orders")
]
for worker in workers:
    worker.start()
for worker in workers:
    worker.join()
```

Why this is only a starting design:

- job keys are immutable and each worker publishes one explicit result or failure;
- the owner starts and joins every non-daemon worker;
- the client must still document concurrent use as safe, or each worker must own a separate client;
- sequential unbounded joins do not implement a request deadline or cancellation;
- direct one-thread-per-call creation has no capacity bound;
- exception text may be appropriate for internal evidence but must not leak sensitive details to an external response.

For repeated work, `ThreadPoolExecutor` and futures belong to `PY-CON-050`. For queues, backpressure, locks, and shutdown signaling, continue with `PY-CON-030`.

### 6.5 Debugging example: fire-and-forget persistence

Keep the correction hidden until an attempt.

```python
def accept_audit_event(event: dict[str, object]) -> str:
    def write_later() -> None:
        request_client.write(event)

    Thread(target=write_later, daemon=True).start()
    return "accepted"
```

Before changing code:

1. List every unowned lifecycle, data, client, failure, and shutdown assumption.
2. Decide what “accepted” promises to the caller.
3. Identify whether `event` and `request_client` may be accessed safely after the function returns.
4. Propose the smallest boundary that makes the promise testable, without writing the final implementation yet.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| Calling `worker.run()` starts a thread. | `run` contains the target invocation. | Direct `run()` executes in the caller; only `start()` creates the separate control flow. | Record `current_thread().name` inside the target for direct `run()` and `start()` cases. |
| A `Thread` can be restarted after it terminates. | The Python object still exists. | One object has one start transition; create a new `Thread` for a new activity. | Call `start()` twice and predict the `RuntimeError` boundary. |
| `join(timeout)` returns a success boolean. | Many timeout APIs do. | It always returns `None`; check `is_alive()` afterward. | Join a worker held at a controlled event with a zero timeout. |
| `join()` re-raises the worker exception. | The owner waits at the failure point. | The uncaught failure goes to `threading.excepthook()`; join observes termination. | Run `failure_reporting.py`. |
| Timeout means the worker was cancelled. | The owner's wait ended. | Only the wait ended; the target may still be running and using resources. | Hold a worker, time out, inspect `is_alive()`, then release and join it. |
| Daemon means managed background service. | Both terms describe non-request foreground work. | Daemon is an interpreter-exit rule and permits abrupt stopping. | Run a subprocess whose daemon delays a flush; never use the outcome as a production protocol. |
| Thread names or IDs are permanent unique identities. | They appear in logs and system tools. | Names need not be unique; `ident` and native IDs may be recycled after termination. | Create sequential short-lived workers and treat IDs only as diagnostic values. |
| Every attribute of a `threading.local` subclass is local. | The instance is thread-local. | Attributes backed by subclass `__slots__` are shared across threads. | Compare a normal attribute with a slot attribute in a controlled experiment. |
| `ContextVar` always propagates to a new thread. | It propagates naturally across many async task boundaries. | In Python 3.14, omitted thread context follows a runtime flag whose default differs by build. | Run EXP-01 with the flag set to zero and one. |
| A copied context creates deep copies of bound objects. | The word “copy” suggests data duplication. | The context binding is copied; a mutable value can still be the same shared object. | Bind a list, copy the context, and compare identity without mutating it concurrently. |
| The same `Context` can run in several threads at once. | A context looks like a read-only configuration snapshot. | Entering an already entered `Context` raises `RuntimeError`. | Hold one `Context.run` active and attempt to enter it from another controlled thread. |
| The regular GIL makes a compound invariant safe. | Only one thread runs Python bytecode at an instant. | Switches and blocking calls can separate the invariant's steps; free-threaded builds increase simultaneous execution. | Draw the full read/validate/write sequence and mark every possible blocking boundary. |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| `copy_context()` | O(1) | This is the documented binding-copy complexity, not a deep copy of bound values. |
| Construct/start one OS thread | Non-trivial startup plus per-thread runtime/stack resources | Exact time and memory are platform, build, stack-size, and workload dependent; no measurement is claimed here. |
| `join()` without timeout | Blocks until termination | Waiting cost is dominated by remaining worker lifetime and scheduling; it performs no useful cancellation. |
| `threading.local` attribute access | Per-access lookup in thread-specific state | Treat exact constants and implementation structure as runtime details. |
| One thread per request or subcall | Resource use grows with concurrent calls | Unbounded creation can exhaust memory, file descriptors, connections, or downstream capacity. |
| Message/result boundary | Adds allocation and coordination cost | It reduces ambiguous shared mutation and gives the owner a place to define failure and shutdown. |

Do not benchmark thread creation or throughput with `sleep` alone and generalize it to a backend. A useful measurement records the client behavior, blocking fraction, worker bound, machine, interpreter build, downstream limit, latency distribution, failures, and trial policy.

## 9. Production relevance and trade-offs

Review a thread boundary in this order:

| Concern | Question |
|---|---|
| Ownership | Which component creates, tracks, signals, joins, and finally releases the worker? |
| Capacity | What bounds live threads, queued jobs, connections, memory, and downstream concurrency? |
| Data | Is input immutable, confined, transferred, or protected as one complete invariant? |
| Client safety | Does the library explicitly permit this object, session, cursor, or connection to be used from multiple threads? |
| Context | Which request, trace, locale, authentication, or warning context is copied, cleared, or passed explicitly? |
| Failure | How does an uncaught exception reach both observability and the caller whose result depends on it? |
| Deadline | Does every blocking operation have a usable timeout, and what happens when the owner's wait expires? |
| Shutdown | Does the service stop admission, signal workers, drain or reject jobs, join, and clean resources in a defined order? |
| Observability | Are names, job IDs, durations, failure summaries, queue depth, and stuck-worker evidence available without storing sensitive data? |
| Portability | Which claims are standard-library contracts, regular-CPython observations, free-threaded behavior, or platform-specific details? |

Avoid holding a lock across unknown application callbacks, remote I/O, or logging unless the invariant truly requires it and the consequences are understood. Avoid putting request-scoped mutable clients into global or thread-local state merely to avoid parameters. Prefer the smallest explicit boundary that makes misuse difficult and shutdown testable.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| `Thread(target=..., daemon=...)`, one-time `start`, `join`, and `is_alive` | Standard library | Long-standing; daemon constructor argument 3.3 | Same core API | Availability excludes WASI; scheduling and OS resources remain platform dependent. |
| `threading.excepthook` | Standard library | 3.8 | Same API | It is process-wide mutable policy; do not retain exception or thread objects unnecessarily. |
| `Thread(context=...)` | Standard library, version-dependent | 3.14 | Use `Thread(target=copied_context.run, args=(worker,))` or another small wrapper. | Pass `Context()` or `copy_context()` explicitly when behavior must not depend on flags. |
| `sys.flags.thread_inherit_context` and its command/environment controls | CPython/runtime configuration | 3.14 | No equivalent flag; propagate with `Context.run` explicitly. | Default is true on free-threaded builds and false otherwise. |
| Setting the OS thread name during `start()` | Standard library plus platform behavior | 3.14 | Python-level `Thread.name` remains available. | OS names may be truncated; changing another thread's Python name may not update the OS name. |
| `PythonFinalizationError` from late joining of a running daemon | Standard library, finalization boundary | 3.14 | Design normal shutdown before finalization; 3.11 has no equivalent documented join exception. | Do not make late daemon joins a cleanup strategy. |
| `ContextVar.Token` used as a context manager | Standard library | 3.14 | Save the token and call `reset(token)` in `finally`. | This is separate from thread context propagation. |
| Optional free-threaded CPython build | CPython, version-dependent | 3.13 | Regular CPython 3.11 uses the GIL-enabled model. | Built-in internal locks are not a substitute for application synchronization. |
| `get_native_id()` and `Thread.native_id` | Standard library plus platform availability | 3.8 | Available on supported Python 3.11 platforms. | IDs may be recycled after a thread terminates; use them diagnostically. |

For a Python 3.11 interview, lead with the stable lifecycle and failure model. Then label `Thread(context=...)`, the inheritance flag, OS-name propagation, and `PythonFinalizationError` as Python 3.14 additions.

## 11. Practice brief

Exercises are specified without solutions in [`practice/README.md`](practice/README.md).

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-CON-020-P01` | Predict | 2 | Predict direct `run`, one-time `start`, timed join, liveness, and exception-hook observations. | [Practice brief](practice/README.md#py-con-020-p01-predict-a-controlled-lifecycle) |
| `PY-CON-020-P02` | Implement | 3 | Build an owned non-daemon worker with cooperative stop, bounded waits, cleanup, and recorded failure. | [Practice brief](practice/README.md#py-con-020-p02-implement-an-owned-worker) |
| `PY-CON-020-P03` | Debug | 3 | Find the first false assumption in a daemon fire-and-forget persistence boundary. | [Practice brief](practice/README.md#py-con-020-p03-debug-fire-and-forget-persistence) |
| `PY-CON-020-P04` | Implement | 4 | Propagate or clear request context explicitly on Python 3.14 and with a Python 3.11-compatible path. | [Practice brief](practice/README.md#py-con-020-p04-make-context-policy-explicit) |
| `PY-CON-020-P05` | Design | 4 | Define a safe backend fan-out boundary including capacity, ownership, results, errors, deadlines, and shutdown. | [Practice brief](practice/README.md#py-con-020-p05-design-a-backend-thread-boundary) |

## 12. Interview prompts

Attempt one prompt at a time; do not read or write a prepared answer before the attempt.

1. What exact state transitions occur from constructing a `Thread` through `start()`, target failure, and `join()`? State what `join()` does not do.
2. A timed `join(0.2)` returned `None`. What can the caller conclude, what must it inspect next, and why is this not cancellation?
3. Compare `threading.local()` and `ContextVar` when a request handler starts a thread in Python 3.14. Which propagation policy would you choose and why?
4. A daemon thread writes audit events after the request returns. Identify the lifecycle and correctness risks before proposing a replacement.
5. A team says a shared dictionary is safe because CPython protects dictionaries and has a GIL. How would you test the claim and move the discussion to the actual invariant?

A strong answer should eventually demonstrate:

- the single-use lifecycle, liveness interval, join timeout check, cooperative shutdown, and daemon boundary;
- separate observability and application failure channels;
- explicit context propagation and the Python 3.11/3.14 difference;
- ownership, whole-invariant reasoning, client contracts, bounded resources, and free-threaded portability.

## 13. Closed-book revision cues

Without reading the note:

1. Draw the `NEW -> ALIVE -> TERMINATED` lifecycle and label every invalid transition.
2. Explain why `run()`, `start()`, `join()`, timeout, cancellation, and result retrieval are six different ideas.
3. Reconstruct the three-plane boundary visual: control, data, and context.
4. Predict both EXP-01 runs when `thread_inherit_context` is zero and one.
5. Explain the `threading.local.__slots__` trap and why a copied `Context` is not a deep copy.
6. Review a one-thread-per-request proposal for capacity, client safety, failure, deadlines, and shutdown.

## 14. Authoritative sources

Important claims are cited near the relevant paragraphs. Sources actually opened and read for this initialization:

1. [`threading` — thread objects, lifecycle, daemon behavior, exception hooks, and thread-local data](https://docs.python.org/3.14/library/threading.html), Python 3.14.7 documentation, accessed 2026-08-28.
2. [`contextvars` — manual context management](https://docs.python.org/3.14/library/contextvars.html#manual-context-management), Python 3.14.7 documentation, accessed 2026-08-28.
3. [`sys.flags.thread_inherit_context`](https://docs.python.org/3.14/library/sys.html#sys.flags.thread_inherit_context), Python 3.14.7 documentation, accessed 2026-08-28.
4. [Python support for free threading — thread safety and context variables](https://docs.python.org/3.14/howto/free-threading-python.html), Python 3.14.7 documentation, accessed 2026-08-28.
5. [Thread states and the global interpreter lock](https://docs.python.org/3.14/c-api/threads.html#thread-states-and-the-global-interpreter-lock), Python 3.14.7 C API documentation, accessed 2026-08-28.
6. [Python 3.11 `threading` reference](https://docs.python.org/3.11/library/threading.html#thread-objects), Python 3.11.15 documentation, accessed 2026-08-28.
7. [PEP 567 — Context Variables](https://peps.python.org/pep-0567/), final standards-track PEP, accessed 2026-08-28.
8. [`queue` — a synchronized queue class](https://docs.python.org/3.14/library/queue.html), Python 3.14.7 documentation, accessed 2026-08-28.
