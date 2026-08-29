# EXP-01 — Code points, normalization, casefolding, and visible text

| Field | Value |
|---|---|
| Owning unit | [PY-BLT-020](../../README.md) |
| Curriculum | [CURRICULUM.md](../../../../../CURRICULUM.md#py-blt-020) |
| Topic branch | `topic/PY-BLT-020` |
| Precise question | What do Python's public string and Unicode APIs reveal when equal-looking or single-looking text has different code-point representations? |
| Classification | Language and Standard library |
| Status | Reproduced |
| Risk | None |

## 1. Why an experiment is necessary

A renderer can hide the exact code-point sequence: precomposed and decomposed accents may look alike, while a flag or family emoji may look like one symbol. Capturing `len`, U+ notation, normalization comparison, case transformation, encoded size, and the Unicode database version makes the hidden representation observable without treating a screenshot as proof.

## 2. Hypothesis

Before execution:

> Precomposed `é` will contain one code point and decomposed `e` plus an acute mark will contain two. Exact equality will be false, NFC equality will be true, `lower()` will not equate `Straße` and `STRASSE`, and `casefold()` will. The India flag and family emoji will contain multiple Python string elements, and UTF-8 byte count will differ from `len(str)`.

Alternative outcome:

> Python or the environment could normalize text implicitly, index encoded units, apply broader equality, or use different case data, causing one or more predictions to fail.

## 3. Environment

Actual values recorded before the run:

```text
Date: 2026-08-29
Operating system: Linux 7.0.0-30-generic, glibc 2.43
Architecture: x86_64
Python version: 3.14.4
sys.version: 3.14.4 (main, Jun 18 2026, 14:25:02) [GCC 15.2.0]
sys.implementation: CPython
Build type: release-style build; Py_DEBUG=0
Free-threaded build: No; Py_GIL_DISABLED=0
Dependencies: Python standard library only
CPU: not reported; irrelevant to this non-benchmark observation
Relevant environment variables: PYTHONUTF8 unset; PYTHONIOENCODING unset
Unicode database reported by runtime: 16.0.0
```

## 4. Controls and variables

### Controlled

- one CPython executable and process;
- literal source sequences expressed with explicit Unicode escapes in the probe;
- NFC as the canonical normalization form;
- default Unicode `lower()` and `casefold()` implementations;
- UTF-8 as the one observed encoding;
- U+ notation rather than terminal cell width as the representation evidence.

### Changed

- precomposed versus decomposed accent spelling;
- lowercase versus casefold transformation;
- simple accent, regional-indicator pair, and zero-width-joiner sequence;
- code-point count versus UTF-8 byte count.

### Measured

- exact code-point sequence;
- `len(str)`;
- exact and NFC-normalized equality;
- lowercase and casefold equality;
- UTF-8 encoded length;
- runtime Unicode database version.

## 5. Files

```text
experiments/EXP-01-code-points-normalization-and-casefold/
├── README.md
└── unicode_probe.py
```

The unit's [focused tests](../../tests/test_examples.py) assert the stable semantic observations.

## 6. Reproduction command

From the repository root:

```bash
python units/built-in-types/PY-BLT-020-strings-and-unicode/experiments/EXP-01-code-points-normalization-and-casefold/unicode_probe.py
```

Test command:

```bash
python -m unittest discover -s units/built-in-types/PY-BLT-020-strings-and-unicode/tests -v
```

## 7. Prediction

```text
composed points: U+00E9; length 1
decomposed points: U+0065 U+0301; length 2
exact equality: false
NFC equality: true
lower equality for Straße/STRASSE: false
casefold equality for Straße/STRASSE: true
India flag: 2 code points
family emoji: 7 code points including three U+200D joiners
UTF-8 length differs from code-point length for non-ASCII examples
```

## 8. Observed output

Captured from the reproduction command on 2026-08-29:

```text
visuals: composed='é'; decomposed='é'
code-points: composed=U+00E9; decomposed=U+0065 U+0301
lengths: composed=1; decomposed=2
comparison: exact=False; NFC=True
caseless: lower=False; casefold=True
flag: len=2; points=U+1F1EE U+1F1F3
family: len=7; points=U+1F468 U+200D U+1F469 U+200D U+1F467 U+200D U+1F466
utf-8: composed-bytes=2; family-bytes=25
Unicode database: 16.0.0
```

No lines were omitted or edited.

## 9. Interpretation

1. The output directly shows that this `str` length and iteration model follows code points: the two accent spellings, flag, and family sequence have the predicted element counts.
2. It directly shows that Python exact equality does not normalize, while an explicit NFC comparison makes the accent spellings equal.
3. It directly shows that default Unicode casefolding equates the chosen German example where lowercasing does not.
4. It directly shows that UTF-8 byte count is a separate measurement from code-point count.
5. It is reasonable to infer that code-point inspection is more reliable than visual appearance for debugging representation.
6. The run cannot establish terminal display width, grapheme boundaries, locale-aware collation, security against confusables, performance, another encoding's size, or behavior for all Unicode strings.

## 10. Visual interpretation

```text
rendered accent                exact Python sequence

       é              ┌── composed:   [U+00E9] ───────── len 1
                      │
                      └── decomposed: [U+0065][U+0301] ─ len 2
                                           │
                                           └── NFC ──> [U+00E9]

rendered family       [person][ZWJ][person][ZWJ][person][ZWJ][person]
                                        7 code points / 25 UTF-8 bytes
```

### How to read this visual

Read the accent rows from rendering to code points and then through NFC. Read the family row as the seven elements counted by Python; encoding those elements produces a different number of UTF-8 bytes.

### Key insight

Visible appearance, code-point sequence, normalized equality, and byte representation are independent observables connected only by explicit algorithms.

### Simplification or limitation

The glyphs are labels for the tested strings, not evidence of renderer behavior. The diagram does not implement grapheme segmentation and does not depict CPython memory layout.

## 11. Language and implementation conclusion

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| `str` length and iteration expose the tested code-point sequences | Language / Standard library | Python 3.14.4 observation; Python 3 language model | Portable result for these exact strings; renderer is separate |
| Exact comparison does not normalize automatically | Language / Standard library | Python 3.14.4 observation | Portable; the explicit normalization form is application policy |
| NFC makes the tested canonical equivalents equal | Standard library / Unicode | CPython 3.14.4 with UCD 16.0.0 | Normalization follows the bundled Unicode data and Unicode stability rules |
| `casefold()` handles the tested sharp-S match where `lower()` does not | Standard library / Unicode | CPython 3.14.4 with UCD 16.0.0 | Default Unicode caseless mapping is not locale-aware collation |
| UTF-8 encoded sizes differ from code-point counts | Standard library / Encoding | Python 3.14.4 observation | Specific counts belong to UTF-8 and these exact strings |
| Runtime reports Unicode database 16.0.0 | Implementation / Version dependent | CPython 3.14.4 | Query the deployed runtime instead of assuming the newest Unicode release |

## 12. Limitations and threats to validity

- Only one CPython 3.14.4 build was run; no alternate interpreter was tested.
- The terminal rendering is not measured, and copied output may render differently elsewhere.
- The examples are representative, not an exhaustive Unicode normalization or casefold conformance suite.
- No grapheme-cluster library or Unicode segmentation algorithm was tested.
- Only UTF-8 was encoded, and encoding error handlers were not varied.
- No timing or allocation result was measured; this experiment supports no performance claim.
- The bundled Unicode 16.0.0 database differs from the newest Unicode Standard version, so newly assigned properties require a deployment-version check.

## 13. Follow-up

- Related unit: `PY-BLT-030` for bytes, bytearray, memoryview, encoding boundaries, and the buffer model.
- Improved experiment: add a Unicode normalization conformance subset when a later unit studies property-based and conformance testing.
- Remaining question: which grapheme-segmentation dependency and Unicode-version policy should a real UI use when product limits are defined in user-perceived characters?

## 14. Authoritative sources

1. [Python 3.14.7 Built-in Types—Text Sequence Type `str`](https://docs.python.org/3.14/library/stdtypes.html#text-sequence-type-str), accessed 2026-08-29.
2. [Python 3.14.7 Unicode HOWTO—Comparing Strings](https://docs.python.org/3.14/howto/unicode.html#comparing-strings), accessed 2026-08-29.
3. [Python 3.14.7 `unicodedata`—Unicode Database](https://docs.python.org/3.14/library/unicodedata.html), accessed 2026-08-29.
4. [Unicode Standard Annex #15—Unicode Normalization Forms](https://www.unicode.org/reports/tr15/), accessed 2026-08-29.
