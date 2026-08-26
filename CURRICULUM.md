# Python Mastery Curriculum

This is the canonical catalog of **121 independently trackable learning units**.

- Choose a recommended sequence in [LEARNING_PATHS.md](LEARNING_PATHS.md).
- Learn any unit earlier when useful; Codex should warn about prerequisites and provide a short bridge rather than block study unnecessarily.
- Use one dedicated Codex chat per learning unit.
- Create unit folders only when a unit is initialized.

## Curriculum hierarchy

```text
Domain
└── Learning unit
    ├── Subtopic
    └── Evidence artifact
```

| Level | Stable ID | Dedicated chat | Progress row | Folder | Estimate |
|---|---:|---:|---:|---:|---:|
| Domain | Domain code only | No | Roll-up only | No | Aggregate |
| Learning unit | Yes | Yes | Yes | Just in time | Yes |
| Subtopic | Normally no | No | Normally no | No | Included in unit |
| Evidence artifact | Local artifact ID | Same unit chat | Linked evidence | When needed | Activity-specific |

## Stable-ID rules

1. Unit IDs use `PY-<DOMAIN>-<THREE-DIGIT-SEQUENCE>`.
2. IDs are immutable, never silently reused, and always written in full.
3. Titles and paths may evolve without changing the ID.
4. Gaps of ten permit later insertion without renumbering.
5. Splits, merges, retirement, or reclassification require an explicit curriculum decision.

## Granularity rules

A concept becomes an independent unit when several of these are true:

- it has a distinct observable learning outcome;
- it introduces a new mental model or protocol;
- it has meaningful prerequisite boundaries;
- it needs independent practice, review, or a runtime experiment;
- it appears independently in interviews or production design;
- it normally requires at least two focused hours;
- combining it would make the parent unit exceed roughly 10–12 first-pass hours.

A concept remains a subtopic when it shares the same mental model, prerequisites, evidence, and review cycle as its parent. Do not create one folder per function, method, or minor standard-library API.

## Classification legend

`Class` is written as `Priority / Interview frequency / Backend relevance / Depth`.

| Dimension | Values | Meaning |
|---|---|---|
| Priority | `C`, `P`, `A`, `R` | Core, Professional, Advanced, Specialist/reference |
| Interview frequency | `H`, `M`, `L` | High, Medium, Low |
| Backend relevance | `H`, `M`, `L` | High, Medium, Low |
| Depth | `D1`, `D2`, `D3`, `D4` | Fluent use, formal mechanics, runtime-aware, CPython source/C-level |
| Scope | `Lang`, `Std`, `Tool`, `CPy`, `Plat`, `3P` | Language, standard library, tooling, CPython, platform, third-party |
| Evidence | `E`, `C`, `D`, `X`, `(X)`, `R` | Explain, code, debug, required experiment, recommended experiment, production/design transfer |

## Time sizes

| Size | First understanding | Hands-on practice |
|---|---:|---:|
| `S` | 1–2 hours | 1–2 hours |
| `M` | 2–4 hours | 2–4 hours |
| `L` | 4–6 hours | 4–8 hours |
| `XL` | 6–10 hours | 8–14 hours |

Estimates are ranges, not promises. Add roughly 20–35% for two meaningful review cycles and more for research-grade CPython work.

## Domain totals

| Domain | Units | First understanding | Practice |
|---|---:|---:|---:|
| Foundations and execution | 6 | 13–24 h | 13–26 h |
| Built-in types, operations, and functions | 9 | 30–48 h | 30–60 h |
| Functions, callables, iteration, and laziness | 9 | 30–48 h | 30–60 h |
| Object model and object-oriented Python | 9 | 34–54 h | 36–70 h |
| Exceptions and resource management | 3 | 10–16 h | 10–20 h |
| Modules, imports, packaging, and environments | 8 | 27–44 h | 29–56 h |
| Static typing and interfaces | 8 | 28–44 h | 28–56 h |
| Standard-library data and utility tools | 8 | 30–46 h | 30–60 h |
| Files, operating systems, formats, and networking | 9 | 36–56 h | 38–74 h |
| Testing, debugging, and engineering quality | 7 | 24–38 h | 24–48 h |
| Concurrency, parallelism, and asynchronous Python | 9 | 32–52 h | 34–66 h |
| Memory, object lifecycle, and performance | 10 | 40–62 h | 42–82 h |
| Security and production Python | 7 | 24–38 h | 24–48 h |
| CPython internals | 13 | 66–106 h | 80–146 h |
| Interview synthesis and capstones | 6 | 24–38 h | 26–50 h |
| **Total** | **121** | **448–714 h** | **474–922 h** |

## Canonical learning units

Every ID cell below contains the stable anchor used by learning-path and progress links.

## Foundations and execution

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-fnd-010"></a>`PY-FND-010` — **Python syntax and execution** | Run and explain Python programs: lexical basics, indentation, statements, REPL, scripts, modules, comments, docstrings, simple I/O, and style | None | `C/H/H/D1` | `Lang` | `S` | `E+C` |
| <a id="py-fnd-020"></a>`PY-FND-020` — **Objects, names, references, and mutability** | Reason precisely about objects, names, bindings, identity, type, value, references, mutability, aliasing, and copying | `PY-FND-010` | `C/H/H/D2` | `Lang` | `L` | `E+C+D+(X)` |
| <a id="py-fnd-030"></a>`PY-FND-030` — **Namespaces, scope, and name resolution** | Reconstruct namespaces and LEGB lookup; use local, global, nonlocal, and class scopes correctly | `PY-FND-020` | `C/H/H/D2` | `Lang` | `M` | `E+C+D` |
| <a id="py-fnd-040"></a>`PY-FND-040` — **Expressions, evaluation order, and operators** | Predict expression evaluation, precedence, associativity, short-circuiting, assignment expressions, and side-effect order | `PY-FND-010` | `C/H/M/D2` | `Lang` | `M` | `E+D` |
| <a id="py-fnd-050"></a>`PY-FND-050` — **Truthiness, comparisons, equality, and identity** | Use truthiness, comparisons, identity, equality, chained comparison, and sentinel patterns correctly | `PY-FND-020`, `PY-FND-040` | `C/H/H/D2` | `Lang` | `M` | `E+C+D` |
| <a id="py-fnd-060"></a>`PY-FND-060` — **Control flow and structural pattern matching** | Design and trace conditional flow, loops, loop `else`, `break`, `continue`, and structural pattern matching | `PY-FND-040`, `PY-FND-050` | `C/H/H/D2` | `Lang` | `M` | `E+C+D` |

## Built-in types, operations, and functions

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-blt-010"></a>`PY-BLT-010` — **Numbers, booleans, and None** | Use `int`, `bool`, `float`, `complex`, and `None`; explain numeric conversion, floating-point limitations, and numeric edge cases | `PY-FND-020`, `PY-FND-040` | `C/H/H/D2` | `Lang, Std` | `M` | `E+C+D+(X)` |
| <a id="py-blt-020"></a>`PY-BLT-020` — **Strings and Unicode** | Work correctly with `str`, Unicode code points, normalization awareness, formatting, indexing, slicing, and string APIs | `PY-FND-020` | `C/H/H/D2` | `Lang, Std` | `L` | `E+C+D` |
| <a id="py-blt-030"></a>`PY-BLT-030` — **Bytes, bytearray, memoryview, and the buffer model** | Use `bytes`, `bytearray`, `memoryview`, and the buffer model; distinguish text from binary data | `PY-BLT-020`, `PY-FND-020` | `P/M/H/D2` | `Lang, Std` | `L` | `E+C+X` |
| <a id="py-blt-040"></a>`PY-BLT-040` — **Lists, tuples, ranges, and sequence behaviour** | Select and use `list`, `tuple`, and `range`; reason about slicing, copies, nesting, and sequence behaviour | `PY-FND-020`, `PY-FND-040` | `C/H/H/D2` | `Lang, Std` | `L` | `E+C+D+(X)` |
| <a id="py-blt-050"></a>`PY-BLT-050` — **Dictionaries and mapping behaviour** | Use dictionaries deeply: construction, lookup, insertion order, views, merging, missing keys, iteration, and implementation-aware trade-offs | `PY-FND-020`, `PY-FND-050` | `C/H/H/D3` | `Lang, Std, CPy` | `L` | `E+C+D+(X)` |
| <a id="py-blt-060"></a>`PY-BLT-060` — **Sets and frozensets** | Use sets and frozen sets; reason about membership, algebra, deduplication, and hash-based behaviour | `PY-FND-020`, `PY-FND-050` | `C/H/M/D2` | `Lang, Std` | `M` | `E+C+D` |
| <a id="py-blt-070"></a>`PY-BLT-070` — **Unpacking, comprehensions, and generator expressions** | Use unpacking, starred targets, sequence/mapping patterns, comprehensions, and nested-comprehension scope correctly | `PY-BLT-040`, `PY-BLT-050`, `PY-FND-060` | `C/H/H/D2` | `Lang` | `M` | `E+C+D` |
| <a id="py-blt-080"></a>`PY-BLT-080` — **Equality, ordering, hashing, and hashability** | Preserve equality, ordering, hashing, and hashability contracts; design keys and use key-based sorting | `PY-FND-050`, `PY-BLT-040`, `PY-BLT-050`, `PY-BLT-060` | `C/H/H/D2` | `Lang` | `L` | `E+C+D` |
| <a id="py-blt-090"></a>`PY-BLT-090` — **Protocol-facing built-in functions and container complexity** | Master protocol-facing built-ins: `len`, `iter`, `next`, `enumerate`, `zip`, `map`, `filter`, `sorted`, `any`, `all`, `sum`, `min`, `max`, `open`, `getattr`, `setattr`, `isinstance`, `issubclass`, `callable`, `repr`, `format`, and `compile`; compare container complexity | `PY-FND-060`, `PY-BLT-040`, `PY-BLT-050`, `PY-BLT-080` | `C/H/H/D2` | `Lang, Std` | `L` | `E+C+D+R` |

## Functions, callables, iteration, and laziness

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-fit-010"></a>`PY-FIT-010` — **Function definitions, calls, returns, and first-class behaviour** | Define, call, return from, document, annotate, and pass functions as objects | `PY-FND-030`, `PY-FND-040` | `C/H/H/D2` | `Lang` | `M` | `E+C` |
| <a id="py-fit-020"></a>`PY-FIT-020` — **Parameter binding and argument evaluation** | Predict parameter binding: positional-only, keyword-only, defaults, variadics, unpacked calls, and argument evaluation | `PY-FIT-010`, `PY-FND-040` | `C/H/H/D2` | `Lang` | `L` | `E+C+D+(X)` |
| <a id="py-fit-030"></a>`PY-FIT-030` — **Higher-order functions, callable objects, and side effects** | Apply first-class and higher-order functions, lambdas, callable objects, pure functions, and controlled side effects | `PY-FIT-010` | `C/H/H/D2` | `Lang` | `M` | `E+C+R` |
| <a id="py-fit-040"></a>`PY-FIT-040` — **Closures, free variables, and late binding** | Explain nested functions, closures, free variables, cells, `nonlocal`, late binding, and closure inspection | `PY-FIT-010`, `PY-FND-030` | `C/H/H/D3` | `Lang, CPy` | `L` | `E+C+D+X` |
| <a id="py-fit-050"></a>`PY-FIT-050` — **Decorators** | Build and review decorators, preserve metadata, handle parameters, stack decorators, and avoid state/descriptor mistakes | `PY-FIT-030`, `PY-FIT-040` | `C/H/H/D2` | `Lang, Std` | `L` | `E+C+D` |
| <a id="py-fit-060"></a>`PY-FIT-060` — **Recursion and iterative alternatives** | Use recursion responsibly; trace call stacks, base cases, recursion limits, and iterative alternatives | `PY-FIT-010`, `PY-FND-060` | `P/M/M/D2` | `Lang` | `M` | `E+C+D` |
| <a id="py-fit-070"></a>`PY-FIT-070` — **Iterable and iterator protocols** | Implement and consume iterable and iterator protocols; reason about exhaustion, reusability, and custom iterators | `PY-BLT-040`, `PY-FND-060` | `C/H/H/D2` | `Lang` | `L` | `E+C+D` |
| <a id="py-fit-080"></a>`PY-FIT-080` — **Generators, yield, and delegation** | Build generators with `yield`, delegation through `yield from`, and advanced generator control using `send`, `throw`, and `close` | `PY-FIT-010`, `PY-FIT-070` | `C/H/H/D3` | `Lang, CPy` | `L` | `E+C+D+X` |
| <a id="py-fit-090"></a>`PY-FIT-090` — **Lazy pipelines and streaming transformations** | Design lazy pipelines, generator expressions, chunked processing, streaming, and memory-efficient transformations | `PY-FIT-070`, `PY-FIT-080`, `PY-BLT-070` | `C/H/H/D2` | `Lang, Std` | `L` | `E+C+D+R` |

## Object model and object-oriented Python

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-obj-010"></a>`PY-OBJ-010` — **Classes, instances, methods, and construction** | Explain class-body execution, classes, instances, namespaces, method binding, class/static methods, `__new__`, `__init__`, and factories | `PY-FND-020`, `PY-FND-030`, `PY-FIT-010`, `PY-FIT-020` | `C/H/H/D3` | `Lang, CPy` | `L` | `E+C+D+X` |
| <a id="py-obj-020"></a>`PY-OBJ-020` — **Properties, encapsulation, and composition** | Apply properties, encapsulation, validation, composition, delegation, and class responsibility boundaries | `PY-OBJ-010` | `C/H/H/D2` | `Lang` | `M` | `E+C+R` |
| <a id="py-obj-030"></a>`PY-OBJ-030` — **Inheritance, MRO, and super** | Use inheritance, multiple inheritance, C3 MRO, cooperative `super`, overrides, and composition trade-offs | `PY-OBJ-010` | `C/H/H/D2` | `Lang` | `L` | `E+C+D+(X)` |
| <a id="py-obj-040"></a>`PY-OBJ-040` — **Python data model and special methods** | Implement coherent special methods and Python data-model protocols for representation, comparison, hashing, containers, iteration, calls, arithmetic, and context management | `PY-OBJ-010`, `PY-BLT-080`, `PY-FIT-070` | `C/H/H/D3` | `Lang` | `XL` | `E+C+D+R` |
| <a id="py-obj-050"></a>`PY-OBJ-050` — **Attribute lookup, customization, and slots** | Trace attribute lookup and customize it with `__getattribute__`, `__getattr__`, `__setattr__`, and `__slots__` | `PY-OBJ-010`, `PY-FND-030` | `C/H/H/D3` | `Lang, CPy` | `L` | `E+C+D+X` |
| <a id="py-obj-060"></a>`PY-OBJ-060` — **Descriptors** | Explain and implement descriptors, data/non-data precedence, function binding, and managed attributes | `PY-OBJ-050`, `PY-OBJ-020` | `A/M/M/D3` | `Lang, CPy` | `L` | `E+C+D+X` |
| <a id="py-obj-070"></a>`PY-OBJ-070` — **Class-creation hooks and class decorators** | Customize class creation using `__set_name__`, `__init_subclass__`, class decorators, registration, and related hooks | `PY-OBJ-010`, `PY-OBJ-050`, `PY-OBJ-060` | `A/M/M/D3` | `Lang` | `L` | `E+C+D+X` |
| <a id="py-obj-080"></a>`PY-OBJ-080` — **Metaclasses and dynamic class creation** | Explain metaclass selection, the class-creation sequence, conflicts, `type`, and dynamic class creation | `PY-OBJ-070`, `PY-OBJ-030` | `A/L/L/D4` | `Lang, CPy` | `L` | `E+C+D+X` |
| <a id="py-obj-090"></a>`PY-OBJ-090` — **Introspection, reflection, and monkey patching** | Use introspection and reflection safely; understand dynamic access, monkey patching, and production risks | `PY-OBJ-050`, `PY-FIT-010` | `P/M/M/D3` | `Lang, Std` | `M` | `E+C+D+R` |

## Exceptions and resource management

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-err-010"></a>`PY-ERR-010` — **Exception flow and exception-safe control** | Use the exception hierarchy, `try`/`except`/`else`/`finally`, raising, propagation, and exception-safe flow | `PY-FND-060` | `C/H/H/D2` | `Lang` | `M` | `E+C+D` |
| <a id="py-err-020"></a>`PY-ERR-020` — **Custom exceptions, chaining, warnings, and exception groups** | Design custom exceptions; use chaining, tracebacks, warnings, `ExceptionGroup`, and `except*` correctly | `PY-ERR-010`, `PY-OBJ-010` | `C/H/H/D2` | `Lang, Std` | `L` | `E+C+D` |
| <a id="py-err-030"></a>`PY-ERR-030` — **Context managers and resource safety** | Implement context managers, `contextlib`, `ExitStack`, cleanup, and resource safety | `PY-ERR-010`, `PY-FIT-080`, `PY-OBJ-040` | `C/H/H/D2` | `Lang, Std` | `L` | `E+C+D+R` |

