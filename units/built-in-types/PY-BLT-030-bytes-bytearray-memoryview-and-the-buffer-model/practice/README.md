# Practice — PY-BLT-030 Bytes, bytearray, memoryview, and the buffer model

| Field | Value |
|---|---|
| Unit note | [`PY-BLT-030`](../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../CURRICULUM.md#py-blt-030) |
| Topic branch | `topic/PY-BLT-030` |
| Evidence target | E+C+X |
| Attempt required before solution | Yes |
| Test command | `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s units/built-in-types/PY-BLT-030-bytes-bytearray-memoryview-and-the-buffer-model/tests -v` plus learner-created focused tests |
| Status | Not attempted |

## Practice rules

1. Record a prediction or design before running code.
2. Preserve the original attempt, including the smallest failing version.
3. Request one progressive hint at a time; no hints are prewritten here.
4. A passing test is not enough when ownership, byte length, layout, or lifetime reasoning is wrong.
5. Final comparison code appears only after the exercise is closed.
6. Never use an address, reference count, or implementation accident as evidence for a public ownership contract.
7. Do not push later practice changes automatically unless the completion publication choice explicitly authorizes it.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Files | Status |
|---|---|---:|---|---|---|
| `PY-BLT-030-P01` | Predict | 3 | Trace construction, indexing, copying, aliasing, read-only access, and release | This file | Not attempted |
| `PY-BLT-030-P02` | Implement / Test | 4 | Parse a bounded binary envelope through the buffer protocol | Learner-created `envelope.py`, `test_envelope.py` | Not attempted |
| `PY-BLT-030-P03` | Implement / Design | 4 | Mutate fixed-width record flags in place without resizing | Learner-created `record_flags.py`, `test_record_flags.py` | Not attempted |
| `PY-BLT-030-P04` | Experiment | 4 | Reproduce ownership, format, shape, stride, and lifetime claims across exporters | Learner-created experiment directory | Not attempted |
| `PY-BLT-030-P05` | Review / Design | 5 | Review a binary upload pipeline with explicit ownership and resource limits | Learner-created `binary_pipeline_review.md` | Not attempted |

## PY-BLT-030-P01 — Predict binary sequence and view behavior

### Problem

Without running Python, record the exact value, type, exception class, and first governing rule for every label. Evaluate the statements in order because later labels observe earlier mutations.

```python
from array import array

blob = b"A\x00\xff"
mutable = bytearray(blob)
copied = mutable[1:]
root = memoryview(mutable)
window = root[1:]
readonly = window.toreadonly()

# A
type(blob[0]), blob[0]

# B
type(blob[:1]), blob[:1]

# C
b"A" in blob, 65 in blob

# D
bytes(3)

# E
bytes([65, 0, 255])

# F
bytes("é", "utf-8")

# G
type(bytearray(b"ab").upper())

# H
mutable[0] = ord("Z")
(mutable, copied, window.tobytes())

# I
window[0] = 7
(mutable, copied, readonly.tobytes())

# J
readonly[0] = 8

# K
snapshot = bytes(window)
mutable[2] = 9
(snapshot, window.tobytes(), readonly.tobytes())

# L
mutable.append(10)

# M
readonly.release()
window.release()
root.release()
mutable.append(10)
mutable

# N
window[0]

words = array("H", [1, 256, 513])
word_view = memoryview(words)

# O
(len(word_view), word_view.itemsize, word_view.nbytes, word_view.format)

# P
byte_view = word_view.cast("B")
(len(byte_view), byte_view.itemsize, byte_view.nbytes)

# Q
strided = byte_view[::2]
(strided.shape, strided.strides, strided.c_contiguous)
```

Do not compress the answer into “bytes are immutable and views are shared.” Each label must identify the operation's element type, result ownership, current exporter state, and whether an exception leaves state unchanged.

### Learning evidence

This exercise should demonstrate:

- exact distinction among byte values, one-byte binary sequences, copied slices, and view slices;
- stateful reasoning about mutations visible through aliases;
- the difference between read-only permission and an immutable snapshot;
- view-release and exporter-resize lifetime reasoning;
- separation of element count, item size, logical byte count, and physical stride.

### Constraints

- Do not run any line until all predictions are recorded.
- Use decimal and two-digit hexadecimal notation for byte values when that aids checking.
- Do not use `id()`, `sys.getrefcount()`, `ctypes`, or implementation-specific addresses.
- Treat native `array('H')` byte order and item size as runtime facts; predict portable relationships before exact platform values.
- Preserve predictions even when execution disproves them.

### Required edge cases

- integer indexing versus slicing;
- integer and subsequence containment;
- integer constructor as size versus iterable constructor as values;
- non-ASCII text encoding;
- mutation through exporter and view;
- read-only view over mutable storage;
- live-export resizing restriction;
- released-view access;
- element count versus `nbytes`;
- non-contiguous striding.

### Acceptance criteria

- [ ] All seventeen labels have exact predictions and governing rules.
- [ ] Stateful answers use the mutations from earlier labels.
- [ ] Copy, alias, and snapshot claims are kept separate.
- [ ] Native-layout uncertainty is stated rather than guessed.
- [ ] Every mismatch names the first incorrect assumption.
- [ ] Observed output is recorded only after all predictions are preserved.

### Prediction before execution

| Label | Predicted value/type/exception | Ownership or lifetime reasoning | Confidence |
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
| P |  |  |  |
| Q |  |  |  |

### Learner attempt

- Attempt date:
- Python runtime:
- Execution command:
- Observed results:
- First mismatch:
- Corrected mental model:

### Progressive hints

No hints are recorded. Request one only after completing the prediction table.

## PY-BLT-030-P02 — Implement a bounded binary envelope parser

### Problem

Implement this public contract:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Envelope:
    version: int
    flags: int
    payload: bytes

def parse_envelope(data: object, *, max_payload: int = 1_048_576) -> Envelope:
    """Validate and parse one complete PM envelope from a contiguous buffer."""
```

The synthetic wire layout is:

```text
offset  size  meaning
0       2     ASCII magic bytes PM
2       1     version; only 1 is accepted
3       1     flags; high four bits are reserved and must be zero
4       4     unsigned payload byte length in network byte order
8       N     opaque payload bytes
8+N     1     checksum: sum(payload byte values) modulo 256
```

The parser accepts any object whose exported buffer is readable and C-contiguous. It must validate the header and bounded declared length before materializing the final `bytes` payload. It must consume exactly one complete envelope: missing and trailing bytes are errors.

### Learning evidence

This exercise should demonstrate:

- protocol parsing by byte offsets and explicit network order;
- generic buffer consumption without treating `str` as binary data;
- correct use of `nbytes` when element size need not be one;
- size validation before copying or allocating attacker-declared data;
- deterministic cleanup of temporary views on every success and failure path.

### Constraints

- Use only Python 3.11-compatible standard-library code.
- Accept at least `bytes`, `bytearray`, `memoryview`, and `array('B')` inputs.
- Reject `str`, non-buffer objects, and non-C-contiguous views explicitly.
- Do not call `bytes(data)` or `.tobytes()` before validating magic, version, flags, declared length, total length, and `max_payload`.
- Use an explicit byte-order contract; do not rely on native `struct` mode.
- Reject `bool` for `max_payload`, negative limits, and payload declarations beyond the caller's limit.
- Release every view even when validation fails.
- Do not import or adapt the completed example module.

### Examples

```text
Valid domains:
empty payload; opaque payload containing zero and 0xff; read-only and writable exporters

Invalid domains:
short header; wrong magic; unsupported version; reserved flag; length overflow;
truncation; trailing byte; wrong checksum; non-contiguous view; text input
```

### Required edge cases

- empty payload with checksum zero;
- maximum accepted payload and one byte over the caller's limit;
- a declared length that is much larger than the actual input;
- correct prefix followed by trailing junk;
- checksum wraparound modulo 256;
- a multi-byte element exporter whose `nbytes` differs from `len(view)`;
- a step-sliced non-contiguous view;
- all validation failures leave the mutable input unchanged.

### Acceptance criteria

- [ ] The public contract and exception taxonomy are documented.
- [ ] Header interpretation is independent of host byte order and alignment.
- [ ] Bounds are validated before payload materialization.
- [ ] Focused tests cover every required edge case and all named exporters.
- [ ] Resource release is deterministic on success and failure.
- [ ] The learner can identify the one intentional copy and why the return type requires it.
- [ ] No unrelated streaming framework or protocol abstraction was added.

### Prediction before implementation

- Exact header size:
- First validation that must occur:
- Point at which payload copying becomes safe:
- Expected ownership of returned payload:
- Cleanup strategy:
- Most likely hidden bug:

### Learner attempt

- Attempt file: `practice/envelope.py`
- Test file: `practice/test_envelope.py`
- Learner's design:
- Test command:
- Observed result:

### Progressive hints

No hints are recorded. Request the smallest conceptual nudge after preserving a failing attempt.

## PY-BLT-030-P03 — Clear reserved flag bits in place

### Problem

Implement this fixed-record mutation contract:

```python
def clear_reserved_bits(buffer: object) -> int:
    """Clear the high two flag bits in each four-byte record; return changes."""
```

Each record is exactly four bytes:

```text
byte 0: flags (bits 7 and 6 reserved; bits 5 through 0 meaningful)
byte 1: record code
bytes 2..3: opaque value bytes that this function must not interpret
```

The function must mutate writable C-contiguous storage in place, must not change the buffer's length, and must return the number of records whose flag byte changed. An empty buffer contains zero valid records.

### Learning evidence

This exercise should demonstrate:

- a writable buffer consumer whose mutation permissions are explicit;
- byte-level masking without disturbing unrelated fields;
- fixed-size mutation through a view without resizing or returning a replacement buffer;
- validation of layout, record boundaries, mutability, and exporter lifetime.

### Constraints

- Accept writable `bytearray`, writable `memoryview`, and `array('B')` exporters.
- Reject immutable `bytes`, read-only views, text, and arbitrary iterables.
- Reject non-C-contiguous views and byte lengths not divisible by four.
- Do not reconstruct the entire buffer, use slice deletion, append, resize, or return a new binary sequence.
- Do not interpret the two value bytes with native byte order.
- Preserve every non-reserved bit and byte exactly.
- Use Python 3.11-compatible standard-library code.
- Do not import the unit's example mutation helper.

### Examples

```text
Input records, shown as hexadecimal:
c1 10 aa bb | 3f 20 00 ff | 80 30 12 34

Observable contract:
only bits 7 and 6 of byte zero in each four-byte record may change;
the function returns how many flag bytes changed
```

The example states the contract but deliberately omits the resulting bytes.

### Required edge cases

- empty writable exporter;
- one record with neither reserved bit set;
- one record with one reserved bit set;
- one record with both reserved bits set;
- several records with zero and `0xff` in opaque positions;
- truncated final record;
- read-only and non-contiguous views;
- a writable subview over a larger exporter, proving bytes outside the subview remain unchanged.

### Acceptance criteria

- [ ] Mutation is visible through the original exporter.
- [ ] Length and all non-reserved data remain unchanged.
- [ ] The return count matches records actually modified.
- [ ] Every required edge case has a deterministic test.
- [ ] Failure occurs before partial mutation when structural validation fails.
- [ ] The learner explains why a read-only view is different from immutable storage.
- [ ] The original attempt remains preserved.

### Prediction before implementation

- Required validation order:
- Byte positions that may change:
- Invariant for length and untouched bytes:
- Expected result for already-clean input:
- Cleanup strategy:

### Learner attempt

- Attempt file: `practice/record_flags.py`
- Test file: `practice/test_record_flags.py`
- Learner's reasoning:
- Test command:
- Observed result:

### Progressive hints

No hints are recorded. Request one only after adding a test that detects partial or out-of-window mutation.

## PY-BLT-030-P04 — Run a cross-exporter buffer contract experiment

### Problem

Design, predict, run, and interpret a deterministic experiment comparing:

1. `bytes`;
2. `bytearray`;
3. `array('H')`;
4. a writable `memoryview` and its read-only derivative;
5. a contiguous view, a step-two view, and a legal cast.

The experiment must answer:

- Which operations copy, and which create views?
- Which mutations are visible through which handles?
- What do `len`, `itemsize`, `nbytes`, `format`, `shape`, and `strides` measure?
- Which layouts are C-contiguous?
- Which handles permit writes?
- Which live exports prevent exporter resizing?
- What remains valid after releasing a parent view while a derived view still exists, and after releasing every view?

Do not reuse the canonical experiment's exact inputs or report. Choose a distinct bounded dataset and add at least one multi-byte element observation.

### Learning evidence

This exercise should demonstrate:

- a falsifiable hypothesis stated before execution;
- controlled observation of hidden alias and lifetime state;
- separation of portable contracts from runtime-labelled observations;
- honest limitations that rule out allocation, speed, and universal-layout claims.

### Constraints

- Create a dedicated directory under `practice/experiments/` only after recording the hypothesis.
- Follow `templates/experiment.md` structure.
- Use only public APIs and standard-library exporters.
- Record exact runtime, implementation, OS, architecture, build flags, command, and unedited relevant output.
- Do not use timing, addresses, `id()`, reference counts, private APIs, `ctypes`, or CPython source as a shortcut.
- Treat native `array('H')` size and byte order as measured platform facts.
- Clean up all views deterministically.
- Add focused assertions for stable semantic observations.

### Required controls

- one initial dataset per exporter;
- one same-size write;
- one resize attempt before and after release;
- one snapshot conversion;
- one read-only derived view;
- one multi-byte element format;
- one strided non-contiguous view;
- no randomness, concurrency, filesystem input, or third-party dependency.

### Acceptance criteria

- [ ] The question, hypothesis, alternative outcome, controls, and variables precede execution.
- [ ] Raw or exact relevant output is preserved.
- [ ] Every conclusion cites the observation that supports it.
- [ ] Language, standard-library, CPython, platform, and artifact claims are classified separately.
- [ ] Python 3.11 compatibility is documented without claiming it was run unless it was.
- [ ] The visual has a reading guide, key insight, and limitation.
- [ ] The report makes no unmeasured allocation or performance claim.

### Prediction before execution

- Expected copy/view relationships:
- Expected mutation visibility:
- Expected element and byte-count relationships:
- Expected resize restriction:
- Platform-sensitive facts:
- Alternative outcome that would change the model:

### Learner attempt

- Experiment directory: `practice/experiments/EXP-01-.../`
- Reproduction command:
- Prediction preserved:
- Observed output:
- First mismatch:
- Interpretation:
- Limitations:

### Progressive hints

No hints are recorded. Request one after writing the question, hypothesis, controls, and expected report fields.

## PY-BLT-030-P05 — Review a bounded binary upload pipeline

### Problem

Write a senior-level design review for this synthetic service requirement:

> An HTTP endpoint accepts a compressed binary upload of up to 200 MiB. The first 24 decompressed bytes are a fixed header, followed by UTF-8 metadata and an opaque media payload. The implementation currently reads the complete request into `bytes`, copies it into `bytearray`, creates several long-lived `memoryview` slices, decodes metadata with `errors="ignore"`, sends a view to a background worker, and appends a checksum to the original `bytearray`. It logs failed payload prefixes and stores the media in an object store.

Turn every ambiguous sentence into an explicit, testable ownership, validation, and resource policy. The review must address network chunking, compressed and decompressed limits, decompression bombs, header byte order, exact length checks, malformed UTF-8, view lifetime, resize restrictions, mutation ownership, asynchronous handoff, snapshots versus aliases, storage API expectations, logging/privacy, cleanup, observability, and Python 3.11/3.14 compatibility.

### Learning evidence

This exercise should demonstrate:

- transfer from built-in binary semantics to a backend boundary;
- explicit decisions about ownership, copying, lifetime, and mutation;
- resource-exhaustion reasoning before allocation and decompression;
- refusal to treat zero-copy as an unconditional optimization.

### Constraints

- Use synthetic identifiers and data only.
- Do not propose accepting both `str` and bytes-like values through implicit conversion.
- Do not use `errors="ignore"` without documenting irreversible data loss and a domain reason.
- Do not claim a `memoryview` is safe across asynchronous ownership transfer merely because it is read-only.
- Name where input, decompressed, metadata-byte, text, and media limits are enforced and in which units.
- Distinguish checksum/integrity detection from authentication and authorization.
- Identify at least four decisions requiring product, protocol, security, infrastructure, or storage-owner input.
- Include failure cleanup and metrics without logging private payload bytes.

### Required edge cases

- a small compressed body expanding beyond the decompressed limit;
- a header split across network chunks;
- declared lengths below, equal to, and above available bytes;
- non-ASCII metadata whose code-point and UTF-8 byte lengths differ;
- malformed UTF-8 at the end of a metadata window;
- payload mutation after a view is handed off;
- checksum append while live views exist;
- cancellation or worker failure while buffers are retained;
- storage SDK accepting a general buffer versus requiring immutable `bytes`;
- diagnostic logging for a secret-bearing payload.

### Acceptance criteria

- [ ] The review includes an ownership-and-lifetime table or diagram.
- [ ] Every limit names bytes, code points, records, or decompressed units explicitly.
- [ ] Copy points are justified by ownership or API boundaries, not hidden.
- [ ] View acquisition, handoff, release, and mutation rules are testable.
- [ ] Error handling preserves the first protocol violation and cleans resources.
- [ ] Security, integrity, encoding, and privacy claims are not conflated.
- [ ] Tests, metrics, cancellation behavior, and portability notes are included.
- [ ] Unresolved decisions name the responsible external owner.

### Prediction before design

- Proposed ownership model:
- Intentional copy points:
- Maximum simultaneously retained bytes:
- View lifetime boundary:
- Text decoding policy:
- Security properties deliberately not claimed:
- Questions requiring external ownership:

### Learner attempt

- Review file: `practice/binary_pipeline_review.md`
- Design summary:
- Strongest claim with evidence:
- Highest-risk unresolved boundary:
- Review result:

### Progressive hints

No hints are recorded. Request one after drawing the ownership pipeline and listing all size units.

## Practice closure

Complete only after individual exercises are reviewed.

| Evidence | Status | Link | What remains |
|---|---|---|---|
| Explanation and prediction | Not attempted | — | Complete and review `PY-BLT-030-P01` |
| Code | Not attempted | — | Complete and review `PY-BLT-030-P02` and `PY-BLT-030-P03` |
| Runtime experiment | Not attempted | — | Complete, reproduce, and review `PY-BLT-030-P04` |
| Production transfer | Not attempted | — | Complete and review `PY-BLT-030-P05` |

Do not advance `PROGRESS.md` from generated exercises alone. Link preserved learner attempts, actual test output, the reproduced learner experiment, and review evidence.
