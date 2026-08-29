# Practice — PY-BLT-020 Strings and Unicode

| Field | Value |
|---|---|
| Unit note | [PY-BLT-020](../README.md) |
| Curriculum | [CURRICULUM.md](../../../../CURRICULUM.md#py-blt-020) |
| Topic branch | `topic/PY-BLT-020` |
| Evidence target | E+C+D |
| Attempt required before solution | Yes |
| Test command | `python -m unittest discover -s units/built-in-types/PY-BLT-020-strings-and-unicode/tests -v` plus learner-created focused tests |
| Status | Not attempted |

## Practice rules

1. Record a prediction or design before running code.
2. Preserve the original attempt, including a failing version.
3. Request one progressive hint at a time; no hints are prewritten here.
4. A passing test is not enough when the code-point, normalization, or boundary reasoning is wrong.
5. Final comparison code appears only after the exercise is closed.
6. Do not push later practice changes automatically unless the completion publication choice explicitly authorizes it.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Files | Status |
|---|---|---:|---|---|---|
| `PY-BLT-020-P01` | Predict | 2 | Trace code points, slices, search, splitting, stripping, and formatting | This file | Not attempted |
| `PY-BLT-020-P02` | Implement | 3 | Build an auditable code-point report without confusing text and bytes | Learner-created `code_point_report.py`, `test_code_point_report.py` | Not attempted |
| `PY-BLT-020-P03` | Implement / Design | 4 | Preserve display labels while enforcing an NFC caseless uniqueness policy | Learner-created `label_registry.py`, `test_label_registry.py` | Not attempted |
| `PY-BLT-020-P04` | Debug | 3 | Repair exact-affix, missing-separator, empty-field, and display/canonicalization bugs | Learner-created `route_parser.py`, `test_route_parser.py` | Not attempted |
| `PY-BLT-020-P05` | Review / Design | 5 | Design an explicit multilingual backend text boundary and state its limits | Learner-created `text_boundary_review.md` | Not attempted |

## PY-BLT-020-P01 — Predict the exact string behavior

### Problem

Without running Python, record the exact value, type, or exception for every labeled expression. For every string result, also state which code points it contains when visual appearance is ambiguous.

```python
text = "A\U0001f1ee\U0001f1f3e\u0301"

# A
len(text)

# B
text[1]

# C
text[1:3]

# D
text[-1]

# E
text[3:100]

# F
text[::-1]

# G
"" in text

# H
"alpha".find("a")

# I
"alpha".find("z")

# J
" a  b ".split()

# K
" a  b ".split(" ")

# L
"mississippi".rstrip("ip")

# M
"/api/admin".lstrip("/api/")

# N
"/api/admin".removeprefix("/api/")

# O
f"{1234.5:>12,.2f}"
```

Do not combine multiple expressions into one vague answer. The reasoning must identify whether each operation uses code points, a half-open slice, a substring, a delimiter, a character set, an exact prefix, or a format specification.

### Learning evidence

This exercise should demonstrate:

- exact sequence reasoning without relying on rendering;
- distinction among search indices, Boolean truth, delimiter policies, and literal affixes;
- ability to parse a format specification.

### Constraints

- Do not run any expression until all predictions are recorded.
- Use U+ notation for the India-flag indicators and the combining mark.
- Preserve the prediction even when execution disproves it.

### Required edge cases

- an empty substring;
- an out-of-range slice bound;
- a search hit at index zero and a missing search result;
- consecutive and surrounding whitespace;
- a character-set stripping trap.

### Acceptance criteria

- [ ] All fifteen predictions include reasoning.
- [ ] Values, types, and exceptions are exact.
- [ ] Code-point and visible-symbol reasoning are not conflated.
- [ ] The original predictions remain visible beside observed results.
- [ ] Every mismatch names the first incorrect assumption.

### Prediction before execution

| Label | Predicted value/type/exception | Reasoning | Confidence |
|---|---|---|---|
| A |  |  |  |
| B |  |  |  |
| C |  |  |  |
| D |  |  |  |
| E |  |  |  |
| F |  |  |  |
| G |  |  |  |
| H |  |  |  |
| I |  |  |  |
| J |  |  |  |
| K |  |  |  |
| L |  |  |  |
| M |  |  |  |
| N |  |  |  |
| O |  |  |  |

### Learner attempt

- Attempt date:
- Execution command:
- Observed results:
- First mismatch:
- Corrected mental model:

### Progressive hints

No hints are recorded. Request one only after completing the prediction table.

## PY-BLT-020-P02 — Implement a code-point report

### Problem

Create a function with this public contract:

```python
def describe_text(text: str) -> tuple[dict[str, object], ...]:
    """Return one deterministic record per Python string element."""
```

Each record must expose:

- zero-based index;
- the length-1 string element;
- stable uppercase U+ notation with at least four hexadecimal digits;
- Unicode name, with an explicit fallback for unnamed code points;
- general category;
- canonical combining class.

Write focused tests. The task is to implement the contract, not to copy the unit's example module.

### Learning evidence

This exercise should demonstrate:

- iteration over `str` code points;
- correct use of `ord` and public `unicodedata` APIs;
- deterministic handling of ordinary, combining, supplementary-plane, control, empty, and invalid inputs.

### Constraints

- Reject non-`str` input explicitly.
- Do not encode the text to discover code points.
- Do not depend on glyph rendering, terminal width, CPython object layout, or private APIs.
- Use only the standard library and Python 3.11-compatible syntax.
- Do not import the completed example implementation.

### Examples

```text
Input domains:
ASCII letter; precomposed accent; decomposed accent; India flag; empty string

Expected observable behaviour:
One record per indexed code point, with stable metadata independent of how a terminal draws it
```

### Required edge cases

- empty text returns an empty tuple;
- U+000A has no printable glyph but still has a category and a stable notation;
- U+1F600 requires more than four hexadecimal digits;
- U+0301 has a nonzero combining class;
- `bytes` input is rejected rather than silently decoded.

### Acceptance criteria

- [ ] Public contract and types are clear.
- [ ] Deterministic tests cover all required edge cases.
- [ ] Tests do not assert font-dependent rendering.
- [ ] The learner explains why `encode()` answers a different question.
- [ ] The original implementation attempt is preserved.

### Prediction before execution

- Expected record count for each test input:
- Expected U+ notation:
- Expected failure mode:
- Uncertainty:

### Learner attempt

- Attempt file: `practice/code_point_report.py`
- Test file: `practice/test_code_point_report.py`
- Learner's reasoning:
- Test command:
- Observed result:

### Progressive hints

No hints are recorded. Request the smallest conceptual nudge after preserving a failing attempt.

## PY-BLT-020-P03 — Build a normalization-aware label registry

### Problem

Implement an in-memory registry for user-facing labels with this domain policy:

1. Input must be `str`.
2. Surrounding Unicode whitespace is trimmed.
3. Blank labels and labels containing control characters are rejected.
4. Display labels are stored in NFC.
5. Uniqueness and lookup use an NFC → `casefold()` → NFC key.
6. The first accepted display spelling is preserved and returned.
7. NFKC is deliberately not used, so compatibility distinctions remain distinct.

Choose a small public API such as `add(raw)`, `find(query)`, and `__len__()`. Define the duplicate and missing-label behavior before writing code.

### Learning evidence

This exercise should demonstrate:

- separation of display data and derived comparison keys;
- consistent normalization at write and lookup boundaries;
- documented exception behavior and deterministic tests;
- explanation of what the policy does not secure.

### Constraints

- Use only the standard library.
- Keep normalization and key construction in one auditable function.
- Do not mutate a caller's text or replace the stored display value during lookup.
- Do not claim locale-aware collation or confusable protection.
- Do not import the completed example implementation.

### Examples

```text
Scenario:
Add a precomposed mixed-case label, then query with a decomposed uppercase spelling.

Expected observable behaviour:
Lookup follows the documented canonical-caseless key and returns the first stored NFC display label.
```

### Required edge cases

- `"Café"` versus `"CAFE\u0301"`;
- `"Straße"` versus `"STRASSE"`;
- circled `"①"` versus ASCII `"1"` under the deliberate NFC policy;
- blank-after-trim input;
- newline or tab inside a label;
- missing lookup;
- non-string input.

### Acceptance criteria

- [ ] The policy is written before implementation.
- [ ] Display and key values are stored separately.
- [ ] Duplicate and missing behavior are explicit.
- [ ] Tests cover every required edge case.
- [ ] The learner explains why an NFKC policy would change at least one result.
- [ ] The learner names two Unicode/security concerns outside this registry's guarantee.

### Prediction before execution

- Chosen duplicate behavior:
- Chosen missing behavior:
- Expected stored display values:
- Expected key collisions:
- Uncertainty:

### Learner attempt

- Attempt file: `practice/label_registry.py`
- Test file: `practice/test_label_registry.py`
- Learner's design reasoning:
- Test command:
- Observed result:

### Progressive hints

No hints are recorded. Request one after a focused failing test identifies the uncertain policy stage.

## PY-BLT-020-P04 — Debug a route-and-tag parser

### Problem

Preserve this original implementation, then find and fix its independent contract violations:

```python
def parse_route_and_tags(raw: str) -> tuple[str, tuple[str, ...]]:
    route, _, tag_text = raw.strip().lower().partition(":")
    route = route.lstrip("/api/")
    tags = tuple(tag_text.split("|"))
    return route, tags
```

Intended contract:

- input must be a string containing exactly one `:` separator;
- surrounding whitespace around the whole record may be removed;
- one literal `/api/` route prefix is optional and removed exactly once;
- route spelling is preserved for display;
- tags use `|` as an explicit delimiter, so empty tags remain observable for validation;
- no empty route or empty tag is accepted;
- normalized caseless route lookup, if needed, belongs in a separate derived key.

### Learning evidence

This exercise should demonstrate:

- diagnosis of several plausible string-API misconceptions;
- smallest counterexamples before replacement code;
- separation of parsing, validation, display preservation, and comparison policy.

### Constraints

- Record the first failing assumption before changing code.
- Add one focused test per independent bug.
- Do not replace the simple grammar with a regular expression or parser framework.
- Preserve the original faulty function in the attempt history.

### Required edge cases

- missing `:`;
- more than one `:`;
- `/api/admin`, `/api/api`, and `/ping` routes;
- mixed-case display route;
- adjacent, leading, and trailing `|` delimiters;
- whitespace-only route or tag;
- non-string input.

### Acceptance criteria

- [ ] Every failing test names one contract violation.
- [ ] Literal prefix removal cannot over-strip characters.
- [ ] Separator presence and cardinality are validated.
- [ ] Empty fields are preserved long enough to reject deliberately.
- [ ] Display text is not overwritten by a lookup transformation.
- [ ] The learner explains why `partition` may still be preferable to chained `split` calls.

### Prediction before execution

- Smallest input exposing `lstrip` misuse:
- Smallest input exposing an ignored separator:
- Input exposing premature lowercasing:
- Expected empty-field behavior:

### Learner attempt

- Attempt file: `practice/route_parser.py`
- Test file: `practice/test_route_parser.py`
- First incorrect assumption:
- Test command:
- Observed result:

### Progressive hints

No hints are recorded. Request one only after adding the smallest failing test for the first bug.

## PY-BLT-020-P05 — Review a multilingual text boundary

### Problem

Write a senior-level design review for this synthetic service requirement:

> An HTTP endpoint accepts a UTF-8 JSON display name and an optional search alias. The UI promises a limit of 40 user-perceived characters. Search is case-insensitive. The database currently has a locale-dependent collation. Names appear in structured logs and CSV exports. Duplicate display names are allowed, but aliases must be unique.

Your review must turn every ambiguous sentence into a testable policy. Cover decoding ownership, malformed input, size limits, normalization, caseless matching, display preservation, uniqueness, database agreement, grapheme-aware length, control and bidirectional characters, confusables, logging, CSV serialization, migration, and Python 3.11/3.14 portability.

### Learning evidence

This exercise should demonstrate:

- transfer from string mechanics to backend API and persistence design;
- clear separation of correctness, product choice, security boundary, and unresolved requirement;
- ability to reject false guarantees.

### Constraints

- Do not invent a universal “sanitize string” function.
- Do not claim `len()` enforces the UI's user-perceived-character promise.
- Do not claim normalization plus casefolding solves locale, confusables, or identity.
- Name which layer owns bytes-to-text decoding.
- Identify at least three questions that require product, security, or database-owner input.

### Required edge cases

- composed and decomposed accents;
- a zero-width-joiner emoji sequence;
- Turkish dotted/dotless I policy ambiguity;
- compatibility characters;
- newline and bidirectional controls;
- aliases that application code treats equal but the database treats distinct, and the reverse;
- malformed UTF-8 before JSON decoding.

### Acceptance criteria

- [ ] The review supplies a boundary pipeline or state table.
- [ ] Each limit names its unit: bytes, code points, grapheme clusters, or storage units.
- [ ] Display, search, and unique-key representations are separated.
- [ ] Database and application equivalence are reconciled.
- [ ] Destination-specific logging and CSV handling are named.
- [ ] Unresolved decisions and threat-model limits are explicit.
- [ ] Tests and migration observability are included.

### Prediction before design

- Assumed normalization form and why:
- Assumed case policy and why:
- Limit unit and implementation dependency:
- Security properties deliberately not claimed:
- Questions requiring external ownership:

### Learner attempt

- Review file: `practice/text_boundary_review.md`
- Design summary:
- Strongest claim with evidence:
- Most uncertain boundary:
- Review result:

### Progressive hints

No hints are recorded. Request one after writing the boundary pipeline and unresolved-question list.

## Practice closure

Complete only after individual exercises are reviewed.

| Evidence | Status | Link | What remains |
|---|---|---|---|
| Explanation and prediction | Not attempted | — | Complete and review `PY-BLT-020-P01` |
| Code | Not attempted | — | Complete and review `PY-BLT-020-P02` and `PY-BLT-020-P03` |
| Debugging | Not attempted | — | Complete and review `PY-BLT-020-P04` |
| Production transfer | Not attempted | — | Complete and review `PY-BLT-020-P05` |

Do not advance `PROGRESS.md` from generated exercises alone. Link preserved learner attempts and actual review evidence.
