# EXP-01 — Live views and shallow copies

| Field | Value |
|---|---|
| Owning unit | [PY-BLT-050](../../README.md) |
| Curriculum | [CURRICULUM.md](../../../../../CURRICULUM.md#py-blt-050) |
| Topic branch | `topic/PY-BLT-050` |
| Precise question | Which observations remain live, and which child references survive a shallow snapshot? |
| Classification | Language / Standard library; iterator error observed on CPython |
| Status | Interpreted |
| Risk | None; small in-memory synthetic values |

## 1. Why an experiment is necessary

A tuple of items can appear frozen while still containing a reference to an editable list. The probe separates structural changes, child mutation, rebinding, read-only access, and a paused iterator. These are author observations, not a learner's completed prediction exercise.

## 2. Hypothesis

Before execution: views and the proxy will reflect new bindings; a saved key tuple will not. The shallow copy and materialized item tuples will retain the original list. Rebinding the source entry will leave those retained references alone.

Alternative outcome: if a snapshot recursively isolated children, an edit to the original list would not appear through it. This would contradict the proposed shallow-copy model.

## 3. Environment

Recorded on **2026-08-30**, with standard-library-only scripts.

| Field | Canonical run | Compatibility run |
|---|---|---|
| Implementation | CPython | CPython |
| Python version | 3.14.7 | 3.11.16 |
| `sys.version` | `3.14.7 (main, Aug 25 2026, 14:02:56) [Clang 22.1.3 ]` | `3.11.16 (main, Aug 25 2026, 14:00:53) [Clang 22.1.3 ]` |
| `sys.implementation` name / cache tag | `cpython` / `cpython-314` | `cpython` / `cpython-311` |
| Operating system / kernel | Linux / `7.0.0-30-generic` | Same host |
| Architecture / pointer size | x86_64 / 64 bits | Same host |
| Build type | Non-debug; `Py_DEBUG=0` | Non-debug; `Py_DEBUG=0` |
| Free-threaded build | No; `Py_GIL_DISABLED=0`; GIL enabled | Conventional GIL build; that config variable is absent |
| Relevant flags | `-B`, optimization level 0, hash randomization enabled | Same |
| Relevant environment | `PYTHONHASHSEED` unset | Same |
| Dependencies | Standard library | Standard library |
| CPU / timings | CPU model not sampled; no timing measurements | Same |

The exact interpreter builds were selected explicitly. The portable reproduction commands below use `uv` to select those installed versions; a writable temporary `UV_CACHE_DIR` was used by the author. This tool-cache location has no role in the Python observations.

## 4. Controls and variables

### Controlled

Same input, operation order, one process, no concurrent writers, no custom key methods, and no memory-address output.

### Changed

Add a key, edit the shared list, replace the source's list binding, attempt proxy assignment, then add a key while an iterator is paused.

### Measured

Ordered values, retained membership, identity comparisons, and exception class names. No allocation sizes or elapsed times are measured.

## 5. Files

- [probe_views.py](probe_views.py): complete runnable probe.
- This note: environment, captured stdout, and interpretation.

## 6. Reproduction command

From the repository root, with the two runtimes installed:

```bash
uv run --offline --no-project --python 3.14.7 python -B units/built-in-types/PY-BLT-050-dictionaries-and-mapping-behaviour/experiments/EXP-01-live-views-and-shallow-copies/probe_views.py
uv run --offline --no-project --python 3.11.16 python -B units/built-in-types/PY-BLT-050-dictionaries-and-mapping-behaviour/experiments/EXP-01-live-views-and-shallow-copies/probe_views.py
```

Using either explicitly selected interpreter directly gives the same probe. `uv` is a reproduction convenience, not a runtime dependency of the script.

## 7. Prediction

The live key view gains `region`; the saved key tuple does not. Editing list A appears through the item snapshot and copy. Rebinding the source to a new list affects the live items and proxy only. Proxy assignment should fail. On these CPython builds, the added entry should invalidate the paused iterator.

## 8. Observed output

Actual complete stdout was identical on both tested runtimes; each process exited with code 0. Exception class lines were printed by the probe's handlers.

```text
live keys: ['tags', 'timeout', 'region']
key snapshot: ('tags', 'timeout')
snapshot items after child edit: (('tags', ['base', 'canary']), ('timeout', 10))
copy after child edit: {'tags': ['base', 'canary'], 'timeout': 10}
same child: True
live items after rebinding: [('tags', ['replacement']), ('timeout', 10), ('region', 'west')]
copy after rebinding: {'tags': ['base', 'canary'], 'timeout': 10}
proxy follows rebinding: True
proxy assignment: TypeError
iterator first: tags
iterator after insertion: RuntimeError
```

## 9. Interpretation

1. Adding a binding separates the live view from the key snapshot and copied dict.
2. The immutable pair tuples still contain a reference to the editable list. An immutable outer structure does not imply an immutable object graph.
3. After rebinding, the source/proxy reaches the replacement while the copy reaches the original list.
4. The proxy restricts assignment through one access path. It does not freeze the source.
5. One observed iterator error does not establish that all structural mutations are detected, including delete-then-add cases with unchanged size.

## 11. Language and implementation conclusion

| Conclusion | Classification | Version checked | Portability note |
|---|---|---|---|
| Views are live | Built-in contract | 3.14.7 and 3.11.16 | Re-observation reflects the original dictionary |
| A dict copy retains child references | Language / copy contract | Both | Does not recursively copy values |
| The proxy rejects its own writes and tracks source writes | Standard library | Both | No deep immutability guarantee |
| This insertion causes the paused iterator to raise | CPython observation within documented unsafe mutation | Both | Do not promise detection for every mutation pattern |

## 12. Limitations and threats to validity

- Single-threaded built-in dict/list objects only; no custom copy protocol or external writers.
- Actual identity tests avoid addresses, but do not reveal allocation layout.
- Neither snapshots nor proxies were tested as synchronization mechanisms.
- No alternative interpreter or free-threaded build was tested.

## 13. Follow-up

Reconstruct the [ownership visual](../../README.md#51-shallow-copy-separates-bindings-not-all-objects) before replaying the explorer. A future learner run should preserve its own prediction and interpretation. Related units: [PY-FND-020](../../../../../CURRICULUM.md#py-fnd-020) and [PY-BLT-080](../../../../../CURRICULUM.md#py-blt-080).

## 14. Authoritative sources

Read on 2026-08-30: [dictionary views](https://docs.python.org/3.14/library/stdtypes.html#dict-views), [`copy`](https://docs.python.org/3.14/library/copy.html), and [`MappingProxyType`](https://docs.python.org/3.14/library/types.html#types.MappingProxyType).
