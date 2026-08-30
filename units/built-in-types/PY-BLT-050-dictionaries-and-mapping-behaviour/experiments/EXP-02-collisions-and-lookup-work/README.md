# EXP-02 — Collisions and lookup work

| Field | Value |
|---|---|
| Owning unit | [PY-BLT-050](../../README.md) |
| Curriculum | [CURRICULUM.md](../../../../../CURRICULUM.md#py-blt-050) |
| Topic branch | `topic/PY-BLT-050` |
| Precise question | Do unequal keys with identical hashes overwrite entries, or require more equality work? |
| Classification | Language correctness; CPython-specific comparison counts |
| Status | Interpreted |
| Risk | None; at most 128 synthetic keys per mapping |

## 1. Why an experiment is necessary

“Hash tables are fast” hides both the key-equivalence rule and the cost of collisions. This probe exposes Python-level equality calls while keeping successful lookup results visible. It is an instrumented operation count, not a timing benchmark.

## 2. Hypothesis

Before execution: distinct labels remain separate entries under a constant hash. Compared with distinct hashes, missing-key and late-key lookups should invoke more equality comparisons under deliberate collisions. A fresh key equal to an existing one should replace that key's value without adding another entry.

Alternative outcome: if the hash alone determined identity, constant-hash keys would collapse into one entry. If hash distribution did not affect candidate comparisons, equality counts would not increase.

## 3. Environment

Author runs on **2026-08-30**, using **CPython 3.14.7** and **CPython 3.11.16**, on Linux `7.0.0-30-generic`, x86_64, 64-bit pointers, conventional non-debug GIL builds. The full `sys.version`, build, implementation/cache tags, flags, and environment are recorded in [EXP-01's environment](../EXP-01-live-views-and-shallow-copies/README.md#3-environment); these probes ran in the same verification session with the same settings.

Dependencies: standard-library `dataclasses` and `typing`. `PYTHONHASHSEED` was unset; `-B` was used. The custom hashes do not depend on randomized string hashes. CPU model, power mode, warm-up, and timing uncertainty are not reported because no elapsed-time measurements were made.

## 4. Controls and variables

### Controlled

Frozen integer-labelled keys; identical equality rules; increasing insertion order; a fresh equal key for each hit; a missing label outside the input range; no writers during lookup. The class-wide counter is reset after construction and before each lookup, excluding construction comparisons.

### Changed

Input size: 8, 32, 128. Hash policy: each key's integer label, or constant zero. The mode flag participates in equality, so equal objects always have compatible hashes.

### Measured

Mapping length, hit value, missing-key membership result, and calls to `ProbeKey.__eq__`. This does not count hashing, every internal slot probe, allocation, or processor time.

## 5. Files

- [probe_collisions.py](probe_collisions.py): key type, reset points, and lookups.
- This note: predictions, complete observations, and limits.

## 6. Reproduction command

From the repository root, with both runtimes installed:

```bash
uv run --offline --no-project --python 3.14.7 python -B units/built-in-types/PY-BLT-050-dictionaries-and-mapping-behaviour/experiments/EXP-02-collisions-and-lookup-work/probe_collisions.py
uv run --offline --no-project --python 3.11.16 python -B units/built-in-types/PY-BLT-050-dictionaries-and-mapping-behaviour/experiments/EXP-02-collisions-and-lookup-work/probe_collisions.py
```

The author used a writable temporary `UV_CACHE_DIR`. The script itself is standard-library-only and can be run directly with the selected Python executable.

## 7. Prediction

All mappings retain their input size. Each miss is false and each hit returns the final label. Constant hashes cause more equality work. Exact counts are to be observed, not assumed from a universal Python contract.

## 8. Observed output

Complete actual stdout, identical on both tested builds. Both commands exited with code 0.

```text
n=8 hashes=distinct len=8 missing_found=False miss_eq=0 hit=7 hit_eq=1
n=8 hashes=constant len=8 missing_found=False miss_eq=8 hit=7 hit_eq=8
n=32 hashes=distinct len=32 missing_found=False miss_eq=0 hit=31 hit_eq=1
n=32 hashes=constant len=32 missing_found=False miss_eq=32 hit=31 hit_eq=32
n=128 hashes=distinct len=128 missing_found=False miss_eq=0 hit=127 hit_eq=1
n=128 hashes=constant len=128 missing_found=False miss_eq=128 hit=127 hit_eq=128
equal-key replacement: 2 replacement
unequal colliding key survives: second
```

## 9. Interpretation

1. Collisions did not discard unequal keys. Equality, not a hash alone, distinguished them.
2. Constant hashes produced increasing equality work in this controlled workload. A correct answer can still require substantial lookup work.
3. A missing-key lookup with zero equality calls still performed hashing and table work. The instrument did not count those operations.
4. Fresh equal-key replacement left the mapping length at two; the unequal colliding key remained accessible.
5. The exact `n`-comparison pattern belongs to these inputs and builds. It is neither a language guarantee nor a measured latency ratio.

## 11. Language and implementation conclusion

| Conclusion | Classification | Version checked | Portability note |
|---|---|---|---|
| Unequal hash-colliding keys remain distinct | Language key contract | 3.14.7 and 3.11.16 | Assumes valid stable hash/equality methods |
| Equal keys address one entry | Language key contract | Both | Hash/equality consistency is essential |
| These lookups made the recorded equality calls | CPython observation | Both exact builds | Other inputs, versions, or implementations may use different counts |

## 12. Limitations and threats to validity

- Deliberate constant hashing is an adversarial distribution, not a representative string-key workload.
- The Python counter changes execution cost; no timing inference is justified.
- Only ordinary fresh-key hits and misses were measured. Identity shortcuts and other key classes are separate cases.
- Three input sizes illustrate a mechanism, not a statistical performance study.
- No alternative interpreter, free-threaded runtime, memory sizing, or multithreaded behaviour was tested.

## 13. Follow-up

[PY-BLT-050-P05](../../practice/README.md#py-blt-050-p05) asks for a new prediction about key identity and an unrecorded size. Designing production key types belongs to [PY-BLT-080](../../../../../CURRICULUM.md#py-blt-080); full asymptotic analysis belongs to [PY-MPR-070](../../../../../CURRICULUM.md#py-mpr-070).

## 14. Authoritative sources

Read on 2026-08-30: [Data model — `__hash__`](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__), [CPython v3.14.7 `dictobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictobject.c) (`compare_generic` and `do_lookup`), and [dictionary design notes](https://github.com/python/cpython/blob/v3.14.7/Objects/dictnotes.txt).
