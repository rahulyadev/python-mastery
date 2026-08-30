# Practice — PY-BLT-050 Dictionaries and mapping behaviour

| Field | Value |
|---|---|
| Unit note | [PY-BLT-050](../README.md) |
| Curriculum | [CURRICULUM.md](../../../../CURRICULUM.md#py-blt-050) |
| Topic branch | `topic/PY-BLT-050` |
| Evidence target | E+C+D; optional X |
| Attempt required before solution | Yes |
| Test command | Learner tests do not exist yet; add a command with the first attempt |
| Status | Not attempted |

## Practice rules

1. Record a prediction or design before execution.
2. Preserve the original attempt and subsequent corrections in separate revisions.
3. Ask for one progressive hint at a time. No hints or comparison solutions are prewritten.
4. Passing tests is insufficient if the reasoning relies on a false assumption.
5. The unit's authored tests validate teaching examples, not these exercises.
6. Later learner changes stay local until another explicit publication choice.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Files | Status |
|---|---|---:|---|---|---|
| `PY-BLT-050-P01` | Predict | 2 | Separate key equivalence, order, and saved observations | Inline prompt | Not attempted |
| `PY-BLT-050-P02` | Implement | 3 | Build an index with an explicit duplicate policy | Create attempt and tests after starting | Not attempted |
| `PY-BLT-050-P03` | Debug | 3 | Preserve records in a reverse index | Inline broken example | Not attempted |
| `PY-BLT-050-P04` | Implement / Review | 4 | Report mapping changes without losing absence information | Create attempt and tests after starting | Not attempted |
| `PY-BLT-050-P05` | Design / Experiment | 4 | Separate key identity, equality work, and lookup cost | Create a distinct experiment attempt | Not attempted |

<a id="py-blt-050-p01"></a>
## PY-BLT-050-P01 — Follow the bindings

### Problem

Without execution, predict each printed line. Explain which writes create entries and which replace values.

```python
index = {True: "enabled", 2: "two"}
live = index.keys()
saved = tuple(index.items())
index[1.0] = "changed"
del index[2]
index[False] = "disabled"
index[2] = "returned"
print(len(index))
print(list(index.items()))
print(list(live))
print(saved)
```

### Learning evidence

E+D: connect equality and hashing with one-entry replacement; distinguish current order from a saved selection.

### Constraints and examples

Do not execute until the prediction is recorded. Treat all values here as immutable strings. For every line, explain the causal step rather than just writing the output.

### Required edge cases

- Replace the floating key with a distinct string key and predict what changes.
- Compare the final dict with one constructed in a different order but containing the same pairs.
- Explain which aspects concern the mapping contract and which would need care with pathological custom keys.

### Acceptance criteria

- [ ] The original prediction and reasoning are preserved.
- [ ] Every print is explained by a specific state transition.
- [ ] Actual execution is recorded only after the attempt.

<a id="py-blt-050-p02"></a>
## PY-BLT-050-P02 — Build a strict job index

### Problem

Implement `index_jobs(rows)`. Input is a possibly one-pass iterable of mappings with `id` and `status` fields. Return a new dict mapping each job ID to its status, in encounter order. Reject duplicate IDs with `ValueError`, even if their statuses agree. Never silently accept the last duplicate.

### Learning evidence

C: choose a domain policy that ordinary dict construction does not enforce; handle a single-pass input without modifying its records.

### Constraints

- An ID must be a nonempty string; treat it as case-sensitive and do not normalize it.
- Status must be exactly one of the strings `queued`, `running`, or `done`.
- Missing or invalid required fields raise `ValueError`; ignore extra fields.
- Do not modify input records. No partial result may be returned on failure.
- An error need not undo consumption of an input iterator.
- Avoid frameworks and unnecessary classes.

### Examples

```text
Input rows:
  {'id': 'job-c', 'status': 'queued'}
  {'id': 'job-a', 'status': 'done', 'extra': 9}

Required result:
  {'job-c': 'queued', 'job-a': 'done'}

Another row for 'job-c' must raise ValueError.
```

### Required edge cases

Empty input; a generator input; a repeated ID; a boolean ID; an empty ID; absent fields; an invalid status; and input records checked for changes after the call.

### Acceptance criteria

- [ ] Tests cover the contract and every required boundary.
- [ ] A duplicate never silently replaces a previous record.
- [ ] The learner explains expected time and extra-space cost.
- [ ] The implementation does not depend on visiting the input twice.

<a id="py-blt-050-p03"></a>
## PY-BLT-050-P03 — A reverse index loses information

### Problem

An engineer wants every route owned by each team. This version loses information:

```python
routes = [
    {"route": "/health", "team": "ops"},
    {"route": "/jobs", "team": "batch"},
    {"route": "/metrics", "team": "ops"},
]
by_team = {row["team"]: row["route"] for row in routes}
print(by_team)
```

Predict the printed result and identify the first incorrect assumption. Then implement a replacement which maps each team to a list of all its routes. Preserve team encounter order and route encounter order, including repeated route rows.

### Learning evidence

D+C: distinguish “unique key” from “unique value,” preserve one-to-many relationships, and verify separate ownership of each team's result list.

### Constraints and examples

All input fields are present strings for this exercise. Each input row contributes exactly one route occurrence. Different teams must not share a result list, and the input must not be modified. Do not use the fixed example's team names inside the implementation.

### Required edge cases

No rows; one team; interleaved teams; a repeated route row; and appending to one result list without changing another team's list.

### Acceptance criteria

- [ ] The original wrong assumption is recorded before a correction.
- [ ] Tests prove that every occurrence survives.
- [ ] An ownership check rules out accidental sharing across teams.
- [ ] No corrected code or test result is claimed before an actual attempt.

<a id="py-blt-050-p04"></a>
## PY-BLT-050-P04 — Report changes precisely

### Problem

Implement `diff_settings(before, after)` for stable mappings with string keys and values restricted to `None`, `bool`, `int`, or `str`. Return a dict with three lists:

- `added`: `(key, new_value)` pairs in `after` order.
- `removed`: `(key, old_value)` pairs in `before` order.
- `changed`: `(key, old_value, new_value)` triples in `before` order.

For keys present on both sides, ordinary Python `==` defines an unchanged value. Merely changing insertion order is not a value change. Neither input may be modified.

### Learning evidence

C+D: keep absence separate from legitimate values, and give a report an explicit ordering contract.

### Constraints and examples

```text
Before: {'quota': None, 'enabled': False}
After:  {'enabled': False, 'label': ''}

Required behaviour:
  Report quota as removed with its stored None value.
  Report label as added with its stored empty string.
  Do not report enabled as changed.
```

Do not sort the inputs. Do not rewrite the equality policy to require equal types. State how that policy treats `0` and `False`.

### Required edge cases

Empty mappings; no changes; reorder-only changes; absent versus `None`; `None` versus a present integer; zero versus `False`; and changes spread across all three categories.

### Acceptance criteria

- [ ] Tests verify category membership and list order independently.
- [ ] Stored falsey values are not treated as missing.
- [ ] The result is new and the inputs are unchanged.
- [ ] Expected cost and the stable-input assumption are explained.

<a id="py-blt-050-p05"></a>
## PY-BLT-050-P05 — What does the lookup counter measure?

### Problem

Design a small extension to [EXP-02](../experiments/EXP-02-collisions-and-lookup-work/README.md). Compare a lookup using the exact stored key object with a lookup using a fresh, equal key. Also try a missing key at one input size not already recorded in that experiment.

### Learning evidence

E+X: make a prediction, isolate a variable, and distinguish equality-method counts from internal probes and elapsed time.

### Constraints and examples

Record a prediction before changing or running the probe. Keep the original experiment intact. State the interpreter, version, command, input size, and counter-reset point. No timing claim is required. A zero equality count must not be described as “no lookup work.”

### Required edge cases

A hit using the stored object; a hit using an equal new object; a miss; and both distinct-hash and deliberately colliding keys. If another interpreter is unavailable, record that limitation rather than claiming portability was tested.

### Acceptance criteria

- [ ] Hypothesis and actual output are recorded separately.
- [ ] Counter effects are distinguished from table internals.
- [ ] An unexpected result is investigated rather than edited away.
- [ ] The explanation identifies at least one limit of the experiment.

## Prediction before execution

For each started exercise, add its full exercise ID, expected result/design, reasoning, and uncertainty. No learner prediction has been recorded yet.

## Learner attempt

Create attempt files only when starting. Record the full exercise ID, file link, original reasoning, actual test command, and observed result. No learner code or test execution exists yet.

## Progressive hints

None supplied. Request one hint at a time after an attempt.

## Review

After an attempt, record what is correct, the first incorrect assumption or missing step, the smallest revealing edge case, and one targeted next action. No learner weakness has been inferred from the prepared material.

## Test evidence

Not yet available for these exercises. The 28 authored unit tests are artifact verification and do not close practice.

## Closure

Add only after the learner closes an exercise: the final learner solution, optional comparison solution, explained trade-offs, remaining weakness, and an evidence link. No exercise is closed.