## Modules, imports, packaging, and environments

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-mod-010"></a>`PY-MOD-010` — **Modules, packages, and executable modules** | Explain modules, packages, module namespaces, `__name__`, package initialisation, and executable modules | `PY-FND-010`, `PY-FND-030` | `C/H/H/D2` | `Lang, Std` | `M` | `E+C+D` |
| <a id="py-mod-020"></a>`PY-MOD-020` — **Import resolution, sys.path, and module caching** | Trace import resolution, `sys.path`, module creation, caching in `sys.modules`, absolute/relative imports, and import side effects | `PY-MOD-010`, `PY-FND-030` | `C/H/H/D3` | `Lang, Std, CPy` | `L` | `E+C+D+X` |
| <a id="py-mod-030"></a>`PY-MOD-030` — **Circular imports and package boundaries** | Diagnose circular imports and design clean package and dependency boundaries | `PY-MOD-020` | `C/H/H/D2` | `Lang, Std` | `M` | `E+C+D+R` |
| <a id="py-mod-040"></a>`PY-MOD-040` — **Importlib, import hooks, and namespace packages** | Explore `importlib`, finders, loaders, hooks, namespace packages, `pkgutil`, and dynamic imports | `PY-MOD-020`, `PY-OBJ-040` | `A/L/M/D4` | `Std, CPy` | `XL` | `E+C+D+X` |
| <a id="py-mod-050"></a>`PY-MOD-050` — **Python versions and virtual environments** | Manage interpreter versions and environments using `venv`, `uv`, and explicit runtime selection | `PY-FND-010` | `C/M/H/D1` | `Tool, 3P` | `S` | `E+C` |
| <a id="py-mod-060"></a>`PY-MOD-060` — **Pyproject, dependencies, locking, and reproducibility** | Use `pyproject.toml`, dependency declarations, locking, pinning, and reproducible environment principles | `PY-MOD-050`, `PY-MOD-010` | `C/M/H/D2` | `Tool` | `L` | `E+C+D+R` |
| <a id="py-mod-070"></a>`PY-MOD-070` — **Package layouts, resources, entry points, and plugin boundaries** | Design package layouts, editable installs, package data, resources, command entry points, and plugin boundaries | `PY-MOD-010`, `PY-MOD-060` | `P/M/H/D2` | `Std, Tool` | `L` | `E+C+D` |
| <a id="py-mod-080"></a>`PY-MOD-080` — **Build systems, distributions, publishing, and supply-chain boundaries** | Explain build backends, distributions, wheels, source distributions, versioning, publishing, indexes, and packaging supply-chain concerns | `PY-MOD-060`, `PY-MOD-070` | `P/M/H/D3` | `Tool` | `L` | `E+C+D+R` |

## Static typing and interfaces

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-typ-010"></a>`PY-TYP-010` — **Annotation semantics and static analysis boundaries** | Distinguish annotation runtime behaviour from static analysis; identify version-dependent annotation evaluation | `PY-FIT-010`, `PY-OBJ-010` | `C/H/H/D3` | `Lang, Std` | `L` | `E+C+D+(X)` |
| <a id="py-typ-020"></a>`PY-TYP-020` — **Core annotations, unions, literals, and narrowing** | Use basic annotations, aliases, unions, optionals, literals, finals, narrowing, and unreachable-state reasoning | `PY-TYP-010`, `PY-BLT-080` | `C/H/H/D2` | `Lang, Std` | `M` | `E+C+D` |
| <a id="py-typ-030"></a>`PY-TYP-030` — **Generics and type variables** | Design generic APIs with type variables, bounds, constraints, generic classes/functions, and modern type-parameter syntax | `PY-TYP-020`, `PY-OBJ-040` | `P/M/H/D3` | `Lang, Std` | `L` | `E+C+D` |
| <a id="py-typ-040"></a>`PY-TYP-040` — **Variance and safe generic API design** | Reason about covariance, contravariance, invariance, mutable containers, and safe generic API design | `PY-TYP-030` | `A/M/M/D3` | `Lang, Std` | `M` | `E+C+D` |
| <a id="py-typ-050"></a>`PY-TYP-050` — **Protocols, ABCs, and structural versus nominal typing** | Compare protocols, ABCs, `collections.abc`, duck typing, structural typing, and nominal typing | `PY-OBJ-030`, `PY-OBJ-040`, `PY-TYP-020` | `C/H/H/D3` | `Lang, Std` | `L` | `E+C+D+R` |
| <a id="py-typ-060"></a>`PY-TYP-060` — **Callable typing, overloads, ParamSpec, and Self** | Type callables, overloads, decorators, `ParamSpec`, `Concatenate`, and `Self` | `PY-FIT-020`, `PY-FIT-050`, `PY-TYP-030` | `P/M/H/D3` | `Lang, Std` | `L` | `E+C+D` |
| <a id="py-typ-070"></a>`PY-TYP-070` — **Typed records and advanced narrowing** | Model records and narrowing using `TypedDict`, `NamedTuple`, `TypeGuard`, `TypeIs`, and discriminated designs | `PY-TYP-020`, `PY-TYP-030` | `P/M/H/D2` | `Lang, Std` | `L` | `E+C+D` |
| <a id="py-typ-080"></a>`PY-TYP-080` — **Static-analysis tools, stubs, and gradual adoption** | Configure and interpret mypy/pyright-style checking, stubs, strictness, gradual adoption, and `typing_extensions` | `PY-TYP-010`, `PY-MOD-060` | `C/M/H/D2` | `Tool, 3P` | `L` | `E+C+D+R` |

## Standard-library data and utility tools

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-lib-010"></a>`PY-LIB-010` — **Collections: counting, defaults, mappings, and records** | Select and use `Counter`, `defaultdict`, `namedtuple`, `ChainMap`, `OrderedDict`, `UserDict`, `UserList`, `UserString`, and `pprint` appropriately | `PY-BLT-040`, `PY-BLT-050` | `C/H/H/D2` | `Std` | `L` | `E+C+D+R` |
| <a id="py-lib-020"></a>`PY-LIB-020` — **Deque and queue-like patterns** | Use `deque` for queues, BFS, windows, rotation, bounded buffers, and compare it with `list` and `queue` | `PY-BLT-040` | `C/H/H/D2` | `Std` | `M` | `E+C+D` |
| <a id="py-lib-030"></a>`PY-LIB-030` — **Iterator algebra with itertools** | Build lazy pipelines with `itertools`, including infinite iterators, grouping, combinatorics, `tee`, and buffering trade-offs | `PY-FIT-070`, `PY-FIT-080`, `PY-FIT-090` | `C/M/H/D2` | `Std` | `L` | `E+C+D+(X)` |
| <a id="py-lib-040"></a>`PY-LIB-040` — **Callable transformation with functools and operator** | Transform callables with `functools` and `operator`, including caching, dispatch, partial application, metadata, and getters | `PY-FIT-030`, `PY-FIT-050` | `C/M/H/D2` | `Std` | `L` | `E+C+D+R` |
| <a id="py-lib-050"></a>`PY-LIB-050` — **Heap, bisection, and compact-array tools** | Apply `heapq`, `bisect`, and `array`; implement priority, top-k, sorted-insertion, and compact numeric-storage patterns | `PY-BLT-040`, `PY-BLT-090` | `C/H/M/D2` | `Std` | `L` | `E+C+D` |
| <a id="py-lib-060"></a>`PY-LIB-060` — **Dataclasses, enums, types, and generated data models** | Use and compare `dataclasses`, `enum`, `types`, named records, frozen models, slots, and generated methods | `PY-OBJ-010`, `PY-TYP-010` | `C/M/H/D2` | `Std` | `L` | `E+C+D+R` |
| <a id="py-lib-070"></a>`PY-LIB-070` — **Mathematics, precision, fractions, and statistics** | Use `math`, `decimal`, `fractions`, and `statistics`; choose correct numeric semantics and precision | `PY-BLT-010` | `P/M/M/D2` | `Std` | `L` | `E+C+D+(X)` |
| <a id="py-lib-080"></a>`PY-LIB-080` — **Dates, times, time zones, and calendars** | Use `datetime`, `time`, `zoneinfo`, and `calendar`; handle time zones, monotonic clocks, durations, and calendar arithmetic | `PY-BLT-010` | `C/M/H/D2` | `Std` | `L` | `E+C+D+R` |

