# Practice — PY-CON-040 Multiprocessing, IPC, shared memory, and process isolation

| Field | Value |
|---|---|
| Unit note | [`PY-CON-040`](../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../CURRICULUM.md#py-con-040) |
| Topic branch | `topic/PY-CON-040` |
| Evidence target | E+C+D+X |
| Attempt required before solution | Yes |
| Test command | Define a narrow deterministic command with the first code attempt. |
| Status | Not attempted |

## Practice rules

1. State the process owner, message owner, and resource-cleanup owner before writing code.
2. Use an explicit multiprocessing context; make every child target importable and every entry point safe under `spawn`.
3. Record a prediction before executing a start-method, ordering, isolation, or failure exercise.
4. Preserve the first attempt and first failing deterministic test.
5. Do not use arbitrary sleeps for coordination; use messages, events, barriers, bounded timeouts, or controlled worker functions.
6. Do not use `Queue.empty()` or `qsize()` for correctness and do not cancel feeder flushing merely to hide an ownership bug.
7. Never deserialize untrusted pickle data; document the trust boundary and message schema.
8. Keep comparison solutions hidden until the learner closes the exercise.
9. Do not push later attempts automatically; keep the topic worktree pinned until publication.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Suggested files | Status |
|---|---|---:|---|---|---|
| `PY-CON-040-P01` | Predict | 2 | Trace module state under `spawn` and `fork` without treating globals as IPC. | `practice/p01_prediction.md` | Not attempted |
| `PY-CON-040-P02` | Implement | 3 | Supervise isolated checksum workers with explicit success and failure messages. | `practice/p02_supervisor.py` and focused tests | Not attempted |
| `PY-CON-040-P03` | Debug | 4 | Diagnose a queue feeder/join deadlock from the first invalid lifecycle assumption. | `practice/p03_queue_deadlock.py` and focused tests | Not attempted |
| `PY-CON-040-P04` | Implement | 4 | Build a bounded multi-process transform pipeline with graceful shutdown. | `practice/p04_pipeline.py` and focused tests | Not attempted |
| `PY-CON-040-P05` | Experiment | 4 | Compare copy-based IPC with partitioned shared memory without inventing benchmark claims. | `practice/p05_shared_memory/` | Not attempted |
| `PY-CON-040-P06` | Design | 5 | Specify a secure, observable process boundary for synthetic document analysis. | `practice/p06_design.md` | Not attempted |

## PY-CON-040-P01 — Predict child-visible state

### Problem

Without running this file, predict the output pattern under `spawn` and under `fork` on a POSIX platform. Distinguish what the child sees from what the parent sees, and label every platform-specific assumption.

```python
import multiprocessing as mp

records = ["imported"]


def report(connection):
    records.append("child")
    connection.send(tuple(records))
    connection.close()


def run(method):
    context = mp.get_context(method)
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=report, args=(sender,))
    records.append("parent")
    process.start()
    sender.close()
    child_records = receiver.recv()
    process.join()
    return tuple(records), child_records


if __name__ == "__main__":
    print(run("spawn"))
```

### Learning evidence

- Trace import-time state, the parent's later mutation, child initialization, and child-local mutation separately.
- Explain why a top-level target plus guarded entry point matters.
- State why either observed list is a snapshot rather than a shared Python list.

### Required edge cases

- Replace the top-level target with a nested function.
- Run in an interactive shell rather than an importable file.
- Request `fork` on Windows.
- Start a second child after the parent appends another item.

### Acceptance criteria

- [ ] The `spawn` prediction includes re-import/bootstrap semantics.
- [ ] The parent and child mutations are kept in separate address spaces.
- [ ] `fork` behavior is labelled POSIX-specific and is not presented as a portable design.
- [ ] No execution occurs before the trace is recorded.

### Learner attempt

- Start-method assumptions:
- Parent trace:
- Child trace:
- Prediction:
- Command:
- Observed output:
- First incorrect assumption after review:

## PY-CON-040-P02 — Implement a supervised checksum boundary

### Problem

Implement `run_checksums(payloads, *, context_name="spawn", timeout=...)`. Each payload has a synthetic ID and immutable bytes. Use no more than three child processes at once. Every accepted payload must produce one immutable success or failure record containing its ID and child PID. The parent must return results in input order and prove every child has terminated.

One selected payload should cause a deterministic worker exception. The exception must become data at the owner boundary; it must not silently disappear or turn into a fabricated successful result.

### Constraints

- Standard library only and Python 3.11-compatible public code.
- Importable top-level targets and guarded executable entry point.
- Explicit context supplied by the caller; do not call global `set_start_method()`.
- Bounded messages and timeouts; no arbitrary sleeps or busy waiting.
- No shared mutable Python container and no daemon workers.
- Do not use `terminate()` on a worker that may be holding a queue or lock during the normal path.

### Required edge cases

- Empty input.
- More payloads than the concurrency bound.
- Zero-length bytes.
- One deterministic worker exception.
- Worker exits without sending a result.
- Parent timeout with at least one process still alive.

### Acceptance criteria

- [ ] Process ownership and maximum live-worker count are tested.
- [ ] Success, application failure, abnormal exit, and timeout remain distinct.
- [ ] Input ordering is reconstructed explicitly rather than inferred from completion order.
- [ ] Every process is joined and its exit code inspected.
- [ ] Cleanup behavior is explained for both normal and failure paths.

### Learner attempt

- Ownership model:
- Message schema:
- Attempt files:
- Test command:
- Observed result:
- Remaining uncertainty:

## PY-CON-040-P03 — Debug a queue/join hang

### Problem

Find the first incorrect lifecycle assumption in this program before proposing a fix:

```python
import multiprocessing as mp


def produce(queue):
    queue.put(b"x" * 5_000_000)


if __name__ == "__main__":
    context = mp.get_context("spawn")
    queue = context.Queue()
    process = context.Process(target=produce, args=(queue,))
    process.start()
    process.join()
    payload = queue.get()
    print(len(payload))
```

Explain the background feeder, pipe capacity, child shutdown, receive order, queue closure, and why `cancel_join_thread()` is not a general-purpose repair.

### Constraints

- The first review response contains no replacement implementation.
- Do not shrink the payload, add sleep, remove all joins, or use a private queue attribute to make the symptom disappear.
- Protect the test runner with a bounded outer timeout.
- Preserve the original failing reproduction.

### Required edge cases

- Payload happens to fit in the pipe buffer.
- Child raises before `put()`.
- Parent receives before joining.
- Multiple child producers send messages.
- A producer is forcibly terminated during queue use.

### Acceptance criteria

- [ ] The dependency cycle between feeder flush, receive, and join is explicit.
- [ ] Accidental success with a small payload is not called correctness.
- [ ] The repaired ownership order is deterministic.
- [ ] Queue endpoints and processes are closed or joined deliberately.
- [ ] Forced termination risks are stated.

### Learner attempt

- First invalid assumption:
- Wait-for graph:
- Attempt files:
- Test command:
- Observed result:

## PY-CON-040-P04 — Build a bounded transform pipeline

### Problem

Build a `TransformService` that owns a fixed process count, a bounded input channel, and a result channel. `submit()` must distinguish accepted, overloaded, not-started, and closing states. Each accepted synthetic document receives exactly one success or structured failure. Graceful shutdown closes admission, drains accepted work, sends one stop message per worker, and joins every worker.

### Constraints

- Standard library only; Python 3.11 compatibility.
- Caller-selected multiprocessing context.
- Picklable, versioned message schema with bounded payload size.
- No daemon processes, queue polling for correctness, global mutable registry, or unbounded producer wait.
- Worker code must not hold synchronization primitives while performing unrelated blocking I/O.
- Tests use events or controlled functions, not sleep-based ordering.

### Required edge cases

- Capacity exhausted while workers are blocked by a test gate.
- One job raises but later jobs still complete.
- Shutdown races with a blocked submitter.
- Duplicate job ID.
- Worker exits abnormally before acknowledging a job.
- Shutdown deadline expires.

### Acceptance criteria

- [ ] Admission, processing, result delivery, task accounting, and worker lifetime are separate states.
- [ ] Every accepted ID has one terminal outcome or an explicit indeterminate classification after worker loss.
- [ ] Backpressure is observable and bounded.
- [ ] Graceful shutdown completes without `terminate()` on the normal path.
- [ ] Tests prove no worker remains alive.

### Learner attempt

- State machine:
- Ownership and bounds:
- Attempt files:
- Test command:
- Observed result:
- Remaining uncertainty:

## PY-CON-040-P05 — Compare serialization and shared-memory partitioning

### Problem

Create two implementations of the same synthetic integer transformation:

1. send immutable chunks to workers and receive transformed chunks;
2. place fixed-width integers in shared memory and give each worker a disjoint half-open range.

First prove identical results and cleanup. Only then design a responsible benchmark plan; do not claim one approach is faster until actual measurements and environment details are recorded.

### Constraints

- Standard library only and Python 3.11-compatible execution path.
- Explicit shape, type, byte order, range ownership, and message metadata.
- Exactly one owner calls `unlink()`; every attached handle calls `close()`.
- No overlapping writers in the initial experiment.
- Validate integer range before packing and validate every requested partition.

### Required edge cases

- Empty input.
- One-element input.
- Uneven partitions.
- Worker fails after attaching but before reporting completion.
- Parent attempts cleanup while a worker is still alive.
- Duplicate or overlapping partition description.

### Acceptance criteria

- [ ] Correctness tests precede timing.
- [ ] Transfer bytes and shared buffer layout are calculable from inputs.
- [ ] Cleanup remains correct on every observed failure path.
- [ ] Shared memory is not described as inherently synchronized.
- [ ] Benchmark workload, warm-up, trials, timing method, raw observations, and limitations are recorded if timing occurs.

### Learner attempt

- Hypothesis:
- Buffer and ownership model:
- Attempt files:
- Correctness command and output:
- Benchmark plan:
- Remaining uncertainty:

## PY-CON-040-P06 — Design a production process boundary

### Problem

Design, without framework code, a local multi-process boundary for synthetic document analysis. Requests originate in a network service, documents may be large, worker code may consume excessive CPU or memory, callers may disconnect, deployments may run on Linux or Windows, and results must be auditable.

Cover process topology, start-method/context ownership, request schema, size limits, trust boundary, serialization choice, backpressure, per-job deadlines, worker recycling, graceful shutdown, crash recovery, duplicate delivery, logging context, metrics, deployment constraints, and when an external durable job system should replace local multiprocessing.

### Acceptance criteria

- [ ] Untrusted input is never automatically unpickled.
- [ ] Memory, queue, process, payload, and time bounds are explicit.
- [ ] Cancellation of caller interest is separated from proof that CPU work stopped.
- [ ] Abnormal exit, retry, duplicate effects, and indeterminate work are modeled.
- [ ] No in-memory queue is described as durable across service restart.
- [ ] Platform defaults are not the API contract.
- [ ] The transition to an external worker system has concrete criteria.

### Learner attempt

- Trust and ownership boundaries:
- State machine:
- Failure matrix:
- Observability:
- Trade-off decision:
- Review weakness:
