# EXP-01 — Binary-float neighborhood behind decimal `0.1`

| Field | Value |
|---|---|
| Owning unit | [`PY-BLT-010`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-blt-010) |
| Topic branch | `topic/PY-BLT-010` |
| Precise question | What exact public representations surround `float("0.1")`, why does `0.1 + 0.2 == 0.3` fail here, and how do text-based exact-number constructors differ from float-based constructors? |
| Classification | Python language and standard-library contracts observed through a CPython/platform float runtime |
| Status | Reproduced |
| Risk | None; deterministic, bounded, standard-library-only execution |

## 1. Why an experiment is necessary

The display `0.1` hides the exact rational value represented by the float. The final Boolean `False` from `0.1 + 0.2 == 0.3` also hides where rounding occurred, how far apart adjacent representable floats are, and whether `Decimal` or `Fraction` receives decimal text or an already-rounded float.

This experiment observes only public operations: `repr`, `float.as_integer_ratio`, `float.hex`, `math.nextafter`, `math.ulp`, `math.isclose`, `Decimal`, and `Fraction`. It does not inspect object memory, CPython source, bytecode, or hardware registers.

## 2. Hypothesis

Before execution:

> Decimal text `"0.1"` will map to one finite binary float between two adjacent float values. Its short `repr` will be `0.1`, while its exact ratio and `Decimal.from_float` expansion will reveal a value slightly above one tenth. Adding the independently rounded floats for `0.1` and `0.2` will produce a float different from `float("0.3")`, so exact equality will be false while `math.isclose` under its default policy will be true. Constructing `Decimal` or `Fraction` from text will preserve exactly one tenth; constructing from the float will preserve the float's exact rational value.

Alternative outcomes requiring investigation:

- the runtime uses a float representation whose exact ratio or hexadecimal labels differ;
- `repr` displays more than `0.1`;
- the rounded addition lands on the same float as `0.3`;
- the default `math.isclose` policy rejects the observed gap;
- text-based and float-based exact-number constructors produce the same value;
- the available runtime lacks one of the public observation APIs.

## 3. Environment

Recorded actual values:

```text
Date: 2026-08-29
Operating system: Linux 7.0.0-30-generic with glibc 2.43
Architecture: x86_64
Python version: 3.14.4
sys.version: 3.14.4 (main, Jun 18 2026, 14:25:02) [GCC 15.2.0]
sys.implementation: cpython
Build type: regular release build with the GIL enabled
Py_DEBUG: 0
Py_GIL_DISABLED: 0
Dependencies: Python standard library only
CPU: not queried; this is not a benchmark
Relevant environment variables: PYTHONDONTWRITEBYTECODE=1 for the recorded clean reproduction command
```

The repository's canonical documentation baseline is Python 3.14.7. Execution occurred on the available CPython 3.14.4 runtime. The source is syntactically compatible with Python 3.11, but no Python 3.11 interpreter was executed for this observation.

## 4. Controls and variables

### Controlled

- Decimal source strings are exactly `"0.1"`, `"0.2"`, and `"0.3"`.
- Each float is created with the public `float` constructor.
- Neighbor direction is negative infinity or positive infinity and uses one default `math.nextafter` step.
- Approximate comparison uses the documented default `math.isclose` tolerances.
- Exact decimal and rational controls are constructed once from text and once from the selected float.
- Output uses public deterministic representations and contains no addresses, hashes, timing, locale-sensitive formatting, filesystem state, network data, randomness, threads, or subprocesses.

### Changed

- Representation view: shortest decimal `repr`, exact integer ratio, or hexadecimal float form.
- Position: immediate lower neighbor, selected float, or immediate upper neighbor.
- Arithmetic: parsed `0.1` alone versus parsed `0.1 + 0.2`.
- Comparison policy: exact equality versus default tolerance-based closeness.
- Exact-number construction source: decimal text versus the already-created float.

### Measured

