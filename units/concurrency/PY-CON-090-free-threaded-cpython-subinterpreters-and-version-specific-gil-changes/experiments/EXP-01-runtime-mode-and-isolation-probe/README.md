# EXP-01 — Runtime mode and interpreter isolation probe

| Field | Value |
|---|---|
| Owning unit | [`PY-CON-090`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-con-090) |
| Topic branch | `topic/PY-CON-090` |
| Precise question | On the available CPython 3.14 runtime, which GIL and isolated-interpreter capabilities are active, can a controlled logical update still race, and do two subinterpreters keep distinct Python state inside one process? |
| Classification | CPython build/runtime observation plus Python 3.14 standard-library contract |
| Status | Interpreted |
| Risk | Local standard-library concurrency; two short-lived threads and short-lived subinterpreters; no network, persistent files, external processes, third-party packages, or benchmark load |

## 1. Why an experiment is necessary

Four claims are easy to blur in prose:

1. a version may support a free-threaded build without the current executable being such a build;
2. a free-threaded-capable build may have a different live GIL state;
3. a present GIL does not make a multi-step application invariant atomic;
4. multiple interpreter contexts may isolate Python state while remaining inside one process.

The probe records each boundary separately. It also exercises `InterpreterPoolExecutor` for correctness without using the tiny workload as performance evidence.

## 2. Hypothesis

Before execution:

> The available `python` executable will report CPython 3.14.4, a regular rather than free-threaded build, and an enabled GIL. Because it is Python 3.14, it will report isolated-interpreter support, `concurrent.interpreters`, and `InterpreterPoolExecutor`.

For the controlled race:

> If two threads are forced to read the counter before either writes, both will store `1`, producing `1/2` even with the GIL enabled. Locking the complete read-modify-write will produce `2/2`.

For interpreter isolation:

> Two created interpreters will have distinct interpreter IDs and independent `state` globals, while both report the main process ID. Sequential `exec()` calls will prove isolation but not concurrency.

For the executor boundary:

> Two immutable input batches will cross the interpreter-pool boundary and return partial sums `(6, 9)` and total `15`. No timing or scaling conclusion will be drawn.

Alternative outcomes to classify:

- the executable reports a free-threaded build or disabled GIL;
- one of the Python 3.14 interpreter APIs is unavailable;
- the forced unsafe update reaches `2`, suggesting the control did not place both reads before a write;
- interpreter IDs or namespaces are not distinct;
- a subinterpreter uses a different process ID;
- task serialization, worker initialization, or result transfer fails.

## 3. Environment

Recorded values:

```text
Date: 2026-08-29
Operating system: Linux 7.0.0-30-generic
Architecture: x86_64
Python version: 3.14.4
sys.version: 3.14.4 (main, Jun 18 2026, 14:25:02) [GCC 15.2.0]
sys.implementation: cpython
Build type: regular GIL-enabled CPython
Free-threaded build: False (Py_GIL_DISABLED=0)
GIL enabled: True
ABI flags: empty
Isolated interpreters supported: True
Dependencies: Python standard library only
CPU: 28 logical CPUs reported; not used for a benchmark claim
Relevant flags and environment variables: no -X gil or PYTHON_GIL override supplied
```

The repository's canonical documentation baseline is Python 3.14.7. Execution occurred on the available CPython 3.14.4 runtime, so every observation is labelled accordingly. No free-threaded executable was available or run.

## 4. Controls and variables

### Controlled

- The capability probe reads public runtime/configuration attributes without changing them.
- The unsafe case creates exactly two threads and a fresh counter.
- A two-party `threading.Barrier` forces both unsafe reads before either write.
- The locked case performs the same number of logical increments under one `threading.Lock`.
- Thread join and barrier timeouts are deadlock guards, not scheduling controls or measurements.
- The interpreter case creates exactly two interpreters and one cross-interpreter queue.
- Each interpreter receives a distinct immutable label and private value.
- Both interpreter executions occur sequentially in the owner thread.
- The pool case uses two immutable batches and the built-in `sum` callable.
- Every thread, interpreter, and executor has an explicit termination owner.
- No random sleeps, network calls, filesystem mutation, third-party extension, or benchmark timer is used.

### Changed

