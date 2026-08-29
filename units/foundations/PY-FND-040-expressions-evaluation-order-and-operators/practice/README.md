# PY-FND-040 practice — Expressions, evaluation order, and operators

[Unit note](../README.md) · [Curriculum entry](../../../../CURRICULUM.md#py-fnd-040) · [Progress](../../../../PROGRESS.md)

These exercises begin unsolved. Preserve the first parse, prediction, trace, code, test output, and correction reasoning before revising an attempt. Ask for one progressive hint at a time; complete solutions and prewritten hints do not belong in this scaffold before an attempt.

## Practice protocol

For every expression exercise, record four separate layers:

1. **Parse shape:** add conceptual parentheses or draw a tree using precedence and associativity.
2. **Demand gates:** mark operands or branches that a short-circuit or conditional may skip.
3. **Evaluation timeline:** number every call, lookup, target evaluation, operation, assignment, and possible exception.
4. **Value result:** calculate only after the first three layers are stable.

Suggested evidence record:

```text
Exercise:
Date:
Python implementation and version:
Parse shape:
Demand gates:
Operand timeline:
Operation timeline:
Prediction:
Exact command:
Observed output:
First mismatch:
Corrected rule:
Tests:
Production implication:
Remaining weakness:
```

Do not replace a wrong prediction with only the observed output. The evidence is the first incorrect grouping or transition and the corrected reasoning that follows it.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Status |
|---|---|---:|---|---|
| `PY-FND-040-P01` | Predict | 2/5 | Separate grouping, operand order, operation order, and value | Not attempted |
| `PY-FND-040-P02` | Predict and explain | 3/5 | Trace short-circuit gates and returned operands | Not attempted |
| `PY-FND-040-P03` | Debug | 3/5 | Diagnose target timing in normal and augmented assignment | Not attempted |
| `PY-FND-040-P04` | Review | 3/5 | Decide whether `:=` improves one value-flow contract | Not attempted |
| `PY-FND-040-P05` | Design and review | 4/5 | Preserve falsy cache values and exact side-effect order | Not attempted |

## PY-FND-040-P01 — Three-axis expression trace

**Type:** Predict

**Difficulty:** 2/5

**Evidence target:** Prove that precedence, associativity, and evaluation order answer different questions.

Do not run this program until the worksheet is complete:

```python
events: list[str] = []


def stamp(label: str, value: int) -> int:
    events.append(label)
    return value


result = (
    stamp("A", 2)
    + stamp("B", 3) ** stamp("C", 2) ** stamp("D", 1)
    - stamp("E", 4)
)

print(result)
print(events)
```

### Prediction worksheet

Before execution, provide all of the following:

- a fully parenthesized expression containing no implicit operator grouping;
- a parse tree whose leaves are the five `stamp` calls;
- the exact call-event order;
- the order in which each power, addition, and subtraction operation completes;
- the final integer value;
- one sentence explaining why the right-associative power group does not reverse the operand-call trace;
- one parenthesis change that produces a different result without changing call order.

### Verification constraints

- Run only after the worksheet is timestamped or committed.
- If the value is wrong, identify whether the first error is grouping, temporal order, or arithmetic.
- Do not claim that the event list records operator completion; it records only operand-producing calls.

### Hint gate

If blocked, request `PY-FND-040-P01 Hint 1`. Ask for a later hint only after updating the parse tree.

## PY-FND-040-P02 — Short-circuit gates

**Type:** Predict and explain

**Difficulty:** 3/5

**Evidence target:** Identify every skipped call and the exact operand object returned by `and`, `or`, and a conditional expression.

Do not run this program until every gate has two labelled exits:

```python
events: list[str] = []


def stamp(label: str, value):
    events.append(label)
    return value


first = stamp("A", []) and stamp("B", "published")
second = stamp("C", {"cached": 0}) or stamp("D", {"loaded": 1})
third = stamp("E", "") or stamp("F", 0) or stamp("G", "fallback")
fourth = (
    stamp("H", "accepted")
    if stamp("I", 1)
    else stamp("J", "rejected")
)

print(first)
print(second)
print(third)
print(fourth)
print(events)
```

### Required reasoning

Record:

- the first expression evaluated for each assignment;
- every skipped label and the rule that skips it;
- the type and value assigned to each result name;
- why a non-empty dictionary participates differently from its contained numeric value;
- why the conditional's middle expression runs before its textual first branch;
- the first event that would disappear if the `third` expression's first operand changed to a non-empty string.

### Counterexample requirement

Create one new pair of operands showing that:

- `and` can return a non-Boolean left operand; and
- `or` can return a non-Boolean right operand.

Predict before executing the counterexample. Full truthiness rules are reviewed in `PY-FND-050`; use only the built-in values present here.

### Hint gate

If blocked, request `PY-FND-040-P02 Hint 1`. Later hints require an updated gate diagram.

## PY-FND-040-P03 — The moving subscript

**Type:** Debug

**Difficulty:** 3/5

**Evidence target:** Contrast right-side-before-target normal assignment with target-once-before-right-side augmented assignment.

Analyze this first case without executing:

```python
events: list[str] = []
position = 0
values = [10, 20]


def choose_index() -> int:
    events.append(f"index:{position}")
    return position


def compute() -> int:
    global position
    events.append("rhs")
    position = 1
    return 99


values[choose_index()] = compute()

print(values)
print(position)
print(events)
```

Then reset all state and analyze this distinct statement:

```python
values[choose_index()] += compute()
```

### Prediction worksheet

For each case, record:

- which expression is evaluated first;
- the value of `position` when `choose_index()` runs;
- which list slot is read, if any;
- which list slot is written;
- whether the target expression is evaluated once or more than once;
- the final `values`, `position`, and `events`;
- the first semantic difference between the two statements.

### Debugging task

Assume the intended contract is: “Select the original position once, compute the replacement using whatever state changes it needs, then write to that original position.”

Propose the smallest readable implementation that makes that timing explicit. Do not use a global in the corrected design. Preserve a failing regression test for the original normal-assignment behavior before editing it.

### Required tests

Cover:

- starting positions `0` and `1`;
- a computation that does not change selection state;
- a computation that raises before a write;
- a selector that raises before computation in the intended design;
- an assertion about exact call count, not only final values.

### Hint gate

If blocked, request `PY-FND-040-P03 Hint 1`. Each later hint requires a revised event timeline.

## PY-FND-040-P04 — Walrus or explicit state?

**Type:** Review

**Difficulty:** 3/5

**Evidence target:** Decide whether binding and consuming one value in an expression improves or harms the contract.

Review the following code without rewriting it first:

```python
def process_available(read, decode, accept):
    processed = 0
    while (raw := read()) and (record := decode(raw)) and accept(record):
        processed += 1
    return processed
```

Assume all three callables can log and raise. The current interface does not state whether empty `raw`, a falsy decoded `record`, or a rejected record are normal termination, invalid data, or errors.

### Required review format

For each finding, provide:

```text
Priority:
Exact subexpression:
Evaluated after:
Possible skipped work:
Value contract being assumed:
Failure or observability boundary:
Smallest exposing test:
Recommendation:
Trade-off:
```

### Required analysis

Address all of the following:

- the exact call order on a fully successful iteration;
- which call is skipped for each falsy intermediate result;
- whether `raw` and `record` need to remain available after the condition;
- whether the loop distinguishes end-of-stream, invalid data, and policy rejection;
- how many times each callable runs per iteration;
- whether ordinary assignments and explicit branches communicate the contract better;
- one defensible use of `:=` that remains after refactoring, if any;
- Python 3.11 compatibility.

Do not assume the intended sentinel. State the missing API decision and give alternatives before choosing a rewrite.

### Hint gate

If blocked, request `PY-FND-040-P04 Hint 1`. Do not request a completed review before recording your own findings.

## PY-FND-040-P05 — Honest cache fallback

**Type:** Design and review

**Difficulty:** 4/5

**Evidence target:** Preserve meaningful falsy results, exact call counts, exception order, and observable events in a backend boundary.

Review this compact implementation:

```python
def resolve_policy(key, read_cache, read_store, validate, audit):
    return (
        audit("cache", read_cache(key))
        or audit("store", read_store(key))
    ) and validate(
        audit("selected", read_cache(key) or read_store(key))
    )
```

Assume:

- a cache miss is represented by `None`;
- an empty dictionary is a valid cached policy;
- each read can perform I/O or raise;
- `audit` returns the object it receives;
- `validate` may return an empty validated mapping;
- duplicate reads are observable and not allowed.

### Before implementation

Produce:

1. a fully parenthesized shape;
2. one timeline for a non-empty cache hit;
3. one timeline for an empty-dictionary cache hit;
4. one timeline for a cache miss and successful store read;
5. one timeline for a cache exception;
6. an inventory of duplicate calls and skipped calls;
7. the first contract violation in each path.

### Design task

Design a Python 3.11-compatible replacement that:

- calls `read_cache` exactly once;
- calls `read_store` only for the explicit miss sentinel;
- treats an empty cached mapping as a hit;
- audits each actual read exactly once in temporal order;
- validates the selected object exactly once;
- returns the validator's result even when that result is empty;
- does not catch or reorder exceptions without an explicit policy;
- uses intermediate names that reveal the event timeline.

Do not write the implementation until the trace-based contract and tests exist.

### Required tests

Use synthetic callables and an event list to cover:

- non-empty cache hit;
- empty-dictionary cache hit;
- cache miss with store result;
- empty store result;
- cache exception;
- store exception;
- validation exception;
- exact read, audit, and validation call counts;
- no call after the first propagated exception.

### Review explanation

In six to ten sentences, explain why the final structure is easier to verify than the original. Separate truthiness policy from evaluation-order facts. Name one alternative API design that would make the miss/result distinction more explicit.

### Hint gate

If blocked, request `PY-FND-040-P05 Hint 1`. A later hint requires a failing path-specific test and an updated event timeline.

## Completion evidence checklist

Before asking for review, verify that the evidence includes:

- one closed-book precedence ladder reconstruction;
- one fully parenthesized expression and parse tree;
- distinct operand and operation timelines;
- one right-associative power trace;
- one short-circuit gate diagram with skipped calls crossed out;
- one normal-versus-augmented assignment comparison;
- one justified assignment-expression decision;
- a backend refactor preserving exact calls and valid falsy results;
- exact commands and observed outputs;
- the first incorrect assumption, not merely the final answer;
- a remaining weakness stated more precisely than “need more practice.”
