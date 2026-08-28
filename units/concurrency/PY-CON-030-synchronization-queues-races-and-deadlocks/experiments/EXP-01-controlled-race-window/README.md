# EXP-01 — Controlled race window and locked transition

| Field | Value |
|---|---|
| Owning unit | [`PY-CON-030`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-con-030) |
| Topic branch | `topic/PY-CON-030` |
| Precise question | If two threads are deliberately made to read the same counter value before either writes, is one update lost, and does locking the complete read–modify–write transition preserve both updates? |
| Classification | Standard library plus CPython runtime observation |
| Status | Interpreted |
| Risk | Concurrency; controlled and local |

## 1. Why an experiment is necessary

“A race might happen” is too weak to teach causal reasoning, while repeated uncontrolled increments can pass accidentally and encourage conclusions from scheduler luck. A barrier exposes the exact unsafe window: both workers capture the old value, both acknowledge that capture, and only then may either write. The contrasting lock case tests the intended whole-transition boundary.

This is an observation of one controlled program, not a benchmark and not an attempt to estimate how often an uncontrolled race occurs.

## 2. Hypothesis

Before execution:

> Both unsafe workers will capture zero, cross the barrier, and each write one, so the final counter will be one after two attempted updates. When a `Lock` surrounds the complete read–modify–write transition, one worker will observe the other's update and the final counter will be two.

Alternative outcome:

> The regular CPython GIL, list element assignment, or barrier interaction will serialize the unsafe logical transaction so that the final value is two, or the lock case will still lose an update.

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
Relevant environment variables: none
```

## 4. Controls and variables

### Controlled

- Exactly two non-daemon worker threads perform one attempted increment each.
- The unsafe workers read one shared list element before a two-party barrier permits either write.
- Every barrier and thread join has a two-second failure guard.
- Worker exceptions are transferred to the owner and re-raised.
- The same initial value, update count, interpreter process, and final-value observation are used in both cases.

### Changed

- Unsafe case: read and write are separate, and the barrier fixes the race window between them.
- Protected case: one `Lock` encloses the complete read–modify–write transition.

### Measured

- Final counter after two attempted updates.
- Number of lost updates in the controlled unsafe case.
- Whether the locked case preserves the expected final value.
- CPython implementation, version, build configuration, and current GIL state.

## 5. Files

```text
experiments/EXP-01-controlled-race-window/
├── README.md
└── controlled_race.py
```

The runnable source is [`controlled_race.py`](controlled_race.py).

## 6. Reproduction command

Run from the repository root:

```bash
python units/concurrency/PY-CON-030-synchronization-queues-races-and-deadlocks/experiments/EXP-01-controlled-race-window/controlled_race.py
```

## 7. Prediction

```text
attempted updates:         2
controlled unsafe final:  1
controlled lost updates:  1
locked final:             2
locked invariant:         preserved
```

## 8. Observed output

```text
implementation=cpython
version=3.14.4
free_threaded_build=False
gil_enabled=True
attempted_updates=2
controlled_unsafe_final=1
controlled_lost_updates=1
locked_final=2
locked_invariant_preserved=True
```

No output was edited to match the hypothesis.

## 9. Interpretation

1. The trace directly shows a lost update when both workers are forced to use the same captured value: two writes occur, but both write one.
2. It directly shows that the locked version completed two transitions and ended at two on this runtime. The public lock contract explains why only one worker can execute the protected transition at a time.
3. It reasonably supports defining the read, decision, and write as the unit of synchronization instead of relying on the GIL or one container operation.
4. It does not show how frequently an uncontrolled program races, whether `shared[0] += 1` has a particular bytecode decomposition on another runtime, whether lock acquisition is fair, or what performance cost the lock has.
5. It does not run a free-threaded interpreter. The build and GIL observations classify the environment rather than prove behavior on another build.

## 10. Visual interpretation

```text
CONTROLLED UNSAFE                         LOCKED

T1 read 0 ---- barrier --+                T1 acquire
                         +-- T1 write 1      read 0, write 1
T2 read 0 ---- barrier --+-- T2 write 1    release
final: 1                                  T2 acquire
                                            read 1, write 2
                                          release
                                          final: 2
```

### How to read this visual

Read the unsafe side until both barrier arrows meet; at that point both local snapshots are already zero. Either write may occur first, but both compute one. On the locked side, follow ownership down: the second read cannot happen until the first owner releases.

### Key insight

The unsafe result follows from stale snapshots, not from a mysterious scheduler failure. The repair protects the whole transition that decides the next valid state.

### Simplification or limitation

The barrier deliberately injects a blocking synchronization point inside the unsafe operation, so this is a causal reproducer rather than a natural-frequency sample. The list is only a small mutable carrier; the experiment does not claim list operations themselves are corrupt or unprotected internally.

## 11. Language and implementation conclusions

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| A `Barrier(2)` held both workers until each completed its read, producing one deterministic stale-snapshot window. | Standard-library contract plus observation | CPython 3.14.4 observed; `Barrier` exists in Python 3.11 | Barrier waiter release order remains unspecified and irrelevant to the final unsafe value. |
| A `Lock` excluded the second worker from the protected transition until the first released it. | Standard-library contract plus observation | CPython 3.14.4 observed; same public contract in Python 3.11 | Do not infer fairness or a performance bound. |
| The regular build had the GIL enabled and still lost a deliberately split application update. | CPython runtime observation | CPython 3.14.4 regular build | This is not a universal claim about every expression or alternate interpreter. |
| The locked code states a portable public synchronization boundary. | Standard-library design conclusion | Python 3.11 through 3.14 | Correctness still requires every access to follow the same invariant protocol. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular GIL-enabled build was run.
- No free-threaded build or alternative Python interpreter was executed.
- The barrier deliberately controls the unsafe interleaving; the experiment measures causality, not natural occurrence probability.
- Only two threads and one integer-valued list element are involved.
- The example has no external I/O, callbacks, cancellation, process sharing, native extension, or multi-field rollback.
- No performance, fairness, memory-order, or starvation measurement was attempted.

## 13. Follow-up

- Related unit: `PY-CON-090` for free-threaded CPython and version-specific GIL changes.
- Improved experiment: reproduce the same controlled trace on a free-threaded CPython 3.14 build and an alternative interpreter, recording build and GIL state separately.
- Remaining question: for a real reservation service, which invariant belongs in a local lock and which must be enforced atomically by the database?

## 14. Authoritative sources

1. [`threading.Lock` objects](https://docs.python.org/3.14/library/threading.html#lock-objects), Python 3.14.7 documentation, accessed 2026-08-28.
2. [`threading.Barrier` objects](https://docs.python.org/3.14/library/threading.html#barrier-objects), Python 3.14.7 documentation, accessed 2026-08-28.
3. [Python support for free threading — thread safety](https://docs.python.org/3.14/howto/free-threading-python.html#thread-safety), Python 3.14.7 documentation, accessed 2026-08-28.