## Files, operating systems, formats, and networking

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-iop-010"></a>`PY-IOP-010` — **Text and binary files, streams, buffering, and encodings** | Work with text/binary files, encodings, buffering, `io`, streams, file descriptors, `sys` streams, and relevant `mmap` boundaries | `PY-BLT-020`, `PY-BLT-030`, `PY-ERR-030` | `C/H/H/D2` | `Std, Plat` | `L` | `E+C+D+X` |
| <a id="py-iop-020"></a>`PY-IOP-020` — **Pathlib, os, glob, and portable path handling** | Use `pathlib`, `os`, `glob`, and `fnmatch`; compare path objects, raw paths, environment access, and portability | `PY-IOP-010`, `PY-MOD-010` | `C/M/H/D2` | `Std, Plat` | `L` | `E+C+D` |
| <a id="py-iop-030"></a>`PY-IOP-030` — **Filesystem operations, temporary files, and atomicity** | Use `shutil` and `tempfile`; implement safe, atomic, and cleanup-aware filesystem operations | `PY-IOP-020`, `PY-ERR-030` | `P/M/H/D2` | `Std, Plat` | `M` | `E+C+D+R` |
| <a id="py-iop-040"></a>`PY-IOP-040` — **Subprocesses, pipes, exit codes, and signals** | Run and supervise external processes with `subprocess`; understand shell boundaries, pipes, exit codes, and signals | `PY-ERR-010`, `PY-IOP-010` | `C/M/H/D3` | `Std, Plat` | `L` | `E+C+D+X` |
| <a id="py-iop-050"></a>`PY-IOP-050` — **JSON, CSV, TOML, and configuration formats** | Process `json`, `csv`, TOML through `tomllib`, and INI configuration through `configparser` | `PY-BLT-020`, `PY-BLT-040`, `PY-BLT-050`, `PY-IOP-010` | `C/M/H/D2` | `Std` | `L` | `E+C+D` |
| <a id="py-iop-060"></a>`PY-IOP-060` — **Pickle, shelve, copying, and object graphs** | Understand `pickle`, `shelve`, copying, object graphs, compatibility, and deserialization risks | `PY-FND-020`, `PY-ERR-010`, `PY-IOP-010` | `P/M/H/D3` | `Std, CPy` | `L` | `E+C+D+X` |
| <a id="py-iop-070"></a>`PY-IOP-070` — **Regular expressions, argparse, and command-line processing** | Use regular expressions, `argparse`, environment variables, and command-line text-processing patterns responsibly | `PY-BLT-020`, `PY-FND-060`, `PY-MOD-010` | `P/M/H/D2` | `Std, Plat` | `L` | `E+C+D` |
| <a id="py-iop-080"></a>`PY-IOP-080` — **Networking foundations with socket, SSL, HTTP, URL, and email tools** | Understand networking foundations through `socket`, `ssl`, `urllib`, `http`, and `email`, without turning the repository into a networking course | `PY-BLT-030`, `PY-ERR-030` | `P/L/H/D3` | `Std, Plat` | `XL` | `E+C+D+X` |
| <a id="py-iop-090"></a>`PY-IOP-090` — **Streaming large data and bounded processing** | Stream large data using chunking, incremental parsing, lazy transformation, bounded buffers, and backpressure-aware designs | `PY-IOP-010`, `PY-FIT-090` | `C/M/H/D2` | `Lang, Std` | `L` | `E+C+D+R` |

## Testing, debugging, and engineering quality

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-tst-010"></a>`PY-TST-010` — **Testing principles, unittest, and doctest** | Design unit/integration tests, assertions, boundaries, deterministic cases, and use `unittest` and `doctest` appropriately | `PY-FIT-010`, `PY-ERR-010` | `C/H/H/D2` | `Std, Tool` | `M` | `E+C+D` |
| <a id="py-tst-020"></a>`PY-TST-020` — **Pytest fundamentals and fixtures** | Use pytest discovery, assertions, fixtures, setup/teardown, and test organisation | `PY-TST-010`, `PY-MOD-010` | `C/H/H/D2` | `3P, Tool` | `L` | `E+C+D` |
| <a id="py-tst-030"></a>`PY-TST-030` — **Parametrization, marks, monkeypatching, and fixture composition** | Use parametrization, marks, temporary resources, monkeypatching, and fixture composition | `PY-TST-020`, `PY-FIT-050` | `C/M/H/D2` | `3P, Tool` | `M` | `E+C+D` |
| <a id="py-tst-040"></a>`PY-TST-040` — **Test doubles, mocking, and patching boundaries** | Design test doubles; use mocking and `unittest.mock.patch` without patching the wrong namespace | `PY-TST-020`, `PY-OBJ-090`, `PY-MOD-020` | `C/H/H/D3` | `Std, 3P, Tool` | `L` | `E+C+D` |
| <a id="py-tst-050"></a>`PY-TST-050` — **Property-based testing, coverage, and mutation concepts** | Apply property-based testing, coverage analysis, mutation-testing concepts, and edge-case generation | `PY-TST-020`, `PY-BLT-080` | `P/M/H/D2` | `3P, Tool` | `L` | `E+C+D` |
| <a id="py-tst-060"></a>`PY-TST-060` — **Debugging, tracebacks, pdb, logging, and controlled reproduction** | Debug with tracebacks, `breakpoint`, `pdb`, logging, warnings, inspection, and controlled reproduction | `PY-ERR-020`, `PY-MOD-010` | `C/H/H/D2` | `Std, Tool` | `L` | `E+C+D` |
| <a id="py-tst-070"></a>`PY-TST-070` — **Formatting, linting, static analysis, and maintainability** | Apply formatting, linting, static analysis, Python design principles, maintainability, refactoring, and anti-pattern review | `PY-TST-010`, `PY-TYP-080`, `PY-MOD-060` | `C/H/H/D2` | `Tool, 3P` | `L` | `E+C+D+R` |