- Exact numerator and denominator returned by `as_integer_ratio`.
- Exact hexadecimal representations of the selected value, its neighbors, and one unit in the last place.
- Short representation and exact ratio of the addition result.
- Exact-equality and `math.isclose` decisions.
- String forms of `Decimal` and `Fraction` values constructed through both routes.

## 5. Files

```text
experiments/EXP-01-binary-float-neighborhood/
├── README.md
└── binary_float_probe.py
```

Runnable source: [`binary_float_probe.py`](binary_float_probe.py)

Focused regression: [`../../tests/test_examples.py`](../../tests/test_examples.py)

## 6. Reproduction command

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python units/built-in-types/PY-BLT-010-numbers-booleans-and-none/experiments/EXP-01-binary-float-neighborhood/binary_float_probe.py
```

Focused regression command:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s units/built-in-types/PY-BLT-010-numbers-booleans-and-none/tests -v
```

## 7. Prediction

```text
0.1: repr=0.1; ratio=3602879701896397/36028797018963968; hex=0x1.999999999999ap-4
neighbors: lower=0x1.9999999999999p-4; chosen=0x1.999999999999ap-4; upper=0x1.999999999999bp-4; ulp=0x1.0000000000000p-56
0.1 + 0.2: repr=0.30000000000000004; ratio=1351079888211149/4503599627370496
comparison: exact=False; isclose=True
Decimal: text=0.1; from-float=0.1000000000000000055511151231257827021181583404541015625
Fraction: text=1/10; from-float=3602879701896397/36028797018963968
```

## 8. Observed output

```text
0.1: repr=0.1; ratio=3602879701896397/36028797018963968; hex=0x1.999999999999ap-4
neighbors: lower=0x1.9999999999999p-4; chosen=0x1.999999999999ap-4; upper=0x1.999999999999bp-4; ulp=0x1.0000000000000p-56
0.1 + 0.2: repr=0.30000000000000004; ratio=1351079888211149/4503599627370496
comparison: exact=False; isclose=True
Decimal: text=0.1; from-float=0.1000000000000000055511151231257827021181583404541015625
Fraction: text=1/10; from-float=3602879701896397/36028797018963968
```

The prediction and observation matched. No output was edited to create that match. The focused suite also ran 17 tests successfully on the recorded runtime.

## 9. Interpretation

1. `repr=0.1` and the longer exact ratio describe one float, not two values. The short representation is sufficient to round-trip to the same float.
2. The denominator `36028797018963968` is `2**55`, directly exposing a binary rational rather than the decimal rational `1/10`.
3. The lower, chosen, and upper hexadecimal values differ by one least-significant step. `math.ulp(0.1)` reports the size of that local step on this runtime.
4. The addition result has short representation `0.30000000000000004` and a ratio distinct from the float produced by decimal text `"0.3"`; exact equality therefore returned false.
5. Default `math.isclose` returned true for these values. This only demonstrates that the observed gap is inside that default formula; it does not establish a suitable tolerance for money, sensors, geometry, or any other domain.
6. `Decimal("0.1")` and `Fraction("0.1")` preserved the decimal rational one tenth. The float-based constructors preserved the already-selected binary rational exactly.
7. The output supports a representation-and-construction explanation. It does not show that float is unsuitable, that exact equality is always wrong, or that `Decimal` and `Fraction` are always preferable.

## 10. Visual interpretation

```text
decimal target 1/10
        │ parse + nearest representable choice
        v
 lower neighbor             chosen float               upper neighbor
 ...9999p-4  ── one ulp ──> ...999ap-4 ── one ulp ──> ...999bp-4
                                  │
                     ┌────────────┼───────────────┐
                     v            v               v
                 repr(0.1)   exact ratio    Decimal.from_float
                    "0.1"     360287...     0.10000000000000000555...

text "0.1" ───────────────> Decimal("0.1") / Fraction("0.1")
                             exact decimal rational 1/10
```

### How to read this visual

Read from the decimal target down to the chosen dot on the float grid. The three downward branches are alternative public descriptions of that same dot. The bottom path bypasses float conversion, so text-based exact-number constructors preserve the decimal rational instead.

