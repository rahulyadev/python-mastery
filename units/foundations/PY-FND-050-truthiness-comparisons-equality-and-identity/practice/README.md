# PY-FND-050 practice — Truthiness, comparisons, equality, and identity

[Unit note](../README.md) · [Curriculum entry](../../../../CURRICULUM.md#py-fnd-050) · [Progress](../../../../PROGRESS.md)

These exercises begin unsolved. Preserve the first prediction, trace, code, test output, and correction reasoning before revising an attempt. Ask for one progressive hint at a time; complete solutions and prewritten hints do not belong in this scaffold before an attempt.

## Practice protocol

For each exercise, separate these questions before calculating a final result:

1. **Domain states:** Which inputs are missing, present-`None`, present-falsy, present-truthy, invalid, or unsupported?
2. **Protocol entry:** Does the syntax request truth testing, value comparison, identity comparison, ordering, or membership?
3. **Dispatch and demand:** Which hook or comparison method can run, and which later expressions can be skipped?
4. **Observable result:** What value, Boolean, exception, event order, and call count should appear?
5. **Boundary claim:** Is the conclusion a language guarantee, a public-library contract, a version boundary, or one runtime observation?

Suggested evidence record:

```text
Exercise:
Date:
Python implementation and version:
Input-state partition:
Protocol requested:
Hook/dispatch trace:
Skipped expressions:
Identity graph when relevant:
Prediction:
Exact command:
Observed output:
First mismatch:
Corrected rule:
Tests:
Production implication:
Remaining weakness:
```

Do not erase a wrong answer after execution. The useful evidence is the first incorrect state distinction or transition and the rule used to correct it.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Status |
|---|---|---:|---|---|
| `PY-FND-050-P01` | Predict | 2/5 | Resolve truth hooks, defaults, and invalid outcomes | Not attempted |
| `PY-FND-050-P02` | Predict and trace | 3/5 | Prove at-most-once operands and chain short-circuiting | Not attempted |
| `PY-FND-050-P03` | Implement and test | 3/5 | Preserve every present falsy value behind one lookup boundary | Not attempted |
| `PY-FND-050-P04` | Debug | 3/5 | Diagnose a defaulting function that loses zero and `None` | Not attempted |
| `PY-FND-050-P05` | Review and design | 4/5 | Review a domain equality contract and identity misuse | Not attempted |

## PY-FND-050-P01 — Truth protocol ladder

**Type:** Predict

**Difficulty:** 2/5

**Evidence target:** Resolve `__bool__`, `__len__`, and true-by-default paths without treating truth as equality with `True`.

Do not run this program until the worksheet is complete:

```python
events: list[str] = []


class Both:
    def __bool__(self):
        events.append("Both.__bool__")
        return False

    def __len__(self):
        events.append("Both.__len__")
        return 4


class LengthOnly:
    def __init__(self, size: int) -> None:
        self.size = size

    def __len__(self):
        events.append(f"LengthOnly.__len__:{self.size}")
        return self.size


class Plain:
    pass


class BrokenBool:
    def __bool__(self):
        events.append("BrokenBool.__bool__")
        return 1


values = [Both(), LengthOnly(0), LengthOnly(2), Plain(), BrokenBool()]

for value in values:
    try:
        print(type(value).__name__, bool(value))
    except Exception as error:
        print(type(value).__name__, type(error).__name__)

print(events)
```

### Prediction worksheet

Before execution, provide:

- one truth-resolution tree shared by all five objects;
- the exact output line for every object;
- the final event list in order;
- the name of every method that does not run and why;
- the first violated protocol rule, if any;
- one sentence explaining why `Plain()` need not be equal to `True` to be truthy.

### Verification constraints

- Run only after the worksheet is timestamped or committed.
- If an answer differs, identify the first wrong branch in the resolution tree.
- Do not repair `BrokenBool` until the exception has been explained.
- Add a separate negative-length case only after reviewing the initial trace.

### Hint gate

If blocked, request `PY-FND-050-P01 Hint 1`. Ask for a later hint only after updating the decision tree.

## PY-FND-050-P02 — Chain with one middle

**Type:** Predict and trace

**Difficulty:** 3/5

**Evidence target:** Prove that a comparison chain evaluates each operand expression at most once and skips the right suffix after a falsy comparison.

Do not run this program until both timelines are complete:

```python
events: list[str] = []


class Probe:
    def __init__(self, label: str, value: int) -> None:
        self.label = label
        self.value = value

    def __lt__(self, other):
        events.append(f"compare:{self.label}<{other.label}")
        return self.value < other.value

    def __le__(self, other):
        events.append(f"compare:{self.label}<={other.label}")
        return self.value <= other.value


def make(label: str, value: int) -> Probe:
    events.append(f"evaluate:{label}")
    return Probe(label, value)


first = make("A", 1) < make("B", 5) <= make("C", 5)
events.append("separator")
second = make("D", 8) < make("E", 3) <= make("F", 10)

print(first, second)
print(events)
```

### Required reasoning

Record:

- a five-column timeline: source expression, evaluation event, comparison hook, retained value, and current decision;
- how many `Probe` objects are constructed for each chain;
- the exact event list, including the separator;
- which label is absent and which false result causes its absence;
- whether either chain compares its first and third probes directly;
- a conceptual `and` expansion that does not evaluate either middle expression twice.

### Counterexample extension

After the first execution, design one change that makes the first comparison hook return a custom object whose `__bool__` records another event. Predict where that event belongs before running it.

### Hint gate

If blocked, request `PY-FND-050-P02 Hint 1` and show the partial timeline.

## PY-FND-050-P03 — Preserve present values

**Type:** Implement and test

**Difficulty:** 3/5

**Evidence target:** Implement one lookup boundary where fallback depends only on absence and no valid falsy value is lost.

Create an attempt file only after writing the state table:

```text
practice/attempts/p03_present_values.py
```

### Contract

Implement:

```python
def get_option(options: Mapping[str, object], key: str, default: object) -> object:
    ...
```

Required behavior:

| Input state | Returned object |
|---|---|
| key absent | `default` |
| key present with `None` | that `None` object |
| key present with `False` | that `False` object |
| key present with `0` | that zero object |
| key present with `""` | that empty string |
| key present with `[]` | that exact list object |
| key present with a truthy value | that exact value object |

### Constraints

- Do not perform more than one mapping lookup on the normal path.
- Do not compare arbitrary payload values with the sentinel using `==`.
- Do not use a normal domain value as the missing marker.
- Do not copy a present value.
- Keep the marker private to the attempt module.
- Use only Python 3.11-compatible syntax and the standard library.

### Required tests

Write tests that:

- cover all seven table rows;
- prove identity preservation for the present list and one custom object;
- use a payload whose `__eq__` raises, proving lookup does not need payload equality;
- count mapping lookups with a small instrumented mapping;
- prove that a fresh marker object cannot impersonate the private marker.

### Acceptance criteria

- [ ] The state table was written before code.
- [ ] Every present falsy value is preserved.
- [ ] Identity is used only for the sentinel contract.
- [ ] Required deterministic tests pass.
- [ ] The learner explains why `None` is insufficient for this exact domain.
- [ ] The learner explains one boundary where a private `object()` sentinel would be insufficient.
- [ ] No unrelated abstraction was added.

### Hint gate

If blocked, request `PY-FND-050-P03 Hint 1` and include the current attempt plus failing test output.

## PY-FND-050-P04 — The disappearing zero

**Type:** Debug

**Difficulty:** 3/5

**Evidence target:** Identify the first collapsed domain state before changing a fallback expression.

```python
DEFAULT_LIMIT = 100


def resolve_limit(overrides: dict[str, int | None], key: str) -> int | None:
    value = overrides.get(key)
    if value:
        return value
    return DEFAULT_LIMIT
```

The required contract is:

| State | Meaning | Result |
|---|---|---|
| key absent | inherit service default | `100` |
| key present with `None` | explicitly disable the limit | `None` |
| key present with `0` | allow no requests | `0` |
| key present with a positive integer | use the override | that integer |

### Debugging sequence

1. Predict all four results without editing.
2. Name the first pair of domain states collapsed by the implementation.
3. Write the smallest deterministic test that proves that collapse.
4. Decide whether membership, a sentinel, or a richer result object best matches the stated contract.
5. Make one minimal correction in an attempt file.
6. Add a negative-integer case and state whether validation belongs inside this function or at another boundary.
7. Explain why replacing the body with `return overrides.get(key) or DEFAULT_LIMIT` preserves the bug.

### Review questions

- Would `if value is not None` satisfy the complete contract? Prove the answer from the table.
- How many lookups does the chosen repair perform?
- Can a custom mapping change the cost or effects of that decision?
- Which claim is about truthiness, and which is about the service's domain model?

### Hint gate

If blocked, request `PY-FND-050-P04 Hint 1` with the four predicted results.

## PY-FND-050-P05 — Review a domain key

**Type:** Review and design

**Difficulty:** 4/5

**Evidence target:** Review equality semantics, unsupported operands, identity misuse, ordering assumptions, and future hash requirements without implementing a full solution first.

```python
class DomainKey:
    def __init__(self, namespace: str, name: str) -> None:
        self.namespace = namespace
        self.name = name

    def __eq__(self, other):
        return (
            self.namespace.lower() == other.namespace.lower()
            and self.name == other.name
        )

    def __lt__(self, other):
        return self.name < other.name


def cache_hit(requested: DomainKey, stored: DomainKey) -> bool:
    return requested is stored
```

### Review brief

Do not rewrite the class first. Produce a review containing:

1. the intended value relation inferred from current code and every ambiguity that needs product/domain confirmation;
2. behavior for two distinct equal keys, one alias, an unrelated object, and a potential subclass;
3. the first exception raised by an unsupported right operand and why operator fallback cannot occur cleanly;
4. whether case normalization on only one field is reflexive, symmetric, and transitive for ordinary strings;
5. whether the ordering relation is consistent with equality and whether it is total, partial, or under-specified;
6. why the cache-hit function confuses value with identity;
7. what happens to hashability after defining equality and why dictionary-key design belongs in the review even though implementation belongs to `PY-BLT-080`;
8. one test matrix that separates equality, identity, ordering, unsupported types, and mutation risk;
9. the smallest safe change boundary for this unit, leaving full ordering/hash design for the owner unit.

### Constraints

- Do not call `__eq__` directly in behavioral tests of `==`.
- Do not use `id()` numbers as evidence.
- Do not assume CPython string interning.
- Do not generate missing ordering methods without first defining the desired order.
- Do not make instances hashable until equality-defining fields and mutation policy are explicit.

### Acceptance criteria

- [ ] Equality and identity claims are separated.
- [ ] Unsupported-type behavior and `NotImplemented` dispatch are addressed.
- [ ] Reflexivity, symmetry, transitivity, and equality/ordering consistency are reviewed.
- [ ] Hash implications are identified but not over-scoped.
- [ ] Tests include distinct equal objects and one alias.
- [ ] The proposed change is justified in domain language, not only syntax.

### Hint gate

If blocked, request `PY-FND-050-P05 Hint 1` and include the review written so far.

## Review and closure protocol

For each completed exercise, retain:

- the original attempt or prediction;
- the first failing assertion or incorrect event transition;
- the smallest counterexample that revealed it;
- the corrected rule in the learner's own words;
- actual command and output;
- relevant edge cases;
- a short production consequence;
- remaining uncertainty.

Passing tests do not prove understanding when the explanation confuses truth, equality, identity, or absence. Review the reasoning before marking an exercise closed. Only closed attempts with preserved evidence may support a later `PROGRESS.md` transition.

Focused command for the canonical examples and experiment:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s units/foundations/PY-FND-050-truthiness-comparisons-equality-and-identity/tests -v
```
