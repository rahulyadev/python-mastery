# PY-FND-030 — Namespaces, scope, and name resolution

[Curriculum entry](../../../CURRICULUM.md#py-fnd-030) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-FND-030`

## Physical Notebook Core

### Problem this concept solves

The same spelling can be bound in several places: one function call, an enclosing function, a module, the built-ins namespace, or a class. Correct reasoning requires knowing which code block owns a binding and which ordered environment a bare name can search.

### One-sentence mental model

> First classify each name from the whole code block; then, when the code runs, resolve a bare-name read through the nearest visible binding—usually Local, Enclosing functions, Global module, then Built-ins.

### One important visual

```text
Source block                 Runtime lookup for build_label()

def outer(request_id):       L  build_label: label ──> "REQ-7"
    prefix = "worker"        E  outer: prefix ───────> "worker"
    def build_label():        G  module: SERVICE ─────> "payments"
        label = ...           B  builtins: len ───────> [built-in function]
        return (...)

         whole-block classification first ──> nearest visible binding later
```

#### How to read this visual

Read left to right. The compiler inspects a complete block to classify its names. At runtime, start at `L` for the currently executing function and move outward only when the name is not local there. `E` can contain more than one enclosing function scope. `G` means the function's defining module, not its caller's module.

#### Key insight

Lookup order alone is insufficient: a later assignment can classify a name as local for the entire function, so an earlier read fails instead of falling through to a global binding.

#### Simplification or limitation

LEGB is a useful function-oriented mnemonic, not a complete diagram of every Python scope. Class bodies, comprehensions, annotation scopes, and dynamic `exec()`/`eval()` have special rules. The arrows are conceptual bindings, not a literal CPython memory or bytecode layout.

### Governing rules or invariants

1. A namespace associates names with objects; a scope is the region in which a binding is directly visible.
2. A binding operation anywhere in a function block normally classifies that name as local throughout the block, unless `global` or `nonlocal` redirects it.
3. A free bare name in a function searches the nearest enclosing function scopes, then the defining module's global namespace, then built-ins.
4. `global` redirects a name to the module namespace; `nonlocal` redirects it to the nearest already-bound enclosing function scope.
5. A class body executes with a new local namespace that becomes class attributes, but ordinary method bodies do not enclose that class namespace.
6. Comprehension iteration targets live in an implicit nested scope and do not leak into the surrounding scope.

### Minimal example

```python
SERVICE = "payments"


def make_label(request_id: str) -> str:
    prefix = "worker"

    def build() -> str:
        local_id = request_id.upper()
        return f"{prefix}:{SERVICE}:{local_id}:{len(local_id)}"

    return build()


print(make_label("req-7"))
# worker:payments:REQ-7:5
```

Expected reasoning:

1. `local_id` is local to `build`; `request_id` and `prefix` are free there and resolve in `make_label`.
2. `SERVICE` resolves in the module namespace, while `len` resolves in built-ins.
3. The caller's namespace is irrelevant: lexical scope follows where `build` was defined, not where it is called.

### One failure or misconception

**Mistake:** “Python reads `timeout` from the global because the assignment comes after the read.”

```python
timeout = 30


def configure():
    print(timeout)  # UnboundLocalError
    timeout = 60
```

**Correction:** The assignment makes `timeout` local for the complete function block. At the `print`, that local binding has no value yet. Use an explicit parameter and return value when practical; otherwise use a correctly placed `global timeout` only when rebinding module state is genuinely intended.

### Important trade-offs

- Explicit parameters and return values make dependencies and state changes visible, but can add plumbing across layers.
- Module globals are convenient for constants and process-wide configuration, but mutable global state couples tests, requests, and concurrency.
- `nonlocal` can encapsulate small state inside a factory, but hidden mutable state still needs lifecycle, reentrancy, and concurrency reasoning.
- Shadowing can keep short scopes readable, but shadowing built-ins or important outer names increases review and debugging cost.

### Interview-revision cues

- Classify: for every name, identify its binding operation and owning block before tracing output.
- Predict: distinguish `NameError` from `UnboundLocalError` and name the exact lookup step that fails.
- Defend: explain why explicit input/output, object state, `nonlocal`, or `global` is the appropriate state boundary.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Foundations and execution |
| Canonical ID | `PY-FND-030` |
| Learning outcome | Reconstruct namespaces and LEGB lookup; use local, global, nonlocal, and class scopes correctly |
| Hard prerequisites | `PY-FND-020` |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D2 |
| Scope | Language |
| Size | M |
| Evidence profile | E+C+D |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4 on Linux x86_64 |
| Last source audit | 2026-08-29 |
| Artifact state | Approved |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Draw the relevant namespaces for a module, function call, nested function, and class body, then distinguish a namespace from a scope and a code block.
2. Classify local, free, global, nonlocal, class, and built-in name references before predicting their runtime resolution or failure.
3. Diagnose shadowing, read-before-local-binding, incorrect `global`/`nonlocal`, and bare-name access from methods, then choose a maintainable state boundary.

Required evidence:

- Reconstruct the two-stage “classify, then resolve” model closed-book and trace one original example containing L, E, G, and B bindings.
- Complete a prediction or implementation exercise with deterministic tests for `global` or `nonlocal` rebinding and at least one shadowing edge case.
- Debug an `UnboundLocalError` or class-scope mistake by identifying the first incorrect binding classification, not by trial-and-error edits.

Initialization and publication create a source-audited, tested scaffold. They do not constitute learner evidence and do not advance the `Not started` learning state.

## 2. Prerequisite bridge

`PY-FND-020` has an `Approved` artifact, but its tracker has no recorded learning evidence. This bridge is sufficient to start accurately; it does not complete the prerequisite.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | [`PY-FND-020`](../PY-FND-020-objects-names-references-and-mutability/README.md) | Supplies the distinction between names, bindings, objects, mutation, and rebinding | A namespace binding is an arrow from a name to an object. Reading a name follows an existing arrow. Assignment to a name changes an arrow in the namespace selected by the scope rules; it does not mutate the previously referenced object. |

Recommended prerequisite action: redraw the alias-and-rebinding visual from `PY-FND-020` before adding namespace boundaries around those arrows.

## 3. Vocabulary and professional English

### Namespace

| Item | Content |
|---|---|
| Pronunciation | NAYM-spays |
| Simple English meaning | A collection in which names identify things |
| Hindi cue | नामों और objects का mapping |
| Meaning in this Python context | A mapping-like association from names to objects for a module, class body, function execution, or other code context |

Natural examples:

1. Importing the module creates its global namespace.
2. Each function call receives its own local bindings.
3. The class-body namespace later supplies the class attributes.
4. **Interview:** “The two spellings are equal, but they belong to different namespaces.”
5. **Engineering discussion:** “Avoid mutating the module namespace during request handling.”

### Scope

| Item | Content |
|---|---|
| Pronunciation | skohp |
| Simple English meaning | The region or range where something applies |
| Hindi cue | जहाँ नाम दिखाई देता है |
| Meaning in this Python context | The textual region in which a binding can be referenced directly by its bare name |

Natural examples:

1. The parameter is in scope throughout the function body.
2. A method does not treat its class namespace as an enclosing lexical scope.
3. The comprehension target has a separate scope.
4. **Interview:** “I would separate the lifetime of the object from the scope of this binding.”
5. **Engineering discussion:** “Narrow scope makes the dependency easier to audit.”

### Shadow

| Item | Content |
|---|---|
| Pronunciation | SHA-doh |
| Simple English meaning | To hide something behind something nearer |
| Hindi cue | पास वाला नाम बाहर वाले को छिपाता है |
| Meaning in this Python context | To bind the same spelling in a nearer scope so bare-name lookup does not reach an outer binding |

Natural examples:

1. The parameter `id` shadows the built-in function.
2. A local `config` shadows the module-level constant.
3. Rename the binding when the shadowing obscures intent.
4. **Interview:** “This is shadowing, not mutation of the outer object.”
5. **Engineering discussion:** “The fixture name shadows the imported helper and makes this failure misleading.”

### Free variable

| Item | Content |
|---|---|
| Pronunciation | free VAIR-ee-uh-buhl |
| Simple English meaning | A referenced name not bound in the current block |
| Hindi cue | current block के बाहर बंधा नाम |
| Meaning in this Python context | A name used by a block whose binding must be resolved from an enclosing environment |

Natural examples:

1. `prefix` is free in the inner function.
2. A free variable is looked up when the function executes.
3. `nonlocal` permits rebinding an eligible free-variable binding.
4. **Interview:** “The free name resolves lexically, not from the caller.”
5. **Engineering discussion:** “This callback silently depends on three free variables, so I would make two of them explicit.”

## 4. Deep explanation

### 4.1 Why namespaces and scopes exist

Programs need to reuse short names without making every binding process-wide. A request handler may have a local `config`, its module may expose a default `config`, and the application may import a different configuration object elsewhere. Namespaces keep those associations separate. Scope rules make a bare occurrence such as `config` deterministic within a code block.

Python's execution model defines modules, function bodies, class definitions, interactive commands, scripts, and strings passed to `eval()` or `exec()` as code blocks. A block executes in a frame. Do not collapse these terms: a **block** is executable program text, a **namespace** holds bindings, a **scope** describes direct visibility, and an **environment** is the set of scopes visible from a block. See [Execution model — Structure of a program](https://docs.python.org/3.14/reference/executionmodel.html#structure-of-a-program) and [Naming and binding](https://docs.python.org/3.14/reference/executionmodel.html#naming-and-binding).

At module level, the local and global namespace are the same mapping. Each ordinary function call has call-specific local bindings, while the function retains the global namespace from the module where the function was defined. `globals()` returns that module namespace even if another module calls the function. See [Built-in functions — `globals()`](https://docs.python.org/3.14/library/functions.html#globals).

### 4.2 Binding classification comes before lookup

Names are introduced by more than `=`. Parameters, function and class definitions, imports, assignment expressions, loop targets, `with ... as`, exception targets, and capture patterns are binding operations. Even a `del name` target counts as a binding for static classification, although execution removes the binding. The complete list and its version-sensitive additions are specified in [Execution model — Binding of names](https://docs.python.org/3.14/reference/executionmodel.html#binding-of-names).

For an ordinary function block, Python can scan the whole block for binding operations. If the block binds `limit`, then `limit` is local throughout that block unless a `global` or `nonlocal` directive applies. Runtime statement order determines when the local acquires a value; it does not change the earlier classification.

```python
limit = 10


def broken() -> int:
    result = limit + 1  # tries the local slot before it has a value
    limit = 20
    return result
```

`broken()` raises `UnboundLocalError`, a subclass of `NameError`. It does not read the module's `limit`. If a name is not classified as local and no visible binding exists anywhere in its environment, a bare-name read raises `NameError`. See [Execution model — Resolution of names](https://docs.python.org/3.14/reference/executionmodel.html#resolution-of-names).

This gives a reliable two-pass reasoning procedure:

1. Mark every binding operation in the current block.
2. Apply any valid `global` and `nonlocal` directives to those spellings.
3. Classify the remaining uses as local or free.
4. Execute statements in order, tracking whether each selected binding exists yet.
5. For a free read, search the visible enclosing environment at that runtime moment.

### 4.3 LEGB as a function lookup mnemonic

For an ordinary nested function, LEGB expands as follows:

| Letter | Search location | Typical bindings | Important boundary |
|---|---|---|---|
| L | Current function call | Parameters, assignments, imports, loop targets | A classified local that is not yet bound raises `UnboundLocalError`; lookup does not continue |
| E | Nearest to farthest enclosing function scopes | Outer parameters and locals referenced by nested functions | Caller locals are not searched; the relationship is lexical |
| G | Defining module namespace | Module assignments, imports, function and class names | Reading needs no declaration; rebinding from an inner block needs `global` |
| B | Associated built-ins namespace | `len`, `str`, `Exception` | A nearer binding with the same spelling shadows the built-in |

The nearest visible binding wins. A nested function can therefore shadow an outer name locally, or read an outer binding as a free variable. Free-variable resolution occurs at runtime: rebinding a visible global before calling a function changes what that later call reads. The function does not copy the global value at definition time. See [Execution model — Interaction with dynamic features](https://docs.python.org/3.14/reference/executionmodel.html#interaction-with-dynamic-features).

LEGB does not mean “search every dictionary in the process.” It excludes caller-local namespaces, unrelated modules, instance attributes, and ordinary class namespaces surrounding method definitions. Attribute lookup such as `service.timeout` is a different operation owned by later object-model units.

### 4.4 Reading, rebinding, and mutation

A function may read a global or enclosing object without a declaration when it does not bind the same name locally:

```python
settings = {"timeout": 30}


def read_timeout() -> int:
    return settings["timeout"]


def mutate_settings() -> None:
    settings["timeout"] = 60
```

`mutate_settings` mutates the dictionary reached through a free global name; it does not rebind `settings`. No `global` statement is needed for that name. This can still be poor API design—scope legality is not an ownership or concurrency guarantee.

By contrast, assignment to a bare identifier normally binds that identifier in the current local namespace. The assignment rules explicitly redirect the target only when its spelling occurs in a `global` or `nonlocal` statement in the same block. See [Simple statements — Assignment statements](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements).

### 4.5 `global` redirects to the module namespace

```python
events_seen = 0


def record_event() -> int:
    global events_seen
    events_seen += 1
    return events_seen
```

`global events_seen` is a parser directive for the entire current block. It does not create a process-wide variable and does not mean “the outermost name anywhere”; it selects the global namespace of the module containing the function. The directive must precede uses or assignments to that spelling in the same block. At module level it has no useful effect. A `global` embedded in separately parsed `exec()` text does not change the block that called `exec()`. See [Simple statements — The `global` statement](https://docs.python.org/3.14/reference/simple_stmts.html#the-global-statement).

Use mutable module state sparingly in backend code. It persists across calls in the process, complicates test isolation, and can be raced by concurrent execution. A configuration constant read from a module is a different design from a request path incrementing a shared module counter.

### 4.6 `nonlocal` redirects to an enclosing function binding

```python
from collections.abc import Callable


def make_counter(start: int) -> Callable[[], int]:
    count = start

    def increment() -> int:
        nonlocal count
        count += 1
        return count

    return increment
```

`nonlocal count` selects the nearest eligible binding in an enclosing function scope. The name must already be bound in some such scope; it cannot target only a module global, and a missing binding is a compile-time `SyntaxError`. Like `global`, it applies to the entire block and must precede conflicting uses. See [Simple statements — The `nonlocal` statement](https://docs.python.org/3.14/reference/simple_stmts.html#the-nonlocal-statement).

Each `make_counter` call creates independent enclosing state. This is useful for a small factory-local state machine, but `nonlocal` is not automatically thread-safe and can hide dependencies. Closures and late binding receive deeper treatment in `PY-FIT-040`.

### 4.7 Class bodies are executable but are not ordinary enclosing scopes for methods

A class statement executes its body using a newly created local namespace and the original global namespace. When the body completes, the namespace is saved and used to form the class attribute dictionary; then the class object is bound in the surrounding namespace. See [Compound statements — Class definitions](https://docs.python.org/3.14/reference/compound_stmts.html#class-definitions).

```python
LABEL = "module"


class Policy:
    LABEL = "class"
    copied_during_body = LABEL  # class-body local lookup: "class"

    def bare(self) -> str:
        return LABEL             # method free name: module value

    def qualified(self) -> str:
        return self.LABEL        # attribute lookup: class value
```

Names bound in the class body do not become lexical enclosing bindings for ordinary methods, comprehensions, or generator expressions inside the class block. Access class or instance state explicitly through `self`, `cls`, or a known class object. Python 3.14 annotation scopes are a documented exception and are discussed only as a version boundary here. See [Execution model — Resolution of names](https://docs.python.org/3.14/reference/executionmodel.html#resolution-of-names).

### 4.8 Comprehensions and short-lived bindings

Except for the iterable expression in the leftmost `for` clause, a comprehension executes in an implicit nested scope. Its iteration targets therefore do not leak:

```python
item = "outer"
doubled = [item * 2 for item in (1, 2, 3)]

assert item == "outer"
assert doubled == [2, 4, 6]
```

The leftmost iterable is evaluated in the enclosing scope before being passed into the implicit scope. This distinction matters when that expression has a failure or side effect. See [Expressions — Displays for lists, sets and dictionaries](https://docs.python.org/3.14/reference/expressions.html#displays-for-lists-sets-and-dictionaries).

Other constructs may bind in the surrounding block rather than creating a general block scope: an `if`, `for`, `with`, or `try` suite does not by itself give ordinary assigned names a new lexical scope. Exception target cleanup and pattern-binding behavior add lifetime details, but they do not turn those suites into general nested namespaces.

### 4.9 Inspect namespaces without treating inspection as assignment syntax

- `globals()` returns the dictionary implementing the current module namespace.
- `locals()` returns a mapping representing current local bindings, but its write-through behavior depends on the kind of scope.
- `vars(obj)` returns `obj.__dict__` when the object exposes one; with no argument it behaves like `locals()`.

In optimized scopes such as functions, Python 3.13 and later define `locals()` calls as fresh snapshots whose edits do not write back to actual local or nonlocal bindings. At module and class scope, the mapping behavior differs. Use these tools for inspection and carefully designed dynamic APIs, not to evade ordinary assignment or declarations. See [Built-in functions — `locals()`](https://docs.python.org/3.14/library/functions.html#locals) and [`vars()`](https://docs.python.org/3.14/library/functions.html#vars).

### 4.10 Execution sequence

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Parse and compile a function block | Binding operations classify local, free, global, and nonlocal spellings for the whole block |
| 2 | Define the function | The function object retains its code and defining module's global namespace; the body does not run yet |
| 3 | Call the function | A new call-local environment is created and parameters are bound |
| 4 | Execute a bare-name read | Use the precomputed classification; read the selected local or search the visible enclosing environment |
| 5 | Execute an assignment | Bind in the classified namespace, or mutate an attribute/item when the assignment target is not a bare name |
| 6 | Return from the call | Ordinary call-local bindings cease to be directly accessible; reachable objects and captured state may outlive the call |

## 5. Additional visual models

### Static classification versus runtime state

```text
timeout = 30                    compiler view of configure:

def configure():               timeout = local name (assignment exists)
    before = timeout    ──────> before  = local name
    timeout = 60

runtime, first statement:
read local timeout ──> no binding yet ──> UnboundLocalError
                         X no fallback to module timeout
```

#### How to read this visual

Read the source first, then the compiler classification, then the runtime read. The assignment is textually later but still controls classification for the complete function.

#### Key insight

`UnboundLocalError` is not a failed search through all LEGB levels. It is a read from a selected local binding before that binding has a value.

#### Simplification or limitation

This is a language-level reasoning model. It does not show symbol-table flags, code-object fields, bytecode instructions, frames, or CPython's internal storage; those belong to later CPython and memory-model units.

### Class namespace boundary

```text
module namespace                 class statement executes
LABEL ──> "module"              temporary class namespace
Policy ──> class object ◀──────  LABEL ──> "class"
                                   │
                                   └── becomes Policy.LABEL

Policy().bare():       bare LABEL ─────────────> module LABEL
Policy().qualified():  self.LABEL ─> attribute lookup ─> Policy.LABEL
```

#### How to read this visual

Follow the class-body namespace into the class object, then compare the two method reads. The bare name follows lexical name resolution; the qualified expression invokes attribute lookup.

#### Key insight

A class attribute is not an enclosing lexical variable for an ordinary method merely because the method is written inside the class statement.

#### Simplification or limitation

The diagram omits inheritance, descriptors, metaclasses, `__class__` cells, and annotation-scope exceptions. It distinguishes name lookup from attribute lookup without attempting to specify the latter.

## 6. Worked examples

### 6.1 Local, enclosing, global, built-in, and shadowed names

Run [examples/name_resolution.py](examples/name_resolution.py):

```bash
python units/foundations/PY-FND-030-namespaces-scope-and-name-resolution/examples/name_resolution.py
```

Prediction before execution:

- the report reads one value from each LEGB level;
- a deliberately local `len` returns `-1`, while explicit `builtins.len` returns `3`;
- a later assignment causes the earlier `DEFAULT_TIMEOUT` read to report `UnboundLocalError`.

Observed result on the initially tested runtime:

```text
local: REQ-7
enclosing: worker
global: payments
builtin len: 5
shadowed len: -1
builtins.len: 3
read-before-bind failure: UnboundLocalError
```

### 6.2 Backend-oriented state boundaries

Run [examples/rebinding.py](examples/rebinding.py). It contrasts a process-module counter using `global`, two independent factory counters using `nonlocal`, explicit class-attribute access, and a non-leaking comprehension target.

The example does not recommend a global counter for production metrics. Its purpose is to expose the binding target. A backend service should normally place shared state behind an explicit component with a defined lifecycle, synchronization policy, and test reset boundary. A small `nonlocal` counter can be appropriate inside a short-lived adapter or test helper, but an object often communicates a larger stateful contract more clearly.

### 6.3 Debugging example

Keep the correction hidden until the learner attempts it:

```python
retry_limit = 3


def apply_override(raw: str | None) -> int:
    if raw is not None:
        retry_limit = int(raw)
    return retry_limit
```

Before editing, classify `retry_limit`, predict both `apply_override("5")` and `apply_override(None)`, and explain why only one path initializes the selected binding. Then choose whether the value is input, intentionally global state, or enclosing state; the correction must express that ownership decision rather than merely suppress the exception.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| “LEGB always falls through after a missing local value” | LEGB is taught as a simple search list | A classified but unbound function local raises `UnboundLocalError`; it does not fall through | Put a read before a later assignment in one function |
| “Only `=` binds a local name” | Assignment is the most visible binder | Parameters, imports, definitions, loop/`as`/pattern targets, assignment expressions, and even `del` classification can bind | Mark every binding construct before tracing |
| “Reading a global requires `global`” | `global` sounds like an access declaration | Free reads can resolve globally; `global` is needed to redirect bare-name binding | Compare reading a module dictionary with rebinding its name |
| “Mutating a global object and rebinding its name are the same” | Both change later observations | Item/attribute mutation acts on an object; bare-name assignment selects a namespace binding | Compare `settings["x"] = 1` with `settings = {}` |
| “`nonlocal` means any scope outside this one” | The word suggests all outer scopes | It targets the nearest existing eligible enclosing-function binding, not merely a module global | Compile a nested function with `nonlocal missing` |
| “A method sees class variables as enclosing locals” | The method is textually inside the class body | Ordinary method bare-name lookup skips the class namespace; use `self.name`, `cls.name`, or `Class.name` | Give module and class bindings different values |
| “`for` and `if` always create local scopes” | Many languages use block scope | Ordinary suites do not create general lexical scopes; comprehensions do create an implicit scope | Compare a loop target with a comprehension target |
| “Changing `locals()` changes optimized function locals” | The return value looks like a dictionary | On current Python, function-scope `locals()` is a snapshot with no write-back | Edit the returned mapping and read the local normally |
| “Shadowing `len` changes the built-in globally” | The call now behaves differently | A nearer binding hides the built-in only for applicable lexical resolution | Compare `len(...)` with `builtins.len(...)` |

## 8. Complexity and performance

The language specification defines resolution semantics, not Big-O guarantees for every namespace representation. Avoid interview claims such as “all Python variable lookup is O(1).” CPython commonly uses optimized local storage and dictionary-like global/built-in namespaces, but exact opcodes, caches, and costs are implementation- and version-specific.

| Operation or design | Typical cost concern | Qualification |
|---|---:|---|
| Local or enclosing bare-name read | Small fixed runtime overhead in ordinary code | Exact storage and instruction strategy are implementation details |
| Global then built-in read | May check more than one namespace and runtime cache | Language guarantees search order, not a numeric latency bound |
| Explicit parameter plumbing | More call-interface surface | Usually improves dependency visibility and testability |
| Mutable module state | Low syntactic overhead, high coordination cost | Reset, isolation, concurrency, and lifecycle dominate micro-cost |
| Closure state via `nonlocal` | Compact private state | Captured lifetime and synchronization can matter more than lookup speed |
| Repeated namespace introspection | Allocations or mapping work may occur | `locals()` behavior varies by scope kind and Python version |

Optimize architecture before lookup micro-cost. If a hot path genuinely depends on name access, benchmark the real workload on the deployed Python version and implementation; do not generalize from disassembly or a single timing.

## 9. Production relevance and trade-offs

- **Configuration:** Reading immutable module constants is often clear. Runtime-reloadable configuration should usually be an explicit dependency or owned service rather than scattered global rebinding.
- **Testing:** Mutable globals and hidden `nonlocal` state can leak between tests. Expose construction and reset boundaries, and restore any deliberately patched binding.
- **Concurrency:** Scope controls visibility, not atomicity. `global` and `nonlocal` do not synchronize shared mutation across threads, tasks, or processes.
- **Readability:** Avoid shadowing built-ins such as `id`, `type`, `list`, and `len` when the surrounding code may need their ordinary meaning.
- **API design:** Prefer parameters and returned values for data flow; prefer instance state when behavior and lifecycle belong together; reserve `global` and `nonlocal` for small, explicit contracts.
- **Observability:** Namespace inspection can help diagnostics, but logging an entire `globals()` or `locals()` mapping can leak secrets and unrelated private data. Select safe fields explicitly.
- **Security:** Supplying altered namespaces to `exec()` or `eval()` is not a sandbox. Dynamic execution has separate security and code-injection concerns.
- **Maintainability:** A legal lookup can still be a bad dependency. Reviewers should ask who owns the state, how long it lives, and which code is allowed to change it.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| Lexically nested function scopes | Language | 2.2 | Same core behavior | Modern Python 3 details differ from legacy Python 2 list-comprehension behavior |
| `nonlocal` statement | Language | 3.0 | Same syntax and semantics | Must find an eligible enclosing-function binding |
| Non-leaking list-comprehension target | Language | 3.0 | Same behavior | Generator, set, and dictionary comprehensions also use implicit nested scope rules |
| Defined optimized-scope `locals()` snapshot semantics | Language | 3.13 | Treat `locals()` as diagnostic; never rely on mutation write-back | PEP 667 standardized behavior that was previously implementation-dependent |
| Annotation scopes for type parameters and `type` statements | Language | 3.12 | Use `TypeVar`, `Generic`, and assignment-style type aliases as appropriate | Annotation scopes can access an enclosing class namespace unlike ordinary methods |
| Lazy annotation evaluation in annotation scopes | Language | 3.14 | Use Python 3.11 annotation rules, optionally with `from __future__ import annotations` where appropriate | Do not assume Python 3.14 annotation timing on an interview runtime |
| Exact local/global bytecode and inline caches | CPython | Version-specific | Reason from language rules | Opcode names and cache strategy are not portable guarantees |

The executable examples use Python 3.11-compatible syntax. The notes mention Python 3.14 annotation scopes only to prevent the broad but false rule that every construct inside a class skips the class namespace.

## 11. Practice brief

Exercises remain unsolved in [practice/README.md](practice/README.md).

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-FND-030-P01` | Predict | 2 | Classify bindings before tracing LEGB and two failure paths | [Practice](practice/README.md) |
| `PY-FND-030-P02` | Implement | 3 | Use `nonlocal` for an explicit factory-state contract with independent instances | [Practice](practice/README.md) |
| `PY-FND-030-P03` | Debug | 3 | Diagnose a class-versus-module lookup bug and qualify state correctly | [Practice](practice/README.md) |
| `PY-FND-030-P04` | Review | 4 | Review shadowing and mutable module-state boundaries in backend code | [Practice](practice/README.md) |

## 12. Interview prompts

Do not read or store full answers before an attempt.

1. Why can a function raise `UnboundLocalError` for a name that exists in the module, and how is that different from `NameError`?
2. When does rebinding require `global` or `nonlocal`, and why does mutating an object reached through a free name not necessarily require either?
3. Why can a class body read an earlier class-local name while a normal method cannot read that class attribute as a bare name?
4. A request handler increments a module global counter. Review the design for correctness, tests, concurrency, and process topology, then propose a clearer state owner.

A strong answer should eventually demonstrate:

- whole-block binding classification before runtime lookup;
- lexical L/E/G/B resolution and its class/comprehension exceptions;
- the distinction between rebinding a namespace entry and mutating an object;
- a maintainable choice among explicit input/output, instance state, closure state, and module state.

## 13. Closed-book revision cues

Without reading the note:

1. Define namespace, scope, code block, environment, local variable, and free variable without using them as synonyms.
2. Draw L, two E levels, G, and B; state which namespaces are deliberately absent from the drawing.
3. Predict a read-before-later-assignment example and explain why lookup does not fall through.
4. Write the smallest valid `global` and `nonlocal` examples, then name the binding each statement redirects.
5. Draw how a class-body namespace becomes class attributes and why a method uses qualified attribute access.
6. Decide how to own mutable state for a process counter, per-request accumulator, and factory-local test helper.

## 14. Authoritative sources

Only sources read during the 2026-08-29 audit are listed.

1. [Python 3.14.7 Language Reference — Execution model, Structure of a program and Naming and binding](https://docs.python.org/3.14/reference/executionmodel.html), accessed 2026-08-29.
2. [Python 3.14.7 Language Reference — Simple statements, Assignment, `global`, and `nonlocal`](https://docs.python.org/3.14/reference/simple_stmts.html), accessed 2026-08-29.
3. [Python 3.14.7 Language Reference — Compound statements, Class definitions](https://docs.python.org/3.14/reference/compound_stmts.html#class-definitions), accessed 2026-08-29.
4. [Python 3.14.7 Language Reference — Expressions, Displays for lists, sets and dictionaries](https://docs.python.org/3.14/reference/expressions.html#displays-for-lists-sets-and-dictionaries), accessed 2026-08-29.
5. [Python 3.14.7 Library Reference — Built-in functions, `globals()`, `locals()`, and `vars()`](https://docs.python.org/3.14/library/functions.html), accessed 2026-08-29.
