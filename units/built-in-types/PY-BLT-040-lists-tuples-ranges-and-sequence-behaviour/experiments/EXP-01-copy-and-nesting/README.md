# EXP-01 — Copies, nested references, and a partial mutation

| Field | Value |
|---|---|
| Owning unit | [PY-BLT-040](../../README.md) |
| Curriculum | [CURRICULUM.md](../../../../../CURRICULUM.md#py-blt-040) |
| Topic branch | `topic/PY-BLT-040` |
| Precise question | Which references remain shared after a shallow copy, tuple conversion, deep copy, or repetition, and can a later failed store undo a child mutation? |
| Classification | Language guarantees, built-in contracts, and standard-library copying behavior |
| Status | Reproduced |
| Risk | None; bounded synthetic objects and stdout only |

## 1. Why an experiment is necessary

Equal-looking nested containers conceal whether their children are shared. The probe compares identity directly and separates child mutation from outer-slot replacement. A final two-stage operation shows why observing an exception does not prove that nothing changed.

## 2. Hypothesis

Author prediction during probe design, not a learner answer:

> Shallow copying and tuple conversion retain the original child references. Deep copying detaches that child from the source but preserves the repeated-reference relationship inside the copied graph. Repetition shares a child. List in-place addition can succeed before a tuple slot rejects its assignment.

Alternative outcome: each visible occurrence might become an independent child, or the final error might restore the child's old state. The identity checks and post-error output discriminate between these possibilities.

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

This is not a benchmark. No timing, allocation-count, concurrency, or free-threaded claim is made.

## 4. Controls and variables

### Controlled

Use one synthetic child list and two source slots pointing to it. Keep operation order and payloads identical across runtimes. Compare identity with `is`; do not interpret addresses.

### Changed

Change the outer construction method, then distinguish mutating a child from replacing an outer slot. A separate tuple case changes the permitted store target.

### Measured

Record outer/child identity relationships, resulting values, exception class, and the child state after catching the exception.

## 5. Files

- [copy_probe.py](copy_probe.py): executable probe.
- [Unit tests](../../tests/test_examples.py): separate regression checks for the relevant boundaries.

## 6. Reproduction command

From the repository root, with `python` selecting the intended runtime:

```bash
python -B units/built-in-types/PY-BLT-040-lists-tuples-ranges-and-sequence-behaviour/experiments/EXP-01-copy-and-nesting/copy_probe.py
```

The command was run with `python` selecting CPython 3.14.7, then CPython 3.11.16. Each selected interpreter's version was checked before execution. Use the environment details above to compare a reproduction; installation paths are not part of the experiment.

## 7. Prediction

The shallow outer identity will differ; its child identity and the tuple's child identity will match the source. The copied deep child will differ from the source but match its sibling inside the deep copy. Source-child mutation will reach the shallow and tuple containers, not the deep copy. Replacing a shallow slot will not replace the source slot. The final tuple assignment will raise `TypeError` after its child contains `7`.

## 8. Observed output

Both CPython 3.14.7 and 3.11.16 produced this complete, identical stdout:

```text
shallow outer is source: False
shallow child is source child: True
tuple child is source child: True
deep child is source child: False
deep children share with each other: True
source after child mutation: [['queued', 'sent'], ['queued', 'sent']]
shallow after child mutation: [['queued', 'sent'], ['queued', 'sent']]
tuple after child mutation: (['queued', 'sent'], ['queued', 'sent'])
deep after child mutation: [['queued'], ['queued']]
source after shallow slot replacement: [['queued', 'sent'], ['queued', 'sent']]
shallow after slot replacement: [['local'], ['queued', 'sent']]
repeated children share: True
repeated after mutation: [[0, 1], [0, 1]]
tuple augmented assignment: TypeError
tuple child after failed assignment: [7]
```

## 9. Interpretation

The identity checks directly establish the sharing relationships for this graph. The mutation output shows their consequences. `deepcopy` preserved the graph's repeated-reference structure while detaching the mutable child from its source. Its memoization contract explains that result; it does not mean all object types are copied the same way.

The tuple failure happened at the final slot store after list mutation. It is evidence about this operation's sequence, not a universal rule that failed statements mutate inputs or that errors provide rollback.

## 10. Visual interpretation

```text
before source mutation:
source slots 0,1 ──> child X ["queued"] <── shallow slots 0,1
                          ^
                          └──────────────── tuple slots 0,1

deep slots 0,1 ────> child Y ["queued"]       Y is not X

after shallow[0] replacement:
shallow slot 0 ────> child Z ["local"]
shallow slot 1 ────> X                       source still reaches X twice
```

### How to read this visual

Each arrow names the object reached by a slot. Repeated source slots share X; repeated deep slots share a different Y. Only one shallow slot is redirected later.

### Key insight

Independent outer structure and independent children are separate properties. A deep copy can preserve sharing inside its new graph.

### Simplification or limitation

This is a logical reference graph for ordinary lists and tuples. It omits immutable leaves, cycles, custom copy hooks, object layouts, and allocator behavior.

## 11. Language and implementation conclusion

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| Outer shallow copies retain child references | Standard-library / built-in contract | Observed on CPython 3.14.7 and 3.11.16 | Do not generalize to arbitrary custom slicing |
| Deep copy preserves repeated references in this copied graph | Standard-library copying contract | Same observed versions | Custom copying behavior can differ |
| Tuple conversion leaves mutable descendants reachable | Language object model | Same observed versions | Fixed slots do not imply frozen descendants |
| Failed tuple slot store leaves earlier list mutation | Language evaluation plus built-in behavior | Same observed versions | Classify the exact operation, not all exceptions |

## 12. Limitations and threats to validity

- Matching outputs on two CPython versions do not test other interpreters.
- No custom `__copy__`, `__deepcopy__`, `__iadd__`, or resource-owning object appears here.
- Deep copy of cycles, recursion limits, performance, and concurrent mutation are outside this probe.
- The test runner's success is author verification, not learner explanation or practice evidence.

## 13. Follow-up

Use `PY-BLT-040-P05` to predict one changed sharing relationship before execution. Revisit `PY-FND-020` for references and `PY-FND-040` for evaluation order. A useful later experiment adds a cycle and checks its copied relationship rather than printing a memory address.

## 14. Authoritative sources

Read 2026-08-30:

1. [Python 3.14 `copy`](https://docs.python.org/3.14/library/copy.html): shallow/deep copying and memoization.
2. [Python 3.14 object model](https://docs.python.org/3.14/reference/datamodel.html#objects-values-and-types): references and immutability.
3. [Python 3.14 augmented assignment](https://docs.python.org/3.14/reference/simple_stmts.html#augmented-assignment-statements): lookup, operation, and store.
