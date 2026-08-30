# Practice — PY-BLT-040 Lists, tuples, ranges, and sequence behaviour

| Field | Value |
|---|---|
| Unit note | [PY-BLT-040](../README.md) |
| Curriculum | [CURRICULUM.md](../../../../CURRICULUM.md#py-blt-040) |
| Topic branch | `topic/PY-BLT-040` |
| Evidence target | E+C+D+(X) |
| Attempt required before solution | Yes |
| Test command | Learner supplies focused commands after writing an attempt; artifact tests are not practice completion |
| Status | Not attempted |

## Practice rules

1. Work on one exercise at a time. Record the prediction or design before execution.
2. Preserve the first attempt and its reasoning; add corrections rather than replacing the history.
3. Ask for one progressive hint at a time. No hints or comparison solutions are prewritten here.
4. Record the command, runtime, actual result, and why each correction works.
5. Passing tests alone does not establish understanding.
6. Later practice changes remain local until a new explicit publication choice.

The examples and tests elsewhere in this unit verify teaching artifacts. They neither implement these exercise contracts nor contain their expected prediction output.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Files | Status |
|---|---|---:|---|---|---|
| `PY-BLT-040-P01` | Predict / Explain | 2 | Follow references across slicing and tuple conversion | Inline prompt; learner adds an attempt when ready | Not attempted |
| `PY-BLT-040-P02` | Implement / Test | 3 | Rotate a selected segment without changing the input | Learner creates implementation and tests | Not attempted |
| `PY-BLT-040-P03` | Debug | 3 | Repair ordering and ownership in a tail API | Inline broken code; preserve before correcting | Not attempted |
| `PY-BLT-040-P04` | Review / Design | 4 | Specify a meaningful snapshot boundary | Learner records design and counterexample | Not attempted |
| `PY-BLT-040-P05` | Experiment | 3 | Predict a new case before observing it | Learner creates a variant of one probe | Not attempted |

<a id="py-blt-040-p01"></a>

## PY-BLT-040-P01 — Predict before running

### Problem

Predict every printed value and identity relation. Draw the reference graph immediately before and after each mutation. Do not execute until your prediction is recorded.

```python
items = [["left"], ["middle"], ["right"]]
window = items[::2]
fixed = tuple(window)
window[0] = ["local"]
fixed[1].append("seen")
items[0].append("source")

print(items)
print(window)
print(fixed)
print(fixed[0] is items[0], window[0] is items[0])
```

### Learning evidence

Explain which containers were constructed and which children remain shared. Distinguish replacing `window[0]` from mutating the object referenced by `fixed[1]`.

### Constraints and examples

Use symbolic object labels, not invented memory addresses. The code above is the complete input; its output is intentionally withheld.

### Required edge cases

After the first attempt, repeat your reasoning for an empty source and for a source whose positions initially reference the same child. Do not assume printed equality proves identity.

### Acceptance criteria

- [ ] Prediction and graph were recorded before running.
- [ ] Each changed or unchanged value has a reference-based explanation.
- [ ] Actual output is preserved next to the original prediction.
- [ ] Any incorrect prediction is traced to its first mistaken step.

### Attempt and review

Not attempted. No test execution, hint, learner review, or closure is recorded.

<a id="py-blt-040-p02"></a>

## PY-BLT-040-P02 — Rotate one segment

### Problem

Implement `rotate_segment(values, start, stop, shift)` for a list of integers. Return a **new list** with the half-open segment from `start` to `stop` rotated by `shift` positions. Positive shifts rotate right; negative shifts rotate left. Keep the prefix and suffix unchanged.

### Learning evidence

Explain the selected region, how shifts relate to its length, why the input cannot be changed through the returned outer list, and the cost of the result.

### Constraints

- Use Python 3.11-compatible standard-library code; no third-party arrays or deque.
- `start`, `stop`, and `shift` must be plain integers, not booleans; reject other types with `TypeError`.
- Require `0 <= start <= stop <= len(values)`; reject invalid bounds with `ValueError` instead of silently clipping.
- Accept any integer shift, including shifts much larger than the segment.
- An empty segment leaves the values unchanged but still returns a new outer list.
- Keep the caller's list unchanged for valid and rejected requests.
- Do not add a class or a general sequence framework.

### Examples

```text
Input: values=[0, 1, 2, 3, 4], start=1, stop=4, shift=1
Expected observable behavior: result [0, 3, 1, 2, 4]; input unchanged.

Input: values=[0, 1, 2], start=1, stop=1, shift=100
Expected observable behavior: a distinct list with values [0, 1, 2].
```

These examples specify the API, not its implementation.

### Required edge cases

Empty input, empty segment, singleton segment, whole-list segment, zero shift, negative shift, exact multiples of segment length, very large shifts, invalid order of bounds, bounds outside the list, and wrong argument types.

### Acceptance criteria

- [ ] Write the design and invariants before code.
- [ ] Preserve the first implementation and its failures.
- [ ] Write and run meaningful tests for the contract and edge cases.
- [ ] Check both value equality and outer-container independence.
- [ ] Explain time and space complexity, including copies.
- [ ] Explain why the empty-segment case is safe.

### Attempt and review

Not attempted. Create code and tests only when beginning the exercise. No solution file, hints, or test answers are supplied.

<a id="py-blt-040-p03"></a>

## PY-BLT-040-P03 — Repair a tail API

### Problem

A service stores events oldest first. `tail(events, limit)` must return up to the newest `limit` events **in chronological order**, as a new list, without editing the caller's list. The following implementation is a learner review target:

```python
def tail(events, limit):
    selected = events
    selected.reverse()
    return selected[:limit]
```

Preserve it as the original broken attempt. Predict the result and caller state for one request, then test a second request using the same input object. Identify the first incorrect assumption before writing a correction.

### Learning evidence

Distinguish API ordering from traversal direction, aliasing from copying, and Python slice behavior from application validation.

### Constraints

- Require a nonnegative plain integer `limit`; reject a negative value with `ValueError` and other types, including bool, with `TypeError`.
- Preserve duplicate events and their order. Do not deduplicate or sort.
- Return a new outer list even when input is empty or `limit` is zero.
- A shallow result is sufficient: event objects may remain shared, but list membership must not be shared.

### Examples

```text
Input: events=['a', 'b', 'c', 'd'], limit=2
Required behavior: ['c', 'd']; events still ['a', 'b', 'c', 'd'].

Input: the same event list, limit=0
Required behavior: []; events still unchanged.
```

### Required edge cases

Two calls on the same input, no events, one event, duplicate values, zero limit, limit larger than input, invalid limits, and a caller holding another alias to the list.

### Acceptance criteria

- [ ] Preserve predicted and observed behavior of the broken version.
- [ ] State the first incorrect assumption explicitly.
- [ ] Record a minimal failing test before the correction.
- [ ] Retest ordering, ownership, and zero-count behavior independently.
- [ ] Explain why the repaired result satisfies the contract.

### Attempt and review

Not attempted. The broken code has not been accepted as a solution. No correction, hints, or learner results are recorded.

<a id="py-blt-040-p04"></a>

## PY-BLT-040-P04 — Review an ownership boundary

### Problem

A component owns a list of stage records, each shaped as `(stage_name, mutable_labels_list)`. Its accessor returns `tuple(stages)` and advertises an “immutable snapshot.” One consumer stores snapshots for later comparison, another wants to use a snapshot as a dictionary key, and a third appends labels through its own references.

Write a review explaining which promises the accessor must specify before implementation can be accepted. Construct your own small counterexample, record a prediction, then run it. Propose a representation and ownership contract; do not just suggest a copying function name.

### Learning evidence

Separate fixed outer membership, descendant mutation, value stability, hashability, and update cost. Connect each claimed property to a concrete operation.

### Constraints and examples

Use synthetic stage names. Preserve the component's internal records. The shape above is the input model, not a guarantee of independent or hashable data. Do not invoke a database, framework, or external service.

### Required edge cases

Empty stages, a repeated reference to one labels list, later label mutation, duplicate labels, and consumer attempts to change the returned structure.

### Acceptance criteria

- [ ] State what “snapshot” means in the proposed API.
- [ ] Demonstrate the smallest relevant counterexample.
- [ ] Explain memory and conversion costs without invented benchmarks.
- [ ] Identify what belongs to deeper hashing study in `PY-BLT-080`.
- [ ] Avoid claiming that a tuple or a copy solves concurrency by itself.

### Attempt and review

Not attempted. No design approval, hints, or learner evidence is recorded.

<a id="py-blt-040-p05"></a>

## PY-BLT-040-P05 — Make a new prediction

### Problem

Choose one of the unit's [copy](../experiments/EXP-01-copy-and-nesting/README.md) or [slice/range](../experiments/EXP-02-slices-and-ranges/README.md) experiments. Change one controlled variable, state the new hypothesis, and record exact predicted observations **before** running your variant.

### Learning evidence

Show that the model transfers to a new case. An existing author-run transcript is not your prediction or reconstruction.

### Constraints and examples

Keep the original probe unchanged. A separate learner variant may change a child-sharing relationship, a slice direction, an omitted bound, or a range endpoint. Record one change at a time; never materialize the huge range.

### Required edge cases

Include one boundary case appropriate to your change, such as an empty result, singleton, zero step, repeated child, or source mutation after copying.

### Acceptance criteria

- [ ] Question, hypothesis, and prediction precede the command.
- [ ] Runtime and platform are recorded.
- [ ] Actual output is preserved without editing it to fit the prediction.
- [ ] Interpretation separates observation, contract, and implementation detail.
- [ ] One limitation and one follow-up question are recorded.

### Attempt and review

Not attempted. No learner experiment, hints, review date, or closure is recorded.
