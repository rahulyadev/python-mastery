# EXP-01 — Timeout cancellation provenance

| Field | Value |
|---|---|
| Owning unit | [`PY-CON-070`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-con-070) |
| Topic branch | `topic/PY-CON-070` |
| Precise question | On the tested Python 3.14 runtime, how does `asyncio.timeout()` distinguish the cancellation it initiated from an external cancellation request? |
| Classification | Python standard-library contract plus CPython runtime observation |
| Status | Interpreted |
| Risk | Local standard-library execution; no network, files, threads, or external side effects |

## 1. Why an experiment is necessary

Both an expired timeout scope and an external shutdown request are implemented by cancelling a Task. The public outcome must nevertheless preserve provenance: the timeout manager may translate the cancellation it owns into `TimeoutError`, while an unrelated caller's cancellation must remain `CancelledError`.

A controlled trace reveals three boundaries that prose can blur:

1. code inside the timeout scope initially sees cancellation;
2. cleanup runs while that exception unwinds;
3. the timeout context manager performs translation only at its outer boundary.

The experiment also checks that a timeout disabled with `None` does not convert an external cancellation into a timeout.

## 2. Hypothesis

Before execution:

> In the zero-duration timeout case, the current Task will enter the scope, suspend on an unset Event, receive `CancelledError`, run `finally`, and expose `TimeoutError` only after leaving the timeout context. The timeout manager will restore the Task's pre-scope cancellation count.

For the external case:

> A separately owned Task inside `asyncio.timeout(None)` will receive the owner's cancellation request, run cleanup, terminate as cancelled, and propagate `CancelledError` to its owner. No `TimeoutError` event will appear.

Alternative outcomes to classify:

- `TimeoutError` appears inside the timeout scope;
- cleanup does not run;
- timeout-owned cancellation remains pending after successful handling;
- external cancellation is translated to `TimeoutError`;
- the externally cancelled Task reports a non-cancelled terminal state.

Any of those outcomes would contradict at least one hypothesis and require checking the public contract, the test design, or a version difference.

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
Relevant flags and environment variables: no loop factory, task factory, debug flag, or scheduling-related environment variable supplied
```

The repository's canonical documentation baseline is Python 3.14.7. Execution occurred on the available CPython 3.14.4 runtime, so observed facts are labelled accordingly.

## 4. Controls and variables

### Controlled

- Both cases run on one fresh event loop created by `asyncio.run()`.
- Each operation suspends on a fresh unset `asyncio.Event`.
- Each operation records one cleanup event in `finally`.
- No wall-clock sleep, I/O, thread, signal, retry, shield, or third-party loop is used.
- Every explicitly created Task is retained and awaited to a terminal state.

### Changed

- Case one uses `asyncio.timeout(0)`, so the context manager schedules cancellation of its current Task.
- Case two uses `asyncio.timeout(None)` and a distinct owner calls `task.cancel("external shutdown")`.

### Measured

- Ordered boundary events.
- Cancellation count immediately before and after the handled timeout scope.
- The terminal `cancelled()` state of the externally cancelled Task.

## 5. Files

```text
experiments/EXP-01-timeout-cancellation-provenance/
├── README.md
└── timeout_cancellation.py
```

The runnable source is [`timeout_cancellation.py`](timeout_cancellation.py).

## 6. Reproduction command

Run from the repository root:

```bash
python units/concurrency/PY-CON-070-structured-concurrency-cancellation-and-timeouts/experiments/EXP-01-timeout-cancellation-provenance/timeout_cancellation.py
```

The focused regression command is:

```bash
python -m unittest discover -s units/concurrency/PY-CON-070-structured-concurrency-cancellation-and-timeouts/tests -v
```

## 7. Prediction

```text
timeout-owned cancellation
timeout:entered
timeout:inside-cancelled
timeout:cleanup
timeout:outside-timeout-error
timeout cancellation count: 0 -> 0
external cancellation
external:entered
external:cancel-requested
external:inside-cancelled
external:cleanup
external:owner-observed-cancelled
external task cancelled: True
```

The critical prediction is not merely the exception types. It is that the timeout's translation happens after inner cleanup, while external cancellation crosses the timeout context unchanged.

## 8. Observed output

```text
timeout-owned cancellation
timeout:entered
timeout:inside-cancelled
timeout:cleanup
timeout:outside-timeout-error
timeout cancellation count: 0 -> 0
external cancellation
external:entered
external:cancel-requested
external:inside-cancelled
external:cleanup
external:owner-observed-cancelled
external task cancelled: True
```

No output was edited to match the hypothesis.

## 9. Interpretation

1. The zero-duration scope entered before cancellation was delivered because an already-expired timeout is triggered on a subsequent event-loop iteration.
2. Code inside the timeout scope observed `CancelledError`, confirming that the mechanism is Task cancellation rather than a separate exception injected into the awaited operation.
3. The `finally` event preceded the outside `TimeoutError` event, so ordinary unwinding cleanup completed before translation at the context-manager boundary.
4. The current Task's cancellation count was zero before and after the handled timeout in this isolated case. The timeout did not leave its own cancellation request looking like an external pending request.
5. `asyncio.timeout(None)` established no deadline. The explicit owner cancellation stayed `CancelledError`, and the victim reached a genuinely cancelled terminal state.
6. The result supports catching `TimeoutError` outside the timeout scope and allowing unrelated cancellation to propagate.

## 10. Visual interpretation

```text
timeout-owned path                         external path

