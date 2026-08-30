# EXP-02 — Slice positions and compact range descriptions

| Field | Value |
|---|---|
| Owning unit | [PY-BLT-040](../../README.md) |
| Curriculum | [CURRICULUM.md](../../../../../CURRICULUM.md#py-blt-040) |
| Topic branch | `topic/PY-BLT-040` |
| Precise question | How do normalized slice bounds select positions, and which range operations still work without materializing the represented values? |
| Classification | Built-in contracts; CPython/platform observations for size and length limits |
| Status | Reproduced |
| Risk | Resource if modified carelessly; the supplied probe never materializes the huge range |

## 1. Why an experiment is necessary

Omitted and explicit negative bounds look similar but normalize differently. Range slices demonstrate that selecting values can transform a compact description. The large-range case separates representability, index access, and platform length limits.

## 2. Hypothesis

Author prediction during probe design, not a learner answer:

> With six source positions, an omitted negative-step stop normalizes to a sentinel before position zero. Explicit `-1` normalizes to the last position. A range slice remains arithmetic, and a huge range can support small slices and integer membership even if `len` overflows. Shallow size need not grow with the count of represented elements.

Alternative outcome: the two negative stops might select the same positions, a range slice might materialize its elements, or an unrepresentable `len` might make every operation invalid. The printed values distinguish these possibilities.

## 3. Environment

Actual execution date: **2026-08-30**.

```text
Operating system: Linux 7.0.0-30-generic
Architecture: x86_64
CPU: Intel(R) Core(TM) i7-14700HX
Canonical runtime: CPython 3.14.7
sys.version: 3.14.7 (main, Aug 25 2026, 14:02:56) [Clang 22.1.3 ]
sys.implementation.name: cpython
sys.implementation.cache_tag: cpython-314
Compatibility runtime: CPython 3.11.16
sys.version: 3.11.16 (main, Aug 25 2026, 14:00:53) [Clang 22.1.3 ]
sys.implementation.name: cpython
sys.implementation.cache_tag: cpython-311
Build type: release on both
Free-threaded build: False on both
GIL: enabled on 3.14.7; conventional build on 3.11.16
Dependencies: standard library only
Flags: -B (no bytecode writes)
PYTHONHASHSEED: unset; output does not depend on hashing
```

No wall-clock or process-memory measurement was made. `getsizeof` records shallow object size only.

## 4. Controls and variables

### Controlled

Keep the six-letter source and operation order fixed. The huge progression has `start=0`, `stop=10**40`, and `step=3`; select only its first three values and query a plain integer member. Never run `list(huge)` or a potentially linear search with a non-integer candidate.

### Changed

Change raw slice bounds and step, including omission versus explicit `-1`. Compare ranges with different stops, independent iterators, small versus large counts, and an overflowing length.

### Measured

Normalized triples, selected positions, selected values, range representation, equality, iterator advancement, exception classes, and shallow byte sizes.

## 5. Files

- [slice_range_probe.py](slice_range_probe.py): executable probe.
- [Slice explorer](../../visuals/slice-explorer.html): interactive model of ordinary slices.
- [Explorer verification](../../tests/test_visual_model.py): 9,100 model cases checked against Python, plus input validation.

## 6. Reproduction command

From the repository root, with `python` selecting the intended runtime:

```bash
python -B units/built-in-types/PY-BLT-040-lists-tuples-ranges-and-sequence-behaviour/experiments/EXP-02-slices-and-ranges/slice_range_probe.py
```

The command was run with `python` selecting CPython 3.14.7, then CPython 3.11.16. Each selected version was checked before execution. Match the recorded runtime and flags when comparing results; a machine-specific installation path is not required.

## 7. Prediction

The full reverse will visit all six positions. The explicit `-1` stop with a negative step will select none. Clipped bounds will preserve the specified stride. Reusing the normalized reverse triple as a raw slice will lose the omitted-bound meaning. Range slicing will produce a new progression; equal represented sequences can have different stops. Fresh iterators will advance independently. The huge range will support a three-element prefix and integer membership, while its length raises `OverflowError`. No exact shallow byte count was predicted.

## 8. Observed output

Both tested runtimes produced this complete, identical stdout:

```text
[::-1]: bounds=(5, -1, -1); positions=[5, 4, 3, 2, 1, 0]; values=['F', 'E', 'D', 'C', 'B', 'A']
[:-1:-1]: bounds=(5, 5, -1); positions=[]; values=[]
[50:-50:-2]: bounds=(5, -1, -2); positions=[5, 3, 1]; values=['F', 'D', 'B']
[1:5:2]: bounds=(1, 5, 2); positions=[1, 3]; values=['B', 'D']
[1:1]: bounds=(1, 1, 1); positions=[]; values=[]
normalized bounds reused as a raw slice: []
zero slice step: ValueError
range slice: range(7, 27, 8); values=[7, 15, 23]
equal sequences, different stops: True
two fresh iterators: 3, 7; 3
huge range first three: [0, 3, 6]
huge range integer membership: True
huge range length: OverflowError
shallow range sizes in bytes: small=48; large=48
```

## 9. Interpretation

The reverse triples distinguish a stop sentinel from an explicit negative index. `range(*normalized)` expands the selected positions correctly; rebuilding a raw slice causes Python to interpret its negative numbers again.

The range slice denotes `[7, 15, 23]`, and its stop of `27` is an exclusive bound, not a required member. Different constructor parameters can therefore describe the same sequence. The fresh iterators begin independently, while the huge progression remains usable for the bounded operations shown.

The equal **48-byte shallow sizes** are observations on these two x86_64 CPython builds. [`sys.getsizeof`](https://docs.python.org/3.14/library/sys.html#sys.getsizeof) excludes referenced objects: it does not measure integer payloads, total reachable memory, process memory, or allocations made while iterating. Integer magnitude can affect storage and arithmetic cost. This is not proof of a universal byte count or speedup.

## 10. Visual interpretation

```text
raw slice                 normalized triple       visited positions
slice(None, None, -1)  ->  (5, -1, -1)         ->   5, 4, 3, 2, 1, 0
slice(None,   -1, -1)  ->  (5,  5, -1)         ->   none

the normalized -1 is a stop for range(), not an instruction to count from the end
```

### How to read this visual

Read each row left to right. Normalization uses the source length; expansion then obeys the resulting range's direction and exclusive stop.

### Key insight

Raw slice inputs and normalized position bounds belong to different stages. Keep their roles separate.

### Simplification or limitation

The diagram uses one six-element source. It describes built-in slicing, not arbitrary `__getitem__` methods, literal memory layout, or mutation through a view.

## 11. Language and implementation conclusion

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| Omitted bounds depend on step direction | Built-in slice contract | Observed on CPython 3.14.7 and 3.11.16 | Custom objects may interpret slices differently |
| Range slicing and equality concern represented values | Built-in contract | Same observed versions | A representation's exact stop is not unique |
| Range is reusable; its iterators have positions | Sequence / iterator contract | Same observed versions | Does not imply other iterables are reusable |
| Huge length raises while bounded access works | CPython/platform length boundary | x86_64 versions above | Different platforms have different limits |
| Both tested shallow sizes are 48 bytes | CPython measurement | Only the builds above | Not a total-memory or portable-size guarantee |

## 12. Limitations and threats to validity

- No benchmark, process-memory measurement, or alternative-interpreter test was run.
- Small-domain model tests cannot establish support for arbitrary Python integers in JavaScript; the explorer deliberately rejects unsafe integers.
- Plain integer membership here does not establish lookup cost for floats, integer subclasses, or custom equality objects.
- Do not convert the huge range into a list or tuple when adapting the probe.
- Author execution does not advance the learner's progress state.

## 13. Follow-up

In `PY-BLT-040-P05`, predict a different omitted-bound or empty-range case. For production workload comparisons, `PY-BLT-090` owns the broader complexity discussion. A future measurement should state whether it concerns shallow bytes, reachable bytes, allocations, or time before choosing tools.

## 14. Authoritative sources

Read 2026-08-30:

1. [Python 3.14 slice objects](https://docs.python.org/3.14/reference/datamodel.html#slice.indices): normalization contract.
2. [Python 3.14 ranges](https://docs.python.org/3.14/library/stdtypes.html#ranges): representation, indexing, slicing, membership, equality, and length limitations.
3. [Python 3.14 `sys.getsizeof`](https://docs.python.org/3.14/library/sys.html#sys.getsizeof): shallow measurement boundaries.
