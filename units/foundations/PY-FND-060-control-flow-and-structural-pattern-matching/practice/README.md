# Practice — PY-FND-060 Control flow and structural pattern matching

| Field | Value |
|---|---|
| Unit note | [`PY-FND-060`](../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../CURRICULUM.md#py-fnd-060) |
| Topic branch | `topic/PY-FND-060` |
| Evidence target | E+C+D |
| Attempt required before solution | Yes |
| Canonical test command | `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s units/foundations/PY-FND-060-control-flow-and-structural-pattern-matching/tests -v` |
| Status | Not attempted |

## Practice rules

1. Record a prediction or control-flow sketch before running code.
2. Preserve the original attempt and the first failing assertion.
3. Request one progressive hint at a time; no hints or solutions are prewritten here.
4. A passing test is insufficient if the explanation names the wrong control edge.
5. Keep learner code in a new file under this directory so canonical examples remain unchanged.
6. Do not push later practice changes automatically unless the explicit publication prompt is given.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Suggested attempt file | Status |
|---|---|---:|---|---|---|
| `PY-FND-060-P01` | Predict | 2/5 | Reconstruct an exact loop event trace. | `p01_prediction.md` | Not attempted |
| `PY-FND-060-P02` | Implement | 3/5 | Design a bounded search with distinct result states. | `p02_candidate_search.py` | Not attempted |
| `PY-FND-060-P03` | Debug | 3/5 | Repair a multi-level exit while preserving all outcomes. | `p03_matrix_search.py` | Not attempted |
| `PY-FND-060-P04` | Implement | 4/5 | Build a structural event router with explicit validation. | `p04_event_router.py` | Not attempted |
| `PY-FND-060-P05` | Review | 4/5 | Review ordered matching for semantic and production risks. | `p05_review.md` | Not attempted |

## PY-FND-060-P01 — Trace a filtered search

### Problem

Without running the code, write the exact printed lines in order for calls A, B, and C. Then draw the edge taken by every `continue`, `break`, and loop termination.

```python
def trace(values, wanted):
    for index, value in enumerate(values):
        print("visit", index, value)
        if value < 0:
            print("skip", value)
            continue
        if value == wanted:
            print("found", value)
            break
        print("miss", value)
    else:
        print("exhausted")
    print("done")


trace([-1, 4, 7], 4)   # A
trace([-1, 4, 7], 9)   # B
trace([], 4)            # C
```

### Learning evidence

This exercise should demonstrate:

- exact source-order tracing;
- the distinction between `continue`, `break`, and iterator exhaustion;
- the meaning of loop `else` for non-empty and empty inputs.

### Constraints

- Do not run, paste into a REPL, or mentally replace the loop with a flag before writing all three predictions.
- Mark any uncertain line rather than silently changing the prediction.
- After execution, preserve the prediction even if it was wrong.

### Required edge cases

- a match after one `continue`;
- complete exhaustion after body execution;
- an initially empty iterable.

### Acceptance criteria

- [ ] Every output line is in exact order.
- [ ] The loop `else` decision is explained for all three calls.
- [ ] The destination of each transfer statement is named.
- [ ] Prediction and observed output are both preserved.
- [ ] The first incorrect reasoning step, if any, is recorded.

### Prediction before execution

Record in `p01_prediction.md`:

```text
Call A:

Call B:

Call C:

Reasoning:
Uncertainty:
```

### Hint gate

No hint is stored in this artifact. If blocked after a complete prediction, request `PY-FND-060-P01 Hint 1` and include the prediction.

## PY-FND-060-P02 — Select an executable candidate

### Problem

Implement a function that examines candidates in input order and returns a structured result describing one of four outcomes:

- `"selected"`: the first candidate that is enabled, has a non-negative priority, and is not in `blocked_ids`;
- `"empty"`: the iterable produced no candidates;
- `"exhausted"`: candidates existed, but every candidate was rejected;
- `"invalid"`: the caller supplied a negative inspection limit.

Candidate shape:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    enabled: bool
    priority: int
```

Required signature:

```python
def select_candidate(
    candidates,
    blocked_ids: set[str],
    inspection_limit: int,
):
    ...
```

Define an explicit immutable result type. It must include the outcome, selected ID or `None`, inspected IDs, and rejection reasons. Stop requesting input as soon as a candidate is selected or the limit is reached.

### Learning evidence

This exercise should demonstrate:

- deliberate use of `continue`, `break` or early `return`, and natural termination;
- distinct domain states rather than one ambiguous falsy result;
- bounded behavior for a potentially lazy iterable;
- tests that prove later candidates are not consumed after selection.

### Constraints

- Do not convert the whole iterable to a list.
- Do not use exceptions for ordinary `"empty"` or `"exhausted"` outcomes.
- Do not use a mutable `found` flag unless the written design proves why it is clearer than the alternatives.
- Do not inspect more than `inspection_limit` candidates.
- Keep rejection checks free of I/O and global mutation.

### Required edge cases

- negative and zero inspection limits;
- empty input;
- all candidates disabled;
- a blocked candidate before a valid candidate;
- a negative-priority candidate;
- a valid first candidate;
- a generator that raises if one item beyond the selected candidate is requested;
- duplicated candidate IDs, with a stated policy.

### Acceptance criteria

- [ ] All four outcome states are observable and unambiguous.
- [ ] Input order and first-match precedence are documented.
- [ ] Consumption stops at the selected candidate or the limit.
- [ ] Deterministic `unittest` cases cover every required edge.
- [ ] The learner can draw the termination path for each outcome.
- [ ] Time and space costs are explained in terms of inspected items.

### Prediction and design before implementation

Record:

- the loop invariant;
- the progress measure;
- the exact meaning of natural termination;
- the result state produced by limit zero;
- whether loop `else` or early returns will make the policy clearer;
- the first three tests to write.

### Hint gate

If blocked after the design and one failing test, request `PY-FND-060-P02 Hint 1` with both artifacts.

## PY-FND-060-P03 — Escape a matrix search correctly

### Problem

The function should return the coordinates of the first cell equal to `wanted`, scanning rows then columns. It should return `None` only after every reachable cell has been inspected. The current implementation produces incorrect results and misleading metrics.

```python
def locate(matrix, wanted):
    visited = 0
    result = None

    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            visited += 1
            if value == wanted:
                result = (row_index, column_index)
                break
        else:
            result = None

    return result, visited
```

### Debugging sequence

1. Predict `(result, visited)` for `[[1, 2], [3, 4]]` with `wanted=2`.
2. Mark the destination of the inner `break`.
3. Mark the owner and trigger of the inner `else`.
4. Find the smallest matrix for which a found result is later erased.
5. Choose one repair strategy and state why it is clearer:
   - a helper function with early `return`;
   - explicit propagation from the inner loop;
   - another justified control structure.
6. Preserve the original function and add the repair separately.

### Learning evidence

This exercise should demonstrate:

- nearest-loop ownership;
- detection of a later overwrite after a locally correct `break`;
- a multi-level exit design without imaginary labeled breaks;
- accurate consumption/visited metrics.

### Constraints

- Do not use module-level state.
- Do not flatten the matrix before searching.
- Do not raise an exception for the ordinary not-found state.
- Avoid a second full scan.
- Preserve row-major first-match behavior.

### Required edge cases

- empty matrix;
- empty first row followed by a match;
- match in the first cell;
- match before later rows;
- duplicate matches;
- no match;
- a row supplied as a one-pass iterator, if the chosen type contract permits it.

### Acceptance criteria

- [ ] The first failing behavior is explained from exact control edges.
- [ ] A found result cannot be erased by later work.
- [ ] `visited` counts only requested cells.
- [ ] Duplicate matches return the first row-major location.
- [ ] Tests prove both early exit and complete exhaustion.
- [ ] The chosen design is compared with at least one alternative.

### Hint gate

If blocked after the trace, request `PY-FND-060-P03 Hint 1` and include the smallest counterexample.

## PY-FND-060-P04 — Route a versioned job event

### Problem

Implement `route_event(event: object) -> RouteResult` for this closed input protocol:

1. A mapping with `"type": "job.created"`, integer `"version": 1`, and string `"job_id"` routes to `"create-v1"`. Extra metadata is allowed and its keys must be recorded without logging values.
2. A mapping with `"type": "job.created"` and any other integer version routes to `"unsupported-version"` while preserving the version.
3. A two-element sequence whose first item is `"cancel"` or `"delete"` and whose second item is a string ID routes to `"remove"` and records the operation.
4. A `Retry(job_id: str, attempts: int)` instance with attempts from 1 through 3 routes to `"retry"`.
5. Any other `Retry` routes to `"invalid-retry"`.
6. Every other subject routes to `"unsupported-shape"`.

Use structural pattern matching and an immutable result type. Return results; do not print or perform I/O.

### Learning evidence

This exercise should demonstrate:

- mapping, sequence, OR, AS, class, capture, and wildcard patterns;
- correct placement of residual predicates in guards;
- deliberate ordering of overlapping cases;
- strict domain outcomes despite mapping-pattern tolerance for extra keys.

### Constraints

- Do not use `type(event) is ...` as a replacement for all structural patterns.
- Do not mutate the subject.
- Do not log raw metadata values.
- Do not rely on names left by a failed pattern.
- Do not use a bare name where a constant comparison is intended.
- Keep guards deterministic and free of side effects.

### Required edge cases

- extra mapping keys;
- missing `job_id`;
- `version=True`, with an explicit policy acknowledging that `bool` is an `int` subclass;
- version `0` and `2`;
- list and tuple command sequences;
- a plain string such as `"cancel"`;
- retry attempts `0`, `1`, `3`, and `4`;
- an unrelated object;
- a mapping implementation whose lookup behavior is part of its public contract, if supported.

### Acceptance criteria

- [ ] Every protocol rule maps to one tested outcome.
- [ ] Case order handles overlap intentionally.
- [ ] The string/sequence boundary is explained.
- [ ] Captured values are used only after successful patterns.
- [ ] Unsupported inputs cannot disappear silently.
- [ ] A registry-dispatch alternative is discussed for a future open plugin protocol.

### Prediction and design before implementation

Write a case-order table containing:

| Proposed case | Structural facts | Guard facts | Broader cases it must precede |
|---|---|---|---|

Then record two inputs that would change outcome if the cases were reordered.

### Hint gate

If blocked after the case-order table and first attempt, request `PY-FND-060-P04 Hint 1` with both.

## PY-FND-060-P05 — Review a risky dispatcher

### Problem

Review this code without rewriting it first:

```python
READY = "ready"


def dispatch(event, metrics, handlers):
    match event:
        case {"type": "job", "status": READY, "payload": payload}:
            return handlers["ready"](payload)
        case {"type": kind, **rest} if metrics.increment(kind):
            return handlers[kind](rest)
        case [kind, payload]:
            return handlers[kind](payload)
        case _:
            pass
```

Assume the intended policy was to compare status with the constant string `"ready"`, count every recognized event exactly once, reject unknown handler keys cleanly, and remain easy to extend by separately deployed handler packages.

### Review brief

Produce a review containing:

1. the first compile-time or semantic problem and the exact pattern rule behind it;
2. whether `READY` compares, captures, or makes later patterns unreachable;
3. which mapping inputs overlap and how source order affects them;
4. why a side-effecting guard makes metric counts dependent on pattern success and truthiness;
5. failure behavior for a missing handler key, a handler exception, and an unsupported shape;
6. whether a two-character string can match `[kind, payload]` and why;
7. whether mapping extra keys are accepted and whether that fits the stated policy;
8. the security/observability risk of passing unvalidated `rest` into a handler;
9. whether a central `match` remains appropriate for separately deployed extensions;
10. a test matrix that separates syntax, routing, guard effects, handler errors, unknown keys, and fallback behavior;
11. the smallest safe change boundary before any refactor;
12. one alternative design using validation plus registry dispatch.

### Constraints

- Do not execute untrusted handlers during review.
- Do not assume wildcard fallback is sufficient observability.
- Do not hide handler exceptions under a generic not-found outcome.
- Distinguish language semantics from the application's desired policy.
- Cite the exact unit section for each language-level finding.

### Acceptance criteria

- [ ] Capture versus value-pattern semantics are correct.
- [ ] Pattern overlap and case-order policy are explicit.
- [ ] Guard side effects are traced precisely.
- [ ] Sequence eligibility is not confused with general iteration.
- [ ] Error states and logging boundaries remain distinct.
- [ ] The open-extension requirement influences the recommended architecture.
- [ ] No replacement implementation appears before the review.

### Hint gate

If blocked after writing at least five findings, request `PY-FND-060-P05 Hint 1` and include the partial review.

## Review and closure protocol

For every completed exercise, retain:

- the original prediction, design, or review;
- the first failing assertion or incorrect event edge;
- the smallest counterexample that exposed it;
- the corrected rule in the learner's own words;
- actual command and output;
- relevant empty, boundary, fallthrough, and unsupported cases;
- a short production consequence;
- remaining uncertainty.

Passing supplied or learner-written tests does not prove understanding if the explanation confuses natural termination with failure, inner with outer loop ownership, capture with comparison, or pattern success with guard success. Only closed attempts with preserved evidence may support a later `PROGRESS.md` learning-state transition.
