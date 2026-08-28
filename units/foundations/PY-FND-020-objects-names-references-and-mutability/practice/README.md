# PY-FND-020 practice — Objects, names, references, and mutability

[Unit note](../README.md) · [Curriculum entry](../../../../CURRICULUM.md#py-fnd-020) · [Progress](../../../../PROGRESS.md)

These exercises begin unsolved. Preserve the learner's first prediction, graph, code, test output, and correction reasoning before editing an attempt. Ask the mentor for one progressive hint at a time; solutions and completed traces do not belong in this scaffold before an attempt.

## Practice protocol

For each exercise:

1. Write the prediction or ownership contract before running or editing code.
2. Draw names and container positions as arrows to labeled objects such as `L1`, `D1`, and `T1`.
3. Mark every operation as object creation, mutation, rebinding, or reference reuse.
4. Run only after the initial reasoning is preserved.
5. Record the exact command and observed result.
6. Explain the first incorrect reasoning step; do not replace it with only the correct output.

Suggested evidence record:

```text
Exercise:
Date:
Python implementation and version:
Prediction or ownership contract:
Object graph:
Exact command:
Observed output:
First mismatch:
Corrected reasoning:
Tests:
Remaining weakness:
```

## PY-FND-020-P01 — Trace the graph

**Type:** Predict

**Difficulty:** 2/5

**Evidence target:** Trace aliases, shallow and deep descendants, mutation, and rebinding without relying on raw `id()` values.

Do not run this program until the worksheet is complete:

```python
from copy import deepcopy

root = [["queued"]]
alias = root
shallow = root.copy()
deep = deepcopy(root)

alias[0].append("running")
shallow.append(["shallow-only"])
deep[0].append("deep-only")
alias = [["rebound"]]

print(root)
print(alias)
print(shallow)
print(deep)
print(root is shallow)
print(root[0] is shallow[0])
print(root[0] is deep[0])
```

### Prediction worksheet

Before execution, supply all of the following:

- one label for each distinct outer list;
- one label for each distinct inner list;
- the binding target of `root`, `alias`, `shallow`, and `deep` after every statement;
- all seven printed results;
- the first line at which `alias is root` changes from true to false;
- why equal printed values would not be sufficient evidence of identity.

### Verification constraints

- Run with `python` only after preserving the worksheet.
- If one output differs, identify the first graph transition that was wrong.
- Do not describe `deepcopy` as “copy every appearance separately”; explain the object graph it creates.

### Hint gate

If blocked, request `PY-FND-020-P01 Hint 1`. Ask for Hint 2 only after updating the graph with Hint 1. Hints are intentionally not stored here so they can be revealed progressively.

## PY-FND-020-P02 — Own a request schema

**Type:** Implement

**Difficulty:** 3/5

**Evidence target:** Implement a documented two-level ownership boundary and deterministic independence tests.

Implement this contract in a learner attempt file after recording the ownership diagram:

```python
type-like shape: dict[str, list[str]]

def own_filters(filters):
    """Return state independently mutable from filters at both supported levels."""
```

Use ordinary Python 3.11-compatible annotation syntax in the implementation. The function must support any string field name and list-of-string value accepted by the declared schema.

### Required behavior

Given:

```python
incoming = {
    "roles": ["reader"],
    "regions": ["ap-south"],
}
owned = own_filters(incoming)
```

the implementation must satisfy all of these contracts:

1. `owned == incoming` immediately after construction.
2. `owned is not incoming`.
3. Each list value in `owned` is distinct from its corresponding source list.
4. Appending to `incoming["roles"]` does not change `owned["roles"]`.
5. Appending to `owned["regions"]` does not change `incoming["regions"]`.
6. Input order and duplicate strings are preserved.
7. The implementation does not use `copy.deepcopy`.

### Required tests

Write deterministic tests for:

- an empty dictionary;
- one empty child list;
- multiple fields;
- duplicates inside a child list;
- mutation in both directions after construction.

Record the exact test command and output. A passing test suite without a prewritten ownership diagram is incomplete evidence.

### Design explanation

In four to six sentences, explain:

- which graph nodes are newly created;
- which objects are safely reused and why;
- the time and additional-space complexity in terms of field and item counts;
- what schema change would invalidate the current depth policy.

### Hint gate

If blocked, request `PY-FND-020-P02 Hint 1`. Do not request an implementation or full solution before preserving an attempt.

## PY-FND-020-P03 — Debug a snapshot leak

**Type:** Debug

**Difficulty:** 3/5

**Evidence target:** Identify the first shared reference that violates the snapshot contract, then make the narrowest justified correction.

A metrics component promises that a recorded event is a snapshot: later caller mutations must not alter retained event dimensions.

```python
class MetricBuffer:
    def __init__(self) -> None:
        self._events: list[dict[str, object]] = []

    def record(self, event: dict[str, object]) -> None:
        self._events.append(event.copy())

    def events(self) -> list[dict[str, object]]:
        return self._events.copy()


buffer = MetricBuffer()
event = {
    "name": "request.finished",
    "dimensions": {"region": "ap-south", "roles": ["reader"]},
}

buffer.record(event)
event["dimensions"]["roles"].append("writer")

assert buffer.events()[0]["dimensions"]["roles"] == ["reader"]
```

### Debugging sequence

Before editing:

1. Draw the graph immediately after `record`.
2. Label which root was copied and which descendants were reused.
3. State the first object whose sharing contradicts the snapshot promise.
4. Decide whether the return path from `events()` exposes another ownership leak.
5. Write a test that fails for each identified direction of mutation.

Then implement the narrowest correction compatible with this declared event schema:

```text
event = {
    "name": str,
    "dimensions": {
        "region": str,
        "roles": list[str],
    },
}
```

Do not use `deepcopy` until you have written why arbitrary recursive copying is the intended public contract. If you choose it after that analysis, document its supported types and cost boundary.

### Review evidence

Record:

- the failing assertion before the change;
- the first violating reference, not merely “shallow copy issue”;
- the corrected ownership graph;
- tests that mutate caller state after `record`;
- tests that mutate returned state after `events`;
- why equal values at return time alone would not prove isolation.

### Hint gate

If blocked, request `PY-FND-020-P03 Hint 1`. Each later hint requires an updated object graph.

## PY-FND-020-P04 — Review an alias-prone API

**Type:** Review

**Difficulty:** 4/5

**Evidence target:** Produce precise review findings about a mutable default, exposed storage, invalid identity comparison, and ambiguous ownership.

Review this code without executing it first:

```python
class RouteRegistry:
    def __init__(self, routes: list[dict[str, str]] = []) -> None:
        self._routes = routes

    def add(self, path: str, method: str) -> None:
        self._routes.append({"path": path, "method": method})

    def all(self) -> list[dict[str, str]]:
        return self._routes

    def supports(self, method: str) -> bool:
        return any(route["method"] is method for route in self._routes)
```

### Required review format

For each finding, provide:

```text
Priority:
Exact line or expression:
Broken or ambiguous contract:
Object-graph mechanism:
Minimal exposing test:
Correction direction:
Trade-off or compatibility effect:
```

Find at least four independent concerns. At least one must distinguish value equality from identity, and at least one must distinguish constructor ownership from return-value ownership.

### Constraints

- Do not claim that annotations enforce immutability.
- Do not propose “copy everything” without identifying the required depth.
- Do not rely on whether a particular string happens to be interned.
- Preserve intentional caller-supplied routes only if you explicitly choose and document shared ownership.
- Rank correctness and cross-instance leaks above naming or style preferences.

### Verification

After the written review, create minimal tests that expose each correctness finding. Preserve the pre-fix failures and explain which binding or object each test proves is shared.

### Hint gate

If blocked, request `PY-FND-020-P04 Hint 1`. Ask for one finding category at a time rather than a complete review.

## PY-FND-020-P05 — Design an ownership contract

**Type:** Design

**Difficulty:** 4/5

**Evidence target:** Defend an ownership and copying policy for retained backend configuration, including graph depth, typing limits, and tests.

A long-lived service receives configuration shaped like this:

```python
config = {
    "regions": ["ap-south", "eu-west"],
    "retry": {"attempts": 3, "statuses": [429, 503]},
    "headers": {"x-service": "catalog"},
}
```

The caller may reuse and mutate its builder after constructing the service. The service needs occasional internal updates to retry status codes. A diagnostics endpoint must return configuration without allowing callers to mutate service state.

### Design deliverable

Write a short design note that answers:

1. Who owns each mutable node immediately after service construction?
2. Which nodes, if any, remain intentionally shared?
3. Will construction borrow, shallow-copy, schema-copy, deep-copy, or convert each field? Why?
4. How will the internal retry update occur without violating the chosen contract?
5. What does the diagnostics method return, and who owns that result?
6. Which typing choices communicate read-only use, and what can they not enforce at runtime?
7. What is the time and extra-space cost in terms of the configuration graph?
8. How would the policy change if a field later contained a file handle, lock, callback, or database session?

### Required visual

Draw the graph at three moments:

- caller builder before construction;
- caller and service immediately after construction;
- service and diagnostics result after each side performs one mutation.

Label newly created nodes and every intentionally shared reference. State the simplification or limitation of the visual.

### Required tests

Specify, then implement if requested, tests for:

- caller mutation after service construction;
- internal service mutation after construction;
- diagnostics-result mutation after return;
- empty nested collections;
- repeated immutable values;
- a future unsupported resource-bearing field.

### Decision defense

Conclude with one rejected alternative and the exact reason it does not fit. “Too slow” is insufficient without identifying what it traverses or duplicates; “unsafe” is insufficient without identifying the shared object and mutation path.

### Hint gate

If blocked, request `PY-FND-020-P05 Hint 1`. The first hint should address ownership questions only; later hints may address representation and tests.

## Completion evidence checklist

Practice can support progress only when the actual evidence exists:

- [ ] The first prediction or contract is preserved before execution.
- [ ] The object graph labels every distinct mutable node and alias.
- [ ] At least one nested-mutation edge case is tested.
- [ ] The learner distinguishes mutation from rebinding in their own words.
- [ ] The learner distinguishes `is` from `==` without interning folklore.
- [ ] Copy depth is justified against a concrete schema or graph.
- [ ] Actual commands and outputs are recorded.
- [ ] The first incorrect reasoning step is identified after any failure.
- [ ] Remaining weakness is specific enough to drive the next review.

Do not mark an exercise complete from generated scaffolding, copied output, or self-reported confidence alone.
