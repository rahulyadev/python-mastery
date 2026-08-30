# EXP-02 — Hash seeds and collisions

| Field | Value |
|---|---|
| Owning unit | [PY-BLT-060](../../README.md) |
| Curriculum | [CURRICULUM.md](../../../../../CURRICULUM.md#py-blt-060) |
| Topic branch | `topic/PY-BLT-060` |
| Precise question | Can hash behaviour change iteration or lookup work without changing membership? |
| Classification | CPython / runtime configuration; membership contract distinguished below |
| Status | Reproduced |
| Risk | Process; three small local child processes with a 10-second timeout each |

## 1. Why an experiment is necessary

An observed iteration sequence can look like an ordering promise. A successful lookup can hide many collision comparisons. Two controlled probes expose these observations without treating either as a language guarantee.

## 2. Hypothesis

Before execution: the same string members may be visited in different orders with different process hash seeds. Both key classes should retain all 64 unequal members, but a deliberately colliding class should require more equality calls for one missing-key lookup.

Alternative: these particular seeds might happen to produce the same order. That would not establish an ordering guarantee. Small inputs or different probing strategies could also change the comparison count.

## 3. Environment

```text
Date: 2026-08-30
Operating system: Linux-7.0.0-30-generic-x86_64-with-glibc2.43
Architecture: x86_64
CPU: Intel(R) Core(TM) i7-14700HX
Implementation: cpython
Canonical sys.version: 3.14.7 (main, Aug 25 2026, 14:02:56) [Clang 22.1.3 ]
Compatibility sys.version: 3.11.16 (main, Aug 25 2026, 14:00:53) [Clang 22.1.3 ]
Build type: release; Py_DEBUG=0 on both
Free-threaded build: no; Py_GIL_DISABLED=0 on 3.14.7, unavailable on 3.11.16
Dependencies: Python standard library only
Flags: parent and children use -B; optimization level 0
Relevant environment: parent PYTHONHASHSEED unset; child seeds 1, 1, 2
Timing: not measured; this is not a benchmark
```

## 4. Controls and variables

- Order probe: fixed input string list and executable; vary `PYTHONHASHSEED` before child-process startup. Repeat seed 1 once as a control. Collect both iteration order and sorted membership.
- Collision probe: fixed insertion sequence of values 0 through 63 and missing query -1; vary only the key class's hash distribution. Reset the equality counter **after construction**.
- Each key class compares only with its own class, so the two classes do not introduce an equal-object/different-hash contract violation. Key fields are not mutated.

`PYTHONHASHSEED` must be set before the child starts; assigning it inside an already-running interpreter would not recreate that interpreter's hash initialization. See [the environment-variable contract](https://docs.python.org/3.14/using/cmdline.html#envvar-PYTHONHASHSEED).

## 5. Files

[probe_hashing.py](probe_hashing.py) contains both bounded probes. It emits only synthetic member names, boolean observations, and counts; it does not print inherited environment contents.

## 6. Reproduction command

From the repository root, select either recorded runtime as `python`, then run:

```bash
python -B units/built-in-types/PY-BLT-060-sets-and-frozensets/experiments/EXP-02-hash-seeds-and-collisions/probe_hashing.py
```

Recorded executions selected the installed CPython 3.14.7 executable explicitly and `python3.11` for CPython 3.11.16. Children use `sys.executable`, so they follow the selected parent interpreter. The unit's exact transcript audit is intentionally limited to the recorded runtime versions.

## 7. Prediction

Sorted membership should agree, repeated seed 1 should reproduce this build's order, and both custom-key sets should store 64 members while rejecting the missing value. The colliding class should use more equality callbacks; no exact count was required by the hypothesis.

## 8. Observed output

Both recorded runtimes produced this exact stdout:

Recorded stdout:

```text
seed 1 iteration: ['echo', 'charlie', 'foxtrot', 'bravo', 'delta', 'alpha']
seed 1 repeated matches: True
seed 2 iteration: ['alpha', 'bravo', 'echo', 'delta', 'foxtrot', 'charlie']
sorted members match: True
different iteration observed: True
SpreadKey: stored=64, missing_present=False, eq_calls=0
CollidingKey: stored=64, missing_present=False, eq_calls=89
```

## 9. Interpretation

1. Changing the seed changed traversal order for these inputs on these builds, without changing the represented members. That supports treating display order separately from membership.
2. The colliding objects remain distinct because their equality distinguishes them. A matching hash is not a unique object identifier.
3. The counted miss needed 89 equality callbacks for 64 colliding members. Probing may revisit candidates; the counter is not the number of stored objects or the total number of table-slot probes. Zero equality callbacks for the spread-out case does not mean zero lookup work.

## 11. Language and implementation conclusion

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| Unequal colliding members can coexist | Set/hash contract | Tested 3.14.7 and 3.11.16 | Requires valid, stable equality and hashing |
| The displayed orders differed under seeds 1 and 2 | Observed runtime behaviour | These CPython x86_64 builds | Not a guarantee for other inputs, histories, versions, or architectures |
| This missing lookup used 89 equality calls | CPython observation | These two tested builds | Not a fixed complexity constant or cross-build contract |

The pinned [CPython set implementation](https://github.com/python/cpython/blob/v3.14.7/Objects/setobject.c), particularly `set_lookkey`, explains the distinction between hashing, probing, identity checks, and equality callbacks. The language contract does not specify that probing sequence.

## 12. Limitations and threats to validity

- Two seed values and one input size do not characterize all possible set histories.
- Integer-based custom hash functions here are deliberately artificial. Fixed string hash seeds do not make arbitrary application hashes stable.
- A comparison counter observes only `__eq__`, not cached hashes, identity shortcuts, empty slots, memory accesses, or elapsed time.
- The exact transcript is a reproducibility record for this environment, not a portable assertion. Semantic tests avoid exact order/count expectations.
- No benchmark speedup, collision probability, memory saving, free-threaded behaviour, or alternative-interpreter result is claimed.
- Author execution does not advance learner progress.

## 13. Follow-up

After making a prediction, vary the number of custom keys and explain the resulting comparison counts. Keep this bounded; a deliberately colliding large workload can become expensive. Broader container trade-offs belong to [PY-BLT-090](../../../../../CURRICULUM.md#py-blt-090).

## 14. Authoritative sources

Accessed 2026-08-30:

1. [Python 3.14 — `PYTHONHASHSEED`](https://docs.python.org/3.14/using/cmdline.html#envvar-PYTHONHASHSEED), process initialization control.
2. [Python 3.14 — Data model, `__hash__`](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__), equality/hash contract and unordered set iteration.
3. [CPython v3.14.7 — `Objects/setobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/setobject.c), lookup/probing mechanism.
