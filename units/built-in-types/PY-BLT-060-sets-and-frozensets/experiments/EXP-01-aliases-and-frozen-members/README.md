# EXP-01 — Aliases and frozen members

| Field | Value |
|---|---|
| Owning unit | [PY-BLT-060](../../README.md) |
| Curriculum | [CURRICULUM.md](../../../../../CURRICULUM.md#py-blt-060) |
| Topic branch | `topic/PY-BLT-060` |
| Precise question | Which state stays fixed after copying or freezing a set? |
| Classification | Language / Standard-library contract |
| Status | Reproduced |
| Risk | None; small in-memory synthetic objects only |

## 1. Why an experiment is necessary

A printed group alone hides whether two names share the same container and whether a frozen container still refers to a mutable object. Observe those boundaries separately.

## 2. Hypothesis

Before execution: mutating `source` will be visible through `alias`, but will not add members to a prior copy or frozenset. Rebinding `source` will leave `alias` behind. Updating an identity-hashed member's non-key attribute will remain observable through a frozenset.

Alternative: if freezing were recursive, the member's state change would be rejected or invisible through the frozen group.

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
Flags: -B; optimization level 0
Dependencies: Python standard library only
Relevant environment: PYTHONHASHSEED unset; string members sorted for display
```

## 4. Controls and variables

- Controlled: initial `{"api"}` membership, the sequence of operations, one process, no concurrent writers.
- Changed: in-place insertion, name rebinding, augmented assignment to a frozenset name, and a member attribute.
- Measured: membership displays, identity comparisons, and the observed member status.

## 5. Files

[probe_aliases.py](probe_aliases.py) is the entire runnable experiment. `Job` deliberately inherits identity equality/hashing; its `status` is not an equality or hash field.

## 6. Reproduction command

From the repository root, select either recorded runtime as `python`, then run:

```bash
python -B units/built-in-types/PY-BLT-060-sets-and-frozensets/experiments/EXP-01-aliases-and-frozen-members/probe_aliases.py
```

Recorded executions used the installed CPython 3.14.7 executable explicitly and `python3.11` for CPython 3.11.16; do not assume the machine's default `python` has the canonical patch version. The unit tests reproduce the exact command using `sys.executable` for each selected runtime.

## 7. Prediction

The alias should share the insertion, the copied and frozen memberships should stay at `api`, rebinding should break name identity, and the mutable member should be observed as `done` without changing the frozenset's membership.

## 8. Observed output

Both recorded runtimes produced this exact stdout:

Recorded stdout:

```text
after add: source=['api', 'worker'], alias=['api', 'worker']
snapshots: copied=['api'], frozen=['api']
source is alias: True
after rebind: source=['api', 'cron', 'worker'], alias=['api', 'worker']
source is alias: False
frozen |=: current=['api', 'batch'], previous=['api']
same frozen object: False
member status: done
member still present: True
```

## 9. Interpretation

1. The first insertion reaches both names referring to the original set. Neither previously constructed snapshot gains the new string member.
2. The union assigned to `source` changes its binding, not `alias`'s binding. Augmented union on the frozenset similarly leaves the previous frozen object unchanged.
3. The member attribute changes because the frozenset stores a reference to the same `Job`. This does not violate hashing: `Job` uses identity, not status, for equality and hashing.

## 10. Visual interpretation

```text
jobs (frozenset) ---> Job object
fixed membership     status: queued -> done
```

### How to read this visual

The arrow is a member reference. The right-hand object's attribute changes; the left-hand collection of member references does not.

### Key insight

Frozen membership is not recursive object freezing.

### Simplification or limitation

This conceptual reference diagram omits hash slots and allocation. It applies to the deliberately identity-hashed member used here, not to permission to mutate value-based key fields.

## 11. Language and implementation conclusion

| Conclusion | Classification | Tested versions | Portability note |
|---|---|---|---|
| Assignment and mutation have different alias effects | Language | 3.14.7, 3.11.16 | Does not depend on memory addresses |
| A frozenset fixes membership without freezing member attributes | Standard-library / object model | 3.14.7, 3.11.16 | Members must still obey their hash/equality contract |
| A changed frozenset value can be rebound with `\|=` | Language / Standard library | 3.14.7, 3.11.16 | The previous object's membership is unchanged |

## 12. Limitations and threats to validity

- No concurrency, recursive copying, custom value-based equality, or failing hash callback was tested.
- The display sorts strings; it says nothing about set traversal order.
- No timing, allocation, free-threaded, or alternative-interpreter claims follow.
- This is author-prepared evidence, not a learner prediction or completed exercise.

## 13. Follow-up

Reconstruct the alias graph before running the probe yourself. For designing stable value-based keys, continue with [PY-BLT-080](../../../../../CURRICULUM.md#py-blt-080).

## 14. Authoritative sources

Accessed 2026-08-30:

1. [Python 3.14 — Set Types](https://docs.python.org/3.14/library/stdtypes.html#set-types-set-frozenset), mutability and shallow copies.
2. [Python 3.14 — Data model](https://docs.python.org/3.14/reference/datamodel.html#objects-values-and-types), container references and mutability.
3. [Python 3.14 — `__hash__`](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__), default object behaviour and the hash contract.
