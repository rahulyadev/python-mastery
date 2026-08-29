# EXP-01 — Control-flow and dispatch trace

| Field | Value |
|---|---|
| Owning unit | [`PY-FND-060`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-fnd-060) |
| Topic branch | `topic/PY-FND-060` |
| Precise question | Which observable events are skipped or reached by `continue`, `break`, exhaustion, pattern failure, guard failure, and successful pattern binding? |
| Classification | Python language guarantees observed through a CPython runtime |
| Status | Reproduced |
| Risk | None; deterministic standard-library-only execution |

## 1. Why an experiment is necessary

A final result such as `found:2` does not reveal whether the loop `else` ran, which body suffix was skipped, or whether later items were requested. A selected match suite does not reveal how many times the subject expression ran, whether an earlier structural pattern succeeded, which guards ran, or whether captures survive their case suite.

The experiment appends fixed labels at language-visible boundaries. It exposes ordered control edges without inspecting bytecode, addresses, timing, or interpreter-private state.

## 2. Hypothesis

Before execution:

> A negative value will execute `continue` and omit the body tail. A found target will execute `break`, omit loop `else`, and resume after the loop. A complete miss will reach loop `else`. The match subject producer will run once. For a structurally valid score of 5, the urgent pattern will succeed but its guard will fail, the next guard will run, and the normal suite will be selected. A structurally unmatched subject will skip both guards and reach the fallback. A name captured by a selected case will remain bound after the case suite.

Alternative outcomes requiring investigation:

- the body tail records an event after `continue`;
- loop `else` records an event after `break`;
- the subject producer runs once per attempted case;
- the second case is not attempted after the first guard returns false;
- a guard runs even when its pattern fails;
- the successful capture becomes unavailable immediately after its suite.

## 3. Environment

Recorded actual values:

```text
Date: 2026-08-29
Operating system: Linux 7.0.0-30-generic
Architecture: x86_64
Python version: 3.14.4
sys.version: 3.14.4 (main, Jun 18 2026, 14:25:02) [GCC 15.2.0]
sys.implementation: cpython
Build type: regular release build with the GIL enabled
Py_DEBUG: 0
Py_GIL_DISABLED: 0
Dependencies: Python standard library only
CPU: not queried; this is not a benchmark
Relevant environment variables: PYTHONDONTWRITEBYTECODE=1 for the recorded clean reproduction command
```

The repository's canonical documentation baseline is Python 3.14.7. Execution occurred on the available CPython 3.14.4 runtime. The focused source uses syntax compatible with Python 3.11, but no Python 3.11 interpreter was executed for this observation.

## 4. Controls and variables

### Controlled

- Input tuples, target values, subject values, labels, and guard thresholds are fixed.
- Each trace creates a fresh event list.
- Subject and guard helpers append one deterministic label and return their supplied value.
- The successful-binding observation uses the canonical example function.
- No clock, randomness, filesystem data, network, subprocess, thread, signal, external service, or mutable global state is used.
- Formatting is deterministic and covered by a focused regression test.

### Changed

- Loop termination: target found with `break` versus iterator exhaustion.
- Loop item: negative value taking `continue` versus non-matching and matching non-negative values.
- Match subject: a tuple that satisfies both structural patterns versus a tuple that satisfies neither.
- Guard result: the urgent threshold is false and the later valid threshold is true.
- Observation point: inside case selection versus after a successful case suite.

### Measured

- Final loop and match result labels.
- Exact ordered event labels.
- Absence of body-tail, loop-else, or guard labels from paths that should skip them.
- Number of `subject` events.
- Value returned from a name captured inside a selected case and read after the match.

## 5. Files

```text
experiments/EXP-01-control-flow-dispatch-trace/
├── README.md
└── control_flow_trace.py
```

Runnable source: [`control_flow_trace.py`](control_flow_trace.py)

Focused regression: [`../../tests/test_examples.py`](../../tests/test_examples.py)

## 6. Reproduction command

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python units/foundations/PY-FND-060-control-flow-and-structural-pattern-matching/experiments/EXP-01-control-flow-dispatch-trace/control_flow_trace.py
```

Focused regression command:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s units/foundations/PY-FND-060-control-flow-and-structural-pattern-matching/tests -v
```

## 7. Prediction

```text
loop break: result=found:2; events=visit:-1 → continue:-1 → visit:2 → break:2 → after-loop
loop exhaustion: result=not-found; events=visit:-1 → continue:-1 → visit:2 → body-tail:2 → visit:3 → body-tail:3 → loop-else → after-loop
guarded match: result=normal:job-7; events=subject → guard:urgent=False → guard:valid=True → case:normal
unmatched subject: result=unsupported; events=subject → case:fallback
binding after case: job-8
```

## 8. Observed output

```text
loop break: result=found:2; events=visit:-1 → continue:-1 → visit:2 → break:2 → after-loop
loop exhaustion: result=not-found; events=visit:-1 → continue:-1 → visit:2 → body-tail:2 → visit:3 → body-tail:3 → loop-else → after-loop
guarded match: result=normal:job-7; events=subject → guard:urgent=False → guard:valid=True → case:normal
unmatched subject: result=unsupported; events=subject → case:fallback
binding after case: job-8
```

The prediction and observation matched. No output was edited to create that match. The focused suite also ran 14 tests successfully on the recorded runtime.

## 9. Interpretation