- Shared counter update: forced read/write split versus lock-protected read-modify-write.
- Interpreter state: `("alpha", "first-only")` versus `("beta", "second-only")`.
- Execution boundary: direct interpreter `exec()` versus managed interpreter-pool task submission.

### Measured

- Implementation, version, ABI flags, free-threaded build flag, and live GIL state.
- Isolated-interpreter and executor API availability.
- Final counter values.
- Equality or difference of interpreter IDs and process IDs.
- State snapshots copied from each interpreter.
- Interpreter-pool partial sums and total.

## 5. Files

```text
experiments/EXP-01-runtime-mode-and-isolation-probe/
├── README.md
└── runtime_mode_probe.py
```

The probe composes four independently runnable initialized examples:

```text
examples/
├── interpreter_isolation.py
├── interpreter_pool.py
├── runtime_modes.py
└── shared_state_race.py
```

## 6. Reproduction command

Run from the repository root:

```bash
python units/concurrency/PY-CON-090-free-threaded-cpython-subinterpreters-and-version-specific-gil-changes/experiments/EXP-01-runtime-mode-and-isolation-probe/runtime_mode_probe.py
```

The focused regression command is:

```bash
python -m unittest discover -s units/concurrency/PY-CON-090-free-threaded-cpython-subinterpreters-and-version-specific-gil-changes/tests -v
```

To reproduce on another executable, replace only the leading `python` command and record the absolute executable, complete environment, and output separately. Do not overwrite this observation with a different build's output.

## 7. Prediction

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
unsafe controlled result: 1/2
locked result: 2/2
subinterpreter IDs distinct: True
subinterpreters share main PID: True
isolated states: (('alpha', 'first-only'), ('beta', 'second-only'))
interpreter pool partials: (6, 9)
interpreter pool total: 15
```

The crucial predictions are that the build and live-state lines remain distinct, the GIL-enabled runtime still loses the forced logical update, and state isolation coexists with one process ID.

## 8. Observed output

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
unsafe controlled result: 1/2
locked result: 2/2
subinterpreter IDs distinct: True
subinterpreters share main PID: True
isolated states: (('alpha', 'first-only'), ('beta', 'second-only'))
interpreter pool partials: (6, 9)
interpreter pool total: 15
```

No output was edited to match the hypothesis. Interpreter IDs and the numeric process ID are deliberately normalized to stable boolean relationships rather than reported as portable values.

Focused tests observed:

```text
Ran 8 tests in 0.135s

OK
```

That duration is test-run metadata, not a benchmark.

## 9. Interpretation

1. `Py_GIL_DISABLED=0` established that the tested executable is a regular build, while `sys._is_gil_enabled()` independently reported that the GIL was active.
2. Python 3.14's isolated-interpreter capability, public module, and interpreter-pool executor were present even though the executable was not free-threaded. This directly separates the two routes to multi-core execution.
3. The barrier forced both unsafe threads to read zero before either wrote. The final value `1` showed a lost logical update on a GIL-enabled runtime; therefore the GIL did not make the whole read-modify-write invariant atomic.
4. The lock-protected result `2` showed that synchronizing the entire invariant preserved both updates in this controlled case.
5. The two interpreter IDs were distinct and the returned states contained only each interpreter's assigned values, supporting namespace isolation.
6. Both interpreter observations matched the main PID, supporting the same-process boundary and rejecting a “subinterpreters are child processes” model.
7. `InterpreterPoolExecutor` transferred the tiny immutable inputs and results correctly. The result proves API/boundary correctness for this case, not parallel overlap, scalability, lower overhead, or production fitness.
8. No result says how the same code behaves on a free-threaded executable; that remains a separate run.

## 10. Visual interpretation

```text
tested executable
      |
      +-- build probe ------> regular build
      +-- live probe -------> GIL enabled
      |
      +-- two shared threads
      |      +-- forced read/read/write/write --> 1/2
      |      `-- locked read-modify-write ------> 2/2
      |
      `-- two interpreters in one PID
             +-- interpreter A --> ('alpha', 'first-only')
             `-- interpreter B --> ('beta', 'second-only')
