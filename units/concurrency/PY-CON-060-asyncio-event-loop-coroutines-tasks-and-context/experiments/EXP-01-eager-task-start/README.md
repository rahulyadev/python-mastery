# EXP-01 — Default versus eager Task start

| Field | Value |
|---|---|
| Owning unit | [`PY-CON-060`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-con-060) |
| Topic branch | `topic/PY-CON-060` |
| Precise question | On the tested Python 3.14 runtime, which coroutine statements execute before and after `asyncio.create_task()` returns under default start and `eager_start=True`? |
| Classification | Python-version-dependent standard-library behavior plus CPython/default-loop scheduling observation |
| Status | Interpreted |
| Risk | Local standard-library execution; no network or external side effects |

## 1. Why an experiment is necessary

The usual teaching shorthand says that `create_task()` schedules a coroutine to run “soon,” so the caller's next statement runs before the coroutine body. Python 3.14 can override that entry boundary with `eager_start=True`. A controlled trace makes the semantic difference visible and separates it from the later ready-queue interleaving.

The experiment does not recommend eager start. It records where reentrancy can occur so ordering-sensitive code can avoid an invalid assumption.

## 2. Hypothesis

Before execution:

> The default Task will not enter `probe()` inside its `create_task()` call. The eager Task will append `eager:start` synchronously before the caller appends `after-eager`. Because the eager coroutine then awaits `asyncio.sleep(0)`, it will return control to the creator without being done.

For this CPython 3.14.4 Unix selector loop, the predicted later order is:

> At the next loop iteration the already-ready lazy Task starts, the eager Task resumes, and then the main Task resumes from its own `sleep(0)`. The lazy Task resumes after main awaits it.

Alternative outcome:

> Neither coroutine enters synchronously, or the eager coroutine completes before the creation call returns, or the later ready callbacks appear in another order. The first two would contradict the specific code/hypothesis; the last could indicate a different compatible loop implementation or scheduling configuration.

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
Py_GIL_DISABLED: 0
GIL enabled: True
Loop class: asyncio.unix_events._UnixSelectorEventLoop
Task class: _asyncio.Task
Debug mode: False
Dependencies: Python standard library only
CPU: 28 logical CPUs reported; not used for a benchmark claim
Relevant flags and environment variables: no task factory, loop factory, debug flag, or scheduling-related environment variable supplied
```

## 4. Controls and variables

### Controlled

- Both Tasks run the same `probe(label, events)` coroutine.
- Each probe appends one entry event, awaits exactly one `asyncio.sleep(0)`, then appends one resumption event.
- Both Tasks run on the same fresh loop created by `asyncio.run()`.
- No custom loop factory, task factory, threads, wall-clock delay, I/O, cancellation, or external dependency is used.
- The owner awaits both Tasks before the runner closes.

### Changed

- The first Task uses default creation.
- The second Task passes `eager_start=True`.

### Measured

- The order of caller, lazy-probe, and eager-probe events.
- `done()` immediately after each creation boundary.

## 5. Files

```text
experiments/EXP-01-eager-task-start/
├── README.md
└── eager_task_start.py
```

The runnable source is [`eager_task_start.py`](eager_task_start.py).

## 6. Reproduction command

Run from the repository root with Python 3.14 or newer:

```bash
python units/concurrency/PY-CON-060-asyncio-event-loop-coroutines-tasks-and-context/experiments/EXP-01-eager-task-start/eager_task_start.py
```

The focused regression test is:

```bash
python -m unittest discover -s units/concurrency/PY-CON-060-asyncio-event-loop-coroutines-tasks-and-context/tests -v
```

## 7. Prediction

```text
after-lazy done=False
eager:start
after-eager done=False
lazy:start
eager:resume
main:after-turn
lazy:resume
main:collected
```

Critical boundary prediction: `eager:start` appears before `after-eager`, but `lazy:start` cannot appear before `after-lazy` under this default/non-eager first creation.

## 8. Observed output

```text
after-lazy done=False
eager:start
after-eager done=False
lazy:start
eager:resume
main:after-turn
lazy:resume
main:collected
```

No output was edited to match the hypothesis.

## 9. Interpretation

1. The default Task returned to its creator before entering `probe()`, supporting the normal “scheduled soon” mental model for this fresh loop.
2. The eager Task entered `probe()` inside the creation call, proving that user coroutine code can run before the caller's next statement under explicit eager start.
3. The eager Task was not done after creation because `asyncio.sleep(0)` forced a suspension; eager start means “run until blocked/finished,” not “finish synchronously.”
4. The later trace matches the tested CPython loop's ready-handle order: the lazy first step, eager continuation, and main continuation were already queued in that order.
5. The result invalidates code that uses the statement immediately after `create_task()` as a universal “child has not run yet” boundary.

## 10. Visual interpretation

```text
default create_task(lazy)              eager create_task(eager)
        |                                      |
        +-- queue first step                   +-- enter coroutine now
        |                                      |      eager:start
        +-- return Task                        |      await sleep(0)
        |                                      +-- queue continuation
        v                                      +-- return Task
  after-lazy line                              v
                                         after-eager line

