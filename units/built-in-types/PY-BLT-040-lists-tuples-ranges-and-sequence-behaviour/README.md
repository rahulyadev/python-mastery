# PY-BLT-040 — Lists, tuples, ranges, and sequence behaviour

[Curriculum entry](../../../CURRICULUM.md#py-blt-040) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-BLT-040`

## Physical Notebook Core

### Problem this concept solves

Keep ordered data, select parts of it, and decide which later changes should be visible to other code.

### One-sentence mental model

> A list has editable ordered slots, a tuple fixes its ordered slots, and a range describes an integer progression; fixing or copying slots does not freeze the objects they reference.

### One important visual

```text
jobs ───────────> list A [ slot 0 ] ───> child list ["queued"]
alias ──────────>    A                       ^
copy = jobs[:] -> list B [ slot 0 ] ─────────┤
tuple(jobs) ---> tuple C ( slot 0 ) ─────────┘
```

#### How to read this visual

Names point to containers; each slot points to an element. A and B have separate slots, but both slots and C's fixed slot reach the same child.

#### Key insight

Replacing a slot in B affects B; mutating the child is visible through A, B, and C.

#### Simplification or limitation

This is a conceptual reference graph, not CPython memory layout. It omits capacity, object headers, and deeper descendants.

### Governing rules or invariants

1. Indexing chooses one element; slicing chooses positions, excludes the stop, and clips bounds.
2. The step sets direction; omitted bounds depend on that direction. A zero step is invalid when used.
3. List slices copy references into a new outer list. Tuples fix references, not descendant state.
4. `range` is a reusable sequence, not an iterator or a prebuilt list.

### Minimal example

```python
jobs = [["queued"]]
copied = jobs[:]
copied[0].append("sent")
print(jobs)                  # [['queued', 'sent']]
print(copied is jobs)         # False
print(copied[0] is jobs[0])   # True
```

Expected reasoning: the slice creates an outer list; `append` changes the shared child.

### One failure or misconception

**Mistake:** “`tuple(jobs)` makes the whole job graph immutable.”

**Correction:** it fixes membership and order at one level only.

### Important trade-offs

- Choose a list for editable collections, a tuple for fixed membership or a small positional record, and a range for a regular integer progression.
- A shallow copy isolates structure cheaply; independent mutable descendants need an explicit ownership policy.

### Interview-revision cues

- Draw slots before predicting mutation.
- Explain omitted versus explicit negative bounds.
- Separate compact representation from iteration cost.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Built-in types, operations, and functions |
| Canonical ID | `PY-BLT-040` |
| Learning outcome | Select and use `list`, `tuple`, and `range`; reason about slicing, copies, nesting, and sequence behaviour |
| Hard prerequisites | `PY-FND-020`, `PY-FND-040` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D2 |
| Scope | Language, Standard library |
| Size | L |
| Evidence profile | E+C+D+(X) |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.7 and CPython 3.11.16; Linux x86_64, conventional GIL builds |
| Last source audit | 2026-08-30 |
| Artifact state | Approved |

## 1. Learning outcome and evidence

After this unit, explain the choice of sequence type, predict positive and negative slices, distinguish mutation from rebinding, diagnose accidental sharing, and build a sequence API with clear ownership and boundary behavior.

Required evidence for `E+C+D+(X)`:

- **E — Explain:** reconstruct the reference graph and a negative-step slice without reading the note.
- **C — Code:** implement the protected segment-rotation exercise with tests and an ownership explanation.
- **D — Debug:** preserve and repair the original tail-selection attempt, explaining the first incorrect assumption.
- **(X) — Recommended experiment:** predict a changed input before reproducing either recorded experiment.

Start with the [worked operations](examples/sequence_operations.py) and [batch plan](examples/batch_plan.py), then use [practice](practice/README.md). The [copy experiment](experiments/EXP-01-copy-and-nesting/README.md), [slice/range experiment](experiments/EXP-02-slices-and-ranges/README.md), and [interactive slice explorer](visuals/slice-explorer.html) expose hidden state. Open the HTML locally in a browser; GitHub displays its source instead of running it.

Author execution is artifact verification, not learner evidence. No learner attempt or review is recorded; learning remains **Not started**.

### Reproduce artifact checks

From the repository root, use the intended Python environment:

```bash
python -B scripts/validate_repo.py
python -B units/built-in-types/PY-BLT-040-lists-tuples-ranges-and-sequence-behaviour/examples/sequence_operations.py
python -B units/built-in-types/PY-BLT-040-lists-tuples-ranges-and-sequence-behaviour/examples/batch_plan.py
python -B units/built-in-types/PY-BLT-040-lists-tuples-ranges-and-sequence-behaviour/experiments/EXP-01-copy-and-nesting/copy_probe.py
python -B units/built-in-types/PY-BLT-040-lists-tuples-ranges-and-sequence-behaviour/experiments/EXP-02-slices-and-ranges/slice_range_probe.py
python -B -m unittest discover -s units/built-in-types/PY-BLT-040-lists-tuples-ranges-and-sequence-behaviour/tests -v
```

The Python artifacts need only the standard library. Node.js is additionally needed for the three explorer-model checks in [test_visual_model.py](tests/test_visual_model.py); without it they explicitly skip. Editing the visual requires running those checks, not accepting skips as verification.

### Artifact verification — 2026-08-30

Repository validation and all **30 tests** passed on CPython **3.14.7** and **3.11.16**, with no skips. Both example scripts and both experiment probes ran on each runtime. The stored experiment transcripts were compared with actual stdout and matched exactly. The test suite includes 9,100 comparisons between the explorer's JavaScript model and Python slicing; Node.js 24.19.0 was available for those checks.

The browser review exercised the presets, lengths 0 and 12, an out-of-range length, zero step, unsafe integer input, and explicit `None`. Layouts were checked at 320, 360, and 736 pixels without horizontal overflow; no browser console errors were reported. The visual remains a bounded model, not a Python runtime.

The source audit, runnable checks, complete template content, and protected practice justify **Approved** artifact state. No learner attempt, reconstruction, quiz, or delayed recall was recorded, so the learning state and review dates remain unchanged.

## 2. Prerequisite bridge

Both prerequisites have approved artifacts but `Not started` learning states. Use this bridge to begin, then revisit their dedicated units before claiming understanding.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-FND-020` — Objects, names, references, and mutability | Copy and alias behavior depends on which object changes. | Assignment binds a name; it does not clone an object. Follow the reference to distinguish rebinding, slot replacement, and child mutation. |
| Hard | `PY-FND-040` — Expressions, evaluation order, and operators | Subscription and augmented assignment combine lookup, an operation, and storage. | `+=` can mutate an object before assigning its result back. It is not generally interchangeable with `x = x + y`. |

A bridge does not complete either prerequisite.

## 3. Vocabulary and professional English

### Alias

| Item | Content |
|---|---|
| Pronunciation | AY-lee-us |
| Simple English meaning | Another way to refer to the same thing |
| Hindi cue | उसी वस्तु का दूसरा संदर्भ |
| Meaning in this Python context | Another name or slot that reaches the same object |

1. The two names are aliases for one queue.
2. Copying the outer list preserves aliases to its children.
3. Rebinding one name does not redirect the other alias.
4. **Interview:** “I will draw the aliases before predicting this mutation.”
5. **Engineering discussion:** “The returned collection must not expose an alias to our editable internal list.”

### Stride

| Item | Content |
|---|---|
| Pronunciation | stryde |
| Simple English meaning | The distance between successive steps |
| Hindi cue | हर कदम का अंतर |
| Meaning in this Python context | The signed increment between selected sequence positions |

1. A stride of two visits alternate positions.
2. A negative stride moves toward smaller indices.
3. This stride selects no positions because its direction conflicts with the bounds.
4. **Interview:** “I separate the starting index from the stride before expanding the slice.”
5. **Engineering discussion:** “The sample interval is a stride, not the number of returned records.”

## 4. Deep explanation

### 4.1 Why three sequence types?

Consider a batch dispatcher. The pending identifiers change as jobs arrive; a list fits. One dispatched batch has fixed membership; a tuple of immutable identifiers fits. Batch starts are `0, batch_size, 2 * batch_size, ...`; a range expresses that pattern without storing all offsets.

These are design choices, not restrictions on homogeneous versus heterogeneous contents. A tuple can hold many similar values; a list can hold different types. For a record with many fields, names may communicate intent better than positional indices.

```python
pending = ["job-a", "job-b"]
record = ("job-a", 2)      # identifier, attempt count
singleton = ("job-a",)    # comma creates the singleton tuple
grouped = ("job-a")       # just a string expression
offsets = range(0, 7, 3)   # 0, 3, 6
```

The comma distinction is language syntax, not a storage optimization. See [parenthesized forms](https://docs.python.org/3.14/reference/expressions.html#parenthesized-forms).

### 4.2 Indexing and slicing

An index identifies one slot. Negative indices count from the end, and an invalid index raises `IndexError`. A slice selects a sequence of positions. Its result type follows the built-in receiver: list, tuple, or range. The [data model](https://docs.python.org/3.14/reference/datamodel.html#sequences) defines those boundaries.

For a sequence of length `n`, use this reasoning procedure:

1. Choose the step; an omitted step means `1`.
2. For a positive step, default start/stop are `0` and `n`. For a negative step, they are `n - 1` and the sentinel just before position zero.
3. Translate **explicit** negative bounds relative to `n`, then clip them to the allowed endpoints for that direction.
4. Visit positions while still strictly before the stop in the chosen direction.

Use Python to check your reasoning:

```python
letters = list("ABCDEF")
selection = slice(None, None, -2)
bounds = selection.indices(len(letters))
positions = list(range(*bounds))
print(bounds, positions, letters[selection])
```

Observed on both tested runtimes:

```text
(5, -1, -2) [5, 3, 1] ['F', 'D', 'B']
```

`slice.indices(n)` normalizes missing and clipped endpoints. Its output is useful as arguments to `range`, not necessarily as a replacement raw slice. In particular, the normalized `-1` sentinel would become an end-relative index if inserted into a new slice. The [slice contract](https://docs.python.org/3.14/reference/datamodel.html#slice.indices) and [recorded probe](experiments/EXP-02-slices-and-ranges/README.md) ground this distinction.

Slice syntax creates a `slice` object; the receiver interprets it. Creating `slice(None, None, 0)` alone succeeds, but applying it to these sequences or calling its `indices` rejects the zero step. Custom objects can interpret subscriptions differently. See [subscriptions and slicings](https://docs.python.org/3.14/reference/expressions.html#slicings).

### 4.3 Editing lists

The following small examples are independent; each begins with a fresh `items = [10, 20, 30]`.

| Operation | Resulting `items` | Return or distinction |
|---|---|---|
| `items.append([40, 50])` | `[10, 20, 30, [40, 50]]` | Adds one object; returns `None` |
| `items.extend([40, 50])` | `[10, 20, 30, 40, 50]` | Consumes elements; returns `None` |
| `items.insert(1, 15)` | `[10, 15, 20, 30]` | Inserts before position 1 |
| `items.pop(1)` | `[10, 30]` | Returns removed value `20` |
| `items.remove(20)` | `[10, 30]` | Removes first matching value; returns `None` |
| `items[1:2] = [21, 22]` | `[10, 21, 22, 30]` | Replaces a contiguous region; can resize |
| `items[1:1] = [15]` | `[10, 15, 20, 30]` | Empty slice assignment inserts |
| `items[::2] = [11, 31]` | `[11, 20, 31]` | Extended assignment matches selected count |
| `del items[::2]` | `[20]` | Extended deletion may shrink |
| `items.clear()` | `[]` | Existing aliases see the same emptied list |

For extended assignment with step other than `1`, a count mismatch raises `ValueError`. Ordinary slice assignment is allowed to change length. `remove` raises `ValueError` when absent; `pop` raises `IndexError` for an invalid position. See [mutable sequence operations](https://docs.python.org/3.14/library/stdtypes.html#mutable-sequence-types).

For lists, `a += iterable` extends the existing list; `a = a + another_list` binds `a` to a new list. The latter does not redirect old aliases. A tuple's `+=` binds a replacement tuple when the target is a name. Augmented assignment evaluates the target once and can modify it in place before storing the result. See [augmented assignment](https://docs.python.org/3.14/reference/simple_stmts.html#augmented-assignment-statements).

### 4.4 Copies, repetition, and nesting

Assignment creates another reference. `list(existing_list)`, `existing_list.copy()`, and a list slice create outer lists with references to the selected elements. `deepcopy` recursively copies supported contents and uses memoization to preserve graph relationships and handle cycles; it is not a promise to make every occurrence independent. Custom copying behavior and resource objects need separate consideration. See [`copy`](https://docs.python.org/3.14/library/copy.html).

For example, copying a graph with two references to one child can produce a new graph with two references to **one copied child**. [EXP-01](experiments/EXP-01-copy-and-nesting/README.md) records this directly. Deep copying repeated rows is therefore not a general way to create independent rows.

Repetition repeats references too: an expression constructing one child is evaluated once before its containing sequence is repeated. Construct each mutable row independently when rows must vary independently. The [Python FAQ on multidimensional lists](https://docs.python.org/3.14/faq/programming.html#how-do-i-create-a-multidimensional-list) explains this aliasing boundary.

A tuple prevents replacing its slots, adding slots, or removing slots. It does not prevent mutation of an object in a slot. Hashability is also conditional: a tuple containing a list cannot be hashed. Converting the outer container alone does not fix that. See [immutable sequences](https://docs.python.org/3.14/library/stdtypes.html#immutable-sequence-types). Deeper hash contracts belong to `PY-BLT-080`.

### 4.5 A range describes a finite progression

`range(start, stop, step)` describes `start + i * step` at each logical index `i`, stopping before the exclusive bound. It accepts integers or objects supporting the integer-index protocol, not floating-point endpoints. The step cannot be zero.

```python
r = range(17, 2, -4)
print(list(r))       # [17, 13, 9, 5]
print(r[-1])         # 5
print(list(r[1:]))   # [13, 9, 5]
```

The range stores a description, not all its values. Iteration computes values as needed; `list(r)` explicitly materializes them. Range slices are ranges. Equality compares represented sequences, so different constructor arguments can describe equal ranges. Concatenation, repetition, and ordering comparisons are unsupported. See [ranges](https://docs.python.org/3.14/library/stdtypes.html#ranges).

Two calls to `iter(r)` have independent positions; `next(r)` itself is invalid. `range` is thus reusable, unlike an iterator that is already partway through consumption. A very large range can still support indexing and integer membership when `len(r)` overflows the platform's length limit; the probe exercises this without materializing the large range.

### 4.6 Equality, search, sorting, and iteration

List and tuple comparisons are lexicographic: compare corresponding elements until a difference determines the result. Equal prefixes leave the shorter sequence first. A list and tuple do not become equal just because their elements match, and ordering can fail when the compared elements lack a compatible ordering. See [value comparisons](https://docs.python.org/3.14/reference/expressions.html#value-comparisons).

For these containers, membership searches elements rather than contiguous subsequences. `count(x)` counts matches; `index(x)` locates the first or raises `ValueError`. Equality can succeed across numeric types: `4.0 in range(0, 10, 2)` is true. That result alone does not establish the lookup's cost.

`sorted(data)` returns a new list. `data.sort()` edits a list and returns `None`. Both preserve input order among equal sort keys, including when `reverse=True`. Use an explicit key when only part of a record should determine order. [`Sorting Techniques`](https://docs.python.org/3.14/howto/sorting.html#sort-stability-and-complex-sorts) documents stability and key extraction.

`items[::-1]`, `items.reverse()`, and `reversed(items)` have different ownership and result contracts: reversed copy, in-place mutation, and iterator respectively. A list iterator does not snapshot the list. The next-position visual below explains why structurally editing its list is hazardous.

### 4.7 Execution sequence: a failure can follow a successful mutation

In the copy probe, `boxed = ([],)` followed by `boxed[0] += [7]` raises `TypeError`, but the child list already contains `7`.

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Look up `boxed[0]` | The target value is a mutable list |
| 2 | Perform the list's in-place addition | That list now contains `7` |
| 3 | Assign the result back to tuple slot 0 | Tuple slot assignment raises `TypeError` |
| 4 | Inspect after catching the exception | The earlier child mutation remains |

This follows the augmented-assignment steps; an exception is not automatic rollback. The [recorded experiment](experiments/EXP-01-copy-and-nesting/README.md) shows the actual result. This does not imply that all operations failing with `TypeError` partially mutate their inputs.

## 5. Additional visual models

### 5.1 Omitted stop versus explicit `-1`

```text
source index       0   1   2   3   4   5
source value       A   B   C   D   E   F
negative index    -6  -5  -4  -3  -2  -1

[::-1]     normalized positions: 5 -> 4 -> 3 -> 2 -> 1 -> 0   stop: -1 sentinel
[:-1:-1]   normalized start: 5    normalized stop: 5           no visits
```

#### How to read this visual

The top rows name the same six positions two ways. Expand the normalized position range, obeying the direction and excluding its stop.

#### Key insight

An omitted negative-step stop is not an explicit `-1`. Compare the two presets in the [slice explorer](visuals/slice-explorer.html).

#### Simplification or limitation

These are logical positions for built-in sequences. The explorer limits length to 0–12 and inputs to safe JavaScript integers; it is not a Python interpreter. Its model is checked against Python itself.

### 5.2 An iterator's next index survives a deletion

```text
list before next()     ["A", "B", "C"]   next index = 0
next() returns "A"     ["A", "B", "C"]   next index = 1
delete slot 0          ["B", "C"]        next index = 1
next() returns "C"     ["B", "C"]        next index = 2
```

#### How to read this visual

Move downward one action at a time. Deletion shifts list elements left but does not move the iterator's next index back.

#### Key insight

An element can move behind the cursor without being visited. Plan structural edits separately, or choose a deliberate traversal strategy.

#### Simplification or limitation

This illustrates the documented built-in mutable-sequence iterator behavior, not all iterables. It omits reversed iteration, concurrent changes, and custom iterator implementations. See [common sequence operations](https://docs.python.org/3.14/library/stdtypes.html#common-sequence-operations).

### 5.3 Slicing a range selects indices before values

```text
r = range(3, 24, 4)
logical index      0    1    2    3    4    5
value              3    7   11   15   19   23
r[1::2]                 ^        ^        ^
selected indices        1        3        5
selected values         7       15       23
new progression         range(7, 27, 8)
```

#### How to read this visual

Choose positions `1, 3, 5`, then look up their values. The value step becomes `4 * 2`.

#### Key insight

Slicing changes the arithmetic description. The resulting stop need not equal an existing value or the original stop.

#### Simplification or limitation

This is a logical model for one nonempty positive range. It is not a unique constructor representation and does not show implementation storage. Negative and empty cases need their own bound calculations.

## 6. Worked examples

### 6.1 Trace selection, mutation, and sorting

Run [sequence_operations.py](examples/sequence_operations.py). Predict the selected positions and which name retains the list extended by `+=` before execution.

Observed output on CPython 3.14.7 and 3.11.16:

```text
slice bounds: (5, -1, -2)
visited positions: [5, 3, 1]
selected values: ['F', 'D', 'B']
current after += then +: [10, 20, 30, 40]
earlier alias: [10, 20, 30]
priority order: [(1, 'job-b'), (1, 'job-a'), (2, 'job-c')]
arrival order unchanged: [(2, 'job-c'), (1, 'job-b'), (1, 'job-a')]
descending range values: [17, 13, 9, 5]
range slice: range(13, 1, -4) -> [13, 9, 5]
```

The priority key reads only field zero. Equal-priority jobs retain arrival order, even though their identifiers would sort differently.

### 6.2 Backend example: a bounded batch plan

[batch_plan.py](examples/batch_plan.py) validates a positive plain integer batch size and a list of string identifiers. The core loop is:

```python
plan = []
for start in range(0, len(job_ids), batch_size):
    plan.append(tuple(job_ids[start : start + batch_size]))
```

Here `job_ids` and `batch_size` are the validated arguments in the linked function. The list of batches remains editable; each tuple fixes one batch's members. Its string elements are immutable. No deep copy is needed for that deliberately narrow input model.

Observed from the complete script on both runtimes:

```text
batch plan: [('job-a', 'job-b'), ('job-c', 'job-d'), ('job-e',)]
input after later edits: ['replacement', 'job-b', 'job-c', 'job-d', 'job-e', 'job-f']
existing batch plan: [('job-a', 'job-b'), ('job-c', 'job-d'), ('job-e',)]
```

The input must remain stable during construction. The function is eager and uses memory proportional to the identifiers copied into the plan. For an unbounded source, a separate streaming design is needed. Do not generalize this string-only example to mutable job records without revisiting ownership.

### 6.3 Debugging example: attempt before correction

The [tail-selection exercise](practice/README.md#py-blt-040-p03) contains a deliberately broken implementation. Record its effects on the caller, ordering, and empty-input behavior before proposing a fix. No comparison solution is included.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| “Slices are views” | Slice syntax also appears in array libraries | Built-in list slices create shallow outer copies | Compare container and child identities separately |
| “Negative stop always means reverse” | A minus sign suggests direction | The step determines direction | Keep bounds fixed and change step sign |
| “`-0` selects from the end” | It resembles other negative indices | Integer `-0` equals `0` | Evaluate a tail expression when count is zero |
| “Extended assignment can resize” | Ordinary slice assignment can | Non-unit steps require equal replacement length | Compare assignment and deletion on the same stride |
| “A tuple copy must have a new identity” | Mutable copies do | Immutable results may reuse existing objects | Reason from values and contracts, not allocation identity |
| “A tuple containing a list is hashable” | The outer container is immutable | Hashability depends on every element | Try `hash` on the nested tuple |
| “A list loop snapshots contents” | Loop syntax hides the cursor | Structural changes affect later indexed reads | Reconstruct visual 5.2 |
| “A range is consumed after one loop” | It produces values on demand | Iterators consume positions; ranges are reusable | Create two iterators |
| “Equal ranges have equal arguments” | Constructors look like records | Equality concerns represented values | Use the two stops in EXP-02 |
| “Small shallow size proves constant total bytes” | `getsizeof` looks comprehensive | Referenced objects are excluded | Read the memory limit in EXP-02 |

## 8. Complexity and performance

Let `n` be input length and `k` selected length. These are cost models, not timings. Assume constant-cost element operations unless stated otherwise.

| Operation or design | Typical cost | Qualification |
|---|---:|---|
| List indexing or `len` | O(1) | CPython sequence metadata and direct indexing |
| List append | Amortized O(1) | An individual growth can move O(n) references |
| Front insertion or removal | O(n) | Remaining references shift |
| List slice / full shallow copy | O(k) / O(n) | Copies references, not complete descendant graphs |
| List concatenation | O(n + k) | Repeated growing concatenation can accumulate quadratic work |
| List membership / `index` | O(n) comparisons worst case | User equality may be expensive or have side effects |
| Sorting a list | O(n log n) worst-case comparisons | CPython's adaptive sort benefits from existing runs; keys/comparisons add cost |
| Range description / plain integer membership | Independent of represented item count | Integer magnitude still affects arithmetic and storage |
| Iterate or materialize a range | O(n) work; materialization adds O(n) slots | Compact description does not make traversal free |
| Batch plan | O(n) work and output references | Plus batch headers and a temporary slice for the current batch |

The list estimates follow CPython 3.14.7's reference-array operations: `list_resize`, `list_slice_lock_held`, and `list_concat_lock_held` in [listobject.c](https://github.com/python/cpython/blob/v3.14.7/Objects/listobject.c). They are implementation-aware reasoning, not language promises about elapsed time. Sorting details are in [Sorting Techniques](https://docs.python.org/3.14/howto/sorting.html). Range's integer-membership guarantee does not establish a fast path for every object that compares equal to an integer.

For frequent operations at both ends, compare [`collections.deque`](https://docs.python.org/3.14/library/collections.html#collections.deque): end operations avoid list-wide shifting, while middle indexed access is slower. A queue abstraction and concurrency policy are separate decisions.

## 9. Production relevance and trade-offs

- **Ownership:** specify whether a returned sequence is live, an independent outer container, or a snapshot of immutable values. “Returns a tuple” is insufficient for nested records.
- **Boundaries:** choose whether APIs reject bad offsets or intentionally clip. Python slicing's permissiveness need not be the service contract.
- **Memory:** check cardinality before materializing large progressions. An in-memory batch plan suits bounded work, not an unbounded stream.
- **Ordering:** make sort keys explicit. Preserve meaningful arrival order among ties instead of relying on incidental record fields.
- **Failure:** do not assume a failed mutating operation restored the previous state. Validate inputs and document partial-effect boundaries.
- **Concurrency:** this unit's copies and tuples do not establish a synchronization protocol. The batch example explicitly requires stable input during its call.

`PY-BLT-050` owns mapping behavior; `PY-BLT-070` owns comprehensions and unpacking; `PY-BLT-080` owns deeper equality and hashing contracts; `PY-BLT-090` broadens built-in protocols and complexity. This unit does not change their scope or progress.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---|---|---|
| List/tuple indexing, slicing, mutation boundaries | Language and built-in contracts | Before 3.11 | Same forms | All runnable examples execute unchanged on both tested versions |
| Range slicing, negative indexing, fast integer membership | Built-in contract | 3.2 | Same forms | Integer arithmetic costs remain relevant |
| Range equality by represented values | Built-in contract | 3.3 | Same form | Ordering still unsupported |
| `list.copy()` and `list.clear()` | Built-in contract | 3.3 | Same methods | Copy remains shallow |
| Built-in generic annotations such as `list[str]` | Typing syntax | 3.9 | Same forms | Annotations do not validate input at runtime |
| `zip(..., strict=True)` in visual verification | Standard library | 3.10 | Same form | Used only to detect mismatched test result counts |
| List growth, shallow byte counts, length overflow limit | CPython / platform | Version-labelled observation | Verify on target runtime | Neither exact byte sizes nor growth patterns are universal |

The canonical baseline remains Python 3.14; `.python-version` is unchanged. Actual execution used CPython **3.14.7** and **3.11.16**, not an inferred syntax-compatibility claim. The [3.11 sequence documentation](https://docs.python.org/3.11/library/stdtypes.html#sequence-types-list-tuple-range) was checked alongside 3.14. No alternative interpreter or free-threaded runtime was tested.

## 11. Practice brief

All exercises start unsolved. Ask for one hint at a time; retain predictions, attempts, failed tests, and corrections.

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-BLT-040-P01` | Predict / Explain | 2 | E | [Practice](practice/README.md#py-blt-040-p01) |
| `PY-BLT-040-P02` | Implement / Test | 3 | C+E | [Practice](practice/README.md#py-blt-040-p02) |
| `PY-BLT-040-P03` | Debug | 3 | D+E | [Practice](practice/README.md#py-blt-040-p03) |
| `PY-BLT-040-P04` | Review / Design | 4 | E+D | [Practice](practice/README.md#py-blt-040-p04) |
| `PY-BLT-040-P05` | Experiment | 3 | (X)+E | [Practice](practice/README.md#py-blt-040-p05) |

## 12. Interview prompts

Ask one at a time and wait for the learner's answer. These are prompts, not completed interview evidence.

1. How do you choose between a list, tuple, and range for a batch dispatcher?
2. How can two equal-looking copies have different mutation behavior?
3. Why can changing a slice's omitted stop to `-1` change everything it selects?
4. What can happen between the lookup and store in augmented assignment?
5. When does a tuple fail to be a safe immutable record or a hashable key?
6. What does constant-time range membership mean, and which costs does it leave out?
7. How would you review a function that deletes list items while iterating over that list?

A strong answer connects reference identity, position normalization, supported operations, input assumptions, and production ownership. Identify the first missing reasoning step before giving a correction.

## 13. Closed-book revision cues

1. Draw a shallow copy and label exactly which objects are new.
2. Reconstruct default bounds for both step signs.
3. Explain why an extended slice replacement can fail while deletion succeeds.
4. Distinguish a tuple's fixed slots from its children's mutability and hashability.
5. Reconstruct the two-stage failure in the tuple augmented-assignment probe.
6. Explain a sliced range using positions first, then values.
7. State the batch example's memory and concurrency limits.

## 14. Authoritative sources

Accessed 2026-08-30. Explanations, diagrams, code, and practice scenarios are original. Sources were read for the specific contracts below.

1. [Python 3.14 — Built-in Types](https://docs.python.org/3.14/library/stdtypes.html#sequence-types-list-tuple-range): sequence operations, mutation, tuple hashability, and ranges.
2. [Python 3.14 — Data model](https://docs.python.org/3.14/reference/datamodel.html#slice.indices): object/reference boundaries, sequences, and `slice.indices`.
3. [Python 3.14 — Expressions](https://docs.python.org/3.14/reference/expressions.html#slicings): tuple syntax, subscriptions, slices, and value comparisons.
4. [Python 3.14 — Simple statements](https://docs.python.org/3.14/reference/simple_stmts.html#augmented-assignment-statements): augmented assignment evaluation and storage.
5. [Python 3.14 — `copy`](https://docs.python.org/3.14/library/copy.html): shallow/deep copies, memoization, and customization limits.
6. [Python 3.14 — Programming FAQ](https://docs.python.org/3.14/faq/programming.html#how-do-i-create-a-multidimensional-list): repeated mutable children.
7. [Python 3.14 — Sorting Techniques](https://docs.python.org/3.14/howto/sorting.html): key functions, stability, and adaptive sorting.
8. [Python 3.14 — `collections.deque`](https://docs.python.org/3.14/library/collections.html#collections.deque): end-operation and indexing trade-offs.
9. [Python 3.14 — `sys.getsizeof`](https://docs.python.org/3.14/library/sys.html#sys.getsizeof): shallow measurement limitations.
10. [CPython v3.14.7 — `Objects/listobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/listobject.c): resizing and reference-copy loops; no source code is reproduced here.
11. [Python 3.11 — Sequence types](https://docs.python.org/3.11/library/stdtypes.html#sequence-types-list-tuple-range): compatibility cross-check.