```

### How to read this visual

Start at the executable and follow each independent observation branch. The first two branches classify the runtime. The shared-thread branch tests one application invariant. The interpreter branch tests isolation and process identity.

### Key insight

One experiment can observe several properties, but the properties do not collapse: GIL state, logical race safety, interpreter isolation, and process isolation answer different questions.

### Simplification or limitation

The diagram omits worker scheduling, actual interpreter IDs, serialization internals, native extensions, a free-threaded build, parallel timing, memory behavior, repeated interpreter lifecycle, and failure injection.

## 11. Contract and observation conclusions

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| The tested executable was not a free-threaded build and had its GIL enabled. | CPython configuration/runtime observation | CPython 3.14.4 | Re-run for every executable and after the dependency-import boundary relevant to policy. |
| The public isolated-interpreter module and pool executor were available. | Standard-library capability observation | Python/CPython 3.14.4 | They are Python 3.14 additions and are unavailable on the Python 3.11 compatibility baseline. |
| The forced two-thread read-modify-write lost one update while the GIL was enabled. | Controlled Python/CPython observation | CPython 3.14.4 regular build | It proves the logical invariant needs synchronization; it does not estimate uncontrolled race probability. |
| Locking the complete update retained both increments. | Standard-library synchronization observation | Python/CPython 3.14.4 | The example covers one counter only, not fairness or scalability. |
| Two interpreters retained distinct `__main__` state within one PID. | Python 3.14 standard-library contract plus observation | CPython 3.14.4 | Same-process isolation is not a security or fatal-fault boundary. |
| The interpreter pool returned `(6, 9)` and total `15`. | Python 3.14 standard-library observation | CPython 3.14.4 | No concurrency overlap or performance crossover was measured. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular GIL-enabled executable was run.
- Python 3.14.7 documentation was source-audited, but Python 3.14.7 was not the executed runtime.
- No free-threaded executable, `cp314t` dependency, `-X gil` variant, or `PYTHON_GIL` variant was run.
- No third-party or native extension was imported, so automatic GIL enablement and extension safety were not observed.
- The race is intentionally forced. It demonstrates possibility and invariant failure, not natural frequency or throughput impact.
- The interpreter executions used `exec()` sequentially; the experiment does not time or prove their parallel overlap.
- The pool workload is trivial and unsuitable for performance, startup, memory, or scalability conclusions.
- Only two interpreters and two short-lived threads were created once per case.
- No transfer failure, initializer failure, worker exception, cancellation, queue saturation, repeated teardown, process-global native state, signal, or finalization race was exercised.
- The test did not inspect object-level locking, reference-count internals, allocator behavior, immortalization, frame access, or shared iterators.
- Reported CPU count is environment context only and may not equal available CPU quota.

## 13. Follow-up

- Run the same probe with a separately installed CPython 3.14 free-threaded executable and preserve its output as a new labelled observation.
- Repeat that run with `-X gil=1` and with the GIL disabled to separate executable identity from live state.
- Import the exact production native dependency set, capture warnings, and re-check live GIL state after imports.
- Add deterministic transfer-failure, initializer-failure, worker-exception, and shutdown cases for `InterpreterPoolExecutor`.
- Design a real workload benchmark only after fixing task granularity, data distribution, worker warm-up, trial count, CPU quota, and correctness checks.
- Continue the runtime/C-API mechanisms in `PY-CPY-110` after its other prerequisites are ready.

## 14. Authoritative sources

1. [Python support for free threading](https://docs.python.org/3.14/howto/free-threading-python.html), build and live-state probes, runtime selection, extension fallback, and limitations; Python 3.14.7 documentation, accessed 2026-08-29.
2. [`concurrent.interpreters`](https://docs.python.org/3.14/library/concurrent.interpreters.html), interpreter isolation, execution, IDs, cross-interpreter queues, and same-process model; Python 3.14.7 documentation, accessed 2026-08-29.
3. [`InterpreterPoolExecutor`](https://docs.python.org/3.14/library/concurrent.futures.html#interpreterpoolexecutor), worker-interpreter topology and serialization contract; Python 3.14.7 documentation, accessed 2026-08-29.
4. [`threading.Lock` and `threading.Barrier`](https://docs.python.org/3.14/library/threading.html), synchronization contracts used by the controlled race; Python 3.14.7 documentation, accessed 2026-08-29.
