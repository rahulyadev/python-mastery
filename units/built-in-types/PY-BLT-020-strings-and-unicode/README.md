# PY-BLT-020 — Strings and Unicode

[Curriculum entry](../../../CURRICULUM.md#py-blt-020) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-BLT-020`

## Physical Notebook Core

### Problem this concept solves

Programs must preserve, compare, transform, format, and exchange human text even when one visible symbol is not one byte—and is not necessarily one Python string element.

### One-sentence mental model

> A Python `str` is an immutable sequence of Unicode code points; human-visible symbols and encoded bytes are separate layers that require explicit policies.

### One important visual

```text
same-looking text             Python str elements                 length

      é              A: [ U+00E9 LATIN SMALL LETTER E ACUTE ]       1
      é              B: [ U+0065 e ][ U+0301 COMBINING ACUTE ]      2
                               │
                               │ normalize("NFC")
                               ▼
                         [ U+00E9 ]

text boundary:       str  -- encode("utf-8") -->  bytes
                     str  <-- decode("utf-8") --  bytes
```

#### How to read this visual

Read the two rows left to right. The renderer may display both rows alike, but Python indexes the bracketed code points, so their lengths and exact equality differ. The vertical arrow shows an explicit comparison policy. The bottom arrows separate text from its byte representation.

#### Key insight

Never infer code-point count, byte count, exact equality, or safe slicing from visual appearance alone.

#### Simplification or limitation

This is a language-level model, not CPython memory layout. Fonts may render the examples differently, and Unicode grapheme segmentation is richer than the two-code-point accent example.

### Governing rules or invariants

1. `str` is immutable; an apparent modification creates or selects another string.
2. `len`, indexing, iteration, and slicing operate on Unicode code points, not UTF-8 bytes or user-perceived characters.
3. Exact equality compares string contents; canonically equivalent spellings are unequal until an explicit normalization policy makes their code-point sequences equal.
4. `encode()` crosses from text to bytes; `decode()` crosses from bytes to text. An encoding and error policy belong at that boundary.
5. `lower()` changes case for display-oriented transformations; `casefold()` is the stronger operation intended for caseless matching.
6. Formatting controls presentation. It does not validate input, make text safe for every sink, or solve locale and Unicode security policy.

### Minimal example

```python
import unicodedata

composed = "\u00e9"
decomposed = "e\u0301"

print(len(composed), len(decomposed))
print(composed == decomposed)
print(unicodedata.normalize("NFC", composed) == unicodedata.normalize("NFC", decomposed))
```

Observed on CPython 3.14.4:

```text
1 2
False
True
```

Expected reasoning:

1. The first string contains one code point; the second contains a base code point followed by a combining mark.
2. Exact comparison sees different sequences; NFC maps both canonical spellings to the same composed form.

### One failure or misconception

**Mistake:** using `route.lstrip("/api/")` to remove the literal prefix `"/api/"`.

**Correction:** `lstrip` removes any run of characters from a set. Use `route.removeprefix("/api/")` when the contract names one exact prefix.

### Important trade-offs

- Normalize only under a documented contract: NFC preserves canonical distinctions, while NFKC can intentionally erase compatibility distinctions that may matter to the domain.
- Keep original or display text separate from search keys; a comparison key is not automatically the right value to display or persist as the sole source.
- Code-point slicing is simple and deterministic but can separate combining marks or zero-width-joiner sequences that users perceive as one symbol.
- Repeated concatenation is readable for a few fragments; `str.join()` or `io.StringIO` makes the construction policy clearer for many fragments.

### Interview-revision cues

- Say “immutable sequence of Unicode code points,” then distinguish code point, user-perceived character, glyph, and encoded byte.
- Predict `len`, indexes, slices, equality, normalization, and UTF-8 byte length independently.
- Explain why normalization plus casefolding can support a search policy without solving confusables, authorization, or locale-specific rules.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Built-in types, operations, and functions |
| Canonical ID | `PY-BLT-020` |
| Learning outcome | Work correctly with `str`, Unicode code points, normalization awareness, formatting, indexing, slicing, and string APIs |
| Hard prerequisites | `PY-FND-020` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D2 |
| Scope | Language, Standard library |
| Size | L |
| Evidence profile | E+C+D |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4 on Linux x86_64 |
| Last source audit | 2026-08-29 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Model `str` as immutable Unicode code-point sequences and distinguish text, code points, glyphs, user-perceived characters, and bytes.
2. Predict literal parsing, escapes, `len`, indexing, negative indexes, slicing, iteration, containment, comparison, and the results of important string APIs.
3. Choose among exact comparison, Unicode normalization forms, `lower()`, and `casefold()` from an explicit domain policy.
4. Build text maintainably with f-strings, the format mini-language, `join`, and focused parsing methods without confusing presentation with validation.
5. Preserve the `str`/`bytes` boundary and explain why encoding and decoding require named policies.
6. Debug production failures involving canonical equivalence, control characters, empty fields, affix removal, accidental quadratic construction, or slicing across a visible symbol.

Required evidence for `E+C+D`:

- **E — Explain:** reconstruct the layered text visual and explain why the same-looking strings can have different lengths, exact equality, slices, and byte lengths.
- **C — Code:** implement a text boundary with deterministic tests for normalization choice, caseless matching, empty input, control characters, delimiters, formatting, and preservation of display text.
- **D — Debug:** identify the first incorrect string assumption in a faulty parser or normalizer, give the smallest counterexample, and repair the contract without leaking a solution from the exercise.

The included [Unicode models](examples/unicode_models.py), [backend text boundaries](examples/text_boundaries.py), [focused tests](tests/test_examples.py), [protected practice](practice/README.md), and [reproduced experiment](experiments/EXP-01-code-points-normalization-and-casefold/README.md) support those targets. Generated canonical materials do not constitute learner evidence.

## 2. Prerequisite bridge

The tracker records the hard prerequisite as `Not started`, although its canonical note is approved. This bridge is enough to begin; it does not complete the prerequisite.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-FND-020` — Objects, names, references, and mutability | A string operation binds a name to a new immutable object rather than changing the original string in place. Identity and value equality answer different questions. | A name refers to an object. Rebinding a name does not mutate the old object. `==` asks whether values compare equal; `is` asks whether references designate the same object. Never depend on string interning for correctness. |

Recommended dedicated review: revisit `PY-FND-020` before claiming learning evidence for this unit.

## 3. Vocabulary and professional English

### Code point

| Item | Content |
|---|---|
| Pronunciation | KOHD point |
| Simple English meaning | A numbered position in the Unicode character set |
| Hindi cue | Unicode का क्रमांक |
| Meaning in this Python context | The unit produced by indexing or iterating over a `str` |

Natural examples:

1. U+0061 is the code point for Latin small letter `a`.
2. A combining mark occupies its own code point.
3. `ord(character)` returns the code point's integer value.
4. **Interview:** “Python string length counts code points, not UTF-8 bytes.”
5. **Engineering discussion:** “The validator limits code points, but the database column limit is measured differently.”

### Normalize

| Item | Content |
|---|---|
| Pronunciation | NOR-muh-lyze |
| Simple English meaning | Convert different allowed forms into one chosen form |
| Hindi cue | एक मानक रूप में लाना |
| Meaning in this Python context | Transform Unicode text to NFC, NFD, NFKC, or NFKD under a stated comparison or storage policy |

Natural examples:

1. Normalize incoming labels to NFC before building their search keys.
2. The service preserves the submitted display spelling separately.
3. Compatibility normalization would change the circled digit to an ordinary digit.
4. **Interview:** “Normalization is explicit; Python equality does not apply it automatically.”
5. **Engineering discussion:** “We must document whether normalization happens at write time, query time, or both.”

### Canonically equivalent

| Item | Content |
|---|---|
| Pronunciation | kuh-NON-ih-klee ih-KWIV-uh-lent |
| Simple English meaning | Formally considered the same abstract text despite a different representation |
| Hindi cue | रूप अलग, मूल अक्षर समान |
| Meaning in this Python context | Two code-point sequences that a canonical normalization form can map to the same normalized sequence |

Natural examples:

1. A precomposed accented letter can be canonically equivalent to a base letter plus a combining mark.
2. Canonical equivalence does not imply exact `str` equality before normalization.
3. NFC and NFD choose different normalized representations of canonical equivalents.
4. **Interview:** “The inputs look identical but are only canonically equivalent, not binary-identical strings.”
5. **Engineering discussion:** “Our uniqueness key respects canonical equivalence while retaining the display value.”

### Interpolate

| Item | Content |
|---|---|
| Pronunciation | in-TER-puh-layt |
| Simple English meaning | Insert a computed value into surrounding text |
| Hindi cue | बीच में मान जोड़ना |
| Meaning in this Python context | Evaluate a replacement expression and format its value inside an f-string or format string |

Natural examples:

1. The f-string interpolates the request identifier.
2. The format specifier controls width and precision after evaluation.
3. Literal braces must be doubled in the surrounding text.
4. **Interview:** “An f-string evaluates replacement expressions at runtime from left to right.”
5. **Engineering discussion:** “Keep the interpolation template developer-controlled and validate values for the destination sink.”

## 4. Deep explanation

### 4.1 Four layers that must not collapse into one

The word “character” is too ambiguous for precise debugging. Use the layer that matches the question:

| Layer | Example question | Python-facing model |
|---|---|---|
| User-perceived text element | “Will backspace remove what the user sees as one symbol?” | May span multiple code points; core `str` APIs do not promise grapheme segmentation |
| Code point | “What does `text[3]` return?” | One length-1 `str` selected from the code-point sequence |
| Glyph | “How is this text drawn?” | A font and renderer choose visual shapes; `str` does not store glyphs |
| Encoded byte | “What travels over UTF-8?” | `text.encode("utf-8")` produces bytes; byte count can differ from `len(text)` |

Python's library reference defines `str` as an immutable sequence of Unicode code points and notes that indexing returns a length-1 string because Python has no separate character type. The Unicode HOWTO distinguishes code points from glyphs and describes encodings as mappings between Unicode text and bytes. See [Text Sequence Type—`str`](https://docs.python.org/3.14/library/stdtypes.html#text-sequence-type-str) and [Unicode HOWTO—Introduction to Unicode](https://docs.python.org/3.14/howto/unicode.html#introduction-to-unicode).

This model explains several otherwise surprising results:

```python
len("A")                         # 1 code point
len("é")                         # 1 when written as U+00E9
len("e\u0301")                   # 2: base + combining mark
len("🇮🇳")                       # 2 regional-indicator code points
len("👨\u200d👩\u200d👧\u200d👦")             # 7 code points joined into a family emoji by many renderers
len("é".encode("utf-8"))         # 2 bytes
```

The visible results depend on the renderer. The lengths do not: they follow the actual code-point sequences stored in the strings.

### 4.2 Literals, escapes, raw strings, and `str()`

Single-, double-, and triple-quoted literals all create `str` objects. Triple quotes preserve embedded newlines and indentation. Adjacent literals in one expression are concatenated by the parser, which is useful for readable static text:

```python
message = (
    "one compile-time literal "
    "continued across source lines"
)
```

Escapes describe code points or control characters:

```python
newline = "\n"
e_acute = "\u00e9"
grinning_face = "\U0001f600"
snowman = "\N{SNOWMAN}"
```

A raw prefix disables most escape processing and is convenient for patterns such as `r"\d+"`. It does not mean “arbitrary backslashes”: a raw literal cannot end in an odd number of backslashes because the final quote would still be escaped. Python 3.12 warns for unrecognized escapes in ordinary string literals, and the language reference says they are planned to become errors. See [String and bytes literals](https://docs.python.org/3.14/reference/lexical_analysis.html#string-and-bytes-literals).

`str(object)` asks for an object's informal text representation. It is not a default decoder:

```python
str(b"caf\xc3\xa9")                 # "b'caf\\xc3\\xa9'"
b"caf\xc3\xa9".decode("utf-8")       # "café"
```

The second line states the encoding contract; the first merely formats the bytes object.

### 4.3 Immutability, rebinding, and construction

Index assignment is invalid because strings are immutable:

```python
name = "mira"
# name[0] = "M"  # TypeError

updated = "M" + name[1:]
```

`upper`, `replace`, `strip`, and every other transforming string method return a string; they do not mutate the receiver. The original object remains usable through every name that refers to it.

For a known small number of fragments, `+` is direct and readable. For a collection of fragments, gather them and join once:

```python
parts = ["request", "42", "accepted"]
line = " | ".join(parts)
```

The separator owns `join` because it states what appears between every pair of elements. Every element must be `str`; Python does not silently stringify arbitrary values.

### 4.4 Indexing, slicing, iteration, and comparison

The common sequence contract applies to strings. Index zero selects the first code point; a negative index counts from the end. An out-of-range single index raises `IndexError`, while slice bounds are clipped:

```python
text = "Python"

text[0]       # "P"
text[-1]      # "n"
text[1:4]     # "yth"
text[:100]    # "Python"
text[::-1]    # "nohtyP"
```

A slice uses a half-open interval: start is included, stop is excluded. A negative step reverses direction, and a zero step raises `ValueError`. Each result is another `str`.

The same mechanics can break visible text:

```python
accented = "e\u0301"
accented[:1]   # "e"
accented[1:]   # combining mark without its base
```

Iteration yields the same length-1 strings that indexing selects. Containment on strings tests substrings, so `"gg" in "eggs"` is true. Comparisons are lexicographic over the actual sequence; Python does not apply linguistic collation, locale rules, normalization, or case folding automatically. The portable sequence operations are documented in [Common Sequence Operations](https://docs.python.org/3.14/library/stdtypes.html#common-sequence-operations).

### 4.5 Choose a method from its contract

Memorising method names is less useful than grouping them by intent:

| Intent | Prefer | Boundary to remember |
|---|---|---|
| Exact affix test/removal | `startswith`, `endswith`, `removeprefix`, `removesuffix` | `strip`, `lstrip`, and `rstrip` accept a set of removable characters, not an affix |
| One structural split | `partition` or `rpartition` | Always returns three parts and exposes whether the separator was present |
| Repeated delimiter split | `split(sep)` | Explicit separators preserve empty fields between adjacent delimiters |
| Whitespace tokenization | `split()` | No-argument mode collapses whitespace runs and drops leading/trailing empties |
| Reassembly | `separator.join(parts)` | Elements must already be strings |
| Search with absence as data | `find` | Returns `-1`; do not use the result as a Boolean because index `0` is falsy |
| Search with absence as failure | `index` | Raises `ValueError` when missing |
| Replacement | `replace(old, new, count)` | Literal replacement, not a regular expression; original is unchanged |
| Caseless key | `casefold` | More aggressive than `lower`; still requires a normalization and domain policy |

The explicit/no-argument `split` modes are intentionally different:

```python
" a  b ".split()       # ["a", "b"]
"a||b|".split("|")    # ["a", "", "b", ""]
```

Unicode-aware predicates also encode different sets:

- `isdecimal()` is the narrowest useful test for decimal digits.
- `isdigit()` includes additional digit characters.
- `isnumeric()` includes a broader set of numeric characters.
- none of them alone proves that a string satisfies a business identifier, parser, or ASCII protocol contract.

For parsing a protocol with exact grammar, validate that grammar instead of assuming a human-language predicate is equivalent.

### 4.6 Exact equality, normalization, and caseless policy

Two strings compare equal only when their contents compare equal. Unicode permits canonically equivalent sequences such as precomposed `é` and `e` followed by a combining acute accent. Python does not normalize implicitly because the right equivalence policy depends on the domain.

`unicodedata.normalize(form, text)` provides four forms:

| Form | Transformation | Typical policy question |
|---|---|---|
| NFC | Canonical decomposition, then canonical composition | “Should canonical spellings share one composed comparison form?” |
| NFD | Canonical decomposition | “Does this algorithm require decomposed canonical components?” |
| NFKC | Compatibility decomposition, then canonical composition | “May compatibility distinctions such as circled `①` versus `1` be erased?” |
| NFKD | Compatibility decomposition | “May those distinctions be erased while retaining a decomposed form?” |

The Unicode normalization standard warns that compatibility forms must not be applied blindly because they can erase visually or semantically important distinctions. Normalize under a contract, not as generic cleanup. See [Unicode Standard Annex #15—Normalization Forms](https://www.unicode.org/reports/tr15/) and [`unicodedata.normalize`](https://docs.python.org/3.14/library/unicodedata.html#unicodedata.normalize).

Case transformation is another independent policy:

```python
"Straße".lower()    == "STRASSE".lower()     # False
"Straße".casefold() == "STRASSE".casefold()  # True
```

For a normalized caseless key, normalize, casefold, and normalize the result again. Keep the display string separate:

```python
def comparison_key(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text)
    return unicodedata.normalize("NFC", normalized.casefold())
```

This supports one defined kind of matching. It does not provide locale-specific collation, detect visually confusable characters, make identifiers safe, or decide whether two people or accounts are the same. Unicode security needs a separate threat model; see [Unicode Technical Standard #39—Security Mechanisms](https://www.unicode.org/reports/tr39/).

### 4.7 Text and binary data meet at an encoding boundary

An encoding maps Unicode text to bytes; decoding interprets bytes as text:

```python
wire = "नमस्ते".encode("utf-8")
text = wire.decode("utf-8")
assert text == "नमस्ते"
```

The default error policy is `"strict"`, which raises when conversion is impossible. Alternatives such as `"replace"`, `"ignore"`, and `"surrogateescape"` have specialized contracts and can lose information or carry unusual code points. Choose them only at a boundary that documents why.

Python source is UTF-8 by default, but that does not imply that every file, database, subprocess, HTTP body, or legacy protocol is UTF-8. The next unit, `PY-BLT-030`, develops bytes and buffer semantics in depth.

### 4.8 Formatting evaluates, converts, and presents

An f-string has three conceptually separate parts:

```text
f"request={request_id!r} latency_ms={latency_ms:,.2f}"
            expression !conversion             :format spec
```

Replacement expressions are evaluated at runtime from left to right. `!s`, `!r`, and `!a` force `str`, `repr`, and `ascii` conversion. The format specifier then controls presentation such as alignment, width, grouping, type, and precision. See [f-strings](https://docs.python.org/3.14/reference/lexical_analysis.html#f-strings) and the [format specification mini-language](https://docs.python.org/3.14/library/string.html#format-specification-mini-language).

```python
request_id = "req-7"
latency_ms = 1234.5

f"request={request_id!r} latency_ms={latency_ms:,.2f}"
# "request='req-7' latency_ms=1,234.50"
```

Important boundaries:

- formatting a float to two places changes its presentation, not its stored numeric value;
- `!r` is valuable for diagnostics because escapes and quotes become visible, but it is not a universal logging or injection defense;
- f-string expressions are code written by the developer, so never evaluate source text constructed from untrusted input;
- a value formatted for a log is not thereby safe for SQL, HTML, a shell, or another destination grammar.

`str.format()` and `format(value, spec)` share the formatting mini-language. Percent formatting remains relevant to some APIs and existing code, but f-strings are normally clearest when the template is fixed in source.

Python 3.14 also introduces template string literals (`t"..."`), which produce template objects rather than final strings so another component can process interpolations. They are not a drop-in security wrapper and have no Python 3.11 syntax equivalent.

### 4.9 Execution sequence: preparing a searchable display label

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Receive a `str` at a typed text boundary | No byte decoding is hidden inside the function |
| 2 | Trim only boundary whitespace named by the contract | Blank-after-trim is rejected |
| 3 | Normalize display text to NFC | Canonical spelling is stable; compatibility distinctions remain |
| 4 | Reject control characters for this one-line label domain | Display value remains suitable for the intended UI/log record |
| 5 | Copy display text into a separate comparison-key pipeline | Original display intent is not overwritten by matching rules |
| 6 | Casefold and re-normalize the comparison key | Canonical caseless matching policy is explicit |
| 7 | Format diagnostics with named conversion and precision | Presentation policy is visible at the call site |

## 5. Additional visual models

### 5.1 The text stack

```text
human intent
    │
    ▼
user-perceived elements     "é"          "🇮🇳"          family emoji
    │ segmentation/rendering
    ▼
Unicode code points         1 point       2 points       7 points
    │ encode("utf-8")
    ▼
bytes on a boundary         2 bytes       8 bytes        25 bytes
    │ decode + font shaping
    ▼
glyphs on a screen          depends on encoding success, font, and renderer
```

#### How to read this visual

Move downward when data crosses toward storage or transport, and upward when bytes are decoded and displayed. Counts on one row do not determine counts on another.

#### Key insight

Choose limits, indexes, truncation, and validation in the unit the product contract actually names.

#### Simplification or limitation

This conceptual stack omits grapheme-boundary algorithms, normalization state, bidirectional layout, fallback fonts, and platform rendering differences.

### 5.2 Code-point slicing can cut through one visible unit

```text
family =  👨  + ZWJ +  👩  + ZWJ +  👧  + ZWJ +  👦
index      0     1      2     3      4     5      6

family[:3]  └──────────────┘
             syntactically valid str
             possibly a different or broken-looking rendered sequence
```

#### How to read this visual

The upper row shows seven Python string elements. The lower bracket applies an ordinary half-open slice to the first three code points, without asking the renderer where a user-perceived boundary lies.

#### Key insight

Valid code-point slicing is not the same promise as safe UI truncation.

#### Simplification or limitation

The visual assumes a common zero-width-joiner sequence and common emoji rendering. It does not implement the Unicode grapheme-cluster algorithm, and rendering may vary.

### 5.3 A comparison-policy funnel

```text
left display text  ── NFC ── casefold ── NFC ──┐
                                                ├── exact key comparison
right display text ── NFC ── casefold ── NFC ──┘

preserve each display value separately; do not render the folded key as the user's name
```

#### How to read this visual

Each side passes through the same three deterministic transformations. Only the resulting keys are compared. The source display strings remain outside the destructive comparison path.

#### Key insight

Unicode matching becomes reviewable when every equivalence decision is an explicit stage.

#### Simplification or limitation

This policy is suitable only for domains that choose NFC plus default Unicode case folding. It omits locale-specific collation, confusable detection, database collation behavior, and authorization rules.

### 5.4 Formatting anatomy

```text
f"{value!r:>12}"
   └expr┘│ └spec
         └ conversion

evaluation  →  optional conversion  →  __format__(spec)  →  new str
```

#### How to read this visual

Read the field from the expression outward, then follow the bottom pipeline. Literal text surrounding the field is copied into the final string.

#### Key insight

Formatting is a value-to-text protocol with distinct evaluation, conversion, and presentation stages.

#### Simplification or limitation

The example uses `!r`, so alignment applies to the resulting representation string. Numeric precision belongs on a numeric field without first forcing `repr`, as in `{latency_ms:,.2f}`.

## 6. Worked examples

### 6.1 Code-point and normalization observations

The runnable [Unicode example](examples/unicode_models.py) makes every sequence explicit.

```python
composed = "caf\u00e9"
decomposed = "cafe\u0301"

print(f"composed: len={len(composed)}; points={code_point_notation(composed)!r}")
print(f"decomposed: len={len(decomposed)}; points={code_point_notation(decomposed)!r}")
print(f"exact equality: {composed == decomposed}")
print(f"NFC equality: {equal_under_policy(composed, decomposed)}")
```

Prediction before execution:

The strings will render similarly. The decomposed form will have one extra indexed element, exact equality will be false, and NFC-policy equality will be true.

Observed on CPython 3.14.4:

```text
composed: len=4; points=('U+0063', 'U+0061', 'U+0066', 'U+00E9')
decomposed: len=5; points=('U+0063', 'U+0061', 'U+0066', 'U+0065', 'U+0301')
exact equality: False
NFC equality: True
caseless equality: True
family: len=7; points=('U+1F468', 'U+200D', 'U+1F469', 'U+200D', 'U+1F467', 'U+200D', 'U+1F466')
```

### 6.2 Realistic backend boundary: display value, search key, parsing, and diagnostics

The [text-boundary example](examples/text_boundaries.py) deliberately keeps four policies separate:

```python
label = prepare_label("  Cafe\u0301  ")
record = parse_pipe_record("evt-7||ready")
route = remove_route_prefix("/api/ping")
summary = format_request_summary("req-7", label, latency_ms=1234.5)
```

Observed on CPython 3.14.4:

```text
label: PreparedLabel(display='Café', search_key='café')
record: ('evt-7', '', 'ready')
route: 'ping'
request='req-7' label='Café' latency_ms=1,234.50
```

Why this design fits:

- NFC stabilizes canonical display spelling without applying broader compatibility folding.
- The caseless search key is derived and stored separately from display text.
- an explicit delimiter preserves the empty middle field, which may carry domain meaning;
- `removeprefix` states exact affix intent;
- `!r` exposes string boundaries in diagnostics and `,.2f` states numeric presentation.

Alternatives and failure modes:

- NFKC may be appropriate for a restricted identifier namespace, but it must be a deliberate domain decision.
- a database collation may implement different equivalence rules; application keys and database constraints must agree.
- `isprintable()` is only this example's one-line control-character gate, not a complete abuse, spoofing, or UI-safety policy.
- formatting untrusted text for SQL, HTML, shell commands, or structured logs requires the destination's own safe API.

### 6.3 Debugging example—attempt before requesting a hint

Do not correct this implementation yet:

```python
def route_name(raw: str) -> str:
    return raw.strip().lstrip("/api/").lower()
```

Investigate in this order:

1. Predict the output for `"/api/ping"`, `"/api/admin"`, `"/ping"`, and `"/api/api"`.
2. State whether each operation removes a literal substring or a set of characters.
3. Decide whether lowercase display text is the same requirement as a caseless comparison key.
4. Preserve the original attempt and request one hint only after recording the smallest failing input.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| `len(text)` counts visible characters | ASCII often makes bytes, code points, and glyphs appear one-to-one | `len(str)` counts code points | Compare `"é"`, `"e\u0301"`, a flag, and a zero-width-joiner emoji sequence |
| Indexing returns an integer | `bytes[index]` does return an integer | `str[index]` returns a length-1 `str` | Check `type("A"[0])` and `ord("A"[0])` |
| Slicing cannot fail | Bounds are clipped, so it appears universally safe | A zero step raises `ValueError`, and a valid slice can split perceived text | Try `text[::0]` and slice before a combining mark |
| Strings mutate through methods | Method-call syntax resembles mutation | Transforming methods return strings; the receiver is unchanged | Retain both `original` and `original.upper()` |
| `strip(".py")` removes one suffix | The argument visually resembles a suffix | `strip` removes a set of characters from both ends | Compare `"happy.py".strip(".py")` and `.removesuffix(".py")` |
| `split()` and `split(" ")` are equivalent | Both involve spaces | No-argument mode collapses whitespace; explicit mode preserves delimiter-created empties | Use `" a  b ".split()` and `.split(" ")` |
| `find` is safely truthy/falsy | `-1` is often treated as “false” in other languages | Python regards `-1` as truthy and index zero as falsy | Evaluate `bool("abc".find("a"))` and `bool("abc".find("z"))` |
| Same rendering implies equality | Fonts hide representation differences | Exact equality compares sequences without normalization | Compare NFC and NFD spellings and print code points |
| `lower` is Unicode caseless matching | It handles familiar Latin letters | `casefold` is intended for caseless matching and may expand characters | Compare `"Straße"` with `"STRASSE"` |
| NFKC is harmless cleanup | It makes more values match | Compatibility normalization can erase meaningful distinctions | Normalize `"①"` under NFC and NFKC |
| `str(bytes_value)` decodes bytes | The result looks textual | Without an encoding, it produces the bytes object's informal representation | Compare `str(b"A")` with `b"A".decode("ascii")` |
| An f-string sanitizes values | Values become text automatically | Formatting only presents values; sink-specific safety remains separate | Put a newline or markup characters in a formatted value |
| Width means terminal columns | Width often aligns ASCII tables | Width is based on formatted string length, not universal display-cell width | Align combining and wide characters in a terminal |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| `len(text)` | Constant-time on CPython | Language documentation defines the result, not a cross-implementation big-O contract |
| `text[index]` | Constant-time on CPython | Selects one code point; result construction and representation are implementation details |
| `text[start:stop]` | Proportional to result size | A new immutable result is produced; the empty and whole-string cases may be optimized |
| `left + right` | Proportional to produced text | Repeated growth in a loop can become quadratic; implementation optimizations are not a design contract |
| `separator.join(parts)` | Proportional to total output plus traversal | Usually the clearest one-pass construction for many known string fragments |
| Equality or ordering | Up to the examined common prefix | Early differences can stop comparison; exact implementation details vary |
| Substring search and replacement | Input- and pattern-dependent | CPython uses optimized algorithms; avoid claiming one naive formula as the language guarantee |
| `split`, `casefold`, normalization, encoding | Proportional to examined input and produced output | Output may grow; normalization and encoding tables are Unicode/version dependent |

These are asymptotic engineering expectations, not measured results. The included experiment is observational and intentionally not a benchmark.

## 9. Production relevance and trade-offs

### API and storage boundaries

- Declare whether an API accepts text (`str`) or encoded data (`bytes`); do not silently accept both.
- Decode once near ingress and encode once near egress when the protocol allows it.
- Apply normalization consistently at a chosen boundary. Normalizing only queries or only writes can produce surprising uniqueness and lookup behavior.
- Match application comparison keys, database collations, uniqueness constraints, and migration rules deliberately.

### Identity, search, and security

- Preserve display text when product requirements value the user's spelling and casing.
- Use a derived key for a documented search or uniqueness policy; do not assume one key fits authentication, authorization, display, and audit needs.
- Normalization and casefolding do not solve homoglyphs, mixed scripts, bidirectional controls, or confusable identifiers.
- Bound accepted size before expensive normalization, logging, or downstream expansion when text is attacker-controlled.

### Parsing and validation

- Prefer structural methods such as `partition`, explicit-separator `split`, and exact affix methods when the grammar is simple.
- Preserve empty, missing, and whitespace-only states until the domain contract says they are equivalent.
- Use a real parser or destination API when the grammar is SQL, HTML, JSON, a shell, a URL, or another structured language.
- Treat `isalpha`, `isdigit`, and related Unicode predicates as character-property tools, not complete business validators.

### Formatting and observability

- Use `repr`-style diagnostics when seeing escapes and boundaries helps debugging, but avoid recording secrets and private data.
- Keep machine-readable events structured rather than relying on human-formatted strings as a protocol.
- Do not truncate a user-facing string by code points if the product promises intact user-perceived characters.
- Test representative multilingual, combining-mark, empty, control, delimiter, and supplementary-plane inputs.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| `str` is an immutable sequence of Unicode code points | Language / Standard library | Python 3 | Same behavior | Object layout is not implied by the language model |
| `str.removeprefix` and `str.removesuffix` | Standard library | 3.9 | Same API exists | Prefer these over manual slicing when literal-affix intent matters |
| F-string debug specifier such as `f"{value=}"` | Language | 3.8 | Same syntax exists | Best for diagnostics, not stable external protocols |
| Comments, backslashes, and same-quote nesting in f-string expressions | Language | 3.12 | Compute the expression before the f-string or change quoting | PEP 701 removed earlier grammar restrictions |
| Fractional-part grouping in the format mini-language | Standard library | 3.14 | Format without fractional grouping or implement explicit presentation | Presentation-only feature |
| Template string literal `t"..."` | Language / Standard library | 3.14 | No exact equivalent; use fixed f-strings for direct interpolation or an explicit structured template API | Produces a template object, not a `str`; processing policy remains explicit |
| Unicode character properties and case mappings | Standard library / Version dependent | Varies with bundled UCD | Query `unicodedata.unidata_version` and test required characters | CPython 3.14.4 in this unit reports Unicode 16.0.0 |
| Constant-time string length/indexing | CPython implementation detail | Implementation dependent | Do not encode the cost as a portable semantic guarantee | The language guarantees results, not this complexity |

The runnable examples avoid post-3.11 syntax so the core evidence remains interview-compatible. Newer syntax is isolated in version notes.

## 11. Practice brief

Exercises begin unsolved in [practice/README.md](practice/README.md).

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-BLT-020-P01` | Predict | 2 | E | Inline code-point, slice, method, and formatting table |
| `PY-BLT-020-P02` | Implement | 3 | C | Learner-created `practice/code_point_report.py` and tests |
| `PY-BLT-020-P03` | Implement / Design | 4 | C+E | Learner-created normalization-aware label registry and tests |
| `PY-BLT-020-P04` | Debug | 3 | D | Preserved faulty parser, smallest counterexamples, and repair |
| `PY-BLT-020-P05` | Review / Design | 5 | E+D | Text-boundary design review with explicit threat and portability limits |

## 12. Interview prompts

Answer one at a time; do not read or write full answers before an attempt.

1. What exactly does Python count in `len("e\u0301")`, and why may the displayed result appear to be one symbol?
2. Predict the difference between `text[0]`, `text[:1]`, and `text.encode("utf-8")[:1]` for non-ASCII text.
3. Why can two canonically equivalent strings compare unequal, and where would you normalize in a backend system?
4. Contrast `lower()` and `casefold()` without claiming either is locale-aware collation.
5. Explain the semantic difference between `split()` and `split(" ")`, including empty fields.
6. Why is `.strip(".json")` not a suffix operation? Give the smallest counterexample.
7. Explain evaluation, conversion, and formatting in `f"{value!r:>12}"`.
8. Design a username policy that preserves display text, supports lookup, and states what normalization cannot protect against.

A strong answer should eventually demonstrate:

- the code-point sequence model and its boundary with rendering and bytes;
- exact method and normalization contracts rather than ASCII-derived intuition;
- explicit production choices for validation, comparison, storage, formatting, security, and compatibility.

## 13. Closed-book revision cues

Without reading the note:

1. Write the one-sentence `str` mental model and four-layer text stack.
2. Reconstruct the composed/decomposed `é` visual, including code points, lengths, equality, and NFC result.
3. Predict outputs for a combining mark, an India flag, explicit/no-argument `split`, `find` at zero and missing, and `removeprefix` versus `lstrip`.
4. Draw the NFC → casefold → NFC comparison funnel and list two things it does not solve.
5. Explain the `str` ⇄ bytes boundary without entering the full `PY-BLT-030` buffer model.
6. Review a backend text pipeline and identify where limits, decoding, normalization, validation, comparison, storage, and formatting belong.

## 14. Authoritative sources

Only sources read during the 2026-08-29 audit are listed.

1. [Python 3.14.7 Standard Library—Text Sequence Type `str`, String Methods, and Common Sequence Operations](https://docs.python.org/3.14/library/stdtypes.html#text-sequence-type-str), accessed 2026-08-29.
2. [Python 3.14.7 Unicode HOWTO—code points, encodings, properties, and comparing strings](https://docs.python.org/3.14/howto/unicode.html), accessed 2026-08-29.
3. [Python 3.14.7 `unicodedata`—Unicode database and normalization](https://docs.python.org/3.14/library/unicodedata.html), accessed 2026-08-29.
4. [Python 3.14.7 Language Reference—string literals, raw strings, f-strings, and t-strings](https://docs.python.org/3.14/reference/lexical_analysis.html#string-and-bytes-literals), accessed 2026-08-29.
5. [Python 3.14.7 `string`—format syntax and format specification mini-language](https://docs.python.org/3.14/library/string.html#format-string-syntax), accessed 2026-08-29.
6. [Unicode Standard Annex #15, Unicode Normalization Forms, revision 57](https://www.unicode.org/reports/tr15/), accessed 2026-08-29.
7. [Unicode Technical Standard #39, Unicode Security Mechanisms](https://www.unicode.org/reports/tr39/), accessed 2026-08-29.
