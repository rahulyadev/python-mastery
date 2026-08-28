# PY-CON-040 — Multiprocessing, IPC, shared memory, and process isolation

[Curriculum entry](../../../CURRICULUM.md#py-con-040) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-CON-040`

## Physical Notebook Core

### Problem this concept solves

A thread shares one process's memory and runtime constraints. A process gives work a separate address space and interpreter instance, which can isolate failure and let CPU-bound Python work use multiple cores—but every input, result, failure, resource, and shutdown transition must now cross an explicit boundary.

### One-sentence mental model

> Treat each worker process as a separate service on the same machine: choose how it starts, send bounded messages or explicitly shared bytes, collect an outcome, and make one owner responsible for shutdown and cleanup.

### One important visual

```text
PARENT PROCESS                              WORKER PROCESS
private Python heap A                       private Python heap B

job object -- serialize --> [Pipe/Queue] -- recreate --> local job object
result    <-- serialize --- [Pipe/Queue] <-- create ---- local result

             explicit shared-memory block
             +---------------------------+
parent view  | bytes + ownership protocol |  child view
             +---------------------------+
```

#### How to read this visual

Read the message arrows left-to-right for input and right-to-left for output: ordinary Python objects are encoded and reconstructed, not jointly owned. Then read the lower box as the exceptional path: both processes can view the same bytes only because the program created an explicit shared-memory resource and a separate access protocol.

#### Key insight

Process isolation is the default. Communication, sharing, synchronization, failure reporting, and cleanup are separate design decisions.

#### Simplification or limitation

This is a conceptual ownership diagram, not literal CPython or operating-system memory layout. It omits copy-on-write pages, feeder and resource-tracker processes, kernel buffers, native extensions, handles, caches, and remote hosts.

### Governing rules or invariants

1. Child targets and their arguments must work under an explicit available start method; portable code uses importable top-level callables and guards executable entry points.
2. Every accepted job must reach one owner-visible terminal classification: success, application failure, abnormal exit, timeout, or explicitly indeterminate.
3. A queue or pipe transfers serialized values; shared memory transfers byte access, not synchronization, schema, or ownership.
4. The creating process owns process joins, channel closure, pool shutdown, and the final unlink of named shared memory.
5. Graceful stop is a protocol; forced termination is a last resort because it can skip cleanup and damage shared synchronization or IPC state.

### Minimal example

```python
import multiprocessing as mp


def square(value, sender):
    try:
        sender.send(("ok", value * value))
    except Exception as error:
        sender.send(("error", type(error).__name__, str(error)))
    finally:
        sender.close()


if __name__ == "__main__":
    context = mp.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=square, args=(7, sender))
    process.start()
    sender.close()
    outcome = receiver.recv()
    process.join()
    print(outcome, process.exitcode)
```

Expected reasoning:

1. `spawn` starts a fresh interpreter, so the target must be discoverable by importing the main module safely.
2. The integer input and tuple result cross a serialization boundary; neither process shares the other's ordinary Python objects.
3. Receiving the application outcome and inspecting `exitcode` answer different questions.
4. The parent closes its duplicate sender, receives before final cleanup, and joins the child it created.

### One failure or misconception

**Mistake:** “Processes are just faster threads, and the child can use the parent's current globals because Linux forks.”

**Correction:** Processes have higher startup and transfer costs, platform-dependent start semantics, and separate ordinary heaps. Python 3.14 no longer defaults to `fork` anywhere; write import-safe code, pass dependencies explicitly, and use a documented IPC or shared-memory protocol.

### Important trade-offs

- Processes can run CPU-bound Python on multiple cores and isolate address spaces, but startup, memory, serialization, context switching, supervision, and deployment are more expensive than a direct call.
- Messages simplify ownership and failure reasoning but copy and serialize data; shared memory can avoid large copies but adds layout, synchronization, lifetime, and crash-cleanup obligations.
- Local multiprocessing is convenient but not durable: a process or machine restart loses in-memory queues and state.

### Interview-revision cues

- Reconstruct: start method → import/bootstrap → serialized arguments → child work → result/failure → join → cleanup.
- Predict: which state is copied, re-imported, serialized, or truly shared?
- Compare: `Pipe`, `Queue`, manager proxy, `Value`/`Array`, `SharedMemory`, `Pool`, and an external worker system.
- Diagnose: entry-point recursion, unpicklable targets, queue/join hangs, silent child failure, leaked shared memory, and unsafe termination.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Concurrency, parallelism, and asynchronous Python |
| Canonical ID | `PY-CON-040` |
| Learning outcome | Use `multiprocessing`, start methods, IPC, pools, shared memory, serialisation, and process isolation. |
| Hard prerequisites | `PY-CON-010`, `PY-MOD-020`, `PY-IOP-010` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Professional |
| Interview frequency | Medium |
| Backend relevance | High |
| Depth | D3 |
| Scope | Standard library, Platform-specific |
| Size | L |
| Evidence profile | E+C+D+X |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4, regular GIL-enabled build, Linux x86_64 |
| Last source audit | 2026-08-28 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. choose and explicitly propagate a multiprocessing context while explaining `spawn`, `fork`, and `forkserver` platform and version boundaries;
2. design import-safe process targets, supervise lifecycle and exit status, and distinguish application failures from abnormal process termination;
3. select among pipes, queues, manager proxies, synchronized ctypes, and named shared memory from ownership, transfer, synchronization, and cleanup requirements;
4. build and shut down a bounded process pipeline or pool without relying on queue inspection, garbage collection, or forced termination for the normal path;
5. classify serialization and authentication trust boundaries, including why automatically unpickling untrusted messages is unsafe;
6. diagnose entry-point recursion, pickling failures, queue feeder hangs, ordering assumptions, unsafe resource inheritance, leaked shared memory, and worker loss.

Required evidence:

- reconstruct the process/IPC ownership visual and explain every lifecycle invariant without reading;
- complete prediction, implementation, and debugging practice while preserving first attempts and deterministic tests;
- run and interpret one start-method experiment with actual environment and output;
- transfer the design to a bounded backend-style worker boundary and defend when local multiprocessing is or is not appropriate.

Initialization created source-checked material and runnable examples. It did not provide learner evidence, so the learning state remains `Not started` and the artifact remains `Draft`.

## 2. Prerequisite bridge

The tracker currently marks all three hard prerequisites `Not started`. These bridges are enough to enter this unit, but they do not replace or complete the prerequisite units.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-CON-010` — Concurrency, parallelism, scheduling, and the GIL model | Process choice depends on CPU-bound versus I/O-bound work and the distinction between concurrency and parallel execution. | A regular CPython process normally has one GIL for Python bytecode; separate processes have separate interpreter state and can execute CPU work on different cores, while total speed still depends on workload, transfer, startup, and hardware. |
| Hard | `PY-MOD-020` — Import resolution, `sys.path`, and module caching | `spawn` and `forkserver` require child bootstrap/import behavior that exposes import side effects and non-importable targets. | Import executes top-level module code once per interpreter and caches a module in that interpreter's `sys.modules`; executable process creation belongs under `if __name__ == "__main__"`, and child targets should live at importable module scope. |
| Hard | `PY-IOP-010` — Text and binary files, streams, buffering, and encodings | Pipes, queues, shared memory, handles, buffering, byte schemas, and cleanup are I/O/resource concerns. | Bytes need an explicit schema and encoding; buffered writes can outlive the call that enqueued them; each process closes its own endpoint or handle; named resources need a clearly assigned final cleanup owner. |

Recommended follow-up: study each prerequisite in its dedicated topic chat. Continue here by treating the bridges as explicit assumptions.

## 3. Vocabulary and professional English

### Isolation

| Item | Content |
|---|---|
| Pronunciation | eye-suh-LAY-shuhn |
| Simple English meaning | Separation that limits direct interference. |
| Hindi cue | अलगाव |
| Meaning in this Python context | Ordinary mutable state in one process is not the same live Python object in another process. |

Natural examples:

1. The test uses process isolation to contain a crashing parser.
2. Isolation reduces accidental sharing but does not create a security sandbox by itself.
3. Each worker has an isolated module cache.
4. **Interview:** Process isolation changes how arguments, results, and failures cross the boundary.
5. **Engineering discussion:** We chose isolation because the native library occasionally corrupts its own process state.

### Serialize

| Item | Content |
|---|---|
| Pronunciation | SEER-ee-uh-lize |
| Simple English meaning | Convert structured data into a transferable representation. |
| Hindi cue | डेटा को भेजने योग्य रूप देना |
| Meaning in this Python context | Encode an object for a pipe, queue, worker argument, result, or stored message; `multiprocessing` commonly uses pickle internally. |

Natural examples:

1. Serialize only the fields the worker actually needs.
2. Large payloads can make serialization dominate the useful work.
3. The protocol serializes JSON into UTF-8 bytes.
4. **Interview:** A local closure fails because the child cannot serialize and import the target reliably under `spawn`.
5. **Engineering discussion:** We versioned the serialized message schema before deploying mixed worker versions.

### Ownership

| Item | Content |
|---|---|
| Pronunciation | OH-ner-ship |
| Simple English meaning | Clear responsibility for changing, closing, or releasing something. |
| Hindi cue | ज़िम्मेदारी / स्वामित्व |
| Meaning in this Python context | The rule that identifies which process may mutate data and which component must close, join, unlink, retry, or report failure. |

Natural examples:

1. The parent retains ownership of worker lifecycle.
2. A message transfers data, not necessarily business ownership.
3. Each worker owns a disjoint shared-memory range.
4. **Interview:** Without an unlink owner, named shared memory can leak after normal execution.
5. **Engineering discussion:** The queue consumer takes processing ownership only after the job is accepted and identified.

## 4. Deep explanation

### 4.1 Why process-based concurrency exists

`multiprocessing` starts subprocesses with an API deliberately similar to `threading`. Because each subprocess has its own interpreter state, regular CPython processes can execute Python work on separate cores instead of contending for one process's GIL. The package runs on POSIX and Windows, but it is unavailable on Android, iOS, and WASI. See the official [`multiprocessing` introduction and availability](https://docs.python.org/3.14/library/multiprocessing.html#introduction).

That capability does not imply a speedup. A process design adds interpreter startup, memory, scheduling, serialization, data copying, kernel IPC, result collection, and supervision. A small task, an I/O-bound task already handled well by threads or async I/O, or a task that moves far more data than it computes can be slower in processes. Measure only after proving semantics and using a representative workload.

Process isolation is also useful without parallel speed: a child can have a distinct environment, module state, file-descriptor set, native-library state, memory limit enforced externally, or crash boundary. It is still not a complete security boundary: the child normally runs as the same operating-system user and may inherit authority unless the deployment applies stronger controls.

### 4.2 Process lifecycle and two layers of outcome

A `Process` object begins in an initial state. `start()` may be called at most once and arranges for `run()` to execute in a new process. `join(timeout)` always returns `None`; after a bounded join, inspect `is_alive()` or `exitcode`. A normal return gives exit code zero, an uncaught Python exception normally gives one, and POSIX signal termination is represented by a negative signal number. Most lifecycle methods should be called only by the process that created the `Process` object. See the [`Process` reference](https://docs.python.org/3.14/library/multiprocessing.html#process-and-exceptions).

Keep two outcome layers:

| Layer | Question | Example |
|---|---|---|
| Application outcome | Did this identified job succeed or fail according to the worker protocol? | `Outcome(job_id="a", error="invalid input")` |
| Process outcome | Did the operating-system process terminate, and how? | `exitcode == 0`, `exitcode == 1`, or a signal code |

A zero process exit with no result is not automatically application success. A structured application failure can be validly reported by a process that then exits zero. A lost worker may leave a job indeterminate unless the parent has an acknowledgement, durable lease, idempotency rule, or other protocol evidence.

Explicitly join non-daemon children. On POSIX, an exited but unjoined child can remain a zombie until reaped. Daemon processes are not durable services: they are terminated rather than joined when non-daemon processes exit, and a daemon process may not create children.

### 4.3 Isolation, copying, inheritance, and sharing are different

An ordinary list passed to a child is not a jointly owned Python list. Under `spawn`, arguments are serialized into the fresh child. Under `fork`, the operating system initially gives the child a memory snapshot commonly implemented with copy-on-write pages, but later ordinary Python mutations are still local to the process. Under `forkserver`, child creation is delegated to a server process and application state must not be inferred from the caller's current globals.

Use these terms precisely:

- **serialized transfer:** encode a value, transmit bytes, and reconstruct another object;
- **inherited resource:** a child starts with access derived from its ancestor or start mechanism;
- **shared-memory resource:** multiple processes explicitly map the same bytes;
- **manager proxy:** a local proxy sends method requests to an object owned by a manager server process;
- **external shared state:** a database, file, cache, socket service, or other system is shared through its own consistency contract.

None of these is automatically equivalent to shared Python-object identity.

### 4.4 Start methods are part of the API contract

Python 3.14 supports three start methods depending on platform. `fork` is no longer the default on any platform; POSIX platforms that support descriptor passing default to `forkserver`, while Windows and macOS default to `spawn`. Code that requires `fork` must request it explicitly. Python 3.11 instead defaulted to `fork` on most POSIX systems. See [`Contexts and start methods`](https://docs.python.org/3.14/library/multiprocessing.html#contexts-and-start-methods) and the [Python 3.11 comparison](https://docs.python.org/3.11/library/multiprocessing.html#contexts-and-start-methods).

| Method | Initialization model | Availability/default in Python 3.14 | Main engineering consequences |
|---|---|---|---|
| `spawn` | Start a fresh interpreter with only required inherited handles/resources, then bootstrap/import the target environment. | POSIX and Windows; default on Windows and macOS. | Highest startup cost of the three; import safety and picklability are visible; unsafe parent resource assumptions fail early. |
| `fork` | POSIX `fork()` creates a child from the current process snapshot. | POSIX only; never the default in 3.14. | Fast creation can inherit unsafe thread/native-library state; explicitly requesting it is a deliberate platform decision. |
| `forkserver` | Start a mostly single-threaded server, then request that it fork new children. | Selected POSIX platforms; default on those in 3.14. | Avoids forking the caller's multithreaded state but adds a helper server and resource tracker; still requires import/pickling discipline. |

Prefer `multiprocessing.get_context(name)` inside applications and libraries. A context creates mutually compatible `Process`, `Queue`, `Lock`, `Pool`, and other objects without globally fixing the process-wide method. Some objects created under one context are incompatible with processes from another; for example, a lock from a `fork` context cannot simply be passed to a `spawn` or `forkserver` process. Libraries should accept a caller-provided context and document genuine start-method requirements.

`set_start_method()` is global, normally belongs inside the guarded main block, and should not be called more than once. A library that calls it silently can make the containing application impossible to compose.

### 4.5 Importability and the main guard

Under `spawn` and `forkserver`, the child must safely import enough program state to locate the target. Therefore:

1. put worker functions and picklable classes at importable module scope;
2. put process creation and executable side effects under `if __name__ == "__main__":`;
3. do not use a REPL-local function, lambda, nested closure, live generator, open transaction, or arbitrary framework object as a worker target or argument;
4. create per-process resources inside the target or a documented pool initializer;
5. pass immutable configuration or explicit handles rather than reading a parent's later global mutation.

The guard prevents a freshly bootstrapped interpreter from re-running top-level process creation recursively. It does not make every object picklable, remove import side effects, or guarantee that a framework supports child processes.

Frozen POSIX executables created by tools such as PyInstaller or cx_Freeze generally cannot use `spawn` or `forkserver`; `fork` may work only when the program does not use threads. Treat packaging support as a deployment constraint, not an afterthought.

### 4.6 Choose IPC from topology and ownership

| Mechanism | Topology and transfer | Strength | Main cost or hazard |
|---|---|---|---|
| `Pipe(duplex=False)` | One sending end and one receiving end. | Smallest explicit one-way channel; easy ownership. | Do not let multiple processes concurrently use the same end without synchronization. |
| Duplex `Pipe` / `Connection` | Two message-oriented endpoints with send/receive or byte methods. | Request/response and polling; can use byte schemas. | `send()`/`recv()` use pickle; simultaneous same-end access may corrupt data. |
| `Queue` | Multi-producer, multi-consumer FIFO abstraction. | Safer fan-in/fan-out and bounded capacity option. | Serialization, feeder thread, cross-producer ordering caveats, explicit closure. |
| `JoinableQueue` | Queue plus unfinished-task accounting. | Owner can wait for accepted work to be acknowledged. | Every `get()` including sentinels needs exactly one `task_done()`; job completion and worker exit are separate. |
| Manager proxy | Calls are forwarded to an object in a manager server process. | Flexible Python containers and even network-capable manager designs. | Proxy latency, serialization, manager lifecycle, coarse remote method semantics. |
| `Value` / `Array` / shared ctypes | Fixed-layout values in shared memory, optionally synchronized. | Simple numeric shared state. | Compound operations still need an explicit lock/invariant. |
| `SharedMemory` | Named byte buffer mapped by multiple processes. | Avoid repeated serialization/copy for large fixed-layout data. | Schema, range ownership, synchronization, bounds, close/unlink, crash cleanup. |

The standard-library guidance generally prefers message passing and avoiding shared state. That is a reasoning preference, not an absolute performance rule. Choose shared memory only when data movement is material and the program can state a simpler ownership protocol than the copying it replaces. See [`Pipes and Queues`](https://docs.python.org/3.14/library/multiprocessing.html#pipes-and-queues) and [`Sharing state between processes`](https://docs.python.org/3.14/library/multiprocessing.html#sharing-state-between-processes).

### 4.7 Serialization is a trust and compatibility boundary

Multiprocessing queues serialize every item with pickle; the receiver gets a recreated object that does not share memory with the original. `Connection.send()` and `recv()` also serialize and automatically unpickle. Targets, arguments, pool tasks, results, and exceptions may all encounter pickling or import constraints.

[`pickle` is unsafe for untrusted input](https://docs.python.org/3.14/library/pickle.html): a malicious pickle can execute arbitrary code while it is being reconstructed. A local child that the same trusted application created is a different trust boundary from a network client, plugin, downloaded file, compromised peer, or manager exposed beyond the local process family. `multiprocessing.connection.Listener` and `Client` support HMAC-based digest authentication, but authentication identifies possession of a shared key; it does not make a malicious authenticated pickle safe or provide message confidentiality.

For untrusted or cross-language boundaries, use a deliberately limited byte protocol such as size-bounded JSON, validate its schema after decoding, and authenticate/authorize at the transport or application boundary. The runnable [`ipc_protocol.py`](examples/ipc_protocol.py) uses `send_bytes()`/`recv_bytes(maxlength=...)`, UTF-8 JSON, an exact field set, operation allow-list, type checks, and a value-count bound. It is a teaching protocol, not a complete network security layer.

Serialization also creates a version contract. Prefer small immutable records with stable fields, version messages when producers and consumers may be deployed independently, and avoid sending complex live objects whose class import path or invariants may change.

### 4.8 Queue mechanics, ordering, and the join trap

`multiprocessing.Queue.put()` pickles the object and a background feeder thread later flushes bytes to an underlying pipe. Consequently:

- an immediately following `empty()` or `get_nowait()` observation may not reflect the just-completed put;
- messages from one producer preserve that producer's order, while messages from different producers can interleave;
- a child that has queued buffered data normally waits for its feeder to flush before it terminates;
- joining a producer before the parent drains a sufficiently large queued message can deadlock;
- killing a process while it uses a queue can corrupt the channel for other processes.

Do not use `qsize()`, `empty()`, or `full()` for check-then-act correctness. Use blocking operations with bounded timeouts and a protocol state. Do not reach for `cancel_join_thread()` as a casual repair: it permits the process to exit without waiting for buffered data and can lose that data. Fix ownership and receive/join order instead. See the official [queue notes and warnings](https://docs.python.org/3.14/library/multiprocessing.html#pipes-and-queues) and [programming guideline on joining queue producers](https://docs.python.org/3.14/library/multiprocessing.html#programming-guidelines).

For `JoinableQueue`, task accounting is explicit: each item removed by `get()` must lead to exactly one `task_done()`, normally in `finally`; `join()` waits for the unfinished-task counter to reach zero. That does not join worker processes or prove a result was delivered. Use separate evidence for work acknowledgement, result collection, and process exit.

### 4.9 Shared-state choices

`Value` and `Array` provide fixed-layout shared ctypes with optional synchronization. A synchronized wrapper makes individual access mutually exclusive, but a logical read–modify–write sequence still needs one lock covering the whole invariant. `RawValue` and `RawArray` omit the wrapper and require an external protocol.

A manager owns Python objects in a separate server process and gives clients proxies. This is flexible for dictionaries, lists, namespaces, locks, queues, and custom registered types, but each proxy operation may be a serialized round trip. Two separate proxy calls are not one atomic business transition unless the manager exposes one method that implements the complete transition. Protect a proxy if multiple threads in the same process share that proxy instance.

Named `SharedMemory` exposes a `memoryview` over bytes. One process creates a block; another attaches by name. The program defines shape, element type, byte order, offsets, bounds, writer ownership, and synchronization. Shared bytes do not carry Python type metadata or prevent a writer from corrupting another region.

Prefer ownership partitioning where each worker writes a disjoint range and the parent reads only after all workers join. If ranges overlap or readers observe concurrent writes, use synchronization that covers the relevant invariant and understand the representation's atomicity; do not assume a multi-byte write is automatically atomic or ordered across platforms.

### 4.10 Shared-memory lifetime

Every `SharedMemory` instance should call `close()` when that process no longer needs its handle. Exactly one lifecycle owner should call `unlink()` once the block is no longer needed by any process. On Windows, `unlink()` has no effect and the operating system deletes the block after all handles close. Access after unlink may fail differently by platform. See [`SharedMemory.close()` and unlink`](https://docs.python.org/3.14/library/multiprocessing.shared_memory.html#multiprocessing.shared_memory.SharedMemory.close).

Python 3.13 added the `track` parameter. Related processes created through `multiprocessing` share a resource tracker, so the default is normally appropriate. Independently launched Python processes can each get a tracker; with tracking enabled, the first such tracker to exit may delete a block still needed elsewhere. In that special topology, coordinate lifetime outside these unrelated processes and set `track=False` only when another component truly owns cleanup. The parameter is ignored on Windows. See [`SharedMemory` tracking](https://docs.python.org/3.14/library/multiprocessing.shared_memory.html#multiprocessing.shared_memory.SharedMemory).

A `SharedMemoryManager` can own and unlink blocks it created when the manager shuts down. This simplifies lifetime but adds another process and does not remove buffer-layout or concurrent-access obligations.

### 4.11 Pools amortize workers but add a scheduler lifecycle

A `Pool` keeps worker processes and distributes many calls. `map()` returns results in input order; `imap_unordered()` exposes completion order; `apply_async()` and `map_async()` return `AsyncResult` objects whose `get(timeout)` re-raises worker exceptions. Pick a chunk size intentionally: large chunks can reduce scheduling/serialization overhead but worsen load balance and latency; small chunks do the reverse.

Pool methods belong to the process that created the pool. Manage resources explicitly: after successful submissions, call `close()` to reject new work and let accepted tasks finish, then `join()`. On failure, `terminate()` then `join()` may be necessary. Do not rely on garbage collection to finalize a pool. A subtle contract is that leaving `with Pool(...)` calls `terminate()`, not graceful `close()`; ensure all needed results are collected inside the block or use explicit close/join when graceful drain is the lesson. See the [`Pool` lifecycle reference](https://docs.python.org/3.14/library/multiprocessing.html#multiprocessing.pool.Pool).

`maxtasksperchild` replaces a worker after a fixed number of tasks and can release worker-held resources or bound some accumulation. It is not a substitute for fixing leaks, isolating global state, or designing idempotent tasks. Python 3.13 changed the default pool size source from `os.cpu_count()` to `os.process_cpu_count()`; production code should often choose an explicit bound derived from CPU quotas, memory per worker, downstream capacity, and workload rather than accepting any runtime default.

`concurrent.futures.ProcessPoolExecutor`, covered in `PY-CON-050`, provides a more composable future-based interface. It uses the same fundamental process, importability, serialization, failure, and shutdown boundaries.

### 4.12 Cancellation, interruption, termination, and crash recovery

Prefer cooperative stop:

1. close admission;
2. send a stop message or set a shared event;
3. let the worker finish or explicitly abandon a safe boundary;
4. collect outcomes;
5. join with a deadline;
6. escalate only after classifying remaining work and resource risk.

Python 3.14 adds `Process.interrupt()` on POSIX, which sends `SIGINT` and normally raises `KeyboardInterrupt` in the child. Its Windows behavior is undefined, a child may catch and ignore the interrupt, and it does not create transactional rollback. Python 3.11 code should use a cooperative protocol when possible.

`terminate()` skips `finally` blocks and exit handlers, does not terminate descendants, and can corrupt a pipe or queue or leave locks/semaphores acquired. `kill()` is even less cooperative on POSIX. These are containment tools for a last-resort owner, not normal cancellation. If a deadline forces termination, record which jobs are acknowledged, complete, retryable, or indeterminate; make external side effects idempotent or transactional where required.

An in-memory process queue is not durable. If the parent or machine dies, accepted messages, results, acknowledgements, and retry decisions may disappear. Use an external durable queue and separately deployed workers when work must survive service restart, span machines, autoscale independently, enforce stronger resource isolation, or support robust delivery/retry semantics.

### 4.13 Execution sequence for a bounded job

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Parent validates identity, schema, payload size, and admission capacity. | Job is rejected or becomes accepted with a stable ID. |
| 2 | Parent encodes the job and puts it on a bounded channel. | Serialized bytes may be buffered; the original object is not shared ownership. |
| 3 | Worker receives and reconstructs the job. | Worker owns local computation; process exit remains separate. |
| 4 | Worker creates a success or failure record and sends it. | Application outcome is in transit; external side effects need their own atomicity. |
| 5 | Worker acknowledges queue work in `finally`. | Unfinished-task count can fall even when the application outcome is a failure. |
| 6 | Parent receives and validates the outcome, keyed by job ID. | Owner can correlate completion without relying on arrival order. |
| 7 | Parent closes admission, sends stop messages, and waits for accepted work. | No new jobs; graceful drain is in progress. |
| 8 | Parent joins workers and checks every exit code. | Worker lifecycle is terminal or explicitly timed out. |
| 9 | Parent closes queues/connections and unlinks owned shared resources. | Local process and IPC resources are released. |

## 5. Additional visual models

### 5.1 Queue producer join dependency

```text
child: queue.put(large payload)
       feeder thread ---- waits for pipe capacity ----+
       child exit waits for feeder                    |
                                                      |
parent: process.join() ---- waits for child exit -----+
        queue.get()     (cannot run while join blocks)
```

#### How to read this visual

Follow the child row until its feeder needs pipe capacity. Then follow the parent row: the parent waits for child exit before receiving, while child exit waits for the buffered bytes to be received. The arrows form a wait cycle.

#### Key insight

The fact that `put()` returned does not prove the bytes have left the child. Drain expected messages before joining a producer whose feeder may block.

#### Simplification or limitation

This is a conceptual wait-for graph for a sufficiently large buffered message. Pipe capacity, timing, payload representation, and feeder scheduling vary, so a small payload may hide the bug without making the lifecycle order correct.

### 5.2 Shared-memory ownership partition

```text
8 fixed-width slots

index:     0    1    2    3    4    5    6    7
owner:   [ worker A writes ][ worker B writes ]
parent:    initialize --------------------> join both -> read all -> unlink
```

#### How to read this visual

Each bracket is a half-open range assigned to one worker. The parent initializes before workers start, does not read during writes, joins both workers, then reads and performs the single final unlink.

#### Key insight

Disjoint ownership plus phase separation can remove the need for a write lock; shared memory itself did not provide that safety.

#### Simplification or limitation

The visual omits byte order, element width, cache behavior, false sharing, memory ordering, worker failure, validation, handles, and resource tracking. Overlapping access or concurrent reads need a stronger protocol.

## 6. Worked examples

All examples use only the standard library, explicit `spawn` contexts, importable targets, bounded waits, structured results, and owner-side cleanup. The checks are in [`tests/test_examples.py`](tests/test_examples.py).

### 6.1 Ordinary object isolation

[`process_isolation.py`](examples/process_isolation.py) passes a list to a child, mutates the child-visible list, and reports an immutable snapshot over a one-way pipe.

Prediction before execution:

- parent and child PIDs differ;
- the child reports `(1, 2, 3, 99)`;
- the parent's list remains `(1, 2, 3)`.

Observed on CPython 3.14.4:

```text
parent pid=2 values=(1, 2, 3)
child pid=4 values=(1, 2, 3, 99)
```

PIDs are run-specific. The state separation, not the numeric PID values, is the evidence.

### 6.2 Bounded queue pipeline

[`queue_pipeline.py`](examples/queue_pipeline.py) uses a `JoinableQueue(maxsize=4)`, two workers, immutable job/outcome records, one sentinel per worker, exact task accounting, owner-side result collection, and process exit checks.

Observed result:

```text
Outcome(job_id='job-a', value=9, error=None)
Outcome(job_id='job-b', value=None, error='ValueError: synthetic negative input')
Outcome(job_id='job-c', value=25, error=None)
exitcodes=(0, 0)
```

The sorted display order is reconstructed by job ID. It does not claim cross-process queue arrival order.

### 6.3 Byte-oriented IPC protocol

[`ipc_protocol.py`](examples/ipc_protocol.py) deliberately avoids `Connection.recv()` automatic unpickling. It bounds incoming bytes, decodes UTF-8 JSON, requires exact fields, allow-lists one operation, and checks types and element count.

Observed result:

```text
{'ok': True, 'result': 29}
{'error': 'ValueError: values must be a list of at most 100 integers', 'ok': False}
```

This demonstrates explicit validation, not comprehensive protection against CPU-heavy integers, transport impersonation, confidentiality loss, or all denial-of-service inputs.

### 6.4 Disjoint shared-memory partitions

[`shared_memory_partitions.py`](examples/shared_memory_partitions.py) stores six signed 64-bit big-endian integers in one named block. Two workers attach by name and own disjoint ranges. The parent waits for completion and exit, reads the combined buffer, closes its handle, and unlinks once.

Observed result:

```text
values=[10, 20, 30, 40, 50, 60]
partitions=[(0, 3), (3, 6)]
exitcodes=(0, 0)
```

No lock is needed in this controlled example because writer ranges do not overlap and the parent reads after joins. That conclusion does not generalize to arbitrary concurrent buffer access.

### 6.5 Graceful pool batch

[`pool_batch.py`](examples/pool_batch.py) maps three immutable batches with two workers and `chunksize=1`. The success path explicitly calls `close()` then `join()`; the exceptional owner path calls `terminate()` then `join()`.

Observed result:

```text
Summary(batch_id='batch-a', count=3, sum_of_squares=14)
Summary(batch_id='batch-b', count=2, sum_of_squares=41)
Summary(batch_id='batch-c', count=1, sum_of_squares=36)
```

This is a semantic demonstration, not a benchmark or evidence of faster execution.

### 6.6 Debugging example

Find the first invalid assumption before asking for replacement code:

```python
import multiprocessing as mp


def launch():
    context = mp.get_context("spawn")
    prefix = "invoice"
    worker = context.Process(target=lambda: print(prefix))
    worker.start()
    worker.join()


if __name__ == "__main__":
    launch()
```

Record:

- which boundary fails and in which process;
- why the main guard is necessary but insufficient;
- the smallest design change that makes dependencies explicit;
- a deterministic test that proves `spawn`, rather than an inherited `fork` snapshot, is being exercised.

The correction remains hidden until the learner attempts the diagnosis.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| Child mutates a passed list and parent expects the mutation. | The call syntax resembles a thread target. | Ordinary objects are serialized or isolated snapshots; use a result message or explicit shared resource. | Report both PIDs and both snapshots under `spawn`. |
| Code works only because Linux used `fork`. | Older POSIX Python defaults hid importability problems. | Python 3.14 does not default to `fork`; test an explicit portable context. | Run the same file with `spawn` and `forkserver` where available. |
| Process creation occurs at module import. | Top-level code feels like a normal script. | A spawned child imports/bootstrap-executes the main module; creation belongs under the main guard. | Use a bounded subprocess test and inspect recursive startup failure. |
| Lambda, nested target, or REPL function is submitted. | It is callable in the parent. | The child must serialize and locate an importable callable under spawn-like methods. | Force `spawn` in an importable test file. |
| `join(timeout)` returning means the process ended. | Thread/process joins feel boolean. | It always returns `None`; inspect `is_alive()` and `exitcode`. | Join a blocked child with a short timeout and assert it remains alive. |
| Zero exit code proves every job succeeded. | The process ended normally. | Application outcome and process outcome are separate. | Have a worker report a structured validation error and then return normally. |
| Parent joins a queue producer before receiving its large result. | `put()` already returned. | The feeder may still need the parent to drain the pipe before child exit. | Use a large controlled message and an outer test timeout. |
| `Queue.empty()` gates shutdown. | It looks like an authoritative snapshot. | Feeder delay and concurrent producers make inspection unsuitable for check-then-act logic. | Coordinate a put and immediate observation, then replace with protocol state. |
| Multiple producers imply one global FIFO. | The API is called a FIFO queue. | Per-producer order is preserved; messages from different producers may interleave. | Tag producer sequence numbers and run controlled fan-in. |
| `task_done()` means the outcome reached the parent. | Both sound like completion. | It decrements unfinished work; result delivery and worker exit need separate evidence. | Delay result consumption while task accounting reaches zero. |
| Manager dictionary operations form a transaction. | The object looks like a normal dictionary. | Separate proxy calls are separate remote operations. | Run competing read-then-write sequences; expose one atomic manager method instead. |
| `Value` locking makes `value += 1` one atomic invariant. | The wrapper is synchronized. | Compound read–modify–write needs a lock held across the complete transition. | Barrier-control two readers before writes. |
| Shared memory is “zero-copy and thread-safe.” | Both processes see one buffer. | It may reduce copies, but carries no layout or synchronization protocol. | Assign overlapping writes and compare with disjoint ownership. |
| Every process calls `unlink()`. | Every process closes its own handle. | Close is per handle; unlink is once per block and belongs to one lifecycle owner. | Test cleanup under worker success and worker failure. |
| `terminate()` is normal cancellation. | It stops the process promptly. | Cleanup can be skipped and queues/locks corrupted; descendants survive. | Terminate a worker holding a controlled resource in an isolated test only. |
| A local queue is durable. | Jobs remain while workers are busy. | Parent or machine restart loses in-memory state. | Write a recovery design and identify absent persistence/acknowledgements. |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| Start one process | Significant fixed startup plus imported module/resource initialization | Method, platform, imports, security tooling, and deployment dominate; no universal timing is claimed. |
| Serialize/transfer payload of `n` bytes | Usually `O(n)` encode plus `O(n)` copy/transport work | Object graph traversal, protocol, buffers, and OS implementation change constants and extra copies. |
| Queue put/get | Payload-dependent serialization and IPC; queue coordination overhead | `put()` may return before feeder flush completes. |
| Manager proxy method | At least one IPC round trip plus serialization and server execution | A sequence of calls multiplies latency and is not automatically atomic. |
| Shared-memory attach | OS/name-management fixed cost; access then depends on bytes touched | Avoids repeated message serialization but still needs layout, synchronization, and cache-coherence traffic. |
| Partitioned transform of `n` items over `p` workers | Useful work ideally near `O(n/p)` per balanced worker | Startup, skew, memory bandwidth, false sharing, and merge/coordination can dominate. |
| Pool map with chunk size `c` | Approximately `ceil(n/c)` scheduled chunks | Larger `c` lowers scheduling overhead but can worsen balance and tail latency. |
| One worker per request | `O(requests)` process startups | Usually inferior to bounded reuse unless strong per-request isolation is worth the cost. |
| Live worker memory | Interpreter + imports + worker state per process | Copy-on-write may initially share physical pages on POSIX fork, but writes and platform/start method change actual memory. |

Do not claim “processes are faster,” “shared memory is zero-copy,” or a numeric speedup without a recorded workload, runtime, start method, input distribution, warm-up, trials, timing method, raw observations, uncertainty, and limitations.

## 9. Production relevance and trade-offs

### Correctness and API design

- Make the multiprocessing context an injected dependency for reusable libraries.
- Define immutable, bounded, versioned messages with stable job IDs.
- Separate admission, processing, result delivery, acknowledgement, worker exit, and resource cleanup.
- Treat external side effects as idempotent or transactional; process isolation does not make them atomic.
- Use one owner for every process, channel endpoint, pool, manager, and named resource.

### Capacity and latency

- Bound process count by CPU quota, memory per worker, downstream capacity, and measured workload.
- Bound queue length, payload bytes, submit wait, job runtime, result retention, and shutdown time.
- Batch enough useful CPU work to amortize startup/serialization without producing unacceptable tail latency or imbalance.
- Avoid nested pools and accidental oversubscription from libraries that also start threads or processes.

### Failure handling and observability

- Include job ID, worker PID/name, start method, attempt, duration, outcome class, and exit code where appropriate; do not log sensitive payloads.
- Track accepted, queued, running, succeeded, application-failed, worker-lost, timed-out, retried, indeterminate, and rejected counts.
- Alert on abnormal exits, restarts, queue saturation, feeder/receive stalls, shutdown escalation, leaked named resources, and memory growth.
- Preserve the first failure and causal protocol state; never translate every child crash into a generic timeout.

### Security and deployment

- Never accept pickle from an untrusted source; authentication does not make hostile serialized code safe.
- Validate byte length before decode, then schema, types, ranges, and authorization.
- Remember that same-user local processes may access many of the same files, sockets, credentials, and shared-memory names; apply OS/container controls for stronger isolation.
- Test actual Windows, macOS, Linux, container, service-manager, frozen-executable, and framework constraints that matter to deployment.
- Use external durable workers when recovery, multi-host scale, independent rollout, stronger quotas, durable acknowledgement, or cross-language protocols are requirements.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| `spawn`, `fork`, and `forkserver` contexts on supported POSIX platforms | Standard library / Platform | 3.4 for POSIX additions | Same named contexts where the platform supports them | Windows supports only `spawn`; always check `get_all_start_methods()`. |
| POSIX default changed to `forkserver`; `fork` is default nowhere | Standard library / Version / Platform | 3.14 | Python 3.11 usually defaults to `fork` on POSIX; request a context explicitly for stable semantics | macOS and Windows use `spawn`; selected POSIX platforms use `forkserver`. |
| Multithreaded `fork` detection can raise `DeprecationWarning` | Standard library / Version / Platform | 3.12 | Avoid forking a multithreaded parent in 3.11 too; select `spawn` or `forkserver` where available | Warning detection is not proof that every unsafe native thread interaction was found. |
| `Process.interrupt()` | Standard library / Platform | 3.14 | Use cooperative event/message cancellation; reserve `terminate()` for last-resort containment | POSIX sends `SIGINT`; Windows behavior is undefined. |
| `SharedMemory` and `SharedMemoryManager` | Standard library / Platform | 3.8 | Available unchanged in 3.11 | Cleanup behavior differs on Windows; mobile/WASI availability is limited. |
| `SharedMemory(track=...)` | Standard library / Version / Platform | 3.13 | Omit the parameter in 3.11 and explicitly coordinate close/unlink ownership | Relevant especially to independently launched processes; ignored on Windows. |
| Pool default uses `os.process_cpu_count()` | Standard library / Version | 3.13 | Python 3.11 uses `os.cpu_count()`; specify `processes=` for an intentional bound | Neither default accounts for per-worker memory or downstream limits. |
| Pickle default protocol is 5 | Standard library / Version | 3.14 as the default | Python 3.11 defaults to protocol 4; explicitly negotiate a compatible protocol when persisting or crossing versions | Multiprocessing internal serialization remains an implementation/API boundary; do not depend on an implicit protocol. |
| Queue per-producer ordering and feeder behavior | Standard library contract | Supported in 3.11 | Same design | Cross-producer global order is not guaranteed. |
| Process exit-code and join contracts | Standard library contract | Supported in 3.11 | Same design | Signal-specific negative codes are POSIX-oriented. |

The examples deliberately use Python 3.11-compatible syntax and APIs except when a version-specific feature is discussed rather than executed.

## 11. Practice brief

The separate [`practice/README.md`](practice/README.md) protects attempts and progressive hints.

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-CON-040-P01` | Predict | 2 | E+D | Start-method and child-visible-state trace |
| `PY-CON-040-P02` | Implement | 3 | C+D | Supervised checksum boundary with structured failures |
| `PY-CON-040-P03` | Debug | 4 | D+X | Queue feeder/join hang diagnosis |
| `PY-CON-040-P04` | Implement | 4 | C+D | Bounded multi-process transform pipeline |
| `PY-CON-040-P05` | Experiment | 4 | C+X | Copy-based IPC versus partitioned shared memory |
| `PY-CON-040-P06` | Design | 5 | E+D+R | Secure, observable production process boundary |

## 12. Interview prompts

Answer one at a time; do not read or write full answers before attempting.

1. Why can processes execute CPU-bound Python on multiple cores, and which costs can remove the benefit?
2. Compare `spawn`, `fork`, and `forkserver`, including Python 3.11 versus 3.14 defaults.
3. Why is the main guard necessary under `spawn`, and why is it not sufficient for picklability?
4. A child reports a validation failure and exits zero. Did the process succeed? Did the job succeed?
5. Why can joining a process before receiving its large queued message hang?
6. What ordering does a multiprocessing queue provide across one producer and across several producers?
7. Compare a manager dictionary, `Value`/`Array`, and `SharedMemory` for a multi-field invariant.
8. Who should call `close()` and `unlink()` for shared memory, and how does Windows differ?
9. Why does HMAC-authenticated `multiprocessing.connection` traffic not make hostile pickle safe?
10. What is surprising about `Pool.__exit__`, and how do you perform a graceful drain?
11. Design bounded shutdown when one CPU worker ignores cooperative cancellation.
12. When should an external job system replace local multiprocessing?

A strong answer should eventually demonstrate:

- exact isolation, start, import, serialization, IPC, process, and resource-lifetime mechanisms;
- version, platform, trust, failure, durability, and measurement boundaries;
- a production trade-off based on workload, ownership, capacity, recovery, and maintainability rather than “processes are faster.”

## 13. Closed-book revision cues

Without reading the note:

1. Draw the two private heaps, serialized message channel, and explicit shared-memory block.
2. Reconstruct the nine-step bounded-job lifecycle from validation through cleanup.
3. Predict child-visible global state under `spawn` and `fork`; label what is observation versus contract.
4. Draw the queue feeder/join wait cycle and state the correct ownership question.
5. Explain why shared memory supplies bytes but not type, synchronization, or cleanup policy.
6. Separate application failure, abnormal process exit, timeout, cancellation request, and indeterminate job state.
7. State the Python 3.14 start-method change and the Python 3.11 interview answer.
8. Defend one realistic choice among a queue, manager, shared memory, pool, and external durable worker system.

## 14. Authoritative sources

Only sources opened and used for this unit are listed.

1. [`multiprocessing` — Process-based parallelism](https://docs.python.org/3.14/library/multiprocessing.html), especially Introduction, Contexts and start methods, Pipes and Queues, Process Pools, Listeners and Clients, and Programming guidelines; Python 3.14.7 documentation, accessed 2026-08-28.
2. [`multiprocessing.shared_memory` — Shared memory for direct access across processes](https://docs.python.org/3.14/library/multiprocessing.shared_memory.html), especially `SharedMemory`, tracking, close/unlink, and `SharedMemoryManager`; Python 3.14.7 documentation, accessed 2026-08-28.
3. [`pickle` — Python object serialization](https://docs.python.org/3.14/library/pickle.html), security warning, protocol compatibility, and comparison with JSON; Python 3.14.7 documentation, accessed 2026-08-28.
4. [`multiprocessing` — Python 3.11 documentation](https://docs.python.org/3.11/library/multiprocessing.html), Contexts and start methods; Python 3.11.15 documentation, accessed 2026-08-28.
5. [`multiprocessing.shared_memory` — Python 3.11 documentation](https://docs.python.org/3.11/library/multiprocessing.shared_memory.html), compatibility comparison; Python 3.11.15 documentation, accessed 2026-08-28.

## 15. Durable clarification log

| Date | Clarification | Why it belongs in canonical notes | Source or evidence |
|---|---|---|---|
| 2026-08-28 | Python 3.14 no longer defaults to `fork` anywhere and uses `forkserver` by default on supported POSIX platforms. | Older interview answers and Linux-only code often assume the Python 3.11 POSIX default; the difference changes importability and resource-inheritance behavior. | Python 3.14 and 3.11 `multiprocessing` context documentation; `EXP-01` observation. |
| 2026-08-28 | Leaving a `Pool` context invokes `terminate()`, while graceful accepted-work completion is expressed by `close()` followed by `join()`. | “Use a context manager” is normally safe advice, but the exact pool exit contract matters when unfinished work or result collection is possible. | Python 3.14 `Pool` reference; `examples/pool_batch.py`. |
| 2026-08-28 | `SharedMemory(track=...)` solves one lifecycle problem but can shorten lifetime for independently launched Python processes with separate trackers. | Treating resource tracking as universally protective can delete a block still in use by an unrelated process family. | Python 3.14 `SharedMemory` parameter documentation. |
