# PY-CON-010 — Concurrency, parallelism, scheduling, and the GIL model

[Curriculum entry](../../../CURRICULUM.md#py-con-010) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-CON-010`

## Physical Notebook Core

### Problem this concept solves

Backend programs often have several useful pieces of work ready, waiting, or competing for execution. We need precise language for reasoning about their progress and for choosing an execution model that matches the workload instead of assuming that every form of concurrency makes code run in parallel.

### One-sentence mental model

> Concurrency is about managing overlapping tasks; parallelism is simultaneous execution; a scheduler decides what runs when, while the workload and Python runtime determine whether overlap can improve latency or throughput.

### One important visual

```text
time ───────────────────────────────────────────────>

one execution lane
task A:  [run]          [run]          [run]
task B:        [run]          [run]
         interleaved progress = concurrent, not parallel

two execution lanes
task A:  [run][run][run]
task B:  [run][run][run]
         simultaneous execution = parallel (and concurrent)

waiting-shaped task: [request] ··· waiting ··· [resume]
compute-shaped task: [========== CPU work ==========]
```

#### How to read this visual

Read left to right as wall-clock time. First compare the number of execution lanes: interleaving on one lane can advance both tasks without simultaneous execution, while overlapping run blocks on two lanes show parallelism. Then compare the bottom two workload shapes: waiting exposes time in which another task may run; continuous computation needs actual compute capacity for a speedup.

#### Key insight

Concurrency creates an opportunity to use otherwise idle time; parallelism requires more than one execution resource and is constrained by the runtime, including the GIL in a regular CPython build.

#### Simplification or limitation

This is a conceptual timeline, not a literal CPython or operating-system trace. Run blocks are not equal, readiness can change at any instant, native code may execute outside the GIL, and an optional free-threaded CPython build changes the thread-parallelism boundary.

### Governing rules or invariants

1. Concurrent tasks may merely interleave; concurrency does not prove that any two instructions execute simultaneously.
2. Match the mechanism to the measured bottleneck: waiting-heavy work benefits from overlap, while CPU-heavy pure-Python work needs a route to genuine parallel compute if throughput is the goal.
3. The GIL in a regular CPython build serializes Python-bytecode execution across threads; it does not make multi-step application invariants atomic or remove the need for synchronization.

### Minimal example

```python
from collections.abc import Iterator


def operation(name: str) -> Iterator[str]:
    yield f"{name}: start"
    yield f"{name}: finish"


first = operation("first")
second = operation("second")

for selected in (first, second, first, second):
    print(next(selected))
```

Expected reasoning:

1. Each `next()` lets exactly one generator advance to its next suspension point, so one execution lane produces an interleaved trace.
2. Both operations make progress before either is complete, which models concurrency, but the example performs no parallel execution and creates no threads.

### One failure or misconception

**Mistake:** “CPython has a GIL, so threads cannot be useful and shared Python state is automatically safe.”

**Correction:** On a regular GIL-enabled CPython build, only one thread executes Python bytecode at a time, but another thread can run while one waits in blocking I/O, and native code may release the GIL. Application operations can still interleave between steps, so shared invariants require an explicit safe design.

### Important trade-offs

- More concurrency can hide waiting and improve throughput, but it also increases scheduling overhead, contention, resource usage, and failure coordination.
- Threads share memory conveniently; processes offer isolation and ordinary multi-core pure-Python execution at the cost of startup, communication, and serialization.
- A free-threaded CPython build can run Python threads in parallel, but runtime availability, extension compatibility, synchronization, and workload scaling must all be verified.

### Interview-revision cues

- Draw one-lane interleaving versus two-lane simultaneous execution.
- Classify a workload by where wall-clock time is actually spent: running Python, running native code, or waiting.
- Explain both what the regular CPython GIL serializes and what correctness guarantees it does not provide.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Concurrency, parallelism, and asynchronous Python |
| Canonical ID | `PY-CON-010` |
| Learning outcome | Distinguish concurrency, parallelism, scheduling, CPU-bound work, I/O-bound work, and the high-level GIL model |
| Hard prerequisites | `PY-FND-020`, `PY-FIT-010` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D2 |
| Scope | Language, CPython |
| Size | M |
| Evidence profile | E+C+D |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4 on Linux x86_64 |
| Last source audit | 2026-08-27 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Given a timeline or execution trace, distinguish sequential execution, concurrent interleaving, and parallel execution without confusing task count with core usage.
2. Classify a workload as predominantly CPU-bound, I/O-bound, or mixed and explain how scheduling, waiting, overhead, and the execution environment affect an appropriate design.
3. Explain the high-level GIL model for regular and free-threaded CPython builds, including why the GIL neither forbids all useful threading nor guarantees application-level thread safety.

Required evidence:

- Reconstruct the one-lane/two-lane visual and explain concurrency, parallelism, scheduling, CPU-bound work, I/O-bound work, and the regular CPython GIL in precise language.
- Run and extend [`examples/scheduling_trace.py`](examples/scheduling_trace.py), predict the event order before execution, and state exactly why the result demonstrates interleaving rather than parallelism.
- Debug one flawed concurrency argument or shared-state design by identifying the first invalid assumption and proposing an execution boundary appropriate to the workload.

Initialization creates this learning scaffold but does not itself satisfy the evidence or advance the learning state.

## 2. Prerequisite bridge

Both hard prerequisites are currently absent and not started. These minimum bridges allow this unit to proceed, but they do not complete either prerequisite.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-FND-020` — Objects, names, references, and mutability | Concurrent workers may hold references to the same mutable object, so correctness depends on shared identity and mutation rather than variable spelling alone. | Assignment binds a name to an object. Passing or assigning a mutable object can create another reference to the same object; mutation through either reference is visible through the other. |
| Hard | `PY-FIT-010` — Function definitions, calls, returns, and first-class behaviour | Units of work are commonly represented by callables whose calls consume CPU, wait, return, raise, or create side effects. | A function definition creates a callable; calling it runs its body until it returns or raises. A call may have observable side effects and may spend time computing or waiting. |

Initialize the dedicated prerequisite chats when practical. Until then, keep “shared object” distinct from “shared name,” and reason about every task as a call that moves between running, waiting, and finished states.

## 3. Vocabulary and professional English

### Concurrent

| Item | Content |
|---|---|
| Pronunciation | kuhn-KUR-uhnt |
| Simple English meaning | In progress during overlapping periods |
| Hindi cue | साथ-साथ प्रगति |
| Meaning in this Python context | Multiple tasks are managed so that each can make progress before all others finish; their instructions need not execute simultaneously |

Natural examples:

1. The server handles several requests concurrently.
2. The tasks are concurrent even on a single core because their execution interleaves.
3. Concurrent work needs a policy for scheduling and failure handling.
4. **Interview:** “Concurrency describes overlapping progress; I would need stronger evidence to claim parallelism.”
5. **Engineering discussion:** “The concurrent design hides network waiting but must cap open connections.”

### Parallel

| Item | Content |
|---|---|
| Pronunciation | PAIR-uh-lel |
| Simple English meaning | Happening at the same instant |
| Hindi cue | एक ही समय पर निष्पादन |
| Meaning in this Python context | Two or more operations execute simultaneously on distinct processing resources, such as different CPU cores |

Natural examples:

1. The two processes can execute CPU work in parallel.
2. A concurrent program is not necessarily parallel.
3. Parallel execution does not guarantee a linear speedup.
4. **Interview:** “On a regular CPython build, two threads do not execute Python bytecode in parallel.”
5. **Engineering discussion:** “Before adding parallel workers, I would measure the serial fraction and communication cost.”

### Preempt

| Item | Content |
|---|---|
| Pronunciation | pree-EMPT |
| Simple English meaning | Pause something so another thing can proceed |
| Hindi cue | बीच में रोककर बदलना |
| Meaning in this Python context | A scheduler interrupts or stops selecting running work and gives execution time to different runnable work |

Natural examples:

1. The operating system may preempt a running thread.
2. A preempted task remains incomplete but can later resume.
3. Code must not assume that a task will run uninterrupted to its next source line.
4. **Interview:** “Preemption makes the exact thread interleaving nondeterministic.”
5. **Engineering discussion:** “Changing a switch interval is not a substitute for a synchronization boundary.”

### Contention

| Item | Content |
|---|---|
| Pronunciation | kuhn-TEN-shuhn |
| Simple English meaning | Competition for a limited resource |
| Hindi cue | संसाधन के लिए प्रतिस्पर्धा |
| Meaning in this Python context | Multiple tasks compete for a lock, CPU, connection, memory bandwidth, queue slot, or other bounded resource |

Natural examples:

1. Too many workers increased database connection contention.
2. Lock contention can erase the benefit of adding threads.
3. A queue can expose where contention accumulates.
4. **Interview:** “Parallelism may increase throughput until contention becomes the bottleneck.”
5. **Engineering discussion:** “The latency tail suggests contention rather than insufficient task creation.”

## 4. Deep explanation

### 4.1 Why the mechanism exists

A sequential program gives one operation the execution path until it returns, blocks, or the program explicitly moves elsewhere. That model is easy to follow, but it can waste wall-clock time when an operation waits for a socket, disk, database, subprocess, timer, or remote service. Concurrency lets other eligible work use that opportunity. It can improve responsiveness and throughput even when the machine executes only one piece of Python code at any instant.

Parallelism answers a different question: are multiple operations literally executing at once? It can increase compute throughput when the workload has independent work, the runtime can use multiple execution resources, and coordination costs do not dominate. Treating concurrency and parallelism as synonyms hides the main engineering decision: whether the bottleneck is unused waiting time or insufficient compute capacity.

### 4.2 Formal semantics and implementation boundaries

#### Concurrency and parallelism

Python's glossary describes concurrency as the ability to perform multiple tasks in the same period and lists coroutines, operating-system threads, and processes as different mechanisms. It defines parallelism as simultaneous execution, commonly on multiple CPU cores. A program can therefore be concurrent without being parallel, and parallel work is also concurrent when its lifetimes overlap. See the Python 3.14 glossary entries for [concurrency](https://docs.python.org/3.14/glossary.html#term-concurrency) and [parallelism](https://docs.python.org/3.14/glossary.html#term-parallelism).

“Sequential,” “concurrent,” and “parallel” describe relationships between tasks, not particular Python keywords. Threads can be concurrent without executing Python in parallel; processes can be scheduled on one core and merely interleave; an asynchronous event loop can manage many waiting tasks in one thread; native extension code may execute in parallel after releasing the GIL. Always name the mechanism, runtime, and observed relationship.

#### Scheduling and task state

A useful abstract task lifecycle is:

```text
created → runnable → running → completed
              ↑         │
              └─ waiting┘
```

Runnable means the task could make progress if selected. Running means an execution resource is currently advancing it. Waiting means it cannot proceed until an event occurs. A scheduler chooses among runnable work, but different layers schedule different things: the operating system schedules threads and processes, while an event loop chooses ready callbacks or coroutine tasks at explicit suspension boundaries.

CPython's `sys.setswitchinterval()` controls an ideal interpreter thread-switch interval, not an exact timeslice or fairness guarantee. Its documentation states that long-running internal functions can extend the interval and that the operating system decides which thread is scheduled next; the interpreter does not provide its own OS-thread scheduler. Correctness must never depend on a particular interval or winner. See [`sys.setswitchinterval()`](https://docs.python.org/3.14/library/sys.html#sys.setswitchinterval).

#### CPU-bound, I/O-bound, and mixed workloads

A CPU-bound workload spends most relevant wall-clock time executing computation on processing resources. An I/O-bound workload spends a material fraction unable to proceed while it waits for external input or output. “Bound” names the dominant constraint for a particular workload, input, environment, and performance goal; it is not a permanent label on a function.

Most production paths are mixed. A request may parse and validate data, wait for a database, transform the response, wait for another service, serialize JSON, and write a socket. Profile or measure the path before choosing a concurrency mechanism. A synthetic sleep demonstrates waiting but does not reproduce connection limits, server capacity, payload cost, failure modes, or tail latency.

#### The regular CPython GIL model

The GIL is a CPython implementation mechanism, not a Python-language guarantee. In a regular GIL-enabled CPython build, a thread must hold the GIL to execute Python bytecode, so only one thread per interpreter does so at a time. CPython releases the GIL around blocking I/O, and extension code can deliberately release it during native computation. These boundaries explain why threads can overlap I/O and why some native-heavy threaded workloads can use multiple cores even though ordinary pure-Python CPU loops do not. See the [GIL glossary entry](https://docs.python.org/3.14/glossary.html#term-global-interpreter-lock) and [threading performance guidance](https://docs.python.org/3.14/library/threading.html#gil-and-performance-considerations).

The GIL primarily protects interpreter implementation state. It is not a transaction around a source statement, a sequence of calls, or a business invariant. CPython can switch executing threads between bytecode instructions, and blocking operations create further interleaving opportunities. The C API documentation explicitly notes that pure-Python thread safety still needs locks. Do not build correctness on operations that merely “look atomic”; use documented synchronization or avoid shared mutable state. See [Thread states and the GIL](https://docs.python.org/3.14/c-api/threads.html#thread-state-and-the-global-interpreter-lock).

#### Optional free-threaded CPython

Starting with Python 3.13, CPython supports an optional free-threaded build in which the GIL can be disabled. Such a build can execute Python threads in parallel on multiple cores, but it is not the default build. An extension that is not marked as supporting free threading may re-enable the GIL at runtime. The Python 3.14 guidance recommends checking the build configuration with `sysconfig.get_config_var("Py_GIL_DISABLED")` and checking actual GIL state with `sys._is_gil_enabled()` when that distinction matters. See [Python support for free threading](https://docs.python.org/3.14/howto/free-threading-python.html).

Free threading removes one serialization boundary; it does not make shared mutable application state race-free, guarantee speedup, or eliminate contention. Detailed compatibility, object-model, extension, and migration mechanics belong to `PY-CON-090`.

#### Choosing an execution boundary

| Dominant situation | Candidate direction | Why | First qualification to check |
|---|---|---|---|
| A small sequential path already meets its goal | Stay sequential | Lowest coordination and debugging cost | Confirm concurrency would solve a measured problem |
| Many independent I/O waits | Threads or asynchronous I/O | Other work can run while one operation waits | Bound concurrency, timeouts, cancellation, and downstream limits |
| CPU-heavy pure Python on regular CPython | Multiple processes | Separate interpreters can use multiple cores | Startup, serialization, memory, result ordering, and deployment limits |
| CPU-heavy native code that releases the GIL | Threads may provide parallelism | Native regions can overlap across cores | Verify the library contract and measure the real workload |
| CPU-heavy work on free-threaded CPython | Threads may provide parallelism | Multiple threads can execute Python simultaneously | Verify build/runtime GIL state, dependencies, safety, and scaling |

This is a starting hypothesis, not an automatic selector. Later units provide the concrete lifecycle, synchronization, multiprocessing, executor, and `asyncio` APIs.

### 4.3 Execution sequence in two regular-CPython threads

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Two tasks exist in two OS threads and are runnable. | Both may be eligible for OS scheduling; neither ordering nor fairness is promised. |
| 2 | One thread is scheduled and acquires the GIL. | It can execute Python bytecode; the other cannot execute Python bytecode simultaneously. |
| 3 | The running thread calls a blocking I/O operation and releases the GIL. | That thread waits; another thread can acquire the GIL and run Python. |
| 4 | The I/O completes and the first thread becomes runnable again. | It competes for OS scheduling and the GIL; immediate resumption is not guaranteed. |
| 5 | The threads continue to interleave until both complete or fail. | Shared application state may be observed between multi-step updates. |
| 6 | The program evaluates latency, throughput, correctness, and resource use. | Useful overlap is an empirical property of this workload, not a consequence of task count alone. |

## 5. Additional visual models

### Two gates for a regular CPython thread

```text
OS scheduler gate          CPython GIL gate              result
thread selected?     +     GIL acquired?           →     Python bytecode runs
       no            │            —                →     not running
       yes           │            no               →     scheduled but waiting for GIL
       yes           │       native code released  →     native work may run without GIL
       yes           │       blocking I/O          →     thread waits; another can run
```

#### How to read this visual

Read each row from left to right. Being selected by the operating system is necessary for a thread to use a CPU, but regular CPython adds a second condition for Python bytecode: the thread must also own the GIL. Native code and blocking I/O have their own documented boundaries.

#### Key insight

The operating-system scheduler and the GIL solve different problems; neither alone describes the complete execution timeline.

#### Simplification or limitation

The table omits attached thread states, interpreter shutdown, signals, garbage collection pauses, extension-specific behavior, multiple interpreters, and free-threaded internals. It is a high-level default-build model.

## 6. Worked examples

### 6.1 Small example: deterministic interleaving

The runnable file is [`examples/scheduling_trace.py`](examples/scheduling_trace.py).

```python
api = make_task("api", ("send request", "resume with response", "render"))
worker = make_task("worker", ("validate job", "compute result", "persist"))

for event in round_robin((api, worker)):
    print(event)
```

Prediction before execution:

The round-robin driver advances `api` once, then `worker` once, repeating until both generators finish. The output alternates task names. Because the driver calls one `next()` at a time on one thread, the trace demonstrates explicit interleaving only.

Observed result, run with CPython 3.14.4:

```text
api: send request
worker: validate job
api: resume with response
worker: compute result
api: render
worker: persist
```

The generator suspension points stand in for places where a real concurrency mechanism could switch tasks. They do not perform I/O, create threads, invoke an event loop, or prove parallel execution.

### 6.2 Realistic backend example: find the independent waits first

```python
def build_dashboard(user_id: str) -> dict[str, object]:
    profile = load_profile(user_id)       # network/database wait
    orders = load_recent_orders(user_id)  # independent network/database wait
    score = calculate_score(orders)       # local CPU work
    return {"profile": profile, "orders": orders, "score": score}
```

As written, this function is sequential: `load_recent_orders` does not start until `load_profile` returns. The two loads are candidates for concurrent overlap only if they are semantically independent and the chosen clients and runtime support a safe concurrency mechanism. `calculate_score` depends on `orders`, so it cannot begin early without changing the data flow.

A production design must also decide:

- how many downstream calls may be in flight;
- whether each client is safe in the chosen thread or task model;
- how deadlines, cancellation, partial failure, and retries compose;
- whether the score computation is large enough to become CPU-bound;
- how latency, queueing, saturation, and failure are observed.

Concurrency may reduce the two-wait critical path toward the slower wait rather than their sum, but overhead and downstream limits prevent treating that as a guaranteed formula. Concrete thread, executor, and `asyncio` implementations belong to later units.

### 6.3 Debugging example: the GIL is not a transaction

Keep the correction hidden until an attempt.

```python
requests_served = 0


def record_request() -> None:
    global requests_served
    previous = requests_served
    write_audit_record()  # may block
    requests_served = previous + 1
```

Debugging task:

1. Draw an interleaving in which two calls both read the same `previous` value.
2. Identify the first invalid assumption in “the GIL protects this counter.”
3. State what must be protected as one invariant, then propose one shared-state and one ownership-based design direction without implementing the final answer yet.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| “Concurrent” means “on different cores.” | Timelines are often drawn with one lane per task. | Tasks can interleave on one execution lane and still be concurrent. | Record start, suspend, resume, and finish events rather than inferring cores from task names. |
| Two threads make a pure-Python CPU loop twice as fast on regular CPython. | There are two OS threads and perhaps many CPU cores. | Only one thread per interpreter executes Python bytecode at a time in the regular build; overhead may make it slower. | Compare CPU utilization and a controlled workload, recording runtime/build details. |
| The GIL makes a read-modify-write sequence safe. | Only one thread executes bytecode at an instant. | Multiple bytecodes, calls, and blocking points can interleave; the application invariant is larger than GIL ownership. | Force or reason through a switch between reading and writing the shared value. |
| Threads never execute in parallel in CPython. | The default-build GIL is remembered as a universal rule. | Native code may release the GIL, and an optional free-threaded build can run Python threads in parallel. | Identify the interpreter build, actual GIL state, and native-library contract. |
| A function is always I/O-bound or always CPU-bound. | The function has a stable name and source body. | Bottlenecks depend on input, cache state, remote latency, native work, hardware, and the performance goal. | Profile representative inputs and separate running time from waiting time. |
| More workers always improve throughput. | More runnable tasks appear to mean more work completed. | Scheduling, contention, memory, downstream capacity, and coordination impose limits. | Increase bounded concurrency gradually while observing throughput, tail latency, errors, and saturation. |
| `sys.setswitchinterval()` chooses the next thread or fixes a race. | Its name sounds like a scheduler control. | It is an ideal interpreter interval; the OS chooses the next thread, and correctness cannot depend on it. | Repeat a trace under load and use synchronization rather than timing to establish order. |
| A free-threaded build makes existing shared-state code safe. | Removing a global lock sounds like removing the concurrency problem. | It enables more simultaneous execution and therefore requires explicit thread-safe application and extension behavior. | Audit shared mutation and run correctness tests under actual parallel load. |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| Schedule or switch between tasks | Non-zero fixed and runtime-dependent overhead per switch | Exact cost depends on mechanism, OS, runtime build, task state, caches, and measurement environment. |
| Sequential independent waits | Critical path approaches the sum of waits | Local computation and call overhead are additional; dependencies may require sequential order. |
| Ideally overlapped independent waits | Lower bound approaches the longest wait | This is not a guarantee; limits, queueing, setup, failures, and scheduling add time. |
| Thread communication through shared memory | Avoids mandatory process serialization | Synchronization, contention, visibility, and ownership complexity remain. |
| Process-based CPU parallelism | Startup plus data-transfer and serialization cost | Benefits require enough independent CPU work to amortize overhead and memory use. |
| Adding workers | Potential throughput gain with additional resource use | Scaling stops when serial work, the GIL boundary, contention, bandwidth, or a downstream service dominates. |

These are cost models, not measurements. Benchmark claims require a representative workload, environment record, repeated trials, and an explanation of uncertainty.

## 9. Production relevance and trade-offs

Start with the service objective and the bottleneck, not with a preferred concurrency API.

| Concern | Question to answer before adding concurrency |
|---|---|
| Correctness | What state is shared, who owns mutation, and what ordering is actually required? |
| Latency | Which independent waits lie on the critical path, and what is the deadline? |
| Throughput | Which resource saturates first as concurrency increases? |
| Capacity | What bounds tasks, threads, processes, connections, file descriptors, queue depth, and memory? |
| Failure | How are errors, timeouts, cancellation, partial results, and shutdown propagated? |
| Observability | Can traces distinguish running, waiting, queueing, retries, contention, and downstream latency? |
| Portability | Is the claim a Python guarantee, a regular-CPython GIL property, a free-threaded behavior, or an extension contract? |
| Testing | Can tests establish safety without assuming an exact schedule or relying on sleeps? |

For backend fan-out, unbounded overlap can move the bottleneck into a database or remote service and worsen tail latency. For CPU work, distributing tiny jobs may cost more than it saves. For shared state, ownership transfer or message passing can be easier to reason about than a large lock surface. The best design is usually the smallest mechanism that meets measured correctness, latency, throughput, and operational goals.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| Concurrency and parallelism are distinct task relationships | General computing / language-neutral model | Not version-specific | Same model | Do not infer a mechanism or core count from the term alone. |
| One thread executes Python bytecode at a time in a regular GIL-enabled CPython interpreter | CPython implementation detail | Long-standing | Same high-level CPython 3.11 model | Not a Python-language guarantee and not a claim about native code that releases the GIL. |
| `sys.setswitchinterval()` exposes an ideal interpreter thread-switch interval | CPython API behavior | Python 3.2 | Same API | The OS chooses the next thread; do not use timing for correctness. |
| Optional free-threaded CPython build | CPython, version-dependent | Python 3.13 | Unavailable; use processes or documented native GIL-releasing work for CPU parallelism | It is not the default build, and extensions may re-enable the GIL. |
| `sysconfig.get_config_var("Py_GIL_DISABLED")` identifies free-threaded build support | CPython configuration | Python 3.13 | Treat CPython 3.11 as a regular GIL-enabled build | Build capability and current runtime GIL state are different questions. |
| `sys._is_gil_enabled()` reports current GIL state | CPython runtime API | Python 3.13 | No equivalent needed for the standard CPython 3.11 build | The leading underscore signals a CPython-specific boundary; feature-detect before use. |

Interview answers targeting Python 3.11 should lead with the regular GIL-enabled CPython model, then label free threading as a newer optional-build development rather than silently applying it to the interview runtime.

## 11. Practice brief

Exercises remain unsolved until the learner attempts them.

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-CON-010-P01` | Predict | 2 | Predict every event in the deterministic round-robin trace and justify why no event is parallel. | [`examples/scheduling_trace.py`](examples/scheduling_trace.py) |
| `PY-CON-010-P02` | Implement | 3 | Add an explicit waiting state so a task can be skipped until a synthetic event makes it runnable; preserve deterministic order and explain the model's limitation. | Create after the first attempt |
| `PY-CON-010-P03` | Debug | 3 | Produce a lost-update interleaving for `record_request` and identify the invariant that needs protection. | Inline |
| `PY-CON-010-P04` | Design | 4 | Classify five synthetic backend workloads and defend a sequential, thread, process, native, or async direction with caveats. | Create after the first attempt |
| `PY-CON-010-P05` | Review | 4 | Find every portability and correctness error in a proposal that treats the GIL as a universal lock. | Create after the first attempt |

## 12. Interview prompts

Do not read a prepared answer before attempting each prompt.

1. What is the difference between concurrency and parallelism? Give a one-core example and a multi-core example.
2. Why can threads improve an I/O-bound program on regular CPython even though the GIL exists?
3. A team wants to add 64 threads to speed up a CPU-heavy Python service. What facts and measurements do you request before recommending a design?

A strong answer should eventually demonstrate:

- the one-lane interleaving versus simultaneous-execution distinction;
- the regular CPython bytecode, blocking-I/O, native-code, and free-threaded boundaries;
- workload classification, synchronization needs, overhead, bounded capacity, and empirical validation.

## 13. Closed-book revision cues

Without reading the note:

1. Define concurrency, parallelism, scheduling, CPU-bound work, and I/O-bound work in one sentence each.
2. Reconstruct the one-lane/two-lane timeline and label the waiting-shaped and compute-shaped tasks.
3. Predict the event order in `scheduling_trace.py` and explain why task overlap is conceptual rather than simultaneous.
4. Draw a lost-update schedule that remains possible under the regular CPython GIL.
5. Choose an initial execution direction for independent database waits and for a pure-Python CPU loop, then state what could overturn each choice.

## 14. Authoritative sources

Important claims are cited near the relevant paragraphs. Sources actually read for this initialization:

1. [Python Glossary — concurrency, parallelism, global interpreter lock, and free threading](https://docs.python.org/3.14/glossary.html), Python 3.14, accessed 2026-08-27.
2. [`threading` — GIL and performance considerations](https://docs.python.org/3.14/library/threading.html#gil-and-performance-considerations), Python 3.14, accessed 2026-08-27.
3. [Thread states and the global interpreter lock](https://docs.python.org/3.14/c-api/threads.html#thread-state-and-the-global-interpreter-lock), Python 3.14 C API, accessed 2026-08-27.
4. [`sys.setswitchinterval()`](https://docs.python.org/3.14/library/sys.html#sys.setswitchinterval), Python 3.14 Standard Library, accessed 2026-08-27.
5. [Python support for free threading](https://docs.python.org/3.14/howto/free-threading-python.html), Python 3.14, accessed 2026-08-27.
6. [PEP 703 — Making the Global Interpreter Lock Optional in CPython](https://peps.python.org/pep-0703/), accepted proposal, accessed 2026-08-27.
