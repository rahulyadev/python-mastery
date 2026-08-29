# EXP-01 — Expression grouping and side-effect trace

| Field | Value |
|---|---|
| Owning unit | [`PY-FND-040`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-fnd-040) |
| Topic branch | `topic/PY-FND-040` |
| Precise question | When grouping, associativity, short-circuiting, calls, and assignment targets interact, which operand-producing functions actually run and in what order? |
| Classification | Python language guarantee tested through a CPython runtime observation |
| Status | Reproduced |
| Risk | None; deterministic standard-library-only execution |

## 1. Why an experiment is necessary

Precedence is often taught with the phrase “do this operation first,” which hides the difference between parse grouping and temporal evaluation. Prose can state the distinction, but an ordered event trace reveals it directly. The same trace technique also exposes skipped operands, the boundary between argument evaluation and function invocation, and the reversed target/right-side timing of normal versus augmented assignment.

No bytecode inspection is needed. The experiment observes only language-level values and effects produced by ordinary functions.

## 2. Hypothesis

Before execution:

> Mixed arithmetic will group multiplication more tightly while calling operand producers left to right. A power chain will group from the right while its three operand producers still run left to right. Short-circuit expressions will omit unneeded labels. A callable and all arguments will be evaluated before invocation. Normal subscript assignment will evaluate the right side before its target, whereas augmented subscript assignment will evaluate the target once before the right side.

Alternative outcomes requiring investigation:

- the event trace follows precedence rather than source order;
- right-associative power reverses operand calls;
- a skipped operand still records an event;
- the function body records `invoke` before an argument event;
- normal and augmented subscript assignment share the same target timing;
- the two syntactic power/unary forms produce the same values.

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
Relevant environment variables: PYTHONDONTWRITEBYTECODE=1 for repository hygiene
```

The repository's canonical documentation baseline is Python 3.14.7. Execution occurred on the available CPython 3.14.4 runtime, so every observed fact is labelled accordingly.

## 4. Controls and variables

### Controlled

- Every effect appends a fixed label to an in-memory list.
- Inputs are fixed integers, strings, dictionaries, and callables.
- No clock, randomness, filesystem, network, subprocess, thread, signal, or external service is used.
- Every case starts with fresh event state.
- Formatting is deterministic and covered by a focused unit test.

### Changed

- Operator grouping: addition with multiplication versus chained exponentiation.
- Demand: false or true left operands for `and` and `or`, plus one conditional expression.
- Call phase: callable construction, positional argument, keyword argument, then invocation.
- Assignment form: normal subscript assignment versus augmented subscript assignment.
- Parentheses: implicit power/unary grouping versus explicit alternatives.

### Measured

- Final values.
- Exact ordered event labels.
- Labels absent because their operands or branches were skipped.
- Final subscript values after normal and augmented assignment.

## 5. Files

```text
experiments/EXP-01-expression-trace/
├── README.md
└── expression_trace.py
```

The runnable source is [`expression_trace.py`](expression_trace.py). It imports the same source modules exercised by the unit tests.

## 6. Reproduction command

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python units/foundations/PY-FND-040-expressions-evaluation-order-and-operators/experiments/EXP-01-expression-trace/expression_trace.py
```

Focused regression command:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s units/foundations/PY-FND-040-expressions-evaluation-order-and-operators/tests -v
```

## 7. Prediction

```text
precedence: value=22; events=left -> factor -> count
power: value=512; events=base -> inner-exponent -> outer-exponent
short-circuit: values=(0, 'cached', 'loaded', 'ready'); events=and-left -> or-left -> fallback-left -> fallback-right -> condition -> if-branch
call: value=7; events=callee -> positional -> keyword -> invoke
normal assignment: value=5; events=rhs -> target-container -> target-key
augmented assignment: value=15; events=target-container -> target-key -> rhs
power and unary: (-4, 4, 512, 64, 0.25)
```

## 8. Observed output

```text
precedence: value=22; events=left -> factor -> count
power: value=512; events=base -> inner-exponent -> outer-exponent
short-circuit: values=(0, 'cached', 'loaded', 'ready'); events=and-left -> or-left -> fallback-left -> fallback-right -> condition -> if-branch
call: value=7; events=callee -> positional -> keyword -> invoke
normal assignment: value=5; events=rhs -> target-container -> target-key
augmented assignment: value=15; events=target-container -> target-key -> rhs
power and unary: (-4, 4, 512, 64, 0.25)
```

The prediction and observation matched. No output was edited to create that match.

The focused regression suite also ran eight tests successfully on the recorded runtime.

## 9. Interpretation

1. The precedence case grouped multiplication inside the right operand, yet `left` was the first event. This directly separates grouping from temporal operand evaluation.
2. The power case produced `512`, consistent with right grouping, while its labels remained in left-to-right source order. Associativity did not reverse the call timeline.
3. No label ending in `skipped` appeared. The false `and` operand, true `or` operand, and selected conditional branch prevented their alternatives from running.
4. `callee`, `positional`, and `keyword` all preceded `invoke`. The function body began only after the callable and arguments had been evaluated.
5. Normal assignment recorded `rhs` before the container and key target expressions. Augmented assignment recorded the target expressions before `rhs` and wrote the combined value back to that original target.
6. The power/unary tuple distinguishes implicit and explicit grouping without relying on a parse-tree library or implementation-specific opcode.

## 10. Visual interpretation

```text
one source expression                 two complementary views

