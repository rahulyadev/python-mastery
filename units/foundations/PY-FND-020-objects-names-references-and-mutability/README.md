# PY-FND-020 — Objects, names, references, and mutability

[Curriculum entry](../../../CURRICULUM.md#py-fnd-020) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-FND-020`

## Physical Notebook Core

### Problem this concept solves

Python code becomes difficult to predict when we imagine that a variable is a box containing its own value. The useful questions are instead: which object does each name currently refer to, which references are shared, and did an operation mutate an existing object or bind a target to another object?

### One-sentence mental model

> A name is a binding to an object; assignment changes bindings, mutation changes an object visible through every alias, and copying creates new object-graph nodes according to an explicit depth policy.

### One important visual

```text
1. Alias                         2. Mutate through b

a ──┐                            a ──┐
    ├──> L1 ["queued"]               ├──> L1 ["queued", "running"]
b ──┘                            b ──┘

3. Rebind b                     4. Copy a nested graph

a ─────> L1 ["queued", ...]     shallow root S ──> nested N <── original O
b ─────> L2 ["queued", ...,     deep root D ─────> nested N2
                "done"]

name ──> object                 arrow = reference, not embedded copy
```

#### How to read this visual

Read the numbered stages. In stages 1 and 2, `a` and `b` are two names for list object `L1`, so mutation is shared. In stage 3, rebinding moves only `b` to a new list `L2`. In stage 4, a shallow copy creates a new outer object but keeps the nested reference, whereas a deep copy recursively creates a separate nested object.

#### Key insight

Aliasing is a property of the reference graph, not of a variable declaration. Predict behavior by drawing names and container slots as arrows, then distinguish an arrow change from an object change.

#### Simplification or limitation

This is a language-level conceptual graph, not a literal memory-layout diagram. It omits namespaces, reference counts, garbage-collector internals, custom copying hooks, and concurrency; later units own those mechanisms.

### Governing rules or invariants

1. Every object has an identity, a type, and a value; identity and type do not change during that object's lifetime.
2. Assignment evaluates an expression and binds a target to the resulting object; ordinary assignment does not implicitly copy that object.
3. Mutating an object is observable through all references to it; rebinding one name does not rebind any other alias.
4. `is` asks whether two expressions produce the same object; `==` asks for the type-defined notion of equal value.
5. Shallow copy duplicates one compound object and reuses its descendants; deep copy recursively follows the graph while preserving graph relationships through memoization.

### Minimal example

```python
primary = ["queued"]
alias = primary

alias.append("running")       # mutate L1
print(primary)                # ['queued', 'running']

alias = [*alias, "done"]      # create L2, then rebind alias
print(primary)                # ['queued', 'running']
print(alias)                  # ['queued', 'running', 'done']
print(primary is alias)       # False
```

Expected reasoning:

1. `alias = primary` makes a second binding to the same list; it does not create another list.
2. `append` changes that shared list, so `primary` observes the new element.
3. The list display creates a new list and assignment moves only the `alias` binding to it.

### One failure or misconception

**Mistake:** “Passing a list into a function copies it, so the function cannot affect the caller unless it returns the list.”

**Correction:** Argument evaluation supplies an object to parameter binding. A parameter can therefore alias the caller's mutable object. Mutating through the parameter reaches the caller; rebinding the parameter remains local to that call.

### Important trade-offs

- Shared mutable objects avoid copying and can model intentional collaboration, but they require a clear ownership and mutation contract.
- Defensive copies isolate state, but their time, memory, and semantic depth must match the supported object graph.
- Immutable representations make sharing easier to reason about, but an “update” usually constructs another object and may require conversion at boundaries.
- `deepcopy` is convenient for some graphs, but explicit schema-aware copying is often clearer and less likely to duplicate resources or intentionally shared state.

### Interview-revision cues

- Draw: names and container positions as arrows to objects; never draw a variable as the object itself.
- Predict: for each statement, say “new object,” “mutation,” or “rebinding” before giving the output.
- Defend: choose no copy, shallow copy, deep copy, or an immutable/schema copy at an API boundary and state who owns later mutation.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Foundations and execution |
| Canonical ID | `PY-FND-020` |
| Learning outcome | Reason precisely about objects, names, bindings, identity, type, value, references, mutability, aliasing, and copying |
| Hard prerequisites | `PY-FND-010` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D2 |
| Scope | Language |
| Size | L |
| Evidence profile | E+C+D+(X) |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4 on Linux x86_64 |
| Last source audit | 2026-08-29 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Trace names, parameters, attributes, and container entries as bindings or references to objects, separating identity, type, and value.
2. Predict whether assignment, augmented assignment, a method call, slicing, or copying preserves identity, creates aliases, mutates existing state, or rebinds a target.
3. Diagnose accidental shared mutation in nested structures and choose a justified ownership or copy policy for a Python API.

Required evidence:

- Reconstruct the object-graph mental model closed-book and explain mutation versus rebinding using one original trace.
- Complete a prediction or implementation exercise and pass deterministic tests covering a nested mutable object and at least one immutable boundary.
- Debug an alias leak without trial-and-error, identify the first shared reference that violates the ownership contract, and explain why the correction has the intended copy depth.
- Optionally record a runtime experiment about identity reuse or copying, with its implementation-specific limitations stated explicitly.

Initialization and publication create a tested learning scaffold; they do not constitute learner evidence and do not advance the `Not started` learning state.

## 2. Prerequisite bridge

`PY-FND-010` has a `Draft` note but no recorded learning evidence. The bridge below is sufficient to read this unit accurately; it does not complete the prerequisite.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | [`PY-FND-010`](../PY-FND-010-python-syntax-and-execution/README.md) | Supplies expression evaluation, statements, function calls, and the distinction between running a script and inspecting an expression interactively | A Python expression produces an object. An assignment statement binds its target after evaluating the right-hand expression; a call evaluates its arguments before binding them to parameters. Indentation determines which statements execute in a block. |

Recommended prerequisite action: reconstruct the guarded-script example in `PY-FND-010` before attempting this unit's debugging exercise.

## 3. Vocabulary and professional English

### Binding

| Item | Content |
|---|---|
| Pronunciation | BYN-ding |
| Simple English meaning | A connection that associates one thing with another |
| Hindi cue | नाम और object का संबंध |
| Meaning in this Python context | The association from a name or assignment target to an object |

Natural examples:

1. The assignment creates a binding from `jobs` to the new list.
2. Rebinding `jobs` does not mutate the old object.
3. Deleting a name removes a binding, not necessarily the object.
4. **Interview:** “The parameter binding initially refers to the same list as the caller's argument.”
5. **Engineering discussion:** “The cache binding is stable, but the dictionary it exposes remains mutable.”

### Alias

| Item | Content |
|---|---|
| Pronunciation | AY-lee-us |
| Simple English meaning | Another name for the same thing |
| Hindi cue | उसी object का दूसरा नाम |
| Meaning in this Python context | A second reference through which the same object can be reached |

Natural examples:

1. The two list entries are aliases for one dictionary.
2. A shallow copy removed the outer alias but preserved the nested alias.
3. Returning internal storage created an alias across the API boundary.
4. **Interview:** “I would draw the aliases before predicting the mutation.”
5. **Engineering discussion:** “This method returns an owned snapshot so callers cannot alias our mutable state.”

### Mutation

| Item | Content |
|---|---|
| Pronunciation | myoo-TAY-shun |
| Simple English meaning | A change to something that already exists |
| Hindi cue | उसी object में बदलाव |
| Meaning in this Python context | A type-supported change to an existing object's value while its identity remains the same |

Natural examples:

1. `append` performs a mutation on the list.
2. String concatenation is not string mutation because strings are immutable.
3. The test checks whether mutation leaks back to the caller.
4. **Interview:** “The operation preserves list identity, so every alias observes the mutation.”
5. **Engineering discussion:** “Mutation is allowed only while the request builder exclusively owns the object.”

### Shallow

| Item | Content |
|---|---|
| Pronunciation | SHA-loh |
| Simple English meaning | Affecting only the surface or first level |
| Hindi cue | केवल ऊपरी स्तर तक |
| Meaning in this Python context | A copy that creates a new outer compound object but reuses references to its immediate contents |

Natural examples:

1. A shallow list copy has a new list identity.
2. Its nested dictionaries remain shared.
3. A shallow copy is enough when all descendants are immutable.
4. **Interview:** “The root is independent, but the nested list still aliases the original.”
5. **Engineering discussion:** “The schema is two levels deep, so we copy each supported child explicitly instead of assuming a shallow copy is sufficient.”

## 4. Deep explanation

### 4.1 Why the mechanism exists

Python programs constantly connect objects: a name refers to a list, a dictionary slot refers to a request object, an instance attribute refers to a collaborator, and a function parameter refers to an argument object. Reusing references makes composition and function calls practical. It also means that state can be reached by more than one path.

The “variable as a box” model hides this fact. It predicts that `second = first` duplicates a value and then needs special exceptions for lists, parameters, and nested containers. The binding model has one rule: evaluate an expression to obtain an object, then make the target refer to it. Whether later behavior looks shared depends on object identity, mutability, and the graph of references.

### 4.2 Objects: identity, type, and value

The Python 3.14 Language Reference states that every object has an identity, a type, and a value. Identity and type do not change during the object's lifetime. The type determines supported operations and mutability; the value is the type-defined state relevant to behavior. See [Data model — Objects, values and types](https://docs.python.org/3.14/reference/datamodel.html#objects-values-and-types).

Keep the three questions separate:

| Axis | Useful question | Common probe | Boundary |
|---|---|---|---|
| Identity | Are these the very same object? | `left is right`, sometimes `id(obj)` for diagnostics | Numeric `id()` values have no business meaning and may be reused after an object's lifetime |
| Type | Which operations and value domain apply? | `type(obj)`, usually protocol-oriented checks in production code | Exact-type checks can reject valid subtype or protocol behavior |
| Value | What state or abstract value does this type expose? | Representation, attributes, operations, and `==` where defined | Python provides no universal “get the whole value” operation |

For CPython, the current documentation identifies `id(x)` with the object's memory address, but labels that fact as a CPython implementation detail. Portable reasoning needs only the identity guarantee while the object is alive. Do not infer allocation order, object lifetime, or semantic equality from address-shaped integers.

Identity comparison and value comparison are distinct operations. `x is y` is true exactly when both expressions produce the same object. `x == y` invokes the type's equality behavior and can be true for distinct objects. See [Expressions — Identity comparisons](https://docs.python.org/3.14/reference/expressions.html#is-not) and [Value comparisons](https://docs.python.org/3.14/reference/expressions.html#value-comparisons).

```python
left = [1, 2]
right = [1, 2]

assert left == right
assert left is not right
```

Use identity intentionally for singleton sentinels such as `None`. Do not use `is` for numbers or strings merely because a particular interpreter run happens to reuse an immutable object. The data model explicitly allows implementations to reuse objects for equal immutable values.

### 4.3 Assignment binds targets

An assignment statement evaluates its right-hand expression and assigns the single resulting object to its targets. An identifier target binds its name; an attribute or subscription target delegates the state change to the owning object. The language reference therefore describes assignment as both rebinding names and modifying attributes or items of mutable objects. See [Simple statements — Assignment statements](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements).

```python
settings = {"regions": ["ap-south"]}  # bind name to dictionary
alias = settings                       # bind second name to same dictionary
settings["enabled"] = True             # ask dictionary to set an item
settings = {"regions": []}            # rebind only settings
```

The first two lines establish two paths to one dictionary. The subscription assignment mutates that dictionary. The last line creates another dictionary and changes one binding; `alias` still reaches the first dictionary.

Multiple assignment does not introduce hidden copying:

```python
first = second = []
```

The list display is evaluated once, and the resulting single list is assigned to both targets. By contrast, `first = []; second = []` evaluates two list displays and produces two distinct lists.

`del name` removes the binding from the relevant namespace. It is not a command to destroy the object. The object may remain reachable through aliases, containers, frames, or implementation facilities; lifetime and collection belong to later memory units.

### 4.4 Mutation, rebinding, and calls

Mutation changes an existing mutable object's value. Rebinding changes which object a target denotes. The syntax alone does not always settle which occurred: the object's type participates.

An augmented assignment evaluates its target once and may perform the operation in place. For a list, `items += more` normally mutates and preserves list identity. A tuple cannot mutate, so `items += more` creates a tuple result and rebinds the target. The language contract says in-place behavior occurs when possible; it does not define `+=` as universally mutating. See [Augmented assignment statements](https://docs.python.org/3.14/reference/simple_stmts.html#augmented-assignment-statements).

```python
numbers = [1]
list_alias = numbers
numbers += [2]
assert numbers is list_alias       # list changed in place

coordinates = (1,)
tuple_alias = coordinates
coordinates += (2,)
assert coordinates is not tuple_alias  # name rebound to a new tuple
```

Function calls follow the same model. Argument expressions are evaluated before the call, and parameter names are bound to the supplied objects. This is often described as **call by sharing** or **call by object reference**. Those labels are secondary; the predictive rule is:

1. the caller evaluates the argument expression;
2. the callee's parameter initially refers to that resulting object;
3. mutation through the parameter reaches every alias;
4. rebinding the parameter changes only that local binding.

| Step | Event in `mutate_then_rebind(caller)` | Relevant state |
|---:|---|---|
| 1 | Caller evaluates `caller` | Argument is list `L1` |
| 2 | Parameter `statuses` binds; `local = statuses` runs | `caller`, `statuses`, and `local` refer to `L1` |
| 3 | `local.append("running")` runs | `L1` changes; all three paths observe it |
| 4 | `local = [*local, "done"]` runs | new list `L2` is created; only `local` moves to `L2` |
| 5 | Function returns | caller still refers to mutated `L1`; returned snapshots describe both states |

Default argument objects add a time boundary: defaults are evaluated once when the function definition executes, not once per call. A mutable default can therefore be shared across calls that omit the argument. The expressions reference documents this call behavior under [Calls](https://docs.python.org/3.14/reference/expressions.html#calls). Prefer an explicit sentinel and create the mutable object inside the call when each call needs fresh ownership:

```python
def collect(item: str, bucket: list[str] | None = None) -> list[str]:
    owned = [] if bucket is None else bucket
    owned.append(item)
    return owned
```

This pattern does not copy a supplied list; it deliberately mutates it. An API should document that distinction rather than relying on the type annotation to imply ownership.

### 4.5 Containers and graph depth

A container holds references to other objects. Its mutability concerns which immediate objects it refers to, not whether every descendant can change. Consequently, a tuple can be immutable while containing a mutable list:

```python
inner = ["reader"]
policy = (inner,)
inner.append("writer")
assert policy == (["reader", "writer"],)
```

The tuple still refers to the same immediate list; no tuple slot was replaced. The descendant list changed. “Tuple is immutable” must not be expanded into the false claim that everything reachable from a tuple is deeply immutable. This distinction is specified in [Objects, values and types](https://docs.python.org/3.14/reference/datamodel.html#objects-values-and-types).

Reference graphs can share descendants and contain cycles:

```text
root ──> A ──> shared <── B
         ▲                  │
         └──────────────────┘
```

Copying therefore needs a graph policy, not just a new outer identity.

### 4.6 Assignment, shallow copy, and deep copy

The standard-library copy documentation is explicit: assignment creates a binding and does not copy. For compound objects:

- `copy.copy(obj)` creates a new outer object and inserts references to the original's contents;
- `copy.deepcopy(obj)` recursively copies contents while using a memo table to avoid repeatedly copying the same source object and to handle recursive graphs;
- types can customize these operations with `__copy__` and `__deepcopy__`;
- some runtime or resource-bearing objects are not meaningfully copied.

See [`copy` — Shallow and deep copy operations](https://docs.python.org/3.14/library/copy.html).

```text
original O ──> list N

assignment:    alias ───────> O ──> N
shallow copy:  copy S ───────────> N       (new S, shared N)
deep copy:     copy D ───────────> N2      (new D, usually new N2)
```

#### How to read this visual

Start at each root name and follow the arrows. Assignment adds another path to `O`. Shallow copy creates root `S` but makes its child arrow point to existing `N`. Deep copy creates root `D` and recursively constructs `N2`, subject to type-specific copy behavior and memoized graph relationships.

#### Key insight

“Is it a copy?” is incomplete. Ask which nodes are new, which nodes remain shared, and whether cycles or repeated references must remain repeated in the result.

#### Simplification or limitation

The diagram shows a two-node mutable graph. Real objects can customize copying, contain immutable descendants that are safely reused, own resources that should not be duplicated, or expose state outside ordinary Python attributes.

Deep copy is not automatically the safest choice. It can copy too much, hide an unclear ownership contract, invoke user-defined behavior, consume substantial time and memory, and fail to make external resources independent. The copy documentation itself warns that deep copy can duplicate state intended to remain shared. Prefer the smallest explicit copy that establishes the required ownership.

### 4.7 Choosing an ownership boundary

Use this decision sequence at function, cache, request, and domain-model boundaries:

1. **State ownership:** Who may mutate the object after the call?
2. **Graph shape:** Which descendants are mutable or repeated?
3. **Isolation need:** Must caller mutations be invisible, callee mutations be invisible, both, or neither?
4. **Copy policy:** Borrow the reference, shallow-copy the root, copy known schema levels, deep-copy the graph, or convert to an immutable representation.
5. **Verification:** Test the identity relationships that define the contract, not just current equal values.

| Contract | Suitable technique | Important qualification |
|---|---|---|
| Borrowed read-only view | Keep the reference and avoid mutation | Convention or a read-only interface does not make a mutable runtime object immutable |
| Independent outer collection, shared values | `list.copy()`, `dict.copy()`, slicing, or `copy.copy()` | Nested mutable objects remain aliases |
| Known request schema owned by callee | Explicit comprehensions or constructors per supported field | Schema changes must update the copy logic and tests |
| Independent general object graph | `copy.deepcopy()` when types support its semantics | Audit custom hooks, cycles, resources, cost, and intentionally shared nodes |
| Shareable value object | Immutable types, frozen domain objects, or serialization to a value form | “Frozen” may still contain mutable descendants unless enforced recursively |

## 5. Additional visual models

### Repeated-reference trap

```text
rows = [[0] * 2] * 3

rows[0] ──┐
rows[1] ──┼──> one inner list [0, 0]
rows[2] ──┘

rows[0][0] = 9

rows == [[9, 0], [9, 0], [9, 0]]
```

#### How to read this visual

The inner list display runs once. Sequence repetition copies its reference three times into the outer list, so every row position reaches the same inner list.

#### Key insight

Container size does not reveal object count. Repetition can create many reference positions without creating many referred-to objects.

#### Simplification or limitation

This example uses a mutable inner list to expose aliasing. Repeating references to immutable objects is usually harmless because those objects cannot be mutated, although identity still should not be mistaken for value.

Use a comprehension when independent mutable rows are required:

```python
rows = [[0] * 2 for _ in range(3)]
```

## 6. Worked examples

### 6.1 Mutation followed by rebinding

The runnable [`reference_model.py`](examples/reference_model.py) records stable identity relationships rather than unstable numeric addresses.

```python
def mutate_then_rebind(statuses: list[str]) -> BindingReport:
    local = statuses
    same_object_before = local is statuses

    local.append("running")
    caller_after_mutation = tuple(statuses)

    local = [*local, "done"]
    return BindingReport(
        same_object_before=same_object_before,
        caller_after_mutation=caller_after_mutation,
        local_after_rebinding=tuple(local),
        same_object_after=local is statuses,
    )
```

Prediction before execution:

The parameter and local name initially alias the caller's list, so `append` reaches the caller. The list display creates a new list before rebinding `local`, so the caller never sees `"done"`. List `+=` preserves identity in the companion trace; tuple `+=` cannot mutate its tuple and rebinds instead.

Observed on CPython 3.14.4 with `python examples/reference_model.py`:

```text
same object before mutation: True
caller after mutation: ['queued', 'running']
local after rebinding: ['queued', 'running', 'done']
same object after rebinding: False
list += kept identity: True
list alias observed: ['queued', 'running']
tuple += kept identity: False
tuple alias observed: ('queued',)
rebound tuple: ('queued', 'running')
```

### 6.2 Request ownership at a backend boundary

The runnable [`copy_graphs.py`](examples/copy_graphs.py) includes a schema-aware ownership function:

```python
Request = dict[str, list[str]]


def own_request(payload: Request) -> Request:
    return {field: list(values) for field, values in payload.items()}
```

This contract creates a new dictionary and a new list for every supported field. Later caller mutations do not affect the owned request, and later callee mutations do not affect the caller. It is deliberately narrower than `deepcopy`: the function accepts one known schema, copies exactly its mutable layers, and makes the maintenance point visible when the schema evolves.

Alternatives and trade-offs:

- borrowing `payload` is cheapest but makes future mutation a shared-state concern;
- `payload.copy()` separates only dictionary membership and still shares each list;
- tuple values such as `Mapping[str, tuple[str, ...]]` can express a stronger value-oriented boundary;
- serialization can establish a process or storage boundary, but it is not a drop-in copying primitive and may change types or reject values;
- `deepcopy(payload)` is broader, less explicit, and unnecessary for this closed two-level schema.

Failure modes include a newly added nested mutable field that the copy contract does not cover, a caller passing a subclass with surprising behavior, or a downstream component retaining a mutable reference beyond its documented lifetime. Tests should mutate both sides after the copy and assert independence in both directions.

Observed on CPython 3.14.4 with `python examples/copy_graphs.py`:

```text
shallow root is new: True
shallow nested list is shared: True
deep nested list is new: True
original roles: ['reader', 'writer']
shallow roles: ['reader', 'writer']
deep roles: ['reader', 'auditor']
recursive clone is new: True
recursive clone preserves cycle: True
owned roles after caller mutation: ['reader']
```

### 6.3 Debugging example

Keep the correction hidden until an attempt is recorded.

```python
def build_job(payload: dict[str, object]) -> dict[str, object]:
    job = payload.copy()
    headers = job["headers"]
    assert isinstance(headers, dict)
    headers["trace-id"] = "synthetic-123"
    return job


incoming = {"headers": {"accept": "application/json"}}
created = build_job(incoming)

assert "trace-id" not in incoming["headers"]
```

Before changing code, draw the two dictionary roots and their `"headers"` references. Identify the first assertion about ownership that the implementation violates, then propose the narrowest correction compatible with the supported schema. Do not replace the function with `deepcopy` without first defending that semantic and cost choice.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| `a = b = []` creates two lists | There are two targets | The list expression runs once; both names bind to one list | Check `a is b`, then append through one name |
| `a = []; b = []` may share because both are empty | Equal values look interchangeable | Each mutable list display creates a distinct new list | Check `a == b` and `a is b` separately |
| Equal small integers or strings should be compared with `is` | CPython often reuses immutable objects | Reuse is implementation-dependent; use `==` for value and `is` for deliberate identity/singletons | Construct equal values through different expressions or run another implementation |
| A tuple is deeply immutable | Its own slots cannot be reassigned | A tuple can reference a mutable descendant whose value changes | Put a list in a tuple and mutate the list |
| `+=` always mutates | It looks like one in-place operator | In-place behavior depends on the operand type; immutable operands produce a result and the target is rebound | Compare list and tuple aliases before and after `+=` |
| `outer.copy()` isolates nested state | The outer identity is new | A shallow copy reuses immediate contents | Mutate a nested list and observe both roots |
| `deepcopy` duplicates every reachable occurrence independently | “Deep” sounds like blind recursion | Memoization preserves repeated-reference and cycle relationships within the cloned graph | Deep-copy a self-referential list and assert `clone[0] is clone` |
| `[[0] * 2] * 3` builds independent rows | The result prints like three rows | Repetition places the same inner-list reference three times | Mutate one row and inspect all rows |
| `del alias` destroys the aliased object | The name disappears | Only that binding is removed; other paths can keep the object reachable | Keep a second alias and use it after deletion |
| A `Sequence[str]` annotation makes an argument immutable | The interface omits mutating methods | Type hints do not change the runtime object or ownership | Pass a list, retain another alias, and mutate through it |
| Copying input is validation or sanitization | Both create a new value | Copying preserves structure; it does not establish trust, schema validity, or safe content | Supply an invalid or dangerous value and observe it remains present |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| Bind or rebind one ordinary name | Time `O(1)`, no graph-sized copy | Conceptual and typical implementation cost; namespace implementation details belong to later units |
| Mutate one existing list item | Time `O(1)` | Does not include finding the item or application-level validation |
| Append to a list | Amortized time `O(1)` | Individual growth operations can allocate and copy internal storage |
| Shallow-copy a list or dictionary with `n` immediate entries | Time `O(n)`, extra root storage `O(n)` | Descendant objects are reused, so their sizes are not traversed |
| Deep-copy a graph | Roughly proportional to visited nodes and edges; extra graph-sized storage | Custom methods, immutable reuse, cycles, resources, and type behavior can change the cost or result |
| Explicitly copy `m` fields containing `n` total items | Time and extra storage `O(m + n)` | Makes the supported schema and depth part of the API contract |
| Concatenate immutable sequence content of total length `n` | Time and new storage `O(n)` | An “update” cannot mutate the immutable sequence and must produce a result object |

These are asymptotic reasoning aids, not measurements. No benchmark was run for this unit. Real cost depends on graph shape, allocator behavior, custom copy hooks, object sizes, cache effects, and runtime implementation.

## 9. Production relevance and trade-offs

### Make ownership part of the API

Names such as `borrowed`, `owned`, `snapshot`, and `mutable_builder` can reinforce documentation, but tests and behavior must establish the contract. State whether the function retains the object, mutates it during the call, may mutate it later, or returns internal storage. A type annotation describes acceptable operations and shapes; it does not automatically define aliasing or lifetime.

### Protect state at boundaries, not everywhere

Copying every argument defensively adds cost and can erase intentional sharing. Copy at boundaries where ownership changes: accepting mutable configuration for long-term retention, publishing a cache result, storing an event payload for later use, or returning internal collections. Inside a component with exclusive ownership, direct mutation can be simpler and faster.

### Prefer schema-aware transformations for durable contracts

For request and persistence models, constructing a new validated representation is often better than copying arbitrary caller graphs. It narrows accepted types, makes normalization explicit, and avoids pretending that sockets, locks, sessions, iterators, or other resource-bearing objects can be made independent by recursive copying.

### Test alias behavior deliberately

A test that only checks `result == expected` can miss shared identity. For an ownership boundary, mutate the source after construction, mutate the result, and verify both directions. Add `is` assertions only for identity relationships that are part of the contract; avoid pinning harmless implementation reuse of immutable values.

### Concurrency does not repair unclear ownership

Shared mutation becomes more hazardous when execution can overlap, but a lock is not a substitute for knowing which object is shared. First identify the reference graph and invariant, then choose isolation, immutability, message passing, or appropriate synchronization in the concurrency units.

### Copying is not security

Neither shallow nor deep copy validates untrusted input, removes secrets, limits resource use, or makes executable behavior safe. Validate against an explicit schema and enforce security controls separately.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| Objects have identity, type, and value; assignment binds objects | Language | Python 1.x lineage | Same behavior | Core model is unchanged across the repository's 3.11–3.14 range |
| `is` and `is not` test identity | Language | Python 1.x lineage | Same behavior | Do not substitute them for type-defined value equality |
| Mutable and immutable behavior is determined by type | Language | Python 1.x lineage | Same behavior | An immutable container can still reference mutable descendants |
| Shallow and deep copy through `copy.copy` and `copy.deepcopy` | Standard library | Long-standing | Same APIs | Results can be customized and not every runtime/resource object is copyable |
| `copy.replace(obj, **changes)` | Standard library | Python 3.13 | Use `dataclasses.replace`, named-tuple `_replace`, or a type-specific constructor | Replacement is a targeted new-object operation, not general deep copying |
| `id(x)` is the memory address | CPython | Implementation-specific | Rely only on identity semantics | Not a portable language guarantee; never derive application meaning from the number |
| Reuse or interning of equal immutable objects | Implementation | Implementation- and expression-dependent | Compare values with `==` | Identity observations may differ across versions, builds, interpreters, or execution contexts |
| Immediate reclamation after the last reference disappears | CPython tendency, not language guarantee | Implementation-specific | Release external resources explicitly | Object lifetime and finalization are owned by `PY-MPR-010` |

The runnable unit code uses syntax and public APIs available in Python 3.11. Its observed output was recorded on CPython 3.14.4; the reasoning assertions depend on documented language and standard-library behavior rather than numeric identities or CPython caches.

## 11. Practice brief

Exercises are specified without solutions in [`practice/README.md`](practice/README.md).

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-FND-020-P01` | Predict | 2 | Correct name-and-object graph through aliasing, shallow copy, deep copy, mutation, and rebinding | [`practice/README.md`](practice/README.md#py-fnd-020-p01-trace-the-graph) |
| `PY-FND-020-P02` | Implement | 3 | An explicit two-level ownership boundary with deterministic independence tests | [`practice/README.md`](practice/README.md#py-fnd-020-p02-own-a-request-schema) |
| `PY-FND-020-P03` | Debug | 3 | First violating shared reference identified before correction | [`practice/README.md`](practice/README.md#py-fnd-020-p03-debug-a-snapshot-leak) |
| `PY-FND-020-P04` | Review | 4 | Precise review of identity assumptions, mutable defaults, and exposed internal state | [`practice/README.md`](practice/README.md#py-fnd-020-p04-review-an-alias-prone-api) |
| `PY-FND-020-P05` | Design | 4 | Defensible ownership and copy policy for a backend configuration boundary | [`practice/README.md`](practice/README.md#py-fnd-020-p05-design-an-ownership-contract) |

## 12. Interview prompts

Answer one at a time. Do not reveal a full answer before an attempt.

1. After `a = b = []`, what exact claim can you make about `a is b`, and how is that different from `a == b`?
2. A function appends to a list parameter and then assigns the parameter to a new list. What can the caller observe, and why?
3. Why can a tuple be immutable while a value reachable through it still changes?
4. Predict the identity and value effects of `+=` on aliased lists and aliased tuples without using bytecode terminology.
5. A service copies an incoming dictionary with `.copy()` before retaining it, but caller mutations to nested lists still alter service state. Diagnose the first failed assumption.
6. When would a schema-aware copy be preferable to `deepcopy`, and what new maintenance obligation does it create?
7. How would you test that a returned snapshot does not expose a component's mutable internal state?

A strong answer should eventually demonstrate:

- the binding-and-object-graph mechanism rather than “pass by value versus reference” slogans;
- the language boundary between identity, equality, mutability, reachability, and implementation-specific object reuse;
- an ownership trade-off justified by graph depth, resource semantics, cost, and future mutation.

## 13. Closed-book revision cues

Without reading the note:

1. Define object identity, type, value, binding, reference, alias, mutation, and rebinding in one connected explanation.
2. Reconstruct the four-stage alias → mutate → rebind → copy visual and label every arrow.
3. Predict `a = b = []`, `a = []; b = []`, list `+=`, tuple `+=`, and a tuple containing a list.
4. Explain why a shallow copy fails for one nested request and why deep copy may still be the wrong repair.
5. Design and test an ownership boundary for `dict[str, list[str]]` without using `deepcopy`.
6. State which `id()` and immutable-object-reuse observations are CPython details rather than portable semantics.

## 14. Authoritative sources

Only the following opened sources informed the canonical claims in this unit:

1. [Python 3.14 Language Reference — Data model, “Objects, values and types”](https://docs.python.org/3.14/reference/datamodel.html#objects-values-and-types), Python 3.14.7 documentation, accessed 2026-08-29.
2. [Python 3.14 Language Reference — Simple statements, “Assignment statements” and “Augmented assignment statements”](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements), Python 3.14.7 documentation, accessed 2026-08-29.
3. [Python 3.14 Language Reference — Expressions, “Calls,” “Value comparisons,” and “Identity comparisons”](https://docs.python.org/3.14/reference/expressions.html#calls), Python 3.14.7 documentation, accessed 2026-08-29.
4. [Python 3.14 Standard Library — `copy`, “Shallow and deep copy operations”](https://docs.python.org/3.14/library/copy.html), Python 3.14.7 documentation, accessed 2026-08-29.
