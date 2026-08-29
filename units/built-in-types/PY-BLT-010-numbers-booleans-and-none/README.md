# PY-BLT-010 — Numbers, booleans, and None

[Curriculum entry](../../../CURRICULUM.md#py-blt-010) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-BLT-010`

## Physical Notebook Core

### Problem this concept solves

Programs need to represent exact counts, approximate measurements, two-valued decisions, two-dimensional numeric values, and the absence of a value without silently confusing those domains.

### One-sentence mental model

> Choose the value domain first—exact integer, binary approximation, complex pair, Boolean decision, or absence—then reason about every conversion and operation as a possible domain change.

### One important visual

```text
incoming meaning
      │
      ├── exact whole quantity ───────────────> int
      ├── approximate real measurement ──────> float
      ├── real + imaginary components ───────> complex
      ├── truth result / two-state flag ─────> bool ──is-a subtype──> int
      └── no value supplied / no result ─────> None

mixed built-in arithmetic: bool/int ──> float ──> complex
                                      widening can discard exact integer detail
```

#### How to read this visual

Start at the meaning of the data, choose one horizontal branch, and only then select a Python type. Read the bottom arrow when operands from different built-in numeric types meet: arithmetic generally moves toward `float` or `complex`; it does not make an approximate representation exact.

#### Key insight

`False`, `0`, `0.0`, `0j`, and `None` are all falsy, but they do not communicate the same state. Correct code preserves the distinction required by the domain.

#### Simplification or limitation

This is a language-level decision model, not a class diagram or CPython memory layout. It omits user-defined numeric classes, `Decimal`, `Fraction`, fixed-width database fields, arrays, and the detailed dispatch protocol for overloaded operators.

### Governing rules or invariants

1. `int` represents whole numbers with arbitrary precision subject to available resources; `/` still produces a floating-point result for built-in real operands.
2. For nonzero integer `b`, `a == (a // b) * b + (a % b)`; `//` rounds toward negative infinity, not toward zero.
3. `float` stores a finite set of binary approximations on typical platforms; formatting changes display, not the stored value.
4. `bool` has exactly `False` and `True` and is a subclass of `int`, but application validation often needs to reject Boolean values where a count is required.
5. `None` is the sole `NoneType` instance and normally represents absence; test that sentinel with `is None`, not truthiness.

### Minimal example

```python
from math import isclose

retries = 0
configured = None

print(retries == False)          # equal numeric values
print(type(retries) is bool)     # different domains
print(configured is None)        # explicit absence
print(0.1 + 0.2 == 0.3)          # exact float comparison
print(isclose(0.1 + 0.2, 0.3))   # policy-based approximation
```

Expected reasoning:

1. `0 == False` is true because `bool` participates in the integer numeric domain, but `0` is not a Boolean object.
2. `None` is checked by identity so explicit zero remains distinct from missing configuration.
3. The two decimal spellings are converted to nearby binary floats; exact equality and tolerance-based comparison answer different questions.

### One failure or misconception

**Mistake:** “If a value is falsy, treating it as missing is harmless.”

**Correction:** A falsy value may be an explicit and valid state—zero retries, a false feature flag, a zero measurement, an empty result, or absence. Use the domain's exact predicate, such as `value is None`, when only absence should select the missing path.

### Important trade-offs

- `int`, `Decimal`, and `Fraction` preserve different kinds of exactness but may consume more time or memory as values grow.
- `float` is fast, compact, and appropriate for many measurements, but comparisons, aggregation, non-finite values, and external decimal data require an explicit policy.
- Reusing `None` as a sentinel keeps APIs simple only when `None` cannot also be meaningful input.

### Interview-revision cues

- Say “floor toward negative infinity” before predicting `//` or `%` with negative operands.
- Separate value equality from type/domain identity when `bool`, `int`, and `float` meet.
- For float questions, name the intended tolerance, scale, and non-finite-value policy rather than saying “never compare floats.”
- For optional values, distinguish missing, explicit zero, and false before writing a condition.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Built-in types, operations, and functions |
| Canonical ID | `PY-BLT-010` |
| Learning outcome | Use `int`, `bool`, `float`, `complex`, and `None`; explain numeric conversion, floating-point limitations, and numeric edge cases |
| Hard prerequisites | `PY-FND-020`, `PY-FND-040` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D2 |
| Scope | Language, Standard library |
| Size | M |
| Evidence profile | E+C+D+(X) |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4 on Linux x86_64 |
| Last source audit | 2026-08-29 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Select `int`, `float`, `complex`, `bool`, `None`, `Decimal`, or `Fraction` from domain requirements rather than surface syntax alone.
2. Predict literal creation, mixed-type arithmetic, floor division, remainder, rounding, conversion, bitwise behavior, and their important exceptions.
3. Explain binary floating-point representation, display illusion, tolerance-based comparison, non-finite values, signed zero, and aggregation choices.
4. Preserve the distinction between `None`, `False`, integer zero, floating zero, and other falsy values at API and configuration boundaries.
5. Debug numeric code involving Boolean subtyping, lossy conversion, money represented as float, invalid sentinels, complex ordering, or unbounded input costs.

Required evidence for `E+C+D+(X)`:

- **E — Explain:** reconstruct the domain-selection visual and the floor-division invariant, then explain why a short float representation need not be the intended decimal rational.
- **C — Code:** implement a strict numeric boundary with deterministic tests covering absence, Boolean rejection, zero, negative input, large integers, non-finite floats, and a deliberate exactness policy.
- **D — Debug:** locate the first domain collapse or lossy conversion in a faulty example, produce the smallest counterexample, and repair the contract without treating all falsy values alike.
- **(X) — Optional experiment:** reproduce the adjacent binary floats around `0.1`, its exact integer ratio, the result of `0.1 + 0.2`, and the difference between text-based and float-based exact-number construction.

The included [numeric examples](examples/numeric_models.py), [conversion examples](examples/conversion_boundaries.py), [focused tests](tests/test_examples.py), [protected practice](practice/README.md), and [reproduced experiment](experiments/EXP-01-binary-float-neighborhood/README.md) support those targets. Generated canonical materials do not constitute learner evidence.

## 2. Prerequisite bridge

The tracker records both hard prerequisites as `Not started`, although their canonical notes are approved. The following bridge is enough to begin this unit; it does not complete either prerequisite.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-FND-020` — Objects, names, references, and mutability | Numeric literals, `True`, `False`, and `None` produce or reference objects; equality and identity ask different questions. | A name refers to an object. Rebinding a name does not mutate an immutable numeric object. `is` asks whether two references designate the same object; `==` asks for value equality. |
| Hard | `PY-FND-040` — Expressions, evaluation order, and operators | Arithmetic, conversion, comparison, and Boolean expressions have precedence, evaluation order, and result-type rules. | Evaluate reached operands in the documented order, apply operator precedence before arithmetic, and remember that an operator may return a value in a wider or entirely different domain. |

Recommended dedicated review: revisit `PY-FND-020` and `PY-FND-040` before claiming learning evidence for this unit.

## 3. Vocabulary and professional English

### Magnitude

| Item | Content |
|---|---|
| Pronunciation | MAG-ni-tood |
| Simple English meaning | Size, ignoring direction or sign |
| Hindi cue | परिमाण; sign के बिना आकार |
| Meaning in this Python context | The absolute size of a real number, or `abs(z)` for a complex number's distance from zero |

Natural examples:

1. The error is small in magnitude but large relative to the expected value.
2. A huge integer has more digits but remains an `int`.
3. `abs(3 + 4j)` returns the vector's magnitude.
4. **Interview:** “Integer operation cost grows with operand magnitude; it is not universally constant time.”
5. **Engineering discussion:** “Reject measurements whose magnitude exceeds the sensor's documented range.”

### Precision

| Item | Content |
|---|---|
| Pronunciation | pri-SIZH-un |
| Simple English meaning | How finely a value can be represented or distinguished |
| Hindi cue | सूक्ष्मता / कितनी बारीकी |
| Meaning in this Python context | The representable detail available in a numeric model, distinct from display length and from accuracy against the intended value |

Natural examples:

1. More printed digits do not create more float precision.
2. Decimal context precision affects later arithmetic.
3. The calculation lost low-order integer detail when it widened to float.
4. **Interview:** “Precision describes representable resolution; accuracy describes closeness to the target.”
5. **Engineering discussion:** “The aggregation requires a documented precision and rounding policy.”

### Truncate

| Item | Content |
|---|---|
| Pronunciation | TRUNG-kayt |
| Simple English meaning | Cut off a remaining part |
| Hindi cue | बाकी भाग काट देना |
| Meaning in this Python context | Remove a fractional part toward zero, as built-in `int()` does for a finite float |

Natural examples:

1. Converting `-2.9` to `int` truncates toward zero.
2. Truncation is not the same as flooring for a negative value.
3. The parser should reject excess precision rather than silently truncate cents.
4. **Interview:** “`int(x)`, `math.floor(x)`, and `round(x)` encode different policies.”
5. **Engineering discussion:** “Silent truncation would undercharge some transactions, so the boundary raises an error.”

### Sentinel

| Item | Content |
|---|---|
| Pronunciation | SEN-tuh-nuhl |
| Simple English meaning | A special marker with a separate meaning |
| Hindi cue | विशेष पहचान-चिह्न |
| Meaning in this Python context | A distinguished object such as `None` used to signal absence, termination, or “not supplied” outside the ordinary value domain |

Natural examples:

1. `None` is a suitable sentinel when it cannot be valid data.
2. Zero is not the sentinel in this API; it is an explicit limit.
3. A private `object()` sentinel separates omitted from explicitly supplied `None`.
4. **Interview:** “Compare a singleton sentinel by identity, not equality.”
5. **Engineering discussion:** “The public contract must say whether null means clear, inherit, or missing.”

## 4. Deep explanation

### 4.1 Start with the semantic domain

Python does not attach business meaning to a number. `0` could mean a count, an identifier, an error code, a disabled limit, or missing data in a poorly designed protocol. A sound boundary therefore answers these questions before converting:

1. Is the quantity exact or approximate?
2. Is it necessarily whole, decimal, rational, or two-dimensional?
3. Are `None`, zero, false, NaN, and infinity valid and distinct?
4. What rounding, overflow, range, and invalid-input policy does the caller expect?
5. Will the value cross JSON, database, wire, or human-input boundaries that use different numeric models?

The [built-in-types reference](https://docs.python.org/3.14/library/stdtypes.html#numeric-types-int-float-complex) defines three distinct built-in numeric types—`int`, `float`, and `complex`—with `bool` as an `int` subtype. `None` is not numeric: it is the sole `NoneType` instance and commonly represents absence, as documented under [built-in constants](https://docs.python.org/3.14/library/constants.html#None).

### 4.2 Literals create values; a leading sign is an operator

Python has integer, floating-point, and imaginary numeric literal tokens. `0b1010`, `0o12`, `10`, and `0xA` all produce the same integer value. Single underscores may group digits in legal positions. A decimal point or exponent creates a float literal, while a `j` suffix creates an imaginary value. The expression `3 + 4j` combines an integer literal with an imaginary literal; the language does not define one atomic “complex literal.”

The sign is not part of a numeric literal: `-7` is unary minus applied to the literal `7`. That distinction matters for precedence, notably `-2**2 == -(2**2)`. See the [Python 3.14 lexical rules for numeric literals](https://docs.python.org/3.14/reference/lexical_analysis.html#numeric-literals).

Constructors parse or convert at runtime:

```python
int("0xff", 0)       # prefix selects base 16
int("111", 2)        # explicit base 2
float("1.25e2")      # 125.0
complex("3-4j")      # (3-4j)
```

Literal grammar and constructor grammar overlap but are not identical. For example, constructors may accept surrounding whitespace, and `float()` accepts spellings for infinity and NaN. Validate the resulting domain; successful parsing alone does not prove a value is finite, in range, or permitted.

### 4.3 `int`: exact whole-number semantics, resource-bounded execution

Python integers have arbitrary precision: their logical range is not capped at 32 or 64 bits. Arithmetic such as `10**500 + 1` stays exact if the runtime has enough resources. “Arbitrary precision” is not “free” or “infinite”: storage and operation cost grow with magnitude, conversion to a fixed-width system can overflow there, and conversion to `float` can lose detail or raise `OverflowError`.

The operators `/`, `//`, and `%` answer different questions:

- `/` performs true division and returns a float for built-in real operands;
- `//` returns the floor of the exact quotient, toward negative infinity;
- `%` returns the paired remainder required by the division identity;
- `divmod(a, b)` returns the same quotient and remainder pair together.

For integers and nonzero `b`:

```text
a == b * (a // b) + (a % b)
abs(a % b) < abs(b)
a % b is zero or has the sign of b
```

Consequently, `int(-2.9)` is `-2` because conversion truncates toward zero, while `-7 // 3` is `-3` because floor division moves downward. [`int()` conversion rules](https://docs.python.org/3.14/library/functions.html#int) and [`math.floor`, `math.ceil`, and `math.trunc`](https://docs.python.org/3.14/library/math.html#number-theoretic-functions) should be treated as distinct policies.

Integer bitwise operations behave as though negative values use two's complement with infinitely many sign bits. A negative shift count raises `ValueError`. Bit manipulation is clearest when the code also states the mask width or external representation; Python's unbounded integer model does not silently impose a machine-word width.

Since Python 3.11, conversions between very long non-power-of-two integer strings and `int` may be limited to mitigate denial-of-service behavior. This is a conversion/resource boundary, not a restriction on integer arithmetic itself. The active limit is observable through `sys.get_int_max_str_digits()`; do not disable it globally merely to accept untrusted input. The change is documented in the [`int()` version notes](https://docs.python.org/3.14/library/functions.html#int).

### 4.4 `bool`: a decision type with integer ancestry

`bool` has exactly two instances, `False` and `True`, and `bool(value)` applies truth-value testing. It is also a subclass of `int`, so these are all consequences of the language model:

```python
isinstance(True, int)  # True
True + True            # 2
False == 0             # True
```

That compatibility is convenient for summing predicates, but it is hazardous at external boundaries. JSON `true`, for example, becomes a Python `bool`; `isinstance(value, int)` would accept it as an integer count. When the contract requires a plain built-in integer and deliberately excludes Boolean values, `type(value) is int` is precise, with the trade-off that it also excludes `int` subclasses. For general polymorphic numeric code, exact-type checks are usually too restrictive.

Use `and`, `or`, and `not` for logical operations. Bitwise Boolean operations exist, but `~` on `bool` has been deprecated since Python 3.12 and is scheduled to become an error in 3.16. The [Boolean type documentation](https://docs.python.org/3.14/library/stdtypes.html#boolean-type-bool) explicitly discourages relying on Boolean values as the integers 0 and 1 in numeric contexts.

### 4.5 `None`: absence is not falsity or zero

`None` is a singleton constant and the only instance of `NoneType`. A function that reaches the end without `return`, or executes bare `return`, returns `None`. APIs commonly use it for “not supplied,” “not found,” or “no useful result.” Those meanings should not be mixed accidentally.

Prefer:

```python
if value is None:
    ...
```

Do not write `if not value` when only absence should match; that condition also selects `False`, every numeric zero, and every empty built-in container. Do not rely on `x == None`, because equality can be customized by user-defined classes and communicates the wrong relation.

`None` is unsuitable as the only omission sentinel when explicitly passing `None` has its own meaning. In that case, a private marker separates the states:

```python
_MISSING = object()

def update(value=_MISSING):
    if value is _MISSING:
        ...  # caller omitted the argument
    elif value is None:
        ...  # caller explicitly requested the None behavior
```

The full default-argument and signature design belongs to the function units; the invariant here is that each state needs a distinct representation.

### 4.6 `float`: a nearby binary value, not decimal text with a dot

On most current platforms, Python `float` maps to IEEE 754 binary64. A finite value is selected from a fixed grid of binary fractions. The decimal value one tenth repeats in base two, so `0.1` is rounded to the nearest representable binary fraction. `repr(0.1)` displays the short round-trippable string `0.1`, not every decimal digit of the exact stored value. The official [floating-point tutorial](https://docs.python.org/3.14/tutorial/floatingpoint.html) derives its exact ratio as `3602879701896397 / 2**55`.

This explains why:

```python
0.1 + 0.2 == 0.3                  # False
math.isclose(0.1 + 0.2, 0.3)      # True under the default tolerance
```

Neither answer is universally correct for an application. Exact equality is appropriate for values that must be exactly the same float, sentinel states, or deliberately quantized representations. `math.isclose` is appropriate only after choosing relative and absolute tolerances from the domain. Near zero, a relative tolerance alone does not accept a nonzero result; the [`math.isclose` contract](https://docs.python.org/3.14/library/math.html#math.isclose) requires a suitable positive `abs_tol` when the domain needs one.

Important float edge states:

- `float("inf")` and `float("-inf")` are infinities;
- `float("nan")` is not equal to itself and is not close to itself;
- `-0.0 == 0.0`, but the sign can remain observable in operations and `math.copysign`;
- every nonzero numeric value, including NaN, is truthy;
- `1.0 / 0.0` raises `ZeroDivisionError`; Python does not use infinity as that operator's result;
- `math.isfinite` is the direct validity check when a domain rejects both infinities and NaNs.

`round(x, n)` follows the built-in rounding contract, with ties going to the even choice when two multiples are equally close. It does not convert a binary approximation into an exact decimal value. A result such as `round(2.675, 2)` must be explained from the float actually represented, not from the source spelling alone.

For aggregation, plain `sum` is often sufficient, while `math.fsum` tracks multiple partial sums to reduce loss of precision. Neither creates decimal arithmetic. Formatting controls presentation only; it must not be used as a hidden computation policy.

### 4.7 `complex`: two floating components and no natural order

A built-in `complex` contains `.real` and `.imag` floating-point components. `abs(z)` gives magnitude, `z.conjugate()` negates the imaginary component, equality is defined, and ordering operators such as `<` raise `TypeError` because the complex plane has no single language-defined total order. Use `cmath` rather than `math` for functions intended to return complex results.

Mixed arithmetic widens a real operand when a complex operand participates. This can inherit float approximation even if the other operand began as an exact integer. A real-domain calculation that unexpectedly creates a complex result—such as a negative base raised to a fractional power—should make that boundary explicit rather than silently discarding `.imag`.

### 4.8 `Decimal` and `Fraction`: select a different exactness model

The standard library extends the numeric choices:

- `Decimal` represents decimal coefficients and exponents and offers configurable precision, rounding, flags, and traps. Construct from text such as `Decimal("0.1")` to preserve the intended decimal value. `Decimal.from_float(0.1)` instead preserves the exact binary float value, including its long decimal expansion. Decimal arithmetic may still round according to its context; it is not unlimited exact arithmetic. See the [`decimal` module contract](https://docs.python.org/3.14/library/decimal.html).
- `Fraction` represents a rational numerator and denominator in lowest terms. `Fraction("0.1")` is exactly `1/10`, while `Fraction.from_float(0.1)` is exactly the float's binary rational value. Repeated rational operations can grow numerators and denominators substantially. See the [`fractions` constructor rules](https://docs.python.org/3.14/library/fractions.html).

Typical selection:

| Requirement | Useful starting type | Boundary to state |
|---|---|---|
| Exact count, index, mask, identifier component | `int` | range, resource, serialization, and Boolean policy |
| Scientific measurement or approximate model | `float` | tolerance, scale, finite-value, and aggregation policy |
| Money or human-authored decimal quantity | integer minor units or `Decimal` | currency scale, rounding mode, context, and serialization |
| Exact ratio | `Fraction` | denominator growth and interoperability |
| Planar/phasor quantity | `complex` | ordering, serialization, and library support |
| Two-state decision | `bool` | whether unknown is a third state |
| Absence | `None` | whether explicit `None` is valid data |

### 4.9 Conversion is a policy boundary

Converting changes representation and may change value:

| Conversion | Central rule | Important failure or loss |
|---|---|---|
| `int(finite_float)` | Truncate toward zero | Fractional information is discarded |
| `int(text, base)` | Parse a signed integer in base 2–36 or infer prefixes with base 0 | Invalid syntax, digit limit, or prohibited leading-zero form raises `ValueError` |
| `float(integer)` | Select a representable float | Large integers may round or raise `OverflowError` |
| `float(text)` | Parse decimal/hex-related accepted syntax and special values | A successful result may be infinite or NaN |
| `complex(value)` | Convert through the complex numeric protocol | Ordering remains unsupported |
| `bool(value)` | Apply truth-value testing | Domain detail collapses to two states |
| `Decimal(text)` | Preserve the represented decimal input | Later operations obey a context and may round |
| `Fraction(text)` | Preserve an exact finite rational described by the string | Numerator/denominator size can grow |

For custom numeric objects, `int()` uses `__int__()` and falls back to `__index__()`; Python 3.14 no longer falls back to `__trunc__()`. `float()` uses `__float__()` and then `__index__()`. `complex()` uses `__complex__()`, then `__float__()`, then `__index__()`. These are public conversion protocols, not permission for an API to accept every object that can technically convert.

## 5. Additional visual models

### 5.1 Mixed built-in arithmetic widens the representation

```text
type relation:       bool ──subclass of──> int

arithmetic domain:   bool/int ───────────> float ───────────> complex
                         exact whole          binary real         two floats

example:             10**30 + 1             + 0.0
                         │                      │
                         └── exact int ─────────┴──> rounded float
```

#### How to read this visual

The top line is an inheritance fact. The lower line is a mixed-arithmetic result-domain rule: encountering a wider built-in operand moves the computation right. The example starts exact and becomes a float only when `0.0` participates.

#### Key insight

“Python integers are exact” does not guarantee that an expression containing that integer remains exact after mixed arithmetic.

#### Simplification or limitation

This covers built-in numeric types, not operator overloading, abstract numeric ABCs, `Decimal`, `Fraction`, arrays, or third-party scalar promotion rules. The arrows describe result domains, not object memory conversion steps.

### 5.2 Floor division and remainder are one decision

```text
-9        -7        -6        -3         0         3
 |---------●---------|---------|---------|---------|
           a

b = 3
q = floor(a / b) = floor(-7 / 3) = -3
r = a - b*q = -7 - 3*(-3) = 2

-7 = 3*(-3) + 2
              └─ r lies from 0 up to, but not including, 3
```

#### How to read this visual

Read the number line left to right, then calculate downward. The exact quotient lies between `-3` and `-2`; floor selects `-3`. The remainder is whatever reconstructs the dividend while staying in the divisor's remainder interval.

#### Key insight

Predict `//` first by flooring the exact quotient; derive `%` from the invariant. Do not independently guess the signs.

#### Simplification or limitation

The picture uses a positive divisor. With a negative divisor, the valid nonzero remainder has the divisor's negative sign. Floating operands also support `//` and `%`, but rounding can complicate identities near representational boundaries.

### 5.3 A decimal target lands on a binary-float grid

```text
smaller float                 chosen float                  larger float
0x...9999p-4                 0x...999ap-4                  0x...999bp-4
      ●----------------------------●-----------------------------●
                                   ↑
                      decimal text "0.1" rounds here

display:                       repr -> "0.1"
exact stored ratio:      3602879701896397 / 36028797018963968
```

#### How to read this visual

The three dots are adjacent representable floats observed in the included experiment. The decimal parser maps the infinitely repeating binary value of one tenth to the nearest dot. `repr` then chooses a short decimal string that converts back to that same dot.

#### Key insight

The short display is a round-trip label for a binary value; it is not proof that the exact rational `1/10` was stored.

#### Simplification or limitation

Spacing is conceptual, not drawn to decimal scale. The exact hexadecimal labels and ratio were reproduced on the recorded IEEE-754-style CPython runtime; Python permits platform variation in float representation.

### 5.4 Falsy states can carry different information

```text
configuration field
      │
      ├── None  ──> omitted: inherit service default
      ├── False ──> explicit Boolean decision
      ├── 0     ──> explicit numeric limit of zero
      └── value ──> explicit nonzero limit

if not field:  collapses the first three paths into one
is None:       selects only the omission path
```

#### How to read this visual

Read the branches as distinct protocol states. The bottom two lines compare predicates: truthiness merges several states, while identity isolates the singleton absence marker.

#### Key insight

Choose a predicate from the contract's state machine, not from convenience.

#### Simplification or limitation

The diagram assumes `None` means omitted and `False` is accepted separately. Real schemas may reject Boolean input or give explicit null a different meaning; validate that policy at the boundary.

## 6. Worked examples

### 6.1 Floor division, scalar classification, and float policy

Runnable source: [`examples/numeric_models.py`](examples/numeric_models.py)

```python
result = floor_division(-7, 3)
assert result.quotient == -3
assert result.remainder == 2
assert result.reconstructs_dividend

assert scalar_kind(None) == "missing"
assert scalar_kind(False) == "boolean"
assert scalar_kind(0) == "integer"

assert not (0.1 + 0.2 == 0.3)
assert finite_measurements_close(0.1 + 0.2, 0.3)
```

Prediction before execution:

`divmod` must choose `(-3, 2)` to satisfy both flooring and reconstruction. Exact-type classification must check `bool` before `int` or use exact-type comparisons because `bool` subclasses `int`. The float comparison functions answer different contracts.

Observed on CPython 3.14.4:

```text
division (7, 3): DivisionResult(dividend=7, divisor=3, quotient=2, remainder=1)
division (-7, 3): DivisionResult(dividend=-7, divisor=3, quotient=-3, remainder=2)
division (7, -3): DivisionResult(dividend=7, divisor=-3, quotient=-3, remainder=-2)
division (-7, -3): DivisionResult(dividend=-7, divisor=-3, quotient=2, remainder=-1)
kinds: ('missing', 'boolean', 'integer', 'finite-float', 'nan', 'complex')
float comparison: exact=False, close=True
accurate total: 1.0
```

### 6.2 Realistic backend boundary: omission, zero, Boolean rejection, and cents

Runnable source: [`examples/conversion_boundaries.py`](examples/conversion_boundaries.py)

```python
def resolve_batch_size(provided: int | None, *, default: int = 100) -> int:
    checked_default = require_nonnegative_plain_int(default, field="default")
    if provided is None:
        return checked_default
    return require_nonnegative_plain_int(provided, field="provided")


def parse_cents(text: str) -> int:
    amount = Decimal(text)
    if not amount.is_finite() or amount < 0:
        raise ValueError("invalid amount")
    cents = amount * 100
    if cents != cents.to_integral_value():
        raise ValueError("fractions of a cent are not supported")
    return int(cents)
```

Why this design fits:

- identity separates an omitted size from explicit zero;
- exact-type validation rejects JSON Boolean values as counts;
- decimal text preserves the caller's base-10 intent;
- integer cents create a simple exact storage and comparison boundary;
- non-finite and sub-cent amounts fail instead of being rounded silently.

Observed on CPython 3.14.4:

```text
retry missing: None
retry zero: 0
batch default: 50
batch explicit zero: 0
decimal cents: 1990
```

Alternatives and trade-offs:

- Keep a `Decimal` amount when currencies, scales, or later calculations cannot be represented by one fixed minor unit.
- Let a schema/validation layer reject types before this function when that is already an established service boundary.
- Accept `numbers.Integral` rather than exact `int` only when Boolean and third-party integer-like instances genuinely belong to the contract.
- Choose an explicit rounding mode when rounding, rather than rejection, is a product requirement.

### 6.3 Debugging example—attempt before requesting a hint

```python
def effective_timeout(configured, default=30.0):
    if not configured:
        return default
    return float(configured)


def invoice_total(unit_price, quantity):
    return round(float(unit_price) * quantity, 2)
```

Before changing code:

1. List every accepted input state the two functions appear to assume.
2. Find the smallest input for which explicit zero is replaced by a default.
3. Decide whether `False` is a timeout, a count, a disable flag, or invalid input.
4. Trace whether decimal intent is lost before or after multiplication.
5. State whether rounding, rejection, or exact minor-unit conversion is the required money policy.
6. Preserve the original and add tests before implementing a repair.

The correction is deliberately absent. Use [practice exercise `PY-BLT-010-P03`](practice/README.md#py-blt-010-p03-debug-a-billing-and-configuration-boundary) after recording a prediction.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| “Python `int` is 64-bit.” | Many languages and storage systems use fixed-width integers. | Python `int` has arbitrary precision, but external systems and resources still impose limits. | Evaluate `2**200`, then test the target database or wire range separately. |
| `int(-2.9) == -3` | It is confused with floor. | `int(float)` truncates toward zero; `math.floor` moves toward negative infinity. | Compare `int(-2.9)`, `math.trunc(-2.9)`, and `math.floor(-2.9)`. |
| `-7 // 3 == -2` | Ordinary division is mentally truncated. | `//` floors the exact quotient, so the result is `-3`. | Reconstruct `-7` using quotient and remainder. |
| `%` always gives a nonnegative result. | It is learned only with positive divisors. | A nonzero integer remainder has the divisor's sign. | Compare `7 % 3`, `-7 % 3`, `7 % -3`, and `-7 % -3`. |
| `/` preserves integer exactness. | Both operands are integers. | Built-in true division returns float and can round or overflow. | Compare `10**30 + 1` with `float(10**30 + 1)`. |
| `isinstance(value, int)` excludes Boolean values. | `bool` looks like a separate everyday domain. | `bool` is an `int` subclass. | Evaluate `isinstance(True, int)` and test an API count validator. |
| `and` and `or` always return `bool`. | They perform Boolean control. | They return a selected operand; `not` returns a Boolean. | Predict `0 or 12` and `"x" and 5`. |
| `if not value` means “missing.” | `None` is falsy. | It also selects Boolean false, numeric zeros, and empty containers. | Test `None`, `False`, `0`, `0.0`, and `""` separately. |
| `x == None` is equivalent style. | Built-in values behave normally. | Equality is customizable; singleton sentinel intent is identity. | Define a class with unusual `__eq__`, then compare with `is None`. |
| `repr(0.1)` shows the exact stored decimal. | It prints only `0.1`. | It is a short round-trip representation of a binary fraction. | Use `.as_integer_ratio()`, `.hex()`, or `Decimal.from_float`. |
| Pre-rounding inputs fixes binary representation error. | Fewer decimal digits seem easier to store. | The rounded decimal may still be inexact in binary. | Predict and run three rounded `0.1` values versus rounded `0.3`. |
| One universal epsilon makes float comparisons safe. | A tiny constant feels conservative. | Tolerance must reflect scale, units, error budget, and behavior near zero. | Compare values at magnitudes `1e-12`, `1`, and `1e12`. |
| NaN can be detected with `x == float("nan")`. | Other values compare equal to themselves. | NaN is unequal to every value, including itself; use `math.isnan`. | Evaluate equality, inequality, and `math.isnan` on one NaN. |
| Truthiness rejects invalid floats. | Zero is the obvious false numeric value. | NaN and infinities are truthy; use `math.isfinite` for a finite-only domain. | Apply `bool`, `isfinite`, `isnan`, and `isinf`. |
| `round(x, 2)` makes `x` money-safe. | The display has two decimal places. | A float remains binary and rounding policy may be wrong or too late. | Compare `Decimal("2.675")` with `Decimal.from_float(2.675)`. |
| Complex values can be sorted by size automatically. | `abs(z)` provides a size. | Python defines no natural complex ordering. Choose an explicit key if the domain does. | Try `1j < 2j`, then sort using a documented key such as `abs`. |
| `Decimal(0.1)` means decimal one tenth. | The constructor name suggests decimal conversion. | It exactly captures the already-rounded float. Use `Decimal("0.1")` for decimal text intent. | Print both constructors at full precision. |
| `Fraction(0.1) == Fraction(1, 10)`. | Both display concepts are “one tenth.” | The float constructor captures the exact binary rational. | Compare `Fraction.from_float(0.1)` with `Fraction("0.1")`. |
| Huge decimal integer text is always cheap because `int` is unbounded. | Arithmetic supports large values. | Parsing and formatting can be resource-intensive and are length-limited for safety. | Inspect the configured digit limit and test a bounded synthetic input. |
| Small-integer identity is a language guarantee. | A runtime may reuse objects. | Numeric identity reuse is an implementation choice; compare values with `==`. | Construct equal integers through different paths and avoid asserting `is`. |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| Fixed-size `float`, `bool`, or `None` operation | Usually bounded machine-level work | Exact latency and exceptional behavior depend on operation, platform, and implementation. |
| `int` comparison or addition | Grows with the number of machine digits examined | Very small integers are cheap; arbitrary precision removes fixed overflow, not magnitude-dependent cost. |
| `int` multiplication, division, exponentiation | Grows with operand size; algorithms are implementation-dependent | Do not claim one asymptotic formula for every magnitude or Python implementation. |
| `pow(base, exponent, modulus)` | Avoids constructing the full unmodded power | Still depends on exponent and operand sizes; useful for exact modular arithmetic. |
| Decimal `str` to `int` or reverse | Roughly grows with digit count and is guarded by a configurable limit | Power-of-two bases have different conversion properties; never weaken safeguards casually. |
| `float` arithmetic | Fixed representation, approximate result | Constant storage does not imply numerical stability or domain correctness. |
| `math.fsum(values)` | Linear in input count with extra internal work | Usually improves summation accuracy; it is not decimal or symbolic exactness. |
| `Decimal` arithmetic | Depends on precision, exponent, operation, and context | Exact decimal inputs can still produce rounded arithmetic results. |
| `Fraction` arithmetic | Depends on numerator/denominator sizes and normalization | Exact rational results may cause substantial integer growth. |
| Converting `int` to `float` | Magnitude-dependent conversion into fixed precision | May round or raise `OverflowError`; it is not a free type annotation change. |

No benchmark was performed. Complexity claims describe representation-sensitive cost, not measured speed.

## 9. Production relevance and trade-offs

### API and validation boundaries

- Validate type, range, finiteness, scale, and omission separately.
- Remember that JSON numbers do not preserve a Python `int`/`float` distinction in every ecosystem and JSON Boolean values become `bool`.
- Define whether null means omitted, explicit clearing, invalid input, or a third state.
- Reject oversized integer text before expensive downstream work and keep Python's conversion safeguard enabled.

### Money, quotas, and identifiers

- Use integer minor units or a documented `Decimal` policy for money; specify currency scale and rounding.
- Do not allow `True` to become one retry, one item, or one cent merely because it is integer-compatible.
- Treat identifiers as identifiers even when encoded as digits; arithmetic may destroy leading-zero or range semantics.
- Preserve explicit zero when it means “disable,” “unlimited,” or “no retries”; those meanings must not share one sentinel accidentally.

### Measurements and analytics

- Accept float approximation when the domain does, then document finite-value checks, tolerances, units, and aggregation.
- Choose both relative and absolute tolerances; tests near zero need special attention.
- Define a NaN/infinity policy before sorting, aggregating, serializing, or alerting.
- Prefer stable numerical algorithms and standard-library tools such as `math.fsum`, `hypot`, `isclose`, `isfinite`, `expm1`, or `log1p` when they match the problem.

### Portability and observability

- Record runtime and platform when an experiment depends on float representation.
- Never use object identity of numeric values as a cache or correctness contract.
- Log original units and validation outcome, but avoid turning sensitive financial or personal values into diagnostic data.
- When crossing a fixed-width system boundary, validate that system's explicit range before serialization.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| Arbitrary-precision `int`, floor division, Boolean subtyping, `None` singleton | Language | Long established | Same behavior | Resource use and identity reuse remain implementation concerns. |
| Integer string-conversion length safeguard | Language/runtime security behavior | 3.11 | Available | Configuration and exact default can vary; do not hard-code the current limit as a language invariant. |
| `int()` no longer falls back to `__trunc__()` | Language/API change | 3.14 | Implement or use `__int__()` or `__index__()` | Code relying only on `__trunc__()` can differ on 3.11. |
| `int.is_integer()` | Built-in API | 3.12 | For a known `int`, the answer is always true | Added mainly for numeric duck-typing compatibility. |
| `float.from_number()` and `complex.from_number()` | Built-in API | 3.14 | Use `float(x)` or `complex(x)` after validating that strings are not accepted | The class methods accept numeric inputs rather than parsing text. |
| Passing complex values as the separate `real` or `imag` arguments to `complex()` is deprecated | Built-in API | Deprecated in 3.14 | Pass one complex positional value or separate real components | Avoid new code that depends on the deprecated two-argument behavior. |
| Bitwise inversion of `bool` | Version-dependent built-in behavior | Deprecated in 3.12; planned error in 3.16 | Use `not flag` for logical negation | `~` means integer bit inversion, not Boolean negation. |
| `math.isclose`, `isfinite`, `nextafter`, and `ulp` | Standard library | All available by 3.11 | Same APIs | `nextafter(..., steps=...)` gained `steps` in 3.12; one-step calls are 3.11-compatible. |
| Exact hexadecimal and ratio observations for `0.1` | Platform/runtime observation through public APIs | Runtime-specific | Re-run the experiment | Common IEEE 754 binary64 values were observed on CPython 3.14.4; do not universalize the exact labels. |
| Numeric object caching or reuse | CPython/implementation detail | Implementation-specific | Never depend on it | Use `==` for numeric value, not `is`. |

All example and experiment source in this unit is syntactically compatible with Python 3.11. It was executed only on the recorded CPython 3.14.4 environment.

## 11. Practice brief

Exercises begin unsolved in [`practice/README.md`](practice/README.md).

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-BLT-010-P01` | Predict | 2 | E | [Division, conversion, and domain trace](practice/README.md#py-blt-010-p01-predict-division-conversion-and-domain-results) |
| `PY-BLT-010-P02` | Implement | 3 | C | [Strict numeric request boundary](practice/README.md#py-blt-010-p02-implement-a-strict-numeric-request-boundary) |
| `PY-BLT-010-P03` | Debug | 3 | D | [Billing and configuration boundary](practice/README.md#py-blt-010-p03-debug-a-billing-and-configuration-boundary) |
| `PY-BLT-010-P04` | Experiment / explain | 3 | E+(X) | [Float error-budget investigation](practice/README.md#py-blt-010-p04-design-a-float-error-budget-investigation) |
| `PY-BLT-010-P05` | Review / design | 4 | D | [Numeric API review](practice/README.md#py-blt-010-p05-review-a-numeric-api-contract) |

## 12. Interview prompts

Answer one at a time without running code. Full answers are intentionally omitted.

1. What are the exact quotient and remainder for each sign combination of `7` and `3`, and which invariant proves the result?
2. Why can an endpoint expecting `int` accidentally accept JSON `true`, and when is `type(value) is int` justified?
3. Explain why `repr(0.1)` can be short while `Decimal.from_float(0.1)` is long.
4. When is exact float equality correct, and how would you choose `rel_tol` and `abs_tol` for a sensor near zero?
5. Distinguish `int(x)`, `math.trunc(x)`, `math.floor(x)`, `math.ceil(x)`, and `round(x)` for negative non-integral input.
6. Design a public parameter whose states are omitted, explicitly `None`, zero, false, and positive. Which states should exist, and how will they be represented?
7. A service accepts money, percentages, counters, and phasors. Choose numeric types and state the conversion boundary for each.
8. Why can “arbitrary-precision integers” still create performance or denial-of-service risk?

A strong answer should eventually demonstrate:

- domain selection before conversion;
- floor-division and remainder reasoning rather than memorized outputs;
- Boolean subtyping without collapsing business domains;
- binary-float representation, tolerance, and non-finite policies;
- explicit absence and sentinel semantics;
- version, platform, resource, and external-system boundaries.

## 13. Closed-book revision cues

Without reading the note:

1. Draw the five-way domain-selection visual and the mixed-arithmetic widening arrow.
2. Reconstruct the quotient/remainder visual for `-7` divided by `3`, then repeat for divisor `-3`.
3. Explain `0.1` as a location on a finite binary grid without saying merely “floats are inaccurate.”
4. List four distinct falsy values and give one valid domain meaning for each.
5. Predict how `True`, `1`, `1.0`, and `1 + 0j` interact in arithmetic, equality, type checks, and ordering.
6. State a near-zero `math.isclose` policy and explain why relative tolerance alone is insufficient there.
7. Choose between integer minor units, `Decimal`, `Fraction`, and `float` for four concrete production requirements.
8. Name one Python 3.14 conversion change that can affect Python 3.11-compatible code.

## 14. Authoritative sources

1. [Python 3.14.7 Language Reference — Numeric literals](https://docs.python.org/3.14/reference/lexical_analysis.html#numeric-literals), accessed 2026-08-29.
2. [Python 3.14.7 Standard Library — Numeric Types and Boolean Type](https://docs.python.org/3.14/library/stdtypes.html#numeric-types-int-float-complex), accessed 2026-08-29.
3. [Python 3.14.7 Built-in Functions — `int`, `float`, and `complex`](https://docs.python.org/3.14/library/functions.html#int), accessed 2026-08-29.
4. [Python 3.14.7 Tutorial — Floating-Point Arithmetic: Issues and Limitations](https://docs.python.org/3.14/tutorial/floatingpoint.html), accessed 2026-08-29.
5. [Python 3.14.7 Standard Library — Mathematical functions](https://docs.python.org/3.14/library/math.html#floating-point-manipulation-functions), accessed 2026-08-29.
6. [Python 3.14.7 Standard Library — Built-in constants](https://docs.python.org/3.14/library/constants.html#None), accessed 2026-08-29.
7. [Python 3.14.7 Standard Library — Decimal arithmetic](https://docs.python.org/3.14/library/decimal.html), accessed 2026-08-29.
8. [Python 3.14.7 Standard Library — Rational numbers](https://docs.python.org/3.14/library/fractions.html), accessed 2026-08-29.
9. [Python 3.11.15 Standard Library — Numeric Types](https://docs.python.org/3.11/library/stdtypes.html#numeric-types-int-float-complex), accessed 2026-08-29.
