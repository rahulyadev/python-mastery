# PY-CON-090 practice — Free-threaded CPython, subinterpreters, and version-specific GIL changes

[Unit note](../README.md) · [Curriculum](../../../../CURRICULUM.md#py-con-090) · [Progress](../../../../PROGRESS.md)

## Practice contract

These exercises begin unsolved. Preserve the first prediction, design, code, trace, and mistake before requesting a hint or review. A later polished answer must not replace the evidence of how the reasoning changed.

For each exercise:

1. record the exact Python executable, implementation, version, ABI flags, build capability, and live GIL state;
2. name the interpreter, thread, process, state, dependency, and shutdown owners;
3. distinguish documented contract from CPython observation and workload measurement;
4. use barriers, events, or injected outcomes instead of random sleeps for correctness tests;
5. use synthetic data and avoid network, secrets, employer code, or hostile extensions;
6. preserve raw output and explain the first mismatch with the prediction;
7. make no speedup, memory, or safety claim that the evidence did not test.

Ask for hints one at a time. A hint should reveal only the next missing reasoning step.

## Prerequisite assumptions

The tracker records no learning evidence for the four hard prerequisites. Use these minimum bridges without treating them as completion:

- `PY-CON-010`: concurrency is overlapping progress, parallelism is simultaneous execution, and a regular CPython GIL is an interpreter mechanism rather than an application transaction;
- `PY-CON-020`: threads share a process and require explicit lifetime, failure, context, and shared-state ownership;
- `PY-CON-040`: processes isolate address spaces and require explicit serialization, IPC, startup, shutdown, and failure design;
- `PY-MPR-010`: references keep objects alive, CPython often uses reference counting, and finalization timing must not be used as a cross-thread protocol.

## Evidence map

| Exercise | Type | Primary evidence | Required before review |
|---|---|---|---|
| `PY-CON-090-P01` | Predict | Runtime-mode classification | Matrix with proof, unknowns, and safe conclusion for each case |
| `PY-CON-090-P02` | Debug | Shared-cache race | Deterministic failing trace and exact violated invariant |
| `PY-CON-090-P03` | Implement | Startup capability policy | Tests for regular, free-threaded-off, free-threaded-on, unsupported, and post-import change cases |
| `PY-CON-090-P04` | Implement | Isolated worker protocol | Transfer schema, state-isolation tests, failure propagation, and shutdown proof |
| `PY-CON-090-P05` | Review | Native-extension compatibility | Prioritized findings separated by ABI, no-GIL, interpreter, and native-state axes |
| `PY-CON-090-P06` | Design | Backend execution model | Workload/state/fault matrix and justified choice with Python 3.11 fallback |
| `PY-CON-090-P07` | Experiment | Cross-build observation | Reproducible environment, commands, raw output, interpretation, and limitations |
| `PY-CON-090-P08` | Design | Production migration | Staged gates, telemetry, canary, rollback, and stop conditions |

## PY-CON-090-P01 — Classify a runtime matrix

Difficulty: 3/5

For each deployment, fill in these columns before running or researching anything further:

| Case | Build supports disabled GIL? | GIL enabled now? | Interpreter topology | CPU-bound Python parallelism possible? | Shared mutable Python state? | What remains unknown? |
|---|---|---|---|---|---|---|
| A. CPython 3.11, two ordinary threads |  |  |  |  |  |  |
| B. CPython 3.14 regular build, two ordinary threads |  |  |  |  |  |  |
| C. CPython 3.14 free-threaded build launched with `-X gil=1` |  |  |  |  |  |  |
| D. CPython 3.14 free-threaded build launched with `-X gil=0` |  |  |  |  |  |  |
| E. CPython 3.14 regular build, two interpreter-pool workers |  |  |  |  |  |  |
| F. CPython 3.14 free-threaded process after importing an undeclared C extension |  |  |  |  |  |  |
| G. Two CPython worker processes |  |  |  |  |  |  |

For each row:

1. identify whether the statement is a version fact, build fact, runtime-state fact, topology fact, or dependency fact;
2. give the smallest probe or configuration evidence needed;
3. state one conclusion that would still be unsafe;
4. state whether an application lock remains necessary for a shared check-then-write invariant;
5. give the Python 3.11 interview answer without importing a 3.14-only API.

Preserve:

```text
Initial matrix:
Uncertain cells:
Evidence consulted:
Corrected matrix:
First reasoning error:
```

## PY-CON-090-P02 — Debug a GIL-protected cache

Difficulty: 4/5

```python
cache: dict[str, bytes] = {}
published: list[str] = []


def build_and_publish(key: str) -> bytes:
    payload = key.encode()
    published.append(key)
    return payload


def get_or_build(key: str) -> bytes:
    if key not in cache:
        cache[key] = build_and_publish(key)
    return cache[key]
```

The owner claims this is safe because dictionary methods do not corrupt the dictionary and the deployment currently uses a GIL-enabled build.

Before editing:

1. write the business invariant involving both `cache` and `published`;
2. enumerate an interleaving in which two threads publish the same key;
3. build a deterministic test using gates after the membership check and before publication;
4. run it on the regular runtime and record whether the GIL prevents the logical failure;
5. predict what changes on a free-threaded runtime and what does not;
6. compare at least three candidate state architectures without implementing them all;
7. identify failure, cancellation, and retry paths that affect exactly-once or at-least-once claims.

Do not accept a repair merely because the final dictionary has one entry. The duplicate side effect is part of the invariant.

Required evidence:

```text
Invariant:
Predicted interleaving:
Deterministic controls:
Observed trace:
First incorrect assumption:
Candidate designs and trade-offs:
Selected design:
Tests still missing:
```

## PY-CON-090-P03 — Build a runtime startup guard

Difficulty: 4/5

Implement a pure decision layer around an injected capability snapshot. Do not let unit tests depend on the host interpreter's actual mode.

Suggested input shape:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeSnapshot:
    implementation: str
    version: tuple[int, int]
    free_threaded_build: bool
    gil_enabled: bool | None
    isolated_interpreters: bool
    interpreter_pool: bool
```

Your API must decide among:

- accept the configured execution mode;
- fall back to a named conventional mode;
- refuse startup with a precise diagnostic.

Requirements:

1. keep build support and live GIL state separate;
2. represent an unavailable probe as unknown, not `False`;
3. allow a regular Python 3.11 mode without pretending it supports free threading;
4. require the Python 3.14 interpreter APIs before choosing an interpreter pool;
5. support a policy that requires the GIL to remain disabled after all native imports;
6. never automatically force `PYTHON_GIL=0` to override an unqualified extension;
7. produce bounded, non-sensitive startup metadata;
8. make the decision function deterministic and separately test actual probe collection.

Tests must cover at least:

- CPython 3.11 regular mode;
- CPython 3.14 regular mode;
- free-threaded build with GIL disabled;
- free-threaded build with GIL enabled intentionally;
- free-threaded build whose state changed after dependency import;
- non-CPython or missing-probe input;
- requested interpreter pool without the API;
- explicit safe fallback and explicit refusal.

Do not put environment mutation inside the decision function.

## PY-CON-090-P04 — Build an isolated worker boundary

Difficulty: 4/5

Using Python 3.14 `concurrent.interpreters` or `InterpreterPoolExecutor`, build a synthetic worker that accepts immutable records and returns immutable summaries.

Protocol constraints:

- each input has a version, request ID, operation, and bounded payload;
- worker module state is initialized independently;
- no mutable application object is assumed to be shared;
- errors return or raise a bounded, documented representation;
- submission and result queues are finite or controlled by finite executor capacity;
- shutdown stops admission, waits for owned work, and finalizes every interpreter only after execution ends;
- repeated execution makes retry/idempotency behavior visible;
- Python 3.11 follows a documented process-pool or synchronous fallback.

Required deterministic tests:

1. two interpreters mutate the same global name without sharing its value;
2. all worker observations share the main process ID but use distinct interpreter IDs;
3. an unsupported transfer object fails at the boundary without hanging shutdown;
4. a worker exception retains enough type/message context for diagnosis;
5. initializer failure rejects or fails pending work predictably;
6. no task executes after the owner closes the boundary;
7. empty input creates no unnecessary worker;
8. output order is explicitly defined rather than inferred from completion timing.

Do not benchmark until correctness, worker reuse, warm-up, payload distribution, and raw observations are controlled.

## PY-CON-090-P05 — Review a native-extension plan

Difficulty: 5/5

Review this proposal:

```text
We publish one cp314 abi3 wheel.
The module uses single-phase initialization and C static caches.
It imports successfully in regular CPython.
We will use it from InterpreterPoolExecutor and from free-threaded threads.
If Python emits a GIL warning, production will set PYTHON_GIL=0.
The cache does not need a lock because Python calls us while holding the GIL.
```

Produce prioritized findings. For every finding, include:

1. exact unsafe or unsupported assumption;
2. affected mode: ABI/build, free-threaded execution, isolated interpreters, both, or general lifecycle;
3. concrete failure scenario;
4. authoritative contract or missing evidence;
5. smallest safe next step;
6. test or review evidence needed to close the finding.

Your review must distinguish:

- regular versus `t`-suffixed extension binaries;
- Limited API/Stable ABI claims from ordinary C API use;
- `Py_mod_gil` from `Py_mod_multiple_interpreters`;
- multi-phase per-module state from process-global C `static` state;
- a correct ABI tag from correct synchronization;
- forcing a runtime flag from proving extension safety;
- Python-owned locks from a transitive native library's internal state.

Do not write replacement C code before the findings and test matrix are complete.

## PY-CON-090-P06 — Choose the backend execution model

Difficulty: 5/5

You own a service with four stages:

1. receive an async request and read a bounded body;
2. parse a small JSON envelope;
3. run a CPU-heavy pure-Python rules engine with a read-mostly model and a small mutable statistics cache;
4. write a result through a native database driver whose free-threading and multi-interpreter support are unknown.

Compare these candidate designs:

- ordinary threads on a regular build;
- free-threaded threads;
- interpreter-pool workers;
- process-pool workers;
- a hybrid boundary.

Your decision record must include:

| Dimension | Evidence or decision |
|---|---|
| Workload classification |  |
| Shared mutable state |  |
| Model distribution/update |  |
| Native dependency boundary |  |
| Input/result transfer cost |  |
| Fault and security boundary |  |
| Admission/backpressure |  |
| Deadline and cancellation |  |
| Retry/idempotency |  |
| Startup and warm-up |  |
| Shutdown ownership |  |
| Python 3.11 fallback |  |
| Metrics and success criteria |  |
| Rollback |  |

Do not select a design solely because it can use multiple cores. State what evidence could reverse your choice.

## PY-CON-090-P07 — Run the cross-build experiment

Difficulty: 5/5

Extend the initialized [runtime-mode experiment](../experiments/EXP-01-runtime-mode-and-isolation-probe/README.md) only when both a regular and a free-threaded CPython 3.14 executable are available.

Before execution, record:

- absolute executable path and `python -VV` output;
- `sys.version`, `sys.implementation`, ABI flags, and `Py_GIL_DISABLED`;
- live GIL state before and after importing the candidate dependency set;
- operating system, architecture, logical CPU availability, container/cgroup limits, and build provenance;
- exact command, environment flags, dependencies, and source commit;
- whether the run is a correctness experiment or benchmark.

Run the same deterministic cases on:

1. regular CPython 3.14;
2. free-threaded CPython 3.14 with its GIL disabled;
3. the same free-threaded executable with `-X gil=1`;
4. the disabled-GIL mode after importing every candidate native dependency;
5. Python 3.11 for compatibility where the code path applies.

Minimum observations:

- capability report;
- controlled lost-update trace;
- locked invariant trace;
- interpreter-isolation trace on 3.14;
- interpreter-pool correctness;
- warnings and post-import GIL state;
- memory and time only if a separately designed benchmark controls them.

Do not merge outputs from different executables into one unlabeled block. Do not infer free-threaded behavior from the initialized regular-runtime observation.

## PY-CON-090-P08 — Design a free-threading rollout

Difficulty: 5/5

Design a staged rollout for one CPU-heavy service component. Your plan must contain:

### Inventory

- exact Python executables and deployment images;
- transitive native dependency and wheel matrix;
- shared state, locks, caches, iterators, frames, callbacks, and finalizers;
- thread, interpreter, process, executor, and resource owners;
- workload/task size distribution and service objectives.

### Gates

1. deterministic invariant tests;
2. dependency support and ABI evidence;
3. regular/free-threaded/interpreter/process comparison as applicable;
4. representative load with raw observations;
5. shutdown, cancellation, late outcome, and rollback drills;
6. capacity and fault-injection tests;
7. code review by owners of native and application state.

### Canary

- percentage or cohort selection;
- exact mode assertion after imports;
- worker and admission bounds;
- correctness shadow or reconciliation signal;
- throughput, latency, memory, CPU, queue, error, and retry metrics;
- automatic and manual rollback thresholds;
- duration and evidence needed to expand.

### Rollback

- conventional executable or topology retained;
- no irreversible shared-state migration tied to the candidate mode;
- safe drain and restart sequence;
- treatment of in-flight, duplicated, or indeterminate work;
- post-rollback reconciliation and incident evidence.

End with three lists:

```text
Claims proven:
Claims still unproven:
Conditions that stop rollout:
```

## Review rubric

| Dimension | Needs work | Acceptable | Strong |
|---|---|---|---|
| Runtime model | Uses version or “GIL/no-GIL” as one fact | Separates build and live state | Also separates topology, imports, fallback, and evidence timing |
| Correctness | Relies on stress or assumed atomicity | Forces the critical interleaving | Names the full business invariant and failure/retry paths |
| Isolation | Treats interpreters as processes | Identifies separate runtime state and same process | Designs bounded transfer, native-state audit, lifecycle, and fault boundaries |
| Extensions | Treats import or wheel tag as support | Checks ABI and one declaration | Separates both declarations, state ownership, transitive native code, and exact-mode tests |
| Compatibility | Ignores Python 3.11 | Provides a practical fallback | Keeps canonical 3.14 design clear while testing both paths |
| Performance | Claims speedup from worker count | Records workload-specific measurements | Controls inputs, warm-up, raw data, uncertainty, contention, memory, and correctness |
| Operations | Says “canary and monitor” | Names signals and rollback | Asserts live mode after imports, bounded capacity, reconciliation, shutdown, and stop gates |
| Explanation | Repeats feature names | Explains mechanisms and trade-offs | Classifies contracts, observations, unknowns, and decisions precisely |

The topic is not complete merely because initialized tests pass. Completion requires the evidence profile in the unit note and an evidence-based tracker update.
