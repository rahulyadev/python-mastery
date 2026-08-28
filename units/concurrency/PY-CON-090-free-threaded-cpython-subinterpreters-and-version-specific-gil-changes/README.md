# PY-CON-090 — Free-threaded CPython, subinterpreters, and version-specific GIL changes

[Curriculum entry](../../../CURRICULUM.md#py-con-090) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-CON-090`

## Physical Notebook Core

### Problem this concept solves

“Python has a GIL” is no longer a sufficient deployment model. Modern CPython can use a regular build, a free-threaded build whose GIL may still be enabled at runtime, or multiple isolated interpreters with separate GILs. Code, dependencies, and operations must agree on the actual mode.

### One-sentence mental model

> Build capability, runtime GIL state, and interpreter topology are separate axes; detect all three, then protect application invariants explicitly.

### One important visual

```text
CPython 3.14 execution choices

BUILD                     TOPOLOGY                         SHARED-STATE RULE
regular CPython ───────┬─ one interpreter + N threads ─┬─ shared objects; one GIL
                      └─ N isolated interpreters ──────┼─ separate state; one GIL each
free-threaded CPython ─── one interpreter + N threads ─┼─ shared objects; GIL may be off/on
N processes ───────────────────────────────────────────┴─ separate address spaces

                           every shared invariant still needs an explicit protocol
```

#### How to read this visual

Read left to right. First identify the executable's build, then the number of interpreter contexts, then ask which mutable state is genuinely shared. The last line applies to every path that shares mutable state; neither a present nor absent GIL is an application transaction.

#### Key insight

Free threading and subinterpreters are different routes to parallelism: one changes synchronization inside a shared interpreter, while the other changes the isolation boundary.

#### Simplification or limitation

This is a CPython 3.14 conceptual deployment map, not a literal runtime-memory diagram. It omits native libraries that release the GIL, accelerators, operating-system scheduling, cross-interpreter queues, allocator details, and mixed topologies.

### Governing rules or invariants

1. Do not infer the GIL state from `sys.version_info`; inspect build support and current runtime state separately.
2. The GIL protects CPython runtime machinery, not a multi-step application invariant such as check-then-write.
3. Creating an interpreter gives isolation, not concurrency; combine it with another thread or an executor to run concurrently.
4. A native extension must be audited separately for free-threaded execution and isolated-interpreter use.

### Minimal example

```python
import sys
import sysconfig

free_threaded_build = bool(
    sysconfig.get_config_var("Py_GIL_DISABLED")
)
gil_probe = getattr(sys, "_is_gil_enabled", None)
gil_enabled = gil_probe() if callable(gil_probe) else None

print(free_threaded_build, gil_enabled)
```

Expected reasoning:

1. The configuration variable answers whether this executable was built to support disabling the GIL.
2. The runtime probe answers whether the GIL is active in this process; on Python 3.11 it is unavailable, so the compatibility result is `None` rather than a fabricated answer.

On the initially tested regular CPython 3.14.4 runtime, the observed pair was `False True`.

### One failure or misconception

**Mistake:** “The service runs Python 3.14, so its threads execute Python code without a GIL.”

**Correction:** Python 3.14 makes the free-threaded build officially supported, but it remains optional and is not the default. Even a free-threaded executable can start or become GIL-enabled.

### Important trade-offs

- Free-threaded threads retain ordinary shared-memory ergonomics but widen the set of simultaneous interleavings and require compatible native dependencies.
- Isolated interpreters provide parallelism with less implicit sharing, but imports, mutable state, arguments, results, errors, and shutdown cross an explicit boundary.
- Processes offer a stronger fault and address-space boundary, usually with higher startup and data-transfer cost.

### Interview-revision cues

- Name the three independent facts: build capability, current GIL state, and interpreter topology.
- Explain why `if key not in cache: cache[key] = build()` is not made correct by the GIL.
- Compare a free-threaded `ThreadPoolExecutor`, `InterpreterPoolExecutor`, and `ProcessPoolExecutor` for one CPU-bound service stage.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Concurrency and parallelism |
| Canonical ID | `PY-CON-090` |
| Learning outcome | Understand version-specific GIL changes, supported free-threaded CPython, subinterpreters, compatibility, and migration risks |
| Hard prerequisites | `PY-CON-010`, `PY-CON-020`, `PY-CON-040`, `PY-MPR-010` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Advanced |
| Interview frequency | Medium |
| Backend relevance | Medium |
| Depth | D4 |
| Scope | CPython |
| Size | XL |
| Evidence profile | E+D+X+R |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4, Linux x86_64, regular GIL-enabled build |
| Last source audit | 2026-08-29 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. reconstruct the CPython 3.11–3.14 GIL and subinterpreter timeline without treating a version number as a runtime-mode probe;
2. detect build support, active GIL state, and isolated-interpreter availability, then explain what each result proves and does not prove;
3. distinguish free-threaded shared memory, per-interpreter isolation, and process isolation when choosing a backend concurrency boundary;
4. identify Python and C-extension assumptions that were accidentally protected by a process-wide GIL;
5. design a staged migration with dependency qualification, deterministic race tests, production observability, rollback, and compatibility gates.

Required evidence:

- a closed-book explanation and reconstruction of the three-axis model and version timeline;
- a debugging or review artifact that identifies the first unsafe shared-state invariant and supplies deterministic evidence;
- a runtime experiment that records the executable, build flag, live GIL state, interpreter capabilities, observed output, and limitations;
- a production migration review that separates pure-Python correctness, native-extension readiness, data-transfer boundaries, and operational rollback.

Initialization creates the learning surfaces and tests them; it does not supply learner evidence or advance the `Not started` learning state.

## 2. Prerequisite bridge

The tracker records no learning evidence for any hard prerequisite. The first three notes exist in `Draft`; `PY-MPR-010` is still absent. These bridges permit accurate reading of this unit but do not complete those prerequisites.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | [`PY-CON-010`](../PY-CON-010-concurrency-parallelism-scheduling-and-the-gil-model/README.md) | Supplies concurrency, parallelism, scheduling, CPU/I/O work, and the baseline GIL model | Concurrency is overlapping progress; parallelism is simultaneous execution. A regular CPython GIL usually serializes Python execution inside one interpreter but may be released by blocking or native work. |
| Hard | [`PY-CON-020`](../PY-CON-020-threads-lifecycle-context-and-thread-safe-boundaries/README.md) | Supplies thread ownership, context, failure, joining, and safe shared-state boundaries | Threads share a process and usually Python objects. Own their lifetime, propagate failures, join them, and use locks or message passing for application invariants. |
| Hard | [`PY-CON-040`](../PY-CON-040-multiprocessing-ipc-shared-memory-and-process-isolation/README.md) | Supplies the comparison boundary for CPU parallelism and isolation | Processes have separate address spaces and communicate explicitly. Serialization, startup, shutdown, failure, and duplicated state are part of their contract. |
| Hard | `PY-MPR-010` | Supplies references, CPython reference counting, finalization, and weak-reference boundaries | CPython object lifetime depends on references, but timing is implementation- and build-sensitive. Free-threaded reference-counting strategies can delay reclamation; never use immediate destruction as cross-thread coordination. |

Recommended next action after this unit: initialize the missing `PY-MPR-010` unit before relying on object-lifetime details. `PY-CON-090` also feeds directly into [`PY-CPY-110`](../../../CURRICULUM.md#py-cpy-110), where the runtime and C-API mechanisms are studied more deeply.

## 3. Vocabulary and professional English

### Isolation

| Item | Content |
|---|---|
| Pronunciation | eye-suh-LAY-shun |
| Simple English meaning | Separation that limits what state can affect another part |
| Hindi cue | अवस्था और प्रभाव को अलग रखने की सीमा |
| Meaning in this Python context | Each subinterpreter has separate runtime state and module objects, so interaction must cross a deliberate boundary. |

Natural examples:

1. Interpreter isolation prevents one worker's module global from becoming another worker's module global.
2. The test verifies namespace isolation without claiming a security sandbox.
3. Process isolation survives faults that may still terminate a multi-interpreter process.
4. **Interview:** Multiple interpreters trade implicit shared memory for explicit communication and independent GILs.
5. **Engineering discussion:** We chose process isolation because the native library can corrupt process-wide state.

### Contention

| Item | Content |
|---|---|
| Pronunciation | kun-TEN-shun |
| Simple English meaning | Competition for the same limited resource |
| Hindi cue | एक ही संसाधन के लिए प्रतिस्पर्धा |
| Meaning in this Python context | Threads compete for a GIL, object lock, application lock, cache line, allocator path, or downstream capacity. |

Natural examples:

1. Removing one global lock can expose contention on a smaller lock.
2. Shared counters create cache-line contention even when their updates are correct.
3. A workload can scale poorly because of contention rather than insufficient worker count.
4. **Interview:** Free threading removes the mandatory interpreter-wide bottleneck, not all synchronization costs.
5. **Engineering discussion:** The profile shows contention around the shared cache, so adding threads will not solve the latency spike.

### Serialization

| Item | Content |
|---|---|
| Pronunciation | seer-ee-uh-luh-ZAY-shun |
| Simple English meaning | Converting data to a transferable representation; also forcing events into an order |
| Hindi cue | डेटा को भेजने योग्य रूप देना; या क्रम में चलाना |
| Meaning in this Python context | Interpreter-pool arguments and results are pickled, while a GIL serializes execution; the two meanings must not be confused. |

Natural examples:

1. The callable failed at the serialization boundary before worker execution.
2. Immutable batches keep the transfer contract small.
3. The GIL serializes Python execution but does not serialize a whole business transaction.
4. **Interview:** `InterpreterPoolExecutor` gains isolation and parallelism at the cost of pickle-based task transfer.
5. **Engineering discussion:** Serialization dominates the task cost, so the batch is too fine-grained.

### ABI

| Item | Content |
|---|---|
| Pronunciation | A-B-I |
| Simple English meaning | The binary-level contract between compiled components |
| Hindi cue | compiled हिस्सों के बीच binary contract |
| Meaning in this Python context | Regular and free-threaded CPython builds require different extension binaries, commonly identified by a `t` suffix for the free-threaded ABI. |

Natural examples:

1. The source API compiled, but the wheel targeted the wrong ABI.
2. CI publishes a separate free-threaded wheel.
3. An ABI tag is not evidence that the extension's internal state is race-free.
4. **Interview:** Source compatibility, API compatibility, and ABI compatibility are separate claims.
5. **Engineering discussion:** The release gate checks both `cp314` and `cp314t` artifacts before rollout.

## 4. Deep explanation

### 4.1 Why the mechanisms exist

A regular CPython interpreter uses a GIL so runtime code can operate on Python objects under one broad synchronization regime. That design simplifies much of CPython's implementation and makes threads effective for overlapping blocking work, but CPU-bound Python threads inside the same interpreter cannot normally execute Python bytecode simultaneously.

Two modern mechanisms attack that bottleneck differently:

- a **free-threaded build** makes the GIL optional and adds finer-grained runtime synchronization so threads in one interpreter may execute Python code in parallel;
- **isolated interpreters** move most runtime state behind separate interpreter boundaries, allowing each interpreter to have its own GIL and run in a different thread.

Neither mechanism is “multiprocessing but faster.” Free-threaded execution keeps mutable Python objects naturally shareable and therefore keeps race risk. Isolated interpreters make sharing opt-in but remain inside one process, so they do not provide an operating-system security or crash-containment boundary. Processes remain important where memory, privileges, lifecycle, or native-library faults must be isolated.

### 4.2 Three facts, not one version check

Treat these as independent deployment facts:

| Axis | Question | Reliable probe or evidence | What it does not prove |
|---|---|---|---|
| Build capability | Can this executable run with the GIL disabled? | `sysconfig.get_config_var("Py_GIL_DISABLED") == 1`; free-threaded ABI/build metadata | That the GIL is disabled now |
| Runtime state | Is the GIL active in this process now? | `sys._is_gil_enabled()` on CPython 3.13+ | That code is race-free or that every dependency supports no-GIL execution |
| Interpreter topology | How many isolated interpreter contexts run, and on which threads? | Owned interpreter/executor configuration and runtime inventory | That work is concurrent merely because an interpreter object exists |

The full capability probe is [`runtime_modes.py`](examples/runtime_modes.py). It returns `None` when an older runtime has no live-GIL probe instead of treating absence as disabled. This distinction is operationally important: an extension import can enable the GIL in a free-threaded process, and `-X gil` or `PYTHON_GIL` can select a runtime state supported by that executable ([Python support for free threading](https://docs.python.org/3.14/howto/free-threading-python.html)).

Do not make a hot-path branch on these values. Detect them at startup, validate the deployment, emit bounded metadata, and fail or degrade according to an explicit compatibility policy.

### 4.3 Version timeline: 3.11 through 3.14

| Version | Regular CPython threads | Free-threaded build | Isolated-interpreter milestone | Practical compatibility statement |
|---:|---|---|---|---|
| 3.11 | One process-wide GIL serializes Python execution across ordinary threads and legacy subinterpreters | Unavailable as a supported CPython build | Multiple interpreters are principally a C-API facility and share the legacy GIL | Use processes or native code that releases the GIL for CPU parallelism; explicit locks remain necessary for shared invariants |
| 3.12 | Default threading model remains GIL-enabled | Not yet the PEP 703 distribution mode | PEP 684 adds sufficiently isolated interpreters with an own-GIL configuration through `Py_NewInterpreterFromConfig()` | Extension state and multi-interpreter compatibility become explicit concerns |
| 3.13 | Regular build remains the default | PEP 703 introduces an explicitly experimental `--disable-gil` build, live state probe, `-X gil`, `PYTHON_GIL`, and free-threaded extension opt-in | Per-interpreter GIL work remains available primarily through lower-level APIs | Test both regular and `t` binaries; absence of an extension declaration may re-enable the GIL |
| 3.14 | Regular GIL-enabled build still exists and remains the default | PEP 779 moves the optional free-threaded build to officially supported phase II | PEP 734 adds `concurrent.interpreters`; `InterpreterPoolExecutor` adds a familiar high-level pool | Treat Python 3.14 as a capability expansion, not an automatic mode change |

PEP 779 explicitly distinguishes phase II, “officially supported but still optional,” from a future phase in which free-threaded Python could become the default ([PEP 779](https://peps.python.org/pep-0779/)). The timeline is CPython-specific; other Python implementations may use different locking or interpreter models.

### 4.4 What the GIL does—and does not do

In a GIL-enabled interpreter, one thread must hold that interpreter's GIL to operate on Python objects. CPython can switch the holder, detach thread state around blocking I/O, and allow native code to run without holding the GIL. A regular build can therefore overlap I/O and can run native work in parallel when the extension deliberately releases the lock.

The GIL has never been a substitute for an application lock:

```python
if request_id not in cache:
    cache[request_id] = build_response(request_id)
```

The invariant spans a membership test, arbitrary user work, and assignment. A switch, blocking call, callback, or native release can occur between those conceptual steps. Two workers can both build, overwrite, duplicate a side effect, or expose an intermediate state. Code that was merely hard to interleave on one build can become frequently concurrent on a free-threaded build.

Free-threaded CPython uses internal synchronization for built-in containers so concurrent access does not simply corrupt interpreter bookkeeping. Official guidance still recommends explicit synchronization instead of relying on undocumented or version-sensitive container behavior ([free-threading thread safety](https://docs.python.org/3.14/howto/free-threading-python.html#thread-safety)). Protect the complete logical invariant, not an assumed bytecode or one container method.

[`shared_state_race.py`](examples/shared_state_race.py) forces both threads to read the same value before either writes. It loses one update on the tested GIL-enabled build, proving that “a GIL exists” and “the business invariant is atomic” are different claims. The example does not benchmark race frequency.

### 4.5 Free-threaded CPython

#### Build and startup

A source build uses `--disable-gil`; supported platform distributions may expose a binary or ABI suffix such as `python3.14t`. `sysconfig.get_config_var("Py_GIL_DISABLED")` is the documented build-configuration probe. `sys._is_gil_enabled()` reports the live process state.

A free-threaded executable can still run with the GIL enabled through `-X gil=1` or `PYTHON_GIL=1`. Conversely, selecting a disabled state requires a free-threaded-capable build. Command-line selection takes precedence over the environment variable. Record the executable path, version, ABI flags, build configuration, live state, and imported native package set in diagnostics; recording only “Python 3.14” is insufficient.

#### Runtime safety is finer-grained, not synchronization-free

PEP 703 replaces reliance on one mandatory interpreter-wide lock with mechanisms including object locking, critical sections, and changed reference-counting strategies. The public consequence is simultaneous Python execution across threads, not a promise that arbitrary object graphs or sequences of operations are transactional.

Important 3.14 boundaries from the official HOWTO include:

- shared iterators generally are not safe for unsynchronized concurrent access;
- reading `frame.f_locals` while that frame executes in another thread is unsafe;
- some object lifetime and memory behavior differs because of immortalization and free-threaded reference-counting strategies;
- thread context inheritance and warning-filter behavior have different default flags on free-threaded builds;
- single-threaded execution and memory can carry overhead compared with the regular build.

Do not copy a benchmark percentage into a capacity plan. Measure the actual service workload on the exact executable, hardware, dependencies, thread count, data distribution, and observability configuration.

#### An extension can change the process mode

On a free-threaded build, importing a C extension that has not declared no-GIL support can emit a warning and enable the GIL. Therefore:

1. startup begins with a build/runtime combination;
2. dependency imports execute extension initialization;
3. an unqualified module may trigger GIL enablement;
4. the service still runs, but its scaling and scheduling assumptions may no longer hold;
5. a post-import live-state probe and startup policy detect the transition.

Forcing `PYTHON_GIL=0` is not proof that an undeclared extension is safe. It overrides the fallback and can expose data races or memory corruption. Qualification requires the extension maintainer's contract plus testing.

### 4.6 Isolated interpreters

An interpreter is an execution context containing runtime state such as `sys.modules`, builtins, imports, and `__main__`. In Python 3.14, `concurrent.interpreters` exposes public creation, execution, and cross-interpreter queue primitives. `create()` creates an idle interpreter; `exec()` and `call()` run in the calling thread, while `call_in_thread()` or a managed executor supplies another thread ([`concurrent.interpreters`](https://docs.python.org/3.14/library/concurrent.interpreters.html)).

Isolation means the same module imported in two interpreters produces distinct module objects and state. Most values crossing the boundary are copied, commonly through pickle; selected immutable values can be shared or copied efficiently, while `memoryview` and the cross-interpreter `Queue` provide carefully managed sharing. Design the boundary like a protocol:

- send immutable, bounded, versioned messages;
- avoid sending framework containers or closures with hidden state;
- initialize dependencies inside each interpreter;
- make errors serializable and observable;
- own interpreter shutdown after all submitted work has terminated;
- verify every native extension under the isolated-interpreter mode.

Interpreters in one process are not a security boundary. Native code can access process memory and can violate runtime isolation, and a fatal native fault can terminate the process. Use processes or stronger operating-system containment for hostile inputs, privilege boundaries, memory caps, or crash isolation.

[`interpreter_isolation.py`](examples/interpreter_isolation.py) creates two interpreters sequentially, binds separate names in their `__main__` modules, and copies snapshots back through a cross-interpreter queue. The observed interpreter IDs differ while the process ID is shared. Because execution is sequential, that example proves isolation only—not parallel speedup.

### 4.7 `InterpreterPoolExecutor`

Python 3.14 adds `concurrent.futures.InterpreterPoolExecutor`. It is a `ThreadPoolExecutor` subclass whose worker threads each own an interpreter and a separate GIL, so CPU-bound Python work can execute on multiple cores in a regular GIL-enabled build. The executor pickles the initializer, callable, arguments, and return value across interpreter boundaries, and attempts to preserve worker exceptions with `ExecutionFailed` context ([executor contract](https://docs.python.org/3.14/library/concurrent.futures.html#interpreterpoolexecutor)).

[`interpreter_pool.py`](examples/interpreter_pool.py) sends two immutable integer tuples and collects integer partial sums. It deliberately avoids a speed claim: the inputs are too small, worker startup and serialization matter, and the example's purpose is to expose the ownership and transfer boundary.

Use a pool when:

- the workload is CPU-bound Python and tasks are coarse enough to amortize transfer and interpreter overhead;
- inputs and results have a clean transferable representation;
- per-worker module state is acceptable or useful;
- every imported native extension supports isolated interpreters;
- same-process failure containment is sufficient.

Do not choose it merely because it is newer than a process pool. Process pools remain preferable when the worker must have a separate address space, resource limits, privilege boundary, independent termination, or compatibility with a process-oriented library.

### 4.8 Comparison matrix

| Model | Mutable Python sharing | CPU-bound Python parallelism | Transfer boundary | Fault boundary | Main migration risk |
|---|---|---|---|---|---|
| Regular-build threads, one interpreter | Direct and implicit | Usually no; native code may release the GIL | Function-call references | Same process and interpreter | Mistaking GIL serialization for an application invariant |
| Free-threaded threads, one interpreter | Direct and implicit | Yes, subject to workload and contention | Function-call references | Same process and interpreter | Races, native-extension safety, allocator/reference behavior, contention |
| Threads across isolated interpreters | No ordinary mutable-object sharing | Yes, through independent interpreter GILs | Copy/share protocol, queue, or serialization | Same process; separate runtime state | Extension isolation, transfer cost, duplicated module state, unfamiliar lifecycle |
| Processes | No ordinary address-space sharing | Yes | IPC, serialization, or explicit shared memory | Separate processes | Startup, IPC, duplicated memory, worker supervision |

For Python 3.11 interview platforms, `InterpreterPoolExecutor` and `concurrent.interpreters` are unavailable, and the free-threaded build does not exist. The practical choices remain GIL-enabled threads, processes, asynchronous I/O, and native work that deliberately releases the GIL.

### 4.9 Native-extension compatibility has two axes

Do not collapse these declarations:

| Extension question | Module slot or mechanism | Meaning |
|---|---|---|
| Can the module run in multiple interpreters? | `Py_mod_multiple_interpreters` | Declares unsupported, shared-GIL-compatible, or per-interpreter-GIL-compatible behavior |
| Can the module run with the GIL disabled? | `Py_mod_gil` with `Py_MOD_GIL_NOT_USED`, or the guarded single-phase unstable API | Declares that importing the extension need not enable the GIL in a free-threaded build |

For isolated interpreters, prefer multi-phase initialization and per-module state rather than mutable C `static` state. Any truly process-global state needs an explicit thread-safety and ownership design ([Isolating Extension Modules](https://docs.python.org/3.14/howto/isolating-extensions.html)).

For free-threaded builds, extensions must guard direct structure-field access, borrowed-reference patterns, container access macros, caches, and global state according to the free-threading C-API guidance. As of the audited Python 3.14 documentation, free-threaded extensions require distinct `t`-suffixed binaries and the free-threaded build does not support the Limited C API or Stable ABI ([C API Extension Support for Free Threading](https://docs.python.org/3.14/howto/free-threading-extensions.html)).

An ABI-compatible import is only the beginning. Test the module under concurrent calls, interpreter creation/destruction, repeated imports, cancellation/shutdown, exceptions, and the library's own native threads.

### 4.10 Migration sequence

| Step | Action | Evidence before advancing |
|---:|---|---|
| 1 | Inventory workloads and boundaries | CPU/I/O classification, state owners, native dependency list, current thread/process topology |
| 2 | Establish deterministic correctness tests | Forced interleavings for check-then-act, iteration, cache publication, shutdown, callbacks, and finalization assumptions |
| 3 | Build a runtime matrix | Python 3.11 regular, Python 3.14 regular, Python 3.14 free-threaded with GIL disabled and enabled, isolated-interpreter path where applicable |
| 4 | Qualify dependencies | Correct wheel/ABI, maintainer declaration, multi-interpreter state model, no-GIL contract, stress results |
| 5 | Choose one bounded candidate stage | Coarse task contract, finite workers, explicit ownership, representative data, idempotent retry or failure policy |
| 6 | Instrument the actual mode | Executable, ABI, build flag, post-import GIL state, worker topology, queue depth, task residence, throughput, latency, errors, memory |
| 7 | Canary with rollback | Compared correctness and service objectives, automatic rollback trigger, conventional path retained |
| 8 | Expand only with evidence | Workload-specific scaling, acceptable tail latency and memory, no correctness regressions, operational playbook |

Avoid a big-bang “remove all locks” migration. Many locks protect domain invariants, not the interpreter. Remove or narrow one only after the protected invariant, interleavings, and replacement protocol are explicit.

## 5. Additional visual models

### 5.1 Shared-memory versus isolated-state execution

```text
free-threaded threads                  isolated interpreters

       one object graph                 interpreter A        interpreter B
      ┌───────────────┐                 ┌───────────┐        ┌───────────┐
T1 ──▶│ cache / model │◀── T2       T1 ─▶│ modules A │   T2 ─▶│ modules B │
      └──────┬────────┘                 └─────┬─────┘        └─────┬─────┘
             │ locks/protocols                 └──── message/copy ──┘
             │
        contention possible               duplicated state possible
```

#### How to read this visual

The left side has two threads pointing at one mutable object graph, so correctness and performance depend on synchronization and contention. The right side has separate object graphs; interaction crosses an explicit message or copy edge.

#### Key insight

The central design choice is not only “can work run in parallel?” but also “where is mutation allowed to be shared?”

#### Simplification or limitation

This conceptual diagram omits cross-interpreter `Queue` and `memoryview`, native process-global state, shared operating-system resources, the interpreter-pool serialization implementation, and hybrid designs.

### 5.2 Extension qualification gate

```text
package imported by candidate worker
                 |
        pure Python only? ── yes ──> audit Python shared-state invariants
                 |
                 no
                 v
       correct regular / t ABI artifact?
                 |
                 v
   no-GIL declaration + concurrent-state audit
                 |
                 v
 multi-interpreter declaration + per-module-state audit
                 |
                 v
       exact-mode stress and shutdown tests
```

#### How to read this visual

Follow each gate downward. A package passes only the modes actually used: a free-threaded single-interpreter deployment needs no-GIL qualification, while an interpreter pool needs multi-interpreter qualification. A deployment using both needs both.

#### Key insight

“Works on Python 3.14” is not a compatibility statement precise enough for native dependencies.

#### Simplification or limitation

The gate omits compiler, platform, transitive native libraries, dynamic loading, sanitizer builds, GPU runtimes, packaging metadata, and library-specific support policies.

## 6. Worked examples

### 6.1 Runtime capability probe

Run:

```bash
python units/concurrency/PY-CON-090-free-threaded-cpython-subinterpreters-and-version-specific-gil-changes/examples/runtime_modes.py
```

Prediction before execution:

The available executable is expected to report regular CPython 3.14.4, no free-threaded build flag, an enabled GIL, and the Python 3.14 isolated-interpreter APIs. The build flag and GIL state should be printed as separate facts.

Observed result on the initially tested runtime:

```text
implementation: cpython
python: 3.14.4
ABI flags: (none)
free-threaded build: False
GIL enabled: True
isolated interpreters supported: True
concurrent.interpreters available: True
InterpreterPoolExecutor available: True
mode: regular CPython build with the GIL enabled
```

The output proves only what this executable reported at this point in startup. It does not exercise a free-threaded binary, qualify third-party extensions, or measure parallel speedup.

### 6.2 Controlled logical race

[`shared_state_race.py`](examples/shared_state_race.py) separates a read and write with a barrier so two threads deterministically read zero before either stores one.

```bash
python units/concurrency/PY-CON-090-free-threaded-cpython-subinterpreters-and-version-specific-gil-changes/examples/shared_state_race.py
```

Observed result:

```text
unsafe controlled result: 1/2
locked result: 2/2
```

The unsafe outcome is expected on this controlled schedule even though the tested runtime has a GIL. The locked case protects the read-modify-write invariant. This is a correctness experiment, not evidence about how often an uncontrolled service loses updates.

### 6.3 Interpreter isolation

[`interpreter_isolation.py`](examples/interpreter_isolation.py) creates two Python 3.14 interpreters and gives each a different `state` global:

```text
subinterpreter IDs distinct: True
subinterpreters share main PID: True
isolated states: (('alpha', 'first-only'), ('beta', 'second-only'))
```

The distinct IDs and states establish separate interpreter contexts; the equal process ID establishes the same-process boundary. The example runs `exec()` sequentially in the owner thread, so it intentionally does not claim concurrent execution.

### 6.4 Interpreter-pool transfer boundary

[`interpreter_pool.py`](examples/interpreter_pool.py) submits immutable batches through `InterpreterPoolExecutor` and obtains copied integer results:

```python
with InterpreterPoolExecutor(max_workers=2) as executor:
    partial_sums = tuple(executor.map(sum, batches))
```

The example uses an executor context manager so shutdown has an owner. Real code should additionally bound submission, propagate deadlines, choose batch size from measurements, make worker initialization explicit, and define retry semantics for indeterminate outcomes.

### 6.5 Debugging example

Keep the correction hidden until the learner records a failure scenario:

```python
cache: dict[str, bytes] = {}


def get_or_build(key: str) -> bytes:
    if key not in cache:
        cache[key] = build_and_publish(key)
    return cache[key]
```

Before editing:

1. identify every shared state transition and external side effect;
2. construct a deterministic two-thread interleaving without relying on random sleeps;
3. state what the GIL does and does not protect on regular CPython;
4. state which new interleavings a free-threaded build makes easier to realize;
5. decide whether the correct boundary is a lock, single-flight protocol, immutable publication, per-thread state, per-interpreter state, or process isolation;
6. test failure, cancellation, retry, and shutdown before asking for a review.

Do not “fix” the example by assuming `dict.setdefault()` makes `build_and_publish()` exactly once. The business side effect and publication policy span more than one container operation.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| Python 3.14 means no GIL | Free threading is a headline 3.14 feature | The free-threaded build is supported but optional and non-default | Log build configuration and live state from the deployed executable |
| `Py_GIL_DISABLED == 1` means the GIL is off | The build was compiled for free threading | It reports capability; runtime flags or an extension import may enable the GIL | Compare the config variable with `sys._is_gil_enabled()` after imports |
| A GIL makes a shared cache thread-safe | Container internals do not normally corrupt under ordinary operations | Multi-operation and side-effect invariants still race | Force both threads past the read before either writes |
| Removing the GIL means removing locks | Some locks were added to compensate for a global interpreter bottleneck | Domain locks may protect uniqueness, order, publication, transactions, or native state | Name the invariant for each lock and test its removal independently |
| Internal list/dict locks make compound logic atomic | Individual operations receive implementation protection | A sequence across operations or objects is not one transaction | Gate between operations and assert the invalid intermediate outcome |
| Two interpreter objects run in parallel automatically | They are distinct execution contexts | `create()` starts no thread; execution in the current thread is sequential unless another concurrency owner exists | Record thread IDs and overlap gates around `exec()` or use an executor |
| Subinterpreters are lightweight processes | They isolate Python runtime state and can use separate GILs | They share a process, native address space, file descriptors, signals, and fatal-fault boundary | Record PID and test only non-hostile synthetic state |
| Mutable module globals are shared across interpreters | Module names look identical | Each interpreter has its own module objects and `sys.modules` | Mutate the same named global separately and return snapshots |
| Every immutable object is copied | Copying is the usual mental model | Some immutable values may be shared or copied efficiently; selected managed types can share data | Use only documented transfer types and avoid identity assumptions |
| A package imports on regular CPython, so it supports interpreter pools | The same wheel and import name are used | C extension state may be process-global or fail the per-interpreter declaration | Run import/use/finalization tests in multiple interpreter workers |
| A `cp314t` wheel is no-GIL safe | The binary targets the correct ABI | ABI targeting does not prove internal synchronization correctness | Require maintainer support plus stress and sanitizer evidence where appropriate |
| Forcing `PYTHON_GIL=0` validates an extension | It prevents automatic fallback | It can suppress a safety fallback and expose unsynchronized native state | Never use the override as qualification evidence |
| Free threading guarantees a speedup | More Python threads can execute simultaneously | Contention, overhead, memory, task granularity, native code, and hardware decide scaling | Benchmark the exact workload with controlled inputs and raw observations |
| Immediate reference-count finalization remains a coordination mechanism | Regular CPython often deallocates promptly | Free-threaded reference strategies can defer reclamation, and timing is not a portable contract | Use explicit close/context ownership and record finalization separately |
| Interpreter isolation is a security sandbox | Python state is separated | Same-process native code can violate isolation | Use process/container boundaries for hostile code or privileges |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| Runtime capability probes | Constant-time configuration/state lookup | Perform at startup; do not poll as a synchronization strategy |
| Application mutex around one invariant | Constant-time API plus contention-dependent wait | Critical-section duration and waiter topology dominate latency |
| Free-threaded access to shared objects | Operation-dependent plus object/critical-section synchronization | Internal locking protects runtime safety, not multi-operation correctness |
| Create an isolated interpreter | Non-trivial startup and duplicated runtime/module state | Python 3.14 documentation notes startup and memory have not been fully optimized |
| Cross-interpreter argument/result transfer | Linear in serialized/copied payload size in the common pickle path | Selected immutable or managed values may use different transfer mechanisms |
| Interpreter-pool task | Submission plus serialization, scheduling, execution, and result transfer | Use coarse tasks; no initialized example benchmark claims a crossover point |
| Process-pool task | IPC/serialization plus process scheduling and execution | Address-space isolation may justify higher cost |
| More worker threads | Potential parallelism plus scheduling, cache, lock, and memory pressure | Throughput can plateau or regress; measure rather than equating workers with cores |
| Duplicated imports per interpreter | Roughly proportional to per-interpreter module state | Native/shared internals and immutable sharing make exact memory use workload-specific |

Separate latency, throughput, CPU utilization, memory, and correctness. A configuration that raises CPU utilization but duplicates work or violates an invariant is not a successful migration.

## 9. Production relevance and trade-offs

### 9.1 Start from the workload contract

For each candidate stage, record:

- CPU-bound Python time versus I/O wait and native time;
- task granularity and input/result size distribution;
- mutable state and the owner of every invariant;
- native packages, their transitive libraries, and their support statements;
- cancellation, timeout, retry, idempotency, and shutdown behavior;
- fault-containment and security requirements;
- Python 3.11 fallback requirements.

This often reveals that only one stage benefits from a new topology. A request handler may remain async or threaded for I/O while a bounded CPU transform uses interpreters or processes.

### 9.2 Prefer explicit state architecture

Free-threaded code benefits from immutable snapshots, single-writer ownership, sharded state, queues, and small critical sections. Subinterpreter code benefits from immutable messages, stable schemas, coarse tasks, per-worker initialization, and minimal result objects. These are not opposing styles: both reduce accidental sharing and make boundaries testable.

Be careful with caches. A per-interpreter cache avoids cross-interpreter locks but duplicates memory and can produce inconsistent freshness. A shared free-threaded cache centralizes data but needs a correct publication and eviction protocol. An external cache adds network and serialization cost but can create a service-wide ownership boundary.

### 9.3 Operational signals

Emit bounded startup and deployment metadata:

- exact executable and CPython version;
- ABI flags and `Py_GIL_DISABLED` build value;
- live GIL state after dependency imports;
- chosen executor/topology and worker count;
- qualified native package versions;
- fallback reason if the service disables a candidate mode.

Measure task queue depth, admission wait, active workers, task residence, completion rate, error type, serialization failures, worker initialization failures, CPU utilization, memory, and tail latency. Do not log every task's payload or private data.

### 9.4 Failure and shutdown ownership

Free-threaded workers share a process and object graph, so shutdown must stop admission, signal workers, allow or abort in-flight invariants, join every thread, and close shared resources once. Interpreter workers add per-interpreter initialization and finalization; no interpreter should be destroyed while its thread executes. Process workers add child termination and IPC cleanup.

Cancellation of a `Future` does not imply that a running thread, interpreter task, or native call stopped. Define the point of no return for side effects, preserve late outcomes, and make retries idempotent or explicitly non-retryable.

### 9.5 Rollout policy

A safe rollout keeps the regular mode available until the candidate proves:

1. deterministic correctness tests pass on every supported runtime mode;
2. native dependencies are explicitly qualified;
3. representative load meets throughput, latency, and memory objectives;
4. post-import live GIL state matches policy;
5. shutdown and rollback complete without lost or duplicated committed work;
6. operators can distinguish capacity saturation from mode incompatibility.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| Regular CPython GIL serializes Python execution inside one interpreter | CPython implementation detail | Historical CPython behavior | Same baseline behavior | Native code may release the GIL; application locks are still needed |
| Per-interpreter GIL through isolated interpreter configuration | CPython C API | 3.12 | Processes for CPU isolation/parallelism | `Py_NewInterpreterFromConfig()` exposes own-GIL configuration |
| Optional free-threaded CPython build | CPython build/runtime | 3.13 experimental; 3.14 supported | Processes or GIL-releasing native work | Still optional and not the default in 3.14 |
| `sysconfig.get_config_var("Py_GIL_DISABLED")` build probe | CPython build configuration | 3.13 | Treat Python 3.11 CPython as a regular build | Capability is distinct from live state |
| `sys._is_gil_enabled()` live probe | CPython implementation API | 3.13 | No equivalent needed for stock 3.11 CPython; represent probe absence explicitly | May not exist on other implementations |
| `-X gil` and `PYTHON_GIL` | CPython runtime configuration | 3.13 free-threaded build | Not applicable | Command-line option takes precedence; does not qualify unsafe extensions |
| `concurrent.interpreters` public API | Standard library / CPython capability | 3.14 | Use processes, or keep lower-level interpreter work out of portable 3.11 code | Not available on WASI; creation alone adds no concurrency |
| `InterpreterPoolExecutor` | Standard library | 3.14 | `ProcessPoolExecutor` for CPU-bound Python; `ThreadPoolExecutor` for I/O or GIL-releasing work | Pickles initializer, call, arguments, and result |
| `Py_mod_multiple_interpreters` | CPython C API / Stable ABI | 3.12 | Avoid extension use in subinterpreters | Support level distinguishes shared-GIL and own-GIL interpreters |
| `Py_mod_gil` | CPython C API / Stable ABI | 3.13 | Not applicable to stock 3.11 execution | Absence defaults to GIL used and may enable the GIL on a free-threaded build |
| Distinct `t`-suffixed extension binary | CPython ABI | 3.13 | Regular ABI wheel | Free-threaded and regular extension binaries are not interchangeable |
| Limited C API / Stable ABI for free-threaded extension binaries | CPython packaging boundary | Not supported in audited 3.14 docs | Continue stable-ABI wheels for regular builds, and build a separate free-threaded artifact | Re-audit on later CPython releases |
| Free-threaded default context inheritance and context-aware warnings flags | CPython runtime behavior | 3.14 | Pass explicit `Thread(context=...)` where available or copy/run context deliberately | Defaults differ between regular and free-threaded builds |

Canonical explanations target Python 3.14. Python 3.11 interview answers should state its conventional process-wide GIL model and should not import 3.14-only interpreter APIs.

## 11. Practice brief

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-CON-090-P01` | Predict | 3 | Correct build/runtime/topology classification | [Practice](practice/README.md#py-con-090-p01-classify-a-runtime-matrix) |
| `PY-CON-090-P02` | Debug | 4 | Deterministic shared-state race diagnosis | [Practice](practice/README.md#py-con-090-p02-debug-a-gil-protected-cache) |
| `PY-CON-090-P03` | Implement | 4 | Mode-aware startup guard with honest fallbacks | [Practice](practice/README.md#py-con-090-p03-build-a-runtime-startup-guard) |
| `PY-CON-090-P04` | Implement | 4 | Explicit isolated-interpreter message boundary | [Practice](practice/README.md#py-con-090-p04-build-an-isolated-worker-boundary) |
| `PY-CON-090-P05` | Review | 5 | Independent C-extension compatibility findings | [Practice](practice/README.md#py-con-090-p05-review-a-native-extension-plan) |
| `PY-CON-090-P06` | Design | 5 | Evidence-based concurrency-model choice | [Practice](practice/README.md#py-con-090-p06-choose-the-backend-execution-model) |
| `PY-CON-090-P07` | Experiment | 5 | Reproducible regular/free-threaded comparison | [Practice](practice/README.md#py-con-090-p07-run-the-cross-build-experiment) |
| `PY-CON-090-P08` | Design | 5 | Staged production migration and rollback | [Practice](practice/README.md#py-con-090-p08-design-a-free-threading-rollout) |

Do not add solutions before an attempt. Preserve predictions, commands, raw output, first mismatches, and corrected reasoning.

## 12. Interview prompts

Ask and answer these one at a time during review:

1. What three runtime facts must you distinguish before saying “this service has no GIL”?
2. Why does Python 3.14 not imply free-threaded execution?
3. Give a race that remains possible on a regular GIL-enabled CPython build.
4. What can enable the GIL after a free-threaded process starts?
5. Why is `Py_GIL_DISABLED` insufficient as a live-state check?
6. Compare per-object runtime locking with an application lock around a business invariant.
7. What changed for isolated interpreters in Python 3.12 and Python 3.14?
8. Why does creating two interpreters not itself create concurrency?
9. What does `InterpreterPoolExecutor` serialize, and how does that affect task granularity?
10. Compare free-threaded threads, interpreter workers, and process workers for mutable state and fault isolation.
11. Why are `Py_mod_gil` and `Py_mod_multiple_interpreters` separate declarations?
12. What evidence would you require before enabling free-threaded execution in a backend service?
13. How would you preserve a Python 3.11 fallback without weakening the Python 3.14 design?
14. Which metrics distinguish successful parallel scaling from duplicated work and contention?

A strong answer should eventually demonstrate:

- accurate CPython version, build, runtime, and topology boundaries;
- explicit invariant ownership rather than reliance on incidental GIL behavior;
- separate pure-Python, C-extension, packaging, isolation, and operational compatibility reasoning;
- a measured migration with deterministic tests, observability, shutdown ownership, and rollback.

## 13. Closed-book revision cues

Without reading the note:

1. Draw the three-axis execution-choices visual.
2. Reconstruct the Python 3.11, 3.12, 3.13, and 3.14 timeline.
3. Write the two probes for build capability and current GIL state.
4. Explain how a free-threaded build can still have its GIL enabled.
5. Force a two-thread lost update on a GIL-enabled runtime without random sleeps.
6. Explain why built-in container protection does not make check-then-act atomic.
7. Draw shared-memory threads beside isolated interpreters.
8. State what interpreter creation, `exec()`, and `call_in_thread()` each own.
9. List the interpreter-pool transfer and failure boundaries.
10. Name both native-extension declarations and what each proves.
11. Give one reason to retain processes after free threading and subinterpreters exist.
12. Design a canary and rollback checklist for one CPU-bound backend stage.

## 14. Authoritative sources

Only official Python sources opened and used during the 2026-08-29 audit are listed.

1. [Python support for free threading](https://docs.python.org/3.14/howto/free-threading-python.html), build/runtime detection, automatic GIL enablement, thread-safety guidance, limitations, and behavioral changes; Python 3.14.7 documentation, accessed 2026-08-29.
2. [PEP 703 — Making the Global Interpreter Lock Optional in CPython](https://peps.python.org/pep-0703/), optional-GIL design, container protection, build mode, and extension opt-in; Python 3.13, accessed 2026-08-29.
3. [PEP 779 — Criteria for supported status for free-threaded Python](https://peps.python.org/pep-0779/), phase-II supported-but-optional status; Python 3.14, accessed 2026-08-29.
4. [`sys._is_gil_enabled()`](https://docs.python.org/3.14/library/sys.html#sys._is_gil_enabled), live GIL-state probe and CPython implementation boundary; Python 3.14.7 documentation, accessed 2026-08-29.
5. [PEP 684 — A Per-Interpreter GIL](https://peps.python.org/pep-0684/), interpreter isolation, own-GIL configuration, and extension implications; Python 3.12, accessed 2026-08-29.
6. [`concurrent.interpreters`](https://docs.python.org/3.14/library/concurrent.interpreters.html), isolation, execution, communication, transfer, and availability; Python 3.14.7 documentation, accessed 2026-08-29.
7. [`InterpreterPoolExecutor`](https://docs.python.org/3.14/library/concurrent.futures.html#interpreterpoolexecutor), worker topology, pickle boundaries, exception behavior, and multi-core execution; Python 3.14.7 documentation, accessed 2026-08-29.
8. [Multiple interpreters in a Python process](https://docs.python.org/3.14/c-api/subinterpreters.html), `Py_NewInterpreterFromConfig()`, isolation, and own-GIL C API; Python 3.14.7 documentation, accessed 2026-08-29.
9. [Module object slots](https://docs.python.org/3.14/c-api/module.html#c.Py_mod_multiple_interpreters), `Py_mod_multiple_interpreters` and `Py_mod_gil`; Python 3.14.7 C API documentation, accessed 2026-08-29.
10. [C API Extension Support for Free Threading](https://docs.python.org/3.14/howto/free-threading-extensions.html), extension opt-in, locking, ABI artifacts, and Limited API/Stable ABI boundary; Python 3.14.7 documentation, accessed 2026-08-29.
11. [Isolating Extension Modules](https://docs.python.org/3.14/howto/isolating-extensions.html), per-module state and process-global state risks; Python 3.14.7 documentation, accessed 2026-08-29.
12. [Python 3.11 `threading`](https://docs.python.org/3.11/library/threading.html), interview-compatibility GIL and CPU/I/O guidance; Python 3.11.15 documentation, accessed 2026-08-29.

## 15. Durable clarification log

| Date | Clarification | Why it belongs in canonical notes | Source or evidence |
|---|---|---|---|
| 2026-08-29 | Free-threaded build capability, current GIL state, and interpreter topology are independent facts. | Prevents version-only and build-flag-only production decisions. | [Free-threading detection](https://docs.python.org/3.14/howto/free-threading-python.html#identifying-free-threaded-python) plus [`runtime_modes.py`](examples/runtime_modes.py) |
| 2026-08-29 | Python 3.14 makes free-threaded CPython officially supported but still optional and non-default. | Corrects the likely interpretation that a 3.14 upgrade removes the GIL automatically. | [PEP 779](https://peps.python.org/pep-0779/) |
| 2026-08-29 | Free threading and isolated interpreters solve the global bottleneck with different state-sharing models. | Keeps shared-memory races separate from message/copy and duplicated-state trade-offs. | [Free-threading HOWTO](https://docs.python.org/3.14/howto/free-threading-python.html) and [`concurrent.interpreters`](https://docs.python.org/3.14/library/concurrent.interpreters.html) |
| 2026-08-29 | A C extension's no-GIL declaration and multi-interpreter declaration are separate compatibility axes. | Prevents one successful import or ABI artifact from being treated as universal concurrency safety. | [Module object slots](https://docs.python.org/3.14/c-api/module.html#module-slots) |
| 2026-08-29 | A GIL-enabled runtime can deterministically lose a logical read-modify-write update. | Replaces vague “GIL makes operations safe” reasoning with an explicit invariant and trace. | [`shared_state_race.py`](examples/shared_state_race.py) |