## Concurrency, parallelism, and asynchronous Python

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-con-010"></a>`PY-CON-010` — **Concurrency, parallelism, scheduling, and the GIL model** | Distinguish concurrency, parallelism, scheduling, CPU-bound work, I/O-bound work, and the high-level GIL model | `PY-FND-020`, `PY-FIT-010` | `C/H/H/D2` | `Lang, CPy` | `M` | `E+C+D` |
| <a id="py-con-020"></a>`PY-CON-020` — **Threads, lifecycle, context, and thread-safe boundaries** | Use `threading`, thread lifecycle, thread-local/context state, failure handling, and thread-safe boundaries | `PY-CON-010`, `PY-ERR-030` | `C/M/H/D3` | `Std, CPy` | `M` | `E+C+D+X` |
| <a id="py-con-030"></a>`PY-CON-030` — **Synchronization, queues, races, and deadlocks** | Use locks, reentrant locks, semaphores, events, conditions, barriers, and `queue`; diagnose races and deadlocks | `PY-CON-020`, `PY-LIB-020` | `C/H/H/D3` | `Std, CPy` | `L` | `E+C+D+X` |
| <a id="py-con-040"></a>`PY-CON-040` — **Multiprocessing, IPC, shared memory, and process isolation** | Use `multiprocessing`, start methods, IPC, pools, shared memory, serialisation, and process isolation | `PY-CON-010`, `PY-MOD-020`, `PY-IOP-010` | `P/M/H/D3` | `Std, Plat` | `L` | `E+C+D+X` |
| <a id="py-con-050"></a>`PY-CON-050` — **Futures and executors** | Coordinate work with `concurrent.futures`, executors, futures, completion, exceptions, and shutdown | `PY-CON-020`, `PY-CON-040` | `C/M/H/D2` | `Std` | `M` | `E+C+D` |
| <a id="py-con-060"></a>`PY-CON-060` — **Asyncio event loop, coroutines, tasks, and context** | Explain the `asyncio` event loop, coroutines, `await`, tasks, futures, scheduling, and `contextvars` | `PY-FIT-080`, `PY-ERR-030`, `PY-CON-010` | `C/H/H/D3` | `Std, CPy` | `L` | `E+C+D+X` |
| <a id="py-con-070"></a>`PY-CON-070` — **Structured concurrency, cancellation, and timeouts** | Apply structured concurrency, `TaskGroup`, cancellation, timeouts, exception groups, and cancellation-safe cleanup | `PY-CON-060`, `PY-ERR-020` | `C/H/H/D3` | `Std` | `L` | `E+C+D+X` |
| <a id="py-con-080"></a>`PY-CON-080` — **Async queues, backpressure, async iteration, and blocking boundaries** | Design async queues, synchronisation, backpressure, async iterators/generators, and blocking-work boundaries | `PY-CON-060`, `PY-CON-070`, `PY-FIT-090` | `C/H/H/D3` | `Std` | `L` | `E+C+D+R` |
| <a id="py-con-090"></a>`PY-CON-090` — **Free-threaded CPython, subinterpreters, and version-specific GIL changes** | Understand version-specific GIL changes, supported free-threaded CPython, subinterpreters, compatibility, and migration risks | `PY-CON-010`, `PY-CON-020`, `PY-CON-040`, `PY-MPR-010` | `A/M/M/D4` | `CPy` | `XL` | `E+D+X+R` |

## Memory, object lifecycle, and performance

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-mpr-010"></a>`PY-MPR-010` — **Object lifetime, reference counting, finalization, and weak references** | Explain object lifetime, references, CPython reference counting, finalisation, `__del__`, and `weakref` | `PY-FND-020`, `PY-OBJ-010` | `C/H/H/D3` | `Lang, Std, CPy` | `L` | `E+C+D+X` |
| <a id="py-mpr-020"></a>`PY-MPR-020` — **Cyclic garbage collection and gc inspection** | Explain cyclic garbage collection, generations, tracked objects, collection triggers, and `gc` inspection | `PY-MPR-010` | `P/M/M/D3` | `Std, CPy` | `L` | `E+C+D+X` |
| <a id="py-mpr-030"></a>`PY-MPR-030` — **Stack, frame, heap, call, and local-variable mental models** | Build accurate stack, frame, heap, call, and local-variable mental models without treating them as language guarantees | `PY-FIT-010`, `PY-FND-030` | `C/M/M/D3` | `Lang, CPy` | `M` | `E+D+X` |
| <a id="py-mpr-040"></a>`PY-MPR-040` — **Object sizing, interning, caches, and shallow measurements** | Measure object sizes and graphs; understand `sys.getsizeof`, `__slots__`, interning, caches, and shallow measurements | `PY-MPR-010`, `PY-BLT-040`, `PY-BLT-050`, `PY-OBJ-050` | `P/M/M/D3` | `Std, CPy` | `L` | `E+C+D+X` |
| <a id="py-mpr-050"></a>`PY-MPR-050` — **CPython small-object allocation and fragmentation** | Understand CPython arenas, pools, blocks, small-object allocation, fragmentation, and OS-visible memory | `PY-MPR-010` | `A/L/L/D4` | `CPy, Plat` | `L` | `E+X` |
| <a id="py-mpr-060"></a>`PY-MPR-060` — **Memory-growth and leak diagnosis** | Diagnose memory growth and leaks using `tracemalloc`, `gc`, object graphs, snapshots, and reproducible workloads | `PY-MPR-020`, `PY-MPR-040` | `P/M/H/D3` | `Std, CPy, Tool` | `L` | `E+C+D+X` |
| <a id="py-mpr-070"></a>`PY-MPR-070` — **Algorithmic and memory complexity** | Analyse algorithmic and memory complexity; choose appropriate built-in and standard-library structures | `PY-BLT-040`, `PY-BLT-050`, `PY-BLT-060` | `C/H/H/D2` | `Lang, Std` | `L` | `E+C+D+R` |
| <a id="py-mpr-080"></a>`PY-MPR-080` — **Responsible benchmarking** | Benchmark responsibly using `timeit`, `pyperf`, repeated trials, warm-up, noise analysis, and environment records | `PY-MPR-070`, `PY-FIT-010` | `C/M/H/D3` | `Std, 3P, Tool` | `L` | `E+C+D+X` |
| <a id="py-mpr-090"></a>`PY-MPR-090` — **Profiling and tracing** | Profile with `cProfile`, `profile`, `pstats`, tracing, and sampling concepts; distinguish CPU time from waiting | `PY-MPR-080`, `PY-TST-060` | `C/M/H/D3` | `Std, Tool` | `L` | `E+C+D+X` |
| <a id="py-mpr-100"></a>`PY-MPR-100` — **Performance optimization strategy** | Optimise through algorithms, data selection, allocation reduction, laziness, caching, vectorisation/native boundaries, and I/O/database/network/concurrency trade-offs | `PY-MPR-070`, `PY-MPR-080`, `PY-MPR-090`, `PY-FIT-090`, `PY-CON-010` | `C/H/H/D3` | `Lang, Std, Tool` | `XL` | `E+C+D+X+R` |