left() + factor() * count()           grouping tree:      +
                                                         / \
                                                     left   *
                                                           / \
                                                      factor count

                                       observed marks: left -> factor -> count
                                       operation flow: factor * count -> add left
```

### How to read this visual

Read the tree vertically to determine which values combine. Read the observed marks horizontally to determine when operand-producing calls execute. The operation-flow line begins only after the required operand values exist.

### Key insight

One expression needs both a structural view and a temporal view. Neither view alone predicts every side effect and value.

### Simplification or limitation

Only calls to `mark` are observed directly; operator-completion order is inferred from the language rules and resulting values. The diagram omits exceptions, custom special methods, asynchronous suspension, callbacks, and concurrency.

## 11. Language and implementation conclusion

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| Mixed arithmetic grouped by precedence while operand calls were evaluated left to right. | Language guarantee plus observation | Documented for Python 3.14.7; observed on CPython 3.14.4 | Do not infer bytecode shape from the trace. |
| Chained power grouped right and produced `512`, while operand calls remained left to right. | Language guarantee plus observation | Python/CPython 3.14.4 | The same semantic prediction applies to conforming Python implementations. |
| `and`, `or`, and the conditional expression skipped unneeded code. | Language guarantee plus observation | Python/CPython 3.14.4 | Custom truth testing could add effects not represented here. |
| Callable and argument expressions completed before the function body recorded invocation. | Language guarantee plus observation | Python/CPython 3.14.4 | A failing argument would stop the path before invocation. |
| Normal assignment evaluated its right side before target expressions; augmented assignment evaluated its target once first. | Language guarantee plus observation | Python/CPython 3.14.4 | Custom item and in-place methods can add effects while preserving this high-level order. |
| Exact event formatting and test execution are properties of this artifact. | Tooling observation | CPython 3.14.4 | Other runs should compare values and order, not runtime speed. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular GIL-enabled build was executed.
- Python 3.14.7 documentation was audited, but that maintenance release was not the runtime used.
- Built-in operand types are used; reflected, subclass, and in-place custom-method dispatch is not tested.
- Event logging itself is a side effect, but it is deterministic and does not influence branch truth values.
- The trace records operand-producing calls, not internal interpreter steps or operator opcodes.
- No exception path is executed; exercises require the learner to add and trace one.
- No comparison chain, comprehension, generator, `await`, descriptor, callback, or concurrent mutation is included.
- This is not a benchmark and supports no latency, allocation, or optimization claim.

## 13. Follow-up

- Add a controlled raising operand and record which later events disappear.
- Define a tiny custom numeric type that records normal and reflected method calls, then classify that as data-model evidence for `PY-OBJ-040`.
- Extend the trace to comparison chaining in `PY-FND-050`, proving that the middle expression evaluates once.
- Compare normal and augmented assignment with a mutable aliased operand in `PY-FND-020` or the data-model unit.
- Add a generator-expression case only when studying eager leftmost-iterable evaluation and later lazy work.

## 14. Authoritative sources

1. [Python 3.14.7 Language Reference — Evaluation order and operator precedence](https://docs.python.org/3.14/reference/expressions.html#evaluation-order), accessed 2026-08-29.
2. [Python 3.14.7 Language Reference — Boolean operations, assignment expressions, and conditional expressions](https://docs.python.org/3.14/reference/expressions.html#boolean-operations), accessed 2026-08-29.
3. [Python 3.14.7 Language Reference — Calls](https://docs.python.org/3.14/reference/expressions.html#calls), accessed 2026-08-29.
4. [Python 3.14.7 Language Reference — Assignment and augmented assignment statements](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements), accessed 2026-08-29.
5. [PEP 572 — Assignment Expressions, evaluation-order change](https://peps.python.org/pep-0572/#change-to-evaluation-order), accessed 2026-08-29.
