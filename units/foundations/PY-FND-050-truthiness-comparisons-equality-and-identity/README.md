# PY-FND-050 — Truthiness, comparisons, equality, and identity

[Curriculum entry](../../../CURRICULUM.md#py-fnd-050) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-FND-050`

## Physical Notebook Core

### Problem this concept solves

Python lets any object participate in a condition and lets types define what their values mean for comparison. That flexibility is useful only when truth, equality, identity, ordering, and absence remain separate questions.

### One-sentence mental model

> Truth asks an object for a yes/no interpretation, equality asks its types for a value relation, identity asks whether both expressions produced the very same object, and a comparison chain evaluates each written operand at most once.

### One important visual

```text
value used by if / while / bool
          |
          v
   has __bool__? ---- yes ---> call it; require bool
          |
          no
          v
    has __len__? ---- yes ---> call it; 0 is false, positive is true
          |
          no
          v
        true by default

left == right  ---> type-defined value comparison
left is right  ---> same-object test; never customized
```

#### How to read this visual

Follow the truth-testing tree downward and stop at the first available hook. Then read the two comparison lines independently: `==` and `is` ask different questions even when they happen to return the same Boolean.

#### Key insight

Truthiness is a protocol, equality is a relation chosen by types, and identity is sameness. None is a reliable substitute for another.

#### Simplification or limitation

This is a language-level decision model, not CPython control flow or memory layout. It omits exceptions from hooks, rich-comparison fallback between operand types, non-Boolean comparison results, chained-comparison reuse, and implementation-specific object caching; those boundaries appear below.

### Governing rules or invariants

1. `None`, `False`, numeric zero, and empty built-in containers are falsy; most other objects are truthy.
2. Truth testing calls `__bool__()` first, otherwise `__len__()`, otherwise treats the object as true; a hook may raise instead of producing a truth value.
3. `==` and ordering operators are type-defined operations; `is` and `is not` test identity and cannot be customized.
4. A comparison chain evaluates each operand expression at most once and stops when one comparison is false.
5. Use `is None` for the `None` singleton, and use a private unique sentinel when `None` or another falsy object is valid data.
6. Never infer portable identity from CPython interning or object reuse observed for equal strings, integers, or immutable constants.

### Minimal example

```python
MISSING = object()


def setting_or_default(settings, key, default):
    value = settings.get(key, MISSING)
    if value is MISSING:
        return default
    return value


settings = {"retries": 0, "label": "", "owner": None}

assert setting_or_default(settings, "missing", 3) == 3
assert setting_or_default(settings, "retries", 3) == 0
assert setting_or_default(settings, "label", "default") == ""
assert setting_or_default(settings, "owner", "system") is None
```

Expected reasoning:

1. `dict.get` returns the unique sentinel only when the key is absent.
2. Identity testing recognizes that exact sentinel without invoking user-defined equality.
3. Present values are returned unchanged, even when their truth value is false.

### One failure or misconception

**Mistake:** “`if value:` tells me whether the caller supplied a value.”

**Correction:** It tells you only the value's truth interpretation. Absence, `None`, `False`, zero, and empty data may be different domain states and need an explicit sentinel or state representation.

### Important trade-offs

- Truthiness makes ordinary conditions compact, but an API boundary should use explicit state checks when falsy values carry distinct meanings.
- Value equality is expressive, but custom comparison code can be expensive, effectful, non-Boolean, or exception-raising; identity is narrower and intentionally non-customizable.
- Chained comparisons avoid duplicate evaluation and match mathematical notation, but a named intermediate can be clearer when calls have effects or the predicates represent different domain concepts.

### Interview-revision cues

- Reconstruct: `__bool__` → `__len__` → true by default.
- Contrast: `==` asks value; `is` asks same object.
- Trace: in `low() < middle() <= high()`, evaluate `middle()` once and skip `high()` if the first comparison is false.
- Defend: distinguish missing, present-`None`, present-falsy, and present-truthy states.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Foundations and execution |
| Canonical ID | `PY-FND-050` |
| Learning outcome | Use truthiness, comparisons, identity, equality, chained comparison, and sentinel patterns correctly |
| Hard prerequisites | `PY-FND-020`, `PY-FND-040` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D2 |
| Scope | Language |
| Size | M |
| Evidence profile | E+C+D |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4 on Linux x86_64 |
| Last source audit | 2026-08-29 |
| Artifact state | Approved |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Predict truth testing for built-ins and user-defined objects, including hook priority, invalid hook results, and exception propagation.
2. Separate equality, ordering, and identity; explain rich-comparison fallback through `NotImplemented` without confusing it with `NotImplementedError`.
3. Trace chained comparisons with exact operand-evaluation count, rich-comparison calls, short-circuit paths, and possible failures.
4. Design backend boundaries that preserve valid `None`, zero, `False`, and empty values by choosing an explicit sentinel or state model.
5. Identify implementation-dependent identity observations and version-sensitive behavior without converting them into language guarantees.

Required evidence:

- Reconstruct the truth-resolution tree and the equality-versus-identity visual without reading the note.
- Complete prediction and debugging exercises covering custom truth hooks, a short-circuited comparison chain, equality fallback, and a sentinel-safe API boundary.
- Implement or review one realistic lookup/default boundary whose tests distinguish missing, `None`, zero, `False`, empty data, and a truthy value.
- Explain the Python 3.11 versus 3.14 `NotImplemented` truth-testing boundary and reproduce the controlled experiment's semantic observations.

Initialization and publication create a source-audited, executed, and tested artifact. They do not constitute learner evidence and do not advance the `Not started` learning state.

## 2. Prerequisite bridge

Both prerequisite artifacts are approved, but neither has recorded learning evidence. These bridges are sufficient to begin accurately; they do not complete either prerequisite.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | [`PY-FND-020`](../PY-FND-020-objects-names-references-and-mutability/README.md) | Supplies objects, bindings, value, identity, and aliasing | Every expression produces an object. Two names may refer to one object, two distinct objects may expose equal values, and `is` tests the first relation while `==` asks the types about the second. |
| Hard | [`PY-FND-040`](../PY-FND-040-expressions-evaluation-order-and-operators/README.md) | Supplies grouping, left-to-right evaluation, and short-circuit demand | First determine expression shape, then trace only demanded operands. Boolean operations and comparison chains may skip later expressions; grouping is not a runtime schedule. |

Recommended prerequisite action: draw one name-to-object graph from `PY-FND-020`, then trace one short-circuit expression from `PY-FND-040` before attempting this unit's comparison-chain practice.

## 3. Vocabulary and professional English

### Truthiness

| Item | Content |
|---|---|
| Pronunciation | TROO-thee-ness |
| Simple English meaning | Whether a value acts as true or false in a condition |
| Hindi cue | condition में value सच या झूठ मानी जाएगी |
| Meaning in this Python context | The result of Python's truth-value-testing protocol, not a claim that the object is literally `True` or `False` |

Natural examples:

1. An empty list has false truthiness.
2. A non-empty string is truthy even when its text is `"false"`.
3. A custom object can define truthiness through `__bool__`.
4. **Interview:** “I would trace the object's truth protocol rather than compare it to `True`.”
5. **Engineering discussion:** “Truthiness is too coarse here because zero and absence have different business meanings.”

### Reflexive

| Item | Content |
|---|---|
| Pronunciation | rih-FLEK-siv |
| Simple English meaning | Related to itself under the same rule |
| Hindi cue | खुद के साथ relation सही होना |
| Meaning in this Python context | An equality relation is reflexive when `x == x` is true; NaN is an important non-reflexive numeric exception |

Natural examples:

1. Ordinary integer equality is reflexive.
2. A broken equality implementation may fail the reflexive rule.
3. Not every domain relation should be modeled as equality.
4. **Interview:** “NaN is the counterexample, so I will not assume every value equals itself.”
5. **Engineering discussion:** “We need reflexive and symmetric equality before these objects can be reliable cache keys.”

### Sentinel

| Item | Content |
|---|---|
| Pronunciation | SEN-tih-nuhl |
| Simple English meaning | A special marker representing a state outside normal data |
| Hindi cue | अलग पहचान वाला विशेष संकेत |
| Meaning in this Python context | A deliberately unique object recognized by identity, often used to distinguish absence from every valid return value |

Natural examples:

1. The sentinel means that the key was not present.
2. `None` works as a sentinel only when `None` is not valid data.
3. A module-private `object()` sentinel avoids collision with ordinary values.
4. **Interview:** “I use `is MISSING` because the sentinel's identity, not its value, defines the state.”
5. **Engineering discussion:** “Do not serialize this process-local sentinel; encode the missing state explicitly at the boundary.”

### Dispatch

| Item | Content |
|---|---|
| Pronunciation | dih-SPATCH |
| Simple English meaning | Choosing which implementation should handle an operation |
| Hindi cue | सही implementation चुनना |
| Meaning in this Python context | The interpreter's selection and fallback among operand types' rich-comparison methods |

Natural examples:

1. Equality dispatch may ask both operand types before falling back.
2. Returning `NotImplemented` keeps comparison dispatch open.
3. Calling `__eq__` directly bypasses the operator's full fallback behavior.
4. **Interview:** “`NotImplemented` is a dispatch signal, not the final Boolean result.”
5. **Engineering discussion:** “Cross-type equality needs a documented dispatch policy and symmetry tests.”

## 4. Deep explanation

### 4.1 Why Python needs truth testing

Conditions need a single decision, but Python values represent many domains: an integer can count retries, a collection can contain work, and a service object can model readiness. Requiring every condition to compare against a literal Boolean would be noisy and would still leave open how other values convert to that Boolean.

Python therefore defines a truth-testing protocol. `if value`, `while value`, `bool(value)`, `not value`, and the decision points inside `and` and `or` ask for the object's truth value. The object does not need to be equal or identical to `True`.

The protocol is convenient within a well-defined domain. It is insufficient when several falsy states mean different things. A request field can be missing, explicitly `None`, zero, `False`, an empty string, or an empty collection; a single `if value` collapses all those states.

### 4.2 Formal truth-testing protocol

The public contract is:

1. If the type supplies `__bool__`, call it and require a real `bool` result.
2. Otherwise, if the type supplies `__len__`, call it; zero means false and a positive length means true.
3. Otherwise, the object is true.
4. If the selected hook raises, truth testing propagates the exception instead of inventing a Boolean.

The standard falsy built-ins include `None`, `False`, numeric zeros, and empty strings and containers. The precise built-in list and protocol are documented in [Python 3.14.7 Built-in Types — Truth Value Testing](https://docs.python.org/3.14/library/stdtypes.html#truth-value-testing). The hook contracts appear in the [Python 3.14.7 Data Model — `object.__bool__`](https://docs.python.org/3.14/reference/datamodel.html#object.__bool__) and [`object.__len__`](https://docs.python.org/3.14/reference/datamodel.html#object.__len__).

```python
class Window:
    def __init__(self, open_slots: int) -> None:
        self.open_slots = open_slots

    def __bool__(self) -> bool:
        return self.open_slots > 0
```

`__bool__` should express a stable, unsurprising predicate. A truth hook that performs network I/O, consumes data, changes state, or depends on distant mutable state makes an ordinary `if window` unexpectedly costly or effectful. In those cases, a named method such as `window.has_capacity()` exposes the operation honestly.

`__len__` is a fallback, not a second vote. If a class defines both hooks, Python does not call `__len__` after `__bool__` returns `False`. A non-Boolean `__bool__` result raises `TypeError`, while a negative `__len__` result raises `ValueError` in the tested runtime.

### 4.3 Boolean operators consume truth but return values

Truth testing and Boolean results are related but not identical:

- `not x` always returns `True` or `False` after truth-testing `x`;
- `x and y` returns `x` when `x` is falsy, otherwise it evaluates and returns `y`;
- `x or y` returns `x` when `x` is truthy, otherwise it evaluates and returns `y`.

This makes `cached or load()` a value-selection expression, not merely a Boolean calculation. It is correct only when every falsy cached value means “load instead.” It is wrong when an empty cached collection, zero limit, empty label, or explicit `False` is a valid hit.

The short-circuit evaluation mechanism is introduced in `PY-FND-040`; this unit adds the exact truth protocol and the domain-state question.

### 4.4 Comparisons and comparison chains

Python's comparison family includes ordering (`<`, `<=`,
`>`, `>=`), value equality (`==`, `!=`), identity (`is`, `is not`), and membership (`in`, `not in`). They share one precedence level and support chaining. The Language Reference specifies that every operand expression in a chain is evaluated at most once. See [Python 3.14.7 Language Reference — Comparisons](https://docs.python.org/3.14/reference/expressions.html#comparisons).

For:

```python
low() < middle() <= high()
```

the useful conceptual expansion is:

```python
_middle = middle()
low() < _middle and _middle <= high()
```

This is a reasoning model, not a source-to-source rewrite: the real chain has its own grammar and temporary handling. The model correctly preserves the two crucial properties:

- `middle()` is evaluated once and its result participates in both neighboring comparisons;
- `high()` is skipped if the first comparison is false.

A mixed-direction chain means two adjacent comparisons share their middle operand; it does not infer any relation between the two outer operands.

Rich comparison methods may return a non-Boolean object. A standalone expression can expose that result; when a condition or chain needs a decision, Python truth-tests it. Most application-level comparison methods should return `bool` or `NotImplemented` because exotic result objects make control flow harder to reason about.

### 4.5 Equality is a type-defined relation

`left == right` asks the operand types to implement a notion of equal value. Distinct objects can compare equal, and one class can decide that only selected fields define value. Classes that do not customize equality inherit identity-based default behavior; default ordering is unavailable and raises `TypeError`.

Rich comparison methods can return the singleton `NotImplemented` when they do not support the other operand. That return is a signal to comparison dispatch: the interpreter may try the reflected operation or another fallback. If every equality attempt declines, `==` and `!=` fall back to identity-based results. Ordering normally raises `TypeError` when no implementation accepts the pair. These details are documented in [Python 3.14.7 Data Model — Rich comparison methods](https://docs.python.org/3.14/reference/datamodel.html#object.__eq__).

```python
class ValueToken:
    def __init__(self, key: str) -> None:
        self.key = key

    def __eq__(self, other):
        if not isinstance(other, ValueToken):
            return NotImplemented
        return self.key == other.key
```

Do not write `return False` merely because the right operand has another type when that other type might know how to compare the pair. Do not raise `NotImplementedError`: it is an exception with a different purpose. And do not call `left.__eq__(right)` when the question is how `left == right` behaves; the direct call observes one hook, while the operator owns the complete protocol.

Python does not automatically derive all ordering relations from one method, and it does not enforce reflexivity, symmetry, transitivity, inverse relations, or equality/hash consistency. Designing those contracts in full belongs to `PY-BLT-080`.

### 4.6 Identity is exact sameness

`left is right` is true exactly when both expressions produce the same object. The operator cannot be customized, applies to any two objects, and does not call `__eq__`. See [Python 3.14.7 Language Reference — Identity comparisons](https://docs.python.org/3.14/reference/expressions.html#identity-comparisons).

Identity is appropriate when sameness itself is the contract:

- compare with `None` using `is None` or `is not None`;
- recognize a private unique sentinel using `is`;
- verify deliberate aliasing or ownership behavior in tests.

Identity is not a faster spelling of equality. CPython may reuse some immutable objects, literals, or constants, and another expression, process, build, version, or interpreter may not. `is` with strings or numbers therefore encodes an implementation accident rather than a value requirement.

The numeric result of `id(obj)` is useful only as a diagnostic token during the object's lifetime. This unit uses Boolean identity relations and never assigns business meaning to address-shaped values.

### 4.7 Sentinel design preserves state

`None` is the sole instance of `NoneType` and commonly represents absence. Use it as a sentinel only when `None` is outside the valid data domain. The constant's role is documented in [Python 3.14.7 Built-in Constants — `None`](https://docs.python.org/3.14/library/constants.html#None), and [PEP 8's programming recommendations](https://peps.python.org/pep-0008/#programming-recommendations) advise singleton comparisons with `is` and warn that `if x` is not equivalent to `if x is not None`.

When every ordinary object, including `None`, may be valid data, allocate a unique marker:

```python
_MISSING = object()


def read(mapping, key):
    value = mapping.get(key, _MISSING)
    if value is _MISSING:
        return "absent"
    return value
```

Keep a private sentinel inside the boundary that owns its meaning. A fresh `object()` has intentionally unhelpful display and serialization behavior; do not serialize it, send it to another process, or recreate it on the receiving side and expect identity to survive. Public libraries sometimes need a named singleton type with a stable representation and explicit copy/pickle behavior, but that is a larger API design than this local pattern.

### 4.8 Built-in comparison boundaries

The operator spelling does not promise that every pair is comparable in the same way.

| Values | Equality | Ordering | Important boundary |
|---|---|---|---|
| Real numeric built-ins | Cross-type mathematical comparison is supported | Supported except for complex values | `True == 1 == 1.0` can hold without identity or equal types |
| Complex numbers | Equality is supported | Raises `TypeError` | No natural total order is defined |
| Strings | Value equality | Lexicographic by Unicode code point | Human-language collation is a different problem |
| Lists and tuples | Value equality within their respective sequence types | Lexicographic within a compatible sequence type | A list and tuple with matching elements are not equal |
| Dictionaries | Equal key-value pairs | No ordering comparison | Insertion order does not create `<` semantics |
| Sets and frozensets | Same members | Proper/subset and superset relations | This is a partial order, not sorted sequence order |
| Ordinary class instances without rich comparisons | Identity-based default equality | Raises `TypeError` | Define a value relation deliberately when needed |
| NaN | Not equal to itself | Ordered comparisons are false | `nan is nan` can be true while `nan == nan` is false |

The important built-in boundaries are summarized in [Python 3.14.7 Built-in Types — Comparisons](https://docs.python.org/3.14/library/stdtypes.html#comparisons) and the Language Reference's [value-comparison section](https://docs.python.org/3.14/reference/expressions.html#value-comparisons).

### 4.9 Execution sequence

For the runnable successful chain:

```python
make_probe(events, "low", 1) \
    < make_probe(events, "middle", 5) \
    <= make_probe(events, "high", 10)
```

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Evaluate the left expression | `low` probe exists |
| 2 | Evaluate the middle expression | one `middle` probe exists and is retained |
| 3 | Apply `low < middle` | result is true, so the chain continues |
| 4 | Evaluate the right expression | `high` probe exists |
| 5 | Apply `middle <= high` | the retained middle object is reused; result is true |
| 6 | Complete the chain | final result is `True` |

If step 3 produces a falsy result, steps 4 and 5 do not occur.

## 5. Additional visual models

### 5.1 Truth-resolution decision tree

```text
truth_test(x)
     |
     +-- type(x) defines __bool__? -- yes --> x.__bool__()
     |                                      |-- bool --> use it
     |                                      `-- other/raise --> error
     |
     +-- type(x) defines __len__?  -- yes --> x.__len__()
     |                                      |-- 0        --> false
     |                                      |-- positive --> true
     |                                      `-- invalid/raise --> error
     |
     `-- neither --------------------------> true
```

#### How to read this visual

Start at the top and take the first available method branch. Never combine the answers from both hooks. An error exit means the object does not produce a truth value on that path.

#### Key insight

Truthiness is method resolution plus a strict result contract, not a universal conversion based on display text or equality with `True`.

#### Simplification or limitation

The tree describes language-visible behavior. It does not show special-method lookup internals, descriptors on the type, CPython slots, or the exact exception message.

### 5.2 Equality and identity on an object graph

```text
left  ───────> Token A {key: "job-7"}
alias ───────> Token A {key: "job-7"}
other ───────> Token B {key: "job-7"}

left is alias   -> True       same node
left == alias   -> True       ValueToken equality sees equal keys
left is other   -> False      different nodes
left == other   -> True       ValueToken equality sees equal keys
```

#### How to read this visual

Arrows represent references produced by names. For `is`, compare arrow destinations. For `==`, ignore graph position and apply the type's equality rule to the two objects.

#### Key insight

Equal value does not imply shared identity, while shared identity and equality can still diverge for exceptional value protocols such as NaN.

#### Simplification or limitation

This is a conceptual reference graph, not memory layout. `ValueToken` has a conventional reflexive equality rule; the picture omits fallback dispatch, subclasses, non-Boolean results, hashability, and mutation.

### 5.3 Chained-comparison value flow

```text
evaluate low()       evaluate middle()
      |                      |
      v                      v
     low  -------- < ------ middle
                              |
                  first false?+---- yes ----> False; skip high()
                              |
                              no
                              v
                        retain middle
                              |
                         evaluate high()
                              |
                              v
                         middle <= high
                              |
                              v
                         final truth value
```

#### How to read this visual

Follow the top comparison first. The middle object has two outgoing roles but only one incoming evaluation. The false branch exits before the rightmost expression.

#### Key insight

A chain shares the middle result and short-circuits between comparisons; it is not a series of independent binary expressions that reevaluate the source text.

#### Simplification or limitation

The visual assumes evaluation and comparison hooks complete normally and return ordinary Booleans. Exceptions, non-Boolean comparison results, subclass dispatch, and longer chains add steps without changing the at-most-once rule.

### 5.4 Four-state lookup partition

```text
lookup result
     |
     +-- is MISSING ------> absent: apply fallback
     |
     `-- present value
           |-- is None ---> present explicit None
           |-- falsy -----> present 0 / False / empty value
           `-- truthy ----> present truthy value
```

#### How to read this visual

Test identity with the sentinel first. Only values on the present branch may then be interpreted according to the domain; truthiness is not used to decide presence.

#### Key insight

One unique sentinel prevents a lossy two-way split from collapsing several valid application states into “missing.”

#### Simplification or limitation

The partition is an API design model. A real domain may distinguish more states, such as invalid, redacted, deferred, failed, or inherited; use a richer result type when those states matter.

## 6. Worked examples

### 6.1 Truth-hook resolution

The runnable source is [`examples/truthiness.py`](examples/truthiness.py).

```python
class BoolFirst:
    def __init__(self, ready: bool, events: list[str]) -> None:
        self.ready = ready
        self.events = events

    def __bool__(self) -> bool:
        self.events.append("__bool__")
        return self.ready

    def __len__(self) -> int:
        self.events.append("__len__")
        return 0
```

Prediction before execution:

`bool(BoolFirst(False, events))` returns `False` and records only `__bool__`. Python does not consult `__len__` after finding the higher-priority hook. A class with only `__len__` uses that method; a class with neither hook is true.

Observed on CPython 3.14.4:

```text
truth protocol: bool-first=False; events=__bool__
truth protocol: len-only=True; events=__len__
truth protocol: plain=True; events=none
sentinel values: ('fallback', 0, None, '')
invalid truth hooks: ('TypeError', 'ValueError')
NotImplemented truth: python=3.14; outcome=raises TypeError; warning=none
```

### 6.2 Comparison-chain trace

The runnable source is [`examples/comparisons.py`](examples/comparisons.py).

```python
result = (
    make_probe(events, "low", 1)
    < make_probe(events, "middle", 5)
    <= make_probe(events, "high", 10)
)
```

Prediction before execution:

The first two operands are evaluated, then `<` runs. Because it succeeds, the high operand is evaluated and `<=` reuses the existing middle object. The failed-chain variant never evaluates its rightmost producer.

Observed on CPython 3.14.4:

```text
chain success: result=True; events=evaluate:low → evaluate:middle → compare:low<middle → evaluate:high → compare:middle<=high
chain short-circuit: result=False; events=evaluate:left → evaluate:middle → compare:left<middle
```

### 6.3 Realistic configuration boundary

```python
from collections.abc import Mapping


MISSING = object()


def setting_or_default(
    settings: Mapping[str, object],
    key: str,
    default: object,
) -> object:
    value = settings.get(key, MISSING)
    if value is MISSING:
        return default
    return value
```

Why this design fits:

- the default applies only to absence;
- explicit `None`, `False`, zero, empty strings, and empty collections remain present values;
- identity testing cannot be redirected by a value's `__eq__` implementation;
- the small local sentinel does not leak into the returned API.

Alternatives include `if key in settings` followed by subscription, a result object with an explicit state, or a typed domain model. Membership plus lookup may perform two mapping operations; a result object is clearer when more than presence/absence matters. `None` is simpler when it is forbidden as input.

Failure modes include exporting the raw sentinel as data, recreating a “matching” `object()` and comparing it by identity, or sending the sentinel through serialization or another process.

### 6.4 Equality, identity, and NaN

Observed from the runnable comparison example:

```text
equality and identity: distinct=(equal=True, identical=False); alias=(equal=True, identical=True); unsupported-equal=False; direct-unsupported-is-NotImplemented=True
NaN: equal-to-self=False; unequal-to-self=True; identical-to-self=True
```

The `ValueToken` class defines equality by its key, so two objects can be equal without being identical. Its direct unsupported `__eq__` call returns `NotImplemented`; the `==` operator completes fallback and produces `False`. The NaN line proves that identity alone cannot be used to predict every type's equality behavior.

### 6.5 Debugging example

Keep the correction hidden until the learner attempts `PY-FND-050-P04`.

```python
def resolve_limit(overrides: dict[str, int | None], key: str) -> int | None:
    value = overrides.get(key)
    if value:
        return value
    return 100
```

Before editing, specify the intended behavior for an absent key, `None`, `0`, a positive value, and an invalid value. Then identify the first state transition this implementation collapses. Do not choose a sentinel or validation strategy until the contract is explicit.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| `if x` means `x is not None` | `None` is falsy | Many other valid objects are falsy | Test `0`, `False`, `""`, `[]`, and `None` separately |
| `x == True` is the explicit form of `if x` | Both seem Boolean | Equality and truth testing are different protocols | Use a truthy object not equal to `True` |
| `__len__` and `__bool__` are both consulted | Both influence truth in examples | `__bool__` wins; `__len__` is only the fallback | Define both and record calls |
| Any integer from `__bool__` is accepted | `bool` is related to integers | `__bool__` must return an actual `bool` | Return `1` and observe `TypeError` |
| A negative `__len__` merely means false | Negative counts look empty-like | Length must be a non-negative integer | Return `-1` and observe `ValueError` |
| `and` and `or` always return Booleans | They control Boolean flow | They return one evaluated operand | Use `[] and "x"` and `"cached" or load()` |
| `a < b < c` evaluates `b` twice | The conceptual `and` form repeats its text | A chain evaluates every operand expression at most once | Make `b()` append one event |
| The rightmost chain operand always runs | It appears in source | A false earlier comparison short-circuits the rest | Put a raising call on the skipped path |
| A chain compares every pair | Three values suggest all pair combinations | Only adjacent pairs are compared | Use a mixed-direction chain and ask what is known about its outer operands |
| `==` is built into the interpreter as field-by-field comparison | Many data classes behave that way | Types define equality; ordinary instances default to identity-based equality | Compare two plain instances with the same attributes |
| Unsupported `__eq__` should return `False` | The pair is not equal from the left type's view | Return `NotImplemented` so operator dispatch may ask the other type | Compare a base object with a cooperating other type |
| `NotImplemented` means `NotImplementedError` | Their names are similar | One is a dispatch singleton; the other is an exception | Return each from a toy `__eq__` and observe behavior |
| `is` is faster `==` | Both produce a Boolean | `is` asks sameness and cannot replace a value relation | Build two distinct equal lists |
| Equal strings or integers should be identical | One CPython run reuses them | Immutable reuse is implementation-dependent | Construct values differently or run another implementation |
| Every value equals itself | Most equality relations are reflexive | NaN is a standard non-reflexive exception | Test one stored NaN with both `is` and `==` |
| `None` is always the right sentinel | It is built in and unique | It fails when `None` is valid data | Test a mapping whose present value is `None` |
| A fresh `object()` can reproduce a sentinel | Both display similarly | Each call creates a distinct object | Compare two `object()` results with `is` |
| Comparison is pure and cheap | Built-in integer cases are simple | Custom methods may allocate, mutate, block, or raise | Add events or a deliberate exception to `__eq__` |

## 8. Complexity and performance

The language specifies comparison and truth behavior, not a universal cost. Type, value size, and custom code determine the work.

| Operation or design | Typical cost concern | Qualification |
|---|---:|---|
| Truth test using a built-in scalar | Usually constant-sized work | Do not generalize to custom `__bool__` or `__len__` |
| Truth test of a built-in collection | Normally constant-time length access | A user-defined length hook can perform arbitrary work |
| Identity comparison | Normally minimal implementation work | Choose it for semantics, not micro-optimization |
| Equality of bounded scalars | Usually small | Large integers, strings, bytes, and structured values depend on size and mismatch position |
| Sequence lexicographic comparison | Up to the shared compared prefix | Element comparisons may themselves be expensive or effectful |
| Custom rich comparison | Arbitrary user-code cost | It can allocate, log, lock, block, or raise |
| Successful chain of `n` operands | Up to `n - 1` comparisons | Each operand expression is evaluated at most once |
| Failed comparison chain | Remaining operands and comparisons are skipped | Work before the failure and truth testing of comparison results still occur |
| Sentinel identity check | Small and independent of payload equality | Its main benefit is collision-free state semantics |

No benchmark is needed for this unit. The evidence target is exact protocol behavior and evaluation count, not a machine-specific timing claim. Benchmark only a concrete comparison workload with fixed types, sizes, data distribution, implementation, warm-up, and trial policy.

## 9. Production relevance and trade-offs

- **API contracts:** Document whether absence differs from explicit `None`, zero, `False`, and empty data. Do not let incidental truthiness choose the contract.
- **Defaults and configuration:** `value or default` is correct only when all falsy values intentionally request the default. Use a sentinel when the default applies only to missing input.
- **Caches:** An empty cached result can be a valid hit. Treating it as a miss changes call count, latency, failure behavior, and observability.
- **Database and JSON boundaries:** SQL `NULL`, JSON `null`, missing fields, empty strings, and zero are separate states even when several map to falsy Python objects.
- **Custom types:** Keep `__bool__` cheap and unsurprising. Prefer a named predicate when readiness or validity can fail, block, mutate, or require context.
- **Equality:** Compare immutable value-defining fields and return `NotImplemented` for unsupported types. Equality/hash design and mutation constraints continue in `PY-BLT-080`.
- **Identity:** Use it for singletons, deliberate sentinels, and explicit alias contracts. Avoid identity assertions for harmless immutable reuse.
- **Side effects:** A comparison chain can call user code and stop partway. Tests should record the first failing or skipped event, not only the final Boolean.
- **Error handling:** Truth and comparison hooks may raise. Do not hide validation, authorization, or remote access inside an innocent-looking condition.
- **Concurrency:** Evaluation order is not atomicity. A hook that reads shared mutable state still needs an ownership or synchronization policy.
- **Security:** A truthy object is not automatically valid, authenticated, authorized, or safe. Truth testing cannot replace schema and policy checks.
- **Typing:** A union containing `None` documents a possible value, but runtime truthiness does not narrow every falsy alternative to the intended state. Use explicit checks that match the contract.
- **Testing:** Include missing, `None`, `False`, zero, empty containers, truthy values, unsupported comparison types, exceptions, and short-circuited calls.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| `__bool__` → `__len__` → true-by-default protocol | Language/data model | Longstanding Python behavior | Same behavior | Hook exceptions propagate |
| Chained comparisons evaluate operands at most once and short-circuit | Language | Longstanding Python behavior | Same behavior | Do not rewrite a middle call twice |
| Rich comparison may return `NotImplemented` | Language/data model | Longstanding Python behavior | Same behavior | The operator, not a direct dunder call, owns fallback |
| `is` and `is not` are non-customizable identity tests | Language | Longstanding Python behavior | Same behavior | Do not infer object layout from identity |
| `None` is a singleton and should be compared by identity | Language plus style guidance | Longstanding Python behavior | Same behavior | A private sentinel is needed when `None` is valid data |
| Truth-testing `NotImplemented` raises `TypeError` | Language/library behavior | Python 3.14 | In Python 3.11 it returns `True` and emits `DeprecationWarning`; do not truth-test it on either version | Return it only as an operator-dispatch signal |
| NaN is not equal to itself | Numeric value contract | Longstanding IEEE-754 behavior | Same behavior | Identity of one stored NaN can still be true |
| Exact reuse/interning of equal immutable objects | Implementation detail | Version/build/expression dependent | Never rely on it | Compare values with `==` |
| `id(obj)` equals a memory address | CPython implementation detail | Implementation-specific | Rely only on identity while the object lives | Other implementations may use another representation |

All runnable source uses Python 3.11-compatible syntax and has a version-aware assertion for `NotImplemented`. The source audit uses Python 3.14.7 and Python 3.11.15 documentation; execution occurred on the available CPython 3.14.4 runtime.

## 11. Practice brief

Exercises remain unsolved in [practice/README.md](practice/README.md).

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-FND-050-P01` | Predict | 2 | Resolve `__bool__`, `__len__`, default truth, and invalid-hook paths | [Practice](practice/README.md#py-fnd-050-p01-truth-protocol-ladder) |
| `PY-FND-050-P02` | Predict and trace | 3 | Prove middle-once evaluation and right-side short-circuiting in chains | [Practice](practice/README.md#py-fnd-050-p02-chain-with-one-middle) |
| `PY-FND-050-P03` | Implement and test | 3 | Preserve all present falsy values behind a sentinel-safe lookup contract | [Practice](practice/README.md#py-fnd-050-p03-preserve-present-values) |
| `PY-FND-050-P04` | Debug | 3 | Find the first collapsed domain state before changing fallback code | [Practice](practice/README.md#py-fnd-050-p04-the-disappearing-zero) |
| `PY-FND-050-P05` | Review and design | 4 | Review rich equality, `NotImplemented`, ordering assumptions, and identity misuse | [Practice](practice/README.md#py-fnd-050-p05-review-a-domain-key) |

## 12. Runtime experiment

[`EXP-01 — Truth and comparison protocol trace`](experiments/EXP-01-truth-and-comparison-protocol/README.md) records actual hook selection, invalid truth-hook failures, falsy-value preservation, chained-comparison evaluation, equality-versus-identity outcomes, NaN non-reflexivity, rich-comparison fallback, and the Python 3.14 `NotImplemented` boundary.

The experiment is language-focused. Its CPython 3.14.4 observations match the audited Python 3.14.7 contracts; no bytecode, address, benchmark, or optimizer claim is used as evidence.

## 13. Interview prompts

Do not read or store full answers before an attempt.

1. What exact resolution order does Python use for `if obj`, and what errors can a broken truth hook produce?
2. Why is `if value` not equivalent to `if value is not None`? Give a backend example where the difference changes behavior.
3. Trace `lower() < current() <= upper()` when the first comparison succeeds and when it fails. How many times can each function run?
4. Distinguish equality and identity using two distinct equal lists, one alias, and one NaN object.
5. Why should unsupported `__eq__` usually return `NotImplemented` instead of `False` or raising `NotImplementedError`?
6. When is `None` the right sentinel, and when is a private `object()` marker necessary?
7. Review `return cache.get(key) or load(key)` for value semantics, call count, exceptions, latency, and valid empty results.
8. Which truths about small-integer or string identity are portable, and which are only observations about a particular CPython run?
9. What changed about `bool(NotImplemented)` in Python 3.14, and what code should be written on a Python 3.11 interview platform?

A strong answer should eventually demonstrate:

- exact truth-protocol resolution and result constraints;
- separation of value equality, ordering, identity, and truth;
- at-most-once operand evaluation plus short-circuiting in a chain;
- correct `NotImplemented` dispatch reasoning;
- a sentinel choice justified by the data domain and boundary;
- explicit language, version, and implementation classifications.

## 14. Closed-book revision cues

Without reading the note:

1. Draw the truth-resolution decision tree, including all error exits.
2. List the standard falsy categories without claiming they are equal to each other.
3. Draw two distinct equal objects and one alias; label all four `is`/`==` results.
4. Reconstruct the successful and failed timelines for a three-operand comparison chain.
5. Explain why direct `__eq__` output can differ from the final `==` result.
6. Give one example where `None` works as a sentinel and one where it loses valid information.
7. Predict one stored NaN's `x is x`, `x == x`, and `x != x` results.
8. State the Python 3.11 and 3.14 outcomes of truth-testing `NotImplemented` and the version-independent rule to follow.
9. Refactor a cache fallback while preserving missing, falsy, exception, and call-count behavior.

## 15. Authoritative sources

Only sources opened and read during the 2026-08-29 audit are listed.

1. [Python 3.14.7 Built-in Types — Truth Value Testing, Boolean Operations, and Comparisons](https://docs.python.org/3.14/library/stdtypes.html#truth-value-testing), accessed 2026-08-29.
2. [Python 3.14.7 Language Reference — Comparisons, value comparisons, and identity comparisons](https://docs.python.org/3.14/reference/expressions.html#comparisons), accessed 2026-08-29.
3. [Python 3.14.7 Data Model — Rich comparison methods, `object.__bool__`, and `object.__len__`](https://docs.python.org/3.14/reference/datamodel.html#object.__eq__), accessed 2026-08-29.
4. [Python 3.14.7 Built-in Constants — `None` and `NotImplemented`](https://docs.python.org/3.14/library/constants.html), accessed 2026-08-29.
5. [Python 3.11.15 Built-in Constants — `NotImplemented`](https://docs.python.org/3.11/library/constants.html#NotImplemented), accessed 2026-08-29.
6. [PEP 8 — Programming Recommendations for singleton and truth checks](https://peps.python.org/pep-0008/#programming-recommendations), accessed 2026-08-29.