### Key insight

Constructor input history matters: an exact type can faithfully preserve either the intended decimal text or the earlier float approximation, and those are different values.

### Simplification or limitation

The spacing is conceptual and only one local neighborhood is shown. The diagram omits sign, exponent-field layout, subnormal values, rounding modes, arithmetic implementation, intermediate precision, and every float other than the observed area around `0.1`.

## 11. Language and implementation conclusion

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| `repr` produced a short string that round-trips to the observed float. | Public runtime behavior plus observation | CPython 3.14.4 | Python's representation contract is public; the exact text for other values or old runtimes can differ. |
| `as_integer_ratio` and `hex` exposed exact public descriptions of this finite float. | Built-in API plus observation | Python/CPython 3.14.4 | Exact values depend on the platform float representation. |
| `nextafter` identified adjacent values and `ulp` identified local spacing. | Standard-library contract plus observation | Python/CPython 3.14.4 | The APIs are portable; exact labels depend on the runtime's float model. |
| `0.1 + 0.2` and parsed `0.3` were different floats. | Arithmetic observation | CPython 3.14.4 on Linux x86_64 | Reproduce before asserting exact output on an unusual platform or implementation. |
| Default `math.isclose` accepted the observed pair. | Standard-library contract plus observation | Python/CPython 3.14.4 | Domain code must choose tolerances; defaults are not universal requirements. |
| Text and float construction produced distinct `Decimal` and `Fraction` values. | Standard-library contract plus observation | Python/CPython 3.14.4 | The distinction follows constructor input values and is not CPython-private. |
| Exact formatting and line order are artifact properties. | Tooling observation | This repository artifact | They do not specify internal representation or performance. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular GIL-enabled build was executed.
- Python 3.14.7 and 3.11.15 documentation was audited, but neither maintenance release was the runtime used.
- The Python 3.11 compatibility claim is source-level and documentation-backed; it was not reproduced on a 3.11 runtime.
- The experiment covers one local float neighborhood and one addition; it does not characterize all decimal inputs, operations, magnitudes, subnormals, overflow, underflow, cancellation, or aggregation order.
- Default rounding mode and common IEEE-754-style binary64 behavior were observed, not established as universal Python language requirements.
- `math.isclose` is exercised only with its defaults and values near `0.3`; no production error budget is derived.
- `Decimal` context arithmetic is not exercised; only construction is observed.
- `Fraction` growth and normalization cost are not measured.
- This is not a benchmark and supports no speed, allocation, or memory-use claim.

## 13. Follow-up

- Reproduce the semantic assertions on an actual Python 3.11 runtime and append, rather than replace, its version-labelled output.
- Design the protected practice experiment for cancellation, reversed aggregation order, `sum`, and `math.fsum`.
- Add a domain-specific near-zero tolerance study with declared units and an error budget.
- Compare decimal text, float, `Decimal`, integer fixed-scale, and `Fraction` only after stating the intended input semantics.
- Move object layout, allocation, small-integer caching, and interpreter specialization questions to their owning CPython units.

## 14. Authoritative sources

1. [Python 3.14.7 Tutorial — Floating-Point Arithmetic: Issues and Limitations](https://docs.python.org/3.14/tutorial/floatingpoint.html), accessed 2026-08-29.
2. [Python 3.14.7 Standard Library — Additional Methods on Float](https://docs.python.org/3.14/library/stdtypes.html#additional-methods-on-float), accessed 2026-08-29.
3. [Python 3.14.7 Standard Library — Floating-point manipulation functions](https://docs.python.org/3.14/library/math.html#floating-point-manipulation-functions), accessed 2026-08-29.
4. [Python 3.14.7 Standard Library — Decimal construction](https://docs.python.org/3.14/library/decimal.html#decimal-objects), accessed 2026-08-29.
5. [Python 3.14.7 Standard Library — Fraction construction](https://docs.python.org/3.14/library/fractions.html#fractions.Fraction), accessed 2026-08-29.
