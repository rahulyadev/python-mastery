# Practice — PY-BLT-060 Sets and frozensets

| Field | Value |
|---|---|
| Unit note | [PY-BLT-060](../README.md) |
| Curriculum | [CURRICULUM.md](../../../../CURRICULUM.md#py-blt-060) |
| Topic branch | `topic/PY-BLT-060` |
| Evidence target | E+C+D |
| Attempt required before solution | Yes |
| Test command | Learner records the command for their own tests after an attempt |
| Status | Not attempted |

## Practice rules

1. Record your prediction or design before execution.
2. Preserve the original attempt when revising it.
3. Request one progressive hint at a time; no hints or solutions are prewritten here.
4. Passing tests do not replace an explanation of why the design works.
5. Comparison solutions appear only after an exercise is closed.
6. Later practice changes remain local until explicitly authorized for publication.

The tests in the unit's `tests/` directory verify author examples and visual evidence. They do not grade or solve these exercises. Write your own tests from each contract below; runnable attempt files are created only when you attempt the exercise.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Files | Status |
|---|---|---:|---|---|---|
| `PY-BLT-060-P01` | Predict / Explain | 2 | Distinguish equivalence, membership, and subset relations | Inline prompt and attempt record | Not attempted |
| `PY-BLT-060-P02` | Implement | 3 | Deduplicate without losing arrival order | Learner creates attempt and tests | Not attempted |
| `PY-BLT-060-P03` | Debug | 3 | Repair a membership-changing traversal | Inline broken example; learner creates repair | Not attempted |
| `PY-BLT-060-P04` | Implement / Design | 3 | Group records by unordered capability membership | Learner creates attempt and tests | Not attempted |
| `PY-BLT-060-P05` | Review | 4 | Audit a proposed durable cache key | Written review here | Not attempted |

## Shared acceptance criteria

- [ ] Original prediction/design and attempt are preserved.
- [ ] Tests exercise ordinary inputs and required edge cases.
- [ ] Observed results and the actual test command are recorded.
- [ ] The first incorrect assumption, if any, is identified precisely.
- [ ] Correctness, ownership, and complexity are explained.
- [ ] No unrelated abstraction or infrastructure was added.

<a id="py-blt-060-p01"></a>
## PY-BLT-060-P01 — Predict without running

### Problem

For each line, predict the printed result or exception class. Explain each prediction. Treat statements within each block as sequential; treat the final hash call separately so an exception cannot hide earlier observations.

```python
members = {0, False, 0.0, "0"}
print(len(members), "0" in members)
print({"north"} < {"south"})
print(frozenset({"north"}) == {"north"})
print({"north"}.issubset(["north", "south"]))
hash(({"north"},))
```

### Learning evidence and constraints

Distinguish equal members from equal types, containment from subset relationships, and outer immutability from hashability. Do not rely on the printed representation order of any set.

### Required edge cases

Repeat your reasoning for both operands empty in a subset comparison, and for a tuple containing a frozenset instead of a set.

### Prediction before execution

No learner prediction recorded. Record expected result, reasoning, and uncertainty per line.

### Learner attempt, test evidence, and review

Not attempted. Preserve your initial predictions before recording actual output. No hints requested; no review or closure evidence yet.

<a id="py-blt-060-p02"></a>
## PY-BLT-060-P02 — Preserve the first arrival

### Problem

Implement `unique_in_order(values: list[str]) -> list[str]`. Return each distinct string exactly once, in the order of its first occurrence. Do not modify the input.

### Learning evidence

Explain why the representation used for membership need not be the representation returned to the caller.

### Constraints

- Python 3.11-compatible standard library only.
- Aim for expected linear work in the number of inputs under ordinary hashing assumptions.
- Case and whitespace are significant. Empty strings are valid values.

### Examples

```text
Input: ['west', 'east', 'west', 'north', 'east']
Expected observable behaviour: ['west', 'east', 'north']; input unchanged.
```

### Required edge cases

Empty input, all repeats, all distinct values, empty strings, case differences, and two successive calls with unrelated inputs.

### Acceptance criteria

Meet the shared criteria, explain retained state and extra memory, and avoid relying on set traversal order.

### Prediction before execution

No design recorded. State what must remain true after processing each input value.

### Learner attempt, test evidence, and review

Not attempted. Record the original attempt file, reasoning, test command, actual results, and revision history. No hints requested; no solution or closure evidence yet.

<a id="py-blt-060-p03"></a>
## PY-BLT-060-P03 — A removal pass with a hidden assumption

### Problem

This function is intended to remove retired names from the caller-owned `live` set **in place**, preserving its identity and all non-retired members. Diagnose and repair it.

```python
def remove_retired(live, retired):
    for name in live:
        if name in retired:
            live.remove(name)
    return live
```

### Learning evidence

Identify the first false assumption before proposing replacement code. Explain what an alias to `live` should observe and whether your repair changes that contract.

### Constraints

Both arguments are built-in sets of strings. They may be the same object. Preserve the attempt and avoid assuming a traversal order or that every unsafe mutation must raise an exception.

### Examples

```text
Input membership: live={'north', 'south'}, retired={'south'}
Expected observable behaviour: live has only 'north'; its identity is unchanged.
```

### Required edge cases

Empty input, no overlap, all members retired, repeated calls, an external alias to `live`, and `live is retired`.

### Prediction before execution

No prediction recorded. State what the original loop might observe when a member is deleted.

### Learner attempt, test evidence, and review

Not attempted. First record a failing case and the exact result, then preserve the original function while adding your repair. No hints requested; the correction is withheld.

<a id="py-blt-060-p04"></a>
## PY-BLT-060-P04 — Group deployments by capabilities

### Problem

Implement `group_by_capabilities(records)` for a finite list of `(deployment_name, capabilities)` pairs. Each deployment name and capability is a string; capabilities is a list of strings. Return a dictionary whose keys represent unordered capability groups and whose values are lists of deployment names in input order.

### Learning evidence

Choose a hashable group representation, explain its equivalence rule, and state which information is intentionally discarded.

### Constraints

Repeated capabilities do not change the group. Repeated deployment records remain repeated in their group's output list. Empty capability groups are valid. Inputs must not be modified; validation of other input types is outside this exercise.

### Examples

```text
Input: ('one', ['read', 'trace']), ('two', ['trace', 'read', 'read']), ('three', [])
Expected observable behaviour: one group lists ['one', 'two']; a separate empty group lists ['three'].
```

### Required edge cases

No records, one empty group, reordered capabilities, repeated capabilities, repeated deployment records, and groups differing by exactly one capability.

### Acceptance criteria

Meet the shared criteria. Test output membership and group value order separately. Explain expected cost in terms of the total capabilities consumed, not only the number of records.

### Prediction before execution

No design recorded. Explain your planned key and why two differently ordered capability lists should share it.

### Learner attempt, test evidence, and review

Not attempted. Record your implementation and tests only after making the prediction. No hints requested; no final comparison solution yet.

<a id="py-blt-060-p05"></a>
## PY-BLT-060-P05 — Review the durable key proposal

### Problem

A service proposes storing responses under `hash(frozenset(requested_fields))`. The numeric key is persisted to disk and reused after worker restarts. Different field groups must never return each other's response. Order and repeated fields are intentionally irrelevant.

### Learning evidence

Write a review that distinguishes the group equivalence requirement from the identifier requirement. Propose a representation or protocol, not a complete cache service.

### Constraints and required edge cases

Consider empty fields, reordered fields, repeated fields, distinct groups, process restarts, and schema/version changes. State where validation belongs and what your design does not guarantee.

### Acceptance criteria

Support the review with one focused test or bounded experiment of your own. Label observations separately from Python guarantees. Avoid claiming that one successful run proves collision freedom or cross-process stability.

### Prediction before execution

No prediction recorded. State the smallest claim you want to test and what would falsify it.

### Learner attempt, test evidence, and review

Not attempted. Record the proposal review, actual command/output, and remaining uncertainty. No hints requested; no review or closure evidence yet.
