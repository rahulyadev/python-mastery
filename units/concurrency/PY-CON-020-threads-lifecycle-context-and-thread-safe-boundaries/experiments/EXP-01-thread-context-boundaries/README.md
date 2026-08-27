# EXP-01 — Explicit and default thread context boundaries

| Field | Value |
|---|---|
| Owning unit | [`PY-CON-020`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-con-020) |
| Topic branch | `topic/PY-CON-020` |
| Precise question | How do omitted, empty, and copied Python 3.14 thread contexts affect the initial `ContextVar` binding, and do worker changes flow back to the main context or its thread-local state? |
| Classification | Standard library plus CPython runtime configuration |
| Status | Interpreted |
| Risk | Concurrency; controlled and local |

## 1. Why an experiment is necessary

“Context follows execution” is too vague to predict a new thread. Python 3.14 makes omitted context depend on `thread_inherit_context`, whose default differs between regular and free-threaded builds. A controlled trace distinguishes that default policy from explicit `Context()` and `copy_context()` behavior and exposes whether worker assignments leak back.

## 2. Hypothesis

Before execution:

> With the inheritance flag set to zero, an omitted context and an explicit empty context will both begin with `UNSET`; with the flag set to one, the omitted context will see the caller's binding at `start()`. An explicit copied context will see the value captured earlier in both runs. Worker assignments will remain in worker contexts and thread-local views.

Alternative outcome:

> Thread creation time rather than `start()` time controls default inheritance, explicit contexts are overridden by the flag, or worker assignments replace the main thread's bindings.

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
CPU: not recorded; this is not a benchmark
Relevant environment variables: none; interpreter -X flags are explicit below
```

## 4. Controls and variables

### Controlled

- One module-level `ContextVar` with default `UNSET`.
- One `threading.local` instance whose main-thread label is `main-thread`.
- Caller binding is `request-at-snapshot` when `copy_context()` runs and `request-at-start` when each worker starts.
- Workers run sequentially with immediate joins so scheduling order and simultaneous context entry are not variables.
- Explicit empty and copied cases are identical in both processes.

### Changed

- `-X thread_inherit_context=0` versus `-X thread_inherit_context=1`.
- Per worker: omitted `context`, explicit `Context()`, or explicit captured `Context`.

### Measured

- Initial and final worker `ContextVar` bindings.
- Initial and final worker `threading.local` labels.
- Main-thread bindings after every worker terminates.
- Runtime build, GIL, and inheritance-flag values.

## 5. Files

```text
experiments/EXP-01-thread-context-boundaries/
├── README.md
└── context_boundary.py
```

The runnable source is [`context_boundary.py`](context_boundary.py).

## 6. Reproduction commands

Run from the repository root:

```bash
python -X thread_inherit_context=0 units/concurrency/PY-CON-020-threads-lifecycle-context-and-thread-safe-boundaries/experiments/EXP-01-thread-context-boundaries/context_boundary.py
python -X thread_inherit_context=1 units/concurrency/PY-CON-020-threads-lifecycle-context-and-thread-safe-boundaries/experiments/EXP-01-thread-context-boundaries/context_boundary.py
```

## 7. Prediction

```text
flag=0:
  default initial context -> UNSET
  empty initial context   -> UNSET
  copied initial context  -> request-at-snapshot

flag=1:
  default initial context -> request-at-start
  empty initial context   -> UNSET
  copied initial context  -> request-at-snapshot

both:
  every worker begins with no main-thread local label
  worker writes remain out of the main context and main thread-local view
