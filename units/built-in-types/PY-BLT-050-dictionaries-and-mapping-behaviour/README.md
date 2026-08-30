# PY-BLT-050 — Dictionaries and mapping behaviour

[Curriculum entry](../../../CURRICULUM.md#py-blt-050) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-BLT-050`

## Physical Notebook Core

### Problem this concept solves

Find and update a value by a meaningful key: a setting name, job ID, or route. A positional sequence would require maintaining positions or repeatedly searching records.

### One-sentence mental model

> A dictionary is a mutable, insertion-ordered collection of bindings from hashable keys to object references.

### One important visual

```text
settings                  after settings['quota'] = 0
'quota'   -> 3             'quota'   -> 0
'enabled' -> True          'enabled' -> True
iteration: quota, enabled  iteration: quota, enabled
```

#### How to read this visual

Read each column from top to bottom in insertion order. An arrow means “this entry refers to this value.” The assignment replaces one binding.

#### Key insight

A changed value does not give an existing key a new position.

#### Simplification or limitation

This is a language-level binding diagram, not hash slots or literal CPython memory. It omits the objects representing the keys.

### Governing rules or invariants

1. Keys must be hashable. Equal keys must have equal hashes; unequal keys may collide.
2. Updating an existing key preserves its position. Deleting and reinserting it puts it last.
3. Absence differs from a stored `None`, `False`, or `0`. Views stay live; shallow copies still share child objects.

### Minimal example

```python
settings = {"quota": 3, "enabled": True}
settings["quota"] = 0
print(list(settings))
print(settings.get("quota", 99))
```

Observed on both tested runtimes: `['quota', 'enabled']`, then `0`. Lookup found an entry; the falsey value is still its value.

### One failure or misconception

**Mistake:** `settings.get("quota") or 99` means “99 only when the key is absent.”

**Correction:** `or` replaces any falsey result. Decide separately whether absence, `None`, and zero should mean different things.

### Important trade-offs

- Key lookup is usually cheap, but hashes, equality, collisions, and memory overhead matter.
- An ordinary merge replaces whole values. A new outer dict does not promise independent nested data.

### Interview-revision cues

- Why do `1`, `True`, and `1.0` address the same entry?
- What survives a value overwrite, a deletion, and reinsertion?
- Which boundary does a view, a shallow copy, or a read-only proxy actually protect?

## Unit metadata

| Field | Value |
|---|---|
| Domain | Built-in types, operations, and functions |
| Canonical ID | `PY-BLT-050` |
| Learning outcome | Use dictionaries deeply: construction, lookup, insertion order, views, merging, missing keys, iteration, and implementation-aware trade-offs |
| Hard prerequisites | `PY-FND-020`, `PY-FND-050` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D3 |
| Scope | Language, Standard library, CPython |
| Size | L |
| Evidence profile | E+C+D+(X) |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.7 and CPython 3.11.16; Linux x86_64, conventional GIL builds |
| Last source audit | 2026-08-30 |
| Artifact state | Approved |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Construct a mapping and explain duplicate-key and hashability decisions.
2. Choose a lookup policy without confusing a missing key with a stored value.
3. Predict insertion order, deletion, reinsertion, and merge precedence.
4. Distinguish a mapping, view, iterator, key snapshot, item snapshot, and shallow copy.
5. Review a backend mapping API for ownership, mutation, and invalid inputs.
6. Explain how collisions affect lookup without confusing implementation observations with language guarantees.

Required evidence is a reconstruction/explanation (E), an original implementation with edge-case checks (C), and a debugging or prediction attempt with correct reasoning (D). Runtime experimentation (X) is optional in the curriculum; two prepared experiments support it here. Running the author's code does not substitute for a learner's prediction and interpretation.

Use [mapping operations](examples/mapping_operations.py), the [settings overlay](examples/settings_overlay.py), and [unsolved practice](practice/README.md). The [live-view experiment](experiments/EXP-01-live-views-and-shallow-copies/README.md) and [collision experiment](experiments/EXP-02-collisions-and-lookup-work/README.md) contain real observations. Open the [dictionary explorer](visuals/dictionary-explorer.html) locally in a browser; GitHub shows its source instead of running it.

### Reproduce artifact checks

From the repository root, select the desired Python runtime, then run:

```bash
python scripts/validate_repo.py
python -B -m unittest discover -s units/built-in-types/PY-BLT-050-dictionaries-and-mapping-behaviour/tests -v
python -B units/built-in-types/PY-BLT-050-dictionaries-and-mapping-behaviour/examples/mapping_operations.py
python -B units/built-in-types/PY-BLT-050-dictionaries-and-mapping-behaviour/examples/settings_overlay.py
python -B units/built-in-types/PY-BLT-050-dictionaries-and-mapping-behaviour/experiments/EXP-01-live-views-and-shallow-copies/probe_views.py
python -B units/built-in-types/PY-BLT-050-dictionaries-and-mapping-behaviour/experiments/EXP-02-collisions-and-lookup-work/probe_collisions.py
python -B units/built-in-types/PY-BLT-050-dictionaries-and-mapping-behaviour/visuals/trace_data.py --check
```

Everything above uses the standard library. The explorer uses ordinary browser JavaScript with no external dependencies. Its data checker executes actual Python operations and compares all captured states with the embedded observations; it does not emulate Python with JavaScript objects. Use `--refresh` only after investigating a mismatch.

### Artifact verification — 2026-08-30

Repository validation, the two example scripts, all three runnable note snippets, both experiment probes, and **28 tests** passed on CPython **3.14.7** and **3.11.16**, with no skipped tests. The experiment transcripts were compared with fresh stdout and matched exactly. All eleven embedded visual states matched fresh Python execution on both runtimes.

Browser review exercised all eleven states, forward/backward controls, scenario reset, and disabled endpoint controls. The standalone visual was checked at 320, 360, and 736 pixels in light and dark themes; the conversation preview was also checked at narrow and wide widths. No horizontal overflow or browser console errors were found. The compact view keeps key labels on one line while allowing long values to wrap.

The source audit, complete template content, runnable checks, and protected practice justify **Approved** artifact state. Learning progress is evaluated separately from artifact quality.

No learner attempt, question response, reconstruction, or recall session was supplied. The learning state remains **Not started**; review dates and weaknesses are unchanged. Prepared exercises and experiment observations are teaching material, not learner evidence.

## 2. Prerequisite bridge

Both prerequisite artifacts exist, but their learner states are `Not started`.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | [PY-FND-020 — Objects, names, references, and mutability](../../../CURRICULUM.md#py-fnd-020) | Dictionary values can alias other objects | Copying the outer container copies bindings, not every reachable object |
| Hard | [PY-FND-050 — Truthiness, comparisons, equality, and identity](../../../CURRICULUM.md#py-fnd-050) | Lookup uses key equivalence; falsey values are still present | `is` asks about identity, `==` about equality, and truth testing is a third question |

Revisit those units in their dedicated topic tasks if either distinction is unfamiliar. The bridge lets this material proceed; it does not complete either prerequisite. Designing custom equality and hash methods belongs primarily to [PY-BLT-080](../../../CURRICULUM.md#py-blt-080).

## 3. Vocabulary and professional English

### Collision

| Item | Content |
|---|---|
| Pronunciation | kuh-LIZH-un |
| Simple English meaning | Two things meet at the same place |
| Hindi cue | टकराव |
| Meaning here | Different keys produce the same hash; equality must still distinguish them |

1. Two scheduled meetings can collide.
2. A collision does not necessarily mean data was lost.
3. This experiment deliberately creates hash collisions.
4. **Interview:** A hash collision does not imply that the keys are equal.
5. **Engineering discussion:** A poor key hash can increase comparison work even when the dictionary returns correct values.

### Snapshot

| Item | Content |
|---|---|
| Pronunciation | SNAP-shot |
| Simple English meaning | A record of selected state at one time |
| Hindi cue | एक समय की स्थिति |
| Meaning here | A materialized selection, whose copied boundary must be specified |

1. The report captures a snapshot of the queue.
2. A snapshot becomes older as the source changes.
3. This tuple preserves the keys that existed when it was created.
4. **Interview:** An item snapshot can retain references to mutable values.
5. **Engineering discussion:** We need to decide whether our snapshot protects only membership or also nested data.

## 4. Deep explanation

### 4.1 Construction and the key contract

`dict` supports key-based access; it is not a sequence with positions. `d[0]` requests the key `0`, not the first entry. Iterating `d` yields keys. Values can repeat and can be unhashable.

```python
literal = {"north": 2, "south": 3}
from_pairs = dict([("north", 2), ("south", 3), ("north", 4)])
from_mapping = dict(literal)
from_keywords = dict(literal, north=5)
squared = {number: number * number for number in range(3)}
assert list(from_pairs.items()) == [("north", 4), ("south", 3)]
assert from_keywords["north"] == 5
assert squared == {0: 0, 1: 1, 2: 4}
assert from_mapping == literal and from_mapping is not literal
```

Dictionary displays evaluate their entries from left to right. Later equal keys replace earlier values; displays do not reject duplicates. A comprehension inserts entries in the order produced, evaluating its key expression before its value expression on both baselines. See [Expressions — Dictionary displays](https://docs.python.org/3.14/reference/expressions.html#dictionary-displays). Comprehension scope and nested unpacking are covered in [PY-BLT-070](../../../CURRICULUM.md#py-blt-070).

The constructor accepts a mapping or an iterable of two-element entries; keyword arguments are applied afterwards. Keyword syntax such as `dict(north=5)` uses identifier names, while literals and pair inputs can use other hashable keys. Duplicate policy should be chosen before construction if silently accepting the final value would hide bad input. See the [3.11 mapping contract](https://docs.python.org/3.11/library/stdtypes.html#mapping-types-dict), also exercised by the examples.

Hashability requires a stable hash and a compatible equality relation. Built-in lists and dicts cannot be keys. A tuple is usable only if its elements are hashable. Conversely, an ordinary user-defined object can be mutable yet retain identity-based equality and hashing. Do not reduce the contract to “mutable versus immutable.” Equal numeric keys such as `1`, `True`, and `1.0` share an entry. Do not mix boolean flags and integer IDs when the application needs them to remain distinct. See [Data model — `__hash__`](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__). Keep equality-relevant state stable while a key is stored.

`dict.fromkeys(names, value)` stores the same supplied value for every name. This is useful for one immutable default, but does not allocate independent lists. The shared-child case is verified in [the boundary tests](tests/test_examples.py).

### 4.2 Lookup is an absence policy

| Need | Operation | Decision the caller makes |
|---|---|---|
| Missing key is exceptional | `d[key]` | Handle or propagate `KeyError` |
| Return a fallback without insertion | `d.get(key, fallback)` | Choose whether `None` is an adequate fallback |
| Ask whether a binding exists | `key in d` | Do not replace this with value truth testing |
| Insert a default on absence | `d.setdefault(key, default)` | Accept mutation and sharing of the supplied object |
| Remove and obtain a value | `d.pop(key, fallback)` | Decide whether absence needs an error or fallback |

The [dict API](https://docs.python.org/3.14/library/stdtypes.html#mapping-types-dict) specifies these operations. A missing-key fallback is not general exception suppression: unhashable keys and errors in user-defined hashing/equality can still fail.

Use a private sentinel when every ordinary value, including `None`, is meaningful. `describe_lookup` in [mapping_operations.py](examples/mapping_operations.py) demonstrates this without modifying the mapping. Sentinel identity must not be a legitimate stored value.

`d.get(key, build())` and `d.setdefault(key, build())` evaluate `build()` before the method can inspect the dictionary. `setdefault` is conditional insertion, not a lazy factory. That follows from [call expression evaluation](https://docs.python.org/3.14/reference/expressions.html#calls), and `eager_defaults()` records both calls even though the key exists.

For a `dict` subclass, missing subscription can invoke `__missing__`; ordinary `get` and membership do not invoke that hook. A hook need not insert anything. `defaultdict(factory)` supplies a particular hook which calls the factory and stores its result for missing subscription; `get` still does not invoke it. See [`defaultdict.__missing__`](https://docs.python.org/3.14/library/collections.html#collections.defaultdict.__missing__). Detailed container selection belongs to [PY-LIB-010](../../../CURRICULUM.md#py-lib-010).

### 4.3 Insertion order, merging, and mutation

Keep two questions separate: “Which value wins?” and “Where will that key be visited?” Overwriting changes the first answer without necessarily changing the second. `popitem()` removes the last inserted remaining entry, not the entry whose value was most recently changed. `reversed(d)` visits keys backwards. Dictionary equality compares contents without considering insertion order; it does not promise the same iteration sequence. These distinctions are covered by the [mapping boundary checks](tests/test_examples.py).

| Expression | Outer object | Input contract for ordinary dict behaviour |
|---|---|---|
| `left \| right` | New dict | Dict operands; other types may provide their own reflected operator |
| `left \|= right` | Mutates `left` | Mapping or iterable of pairs |
| `left.update(right)` | Mutates `left`; returns `None` | Mapping or iterable of pairs; optional keywords follow |
| `{**left, **right}` | New dict | Mapping unpacking |

Later values take precedence. New keys follow existing ones in their source iteration order. These operations do not recursively merge nested dictionaries. The binary union and augmented union deliberately accept different operand sets; an arbitrary `Mapping` interface does not itself provide dict union. See [PEP 584 — Specification](https://peps.python.org/pep-0584/#specification).

```python
left = {"workers": 2, "options": {"connect": 3, "read": 10}}
right = {"options": {"connect": 1}, "enabled": False}
merged = left | right
assert list(merged) == ["workers", "options", "enabled"]
assert merged["options"] == {"connect": 1}
assert merged["options"] is right["options"]
assert left["options"] == {"connect": 3, "read": 10}
```

A failed in-place update is not a rollback mechanism. When input iteration, unpacking, hashing, or equality can fail, do not assume earlier work was undone. Build and validate a candidate separately if the application needs an all-or-nothing replacement, and define how callers observe that replacement.

### 4.4 Views, iterators, and the copy boundary

| Object | What is retained | What later changes can reveal |
|---|---|---|
| `d.keys()`, `d.values()`, `d.items()` | Live access to the original dict | Current entries on later observation |
| `iter(d)` | Traversal state tied to the original dict | Structural changes can invalidate traversal |
| `tuple(d)` | References to the keys selected now | No new or removed membership is reflected |
| `tuple(d.items())` | Materialized pair tuples with value references | Edits inside a selected mutable value remain visible |
| `d.copy()` or `dict(d)` | Another outer dict with shared key/value references | Independent bindings; shared nested objects |

The [view contract](https://docs.python.org/3.14/library/stdtypes.html#dict-views) warns that adding or deleting entries during traversal may raise an error or omit entries. Do not rely on every bad mutation being detected. Replacing values without changing the key set is a different operation; it still does not give the iterator a frozen value snapshot.

When deletion during a pass is required, choose an explicit traversal snapshot or construct a replacement mapping. Specify whether the boundary is keys, pairs, or a supported deep copy. `copy.deepcopy` recursively copies supported contents and preserves graph relationships through memoization; custom objects can customize copying. See [`copy`](https://docs.python.org/3.14/library/copy.html). None of these choices alone promises consistency while another actor changes the source.

Key views support set-style operations, but an operation producing a set does not preserve dict insertion order. Item-view membership can compare list-valued pairs even though constructing a set of those pairs would fail. Values views have no content-equality comparison analogous to lists: two freshly obtained values views do not compare their contents. Choose an explicit sequence or counting representation according to whether order and multiplicity matter. The distinctions are exercised in [the tests](tests/test_examples.py); set algebra continues in [PY-BLT-060](../../../CURRICULUM.md#py-blt-060).

### 4.5 Mapping interfaces and read-only access

`collections.abc.Mapping` describes readable mapping operations; `MutableMapping` additionally describes assignment and deletion. Accepting `Mapping[str, object]` lets an API work with read-only implementations without requiring a concrete dict. It does not enforce a runtime schema, immutable contents, constant-time lookup, insertion ordering, or support for `|`. Custom implementations can define different operational behaviour. See [the ABC method table](https://docs.python.org/3.14/library/collections.abc.html#collections.abc.Mapping).

`MappingProxyType(d)` rejects assignment through that proxy, while still reflecting writes through the original dictionary. It also does not freeze nested lists. This is a restricted access path, not a deep snapshot or synchronization mechanism. See [`MappingProxyType`](https://docs.python.org/3.14/library/types.html#types.MappingProxyType) and [EXP-01](experiments/EXP-01-live-views-and-shallow-copies/README.md).

### 4.6 Execution sequence: replacing a nested reference

| Step | Event | Relevant state |
|---:|---|---|
| 1 | `copied = d.copy()` | Two outer dictionaries refer to list A |
| 2 | Append to list A through `d` | Both paths observe A's changed contents |
| 3 | Bind `d['tags']` to list B | `copied['tags']` still refers to A |
| 4 | Edit A through `copied` | B is unaffected |

#### How to read this visual

Follow the event column in order. A and B are object identities, not variable names or memory addresses.

#### Key insight

Mutating a referent and replacing a binding have different effects on aliases.

#### Simplification or limitation

This models built-in dicts and lists in one thread. It excludes custom copying and concurrent writers.

### 4.7 CPython implementation lens

For a conventional CPython 3.14.7 combined table, distinguish sparse hash slots from the entry array. A simplified general-key lookup follows this sequence:

1. Compute the query hash and choose an initial slot.
2. An unused slot ends an unsuccessful search; a deleted-slot marker means continue probing.
3. For an occupied candidate, identity can establish a match. Otherwise matching hashes permit an equality check; a collision without equality continues the search.
4. On insertion of a new key, entry storage and the hash index are updated. Growth can trigger resizing.

This explains why collisions need not lose data, why deletion cannot always turn a slot straight back into “never used,” and why Python equality-call counts do not count all table work. See `do_lookup` and `compare_generic` in the [pinned implementation](https://github.com/python/cpython/blob/v3.14.7/Objects/dictobject.c). Specialized keys and concurrent-access paths have additional machinery.

Some instance dictionaries use split tables and can share key information while retaining separate values; [PEP 412](https://peps.python.org/pep-0412/) explains that design motivation. This is not a promise that every dictionary has the same layout or memory cost. No byte-offset, load-factor, or allocator-size assumption belongs in the application examples.

## 5. Additional visual models

### 5.1 Shallow copy separates bindings, not all objects

```text
After copy:                     After d['tags'] = ['replacement']:
d['tags'] ------+               d['tags'] -------> list B
                +--> list A
copied['tags'] -+               copied['tags'] --> list A
```

#### How to read this visual

Two arrows meeting at A mean two references to one list. Rebinding redirects only one arrow.

#### Key insight

Outer independence and nested independence are separate ownership decisions.

#### Simplification or limitation

The picture is conceptual. It hides key objects and the containers' internal storage. [EXP-01](experiments/EXP-01-live-views-and-shallow-copies/README.md) checks this with identity comparisons rather than addresses.

### 5.2 Lookup route and iteration route are different

```text
lookup:     key -> hash -> candidate slot -> entry -> match? -> value
                                            |
                                 no match: try another slot

iteration:  entry A -> entry B -> entry C
            visit surviving entries in insertion order
```

#### How to read this visual

The upper route chooses candidate entries through a hash table; a collision alone does not prove equality. The lower route visits entries in their order, independent of where their hash slots happen to be.

#### Key insight

Insertion order and hash-based lookup can coexist because they answer different questions.

#### Simplification or limitation

This is a schematic for CPython's combined-table design, not literal offsets or the complete probing algorithm. In v3.14.7, `dk_indices` refers into entry storage; a general-key candidate can match by identity or by hash plus equality. Deleted slots need distinct bookkeeping so collision searches can continue. Other layouts, including split tables for some instance dictionaries, need additional explanation. See [`Objects/dictobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictobject.c), the layout comments, `compare_generic`, and `do_lookup`.

### 5.3 Interactive dictionary state explorer

Open [dictionary-explorer.html](visuals/dictionary-explorer.html).

#### How to read this visual

Choose “Insertion order” or “Views and shallow copies,” then move one operation at a time. Each state is after the displayed operation. Visit numbers show traversal positions, not integer keys. Equal list labels identify a shared object.

#### Key insight

Compare live keys with the saved tuple, then compare mutation with rebinding across the two dictionaries.

#### Simplification or limitation

The page replays eleven states captured by [trace_data.py](visuals/trace_data.py). It cannot execute arbitrary Python or show physical memory. It has no external assets or network requests. The source note and experiment transcripts remain usable without the interactive page.

## 6. Worked examples

### 6.1 Small operations with visible outcomes

Run [mapping_operations.py](examples/mapping_operations.py). Before executing, explain why a later value can coexist with an earlier key position, why the falsey quota survives, and when a missing-key hook is used.

Observed on CPython 3.14.7 and 3.11.16:

```text
constructed: [('blue', 3), ('green', 2)]
overwritten: [('blue', 4), ('green', 2)]
reinserted: [('green', 2), ('blue', 5)]
last inserted: ('blue', 5)
equal numeric keys: 1 float
lookup states: present: 0 present: None missing
eager defaults: (0, 0, ['built', 'built'])
missing hook: unknown:west None False
defaultdict get: None []
defaultdict subscription: {'west': ['event']}
union: {'workers': 2, 'options': {'connect': 1}, 'enabled': False}
union shares right value: True
in-place union: True 4
```

The missing hook returned a value without insertion; `defaultdict` subscription did insert. Union made a new outer dictionary but retained the right operand's nested options object. An in-place union retained the existing outer object's identity.

### 6.2 Backend example: a settings overlay

[settings_overlay.py](examples/settings_overlay.py) accepts readable mappings, rejects unknown setting names, and returns a new outer dictionary. Absence preserves a default; every supplied value replaces it, including `None`, `False`, and `0`. The return value is intentionally shallow.

Observed from the complete script on both runtimes:

```text
resolved: {'retries': 0, 'enabled': False, 'tags': ['base']}
defaults: {'retries': 3, 'enabled': True, 'tags': ['base']}
new outer dictionary: True
shared tags: True
read-only view stays live: 1
unknown name: unknown settings: 'retry'
```

This fits an internal API with stable mappings and known string names. It catches misspellings without mistaking a disabled setting for missing input. It does not validate the type or range of each setting; a public boundary needs a schema. If nested independence or recursive merge rules are required, specify them rather than adding a generic deep merge whose list, deletion, and `None` policies are unclear. The tests cover falsey overrides, read-only inputs, rejected names, ordering, and aliasing.

### 6.3 Debugging example: attempt before correction

[PY-BLT-050-P03](practice/README.md#py-blt-050-p03) contains a reverse-index bug. Predict the information loss before running it. The diagnosis, corrected implementation, and comparison solution are not prewritten.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| Lookup `d[0]` means first entry | Sequence syntax is familiar | It requests the key `0` | Use string-only keys |
| A collision overwrites another key | Hashes are mistaken for identities | Equality still distinguishes candidates | Run EXP-02 |
| Any tuple is a valid key | The outer tuple cannot be edited | All its elements must be hashable | Use a tuple containing a list |
| `get` is a lazy factory | The default looks conditional | Argument expressions run first | Run `eager_defaults()` |
| A copy recursively isolates values | The outer object is new | Children can still be shared | Reconstruct the two arrows to A |
| Items views always require hashable values | Set construction does | Membership can compare an unhashable value | Compare membership with `set(d.items())` |
| Values views compare contents | They look like collections of values | Choose an explicit comparison representation | Compare two fresh values views, then two lists |
| Order means sorted order | Output is repeatable for a fixed input | Dict preserves the order it receives | Insert keys in two different sequences |
| Unchanged size makes mutation during iteration safe | A size check seems sufficient | Changing the key set is still unsafe | Do not build correctness on error detection |
| A read-only proxy is frozen data | Assignment is rejected | Other aliases and nested objects may change | Run EXP-01 |

## 8. Complexity and performance

Let `n` and `m` be ordinary dict sizes, assuming stable, bounded-cost hashes/equality and no unusually sparse deletion history.

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| `len(d)`; create a view | O(1) | Does not copy entries |
| Lookup, key membership, deletion | Expected O(1) | Collisions can make a lookup O(n); custom methods add cost |
| Insert one key | Amortized expected O(1) | A resize can do much more work on one insertion |
| Value membership | O(n) scan | No reverse index by value |
| Copy or materialize all entries | O(n) time and additional storage | A shallow operation; nested objects are not included |
| `left \| right` | Expected O(n+m) time and O(n+m) result storage | Key overlap affects result size |
| Repeated growing `result = result \| part` | Can become quadratic overall | Earlier entries are copied again on each merge |
| Mutable-key or custom-mapping design | Contract-dependent | Dict estimates do not transfer automatically |

These are implementation-aware estimates, not Python timing guarantees. [CPython's dictionary notes](https://github.com/python/cpython/blob/v3.14.7/Objects/dictnotes.txt) discuss one-key operations, resizing, density, and iteration trade-offs. A dictionary with many deletions can retain storage and holes; `len(d)` is not a measurement of allocation or traversal work. A shallow size measurement would also exclude separately allocated keys and values.

[EXP-02](experiments/EXP-02-collisions-and-lookup-work/README.md) counts equality calls on deliberately colliding keys. It is not a timing benchmark and does not claim a speedup or a fixed cost ratio. Ordinary string hashes are randomized between processes by default; hash values are not durable IDs. Randomization also does not remove the need to bound untrusted workload size. See [Data model — hash randomization](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__). No exact hash or table-size assumption is needed by the examples.

## 9. Production relevance and trade-offs

- **Define presence:** a missing setting, explicit `None`, and a disabled/zero value may have three different meanings.
- **Define duplicate policy:** replacement suits a settings overlay; duplicate IDs may instead need rejection or grouping. Normal construction will not enforce a domain invariant for you.
- **Define ownership:** document whether callers may mutate the result, whether children remain shared, and whether a proxy is live.
- **Define ordering:** sort deliberately when canonical output is required. A dict built from an unordered source preserves that source's encountered order, not a universal order.
- **Define observation boundaries:** a check followed by an update is a multi-step workflow. Do not infer its correctness under concurrent writers from individual dict operations. Use ownership or synchronization that protects the whole invariant; see the [thread-safety guidance](https://docs.python.org/3.14/howto/free-threading-python.html#thread-safety) and [PY-CON-030](../../../CURRICULUM.md#py-con-030).
- **Choose a suitable abstraction:** `Mapping` is useful for readable inputs; a typed record can be clearer for a fixed schema. Specialized collections and schema design have their own units.
- **Bound resource use:** expected cheap lookup does not make an unbounded cache or input map safe. No concurrency or latency benchmark was run for this artifact.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| Insertion order and LIFO `popitem` | Language / built-in contract | 3.7 guarantee | Same operations | CPython 3.6 order was an implementation detail |
| Reverse iteration over dicts and views | Built-in contract | 3.8 | Same operations | Reverse insertion order, not sorting |
| Dict comprehension key-before-value evaluation | Language | 3.8 guarantee | Same syntax | Do not infer this historical order for older versions |
| Mapping unpacking in dict displays | Language | 3.5 | Same syntax | Mapping inputs; later values replace earlier ones |
| Dict union and augmented union | Built-in contract | 3.9 | Same operations | Different accepted input contracts |
| `MappingProxyType` | Standard library | 3.3 | Same constructor | Live read-only access, not deep immutability |
| `dictview.mapping` | Standard library | 3.10 | Same property | Returns a proxy for the underlying dictionary |
| Hash slots, entry storage, collision counts | CPython | Version-labelled observations | Recheck target runtime | Exact layout and counts are not language promises |

The [3.11 mapping documentation](https://docs.python.org/3.11/library/stdtypes.html#mapping-types-dict) was checked alongside 3.14. All authored Python code runs unchanged on the two tested maintenance releases. The repository's Python pin is unchanged. No free-threaded build or alternative interpreter was tested.

## 11. Practice brief

All exercises start **Not attempted**. Use [practice/README.md](practice/README.md); no learner solution or completed-review file has been fabricated.

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-BLT-050-P01` | Predict | 2 | E+D: key equivalence, order, and views | [Prompt](practice/README.md#py-blt-050-p01) |
| `PY-BLT-050-P02` | Implement | 3 | C: reject duplicate records without changing input | [Prompt](practice/README.md#py-blt-050-p02) |
| `PY-BLT-050-P03` | Debug | 3 | D+C: preserve information in a reverse index | [Prompt](practice/README.md#py-blt-050-p03) |
| `PY-BLT-050-P04` | Implement / Review | 4 | C+D: distinguish changed, added, and removed bindings | [Prompt](practice/README.md#py-blt-050-p04) |
| `PY-BLT-050-P05` | Design / Experiment | 4 | E+X: explain lookup work and test its limits | [Prompt](practice/README.md#py-blt-050-p05) |

## 12. Interview prompts

Ask one prompt at a time and wait for an attempt before showing a model answer.

1. Walk through a dictionary lookup when a distinct key has the same hash as an existing key. Which conditions can share an entry?
2. An API promises “a read-only snapshot.” What questions would you ask before choosing a tuple, dict copy, or mapping proxy?
3. Review a configuration merge in which nested values are shared and updates arrive concurrently. Which guarantees must belong to the API rather than to dict itself?

A strong answer should eventually distinguish the public contract, ownership boundary, and implementation cost; giving method names alone is insufficient.

## 13. Closed-book revision cues

1. Reconstruct the one-sentence model and three governing rules.
2. Draw two outer dicts sharing one child, then rebind one entry.
3. Explain a stored `None` versus a missing key without relying on truthiness.
4. Describe how a reverse index can silently discard records.
5. Explain why insertion order does not contradict hash-based lookup.
6. Name one observed CPython detail that should not become an application assumption.

## 14. Authoritative sources

Opened and read on **2026-08-30**. Explanations, examples, exercises, and diagrams are original; no source implementation is copied.

1. [Python 3.14 — Built-in Types](https://docs.python.org/3.14/library/stdtypes.html#mapping-types-dict): dictionaries, methods, order, and dictionary view objects.
2. [Python 3.14 — Expressions](https://docs.python.org/3.14/reference/expressions.html#dictionary-displays): dictionary displays, comprehension evaluation, and calls.
3. [Python 3.14 — Data model](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__): equality/hash contracts and hash randomization.
4. [PEP 584](https://peps.python.org/pep-0584/): union operators, operand contracts, ordering, and replacement semantics.
5. [Python 3.14 — `collections.abc`](https://docs.python.org/3.14/library/collections.abc.html#collections.abc.Mapping): readable and mutable mapping interfaces.
6. [Python 3.14 — `defaultdict`](https://docs.python.org/3.14/library/collections.html#collections.defaultdict): missing-subscription factory behaviour.
7. [Python 3.14 — `MappingProxyType`](https://docs.python.org/3.14/library/types.html#types.MappingProxyType): dynamic read-only access.
8. [Python 3.14 — `copy`](https://docs.python.org/3.14/library/copy.html): shallow/deep copy boundaries and customization.
9. [CPython v3.14.7 — `Objects/dictobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictobject.c): combined/split layouts, `compare_generic`, `do_lookup`, and deletion bookkeeping.
10. [CPython v3.14.7 — `Objects/dictnotes.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictnotes.txt): operation, density, and resize trade-offs.
11. [Python 3.11 — Built-in Types](https://docs.python.org/3.11/library/stdtypes.html#mapping-types-dict): compatibility cross-check.
12. [Python 3.14 — Free-threading support](https://docs.python.org/3.14/howto/free-threading-python.html#thread-safety): limits of internal container locking and explicit synchronization guidance.
13. [PEP 412](https://peps.python.org/pep-0412/): the motivation and ownership boundary for key-sharing dictionaries.
