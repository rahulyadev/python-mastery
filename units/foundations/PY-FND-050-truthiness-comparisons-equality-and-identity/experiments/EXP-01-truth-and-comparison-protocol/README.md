# EXP-01 — Truth and comparison protocol trace

| Field | Value |
|---|---|
| Owning unit | [`PY-FND-050`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-fnd-050) |
| Topic branch | `topic/PY-FND-050` |
| Precise question | Which truth hook, operand expression, and rich-comparison path actually runs when truth testing, chained comparisons, equality fallback, identity, and sentinels interact? |
| Classification | Python language and data-model guarantees tested through a CPython runtime observation |
| Status | Reproduced |
| Risk | None; deterministic standard-library-only execution |

## 1. Why an experiment is necessary

The rules are concise but hide intermediate decisions. `bool(obj)` does not reveal whether `__bool__`, `__len__`, or the default was used. A final chained-comparison result does not reveal that the middle expression ran once or that a rightmost expression was skipped. `left == right` hides `NotImplemented` fallback, and a defaulted lookup can silently erase present falsy values.

An ordered event trace makes those hidden transitions observable without using bytecode, object addresses, timing, or implementation internals. The same run also captures the Python 3.14 behavior of truth-testing `NotImplemented` so that the 3.11 compatibility boundary is explicit.

## 2. Hypothesis

Before execution:

> Python will prefer `__bool__` over `__len__`, use `__len__` only as a fallback, and treat a plain object as true. Invalid hook results will raise. A unique identity sentinel will preserve `0`, `None`, and an empty string as present values. A successful comparison chain will evaluate its middle expression once and reuse it, while a failed first comparison will skip the rightmost expression. Distinct domain objects can compare equal without being identical, direct unsupported equality can return `NotImplemented` while the `==` operator completes with `False`, and one stored NaN can be identical but unequal to itself. On Python 3.14, `bool(NotImplemented)` will raise `TypeError`.

Alternative outcomes requiring investigation:

- `__len__` runs after a false `__bool__` result;
- a plain object is false without either hook;
- an invalid hook value is coerced instead of rejected;
- a present falsy mapping value is replaced by the fallback;
- the middle expression or comparison runs twice;
- the rightmost chain expression records an event after the first comparison fails;
- `is` follows custom equality;
- direct `__eq__` and `==` expose the same unsupported result;
- NaN identity forces NaN equality;
- `NotImplemented` still evaluates as true on the active Python 3.14 runtime.

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

The repository's canonical documentation baseline is Python 3.14.7. Execution occurred on the available CPython 3.14.4 runtime, so every observation is labelled accordingly. The focused test is version-aware for the documented Python 3.11 `NotImplemented` behavior.

## 4. Controls and variables

### Controlled

- Every observable hook or operand producer appends a fixed label to an in-memory list.
- Integer payloads, domain keys, mapping contents, and sentinel construction are fixed.
- Each trace starts with fresh state.
- The sentinel remains private and is never serialized or copied.
- No clock, randomness, filesystem data, network, subprocess, thread, signal, or external service is used.
- Formatting is deterministic and covered by a focused regression test.

### Changed

- Truth implementation: both hooks, length only, neither hook, invalid `__bool__`, and negative `__len__`.
- Mapping state: absent, present zero, present `None`, and present empty string.
- Chain result: true first comparison versus false first comparison.
- Reference relation: distinct equal objects versus one alias.
- Equality support: accepted domain type versus unsupported string type.
- Numeric value: ordinary domain key versus NaN.
- Runtime version boundary: active interpreter's handling of `bool(NotImplemented)`.

### Measured

- Final Boolean or payload values.
- Exact ordered event labels.
- Hook and operand labels absent from the path.
- Exception type for invalid truth hooks.
- Equality and identity results for distinct objects and aliases.
- Direct rich-method sentinel result versus operator result.
- Active major/minor version and `NotImplemented` truth outcome.

## 5. Files

```text
experiments/EXP-01-truth-and-comparison-protocol/
├── README.md
└── protocol_trace.py
```

The runnable source is [`protocol_trace.py`](protocol_trace.py). It imports the same example modules exercised by the focused tests.