enter timeout(0)                          enter timeout(None)
       |                                         |
await unset Event                         await unset Event
       |                                         |
manager cancels current Task              owner calls child.cancel()
       |                                         |
inner CancelledError                      child CancelledError
       |                                         |
finally cleanup                           finally cleanup
       |                                         |
timeout scope recognizes its request      no owned timeout to translate
       |                                         |
outer TimeoutError                        owner observes CancelledError
```

### How to read this visual

Follow each column from cancellation source to public outcome. The middle steps look similar because both use Task cancellation. The divergence occurs at the timeout manager's exit, where it can identify and translate only the cancellation associated with its own scope.

### Key insight

`TimeoutError` is a boundary interpretation of owned cancellation, not evidence that the inner operation never saw cancellation.

### Simplification or limitation

The diagram shows one cancellation request in each case. It omits nested timeouts, repeated external cancellation, simultaneous TaskGroup failure, cancellation messages, shielded children, cleanup failure, and cancellation that arrives before a coroutine first executes.

## 11. Contract and observation conclusions

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| `asyncio.timeout()` cancelled the current Task and translated its resulting `CancelledError` into `TimeoutError` outside the scope. | Standard-library contract plus observation | Python 3.11+; observed on CPython 3.14.4 | Catch the timeout outside the context manager. |
| The inner `finally` ran before timeout translation. | Language `finally` semantics plus standard-library observation | Python/CPython 3.14.4 | A later cancellation or failing cleanup can change the terminal outcome. |
| The isolated timeout restored the pre-scope cancellation count. | Standard-library behavior plus observation | CPython 3.14.4 | Nested or simultaneous cancellation requires a separate controlled case. |
| External cancellation inside `timeout(None)` remained `CancelledError`. | Standard-library contract plus observation | Python/CPython 3.14.4 | An active deadline racing with external cancellation is not tested here. |
| The externally cancelled Task reported `cancelled() is True`. | Task public API observation | Python/CPython 3.14.4 | This requires the coroutine not to suppress `CancelledError`. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular GIL-enabled build was run.
- Python 3.14.7 documentation was source-audited, but Python 3.14.7 was not the executed runtime.
- The timeout duration is exactly zero; positive deadlines introduce real clock scheduling and load sensitivity.
- Only one cancellation request occurs per case.
- No nested timeout, TaskGroup, `wait_for()`, `shield()`, signal handler, cleanup exception, or alternative event loop is exercised.
- The experiment does not measure latency, fairness, throughput, allocation, or cancellation responsiveness.
- The GIL state and CPU count are recorded only for reproducibility and do not explain the contract.
- The external case disables the timeout. It proves preservation without a deadline race, not every simultaneous-cancellation ordering.

## 13. Follow-up

- Repeat with an inner and outer timeout whose absolute deadlines differ, then classify which boundary translates the cancellation.
- Add a second external `cancel()` during awaited cleanup and record `Task.cancelling()` at every boundary.
- Combine an external owner cancellation with a child failure inside nested TaskGroups on Python 3.11, 3.13, and 3.14.
- Compare `asyncio.timeout()` with `asyncio.wait_for()` when the awaited operation performs slow cancellation cleanup.
- Carry deadline propagation and backpressure into `PY-CON-080` without resetting the remaining budget at each queue boundary.

## 14. Authoritative sources

1. [`asyncio.timeout()` and `asyncio.timeout_at()`](https://docs.python.org/3.14/library/asyncio-task.html#timeouts), cancellation transformation, deadline clock, nesting, and version history; Python 3.14.7 documentation, accessed 2026-08-28.
2. [Task cancellation](https://docs.python.org/3.14/library/asyncio-task.html#task-cancellation), cleanup, propagation, structured-concurrency interaction, and `uncancel()` guidance; Python 3.14.7 documentation, accessed 2026-08-28.
3. [`asyncio.CancelledError`](https://docs.python.org/3.14/library/asyncio-exceptions.html#asyncio.CancelledError), BaseException hierarchy and re-raise guidance; Python 3.14.7 documentation, accessed 2026-08-28.
4. [Python 3.11 Coroutines and Tasks](https://docs.python.org/3.11/library/asyncio-task.html), compatibility baseline for timeout scopes, TaskGroup, and cancellation; Python 3.11.15 documentation, accessed 2026-08-28.