## Security and production Python

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-sec-010"></a>`PY-SEC-010` — **Validation, trust boundaries, and resource exhaustion** | Establish trust and validation boundaries; defend against resource exhaustion and malformed input | `PY-ERR-010`, `PY-BLT-080` | `C/M/H/D2` | `Lang, Std` | `M` | `E+C+D+R` |
| <a id="py-sec-020"></a>`PY-SEC-020` — **Deserialization, command, path, and temporary-file security** | Prevent unsafe deserialization, command injection, path traversal, symlink/temp-file mistakes, and filesystem races | `PY-IOP-030`, `PY-IOP-040`, `PY-IOP-060` | `C/M/H/D2` | `Std, Plat` | `L` | `E+C+D` |
| <a id="py-sec-030"></a>`PY-SEC-030` — **Randomness, secrets, hashes, HMAC, UUIDs, and sensitive logs** | Distinguish `random` from `secrets`; use `hashlib`, `hmac`, `uuid`, secure comparison, and sensitive-log controls | `PY-BLT-010`, `PY-IOP-010` | `C/M/H/D2` | `Std` | `L` | `E+C+D+(X)` |
| <a id="py-sec-040"></a>`PY-SEC-040` — **Dependency, credential, configuration, and supply-chain security** | Manage dependencies, configuration, credentials, pinning, provenance, and supply-chain risk | `PY-MOD-060`, `PY-MOD-080` | `P/L/H/D2` | `Tool` | `M` | `E+D+R` |
| <a id="py-sec-050"></a>`PY-SEC-050` — **Production configuration, observability, logging, and graceful shutdown** | Design production configuration, observability, structured logging context, graceful shutdown, and cleanup | `PY-TST-060`, `PY-ERR-030`, `PY-CON-070` | `C/M/H/D3` | `Std, Tool` | `L` | `E+C+D+R` |
| <a id="py-sec-060"></a>`PY-SEC-060` — **Backend API, database, network, validation, and error boundaries** | Design Python API, database, network, transaction, validation, and error boundaries for backend services | `PY-ERR-020`, `PY-TYP-050`, `PY-IOP-080` | `C/H/H/D3` | `Lang, Std` | `L` | `E+C+D+R` |
| <a id="py-sec-070"></a>`PY-SEC-070` — **Async-service deadlines, backpressure, pools, and shutdown** | Integrate async services with deadlines, cancellation, backpressure, blocking libraries, pools, and shutdown semantics | `PY-CON-070`, `PY-CON-080`, `PY-SEC-060` | `C/H/H/D3` | `Std` | `L` | `E+C+D+R` |