## 6. Reproduction command

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python units/foundations/PY-FND-050-truthiness-comparisons-equality-and-identity/experiments/EXP-01-truth-and-comparison-protocol/protocol_trace.py
```

Focused regression command:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s units/foundations/PY-FND-050-truthiness-comparisons-equality-and-identity/tests -v
```

## 7. Prediction

```text
truth bool-first: value=False; events=__bool__
truth len-only: value=True; events=__len__
truth default: value=True; events=none
invalid truth hooks: errors=('TypeError', 'ValueError')
sentinel values: ('fallback', 0, None, '')
chain success: result=True; events=evaluate:low → evaluate:middle → compare:low<middle → evaluate:high → compare:middle<=high
chain short-circuit: result=False; events=evaluate:left → evaluate:middle → compare:left<middle
equality and identity: distinct=(equal=True, identical=False); alias=(equal=True, identical=True); unsupported-equal=False; direct-unsupported-is-NotImplemented=True
NaN: equal-to-self=False; unequal-to-self=True; identical-to-self=True
NotImplemented truth: python=3.14; outcome=raises TypeError; warning=none
```

## 8. Observed output

```text
truth bool-first: value=False; events=__bool__
truth len-only: value=True; events=__len__
truth default: value=True; events=none
invalid truth hooks: errors=('TypeError', 'ValueError')
sentinel values: ('fallback', 0, None, '')
chain success: result=True; events=evaluate:low → evaluate:middle → compare:low<middle → evaluate:high → compare:middle<=high
chain short-circuit: result=False; events=evaluate:left → evaluate:middle → compare:left<middle
equality and identity: distinct=(equal=True, identical=False); alias=(equal=True, identical=True); unsupported-equal=False; direct-unsupported-is-NotImplemented=True
NaN: equal-to-self=False; unequal-to-self=True; identical-to-self=True
NotImplemented truth: python=3.14; outcome=raises TypeError; warning=none
```

The prediction and observation matched. No output was edited to create that match.

The focused regression suite also ran 10 tests successfully on the recorded runtime.

## 9. Interpretation

1. Only `__bool__` appeared for the class defining both hooks. Its false result was final; `__len__` did not receive a second vote.
2. The length-only class recorded `__len__`, and a plain object was true without an event. This directly exposes the three-step resolution order.
3. The deliberately invalid hooks raised `TypeError` and `ValueError`; Python did not silently coerce their results into valid truth values.
4. Only the absent setting selected `"fallback"`. Zero, `None`, and the empty string remained present payloads because identity with the private sentinel decided absence.
5. The successful chain recorded `evaluate:middle` exactly once and then used the `middle` probe as the left operand of the second comparison.
6. The failed chain contained no `evaluate:right-skipped` event, showing that comparison chaining short-circuits the unevaluated suffix.
7. Two distinct `ValueToken` objects were equal but not identical, while an alias was both. The direct unsupported `__eq__` result was `NotImplemented`; the `==` operator then completed its protocol with `False`.
8. One stored NaN was identical to itself but not equal to itself. Identity did not override the numeric value protocol.
9. CPython 3.14.4 raised `TypeError` for `bool(NotImplemented)`, matching the audited Python 3.14.7 documentation. This run does not observe Python 3.11; its behavior is sourced from the 3.11.15 documentation and covered by a version-conditional test branch.

## 10. Visual interpretation

```text
                           one trace, four decision boundaries

truth object ----> __bool__? ----> __len__? ----> true default
                      |
                      `---- first available hook decides or raises

low < middle <= high
 |       |        |
eval    eval      eval only if first comparison is truthy
          `------ same middle object reused ------^

left == right ----> rich comparison / fallback ----> value relation
left is right --------------------------------------> same-object relation

lookup value is MISSING? ---- yes ---> fallback
             `-------------- no ----> preserve payload, even when falsy
