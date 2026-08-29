# Practice — PY-BLT-010 Numbers, booleans, and None

| Field | Value |
|---|---|
| Unit note | [`PY-BLT-010`](../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../CURRICULUM.md#py-blt-010) |
| Topic branch | `topic/PY-BLT-010` |
| Evidence target | E+C+D+(X) |
| Attempt required before solution | Yes |
| Canonical test command | `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s units/built-in-types/PY-BLT-010-numbers-booleans-and-none/tests -v` |
| Status | Not attempted |

## Practice rules

1. Record a prediction, state table, or numeric policy before running code.
2. Preserve the original attempt and the first failing assertion or counterexample.
3. Request one progressive hint at a time; no hints or solutions are prewritten here.
4. A passing test is insufficient if the reasoning confuses floor with truncation, equality with domain identity, approximation with exactness, or falsity with absence.
5. Keep learner code in new files under this directory so canonical examples remain unchanged.
6. State units, range, scale, rounding, tolerance, and non-finite policy whenever they matter.
7. Do not push later practice changes automatically unless the explicit publication prompt is given.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Suggested attempt file | Status |
|---|---|---:|---|---|---|
| `PY-BLT-010-P01` | Predict | 2/5 | Trace division, conversion, type, equality, and exception outcomes. | `p01_prediction.md` | Not attempted |
| `PY-BLT-010-P02` | Implement | 3/5 | Build a strict request boundary without collapsing numeric states. | `p02_numeric_boundary.py` | Not attempted |
| `PY-BLT-010-P03` | Debug | 3/5 | Repair configuration and billing domain mistakes. | `p03_boundary_debug.py` | Not attempted |
| `PY-BLT-010-P04` | Experiment / explain | 3/5 | Investigate aggregation error and derive a tolerance policy. | `p04_error_budget/` | Not attempted |
| `PY-BLT-010-P05` | Review / design | 4/5 | Review a numeric API for correctness, security, and interoperability. | `p05_api_review.md` | Not attempted |

## PY-BLT-010-P01 — Predict division, conversion, and domain results

### Problem

Without running Python, fill in the exact value and type, or the exact exception class, for each expression. Then explain the first language rule that determines it.

```python
# A
-7 // 3

# B
-7 % 3

# C
7 // -3, 7 % -3

# D
int(-2.9)

# E
round(2.5), round(3.5)

# F
isinstance(False, int), type(False) is int

# G
False == 0 == 0.0 == 0j

# H
10**30 + 1 == float(10**30 + 1)

# I
bool(float("nan")), float("nan") == float("nan")

# J
(3 + 4j).real, abs(3 + 4j)

# K
1j < 2j

# L
int("010", 0)

# M
int("010", 8)

# N
None == False, None is False
```

### Learning evidence

This exercise should demonstrate:

- quotient/remainder reasoning for negative operands;
- separation of truncation, floor, and rounding;
- Boolean subtype reasoning without erasing type distinctions;
- awareness of integer-to-float loss, NaN behavior, complex ordering, parsing bases, and sentinel identity.

### Constraints

- Do not use a REPL, calculator, debugger, search engine, or the canonical examples before completing every prediction.
- For A–C, show the reconstruction equation, not only the output.
- For H, state which operand changes domain before deciding equality.
- For every exception prediction, name the operation that rejects the input.
- Preserve the initial table after execution and annotate corrections separately.

### Required edge cases

- positive and negative divisors;
- a negative finite float;
- a half-even rounding pair;
- Boolean/int overlap;
- an integer beyond ordinary float precision;
- NaN;
- complex ordering;
- base-zero parsing;
- `None` versus falsity.

### Acceptance criteria

- [ ] All result values, result types, or exception classes are exact.
- [ ] Division answers satisfy the quotient/remainder invariant.
- [ ] H identifies the lossy conversion point.
- [ ] Equality, identity, subtyping, and truthiness are not used interchangeably.
- [ ] The first incorrect rule, if any, is recorded after execution.
- [ ] Actual output is preserved separately from the prediction.

### Prediction before execution

Record in `p01_prediction.md`:

| Label | Predicted value or exception | Predicted type | Governing rule | Confidence |
|---|---|---|---|---|
| A |  |  |  |  |

Continue through N before running anything.

### Hint gate

No hint is stored in this artifact. If blocked after a complete table, request `PY-BLT-010-P01 Hint 1` and include the table.

## PY-BLT-010-P02 — Implement a strict numeric request boundary

### Problem

Implement a pure function that validates and normalizes a synthetic job-run request:

```python
def normalize_request(payload: object) -> NormalizedRequest:
    ...
```

Return an immutable result containing:

- `max_attempts`: a plain integer from 0 through 20;
- `timeout_seconds`: either `None` or a finite, nonnegative float no greater than 300;
- `sample_rate`: a finite float from 0 through 1 inclusive;
- `enabled`: exactly a Boolean;
- `budget_cents`: a plain nonnegative integer;
- `phase_offset`: a complex value whose real and imaginary components are finite.

Input protocol:

1. `payload` must be a mapping with exactly those six keys.
2. `max_attempts` and `budget_cents` reject `True` and `False` even though `bool` subclasses `int`.
3. `timeout_seconds=None` means no timeout; `0` means an immediate timeout and must be preserved.
4. `sample_rate` may arrive as a plain integer or float, but not a Boolean. Normalize it to float only after validation.
5. `enabled` accepts only the two Boolean instances.
6. `phase_offset` may arrive as a complex number or a two-element pair of real numeric components. Boolean components are invalid.
7. Unknown keys and missing keys are errors; do not silently default them.

Define a small exception type or a consistent built-in exception policy. The message must identify the field without echoing the complete payload.

### Learning evidence

This exercise should demonstrate:

- ordering of type, finiteness, range, and conversion checks;
- deliberate treatment of `bool` as distinct from count and measurement domains;
- preservation of `None` and explicit zero;
- safe normalization of mixed numeric input;
- deterministic tests for ordinary, boundary, and invalid states.

### Constraints

- Do not coerce strings such as `"5"`, `"nan"`, or `"1+2j"` at this boundary.
- Do not use truthiness to detect missing values or validate numbers.
- Do not accept NaN or either infinity in any real or imaginary component.
- Do not mutate the supplied mapping.
- Do not serialize through JSON as an implementation shortcut.
- Do not catch every exception under one generic message.
- Keep validation free of I/O, environment access, clocks, randomness, and globals.

### Required edge cases

- each valid lower and upper bound;
- `None`, `0`, `False`, and `0.0` in every plausible field;
- an integer too large to convert to finite float;
- NaN and both infinities;
- a complex value with one non-finite component;
- a two-item tuple and list for phase input;
- a wrong-length pair;
- missing and extra keys;
- an unrelated object instead of a mapping;
- a custom `int` subclass, with a stated accept/reject policy.

### Acceptance criteria

- [ ] The normalized result is immutable and fully typed.
- [ ] Every state in the input protocol has a deterministic outcome.
- [ ] Boolean values cannot leak into numeric fields.
- [ ] Explicit zero never becomes missing or defaulted.
- [ ] All accepted float and complex components are finite.
- [ ] Error messages identify the field but do not copy the payload.
- [ ] Tests include at least one smallest counterexample per validation rule.
- [ ] The learner explains why check ordering prevents lossy or misleading conversion.

### Prediction and design before implementation

Record:

- one state table per field;
- the exact order of checks;
- whether exact built-in types or numeric subclasses are accepted;
- when normalization occurs;
- the exception taxonomy;
- the first five tests to write;
- time and space complexity in terms of payload size.

### Hint gate

If blocked after the state tables and one failing test, request `PY-BLT-010-P02 Hint 1` with both artifacts.

## PY-BLT-010-P03 — Debug a billing and configuration boundary

### Problem

The following code is intended to read an optional timeout and calculate an exact invoice in cents. It accepts malformed states, changes valid states, and loses the intended decimal value.

```python
def effective_timeout(configured, default=30.0):
    if not configured:
        return default
    return float(configured)


def invoice_total(unit_price, quantity, discount=None):
    if not quantity:
        return None

    subtotal = float(unit_price) * quantity
    if discount:
        subtotal *= 1 - float(discount)

    return int(round(subtotal, 2) * 100)
```

Intended policy:

- timeout: `None` selects the default; a finite value from 0 through 300 is explicit;
- unit price: nonnegative decimal text with at most two fractional digits;
- quantity: a plain integer from 0 through 10,000;
- discount: omitted means zero; otherwise it is decimal text from `0` through `1` with no more than four fractional digits;
- result: a nonnegative integer number of cents rounded once with an explicitly chosen business rounding mode;
- Boolean input is invalid for timeout, quantity, and discount.

### Debugging sequence

1. Predict results for `configured=None`, `0`, `False`, `float("nan")`, and `float("inf")`.
2. Find the smallest valid quantity whose result is confused with absence.
3. Mark the first conversion where decimal text loses its intended exact value.
4. Show whether rounding occurs before or after multiplication by 100 and why that ordering matters.
5. Produce one counterexample for a discount of zero and one for a non-finite discount.
6. State the desired handling of negative zero if it arrives as decimal text.
7. Preserve the original functions, create corrected functions separately, and add tests first.

### Learning evidence

This exercise should demonstrate:

- diagnosis of falsy-state collapse;
- identification of the first lossy conversion rather than only the final wrong result;
- explicit money scale and rounding policy;
- rejection of Boolean and non-finite inputs;
- preservation of zero as valid data.

### Constraints

- Do not repair the code by adding scattered `round()` calls.
- Do not parse money or discounts through float.
- Do not silently clamp invalid input.
- Do not return `None` for a valid zero invoice.
- Do not select a rounding mode without stating the product rule it represents.
- Keep the public result free of `Decimal` if the contract says integer cents.

### Required edge cases

- omitted and explicit zero timeout;
- zero quantity and maximum quantity;
- prices `"0"`, `"0.01"`, `"19.90"`, and an excess-scale price;
- omitted, zero, one, and excess-scale discounts;
- halfway rounding inputs selected for the chosen policy;
- negative, NaN, and infinite inputs;
- Boolean values in all numeric fields;
- a total near a range boundary, with an explicit bound if one is introduced.

### Acceptance criteria

- [ ] The first faulty assumption is named before replacement code appears.
- [ ] Every input field has a domain table and error policy.
- [ ] Missing, false, and zero are distinct.
- [ ] Decimal intent remains exact until the documented rounding point.
- [ ] The result is integer cents and is never `None` for a valid request.
- [ ] Tests prove that the original fails each smallest counterexample.
- [ ] The repair is compared with an integer-minor-unit input API.

### Hint gate

If blocked after the trace and three failing tests, request `PY-BLT-010-P03 Hint 1` and include them.

## PY-BLT-010-P04 — Design a float error-budget investigation

### Problem

Design and run a controlled experiment for a service that aggregates signed sensor deltas. The production team needs to choose among `sum`, `math.fsum`, `Decimal`, and an integer fixed-scale representation, and needs a defensible `math.isclose` policy near zero.

Your experiment must use at least these datasets, in original and reversed order:

```text
A: one large positive value, one small positive value, the matching large negative value
B: ten copies of decimal text 0.1
C: values immediately below, at, and above one chosen float
D: a near-zero expected result with a domain-specific absolute error budget
```

Choose all exact inputs yourself and write the hypothesis before execution. Compare only methods whose input construction is stated unambiguously; `Decimal` from text and `Decimal` from float are different experimental treatments.

### Required experiment record

1. Precise question.
2. Hypothesis and plausible alternative.
3. Python version, implementation, build type, operating system, and architecture.
4. Input construction and order.
5. Controlled, changed, and measured variables.
6. Exact reproduction command.
7. Predicted output pattern.
8. Unedited observed output.
9. Interpretation separated from direct observation.
10. Proposed relative and absolute tolerance with units and error-budget rationale.
11. Language, standard-library, and platform classification.
12. Limitations and threats to validity.

### Learning evidence

This exercise should demonstrate:

- recognition that algebraic equivalence does not force identical floating results;
- separation of representation error, cancellation, ordering, and comparison policy;
- correct construction of decimal and rational controls;
- a production decision supported by evidence without overgeneralizing one runtime.

### Constraints

- Do not benchmark; the question is numerical behavior, not speed.
- Do not use random data.
- Do not omit the original order when testing a reversed order.
- Do not call formatted strings “exact values.”
- Do not use one arbitrary epsilon for all scales.
- Do not edit observed output to match the hypothesis.
- Do not claim IEEE-754 details beyond what the environment and sources support.

### Acceptance criteria

- [ ] Every output line can be traced to one controlled question.
- [ ] Text-based and float-based exact-number constructors are labeled separately.
- [ ] Both relative and absolute tolerance roles are explained.
- [ ] Non-finite inputs have an explicit include/reject policy.
- [ ] The recommendation names units, input magnitude, aggregation length, and limitations.
- [ ] The result is reproducible with standard-library-only code.

### Hint gate

If blocked after the hypothesis and experiment table, request `PY-BLT-010-P04 Hint 1` with both.

## PY-BLT-010-P05 — Review a numeric API contract

### Problem

Review this code before rewriting it:

```python
def prepare_job(payload):
    retries = int(payload.get("retries") or 3)
    threshold = float(payload.get("threshold") or 0.0)
    amount = round(float(payload["amount"]), 2)
    phase = complex(payload.get("phase") or 0)

    if threshold:
        threshold_status = "active"
    else:
        threshold_status = "missing"

    return {
        "retries": retries,
        "threshold": threshold,
        "threshold_status": threshold_status,
        "amount": amount,
        "phase": phase,
    }
```

Assume `payload` is decoded from untrusted JSON and later serialized to a database and message bus. Product documentation says retries may be omitted or explicitly zero, threshold must be finite, amount is money, and phase is optional planar data.

### Review brief

Produce a review containing:

1. the smallest input that changes explicit zero retries to three;
2. the effect of JSON `true` for retries and why conversion makes the error harder to diagnose;
3. the missing-versus-zero collapse in threshold status;
4. behavior for threshold NaN and infinities;
5. the first point where amount loses decimal intent;
6. missing currency, scale, rounding, and range requirements;
7. whether JSON can carry complex values directly and what wire representation is needed;
8. behavior for string, list, null, and Boolean phase values;
9. potential resource risk from huge numeric strings;
10. database fixed-width and precision boundaries;
11. error taxonomy and safe logging requirements;
12. a revised field-by-field contract before any code rewrite;
13. a test matrix spanning omission, zero, false, bounds, non-finite values, and interoperability;
14. the smallest safe refactor boundary.

### Constraints

- Do not assume successful constructor conversion means valid business input.
- Do not log the entire untrusted payload or financial values.
- Do not silently clamp, default, or discard imaginary components.
- Do not propose float money plus additional rounding as the final model.
- Distinguish Python language behavior from JSON, database, and application policy.
- Do not include replacement implementation before the review is complete.

### Acceptance criteria

- [ ] Every finding includes a concrete counterexample and consequence.
- [ ] Boolean subtyping and constructor coercion are traced correctly.
- [ ] Absence, false, and numeric zero remain separate protocol states.
- [ ] Float validity and tolerance are not reduced to truthiness.
- [ ] Money and complex serialization policies are explicit.
- [ ] Resource and fixed-width boundaries are included.
- [ ] Recommendations distinguish strict validation from normalization.
- [ ] The proposed tests would fail the original code for the intended reasons.

### Hint gate

If blocked after writing at least six findings, request `PY-BLT-010-P05 Hint 1` and include the partial review.

## Review and closure protocol

For every completed exercise, retain:

- the original prediction, domain table, design, or review;
- the first failing assertion or incorrect semantic rule;
- the smallest counterexample that exposed it;
- the corrected rule in the learner's own words;
- actual command and output;
- relevant negative, zero, missing, Boolean, huge, non-finite, and precision cases;
- a short production consequence;
- the language, standard-library, implementation, or external-system classification;
- remaining uncertainty.

Passing tests does not prove understanding if the explanation still confuses truncation with floor, exact equality with tolerance, Boolean subtyping with business-domain acceptance, or `None` with every falsy value. Only closed attempts with preserved evidence may support a later `PROGRESS.md` learning-state transition.