```

## 8. Observed output

### Inheritance disabled

```text
implementation=cpython
version=3.14.4
free_threaded_build=False
gil_enabled=True
thread_inherit_context=0
copied: context_before=request-at-snapshot, context_after=worker-context:copied, tls_before=UNSET, tls_after=worker-thread-local:copied
default: context_before=UNSET, context_after=worker-context:default, tls_before=UNSET, tls_after=worker-thread-local:default
empty: context_before=UNSET, context_after=worker-context:empty, tls_before=UNSET, tls_after=worker-thread-local:empty
main: context=request-at-start, tls=main-thread
```

### Inheritance enabled

```text
implementation=cpython
version=3.14.4
free_threaded_build=False
gil_enabled=True
thread_inherit_context=1
copied: context_before=request-at-snapshot, context_after=worker-context:copied, tls_before=UNSET, tls_after=worker-thread-local:copied
default: context_before=request-at-start, context_after=worker-context:default, tls_before=UNSET, tls_after=worker-thread-local:default
empty: context_before=UNSET, context_after=worker-context:empty, tls_before=UNSET, tls_after=worker-thread-local:empty
main: context=request-at-start, tls=main-thread
```

No output was edited to match the hypothesis.

## 9. Interpretation

1. The output directly shows that omitted `context` followed the explicitly selected inheritance flag, while `Context()` stayed empty and the copied context kept the earlier snapshot in both runs.
2. It reasonably supports using explicit empty or copied context whenever application behavior must not vary with interpreter flags or build defaults.
3. The main values show that rebinding the `ContextVar` and assigning the thread-local attribute inside a worker did not replace the main thread's bindings.
4. It does not show that objects stored as context values are immutable, that arbitrary shared objects are safe, or that these threads ran in parallel.

## 10. Visual interpretation

```text
main Context: request-at-snapshot -- copy --> copied worker: request-at-snapshot
                     |
                     +-- set request-at-start -- start default worker
                                                   |
                         flag 0 -> UNSET -----------+
                         flag 1 -> request-at-start-+

explicit Context() ---------------------> empty worker: UNSET

worker rebinding ----X----> main Context remains request-at-start
worker thread-local -X----> main thread-local remains main-thread
```

### How to read this visual

Read the first line as snapshot timing. Then follow the main context to the later binding present at `start()`. The flag selects the default worker's initial binding; it does not affect either explicit context. The crossed arrows show that worker assignments are not reverse propagation.

### Key insight

Default inheritance is runtime policy; explicit context is application policy.

### Simplification or limitation

The diagram shows binding relationships, not object copies or memory layout. A mutable object bound in two contexts can still be the same object, and the sequential workers do not test simultaneous entry or parallel execution.

## 11. Language and implementation conclusions

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| `Thread(context=Context())` starts with an empty context and `Thread(context=copy_context())` starts with an explicit snapshot. | Standard-library contract | Python 3.14.4 observed; API added in 3.14 | Python 3.11 can call `context.run(target)` inside the worker instead. |
| Omitting `context` follows `sys.flags.thread_inherit_context`. | Standard-library contract plus runtime configuration | Python 3.14.4 observed; added in 3.14 | Do not use omitted context when correctness requires one fixed policy. |
| The flag defaults differ between regular and free-threaded builds. | CPython version/build behavior | Python 3.14 documentation | This experiment forced both values on a regular build; it did not run a free-threaded binary. |
| Worker context and thread-local rebinding did not replace main-thread bindings. | Observed standard-library behavior | CPython 3.14.4 | This says nothing about concurrent mutation of an object referenced by multiple bindings. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular build was run.
- The free-threaded default was simulated by forcing the inheritance flag; no free-threaded interpreter executed the experiment.
- Workers were sequential to isolate initial context, so the experiment provides no parallelism, race, or performance evidence.
- Values were immutable strings; the trace does not test shared mutable values.
- No native extension or foreign-created thread participated.

## 13. Follow-up

- Related unit: `PY-CON-030` for synchronization, queues, races, and deadlocks.
- Improved experiment: run the same commands on an actual free-threaded CPython build and record whether its default process matches the forced-true case.
- Remaining question: which application contexts should be copied, passed explicitly as ordinary arguments, or deliberately cleared at a real service boundary?

## 14. Authoritative sources

1. [`Thread` constructor and `context` parameter](https://docs.python.org/3.14/library/threading.html#threading.Thread), Python 3.14.7 documentation, accessed 2026-08-28.
2. [Manual `Context` management](https://docs.python.org/3.14/library/contextvars.html#manual-context-management), Python 3.14.7 documentation, accessed 2026-08-28.
3. [Free-threaded context-variable behavior](https://docs.python.org/3.14/howto/free-threading-python.html#context-variables), Python 3.14.7 documentation, accessed 2026-08-28.
4. [`sys.flags.thread_inherit_context`](https://docs.python.org/3.14/library/sys.html#sys.flags.thread_inherit_context), Python 3.14.7 documentation, accessed 2026-08-28.
