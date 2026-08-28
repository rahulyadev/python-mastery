# EXP-01 — Start methods and module-state inheritance

| Field | Value |
|---|---|
| Owning unit | [`PY-CON-040`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-con-040) |
| Topic branch | `topic/PY-CON-040` |
| Precise question | After the parent mutates a module global, what value does a child observe under `forkserver`, `fork`, and `spawn` on this platform? |
| Classification | Standard-library contract plus platform-specific CPython observation |
| Status | Interpreted |
| Risk | Process; controlled and local |

## 1. Why an experiment is necessary

The start-method descriptions say how a process is created, but programmers often turn those descriptions into an unsafe shortcut: “the child has my current globals.” A direct observation makes the hidden initialization boundary visible. The parent changes one global after import, each child reports that global, and all results include the process IDs and exit status.

This is not a recommendation to communicate through globals. It is a contrast that explains why importable targets, explicit arguments, and IPC are the portable design.

## 2. Hypothesis

Before execution:

> The `fork` child will inherit the parent's mutated in-memory module state. The `spawn` and `forkserver` children will execute import/bootstrap machinery and observe the module's import-time default instead of the parent's later mutation.

Alternative outcome:

> Every child will observe `parent-mutated`, or every child will observe `import-default`, showing that the chosen start method does not produce the predicted state boundary on this runtime.

## 3. Environment

Recorded values:

```text
Date: 2026-08-28
Operating system: Linux 7.0.0-30-generic
Architecture: x86_64
Python version: 3.14.4
sys.version: 3.14.4 (main, Jun 18 2026, 14:25:02) [GCC 15.2.0]
sys.implementation: cpython
Build type: regular GIL-enabled CPython
Free-threaded build: False
GIL enabled: True
Dependencies: Python standard library only
CPU: 28 logical CPUs reported; not used for a benchmark claim
Relevant environment variables: none recorded
Execution note: the forkserver Unix socket required execution outside the filesystem sandbox
```

## 4. Controls and variables

### Controlled

- The module defines `MODULE_TOKEN = "import-default"` at import time.
- The parent changes it once to `"parent-mutated"` before creating any measured child.
- Every child runs the same top-level `observe_token` function.
- A one-way `Pipe` carries exactly the child PID and observed token.
- Every receive and join has a ten-second failure guard.
- All methods run in one parent process on the same interpreter and host.

### Changed

- The multiprocessing context: `forkserver`, `fork`, or `spawn` in the order reported by `get_all_start_methods()`.

### Measured

- The token seen by the child.
- Distinct parent and child PIDs.
- The child exit code.

## 5. Files

```text
experiments/EXP-01-start-method-state/
├── README.md
└── start_method_state.py
```

The runnable source is [`start_method_state.py`](start_method_state.py).

## 6. Reproduction command

Run from the repository root on a platform that supports the desired methods:

```bash
python units/concurrency/PY-CON-040-multiprocessing-ipc-shared-memory-and-process-isolation/experiments/EXP-01-start-method-state/start_method_state.py
```

## 7. Prediction

```text
forkserver -> child token 'import-default'
fork       -> child token 'parent-mutated'
spawn      -> child token 'import-default'
all child PIDs differ from the parent PID
all exit codes are zero
```

## 8. Observed output

```text
method=forkserver parent=149927 child=149940 token='import-default' exitcode=0
method=fork parent=149927 child=149941 token='parent-mutated' exitcode=0
method=spawn parent=149927 child=149942 token='import-default' exitcode=0
```

No output was edited to match the hypothesis.

## 9. Interpretation

1. All three activities ran in distinct child processes and exited successfully.
2. The `fork` child directly observed the parent's mutated snapshot on this Linux CPython run.
3. The `spawn` and `forkserver` children directly observed the import-time value instead.
4. The result supports treating child initialization as explicit: pass needed data, establish resources in an initializer or target, and never depend on a parent's later global mutation.
5. The output does not prove that every inherited resource is safe after `fork`, that globals are a supported IPC mechanism, or that another platform exposes all three methods.

## 10. Visual interpretation

```text
parent imports module              MODULE_TOKEN = "import-default"
parent mutates global              MODULE_TOKEN = "parent-mutated"
             |
             +-- fork -----------> memory snapshot sees "parent-mutated"
             |
             +-- forkserver -----> child bootstrap sees "import-default"
             |
             +-- spawn ----------> fresh interpreter sees "import-default"
```

### How to read this visual

Read downward through the two parent events, then follow each branch to the value the corresponding child reported. The arrows are conceptual initialization paths, not literal memory maps or a complete OS process trace.

### Key insight

Start method is part of program semantics. Import-safe targets and explicit data transfer work across methods; relying on a mutated global does not.

### Simplification or limitation

The diagram omits the forkserver helper process, resource tracker, file descriptors, import caches, threads, and operating-system copy-on-write mechanics. It records this program's public observations rather than specifying CPython internals.

## 11. Language and implementation conclusions

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| `get_context()` selected an explicit start method without mutating the program-wide default. | Standard-library contract plus observation | CPython 3.14.4; API exists in Python 3.11 | Only request a method returned by `get_all_start_methods()`. |
| The `fork` child observed the parent's mutated global snapshot. | POSIX CPython observation | Linux, CPython 3.14.4 | Do not turn this observation into a safe-resource or synchronization guarantee. |
| The `spawn` child observed import-time module state. | Standard-library design plus observation | CPython 3.14.4 | `spawn` is the only method on Windows and the default on Windows and macOS. |
| The `forkserver` child observed import-time module state. | POSIX CPython observation | Linux, CPython 3.14.4 | `forkserver` is unavailable on some POSIX platforms and on Windows. |
| Python 3.14 reports `forkserver` first on this POSIX host. | Version-dependent standard-library behavior | Python 3.14 | Python 3.11 used `fork` as the POSIX default. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular GIL-enabled build was run.
- Windows, macOS, alternative interpreters, frozen executables, containers with different IPC restrictions, and free-threaded builds were not tested.
- One immutable string binding was observed; no file handle, socket, lock, native library, thread, random generator, or database connection was inherited.
- The experiment does not measure startup latency, memory use, copy-on-write cost, throughput, or scheduler behavior.
- The explicit order of available methods is platform- and version-dependent.
- PIDs are one run's observations and will change on reproduction.

## 13. Follow-up

- Related unit: `PY-MOD-020` for import execution and module caching.
- Improved experiment: repeat on Windows and macOS, recording available/default methods and import side effects without attempting unsupported methods.
- Remaining question: which real application resources should be constructed per worker, and which immutable configuration should be passed explicitly?

## 14. Authoritative sources

1. [`multiprocessing` — Contexts and start methods](https://docs.python.org/3.14/library/multiprocessing.html#contexts-and-start-methods), Python 3.14.7 documentation, accessed 2026-08-28.
2. [`multiprocessing` — The spawn and forkserver start methods](https://docs.python.org/3.14/library/multiprocessing.html#the-spawn-and-forkserver-start-methods), Python 3.14.7 documentation, accessed 2026-08-28.
3. [`multiprocessing` — Python 3.11 contexts and start methods](https://docs.python.org/3.11/library/multiprocessing.html#contexts-and-start-methods), Python 3.11.15 documentation, accessed 2026-08-28.