1. `visit:-1` was immediately followed by `continue:-1`; no body-tail event for `-1` appeared. This directly shows the skipped suffix of that cycle.
2. The found path recorded `break:2` and then `after-loop`, with no `loop-else`. This distinguishes a deliberate break from natural termination.
3. The miss path visited all three items, recorded both non-negative body tails, then `loop-else` and `after-loop`. Body execution did not prevent loop `else`; only `break` would have done so.
4. Each match trace contained one `subject` label even though the guarded trace attempted two case blocks. This is consistent with the language rule that the subject expression is evaluated to obtain one subject value before case attempts.
5. The guarded trace recorded the urgent guard as false, then the valid guard as true, then the normal suite. Pattern success did not select a suite until its guard also succeeded.
6. The unmatched subject recorded no guard label. Guards were skipped because their associated patterns failed.
7. `job-8` was read after the selected case suite, showing that a successful capture is not scoped to that suite.
8. The run does not reveal or constrain internal pattern operations, failed partial bindings, cache behavior, bytecode, or performance.

## 10. Visual interpretation

```text
loop input -1                         match ("job", "job-7", 5)
     │                                             │
     v                                             v
  visit:-1                                      subject
     │                                             │
 continue:-1 ──X──> body-tail                  urgent pattern succeeds
     │                                             │
     v                                        guard false
 next item                                         │
                                                   v
loop input 2                                  valid pattern succeeds
     │                                             │
     v                                        guard true
  visit:2                                          │
     │                                             v
  break:2 ──X──> loop-else                    normal case
     │
     v
 after-loop

X = edge deliberately not taken
```

### How to read this visual

Read each column downward. On the left, `continue` and `break` each cross out a different edge. On the right, one subject value proceeds through two successful structural patterns because the first guard fails.

### Key insight

Control transfers are defined by their destinations: `continue` skips a body suffix, `break` skips loop `else`, pattern failure skips a guard, and guard failure advances to the next case.

### Simplification or limitation

This is a language-level event trace for fixed inputs. Pattern boxes summarize successful recognition but do not display element checks, `isinstance`, attribute access, comparison operations, or implementation caching.

## 11. Language and implementation conclusion

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| `continue` skipped the remaining body and allowed a later cycle. | Language guarantee plus observation | Documented for Python 3.14.7; observed on CPython 3.14.4 | Exact labels belong to this artifact; the transfer destination is portable. |
| `break` exited the nearest loop and skipped its `else`. | Language guarantee plus observation | Python/CPython 3.14.4 | No nested loop was used in this experiment. |
| Iterator exhaustion reached loop `else` after several body executions. | Language guarantee plus observation | Python/CPython 3.14.4 | Loop `else` does not imply zero iterations. |
| One match subject expression supplied the value for ordered case attempts. | Language guarantee plus observation | Structural matching since Python 3.10; CPython 3.14.4 observation | Do not infer the count of internal pattern operations. |
| A false guard advanced to a later case; failed patterns skipped guards. | Language guarantee plus observation | Python/CPython 3.14.4 | Guard side effects and exceptions would remain observable in order. |
| A successful capture was readable after its case suite. | Language scope guarantee plus observation | Python/CPython 3.14.4 | No claim is made about partial bindings from a failed pattern. |
| Exact trace formatting and test execution are artifact properties. | Tooling observation | CPython 3.14.4 | Reproductions should compare semantic order and values, not runtime speed. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular GIL-enabled build was executed.
- Python 3.14.7 and 3.11.15 documentation was audited, but neither maintenance release was the runtime used.
- The Python 3.11 compatibility claim is source-level and documentation-backed; it was not reproduced on a 3.11 runtime here.
- Only one `for` loop and tuple-based guarded patterns are traced; no `while`, nested loop, mapping, class-attribute, OR, AS, exception, `return`, `finally`, generator, or asynchronous path is instrumented.
- Event logging is itself a deterministic side effect but does not change the fixed decisions.
- A single successful capture is observed; failed partial bindings are deliberately not inspected because the language leaves them unspecified.
- Pattern internals may invoke or cache operations not represented by these labels.
- This is not a benchmark and supports no latency, allocation, specialization, or optimization claim.

## 13. Follow-up

- Add a separately classified `while` trace whose first test is false and whose `continue` path still reaches natural termination.
- Trace nested-loop ownership with independent inner and outer `else` suites.
- Use controlled custom mapping and class subjects to expose public `get()` and attribute-access effects without assuming internal lookup counts.
- Reproduce the same semantic assertions on an actual Python 3.11 runtime and append, rather than replace, the version-labelled observation.
- Move bytecode or specialization questions to the owning CPython units instead of expanding this D2 language experiment.

## 14. Authoritative sources

1. [Python 3.14.7 Language Reference — `while`, `for`, and `match`](https://docs.python.org/3.14/reference/compound_stmts.html), accessed 2026-08-29.
2. [Python 3.14.7 Language Reference — `break` and `continue`](https://docs.python.org/3.14/reference/simple_stmts.html#the-break-statement), accessed 2026-08-29.
3. [PEP 634 — Structural Pattern Matching: Specification](https://peps.python.org/pep-0634/), accessed 2026-08-29.
4. [Python 3.11.15 Language Reference — the `match` statement](https://docs.python.org/3.11/reference/compound_stmts.html#the-match-statement), accessed 2026-08-29.
