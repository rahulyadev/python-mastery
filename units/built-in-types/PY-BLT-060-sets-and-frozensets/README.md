# PY-BLT-060 — Sets and frozensets

[Curriculum entry](../../../CURRICULUM.md#py-blt-060) · [Progress](../../../PROGRESS.md) · Topic branch: `topic/PY-BLT-060`

## Physical Notebook Core

### Problem this concept solves

Ask whether something exists, remove repeats, or compare groups without confusing membership with position or frequency.

### One-sentence mental model

> A set keeps distinct hashable members; a frozenset fixes that membership so the group itself can be a key.

### One important visual

```text
A = {api, cache, worker}       B = {cache, cron}

         A only          Both          B only
       api, worker       cache          cron

A | B    keep             keep          keep
A & B    omit             keep          omit
A - B    keep             omit          omit
A ^ B    keep             omit          keep
```

#### How to read this visual

Partition members into three columns, then read the selected operation across the row. Names are schematic strings.

#### Key insight

Intersection keeps the overlap; symmetric difference removes it. Difference has a direction.

#### Simplification or limitation

This is membership algebra, not iteration order, proportional areas, or physical memory layout.

### Governing rules or invariants

1. Members must be hashable; equal members must have equal hashes. A collision alone is not equality.
2. Neither set type promises insertion order or supports indexing. Deduplication also loses counts.
3. `set` is mutable and unhashable; `frozenset` is immutable and hashable. Freezing membership does not recursively freeze objects.

### Minimal example

Runnable check: core.

```python
current = {"api", "cache", "worker"}
desired = {"cache", "cron"}
print(sorted(desired - current))
print(sorted(current - desired))
```

Expected reasoning: the first difference identifies additions; the second identifies removals. Sorting is an explicit presentation decision. Observed on both tested runtimes: `['cron']`, then `['api', 'worker']`.

### One failure or misconception

**Mistake:** `list(set(events))` preserves the first arrival of each event.

**Correction:** a set retains membership, not arrival order. Decide which information the output must preserve before selecting a container.

### Important trade-offs

- Efficient repeated membership checks usually justify a hash index; one small scan may not.
- A frozenset suits an unordered group key, not a sequence or a frequency table.

### Interview-revision cues

- Membership, order, count: which matters?
- Same hash versus equal object: what follows from each?
- Mutation versus rebinding: what does another alias observe?

## Unit metadata

| Field | Value |
|---|---|
| Domain | Built-in types, operations, and functions |
| Canonical ID | `PY-BLT-060` |
| Learning outcome | Use sets and frozen sets; reason about membership, algebra, deduplication, and hash-based behaviour |
| Hard prerequisites | `PY-FND-020`, `PY-FND-050` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | Medium |
| Depth | D2 |
| Scope | Language, Standard library |
| Size | M |
| Evidence profile | E+C+D |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.7 and CPython 3.11.16; Linux x86_64, conventional GIL builds |
| Last source audit | 2026-08-30 |
| Artifact state | Approved |

## 1. Learning outcome and evidence

After this unit, reconstruct set algebra, select a representation that preserves the needed information, explain the member/key contract, and diagnose aliasing, ordering, and mutation errors.

Required learner evidence is explanation/reconstruction (E), an original implementation with tests (C), and debugging with correct reasoning (D). The two prepared experiments are optional supporting artifacts; they do not change the curriculum's `E+C+D` profile. Author-written examples, tests, and transcripts are **not learner attempts**. Learning remains **Not started** until the tracker rules are met.

### Reproduce artifact checks

Run from the repository root with the intended interpreter selected:

```bash
python scripts/validate_repo.py
python -B -m unittest discover -s units/built-in-types/PY-BLT-060-sets-and-frozensets/tests -v
python -B units/built-in-types/PY-BLT-060-sets-and-frozensets/examples/set_operations.py
python -B units/built-in-types/PY-BLT-060-sets-and-frozensets/examples/catalog_diff.py
python -B units/built-in-types/PY-BLT-060-sets-and-frozensets/experiments/EXP-01-aliases-and-frozen-members/probe_aliases.py
python -B units/built-in-types/PY-BLT-060-sets-and-frozensets/experiments/EXP-02-hash-seeds-and-collisions/probe_hashing.py
node units/built-in-types/PY-BLT-060-sets-and-frozensets/tests/test_visual.mjs
```

The tests execute four marked note snippets, check the explorer's embedded data against fresh Python computation, and audit the recorded experiment stdout on the two recorded runtime versions. Exact transcript checks are skipped on other runtime versions; they are not portable order or comparison-count assertions. Practice is intentionally excluded.

The Node.js check uses a minimal DOM stand-in to exercise all control-event paths and result labels. It does not launch a browser or verify CSS, responsive layout, or assistive-technology behaviour.

Browser preview was attempted on 2026-08-30, but the Browser security policy blocked the local-file URL. No browser layout check or screenshot is claimed. The static diagrams remain readable in this note, and the explorer's Python data and local JavaScript logic are independently testable.

### Artifact verification — 2026-08-30

Repository validation passed. **37 Python tests** passed with no skips on each of **CPython 3.14.7** and **CPython 3.11.16**. Both example scripts, both experiment probes, all four runnable note snippets, and the visual state generator ran successfully on both runtimes. The experiment transcripts and generated visual data matched fresh execution exactly.

**27 local JavaScript checks** passed on Node.js **24.19.0**, covering initialization plus the 25 scenario/operation combinations. These use the documented DOM stand-in, not a browser. Ruff **0.16.1** lint and formatting checks and Git whitespace checks passed.

The template content, source audit, runnable checks, and protected practice support **Approved** canonical artifact state, with browser layout verification explicitly excluded above. The five exercises remain unattempted; no learner review date, learning-state advancement, or mastery claim was added.

## 2. Prerequisite bridge

Both prerequisites have approved notes but no recorded learning evidence at initialization.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | [PY-FND-020 — Objects, names, references, and mutability](../../../CURRICULUM.md#py-fnd-020) | Sets can be shared through several names | Assignment binds a name; mutating one object is different from rebinding one name |
| Hard | [PY-FND-050 — Truthiness, comparisons, equality, and identity](../../../CURRICULUM.md#py-fnd-050) | Deduplication depends on object equivalence | `is` checks identity, `==` checks equality, and an empty set is falsey |

Use the dedicated prerequisite tasks for deeper review. This bridge does not complete either unit. An ordinary custom object can retain identity-based hashing while some non-key attributes change; the experiment uses this deliberately, not a mutable value-based key.

## 3. Vocabulary and professional English

### Deduplicate

| Item | Content |
|---|---|
| Pronunciation | dee-DOO-pli-kayt |
| Simple English meaning | Remove repeated occurrences |
| Hindi cue | दोहराव हटाना |
| Python meaning | Retain one member per equivalence group, after defining what counts as equal |

1. Deduplicate the mailing list before sending invitations.
2. We deduplicated the imported records.
3. Deduplication should not hide conflicting information.
4. **Interview:** I would clarify whether deduplication must preserve input order.
5. **Engineering discussion:** These IDs are already normalized; deduplication is a separate step.

### Disjoint

| Item | Content |
|---|---|
| Pronunciation | dis-JOYNT |
| Simple English meaning | Having nothing in common |
| Hindi cue | कोई साझा सदस्य नहीं |
| Python meaning | Two sets have an empty intersection |

1. The teams work on disjoint responsibilities.
2. These two lists of attendees are disjoint.
3. We divided the work into disjoint groups.
4. **Interview:** Disjoint sets need not be ordered relative to each other.
5. **Engineering discussion:** The accepted and rejected ID groups must remain disjoint.

## 4. Deep explanation

### 4.1 Start with the information requirement

A list answers “what came next?”; a set answers “is this member present?” A dictionary associates a member with additional data. A frequency table is needed when repeated occurrences matter. Converting data into a set is therefore a modeling decision, not a universal cleanup step.

Construct an empty set with `set()`, not `{}`. A constructor consumes an iterable: `set("queue")` sees characters, whereas `{"queue"}` contains one string. Literal expressions are evaluated left to right, but that evaluation order does not become set iteration order. See [Set displays](https://docs.python.org/3.14/reference/expressions.html#set-displays). Comprehensions and starred forms belong to the next unit, [PY-BLT-070](../../../CURRICULUM.md#py-blt-070).

Runnable check: construction.

```python
letters = set("queue")
whole_name = {"queue"}
print(letters == {"q", "u", "e"}, len(whole_name))
```

Observed on both tested runtimes: `True 1`.

### 4.2 Hashability is a contract, not a synonym for immutability

A hashable object's hash remains stable, and equal hashable objects have equal hashes. Lists, dicts, and sets are unhashable. A tuple containing a list is also unhashable; wrapping something in a tuple does not repair its elements. See [Glossary — hashable](https://docs.python.org/3.14/glossary.html#term-hashable).

`1`, `True`, and `1.0` compare equal and have compatible hashes, so `len({1, True, 1.0})` is one. If a domain distinguishes flags from numeric IDs, validate or explicitly tag those categories before storing them. Conversely, two unequal objects may have the same hash and both remain members. Keep equality-relevant state stable while an object is stored. The full design of custom equality, ordering, and keys belongs to [PY-BLT-080](../../../CURRICULUM.md#py-blt-080); see also [Data model — `__hash__`](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__).

The normal model assumes well-behaved equality. Non-reflexive values such as NaN need separate reasoning; “unique” does not mean normalized, validated, or safe to use as a business identifier.

### 4.3 Algebra and comparison answer different questions

| Question | Expression | Example use |
|---|---|---|
| Present in either group? | `a \| b` | All known service names |
| Present in both? | `a & b` | Names shared by two catalogs |
| In the first but absent from the second? | `a - b` | Retired entries when `a` is old |
| Present in exactly one? | `a ^ b` | Membership changes in either direction |
| Is every member covered? | `a <= b` | Required capabilities are available |
| Covered, with something extra in `b`? | `a < b` | A proper subset |
| No shared member? | `a.isdisjoint(b)` | Nonoverlapping groups |

The algebra operations create results without mutating their operands. Named methods such as `intersection()` accept iterables, while the ordinary built-in set operators require set operands (`set` or `frozenset`). For example, `a.intersection(["cache"])` is valid; `a & ["cache"]` is not. Other objects can implement reflected operators, so this is not a claim about every possible overloaded expression. See the [set API contract](https://docs.python.org/3.14/library/stdtypes.html#set-types-set-frozenset).

`union`, `intersection`, and `difference` accept multiple iterable arguments; `symmetric_difference` takes one. An iterable may be consumed, and some operations can finish early. Do not use a set method merely to drive unrelated side effects in an iterator.

Runnable check: relations.

```python
a, b = {"api"}, {"cron"}
less = a < b
greater = a > b
print(less, a == b, greater)
print(set() <= a, set() < set())
```

Observed on both tested runtimes: `False False False`, then `True False`. Subset relationships form a **partial** order: some pairs are incomparable. `sorted(list_of_sets)` does not define a useful total ordering of sets. If a report needs an order, choose an explicit key. Sorting the members of one set of strings is a different operation.

### 4.4 Mutators need an absence policy and an ownership policy

| Operation | Member-level meaning | Return / absence behaviour |
|---|---|---|
| `s.add(x)` | Insert one member | `None`; an equivalent member need not be added again |
| `s.update(items)` | Insert members from an iterable | `None` |
| `s.remove(x)` | Delete a member that should exist | `None`; missing member raises `KeyError` |
| `s.discard(x)` | Ensure a member is absent | `None`; missing member is acceptable |
| `s.pop()` | Remove some member | Returns that member; empty set raises `KeyError` |
| `s.clear()` | Remove all members | `None` |

For intersection, difference, and symmetric difference, the corresponding `_update` method changes the receiver. `|=`, `&=`, `-=`, and `^=` mutate a built-in set; aliases observe that change. Pure `|`, `&`, `-`, and `^` leave the original set alone. These APIs are also present on the [Python 3.11 compatibility baseline](https://docs.python.org/3.11/library/stdtypes.html#set-types-set-frozenset).

`pop()` is arbitrary, not a randomness API, priority queue, or insertion-order operation. `discard` tolerates absence, not every possible error: an invalid unhashable argument can still fail. Do not change membership while traversing the same set. A set iterator is not a snapshot, and absence of an exception does not establish that a mutation pattern is safe.

### 4.5 Frozen groups and the boundary of freezing

A frozenset is useful when an unordered group is itself an identity. Both set types compare by membership; mixing them in ordinary binary algebra returns the left operand's type. `frozenset` has no membership-mutating methods, but `f |= other` is still valid: it computes a result and rebinds `f`. It does not mutate the previous object. See [the mixed-type and immutable-set contract](https://docs.python.org/3.14/library/stdtypes.html#set-types-set-frozenset).

Runnable check: frozen.

```python
left = frozenset(["json", "gzip"])
right = frozenset(["gzip", "json", "json"])
groups = {left, right}
print(len(groups), left == {"json", "gzip"})
```

Observed on both tested runtimes: `1 True`. That is desirable for capabilities, but wrong for a route whose order matters or a basket whose item counts matter.

`s.copy()` is shallow. `frozenset(s)` fixes the member collection, not the attributes of custom member objects. [EXP-01](experiments/EXP-01-aliases-and-frozen-members/README.md) separates these boundaries with a deliberately identity-hashed object.

### 4.6 Execution sequence: mutation versus rebinding

| Step | Statement | What an existing `alias = s` sees |
|---:|---|---|
| 1 | `s = {"api"}; alias = s` | The same set object |
| 2 | `s.add("worker")` | Both names see the added member |
| 3 | `s = s \| {"cron"}` | `alias` still refers to the old set |

#### How to read this visual

Read downward. The last column tracks the original alias, not the currently bound value of `s` alone.

#### Key insight

Changing a name's binding does not redirect other names.

#### Simplification or limitation

This is a single-threaded reference trace with string members, not an atomic snapshot protocol.

## 5. Additional visual models

### 5.1 Hash narrows the search; it does not prove equivalence

```text
candidate -> hash-based search -> relevant stored candidates
                                  | same object / equal member -> present
                                  | unequal collision          -> keep searching
                                  | search proves no match     -> absent
```

#### How to read this visual

Follow the candidate into the search, then distinguish a matching member from a merely colliding candidate.

#### Key insight

`hash(a) == hash(b)` does not imply `a == b`; collisions can add work without losing distinct members.

#### Simplification or limitation

This is conceptual. CPython v3.14.7 uses a probing table, stored hashes, identity/equality checks, and deleted-slot bookkeeping; see `set_lookkey` in [the pinned implementation](https://github.com/python/cpython/blob/v3.14.7/Objects/setobject.c). The diagram does not specify physical slots, all callbacks, error handling, or a fixed number of probes.

### 5.2 Interactive set-algebra explorer

Open [the offline explorer](visuals/set-explorer.html) in a browser. Its [Python state generator](visuals/trace_data.py) produces the embedded data checked by the tests.

#### How to read this visual

Choose a relationship and operation. Read the A-only, shared, and B-only regions; checked members survive. Try an empty input and equal inputs after the overlapping example.

#### Key insight

The operation changes the membership question without changing the inputs. Swapping the operands changes difference.

#### Simplification or limitation

This replays 25 Python-computed results for strings. It is not a Python interpreter, a hash-table animation, or evidence of iteration order. Display sorting is explicit; custom objects and mutation are outside its scope.

## 6. Worked examples

### 6.1 Operations with visible outcomes

Before running [set_operations.py](examples/set_operations.py), predict which result contains `cache`, which contains `cron`, and whether `add()` returns the modified set.

Observed on CPython 3.14.7 and 3.11.16:

```text
union: ['api', 'cache', 'cron', 'worker']
intersection: ['cache']
current_only: ['api', 'worker']
desired_only: ['cron']
symmetric_difference: ['api', 'cron', 'worker']
mutation: {'members': ['api', 'cache', 'worker'], 'same_object': True, 'add_return': None, 'update_return': None}
frozen key: ('compressed-json', True)
equal numeric members: 1
iterable method: ['cache']
```

### 6.2 Backend example: compare two service catalogs

[catalog_diff.py](examples/catalog_diff.py) returns immutable groups of added, removed, and unchanged names. It consumes each finite input once, rejects a bare string/bytes container, validates names, and does not mutate caller-owned containers. It deliberately keeps case significant and collapses repeats.

Observed on both tested runtimes:

```text
added: ['profile']
removed: ['search']
unchanged: ['billing']
```

This design fits a membership report. It does not apply infrastructure changes, preserve duplicate counts, decide a deployment order, or validate arbitrary catalog metadata. Use a mapping for per-service details and a sequence for an ordered plan. Iterator arguments are consumed: “no container mutation” is not “no observable effect.” Snapshot consistency under concurrent writers needs a separate design.

### 6.3 Debugging example — attempt before correction

[PY-BLT-060-P03](practice/README.md#py-blt-060-p03) contains a deliberately broken removal pass. Its solution, corrected code, and hints are withheld until an attempt.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| `{}` is an empty set | Braces also display sets | Empty braces are a dictionary | Check `type({})` |
| `add("api")` and `update("api")` match | Both seem to add data | One member versus iterable members | Compare the two resulting sets |
| Different types always stay distinct | Type identity is confused with equality | Equal numeric values collapse | Check `len({1, True, 1.0})` |
| All immutable containers are hashable | Outer mutability is checked alone | A tuple can contain an unhashable list | Try constructing `{([],)}` |
| A fixed hash seed guarantees ordered sets | One run is mistaken for a contract | No insertion-order guarantee exists | Reproduce EXP-02 |
| `<` compares cardinality or lexicographic order | Comparison syntax looks familiar | It asks for a proper subset | Compare two disjoint singleton sets |
| A frozenset recursively freezes its members | The name sounds deep | It freezes the container membership | Reproduce EXP-01 |
| A mutable set can be stored inside a set | Some membership tests accept it | Lookup/removal have a frozenset-equivalence convenience; insertion does not | See the focused boundary test |

The final row is a documented special case: lookup, `remove`, and `discard` can accept a set when searching for an equivalent frozenset. It does not make `set` hashable. This is tested separately from ordinary insertion.

## 8. Complexity and performance

For ordinary, reasonably dense CPython hash tables, assume well-distributed hashes and bounded-cost hashing/equality. Let `n = len(a)`, `m = len(b)`, and `k` be the number of values consumed from an iterable.

| Operation | Typical cost under these assumptions | Qualification |
|---|---|---|
| `x in a`, one insertion/removal | Expected O(1); insertion amortized | Collisions can make a lookup O(n); resizing adds occasional work |
| `set(iterable)` | Expected O(k), O(u) member storage | `u` is the number of distinct members; collisions can make construction quadratic |
| `a \| b`, `a ^ b` | Expected O(n + m) | Result allocation and input traversal matter |
| `a & b`, `a.isdisjoint(b)` | Expected O(min(n, m)) upper scan cost | Set operands; disjointness may finish early |
| `a - b` | Expected O(n) | Different from mutating `difference_update`; implementation chooses a strategy |
| `a.copy()` / traversal | Usually O(n) | A deletion-heavy table can retain capacity much larger than current membership |
| Sorted presentation | Typically O(n log n) comparisons | Requires comparable members or an explicit key; this is not the set lookup cost |

These are algorithmic estimates, not language-level performance guarantees or measured timings. They are inferred from the pinned CPython implementation's lookup, table traversal, intersection, and difference paths. Hashing a long new string or comparing expensive objects is additional work. [EXP-02](experiments/EXP-02-hash-seeds-and-collisions/README.md) counts equality calls, not time, memory, or all probes. Its exact count is not an API.

## 9. Production relevance and trade-offs

- **Define equivalence first.** Case folding, Unicode normalization, and domain IDs are separate from set construction. Decide whether information loss is acceptable.
- **Make presentation deterministic.** Sort supported values explicitly for logs or serialized output. Never persist `hash(frozenset(...))` as a unique or cross-process identity: collisions exist and some member hashes vary between processes. See [hash randomization](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__).
- **Avoid hidden shared mutation.** State ownership matters when passing a mutable set into a function. Accept read-only intent where useful and return a frozenset when callers should not modify membership.
- **Bound retained membership.** An ever-growing “seen IDs” set has ever-growing storage needs. A durable deduplication service also needs a retention and cross-worker consistency policy; this unit's in-memory examples do not implement one.
- **Protect compound decisions.** “Check absent, then add, then do work” is not one transaction. Do not infer a whole workflow's thread safety from container operations; see [Python's synchronization guidance](https://docs.python.org/3.14/howto/free-threading-python.html#thread-safety) and [PY-CON-030](../../../CURRICULUM.md#py-con-030).

## 10. Version and implementation boundaries

| Claim or feature | Classification | Version boundary | Python 3.11-compatible form | Notes |
|---|---|---|---|---|
| Construction, algebra, comparison, and mutator APIs used here | Language / Standard library | Present in both 3.11 and 3.14 | Same code | No 3.14-only feature is needed |
| `set[str]`, `frozenset[str]` annotations | Language / typing | Built-in generics since 3.9 | Same spelling | Annotations do not validate inputs; see [PEP 585](https://peps.python.org/pep-0585/) |
| Exact probing paths and equality counts | CPython implementation | Source pinned to v3.14.7 | Keep semantic expectations, not exact counts | Other versions and builds can differ |
| Fixed seed in a newly launched process | Runtime configuration | Tested on 3.11.16 and 3.14.7 | Same experiment command | It controls this experiment, not a portable set order |

The [3.11 set documentation](https://docs.python.org/3.11/library/stdtypes.html#set-types-set-frozenset) was checked alongside 3.14. The repository's Python pin is unchanged. The machine's unqualified `python` is CPython 3.14.4; canonical verification explicitly uses the installed CPython 3.14.7 interpreter. No free-threaded build or alternative interpreter was tested.

## 11. Practice brief

The [practice workspace](practice/README.md) starts unsolved. Do not use author-artifact tests as evidence of completing these exercises.

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-BLT-060-P01` | Predict / Explain | 2 | E+D: explain distinctions without executing first | [Prompt](practice/README.md#py-blt-060-p01) |
| `PY-BLT-060-P02` | Implement | 3 | C: preserve first-occurrence order while deduplicating | [Prompt](practice/README.md#py-blt-060-p02) |
| `PY-BLT-060-P03` | Debug | 3 | D+C: repair unsafe traversal while meeting ownership constraints | [Prompt](practice/README.md#py-blt-060-p03) |
| `PY-BLT-060-P04` | Implement / Design | 3 | C+E: group records by unordered capabilities | [Prompt](practice/README.md#py-blt-060-p04) |
| `PY-BLT-060-P05` | Review | 4 | E+D: review a cross-process cache-key proposal | [Prompt](practice/README.md#py-blt-060-p05) |

## 12. Interview prompts

Use these as a queue; ask only one and wait for the learner's reasoning before moving on.

1. When does converting a sequence into a set silently change the problem?
2. Why can a frozenset be a dictionary key while an ordinary set cannot?
3. Two sets have the same size but neither is less than, greater than, nor equal to the other. Explain a concrete case.
4. What assumptions justify expected constant-time membership, and what would a collision experiment actually measure?

A strong answer eventually separates the semantic contract, ownership boundary, and implementation assumptions. Do not provide a model answer before an attempt.

## 13. Closed-book revision cues

1. Reconstruct the three membership regions and four algebra rows.
2. Explain `add`, `update`, `remove`, `discard`, and `pop` without reading the table.
3. Draw what two aliases observe after mutation and after rebinding.
4. Explain what a frozenset freezes and what it does not.
5. Choose representations for ordered events, unique capabilities, and counted purchases.

## 14. Authoritative sources

Accessed 2026-08-30; explanations, examples, practice, and visuals are original.

1. [Python 3.14 — Built-in Types, Set Types](https://docs.python.org/3.14/library/stdtypes.html#set-types-set-frozenset): public operations, mixed types, comparison, and special lookup behaviour.
2. [Python 3.11 — Built-in Types, Set Types](https://docs.python.org/3.11/library/stdtypes.html#set-types-set-frozenset): compatibility audit.
3. [Python 3.14 — Glossary, hashable](https://docs.python.org/3.14/glossary.html#term-hashable): the member contract.
4. [Python 3.14 — Expressions, Set displays](https://docs.python.org/3.14/reference/expressions.html#set-displays): construction and evaluation boundaries.
5. [Python 3.14 — Data model, `__hash__`](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__): equality, hashing, and randomization.
6. [CPython v3.14.7 — `Objects/setobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/setobject.c): `set_lookkey`, `set_next`, `set_intersection`, and difference paths; implementation lens only.
7. [Python 3.14 — `PYTHONHASHSEED`](https://docs.python.org/3.14/using/cmdline.html#envvar-PYTHONHASHSEED): subprocess experiment control.
8. [Python 3.14 — Free-threading support, thread safety](https://docs.python.org/3.14/howto/free-threading-python.html#thread-safety): synchronization boundaries.
9. [PEP 585](https://peps.python.org/pep-0585/): generic built-in collection annotations since Python 3.9.
