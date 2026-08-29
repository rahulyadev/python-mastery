# PY-FND-040 — Expressions, evaluation order, and operators

[Curriculum entry](../../../CURRICULUM.md#py-fnd-040) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-FND-040`

## Physical Notebook Core

### Problem this concept solves

A compact Python expression can encode three different things: which parts belong together, which parts run first, and which parts may never run. Correct prediction requires separating those questions before reasoning about values or side effects.

### One-sentence mental model

> Parse the expression into groups first, then walk only the demanded groups in Python's specified evaluation order; every evaluated part may produce both a value and an observable effect.

### One important visual

```text
Source
    left() + factor() * count()

Grouping chosen by precedence
              +
             / \
       left()   *
               / \
        factor()  count()

Runtime timeline
    1 left() -> 2 factor() -> 3 count() -> 4 multiply -> 5 add
```

#### How to read this visual

Read the tree from its root to learn grouping: multiplication is the right operand of addition. Read the timeline from left to right to learn runtime order: Python still evaluates `left()` before it begins the multiplication group.

#### Key insight

Higher precedence means tighter grouping, not earlier evaluation. The left operand of `+` can run before the higher-precedence `*` operation on its right.

#### Simplification or limitation

The tree is a conceptual parse model, not CPython bytecode or a literal evaluation stack. It omits short-circuit gates, exceptions, overloaded operator methods, suspension, and assignment-target rules; those appear below.

### Governing rules or invariants

1. Parentheses and Python's grammar determine grouping; precedence is a compact description of that grammar.
2. Within an evaluated expression, Python evaluates component expressions from left to right, even when operators later combine them in another grouping.
3. `and`, `or`, and conditional expressions evaluate only the operand or branch required by the value already obtained.
4. Most operators at the same precedence group left to right; exponentiation and conditional expressions group right to left.
5. `and` and `or` return one of their evaluated operands; `not` returns a `bool`.
6. A normal assignment evaluates its right-hand expression before its target, while augmented assignment evaluates its target once before its right-hand expression.
7. An assignment expression binds one name and also yields the bound value; it is not a replacement for every assignment statement.

### Minimal example

```python
events: list[str] = []


def mark(label: str, value: int) -> int:
    events.append(label)
    return value


total = mark("left", 10) + mark("factor", 3) * mark("count", 4)

print(total)
print(events)
```

Observed on CPython 3.14.4:

```text
22
['left', 'factor', 'count']
```

Expected reasoning:

1. Precedence groups the expression as `left + (factor * count)`, so multiplication supplies the right operand of addition.
2. Component expressions are evaluated left to right, producing the event order `left`, `factor`, `count`.
3. After both multiplication operands exist, Python computes `3 * 4`; it then combines that result with `10`.

### One failure or misconception

**Mistake:** “Multiplication has higher precedence, so `factor()` must run before `left()`.”

**Correction:** Precedence answers “which values are combined?” Evaluation order answers “when are those values produced?” In this expression `left()` runs first, while its returned value waits for the right multiplication group.

### Important trade-offs

- Compact expressions can make data flow obvious, but hidden calls, mutation, I/O, or exceptions make temporal behavior harder to review.
- Short-circuiting can avoid unnecessary or unsafe work, but using `and` or `or` mainly to trigger side effects obscures intent.
- An assignment expression can remove duplicate work, but an ordinary assignment on its own line is often easier to inspect, test, and debug.

### Interview-revision cues

- Draw: rewrite the expression with explicit grouping before predicting output.
- Trace: number every evaluated operand and cross out every skipped operand.
- Defend: distinguish precedence, associativity, evaluation order, short-circuiting, and operator dispatch.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Foundations and execution |
| Canonical ID | `PY-FND-040` |
| Learning outcome | Predict expression evaluation, precedence, associativity, short-circuiting, assignment expressions, and side-effect order |
| Hard prerequisites | `PY-FND-010` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | Medium |
| Depth | D2 |
| Scope | Language |
| Size | M |
| Evidence profile | E+D |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4 on Linux x86_64 |
| Last source audit | 2026-08-29 |
| Artifact state | Approved |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Parenthesize a non-trivial expression according to Python's precedence and associativity rules without confusing grouping with runtime order.
2. Trace calls, operands, short-circuit gates, conditional branches, normal and augmented assignment targets, and exceptions in the exact order they can occur.
3. Use assignment expressions only where binding and consuming the same value improves clarity, and refactor side-effect-heavy expressions into explicit steps.
4. Explain where operator meaning depends on operand types without treating CPython bytecode as the language contract.

Required evidence:

- Reconstruct the “group first, trace second” model closed-book and draw one parse tree plus one execution timeline for an original expression.
- Complete prediction and debugging exercises that cover left-to-right evaluation, a right-associative operator, skipped operands, and normal versus augmented assignment timing.
- Review one realistic backend expression for duplicate work, hidden side effects, falsy-value assumptions, exception boundaries, and maintainability.

Initialization and publication create a source-audited, executed, and tested artifact. They do not constitute learner evidence and do not advance the `Not started` learning state.

## 2. Prerequisite bridge

`PY-FND-010` has a `Draft` artifact but no recorded learning evidence. This bridge is enough to begin accurately; it does not complete the prerequisite.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | [`PY-FND-010`](../PY-FND-010-python-syntax-and-execution/README.md) | Supplies the distinction between source text, parsing, expressions, statements, and execution | An expression is syntax that evaluates to a value. A statement performs a language-level action and may contain expressions. Python parses valid source before executing it; runtime evaluation follows the structure produced by that parse. |

Recommended prerequisite action: run the minimal execution demo from `PY-FND-010`, then identify which lines are statements and which nested parts are expressions.

## 3. Vocabulary and professional English

### Precedence

| Item | Content |
|---|---|
| Pronunciation | PRESS-uh-dens |
| Simple English meaning | A rule deciding which operation binds more tightly |
| Hindi cue | कौन-सा operator पहले group होगा |
| Meaning in this Python context | The grammar-based ranking that decides the implicit grouping of operators when parentheses do not make it explicit |

Natural examples:

1. Multiplication has higher precedence than addition.
2. Parentheses make the intended precedence unambiguous to a reader.
3. Precedence does not by itself tell us which function call runs first.
4. **Interview:** “I will parenthesize the expression before I trace its evaluation.”
5. **Engineering discussion:** “This condition is legal, but explicit parentheses would reduce precedence mistakes during review.”

### Associativity

| Item | Content |
|---|---|
| Pronunciation | uh-SOH-see-uh-TIV-uh-tee |
| Simple English meaning | The direction used to group repeated operators of one level |
| Hindi cue | समान precedence पर grouping की दिशा |
| Meaning in this Python context | The left-to-right or right-to-left grouping rule used when operators share a precedence level |

Natural examples:

1. Subtraction groups from left to right.
2. Exponentiation is a familiar right-associative exception.
3. Associativity is about the parse, not permission to reorder side effects.
4. **Interview:** “The power chain groups from the right, but its operand expressions are still evaluated left to right.”
5. **Engineering discussion:** “I added parentheses because few readers remember the associativity of nested conditional expressions.”

### Operand

| Item | Content |
|---|---|
| Pronunciation | OP-uh-rand |
| Simple English meaning | A value on which an operation works |
| Hindi cue | operator को मिलने वाला value |
| Meaning in this Python context | An expression whose resulting object is supplied to a unary, binary, Boolean, comparison, or other operator |

Natural examples:

1. In `price * quantity`, both names are operand expressions.
2. Evaluating an operand can call a function or raise an exception.
3. The right operand of `and` may be skipped.
4. **Interview:** “Both operands are evaluated before the binary addition is applied.”
5. **Engineering discussion:** “The operand looks cheap, but the property access performs a remote lookup in this abstraction.”

### Short-circuit

| Item | Content |
|---|---|
| Pronunciation | SHORT SUR-kit |
| Simple English meaning | Stop once the result or selected value is already determined |
| Hindi cue | जरूरत न हो तो अगला expression न चलाना |
| Meaning in this Python context | The rule by which `and`, `or`, and conditional expressions skip an unneeded operand or branch |

Natural examples:

1. The guard short-circuits before calling the fallback.
2. An exception in a skipped operand cannot occur on that path.
3. Short-circuiting returns an operand for `and` and `or`, not necessarily a Boolean.
4. **Interview:** “The second call is absent from the trace because the first operand short-circuited.”
5. **Engineering discussion:** “Relying on short-circuiting is clear for a guard, but unclear when the real goal is an incidental side effect.”

## 4. Deep explanation

### 4.1 Ask two questions, in order

For any expression that is not immediately obvious, answer these questions separately:

1. **What is the shape?** Insert conceptual parentheses using the grammar, precedence, and associativity rules.
2. **What is the timeline?** Within that shape, trace component expressions from left to right, applying short-circuit and construct-specific rules.

For example:

```python
left() + factor() * count()
```

The shape is:

```python
left() + (factor() * count())
```

The operand timeline is:

```text
left() -> factor() -> count()
```

Only after values are available can the grouped operations finish. This distinction matters whenever an operand can mutate state, consume an iterator, perform I/O, log, raise, or return a type with overloaded operator behavior.

### 4.2 Precedence establishes grouping

Python's operator-precedence table runs from tightly binding primaries and exponentiation down through arithmetic, shifts, bitwise operators, comparisons, Boolean operators, conditional expressions, `lambda`, and assignment expressions. Operators in the same row generally group left to right. Exponentiation and conditional expressions group right to left. These are language grammar rules, not optimizer hints. See [Python 3.14 Language Reference — Operator precedence](https://docs.python.org/3.14/reference/expressions.html#operator-precedence).

```python
10 - 3 - 2       # groups as (10 - 3) - 2
2 ** 3 ** 2      # groups as 2 ** (3 ** 2)
```

Parentheses override implicit grouping and document intent:

```python
10 - (3 - 2)
(2 ** 3) ** 2
```

The power operator has an asymmetric-looking unary edge case. Unary minus on the left applies after exponentiation, while a unary operator is accepted inside the exponent on the right:

```python
-2**2       # -(2**2), so -4
(-2) ** 2   # 4
2**-2       # 2 ** (-2), so 0.25
```

This behavior is stated in the footnote to the official precedence table; memorizing only a vertical ranking without the power footnote is incomplete.

### 4.3 Evaluation is left to right

The Language Reference states that Python evaluates expressions from left to right and, for normal assignment, evaluates the right-hand expression before the left-hand target. Its examples include expression lists, dictionary items, nested arithmetic, calls, and parallel assignment. See [Python 3.14 Language Reference — Evaluation order](https://docs.python.org/3.14/reference/expressions.html#evaluation-order).

Left-to-right evaluation does not flatten the parse tree. In `left() + factor() * count()`, Python evaluates `left()` first, then enters the grouped right operand and evaluates `factor()` followed by `count()`. The multiplication can then finish, followed by the addition.

An exception stops the current path immediately:

```python
first() + failing() + never_reached()
```

If `failing()` raises, `never_reached()` is not evaluated and no outer operation waiting on the failed value completes. Exception propagation therefore belongs on the execution timeline.

### 4.4 Calls evaluate before invocation

For a call, the primary expression producing the callable is evaluated, then argument expressions are evaluated, and only then is the call attempted. A parameter-binding error does not retroactively undo side effects from already evaluated argument expressions. The call contract is documented in [Python 3.14 Language Reference — Calls](https://docs.python.org/3.14/reference/expressions.html#calls).

```python
handler_factory()(load_left(), right=load_right())
```

A useful trace is:

```text
handler_factory -> load_left -> load_right -> bind/call handler
```

This does not mean default parameter expressions run at each call; default-value timing belongs to `PY-FIT-020`.

### 4.5 Short-circuiting makes evaluation conditional

For `x and y`, Python evaluates `x`. If `x` is false, that value is returned and `y` is skipped; otherwise `y` is evaluated and returned. For `x or y`, a true `x` is returned and `y` is skipped; otherwise `y` is evaluated and returned. Neither operator promises a `bool` result. In contrast, `not x` produces a Boolean. See [Python 3.14 Language Reference — Boolean operations](https://docs.python.org/3.14/reference/expressions.html#boolean-operations).

```python
cached or load()
ready and publish()
```

These can be clear when “use a fallback” or “guard an operation” is genuinely the contract. They are unsafe shorthand when a meaningful cached value may be falsy or when the skipped call contains a required side effect. `PY-FND-050` develops truth testing and sentinel design in depth.

A conditional expression first evaluates its condition, then exactly one branch:

```python
cached if cache_is_valid else load()
```

The textual first expression is not the first runtime event; the middle condition is. This is a construct-specific rule, not a contradiction of left-to-right evaluation.

### 4.6 Normal and augmented assignment differ

In a normal assignment, Python evaluates the complete right-hand expression first and then assigns its result to target lists from left to right. For a subscript target, evaluating the target later includes evaluating its container and subscript expressions. See [Python 3.14 Language Reference — Assignment statements](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements).

```python
container()[key()] = right_hand_side()
```

The observable order is:

```text
right_hand_side -> container -> key -> set item
```

Augmented assignment is not just textual substitution. It evaluates its target once, then the right-hand expression, applies the operation—possibly in place—and writes the result back to that original target:

```python
container()[key()] += right_hand_side()
```

The corresponding order begins:

```text
container -> key -> get item -> right_hand_side -> operation -> set item
```

The target-once and left-before-right rules are specified in [Python 3.14 Language Reference — Augmented assignment](https://docs.python.org/3.14/reference/simple_stmts.html#augmented-assignment-statements). Mutation versus rebinding and alias effects connect back to `PY-FND-020`.

### 4.7 Assignment expressions bind and return one value

An assignment expression—often called the walrus operator—evaluates its right side, binds the result to one identifier, and yields that same result as the value of the larger expression:

```python
while chunk := read_chunk():
    process(chunk)
```

Here each call result is produced once, bound to `chunk`, tested, and, on the continuing path, reused in the body. Assignment expressions were added in Python 3.8. They can target a single name, not an attribute, subscript, or unpacking pattern, and some syntactic positions require parentheses. See [Python 3.14 Language Reference — Assignment expressions](https://docs.python.org/3.14/reference/expressions.html#assignment-expressions) and [PEP 572 — Syntax and semantics](https://peps.python.org/pep-0572/#syntax-and-semantics).

Use `:=` when the name improves the surrounding expression and eliminates a meaningful duplicate evaluation. Prefer a separate statement when the binding has a long lifetime, needs explanation, or makes the condition visually dense.

### 4.8 Operators receive objects, not abstract symbols

The grammar determines grouping and evaluation order, but operand types determine much of an operator's meaning. For built-ins, `+` can add numbers or concatenate compatible sequences; `*` can multiply numbers or repeat a sequence; bitwise operators work on integers and may be defined by custom objects. User-defined types can implement special methods for arithmetic and reflected operations. See [Python 3.14 Data Model — Emulating numeric types](https://docs.python.org/3.14/reference/datamodel.html#emulating-numeric-types).

This yields a disciplined boundary:

1. Evaluate the operand expressions in the language-defined order.
2. Apply the operator according to the operand types' protocol.
3. If the operation raises, stop the current expression path.

Full dispatch precedence among normal, reflected, subclass, and in-place methods belongs to `PY-OBJ-040`; this unit needs only the fact that an operator may invoke user code and have non-constant cost.

### 4.9 Execution sequence

For the tested expression:

```python
mark("left", 10) + mark("factor", 3) * mark("count", 4)
```

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Parse according to precedence | Shape is `left + (factor * count)` |
| 2 | Evaluate the left operand of `+` | Event `left`; pending value `10` |
| 3 | Evaluate the left operand of `*` | Event `factor`; pending value `3` |
| 4 | Evaluate the right operand of `*` | Event `count`; pending value `4` |
| 5 | Apply multiplication | Right side of `+` becomes `12` |
| 6 | Apply addition | Final value becomes `22` |

## 5. Additional visual models

### 5.1 Compact precedence ladder

```text
tighter binding
      |
      v
primaries: attribute, call, subscription
await
power **
unary +  -  ~
*  @  /  //  %
+  -
left shift, right shift
&
^
|
comparisons, membership, identity
not
and
or
conditional: value_if_true if condition else value_if_false
lambda
assignment expression :=
      |
      v
looser binding
```

#### How to read this visual

Start at the top. A construct higher on the ladder binds more tightly than one below it unless parentheses specify another shape. For operators on one line, consult associativity; do not use vertical position as a runtime schedule.

#### Key insight

The ladder helps reconstruct implicit parentheses. It cannot replace the separate left-to-right evaluation trace.

#### Simplification or limitation

This is a revision aid, not the formal grammar. It compresses the comparison family, omits syntax restrictions and footnotes, and does not show exponentiation's special relationship with a unary operator on its right.

### 5.2 Short-circuit gates

```text
x and y
   evaluate x
      |-- x is false --> return x; skip y
      `-- x is true  --> evaluate and return y

x or y
   evaluate x
      |-- x is true  --> return x; skip y
      `-- x is false --> evaluate and return y

a if condition else b
   evaluate condition
      |-- true  --> evaluate and return a; skip b
      `-- false --> evaluate and return b; skip a
```

#### How to read this visual

Begin at the first evaluation in each block, follow exactly one arrow, and cross out the skipped expression. “True” and “false” describe truth testing, not necessarily objects equal to `True` or `False`.

#### Key insight

Skipped code has no effects on that path: it does not call, mutate, log, consume input, or raise.

#### Simplification or limitation

The gates omit how custom objects define truth values and which built-ins are falsy. Those contracts belong to `PY-FND-050`. The diagram also assumes the first evaluated expression completes normally.

### 5.3 Assignment timing contrast

```text
normal:     target()[key()] = rhs()
            rhs -> target -> key -> set

augmented:  target()[key()] += rhs()
            target -> key -> get -> rhs -> operate -> set
                     \___________/
                       same target
```

#### How to read this visual

Follow each arrow as a possible observable event. In the augmented path, the bracket underlines that the container and key expressions are evaluated once and the original target is reused for the write-back.

#### Key insight

Rewriting augmented assignment as ordinary assignment can change target evaluation count, timing, and mutation behavior even when the arithmetic result looks similar.

#### Simplification or limitation

The visual assumes subscript access succeeds and the operation returns normally. Descriptors, custom item methods, in-place methods, aliases, and exceptions can add effects without changing the high-level ordering rule.

### 5.4 Assignment-expression value flow

```text
read_chunk()
     |
     v
bind the returned object to chunk
     |
     v
the same object becomes the value of (chunk := read_chunk())
     |
     v
truth-test it for while ---- false ---> leave loop
     |
    true
     v
process(chunk)
```

#### How to read this visual

Follow the single produced object downward. The walrus expression does not call `read_chunk()` twice and does not create a second copy merely to return a value.

#### Key insight

Binding and consuming one evaluation result is the core benefit of `:=`.

#### Simplification or limitation

The diagram uses a conventional empty-chunk sentinel. It omits scope rules inside comprehensions, mandatory-parentheses positions, exceptions, and APIs where an empty value is valid data rather than termination.

## 6. Worked examples

### 6.1 Grouping versus evaluation trace

The runnable source is [`examples/evaluation_order.py`](examples/evaluation_order.py).

```python
value = mark(events, "left", 10) + (
    mark(events, "factor", 3) * mark(events, "count", 4)
)
```

Prediction before execution:

- value: `22`;
- operand events: `left`, `factor`, `count`;
- multiplication completes before the final addition, although `left` is the first evaluated operand.

Observed on CPython 3.14.4:

```text
precedence: value=22; events=left -> factor -> count
power: value=512; events=base -> inner-exponent -> outer-exponent
call: value=7; events=callee -> positional -> keyword -> invoke
short-circuit: values=(0, 'cached', 'loaded', 'ready'); events=and-left -> or-left -> fallback-left -> fallback-right -> condition -> if-branch
```

The power case demonstrates that `2 ** 3 ** 2` groups from the right while the three operand-producing calls still occur in source order.

### 6.2 Realistic backend fallback

```python
from collections.abc import Callable


def get_policy(
    key: str,
    read_cache: Callable[[str], dict[str, object] | None],
    read_store: Callable[[str], dict[str, object]],
) -> dict[str, object]:
    cached = read_cache(key)
    if cached is not None:
        return cached
    return read_store(key)
```

A tempting compression is:

```python
return read_cache(key) or read_store(key)
```

The compressed form changes the contract: it calls the store for every falsy cache result, not only for the explicit cache-miss sentinel. An empty dictionary may be a valid cached policy. The explicit version makes call count, fallback condition, return path, and exception boundary visible. It is a little longer but easier to test and review.

This example uses `is not None` as a boundary preview. Equality, identity, and sentinel reasoning are developed in `PY-FND-050`.

### 6.3 Assignment expression for chunked input

The runnable function is in [`examples/assignment_expressions.py`](examples/assignment_expressions.py).

```python
from collections.abc import Callable


def consume_chunks(read: Callable[[], bytes]) -> tuple[bytes, ...]:
    chunks: list[bytes] = []
    while chunk := read():
        chunks.append(chunk)
    return tuple(chunks)
```

Observed with the synthetic stream `b"alpha"`, `b"beta"`, `b""`:

```text
walrus chunks: (b'alpha', b'beta')
```

The test verifies exactly three reads: two yielded chunks and one terminating empty chunk. A separate assignment plus `break` would also be correct; prefer it if the loop needs multiple stop conditions or the empty value is valid data.

### 6.4 Debugging example

Keep the correction hidden until the learner attempts `PY-FND-040-P03`.

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
```

Before execution, predict the event list, the final `position`, and both list elements. Then reset all state and compare the reasoning with an augmented-assignment variant. The first task is to identify the target-versus-right-side timing rule, not to edit the functions.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| “Higher precedence runs first” | Arithmetic lessons use “do multiplication first” | Precedence groups; operand expressions still follow the language's evaluation order | Put event-recording calls on both sides of mixed operators |
| `2 ** 3 ** 2` groups from the left | Most binary operators group left to right | Exponentiation groups from the right | Compare it with `(2 ** 3) ** 2` |
| `-2**2` means `(-2) ** 2` | The minus looks attached to the literal | A negative number is a unary operation; power binds first on its left side | Evaluate it beside the explicitly parenthesized form |
| `and` and `or` always return Booleans | Their names sound Boolean | They return the last evaluated operand | Use empty and non-empty strings as trace values |
| A skipped operand can still raise | The source text contains the failing expression | An unevaluated operand performs no runtime action on that path | Put a raising function in a deliberately skipped branch |
| Call validation happens before argument effects | A bad call “should fail immediately” | Argument expressions are evaluated before the call is attempted | Add logging arguments to a call with a deliberate binding error |
| Normal subscript assignment evaluates its target first | The target is textually leftmost | The right-hand expression is evaluated before the normal assignment target | Make the right side change state read by the subscript |
| `target[key] += rhs` is identical to `target[key] = target[key] + rhs` | The formulas look equivalent | Augmented assignment evaluates the target once and may mutate in place | Count target evaluations and inspect aliases |
| `:=` can target an attribute or unpack values | Ordinary assignment can do both | An assignment expression directly targets one identifier | Compile a proposed attribute or unpacking target separately |
| Repeated comparisons are ordinary left-associated binaries | Most operators use one associativity direction | Comparison chains have dedicated semantics and middle expressions evaluate once | Defer the full trace to `PY-FND-050` |
| An arithmetic symbol guarantees cheap primitive work | The expression looks built in | Operand types may route an operator into user-defined methods | Use a tiny tracing class, labelled as data-model behavior |

## 8. Complexity and performance

Parsing and grouping rules do not give a universal runtime complexity for an operator. Cost depends on operand types, input sizes, invoked special methods, and skipped paths. Avoid claims such as “an operator is O(1)” without naming the concrete operation and types.

| Operation or design | Typical cost concern | Qualification |
|---|---:|---|
| Arithmetic on bounded machine-like values | Usually small relative to I/O | Python integers are arbitrary precision, so cost can grow with magnitude |
| Sequence concatenation or repetition | Depends on result size | The same `+` or `*` symbol can allocate and copy container elements |
| Custom operator method | Arbitrary user-code cost | May allocate, block, log, mutate, or raise |
| Short-circuited operand | Zero execution cost on the skipped path | The first operand and its truth test still run |
| Repeating an expensive expression | Repeats its full cost and effects | A separate assignment or careful `:=` can evaluate it once |
| Dense one-line expression | Low line count, potentially high review cost | Readability and correct change safety usually dominate micro-syntax |

No benchmark is needed for this unit: the important evidence is semantic order, not a machine-specific timing difference. Benchmark a real operator workload only after fixing types, sizes, implementation, version, warm-up, and measurement method.

## 9. Production relevance and trade-offs

- **Correctness:** Treat every call, property access, custom operator, and truth test as a possible effect or failure boundary while tracing.
- **Readability:** Use parentheses to document non-obvious grouping even when the grammar already gives the same result. Use intermediate names when a timeline cannot be explained in one breath.
- **API behavior:** All argument expressions run before invocation. A later binding `TypeError` does not prevent earlier argument-side effects.
- **Fallbacks:** `cached or load()` is only correct when every falsy cached value means “miss.” Prefer an explicit sentinel check when empty values are valid.
- **Error handling:** Short-circuiting and conditional expressions can guard unsafe work, but they are not substitutes for validation or exception policy.
- **Observability:** One expression may emit several logs or metrics before failing. Stable event labels make the first incorrect assumption visible in tests.
- **Mutation:** Augmented assignment can mutate an aliased object through an in-place method. The spelling does not guarantee either mutation or allocation.
- **Concurrency:** Evaluation order is not an atomicity guarantee. Another thread, task, process, signal handler, or callback may interact at boundaries defined elsewhere.
- **Security:** Do not hide authorization, validation, or audit effects behind optional short-circuit operands whose execution depends on unrelated truthiness.
- **Maintainability:** The walrus operator is valuable when the bound value is immediately meaningful. If a reviewer must scan backward to find why the name exists, use a statement.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| Left-to-right expression evaluation | Language | Longstanding Python behavior | Same behavior | Do not infer exact bytecode or optimizer strategy |
| Normal assignment evaluates the right side before the target | Language | Longstanding Python behavior | Same behavior | Target lists themselves assign left to right |
| Augmented assignment evaluates its target once before the right side | Language | Longstanding Python behavior | Same behavior | In-place mutation depends on the operand protocol |
| Assignment expression `:=` | Language | 3.8 | Same syntax and semantics in 3.11 | Some positions require parentheses; target is one name |
| Dict-comprehension key before value | Language | 3.8 | Same behavior in 3.11 | PEP 572 made this order explicit and changed earlier behavior |
| Matrix-multiplication operator `@` | Language and data-model protocol | 3.5 | Same syntax in 3.11 | No built-in type implements matrix multiplication |
| Exact numeric operator dispatch and reflected-method details | Language data model | Version-sensitive at edges | Reason from the Python 3.11 data model when interviewing | Three-argument reflected power behavior changed in Python 3.14 |
| Opcode sequence, adaptive cache, or temporary stack layout | CPython implementation detail | Version-specific | Do not rely on it | Disassembly may explain one build, never redefine the language contract |

All runnable source in this unit uses Python 3.11-compatible syntax. The source audit uses Python 3.14.7 documentation, while execution occurred on the available CPython 3.14.4 runtime.

## 11. Practice brief

Exercises remain unsolved in [practice/README.md](practice/README.md).

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-FND-040-P01` | Predict | 2 | Separate parse shape, operand timeline, operation timeline, and final value | [Practice](practice/README.md#py-fnd-040-p01-three-axis-expression-trace) |
| `PY-FND-040-P02` | Predict and explain | 3 | Trace skipped operands and returned operand values | [Practice](practice/README.md#py-fnd-040-p02-short-circuit-gates) |
| `PY-FND-040-P03` | Debug | 3 | Diagnose normal versus augmented assignment target timing | [Practice](practice/README.md#py-fnd-040-p03-the-moving-subscript) |
| `PY-FND-040-P04` | Review | 3 | Judge assignment-expression clarity and preserve exact call counts | [Practice](practice/README.md#py-fnd-040-p04-walrus-or-explicit-state) |
| `PY-FND-040-P05` | Design and review | 4 | Refactor a backend fallback without changing valid falsy results or effects | [Practice](practice/README.md#py-fnd-040-p05-honest-cache-fallback) |

## 12. Runtime experiment

[`EXP-01 — Expression grouping and side-effect trace`](experiments/EXP-01-expression-trace/README.md) records the actual order of marked operands for precedence, right-associative exponentiation, short-circuit gates, calls, normal assignment, and augmented assignment.

The experiment is language-focused. Its CPython 3.14.4 run reproduces outcomes predicted from the Python 3.14 Language Reference; it does not use bytecode as evidence or generalize from timing.

## 13. Interview prompts

Do not read or store full answers before an attempt.

1. In `left() + middle() * right()`, which call runs first, and which operation finishes first? Explain why those answers differ.
2. How can exponentiation group from the right while its operand-producing calls still appear left to right in a trace?
3. What values can `and` and `or` return, and how would you prove that an operand was skipped?
4. Why can `container()[key()] += rhs()` behave differently from the visually expanded normal assignment?
5. When does an assignment expression improve code, and which target forms and readability limits should a reviewer check?
6. A cache fallback uses `read_cache(key) or read_store(key)`. Review its value contract, call count, exceptions, observability, and valid empty results.

A strong answer should eventually demonstrate:

- explicit separation of grouping, evaluation order, and operator dispatch;
- precise short-circuit and conditional-branch traces;
- normal versus augmented assignment target timing;
- assignment-expression value flow and limitations;
- a maintainable production choice that preserves behavior and makes effects visible.

## 14. Closed-book revision cues

Without reading the note:

1. Draw the parse tree and runtime timeline for a mixed addition-and-multiplication expression containing three calls.
2. Write one left-associative and one right-associative counterexample with explicit parentheses and different results.
3. Reconstruct the short-circuit gates for `and`, `or`, and a conditional expression, including which value each returns.
4. Draw normal subscript assignment and augmented subscript assignment as event timelines.
5. Explain why all call arguments can have effects even when parameter binding later fails.
6. Write one clear use of `:=`, one legal but poor use, and one target form it cannot express.
7. Refactor a side-effect-heavy one-liner into statements without changing evaluation count or exception order.

## 15. Authoritative sources

Only sources opened and read during the 2026-08-29 audit are listed.

1. [Python 3.14.7 Language Reference — Expressions, Boolean operations, assignment expressions, conditional expressions, evaluation order, and operator precedence](https://docs.python.org/3.14/reference/expressions.html), accessed 2026-08-29.
2. [Python 3.14.7 Language Reference — Calls](https://docs.python.org/3.14/reference/expressions.html#calls), accessed 2026-08-29.
3. [Python 3.14.7 Language Reference — Simple statements, assignment and augmented assignment](https://docs.python.org/3.14/reference/simple_stmts.html), accessed 2026-08-29.
4. [Python 3.14.7 Data Model — Emulating numeric types](https://docs.python.org/3.14/reference/datamodel.html#emulating-numeric-types), accessed 2026-08-29.
5. [PEP 572 — Assignment Expressions, syntax, precedence, and evaluation-order change](https://peps.python.org/pep-0572/), accessed 2026-08-29.