## CPython internals

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-cpy-010"></a>`PY-CPY-010` — **CPython source tree, builds, and focused tests** | Navigate the CPython source tree; build release/debug interpreters and run focused tests safely | `PY-MOD-050`, `PY-MOD-070`, `PY-TST-060` | `A/L/L/D4` | `CPy, Tool` | `L` | `E+C+X` |
| <a id="py-cpy-020"></a>`PY-CPY-020` — **Tokenizer, PEG parser, grammar, and AST creation** | Trace source text through tokenisation, the PEG parser, concrete grammar, and AST creation | `PY-FND-010`, `PY-MOD-010` | `A/L/L/D4` | `CPy` | `L` | `E+C+X` |
| <a id="py-cpy-030"></a>`PY-CPY-030` — **Symbol tables, scope analysis, and compilation** | Explain symbol-table analysis, scope classification, compiler passes, and code generation | `PY-FND-030`, `PY-CPY-020` | `A/L/L/D4` | `CPy` | `L` | `E+C+X` |
| <a id="py-cpy-040"></a>`PY-CPY-040` — **Code objects and CPython bytecode** | Inspect code objects, constants, names, closures, line tables, exceptions, and CPython bytecode with `dis` | `PY-FIT-010`, `PY-CPY-030` | `A/M/M/D4` | `CPy` | `L` | `E+C+D+X` |
| <a id="py-cpy-050"></a>`PY-CPY-050` — **Frames and the evaluation loop** | Trace frames and the evaluation loop; connect Python execution to interpreter state | `PY-CPY-040`, `PY-MPR-030` | `A/M/M/D4` | `CPy` | `XL` | `E+D+X` |
| <a id="py-cpy-060"></a>`PY-CPY-060` — **Function-call mechanics and vectorcall** | Understand function-call mechanics, argument parsing, vectorcall, bound calls, and call overhead | `PY-FIT-020`, `PY-CPY-050` | `A/M/M/D4` | `CPy` | `L` | `E+C+D+X` |
| <a id="py-cpy-070"></a>`PY-CPY-070` — **PyObject, type objects, slots, descriptors, and runtime dispatch** | Understand `PyObject`, type objects, object headers, slots, special-method lookup, descriptors, and runtime dispatch | `PY-OBJ-040`, `PY-OBJ-050`, `PY-OBJ-060`, `PY-CPY-050`, `PY-MPR-010` | `A/M/M/D4` | `CPy` | `XL` | `E+D+X` |
| <a id="py-cpy-080"></a>`PY-CPY-080` — **Dictionary, set, list, tuple, and string internals** | Explore dictionary, set, list, tuple, and string representations, resizing, lookup, and layout trade-offs | `PY-BLT-040`, `PY-BLT-050`, `PY-BLT-060`, `PY-CPY-070` | `A/M/M/D4` | `CPy` | `XL` | `E+C+D+X` |
| <a id="py-cpy-090"></a>`PY-CPY-090` — **Allocator, reference-count, garbage-collector, and finalization internals** | Connect allocator, reference-count, garbage-collector, finalisation, and object-lifecycle source paths | `PY-MPR-010`, `PY-MPR-020`, `PY-MPR-050`, `PY-CPY-070` | `A/M/M/D4` | `CPy` | `XL` | `E+D+X` |
| <a id="py-cpy-100"></a>`PY-CPY-100` — **Adaptive specialization, inline caches, instrumentation, and JIT boundaries** | Explain adaptive specialisation, inline caches, instrumentation, experimental JIT boundaries, and responsible bytecode interpretation | `PY-CPY-040`, `PY-CPY-050`, `PY-MPR-080` | `A/M/M/D4` | `CPy` | `XL` | `E+D+X` |
| <a id="py-cpy-110"></a>`PY-CPY-110` — **GIL, free-threading, subinterpreters, and extension compatibility** | Study the GIL, free-threaded execution, atomicity changes, subinterpreters, extension compatibility, and runtime trade-offs | `PY-CON-090`, `PY-CPY-050`, `PY-CPY-070`, `PY-CPY-090` | `A/M/M/D4` | `CPy` | `XL` | `E+D+X+R` |
| <a id="py-cpy-120"></a>`PY-CPY-120` — **Python/C API, Limited API, and Stable ABI** | Build extension-module understanding through the Python/C API, Limited API, Stable ABI, reference ownership, and failure handling | `PY-MOD-080`, `PY-CPY-070`, `PY-CPY-090` | `R/L/L/D4` | `CPy` | `XL` | `E+C+D+X` |
| <a id="py-cpy-130"></a>`PY-CPY-130` — **Alternative interpreters and portability** | Compare CPython with PyPy, GraalPy, MicroPython, and other interpreters; identify portability assumptions | `PY-CPY-040`, `PY-CPY-070`, `PY-CON-090` | `A/L/M/D4` | `CPy` | `L` | `E+D+R` |

## Interview synthesis and capstones

| ID | Learning outcome and included scope | Prerequisite IDs | Class | Scope | Size | Evidence |
|---|---|---|---|---|:---:|---|
| <a id="py-int-010"></a>`PY-INT-010` — **Python traps and output-prediction reasoning** | Solve common Python traps and output-prediction questions using semantic reasoning rather than memorisation | `PY-FND-010`, `PY-FND-020`, `PY-FND-030`, `PY-FND-040`, `PY-FND-050`, `PY-FND-060`, `PY-BLT-010`, `PY-BLT-020`, `PY-BLT-030`, `PY-BLT-040`, `PY-BLT-050`, `PY-BLT-060`, `PY-BLT-070`, `PY-BLT-080`, `PY-BLT-090`, `PY-FIT-010`, `PY-FIT-020`, `PY-FIT-030`, `PY-FIT-040`, `PY-FIT-050`, `PY-FIT-060`, `PY-FIT-070`, `PY-FIT-080`, `PY-FIT-090`, `PY-ERR-010`, `PY-ERR-020`, `PY-ERR-030`, `PY-OBJ-010`, `PY-OBJ-030`, `PY-OBJ-040`, `PY-OBJ-050` | `C/H/H/D2` | `Lang, Std` | `M` | `E+D` |
| <a id="py-int-020"></a>`PY-INT-020` — **Debugging, refactoring, and senior code review** | Diagnose and refactor faulty Python through debugging and senior code-review drills | `PY-TST-060`, `PY-TST-070` | `C/H/H/D2` | `Lang, Tool` | `L` | `E+C+D+R` |
| <a id="py-int-030"></a>`PY-INT-030` — **Pythonic implementation exercises** | Complete implementation exercises using Pythonic structure, appropriate containers, tests, and complexity reasoning | `PY-BLT-090`, `PY-FIT-090`, `PY-LIB-010`, `PY-LIB-020`, `PY-LIB-030`, `PY-LIB-040`, `PY-LIB-050`, `PY-MPR-070` | `C/H/H/D2` | `Lang, Std, Tool` | `L` | `E+C+D` |
| <a id="py-int-040"></a>`PY-INT-040` — **Senior backend and API design interviews in Python** | Conduct senior backend/API design interviews involving Python semantics, typing, testing, errors, and runtime boundaries | `PY-SEC-060`, `PY-TYP-050`, `PY-TST-070` | `C/H/H/D3` | `Lang, Std, Tool` | `L` | `E+D+R` |
| <a id="py-int-050"></a>`PY-INT-050` — **Performance, concurrency, memory, and CPython interviews** | Conduct performance, concurrency, memory, and CPython-aware interview rounds | `PY-CON-080`, `PY-MPR-100`, `PY-CPY-040`, `PY-CPY-050`, `PY-CPY-070`, `PY-CPY-080`, `PY-CPY-100`, `PY-CPY-110` | `C/M/H/D3` | `Lang, Std, CPy` | `L` | `E+D+R` |
| <a id="py-int-060"></a>`PY-INT-060` — **Integrated Python mastery capstone** | Demonstrate integrated mastery through teach-back, a substantial Python project, experiments, review, and design defence | `PY-INT-010`, `PY-INT-020`, `PY-INT-030`, `PY-INT-040`, `PY-INT-050` | `P/M/H/D3` | `Lang, Std, Tool, CPy` | `XL` | `E+C+D+X+R` |

## Related repository views

- [Recommended learning paths](LEARNING_PATHS.md)
- [Evidence and progress tracker](PROGRESS.md)
- [Milestone projects](PROJECTS.md)
- [Daily workflow](docs/WORKFLOW.md)