```

### How to read this visual

Read each row from left to right. The truth row stops at one hook, the chain row reuses one middle object and may omit the high operand, the comparison rows enter different protocols, and the lookup row tests presence before any payload truth interpretation.

### Key insight

Correct reasoning begins by naming the decision being requested—truth, value relation, sameness, or presence—then tracing only that protocol's demanded work.

### Simplification or limitation

The visual combines language-level models; it is not interpreter control flow. It omits special-method lookup mechanics, subclass priority, non-Boolean comparison objects, exceptions from successful hooks, membership, serialization, concurrency, and exact CPython slots.

## 11. Language and implementation conclusion

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| `__bool__` took priority, `__len__` served as fallback, and no hook meant true. | Language/data-model guarantee plus observation | Documented for Python 3.14.7; observed on CPython 3.14.4 | The exact event labels belong to this artifact; resolution order is portable. |
| Invalid `__bool__` and `__len__` results raised instead of coercing. | Language/data-model contract plus observation | CPython 3.14.4 | Other conforming implementations must preserve the public result constraints, not exact messages. |
| A private identity sentinel preserved all present falsy payloads. | Language identity semantics plus API design observation | Python/CPython 3.14.4 | The sentinel must remain the same object within the owning boundary. |
| The middle chain expression ran once and the right suffix was skipped after failure. | Language guarantee plus observation | Python/CPython 3.14.4 | No bytecode shape or optimizer behavior is inferred. |
| Distinct objects were equal without identity; direct unsupported equality returned `NotImplemented` while `==` returned `False`. | Language/data-model guarantee plus observation | Python/CPython 3.14.4 | Another cooperating right type could accept the comparison during fallback. |
| A stored NaN was identical but unequal to itself. | Numeric value contract plus observation | CPython 3.14.4 | Do not generalize reflexivity from identity alone. |
| Truth-testing `NotImplemented` raised `TypeError`. | Version-dependent language/library behavior | CPython 3.14.4 | Python 3.11 returns true with `DeprecationWarning`; code should not truth-test it on either version. |
| Exact trace text and test execution are properties of this artifact. | Tooling observation | CPython 3.14.4 | Reproductions should compare semantic values and order, not runtime speed. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular GIL-enabled build was executed.
- Python 3.14.7 and 3.11.15 documentation was audited, but neither maintenance release was the runtime used.
- The Python 3.11 `NotImplemented` branch was not executed in this run; it is documentation-backed and version-conditional in tests.
- Only `__bool__`, `__len__`, `__lt__`, `__le__`, and `__eq__` are instrumented.
- No subclass-priority, reflected ordering, non-Boolean comparison result, membership, hashing, or mutable equality case is executed.
- The sentinel remains in one process and module; no copy, pickle, JSON, process, or network boundary is tested.
- Event logging is itself a deterministic side effect but does not change payload truth or comparison values.
- The trace records language-visible calls, not interpreter frames, slots, bytecode, caches, or machine instructions.
- No concurrency or mutation occurs between the two comparisons in a chain.
- This is not a benchmark and supports no latency, allocation, or optimization claim.

## 13. Follow-up

- Add a comparison-result object with its own traced `__bool__` and locate that event inside a chain.
- Add two cooperating operand types to expose reflected comparison priority, then move the full contract to `PY-BLT-080` or `PY-OBJ-040`.
- Run the version-aware `NotImplemented` case on an actual CPython 3.11 runtime and append a separately labelled reproduction rather than replacing this output.
- Design a named public sentinel with stable representation and pickle behavior only in a unit that owns library API design.
- Extend the lookup example to a typed result object when missing, explicit null, invalid, and inherited states all need separate representation.

## 14. Authoritative sources

1. [Python 3.14.7 Built-in Types — Truth Value Testing and Comparisons](https://docs.python.org/3.14/library/stdtypes.html#truth-value-testing), accessed 2026-08-29.
2. [Python 3.14.7 Language Reference — Comparisons and identity comparisons](https://docs.python.org/3.14/reference/expressions.html#comparisons), accessed 2026-08-29.
3. [Python 3.14.7 Data Model — Rich comparison methods, `object.__bool__`, and `object.__len__`](https://docs.python.org/3.14/reference/datamodel.html#object.__eq__), accessed 2026-08-29.
4. [Python 3.14.7 Built-in Constants — `None` and `NotImplemented`](https://docs.python.org/3.14/library/constants.html), accessed 2026-08-29.
5. [Python 3.11.15 Built-in Constants — `NotImplemented`](https://docs.python.org/3.11/library/constants.html#NotImplemented), accessed 2026-08-29.
