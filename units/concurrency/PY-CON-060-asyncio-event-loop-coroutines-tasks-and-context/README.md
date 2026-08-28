# PY-CON-060 — Asyncio event loop, coroutines, tasks, and context

[Curriculum entry](../../../CURRICULUM.md#py-con-060) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-CON-060`

## Physical Notebook Core

### Problem this concept solves

A synchronous call stack cannot make useful progress while its current operation waits. An asynchronous program needs a way to pause one operation at an explicit waiting point, remember its execution state, run other ready work on the same thread, and resume the paused operation when its dependency becomes ready.

### One-sentence mental model

> A coroutine is a suspendable computation; a Task lets the event loop advance that computation until `await` produces a pending dependency, and the dependency's completion schedules the Task to continue.

### One important visual

```text
asyncio.run(main())
        |
        v
+--------------------------- event-loop thread ---------------------------+
|                                                                         |
|  ready callbacks --> Task A step --> await pending Future F             |
|       ^                              |                                   |
|       |                              v                                   |
|       |                         Task A suspended                          |
|       |                              |                                   |
|       +---- schedule Task A wakeup <--+---- F gets result/exception      |
|                                                                         |
|  while A waits: Task B step, callbacks, timers, and I/O readiness run   |
+-------------------------------------------------------------------------+

Task A's Python code and Task B's Python code do not run simultaneously
on this one loop thread; they cooperate by suspending at real wait points.
```

#### How to read this visual

Start at `asyncio.run(main())`, then follow one Task from the ready side into a coroutine step. If `await` finds a pending Future, that Task stops advancing and registers a wakeup. The loop can advance other ready work. When the Future reaches a terminal state, its callback places the Task's continuation back on the ready side.

#### Key insight

`await` does not mean “start a background thread.” It is a protocol for suspending and resuming a computation, and useful concurrency appears only when the current Task reaches an awaitable that actually suspends.

#### Simplification or limitation

This is a public-contract mental model with a CPython-shaped ready queue. It omits selectors versus proactors, transports, system calls, timer heaps, cancellation, structured task ownership, eager task start, alternative event loops, and the exact C implementation of `Task`. A completed awaitable may return without suspending, and Python 3.14 can explicitly start a task eagerly.

### Governing rules or invariants

1. Calling an `async def` function creates a coroutine object; it does not run or schedule the body.
2. On one event-loop thread, Tasks are cooperatively scheduled: one Task executes Python code until it returns, raises, or reaches an await that suspends.
3. Every created Task needs an owner that keeps a strong reference and eventually observes its value, exception, or cancellation.
4. An `asyncio.Future` is normally a low-level bridge whose completion wakes awaiters; application APIs should usually expose domain values or coroutines instead of mutable Futures.
5. A Task copies the current `contextvars.Context` when it is created unless an explicit context is supplied; later binding changes are task-local, but referenced mutable objects are not deep-copied.
6. Blocking the event-loop thread blocks every Task and I/O callback that depends on that loop.

### Minimal example

```python
import asyncio


async def worker(gate: asyncio.Event) -> int:
    print("worker: waiting")
    await gate.wait()          # suspends while the Event is unset
    print("worker: resumed")
    return 42


async def main() -> None:
    gate = asyncio.Event()
    task = asyncio.create_task(worker(gate), name="worker")
    await asyncio.sleep(0)     # give ready work a cooperative checkpoint
    print("owner: releasing")
    gate.set()
    print("owner: result", await task)


asyncio.run(main())
```

Expected reasoning:

1. `worker(gate)` creates a coroutine object; `create_task()` gives the loop ownership of advancing it and returns a Task handle to `main`.
2. The worker runs until `gate.wait()` is pending, then its Task suspends without blocking the loop thread.
3. `gate.set()` completes the internal wait condition and schedules the worker to resume; awaiting the Task lets the owner collect its terminal result.

### One failure or misconception

**Mistake:** “An `async def` call starts concurrently, and every `await` yields to the loop.”

**Correction:** Calling creates a dormant coroutine object. Directly awaiting it runs it within the current Task rather than creating a sibling Task. An await of an already-completed object can continue synchronously, so `await` is a possible suspension point, not a promise that another Task ran.

### Important trade-offs

- One event-loop thread can coordinate many waiting I/O operations with low per-Task overhead, but one blocking callback or CPU-heavy loop delays all of them.
- Cooperative scheduling makes suspension explicit and avoids many shared-thread races, but fairness depends on code reaching genuine suspension points.
- `create_task()` enables overlap and independent lifetime, but it also creates failure, cancellation, reference, and shutdown ownership that direct `await` does not create.
- `ContextVar` bindings make request context follow Tasks without threading arguments through every call, but hidden ambient state can obscure dependencies and mutable values can still be shared.

### Interview-revision cues

- Reconstruct: coroutine function → coroutine object → Task step → pending Future → wakeup → next Task step.
- Distinguish: coroutine, awaitable, Task, Future, callback, and event loop.
- Predict: direct `await` versus `create_task()`, pending versus completed awaitable, and default versus eager task start.
- Diagnose: forgotten await, unobserved task exception, loop-thread blocking, task-context leakage assumptions, and unsafe cross-thread loop calls.
- Choose: direct await for a dependency, an owned Task for concurrent lifetime, and a Future only at a low-level callback boundary.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Concurrency, parallelism, and asynchronous Python |
| Canonical ID | `PY-CON-060` |
| Learning outcome | Explain the `asyncio` event loop, coroutines, `await`, tasks, futures, scheduling, and `contextvars`. |
| Hard prerequisites | `PY-FIT-080`, `PY-ERR-030`, `PY-CON-010` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D3 |
| Scope | Standard library / CPython |
| Size | L |
| Evidence profile | E+C+D+X |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4, regular GIL-enabled build, Linux x86_64 |
| Last source audit | 2026-08-28 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. distinguish coroutine functions, coroutine objects, awaitables, Tasks, Futures, callback handles, and event loops by responsibility and lifecycle;
2. trace how a Task advances a coroutine, suspends on a pending dependency, is scheduled for wakeup, and exposes a terminal result or exception;
3. predict when direct `await`, task creation, a completed Future, `asyncio.sleep(0)`, and Python 3.14 eager start can or cannot transfer control;
4. use `asyncio.run()`, `get_running_loop()`, `create_task()`, loop-created Futures, and `ContextVar` bindings without leaking task lifetime or blocking the loop thread;
5. explain the public scheduling contract separately from CPython's default-loop ready-queue implementation and from alternative event loops.

Required evidence:

- reconstruct the core visual and narrate the coroutine/Task/Future handoff without reading;
- complete prediction, implementation, debugging, context-isolation, and ownership practice while preserving the first attempt;
- run the lifecycle, Future-bridge, and task-context examples with deterministic tests;
- reproduce and classify the Python 3.14 eager-start experiment, including why its exact interleaving is version- and implementation-sensitive;
- review a backend async boundary for task ownership, blocking work, context, exception observation, and shutdown responsibility.

Initialization created source-audited material, runnable examples, deterministic tests, and one interpreted experiment. It did not provide learner attempts, recall, or review evidence, so the learning state remains `Not started` and the artifact remains `Draft`.

## 2. Prerequisite bridge

The tracker records no learner evidence for any hard prerequisite; two prerequisite artifacts are absent. These bridges are the minimum assumptions needed to enter the unit and do not complete those units.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-FIT-080` — Generators, yield, and delegation | Coroutines are resumable computations, and `await` is defined through the awaitable protocol rather than as a thread primitive. | A suspended function retains its frame state. Advancing sends a value or exception in; yielding transfers control out. Native coroutines are distinct from ordinary generators, but suspension/resumption is the essential bridge. |
| Hard | `PY-ERR-030` — Context managers and resource safety | Event-loop runners, task owners, adapters, and context-variable bindings all have cleanup boundaries that must survive exceptional exit. | The component acquiring a resource owns deterministic release, normally through `try/finally` or a context manager. An exception does not erase already-acquired resources or accepted work. |
| Hard | `PY-CON-010` — Concurrency, parallelism, scheduling, and the GIL model | `asyncio` provides concurrency through cooperative scheduling, not automatic CPU parallelism. | Concurrency means lifetimes overlap; parallelism means execution occurs simultaneously. One event-loop thread interleaves Tasks at suspension points, and CPU-heavy Python code on that thread prevents other Tasks from advancing. |

Recommended follow-up: study all three prerequisites in their dedicated topic chats. Continue here by treating these bridges as explicit assumptions.

## 3. Vocabulary and professional English

### Coroutine

| Item | Content |
|---|---|
| Pronunciation | koh-roo-TEEN |
| Simple English meaning | A computation that can pause and later continue from saved state. |
| Hindi cue | रुककर वहीं से फिर चलने वाली computation |
| Meaning in this Python context | Usually an `async def` function or the coroutine object returned by calling it; the object must be awaited, scheduled, or explicitly closed. |

Natural examples:

1. Calling the coroutine function produced an object but did not execute its body.
2. This coroutine suspends while the socket is not readable.
3. The Task owns advancement of the coroutine.
4. **Interview:** Directly awaiting a coroutine does not automatically create another Task.
5. **Engineering discussion:** The public method returns a coroutine whose lifetime remains inside the request Task.

### Suspend

| Item | Content |
|---|---|
| Pronunciation | suh-SPEND |
| Simple English meaning | Pause while keeping enough state to continue later. |
| Hindi cue | अस्थायी रूप से रोकना |
| Meaning in this Python context | Stop advancing a coroutine because an awaitable is pending, while preserving its frame and arranging a future wakeup. |

Natural examples:

1. The handler suspends until a response is available.
2. Awaiting an already-done Future did not suspend this time.
3. Suspension is not thread blocking.
4. **Interview:** `await` marks a possible suspension point, not a guaranteed context switch.
5. **Engineering discussion:** Add a real asynchronous wait; a decorative `async def` does not make this blocking client cooperative.

### Cooperative

| Item | Content |
|---|---|
| Pronunciation | koh-OP-er-uh-tiv |
| Simple English meaning | Participants deliberately give others a chance to proceed. |
| Hindi cue | मिलकर स्वेच्छा से control देना |
| Meaning in this Python context | A Task keeps the loop thread until it reaches an operation that suspends, so application code must avoid blocking and yield through real async boundaries. |

Natural examples:

1. The scheduler is cooperative rather than preempting the Task at arbitrary Python instructions.
2. A long CPU loop needs chunking, offloading, or another execution design.
3. One cooperative checkpoint let the ready callback run.
4. **Interview:** Cooperative scheduling reduces arbitrary interleavings but does not eliminate shared-state bugs across awaits.
5. **Engineering discussion:** This parser is synchronous and monopolizes the cooperative loop under large inputs.

### Ambient context

| Item | Content |
|---|---|
| Pronunciation | AM-bee-uhnt KON-tekst |
| Simple English meaning | Information available implicitly around an operation. |
| Hindi cue | आसपास उपलब्ध implicit context |
| Meaning in this Python context | Task-associated `ContextVar` bindings such as a request ID that code can read without receiving an explicit argument. |

Natural examples:

1. The logger reads the request ID from ambient context.
2. The child Task captured the binding at creation time.
3. Reset the token when leaving the temporary binding scope.
4. **Interview:** Context isolation copies bindings, not the mutable objects stored as values.
5. **Engineering discussion:** Keep authorization inputs explicit even if tracing metadata uses ambient context.

## 4. Deep explanation

### 4.1 Why the mechanism exists

Network servers spend much of their lifetime waiting for sockets, timers, subprocess pipes, or coordination primitives. One operating-system thread per wait can work, but thread stacks, synchronization, shared state, and capacity grow with concurrency. `asyncio` instead lets one event-loop thread watch readiness sources and advance many explicitly suspendable computations.

This is an execution model, not a speed annotation. An `async def` body that performs blocking file, database, HTTP, DNS, or CPU work directly still occupies the loop thread. The official development guide states that blocking CPU work called directly delays every concurrent Task and I/O operation on that loop; executor and thread boundaries are deliberate escape hatches, not automatic behavior. See [Developing with asyncio — Running Blocking Code](https://docs.python.org/3.14/library/asyncio-dev.html#running-blocking-code).

### 4.2 The layers and their responsibilities

| Object or concept | What it is | What makes progress | Owner-visible boundary |
|---|---|---|---|
| Coroutine function | Function declared with `async def` | Nothing; it is a callable definition | Calling it creates a coroutine object |
| Coroutine object | One suspendable invocation with frame state | Direct `await` or a Task advancing it | Produces one return value or exception; cannot be reused after completion |
| Awaitable | Object accepted by `await`, with an `__await__()` protocol | The surrounding Task drives its iterator | May complete immediately or suspend |
| Task | Future-like scheduler/owner for one coroutine | Event loop invokes Task steps | Can be awaited and inspected for result, exception, cancellation, name, stack, and context |
| `asyncio.Future` | Loop-bound placeholder for one eventual result | A producer callback or low-level API calls `set_result()` or `set_exception()` | Awaiters suspend until terminal; repeated awaits return the same outcome |
| Callback handle | One scheduled ordinary callable plus arguments and context | Event loop invokes it when ready | No coroutine suspension inside the callback itself |
| Event loop | Scheduler plus I/O, timer, callback, Future, and Task integration | A runner repeatedly polls and executes ready handles | Normally owned through `asyncio.run()` or `asyncio.Runner` |

The standard documentation deliberately calls Future a low-level bridge between callback-based code and `async`/`await`, recommends `loop.create_future()` so alternative loops can provide their own implementation, and advises against exposing Futures in user-facing APIs. See [`asyncio` Futures](https://docs.python.org/3.14/library/asyncio-future.html).

`asyncio.Future` and `concurrent.futures.Future` are not interchangeable. The asyncio type is loop-bound, awaitable, and not thread-safe. The concurrent-futures type represents executor work and has blocking collection methods; use documented adapters such as `asyncio.wrap_future()` or loop executor APIs at the boundary.

### 4.3 What `await` means

The language reference defines `await expression` as suspending a coroutine on an awaitable and permits it only inside a coroutine function. At the protocol level, the awaitable supplies an iterator through `__await__()`; the surrounding Task advances the coroutine/awaitable chain until it returns, raises, or yields a pending dependency. See the [await-expression reference](https://docs.python.org/3.14/reference/expressions.html#await-expression) and [PEP 492](https://peps.python.org/pep-0492/).

Three cases must stay separate:

1. `result = await child()` directly composes `child` into the current Task. The caller cannot advance past that expression until the child returns, although the Task may suspend while the child waits.
2. `task = asyncio.create_task(child())` creates an independently scheduled Task. The creator continues until it next suspends, unless eager task start is selected.
3. `result = await done_future` normally retrieves the stored terminal outcome without suspending. The syntax contains `await`, but this execution has no need to yield.

`asyncio.sleep(0)` is a documented optimized path that always suspends the current Task and lets other ready work run. It is useful for a deliberate checkpoint, but adding it mechanically is not a fairness proof, capacity policy, or substitute for making blocking work non-blocking. See [`asyncio.sleep()`](https://docs.python.org/3.14/library/asyncio-task.html#asyncio.sleep).

### 4.4 How the event loop schedules work

Application code should normally enter through `asyncio.run(main())`. In Python 3.14 it accepts any awaitable, creates a fresh event loop, drives the top-level work, finalizes asynchronous generators, shuts down the default executor, and closes the loop. It cannot be called while another event loop runs in the same thread. Use `asyncio.Runner` when several top-level calls deliberately share one loop and Context. See [`asyncio` Runners](https://docs.python.org/3.14/library/asyncio-runner.html).

Inside asynchronous code, `asyncio.get_running_loop()` is the precise way to retrieve the active loop. Low-level `get_event_loop()` behavior changed in Python 3.14 and the policy system is deprecated for removal in Python 3.16, so new configuration should prefer an explicit `loop_factory` rather than depending on implicit policy lookup. See [Obtaining the Event Loop](https://docs.python.org/3.14/library/asyncio-eventloop.html#obtaining-the-event-loop).

The public loop contract includes:

- `call_soon()` schedules a callback for the next loop iteration, preserves registration order among `call_soon()` callbacks, and captures the current Context unless one is supplied;
- `call_later()` and `call_at()` use the loop's monotonic clock, but callbacks with exactly equal scheduled times have undefined relative order;
- `call_soon_threadsafe()` is the cross-thread scheduling entry point; ordinary `call_soon()` is not thread-safe;
- `create_task()` schedules a coroutine and `create_future()` creates a Future appropriate for that loop implementation.

**CPython 3.14 implementation detail:** the default `BaseEventLoop._run_once()` chooses a selector timeout, processes I/O events, moves due timers to a ready deque, snapshots the deque length, and invokes that batch. Handles scheduled by those callbacks stay for a later iteration. This explains the controlled experiment, but code must not depend on private `_ready`, `_scheduled`, `_run_once()`, or one alternative loop matching this exact batching. See CPython 3.14.7 [`Lib/asyncio/base_events.py`, `BaseEventLoop._run_once`](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/base_events.py).

### 4.5 Tasks and Futures

By default, `asyncio.create_task(coro)` copies the current Context, registers the coroutine for execution “soon,” and returns immediately with a Task. The loop runs one Task at a time; when that Task awaits a pending Future, the Task records the dependency and arranges a done callback that will wake it. When the Future completes, the wakeup advances the coroutine with a value or throws the stored exception into it. See [Task objects](https://docs.python.org/3.14/library/asyncio-task.html#task-object).

A Task is Future-like for consumers but rejects producer methods such as `set_result()` and `set_exception()` because the wrapped coroutine determines its outcome. Application code should normally create Tasks through `create_task()` or a structured owner rather than calling `Task(...)` directly.

Task lifetime has two owners:

- the event loop schedules advancement but retains only weak references in relevant registries;
- application or structured-concurrency code retains a strong reference, decides lifetime, and observes the terminal outcome.

Dropping an unstructured Task handle can hide exceptions and allow a pending Task to be destroyed. A long-lived background-task registry needs strong references, done-callback cleanup, explicit exception observation, and a shutdown policy. `TaskGroup`, cancellation, and timeout semantics belong to `PY-CON-070`; this unit establishes why that ownership structure is needed.

Python 3.14 adds `eager_start` forwarding to task creation. With `eager_start=True` on a running compatible loop, the coroutine may begin synchronously inside the creation call and continue until its first suspension. That changes ordering and can make a task finish before `create_task()` returns. The default mental model remains “scheduled soon” unless an eager factory or explicit eager start is selected. See [`asyncio.create_task()`](https://docs.python.org/3.14/library/asyncio-task.html#asyncio.create_task).

### 4.6 Context variables follow logical Tasks

Thread-local state cannot distinguish two asynchronous requests interleaved on the same OS thread. `contextvars` provides logical-context bindings instead. `ContextVar` keys should normally be declared at module scope; `set()` changes the binding in the current Context and returns a Token that can restore the previous binding.

Task creation copies the current Context when no explicit `context=` is supplied. Each Task then runs every coroutine step in its own Context. Therefore:

1. a child sees the binding present when the Task was created, not whatever the parent binds later;
2. the child's later `ContextVar.set()` does not change the parent's binding;
3. suspension and resumption preserve the child's binding;
4. the copy is shallow, so two contexts can still refer to the same mutable list, client, or request object.

`copy_context()` has documented O(1) complexity. That is a complexity claim about copying the Context mapping structure, not about deep-copying its values or making them thread-safe. See [`contextvars`](https://docs.python.org/3.14/library/contextvars.html) and [PEP 567](https://peps.python.org/pep-0567/).

Context is appropriate for cross-cutting metadata such as trace IDs, locale, or diagnostic tags. Keep business inputs, authorization decisions, and resource ownership explicit where hidden dependency would make review or testing unsafe.

### 4.7 Execution sequence

| Step | Event | Relevant state |
|---:|---|---|
| 1 | `asyncio.run(main())` creates and owns a loop | Fresh loop, top-level awaitable prepared |
| 2 | The runner wraps a coroutine in a Task when needed | Main Task ready with a copied Context |
| 3 | Loop invokes the Task's first step | Coroutine changes from created to running |
| 4 | Coroutine reaches `await pending_future` | Task stores the Future dependency and suspends |
| 5 | Loop advances callbacks, other Tasks, timers, or I/O | Suspended Task consumes no Python execution time |
| 6 | Producer resolves the Future | Result/exception stored; Task wakeup scheduled |
| 7 | Loop invokes the Task again | Await produces the result or raises; coroutine resumes |
| 8 | Coroutine returns or raises | Task becomes terminal; its awaiters/callbacks are scheduled |
| 9 | Owner awaits or inspects the Task | Terminal outcome is observed and classified |
| 10 | Runner exits | Async generators/default executor are finalized and loop closes |

## 5. Additional visual models

### Coroutine, Task, and Future state relationship

```text
coroutine object
  CREATED -- first advance --> RUNNING -- await pending F --> SUSPENDED
                                  ^                            |
                                  |------ F wakeup ------------|
                                  |
                                  +---- repeated advances -----+
                                  |
                                  +-- return/raise --> CLOSED

Task owner view
  PENDING/active ------------------------------> DONE(value/exception)
       |                    wraps coroutine
       +---------- awaiting Future F ----------+

Future F
  PENDING -- producer set_result/set_exception --> DONE
             \-- cancellation handled in PY-CON-070
```

#### How to read this visual

Read the coroutine row as execution state, then align the Task row with the coroutine it drives. A pending Future is not the Task itself: it is the current dependency. Future completion schedules a Task wakeup; it does not run the whole coroutine inline inside the producer's callback.

#### Key insight

The Task is the scheduling and outcome wrapper; the coroutine is the resumable computation; a Future is commonly one dependency that temporarily blocks further Task advancement.

#### Simplification or limitation

The state names combine public introspection and a conceptual model. Task cancellation, multiple nested awaitables, callbacks, eager completion, exception injection, generator-based coroutines, and private CPython Task fields are omitted.

### Context snapshot branching

```text
parent Context: request_id = "A"
        |
        +-- create Task A ---- snapshot ----> Task A starts with "A"
        |
        +-- parent sets "B"
        |       |
        |       +-- create Task B -- snapshot -> Task B starts with "B"
        |
        +-- parent remains "B"

Task A sets "A/child"       Task B sets "B/child"
       |                            |
       +-- await/resume: same       +-- await/resume: same

Neither binding change rewrites the parent's binding.
```

#### How to read this visual

Follow the parent downward in time. Each rightward branch is a shallow Context snapshot taken at task creation. Then follow each child vertically across its own suspension.

#### Key insight

Task-locality follows logical task creation and resumption, not merely the OS thread currently executing the code.

#### Simplification or limitation

The diagram shows immutable strings. With a mutable value, isolated bindings can still point to one shared object. Explicit `context=`, callbacks, thread offloading, manually entered Contexts, and alternative task frameworks are omitted.

## 6. Worked examples

All observations below were produced with CPython 3.14.4 on Linux x86_64. They are deterministic teaching traces, not timing benchmarks.

### 6.1 Coroutine and Task lifecycle

The runnable file is [`examples/coroutine_lifecycle.py`](examples/coroutine_lifecycle.py).

It creates a coroutine object, records `inspect.getcoroutinestate()`, wraps the exact object in a named Task, gives the loop one explicit checkpoint, and then awaits the Task. The worker also has one checkpoint, so it has started but cannot be done when the owner resumes after the first turn.

Observed result:

```text
created state: CORO_CREATED
done immediately after create_task: False
done after one loop turn: False
closed state: CORO_CLOSED
result: 42
events: ('owner:coroutine-created', 'owner:task-created', 'worker:start', 'owner:after-one-turn', 'worker:resume', 'owner:collected')
```

This proves the controlled lifecycle on the tested runtime. It does not establish a universal callback interleaving for arbitrary event-loop implementations or eager task factories.

### 6.2 Callback-to-Future adapter

The runnable file is [`examples/future_bridge.py`](examples/future_bridge.py).

`begin_lookup()` creates a loop-owned Future and schedules a plain callback that resolves it. The first await suspends because the Future is pending. Before the second await, the owner schedules another callback; the already-done Future returns its stored result without suspending, so the owner records its line before the queued callback runs.

Observed result:

```text
first result: 'ready'
repeated result: 'ready'
future done: True
events: ('adapter:scheduled', 'owner:before-first-await', 'adapter:completed', 'owner:after-first-await', 'owner:after-second-await', 'callback:queued-before-second-await', 'owner:after-explicit-yield')
```

Production adapters must also define duplicate completion, cancellation, late callback, callback failure, thread-safety, and resource-unregistration behavior. Those policies are intentionally not hidden inside this minimal bridge.

### 6.3 Task Context snapshots

The runnable file is [`examples/task_context.py`](examples/task_context.py).

The parent creates two Tasks under two different request-ID bindings. Each child changes only its own binding, crosses an await, records the retained value, and resets its Token. The parent binding remains the second value until its own reset.

Observed result:

```text
child-a: inherited='request-a' local_after_await='request-a/child-a'
child-b: inherited='request-b' local_after_await='request-b/child-b'
parent after children: 'request-b'
```

The values are strings so the trace isolates binding behavior. It does not show safety for a shared mutable value.

### 6.4 Debugging example: an `async def` that blocks

Diagnose before changing the code:

```python
import asyncio
import time


async def heartbeat(events: list[str]) -> None:
    for index in range(3):
        events.append(f"beat:{index}")
        await asyncio.sleep(0)


async def load_record(events: list[str]) -> None:
    events.append("load:start")
    time.sleep(1)  # a synchronous blocking boundary
    events.append("load:end")


async def main() -> None:
    events: list[str] = []
    heartbeat_task = asyncio.create_task(heartbeat(events))
    await load_record(events)
    await heartbeat_task
    print(events)


asyncio.run(main())
```

Before running, identify:

1. the exact OS thread occupied by `time.sleep()`;
2. why the presence of `async def` and a sibling Task does not help;
3. which events can occur before `load:end`;
4. the API boundary that should become genuinely asynchronous or be deliberately offloaded;
5. what lifetime, context, cancellation, and shutdown obligations an offload would create.

The correction remains withheld until an attempt.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| Calling `async_fn()` starts the body. | Ordinary function calls execute immediately. | It creates a coroutine object; an awaiter or Task must advance it. | Record before the first body line and inspect `CORO_CREATED`. |
| `await` always lets siblings run. | It is described as a yield point. | A completed awaitable can return synchronously; suspension depends on the object and state. | Await a done Future with a queued callback as in `future_bridge.py`. |
| Direct `await child()` creates concurrency. | Both functions are asynchronous. | It composes child execution into the same Task; create a separately owned Task for overlapping lifetime. | Compare `current_task()` and an ordered trace. |
| `create_task()` runs the child before the next statement. | It schedules execution “soon.” | Default scheduling normally queues the first step; Python 3.14 eager start can deliberately change this. | Compare default and `eager_start=True` in the experiment. |
| An `async def` wrapper makes a blocking client asynchronous. | The signature is awaitable. | Synchronous work still occupies the loop thread until it returns. | Run heartbeat work beside an event-controlled blocking boundary. |
| One loop runs many Tasks in parallel. | Lifetimes overlap. | One loop thread advances one Task's Python code at a time; parallelism requires another thread/interpreter/process or native operation. | Record thread IDs and insert a CPU-heavy non-awaiting section. |
| Task creation is “fire and forget.” | The loop knows about the Task. | The application needs a strong reference, exception observation, and shutdown policy. | Create a failing unobserved Task under debug mode and inspect the warning. |
| `Task.done()` means success. | No more execution remains. | Done includes value, exception, or cancellation. | Call `result()` on controlled terminal categories. |
| A Future is a Task. | Task inherits a Future-like consumer interface. | A Task drives a coroutine; a Future usually represents an externally completed dependency. | Try `task.set_result()` and compare with a loop-created Future. |
| An asyncio Future can be resolved from any thread. | Futures represent cross-time results. | The object is not thread-safe; cross-thread producers schedule through `call_soon_threadsafe()`. | Enable debug mode and attempt the wrong-thread low-level call in an isolated test. |
| `ContextVar` means thread-local. | Contexts are stored through thread state. | asyncio captures and re-enters a distinct logical Context for each Task. | Create two Tasks under different bindings on one thread. |
| A copied Context deep-copies values. | Child binding changes are isolated. | The Context copy is shallow; a mutable value can still be one shared object. | Bind one list, mutate it in two Task contexts, and compare identity. |
| A ContextVar can be declared inside a closure safely forever. | It behaves like an ordinary local key. | Contexts hold strong references to variables; declare keys at module scope as documented. | Create short-lived keys and inspect retained Context items in a controlled process. |
| `asyncio.run()` can be nested. | It is the standard entry point. | It cannot run while another event loop runs in the same thread. | Call it from a coroutine and classify the `RuntimeError` without leaking the new coroutine. |
| Equal timer deadlines have FIFO order. | `call_soon()` is ordered. | Equal-time `call_at()` ordering is undefined by the public contract. | Schedule equal deadlines repeatedly; never make correctness depend on the observation. |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| Coroutine object creation | Allocation plus argument/frame setup | Body execution has not begun; exact object layout is CPython-specific. |
| Task creation | Task allocation, shallow Context copy, registration, and scheduling | `copy_context()` is documented O(1); custom task factories and eager start change work done inline. |
| Future completion | Store one terminal outcome plus schedule registered callbacks | Callback count and loop implementation determine total work; callbacks do not all become free. |
| Await pending Future | Suspend current Task and register wakeup machinery | Exact C/Python implementation is version-specific; application cost also includes retained frame state. |
| Await completed Future | Constant-time-style terminal check and outcome retrieval | Do not depend on an exact instruction count; important semantic point is that it need not suspend. |
| `call_soon()` | Handle allocation and ready-queue insertion | FIFO registration order is public for `call_soon()` callbacks; private deque complexity is not an application contract. |
| Timer scheduling | Heap-style scheduling in CPython's default loop | Public API does not promise one data structure; equal-deadline order is undefined. |
| Selector poll | Proportional to ready OS events plus system-call overhead | Platform, selector, descriptors, transports, and alternative loops differ. |
| One Task per operation | Lower footprint than one OS thread in many I/O workloads | Still retains coroutine frames, arguments, Context values, callbacks, results, and application resources. Bound concurrency separately. |
| Blocking callback of duration `t` | Roughly adds `t` delay to all work needing that loop thread | Scheduler latency can compound with queues and external deadlines; measure the deployed service. |

These are cost models, not benchmark results. A benchmark must record Task count, readiness pattern, payloads, loop implementation, runtime/build, OS, debug mode, warm-up, trials, raw observations, and uncertainty.

## 9. Production relevance and trade-offs

### Entry points and loop ownership

- Give the process or thread one clear high-level loop owner; prefer `asyncio.run()` for one entry point or `asyncio.Runner` for deliberate repeated top-level calls.
- Do not hide nested loop runners inside library APIs. Libraries should expose coroutines and let the application own loop lifecycle.
- Use `get_running_loop()` inside coroutine/callback code and explicit `loop_factory` configuration when loop selection matters.
- Close transports, async generators, clients, and task owners through their documented async context boundaries before runner shutdown.

### Task ownership and failure

- Directly await work that is a required dependency and needs no independent lifetime.
- When creating a Task, name it, retain it, define who awaits it, and decide how its exception reaches the responsible boundary.
- Avoid unstructured background Tasks for request-critical work. A callback that merely removes the Task from a set must not silently consume failure.
- Treat task result, task exception, cancellation, and owner shutdown as separate outcomes. `PY-CON-070` builds the structured policy.

### Loop health and blocking boundaries

- Audit every library call inside async code: a synchronous network client, file operation, lock, subprocess wait, compression step, serializer, or CPU loop can stall the loop.
- Prefer a genuinely asynchronous library when it matches the protocol. Use `asyncio.to_thread()` or executor APIs only with bounded capacity, thread-safe clients, context expectations, cancellation limits, and shutdown ownership.
- Never use arbitrary sleeps to “fix” scheduling. Use Events, Futures, queues, protocol readiness, or explicit checkpoints whose contract matches the dependency.
- Enable asyncio debug mode in development to expose slow callbacks, wrong-thread calls, un-awaited coroutines, and resource leaks.

### Context and observability

- Use module-level `ContextVar` keys for safe tracing metadata such as request ID, trace ID, locale, or tenant label.
- Set and reset temporary bindings with the returned Token; Python 3.14 can use the Token as a context manager, while Python 3.11 uses `try/finally`.
- Keep mutable clients and authorization inputs explicit. A Context binding is not resource ownership, immutability, or access control.
- Log safe Task name, loop identity where useful, request/trace ID, scheduling delay, operation duration, terminal category, and shutdown phase; do not log secrets or payloads.

### Threads and callbacks

- Most asyncio objects are not thread-safe. Use `loop.call_soon_threadsafe()` to inject a callback from another OS thread and `asyncio.run_coroutine_threadsafe()` only when the cross-thread ownership protocol is explicit.
- Complete loop-owned Futures on the loop thread. A foreign callback thread should schedule the completion callback rather than mutating the Future directly.
- Callback adapters must handle duplicate signals, callback deregistration, late completion, already-cancelled Futures, and exceptions raised while translating a result.

### Testing

- Prefer deterministic Events, Futures, and explicitly ordered callbacks over wall-clock sleeps.
- Assert state and ownership, not private queue contents or fragile timestamps.
- Run with debug mode and warnings enabled when testing forgotten coroutines, leaked transports, slow callbacks, and unobserved task exceptions.
- Version-gate eager-start expectations and label exact loop-turn traces as CPython/default-loop observations.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| Native `async def`, `await`, coroutine objects, and awaitable protocol | Language | 3.5 | Same syntax and core semantics | Generator-based coroutine compatibility is historical; prefer native coroutines. |
| `asyncio.run()` | Standard library | 3.7 | Available in 3.11 | Python 3.14 accepts any awaitable; wrap a non-coroutine awaitable in a small coroutine for 3.11. |
| `asyncio.create_task()` | Standard library | 3.7 | Same core API | Requires a running loop in the current thread. |
| Task names | Standard library | 3.8 | Available in 3.11 | Names aid diagnostics but are not stable business identity. |
| `contextvars` and native asyncio task-context support | Standard library | 3.7 | Available in 3.11 | Context snapshots are shallow and bindings are logical-task-local. |
| `create_task(..., context=...)` | Standard library | 3.11 | Available in the interview baseline | Omit to copy the current Context. |
| `asyncio.Runner` | Standard library | 3.11 | Available in the interview baseline | Reuses one loop and Context for multiple top-level calls. |
| `asyncio.eager_task_factory()` | Standard library / Version | 3.12 | Use default scheduled start and do not depend on inline entry | Eager execution changes ordering and observability. |
| `create_task(..., eager_start=...)` and full keyword forwarding | Standard library / Version | 3.14 | Omit `eager_start`; Python 3.11 schedules normally | Requires a compatible loop/task factory. |
| `ContextVar.Token` as a context manager | Standard library / Version | 3.14 | `token = var.set(value)` plus `try/finally: var.reset(token)` | The explicit 3.11 form remains clear and portable. |
| `get_event_loop()` raises when no current loop | Standard library / Version | 3.14 behavior | Prefer `get_running_loop()` inside async code and runner-owned setup | Policy system is deprecated for removal in 3.16. |
| `BaseEventLoop._run_once()` ready-deque batch behavior | CPython implementation detail | Version-specific | Depend only on public scheduling contracts | Alternative loops and future CPython versions may batch differently. |
| Default `asyncio.Task` implemented by `_asyncio.Task` in tested CPython | CPython implementation detail | Version/build-specific | Treat `Task` through its public API | The pure-Python source is explanatory; accelerator details may differ. |

For a Python 3.11 interview, lead with coroutine cold creation, direct await, Task creation, cooperative suspension, Futures as callback bridges, `asyncio.run()`, `Runner`, task Context capture, loop-thread blocking, task ownership, and deterministic debugging. Label eager task start, Token context-manager syntax, arbitrary-awaitable runners, and policy changes as newer behavior.

## 11. Practice brief

Exercises are unsolved in [`practice/README.md`](practice/README.md); hints and comparison solutions remain withheld until an attempt.

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-CON-060-P01` | Predict | 2 | E+D | Direct await, Task creation, and completed-awaitable trace |
| `PY-CON-060-P02` | Implement | 3 | C+D | Safe callback-to-Future adapter |
| `PY-CON-060-P03` | Debug | 3 | D | Forgotten coroutine, hidden blocking, and lost Task failure |
| `PY-CON-060-P04` | Implement | 3 | C+X | Request Context capture and isolation |
| `PY-CON-060-P05` | Design / Review | 4 | E+D | Owned background-task boundary and loop-health review |

## 12. Interview prompts

Attempt one at a time; do not read or write a prepared answer first.

1. What exactly happens when an `async def` function is called, and what must happen before its body executes?
2. Draw coroutine, Task, and Future roles around one pending `await`.
3. Why does `await child()` not necessarily create concurrency? When would `create_task(child())` change the lifetime?
4. Is every `await` a scheduling point? Prove your answer with a completed Future.
5. What does “the event loop runs one Task at a time” guarantee, and what race conditions can still occur across awaits?
6. Why is `time.sleep()` inside `async def` harmful even though it releases the CPython GIL?
7. How would you adapt a callback API that can complete from another thread into an asyncio-facing API?
8. When does a new Task capture Context, and what happens if the ContextVar value is a mutable dictionary?
9. What changed with eager task start, and which ordering assumption does it invalidate?
10. Why should application-facing APIs usually not expose mutable Futures?
11. How do `asyncio.run()`, `asyncio.Runner`, and `get_running_loop()` divide loop ownership and lookup?
12. Review a request handler that launches an unreferenced background Task. What must the design specify before production use?

A strong answer should eventually demonstrate:

- cold coroutine creation, awaitable protocol, cooperative Task stepping, and Future wakeup mechanics;
- separation of direct composition, independently scheduled lifetime, and callback adaptation;
- loop ownership, blocking boundaries, Context snapshots, failure observation, version differences, and public-versus-CPython contracts.

## 13. Closed-book revision cues

Without reading the note:

1. Reconstruct the main event-loop/Task/Future visual and narrate both arrows back to the ready side.
2. Define coroutine function, coroutine object, awaitable, Task, Future, callback, and loop in one sentence each.
3. Predict a direct `await` and a sibling `create_task()` trace.
4. Explain why awaiting a completed Future may not run a queued callback first.
5. Reconstruct the Context snapshot branching visual and state the mutable-value limitation.
6. Name the owner of loop lifecycle, Task lifetime, Future completion, and Context reset.
7. Diagnose a synchronous database client called inside `async def`.
8. State the safe cross-thread entry point for scheduling a loop callback.
9. Compare Python 3.11 default task start with Python 3.14 `eager_start=True`.
10. Explain which parts of `_run_once()` are useful CPython evidence but unsafe application dependencies.
11. List the warnings/debug signals for a forgotten coroutine, unobserved task exception, slow callback, and wrong-thread call.
12. Review one backend endpoint for suspension points, hidden blocking, task ownership, context, and terminal-outcome observation.

## 14. Authoritative sources

Only official sources opened and used for this unit are listed.

1. [Python Language Reference — Await expression](https://docs.python.org/3.14/reference/expressions.html#await-expression), syntax and suspension contract; Python 3.14.7 documentation, accessed 2026-08-28.
2. [`asyncio` — Coroutines and Tasks](https://docs.python.org/3.14/library/asyncio-task.html), coroutine creation, Tasks, cooperative scheduling, sleep, task references, context, and eager start; Python 3.14.7 documentation, accessed 2026-08-28.
3. [`asyncio` — Event loop](https://docs.python.org/3.14/library/asyncio-eventloop.html), loop ownership, callback/timer scheduling, thread-safe entry, Future/Task creation, and policy changes; Python 3.14.7 documentation, accessed 2026-08-28.
4. [`asyncio` — Futures](https://docs.python.org/3.14/library/asyncio-future.html), callback bridge, loop-created Future guidance, repeated await, and thread-safety boundary; Python 3.14.7 documentation, accessed 2026-08-28.
5. [`asyncio` — Runners](https://docs.python.org/3.14/library/asyncio-runner.html), `asyncio.run()`, `Runner`, cleanup, loop factory, and Python 3.14 changes; Python 3.14.7 documentation, accessed 2026-08-28.
6. [`contextvars` — Context Variables](https://docs.python.org/3.14/library/contextvars.html), ContextVar/Token/Context API, O(1) context copying, and 3.14 Token context-manager support; Python 3.14.7 documentation, accessed 2026-08-28.
7. [Developing with asyncio](https://docs.python.org/3.14/library/asyncio-dev.html), debug mode, thread boundaries, blocking code, un-awaited coroutines, and unobserved exceptions; Python 3.14.7 documentation, accessed 2026-08-28.
8. [PEP 492 — Coroutines with async and await syntax](https://peps.python.org/pep-0492/), native coroutine and awaitable design; final standards-track PEP, accessed 2026-08-28.
9. [PEP 567 — Context Variables](https://peps.python.org/pep-0567/), task-context rationale, capture semantics, and implementation model; final standards-track PEP, accessed 2026-08-28.
10. [Python 3.11 Coroutines and Tasks](https://docs.python.org/3.11/library/asyncio-task.html), interview-baseline task API and version comparison; Python 3.11.15 documentation, accessed 2026-08-28.
11. [CPython 3.14.7 `Lib/asyncio/base_events.py`](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/base_events.py), `BaseEventLoop._run_once()` ready/timer/I/O batch implementation; accessed 2026-08-28.
12. [CPython 3.14.7 `Lib/asyncio/tasks.py`](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/tasks.py), explanatory pure-Python Task context, eager-start, wait, and wakeup paths; accessed 2026-08-28.

## 15. Durable clarification log

| Date | Clarification | Why it belongs in canonical notes | Source or evidence |
|---|---|---|---|
| 2026-08-28 | An `await` expression is a possible suspension point, not proof that control transferred; a completed Future can return before an already-queued callback runs. | Treating every await as a fairness boundary creates fragile ordering and starvation assumptions. | Python 3.14 await/Future contracts; `examples/future_bridge.py`. |
| 2026-08-28 | A Task captures a shallow Context snapshot at creation, so later bindings are isolated while mutable referenced values can remain shared. | “Task-local” is often incorrectly expanded into deep-copy or object-safety guarantees. | Python 3.14 `create_task()` and `contextvars`; `examples/task_context.py`; PEP 567. |
| 2026-08-28 | Python 3.14 eager task start can execute the coroutine body inside `create_task()` before the caller's next statement. | Code written around the older “first step always later” assumption can change ordering, reentrancy, and observability under eager mode. | Python 3.14 `create_task()`; `experiments/EXP-01-eager-task-start/`. |
| 2026-08-28 | CPython's default loop snapshots the current ready batch, leaving handles scheduled by that batch for a later loop iteration. | The detail explains controlled traces but must remain labelled so code does not depend on a private queue or alternative-loop behavior. | CPython 3.14.7 `BaseEventLoop._run_once()` source and experiment trace. |
