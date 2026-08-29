# EXP-01 — Buffer aliasing, metadata, and view lifetime

| Field | Value |
|---|---|
| Owning unit | [`PY-BLT-030`](../../README.md) |
| Curriculum | [`CURRICULUM.md`](../../../../../CURRICULUM.md#py-blt-030) |
| Topic branch | `topic/PY-BLT-030` |
| Precise question | Which public observations distinguish a copied `bytearray` slice from an aliasing `memoryview`, and how do mutability, layout metadata, striding, and release affect the exporter? |
| Classification | Python and standard-library buffer contracts observed on CPython |
| Status | Reproduced |
| Risk | None; deterministic, bounded, standard-library-only memory operations |

## 1. Why an experiment is necessary

The expressions `data[2:6]` and `memoryview(data)[2:6]` can expose the same initial byte values while having opposite ownership behavior. A static value print therefore cannot establish whether later writes are shared. The restrictions caused by a live export, the invalid state after `release()`, and the shape/stride interpretation of one storage block are also hidden until code observes them.

This experiment uses only public operations: slicing, integer assignment, `toreadonly()`, `release()`, `cast()`, documented attributes, `hex()`, and a `bytearray.append()` resize attempt. It does not inspect addresses, object layout, reference counts, C structures, allocator state, or timing.

## 2. Hypothesis

Before execution:

> Slicing a `bytearray` will create an independent `bytearray`, while slicing its `memoryview` will create another view of the exporter's storage. Writes through the writable view and direct same-size writes through the exporter will therefore be mutually visible, but the copied slice will remain unchanged. A read-only view will reject writes without becoming a snapshot. While views remain exported, resizing the `bytearray` will fail; after all views are released, resizing will succeed and the released view will reject access. Casting eight byte elements to a 2-by-4 view will change shape and strides without changing byte count, while a step-two slice will be non-contiguous.

Alternative outcomes requiring investigation:

- the `bytearray` slice aliases the original;
- the memoryview slice copies values;
- `toreadonly()` creates a frozen snapshot;
- same-size mutation is blocked together with resizing;
- releasing one or all views does not remove the resize restriction;
- accessing a released view remains valid;
- the two-dimensional cast changes or copies byte values;
- the step-two view is reported as C-contiguous;
- an exception class or layout attribute differs on the available runtime.

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

The repository documentation baseline is Python 3.14.7. Execution used the available CPython 3.14.4 runtime. The probe avoids post-3.11 syntax and APIs, but no Python 3.11 interpreter was executed for this observation.

## 4. Controls and variables

### Controlled

- one CPython executable and process;
- initial mutable exporter `bytearray(range(8))`;
- slice bounds `[2:6]` for both copy and view;
- fixed-size writes `0xAA` and `0xBB`;
- one read-only view derived from the writable view;
- one append attempt before release and one after release;
- immutable eight-byte input for shape and stride observations;
- hexadecimal values and public metadata rather than addresses or object identities;
- no randomness, timing, files, network access, threads, subprocesses, or third-party dependencies.

### Changed

- access path: copied slice, writable view, read-only view, or exporter;
- mutation source: view write or direct exporter write;
- exporter state: live exports versus all experiment-owned views released;
- interpretation: one-dimensional bytes, two-dimensional 2-by-4 bytes, or step-two strided bytes.

### Measured

- hexadecimal values of exporter, copy, and views before and after writes;
- `format`, `itemsize`, `ndim`, `shape`, `strides`, `nbytes`, `readonly`, and `c_contiguous`;
- exception class from resizing with live views;
- exception class from accessing a released view;
- exporter length and appended value after release;
- one indexed matrix element and the step-two logical byte sequence.

## 5. Files

```text
experiments/EXP-01-aliasing-metadata-and-view-lifetime/
├── README.md
└── buffer_alias_probe.py
```

Runnable source: [`buffer_alias_probe.py`](buffer_alias_probe.py)

Focused regression: [`../../tests/test_examples.py`](../../tests/test_examples.py)

## 6. Reproduction command

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python units/built-in-types/PY-BLT-030-bytes-bytearray-memoryview-and-the-buffer-model/experiments/EXP-01-aliasing-metadata-and-view-lifetime/buffer_alias_probe.py
```

Focused regression command:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s units/built-in-types/PY-BLT-030-bytes-bytearray-memoryview-and-the-buffer-model/tests -v
```

## 7. Prediction

```text
initial: exporter=0001020304050607; copy=02030405; view=02030405
view-write: exporter=0001aa0304050607; copy=02030405; view=aa030405
exporter-write: exporter=0001aabb04050607; view=aabb0405; readonly-view=aabb0405
view-metadata: format=B; itemsize=1; ndim=1; shape=(4,); strides=(1,); nbytes=4; readonly=False; c_contiguous=True
resize-while-exported: BufferError
access-after-release: ValueError
resize-after-release: length=9; tail=255
matrix: format=B; itemsize=1; ndim=2; shape=(2, 4); strides=(4, 1); nbytes=8; element[1,2]=6
strided: bytes=00020406; shape=(4,); strides=(2,); c_contiguous=False
```

## 8. Observed output

Captured from the reproduction command on 2026-08-29:

```text
initial: exporter=0001020304050607; copy=02030405; view=02030405
view-write: exporter=0001aa0304050607; copy=02030405; view=aa030405
exporter-write: exporter=0001aabb04050607; view=aabb0405; readonly-view=aabb0405
view-metadata: format=B; itemsize=1; ndim=1; shape=(4,); strides=(1,); nbytes=4; readonly=False; c_contiguous=True
resize-while-exported: BufferError
access-after-release: ValueError
resize-after-release: length=9; tail=255
matrix: format=B; itemsize=1; ndim=2; shape=(2, 4); strides=(4, 1); nbytes=8; element[1,2]=6
strided: bytes=00020406; shape=(4,); strides=(2,); c_contiguous=False
```

The prediction and observation matched. No output was edited to create that match. The focused suite also ran 20 tests successfully on the recorded runtime.

## 9. Interpretation

1. The copy and view began with equal visible bytes, but only the view tracked later writes. Initial equality therefore did not imply shared ownership.
2. Assigning through the view changed the exporter, and assigning through the exporter changed both writable and read-only views. The read-only flag controls writes through that view; it does not freeze or copy the exporter.
3. The copied `bytearray` remained `02030405`, proving independence for this operation without relying on object identity or memory addresses.
4. The live views permitted equal-size byte replacement but the append attempt raised `BufferError` on this runtime. That matches the documented rule that a `bytearray` temporarily forbids resizing while a view is exported.
5. Once both experiment-owned views were released, access through the released view raised `ValueError` and appending `0xFF` succeeded.
6. The two-dimensional view retained `nbytes=8` while exposing shape `(2, 4)`, strides `(4, 1)`, and element `[1,2]=6`. A cast changed interpretation metadata, not the tested bytes.
7. The step-two view exposed bytes `00 02 04 06`, stride `(2,)`, and `c_contiguous=False`. Logical sequence length and physical adjacency are distinct properties.
8. The run supports ownership, metadata, and lifetime reasoning. It does not measure allocation size, prove a universal asymptotic cost, or establish behavior for every exporter and consumer.

## 10. Visual interpretation

```text
storage owned by bytearray exporter
index       0    1    2    3    4    5    6    7
initial    [00] [01] [02] [03] [04] [05] [06] [07]
                       ^----------------^
                       view [2:6] aliases

copied     independent [02] [03] [04] [05]

view[0]=AA                  │
                            v
exporter   [00] [01] [AA] [03] [04] [05] [06] [07]
copied                [02] [03] [04] [05]    unchanged

live view ──> same-size writes allowed; exporter resize held
release   ──> view invalid; exporter resize allowed again
```

### How to read this visual

Read the top row as the exporter's eight storage positions. The bracket under positions 2 through 5 is a window onto those positions, while the separate copied row owns independent values. Then follow the mutation arrow into the exporter and the lifetime line from live export to release.

### Key insight

A `memoryview` is an interpretation and permission-bearing reference to exporter-owned storage, not an immutable value snapshot; ownership and lifetime remain part of the API contract.

### Simplification or limitation

The boxes are conceptual byte positions, not literal CPython object layout or addresses. The visual omits export counters, C-level request flags, multi-byte element formats, negative strides, suboffsets, concurrent access, and exporters with external resources.

## 11. Language and implementation conclusion

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| A `bytearray` slice in the probe produced an independent mutable binary sequence. | Built-in sequence contract plus observation | CPython 3.14.4; Python 3 contract | Do not infer the same ownership rule for `memoryview` slicing or third-party array APIs. |
| The memoryview slice shared writes with its exporter. | Standard-library buffer contract plus observation | CPython 3.14.4; documented in Python 3.14.7 and 3.11.15 | Mutability still depends on exporter and requested view. |
| A read-only derived view observed later exporter writes. | Standard-library contract plus observation | CPython 3.14.4 | Read-only means writes through that view are forbidden; it does not promise a snapshot. |
| The live views temporarily prevented `bytearray` resizing. | Standard-library contract plus observation | CPython 3.14.4 | `BufferError` is the observed exception; other exporters may impose different resource restrictions. |
| A released memoryview rejected later access. | Standard-library contract plus observation | CPython 3.14.4 | `release()` is idempotent, but other operations on that released view are invalid. |
| `cast()` changed shape and format interpretation without copying the buffer. | Standard-library contract plus observation | CPython 3.14.4 | Supported casts require documented contiguity, format, and equal-byte-length conditions. |
| The step-two view was non-contiguous and retained a stride of two bytes. | Standard-library metadata contract plus observation | CPython 3.14.4 | Consumers may reject layouts they cannot handle; acceptance is consumer-specific. |
| Exact exception text and report order are artifact observations. | CPython / Tooling observation | This runtime and repository artifact | Tests intentionally assert stable exception classes, not CPython wording. |

## 12. Limitations and threats to validity

- Only CPython 3.14.4 on one Linux x86_64 regular GIL-enabled build was executed.
- Python 3.14.7 and 3.11.15 documentation were audited, but neither maintenance release was run.
- Only `bytes` and `bytearray` storage were used in the probe; `array.array` appears in focused tests, and no NumPy, image, shared-memory, or custom exporter was tested.
- Only unsigned-byte element format `B` was observed; native multi-byte formats can have platform-dependent size and byte order.
- The matrix is C-contiguous and the strided view is one-dimensional; Fortran layout, negative strides, zero-dimensional views, and suboffsets are not covered.
- The append attempt observes one resizing operation and exception class; it does not expose the export counter or prove internal implementation structure.
- No address, allocation, copy counter, profiler, or timing measurement was taken, so the experiment supports no allocation count or speedup claim.
- No concurrent mutation was attempted. Shared visibility does not itself define synchronization or atomicity.

## 13. Follow-up

- Related unit: `PY-IOP-010` for binary files, streams, buffering, and `readinto()` boundaries.
- Improved experiment: reproduce the same semantic assertions on an actual Python 3.11 runtime and append a version-labelled result.
- Improved experiment: add an exporter with a multi-byte format and state the native-size and byte-order controls explicitly.
- Remaining question: which deployed consumers require C-contiguous bytes, and which correctly accept general shape/stride metadata?

## 14. Authoritative sources

1. [Python 3.14.7 Standard Library — Binary Sequence Types and Memory Views](https://docs.python.org/3.14/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview), accessed 2026-08-29.
2. [Python 3.14.7 C API — Buffer Protocol](https://docs.python.org/3.14/c-api/buffer.html), accessed 2026-08-29.
3. [Python 3.14.7 Standard Library — `struct`](https://docs.python.org/3.14/library/struct.html), accessed 2026-08-29.
4. [Python 3.11.15 Standard Library — Memory Views](https://docs.python.org/3.11/library/stdtypes.html#memory-views), accessed 2026-08-29.
