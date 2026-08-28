# PY-FND-030 practice — Namespaces, scope, and name resolution

[Unit note](../README.md) · [Curriculum entry](../../../../CURRICULUM.md#py-fnd-030) · [Progress](../../../../PROGRESS.md)

These exercises begin unsolved. Preserve the learner's first classification, prediction, code, test output, and correction reasoning before editing an attempt. Ask the mentor for one progressive hint at a time; completed traces and solutions do not belong in this scaffold before an attempt.

## Practice protocol

For every exercise:

1. Draw the code blocks and their namespaces before running or changing code.
2. Circle every binding operation, including parameters, imports, definitions, loop targets, and `as` targets.
3. Classify each relevant spelling as local, free, global, nonlocal, class-local, or built-in.
4. Predict the first failing or state-changing line and the exact exception type where applicable.
5. Preserve the initial answer, then run the exact command and record the observed result.
6. Identify the first incorrect classification or state transition; do not replace the attempt with only the final output.

Suggested evidence record:

```text
Exercise:
Date:
Python implementation and version:
Code blocks and namespaces:
Binding operations:
Name classifications:
Prediction:
Exact command:
Observed output:
First mismatch:
Corrected reasoning:
Tests:
Remaining weakness:
```

## PY-FND-030-P01 — Classify before executing

**Type:** Predict

**Difficulty:** 2/5

**Evidence target:** Classify local, enclosing, global, and built-in names before tracing normal and failing paths.

Do not run this program until the worksheet is complete:

```python
limit = 5
label = "module"


def make_runner(prefix: str):
    label = "enclosing"

    def run(values: list[int], override: int | None = None):
        if override is not None:
            limit = override
        selected = values[:limit]
        return prefix, label, len(selected), selected

    return run


runner = make_runner("batch")
print(runner([10, 20, 30, 40], 2))
print(runner([10, 20, 30, 40]))
```

### Prediction worksheet

Before execution, provide all of the following:

- every code block in the program;
- every binding operation for `limit`, `label`, `prefix`, `values`, `override`, `selected`, and `len`;
- the classification of each occurrence inside `run`;
- the complete first printed result;
- whether the second call prints or raises, with the exact exception class;
- why the module binding `limit = 5` does or does not participate;
- whether the caller could change the result merely by defining its own local `limit`.

### Verification constraints

- Run only after the worksheet is timestamped or committed.
- If the prediction differs, identify the first classification error rather than editing only the final output.
- Do not add `global` or `nonlocal` until you have stated which namespace should own `limit`.

### Hint gate

If blocked, request `PY-FND-030-P01 Hint 1`. Ask for Hint 2 only after updating the binding table with Hint 1.

## PY-FND-030-P02 — Build an isolated retry budget

**Type:** Implement

**Difficulty:** 3/5

**Evidence target:** Use one enclosing binding deliberately, prove independent factory instances, and explain the state boundary.

Implement this Python 3.11-compatible contract in a learner attempt file:

```python
from collections.abc import Callable


def make_retry_budget(total: int) -> tuple[Callable[[], bool], Callable[[], int]]:
    """Return consume() and remaining() functions sharing one private budget."""
```

### Required behavior

For `consume, remaining = make_retry_budget(2)`:

1. `remaining()` initially returns `2`.
2. The first two `consume()` calls each return `True` and reduce the remaining budget by one.
3. Later `consume()` calls return `False` and do not make the budget negative.
4. `remaining()` reports the current budget without mutating it.
5. Two separate factory calls have independent budgets.
6. A negative initial total raises `ValueError` before either function is returned.
7. No module-global mutable state and no mutable default argument is used.

### Before implementation

Draw:

- the module namespace;
- the local namespace of one `make_retry_budget` call;
- the two returned function objects;
- the single binding that both returned functions need to observe;
- a second factory call with a separate binding.

State which inner function needs `nonlocal`, which one does not, and why reading differs from rebinding.

### Required tests

Write deterministic tests for:

- totals `0`, `1`, and `3`;
- consumption after exhaustion;
- interleaved calls to two independent budgets;
- negative construction;
- repeated `remaining()` calls having no effect.

Record the exact test command and output. Passing tests without the prewritten scope diagram are incomplete evidence.

### Design explanation

In five to seven sentences, explain:

- which block owns the budget binding;
- why `nonlocal` is or is not required in each returned function;
- why a module global would change isolation and test behavior;
- why lexical scope does not provide synchronization;
- when a small class would communicate the contract better.

### Hint gate

If blocked, request `PY-FND-030-P02 Hint 1`. Do not request a complete implementation before preserving an attempt.

## PY-FND-030-P03 — Debug a policy lookup

**Type:** Debug

**Difficulty:** 3/5

**Evidence target:** Distinguish a method's lexical name lookup from class attribute lookup, then make the narrowest ownership-correct fix.

Review without executing first:

```python
TIMEOUT_SECONDS = 30


class PartnerPolicy:
    TIMEOUT_SECONDS = 5
    MAX_ATTEMPTS = 3

    def request_window(self) -> int:
        return TIMEOUT_SECONDS * MAX_ATTEMPTS
```

The intended contract is that each policy subclass may override both values and `request_window()` must use the effective class or instance attributes.

### Debugging sequence

Before editing:

1. Draw the module namespace and the namespace produced by the class body.
2. Classify both bare names inside `request_window`.
3. Predict whether the method returns a number or raises, and identify the first lookup result or failure.
4. Explain why the method's textual indentation inside the class does not make the class namespace an ordinary enclosing function scope.
5. Decide whether the contract requires instance-qualified or class-qualified access.
6. Write a subclass-based test that would reject a fix that hard-codes `PartnerPolicy`.

### Required tests

Cover:

- the base policy's expected window;
- a subclass overriding only the timeout;
- a subclass overriding only the attempt count;
- an instance attribute override if the chosen public contract permits it;
- the module constant remaining unchanged.

### Review evidence

Record the original behavior, exact lookup path for each bare name, corrected access path, and why changing or deleting the module global would not by itself repair the intended polymorphic contract.

### Hint gate

If blocked, request `PY-FND-030-P03 Hint 1`. Each later hint requires an updated namespace diagram.

## PY-FND-030-P04 — Review a module-state API

**Type:** Review

**Difficulty:** 4/5

**Evidence target:** Produce precise findings about built-in shadowing, hidden module mutation, test isolation, and process-level correctness.

Review this code without executing it first:

```python
dict = {}
processed = 0


def handle(items: list[str], len: int | None = None) -> dict[str, int]:
    global processed
    processed += 1

    if len is None:
        len = 10

    dict["latest_size"] = min(len, items.__len__())
    return dict
```

Assume `handle` may be called by concurrent request workers and tests run multiple cases in one process.

### Required review format

For each finding, provide:

```text
Priority:
Exact name or expression:
Owning namespace:
Lookup or rebinding mechanism:
Broken or ambiguous contract:
Smallest exposing test:
Recommended boundary:
Trade-off:
```

### Required analysis

Address all of the following without giving a wholesale rewrite first:

- both shadowed built-in names and the exact scopes in which shadowing applies;
- module-level mutation of `processed` and the returned dictionary;
- whether `global` provides any concurrency guarantee;
- whether one process-wide count represents a multi-process service count;
- mutation by a caller after receiving the returned mapping;
- order-dependent tests and the reset problem;
- why directly calling `items.__len__()` is not a scope fix;
- a state-owner design whose lifecycle and synchronization policy can be stated explicitly.

### Verification constraints

Create at least one deterministic test for each state leak you claim. Separate scope facts from concurrency assumptions, and do not claim a race was observed unless you actually run a controlled experiment.

### Hint gate

If blocked, request `PY-FND-030-P04 Hint 1`. Do not request a completed review before recording your own prioritized findings.

## Completion evidence checklist

Before asking for review, verify that the evidence includes:

- one closed-book namespace and scope reconstruction;
- a binding table made before execution;
- an exact `NameError` versus `UnboundLocalError` explanation;
- one tested `nonlocal` or `global` rebinding contract;
- one class-body-versus-method lookup trace;
- preserved first attempts and progressive hints;
- exact commands and observed outputs;
- a remaining weakness stated precisely rather than “need more practice.”