next loop work on this run:
  lazy:start -> eager:resume -> main:after-turn -> lazy:resume
```

### How to read this visual

Compare the two vertical creation paths first. The default path returns after queueing; the eager path runs user code until the first suspension before returning. Then read the bottom line as this runtime's observed ready-order continuation, not a cross-loop guarantee.

### Key insight

Task creation can be a reentrant execution boundary when eager start is enabled.

### Simplification or limitation

The diagram omits Tasks that return or raise before suspending, custom task factories, explicit Context objects, callbacks created inside `probe()`, alternative event loops, debug hooks, cancellation, and structured task owners.

## 11. Language and implementation conclusions

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| `create_task(..., eager_start=True)` entered the coroutine during the creation call. | Python-version-dependent standard-library behavior plus observation | CPython 3.14.4 | `eager_start` is unavailable in Python 3.11; compatible third-party loops/factories must define support. |
| The eager Task returned incomplete after reaching `sleep(0)`. | Standard-library contract plus observation | Python/CPython 3.14.4 | `sleep(0)` always suspends, but a coroutine that returns before awaiting may already be done. |
| Default task creation did not enter the coroutine inline. | Default configuration observation | CPython 3.14.4 fresh Unix selector loop | A configured eager task factory can change default creation behavior. |
| The later ready order matched insertion order in `BaseEventLoop._run_once()`. | CPython implementation observation | CPython 3.14.4 | Do not require another event loop or future CPython version to expose the same mixed Task/callback trace. |
| Both Tasks completed on one OS thread. | Observation and asyncio scheduling model | CPython 3.14.4 | This experiment says nothing about CPU parallelism or thread offloading. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular GIL-enabled build was run.
- Python 3.11 cannot run the eager-start call; Python 3.14.7 documentation was source-audited but 3.14.7 was not the executed runtime.
- Only the built-in Unix selector event loop and default Task class were observed.
- The probes suspend exactly once with `asyncio.sleep(0)`; immediate return, immediate exception, pending I/O, and multiple awaits can produce other traces.
- Debug mode, a custom task factory, `asyncio.eager_task_factory()`, explicit Context, alternative event loops, Windows proactor behavior, and free-threaded CPython were not tested.
- The experiment measures order only. It does not measure latency, throughput, allocation, fairness, or eager-start performance.
- The GIL state is recorded for reproducibility but does not explain the eager-start contract.

## 13. Follow-up

- Related unit: `PY-CON-070` for structured task ownership, cancellation, and exception propagation when eager code raises or completes during creation.
- Related unit: `PY-CON-080` for fairness, backpressure, async iteration, and blocking boundaries under real workload.
- Improved experiment: repeat with immediate return, immediate exception, explicit `context=`, a configured eager task factory, and an alternative event loop while keeping every outcome owned.
- Remaining question: which libraries deliberately enable eager factories, and how do they document reentrancy to callers?

## 14. Authoritative sources

1. [`asyncio.create_task()`](https://docs.python.org/3.14/library/asyncio-task.html#asyncio.create_task), `eager_start`, Context capture, task-reference guidance, and 3.14 change note; Python 3.14.7 documentation, accessed 2026-08-28.
2. [`asyncio.sleep()`](https://docs.python.org/3.14/library/asyncio-task.html#asyncio.sleep), guaranteed suspension and optimized zero-delay path; Python 3.14.7 documentation, accessed 2026-08-28.
3. [CPython 3.14.7 `Lib/asyncio/tasks.py`](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/tasks.py), explanatory Task eager-start and scheduled-step paths; accessed 2026-08-28.
4. [CPython 3.14.7 `Lib/asyncio/base_events.py`](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/base_events.py), `BaseEventLoop._run_once()` ready-batch implementation; accessed 2026-08-28.
5. [Python 3.11 Coroutines and Tasks](https://docs.python.org/3.11/library/asyncio-task.html), compatibility baseline without `eager_start`; Python 3.11.15 documentation, accessed 2026-08-28.
