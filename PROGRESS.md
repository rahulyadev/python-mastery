# Python Mastery Progress

[Curriculum](CURRICULUM.md) · [Learning paths](LEARNING_PATHS.md) · [Workflow](docs/WORKFLOW.md)

Artifact state and learning state are separate. Generated files never prove learning.

## Artifact state

| State | Meaning |
|---|---|
| `Absent` | No unit folder exists |
| `Draft` | Material exists but is incomplete, unapproved, or not fully source-checked |
| `Approved` | Canonical material is coherent, source-checked, and runnable where applicable |

## Learning state

```text
⬜ Not started
→ 🟠 Learning
→ 🟡 Practiced
→ 🔵 Recalled
→ 🟣 Demonstrated
→ 🟢 Retained
```

`★ Mastery` is a separate, exceptional badge.

## Evidence-based transitions

### Not started → Learning

- The learner engaged with the mental model.
- At least one reconstruction, question, prediction, or misconception was recorded.
- Folder creation alone is insufficient.

### Learning → Practiced

- Mandatory exercises were attempted before solutions.
- Deterministic tests pass where applicable.
- Important edge cases and the reasoning behind corrections are understood.
- Concrete evidence is linked.

### Practiced → Recalled

- A closed-book review occurred after at least one day.
- The central mental model and visual were reconstructed without reading.
- No critical misconception remains.
- Roughly 80% of core retrieval checks were correct.

### Recalled → Demonstrated

- A new, non-memorized scenario was completed.
- The mechanism and trade-offs were explained.
- Required coding, debugging, experiment, or production-transfer evidence was satisfied without a direct solution.

### Demonstrated → Retained

- One successful retrieval normally occurred at least seven days later.
- A second successful retrieval normally occurred at least twenty-one days after that.
- Equivalent documented production or milestone-project evidence may substitute.
- No critical weakness remains unresolved.

### Mastery badge

Requires Retained state, transfer across at least two contexts, successful teach-back, diagnosis of a subtle failure, explanation of boundaries and uncertainty, and a current-version check.

## Tracker

| Unit ID | Title | Priority | Artifact state | Learning state | Last evidence | Next review | Weakest point | Evidence link |
|---|---|---|---|---|---|---|---|---|
| `PY-FND-010` | [Python syntax and execution](CURRICULUM.md#py-fnd-010) | Core | Draft | Not started | — | — | — | [Unit note](units/foundations/PY-FND-010-python-syntax-and-execution/README.md) |
| `PY-FND-020` | [Objects, names, references, and mutability](CURRICULUM.md#py-fnd-020) | Core | Approved | Not started | — | — | — | [Unit note](units/foundations/PY-FND-020-objects-names-references-and-mutability/README.md) |
| `PY-FND-030` | [Namespaces, scope, and name resolution](CURRICULUM.md#py-fnd-030) | Core | Approved | Not started | — | — | — | [Unit note](units/foundations/PY-FND-030-namespaces-scope-and-name-resolution/README.md) |
| `PY-FND-040` | [Expressions, evaluation order, and operators](CURRICULUM.md#py-fnd-040) | Core | Absent | Not started | — | — | — | — |
| `PY-FND-050` | [Truthiness, comparisons, equality, and identity](CURRICULUM.md#py-fnd-050) | Core | Absent | Not started | — | — | — | — |
| `PY-FND-060` | [Control flow and structural pattern matching](CURRICULUM.md#py-fnd-060) | Core | Absent | Not started | — | — | — | — |
| `PY-BLT-010` | [Numbers, booleans, and None](CURRICULUM.md#py-blt-010) | Core | Absent | Not started | — | — | — | — |
| `PY-BLT-020` | [Strings and Unicode](CURRICULUM.md#py-blt-020) | Core | Absent | Not started | — | — | — | — |
| `PY-BLT-030` | [Bytes, bytearray, memoryview, and the buffer model](CURRICULUM.md#py-blt-030) | Professional | Absent | Not started | — | — | — | — |
| `PY-BLT-040` | [Lists, tuples, ranges, and sequence behaviour](CURRICULUM.md#py-blt-040) | Core | Absent | Not started | — | — | — | — |
| `PY-BLT-050` | [Dictionaries and mapping behaviour](CURRICULUM.md#py-blt-050) | Core | Absent | Not started | — | — | — | — |
| `PY-BLT-060` | [Sets and frozensets](CURRICULUM.md#py-blt-060) | Core | Absent | Not started | — | — | — | — |
| `PY-BLT-070` | [Unpacking, comprehensions, and generator expressions](CURRICULUM.md#py-blt-070) | Core | Absent | Not started | — | — | — | — |
| `PY-BLT-080` | [Equality, ordering, hashing, and hashability](CURRICULUM.md#py-blt-080) | Core | Absent | Not started | — | — | — | — |
| `PY-BLT-090` | [Protocol-facing built-in functions and container complexity](CURRICULUM.md#py-blt-090) | Core | Absent | Not started | — | — | — | — |
| `PY-FIT-010` | [Function definitions, calls, returns, and first-class behaviour](CURRICULUM.md#py-fit-010) | Core | Absent | Not started | — | — | — | — |
| `PY-FIT-020` | [Parameter binding and argument evaluation](CURRICULUM.md#py-fit-020) | Core | Absent | Not started | — | — | — | — |
| `PY-FIT-030` | [Higher-order functions, callable objects, and side effects](CURRICULUM.md#py-fit-030) | Core | Absent | Not started | — | — | — | — |
| `PY-FIT-040` | [Closures, free variables, and late binding](CURRICULUM.md#py-fit-040) | Core | Absent | Not started | — | — | — | — |
| `PY-FIT-050` | [Decorators](CURRICULUM.md#py-fit-050) | Core | Absent | Not started | — | — | — | — |
| `PY-FIT-060` | [Recursion and iterative alternatives](CURRICULUM.md#py-fit-060) | Professional | Absent | Not started | — | — | — | — |
| `PY-FIT-070` | [Iterable and iterator protocols](CURRICULUM.md#py-fit-070) | Core | Absent | Not started | — | — | — | — |
| `PY-FIT-080` | [Generators, yield, and delegation](CURRICULUM.md#py-fit-080) | Core | Absent | Not started | — | — | — | — |
| `PY-FIT-090` | [Lazy pipelines and streaming transformations](CURRICULUM.md#py-fit-090) | Core | Absent | Not started | — | — | — | — |
| `PY-OBJ-010` | [Classes, instances, methods, and construction](CURRICULUM.md#py-obj-010) | Core | Absent | Not started | — | — | — | — |
| `PY-OBJ-020` | [Properties, encapsulation, and composition](CURRICULUM.md#py-obj-020) | Core | Absent | Not started | — | — | — | — |
| `PY-OBJ-030` | [Inheritance, MRO, and super](CURRICULUM.md#py-obj-030) | Core | Absent | Not started | — | — | — | — |
| `PY-OBJ-040` | [Python data model and special methods](CURRICULUM.md#py-obj-040) | Core | Absent | Not started | — | — | — | — |
| `PY-OBJ-050` | [Attribute lookup, customization, and slots](CURRICULUM.md#py-obj-050) | Core | Absent | Not started | — | — | — | — |
| `PY-OBJ-060` | [Descriptors](CURRICULUM.md#py-obj-060) | Advanced | Absent | Not started | — | — | — | — |
| `PY-OBJ-070` | [Class-creation hooks and class decorators](CURRICULUM.md#py-obj-070) | Advanced | Absent | Not started | — | — | — | — |
| `PY-OBJ-080` | [Metaclasses and dynamic class creation](CURRICULUM.md#py-obj-080) | Advanced | Absent | Not started | — | — | — | — |
| `PY-OBJ-090` | [Introspection, reflection, and monkey patching](CURRICULUM.md#py-obj-090) | Professional | Absent | Not started | — | — | — | — |
| `PY-ERR-010` | [Exception flow and exception-safe control](CURRICULUM.md#py-err-010) | Core | Absent | Not started | — | — | — | — |
| `PY-ERR-020` | [Custom exceptions, chaining, warnings, and exception groups](CURRICULUM.md#py-err-020) | Core | Absent | Not started | — | — | — | — |
| `PY-ERR-030` | [Context managers and resource safety](CURRICULUM.md#py-err-030) | Core | Absent | Not started | — | — | — | — |
| `PY-MOD-010` | [Modules, packages, and executable modules](CURRICULUM.md#py-mod-010) | Core | Absent | Not started | — | — | — | — |
| `PY-MOD-020` | [Import resolution, sys.path, and module caching](CURRICULUM.md#py-mod-020) | Core | Absent | Not started | — | — | — | — |
| `PY-MOD-030` | [Circular imports and package boundaries](CURRICULUM.md#py-mod-030) | Core | Absent | Not started | — | — | — | — |
| `PY-MOD-040` | [Importlib, import hooks, and namespace packages](CURRICULUM.md#py-mod-040) | Advanced | Absent | Not started | — | — | — | — |
| `PY-MOD-050` | [Python versions and virtual environments](CURRICULUM.md#py-mod-050) | Core | Absent | Not started | — | — | — | — |
| `PY-MOD-060` | [Pyproject, dependencies, locking, and reproducibility](CURRICULUM.md#py-mod-060) | Core | Absent | Not started | — | — | — | — |
| `PY-MOD-070` | [Package layouts, resources, entry points, and plugin boundaries](CURRICULUM.md#py-mod-070) | Professional | Absent | Not started | — | — | — | — |
| `PY-MOD-080` | [Build systems, distributions, publishing, and supply-chain boundaries](CURRICULUM.md#py-mod-080) | Professional | Absent | Not started | — | — | — | — |
| `PY-TYP-010` | [Annotation semantics and static analysis boundaries](CURRICULUM.md#py-typ-010) | Core | Absent | Not started | — | — | — | — |
| `PY-TYP-020` | [Core annotations, unions, literals, and narrowing](CURRICULUM.md#py-typ-020) | Core | Absent | Not started | — | — | — | — |
| `PY-TYP-030` | [Generics and type variables](CURRICULUM.md#py-typ-030) | Professional | Absent | Not started | — | — | — | — |
| `PY-TYP-040` | [Variance and safe generic API design](CURRICULUM.md#py-typ-040) | Advanced | Absent | Not started | — | — | — | — |
| `PY-TYP-050` | [Protocols, ABCs, and structural versus nominal typing](CURRICULUM.md#py-typ-050) | Core | Absent | Not started | — | — | — | — |
| `PY-TYP-060` | [Callable typing, overloads, ParamSpec, and Self](CURRICULUM.md#py-typ-060) | Professional | Absent | Not started | — | — | — | — |
| `PY-TYP-070` | [Typed records and advanced narrowing](CURRICULUM.md#py-typ-070) | Professional | Absent | Not started | — | — | — | — |
| `PY-TYP-080` | [Static-analysis tools, stubs, and gradual adoption](CURRICULUM.md#py-typ-080) | Core | Absent | Not started | — | — | — | — |
| `PY-LIB-010` | [Collections: counting, defaults, mappings, and records](CURRICULUM.md#py-lib-010) | Core | Absent | Not started | — | — | — | — |
| `PY-LIB-020` | [Deque and queue-like patterns](CURRICULUM.md#py-lib-020) | Core | Absent | Not started | — | — | — | — |
| `PY-LIB-030` | [Iterator algebra with itertools](CURRICULUM.md#py-lib-030) | Core | Absent | Not started | — | — | — | — |
| `PY-LIB-040` | [Callable transformation with functools and operator](CURRICULUM.md#py-lib-040) | Core | Absent | Not started | — | — | — | — |
| `PY-LIB-050` | [Heap, bisection, and compact-array tools](CURRICULUM.md#py-lib-050) | Core | Absent | Not started | — | — | — | — |
| `PY-LIB-060` | [Dataclasses, enums, types, and generated data models](CURRICULUM.md#py-lib-060) | Core | Absent | Not started | — | — | — | — |
| `PY-LIB-070` | [Mathematics, precision, fractions, and statistics](CURRICULUM.md#py-lib-070) | Professional | Absent | Not started | — | — | — | — |
| `PY-LIB-080` | [Dates, times, time zones, and calendars](CURRICULUM.md#py-lib-080) | Core | Absent | Not started | — | — | — | — |
| `PY-IOP-010` | [Text and binary files, streams, buffering, and encodings](CURRICULUM.md#py-iop-010) | Core | Absent | Not started | — | — | — | — |
| `PY-IOP-020` | [Pathlib, os, glob, and portable path handling](CURRICULUM.md#py-iop-020) | Core | Absent | Not started | — | — | — | — |
| `PY-IOP-030` | [Filesystem operations, temporary files, and atomicity](CURRICULUM.md#py-iop-030) | Professional | Absent | Not started | — | — | — | — |
| `PY-IOP-040` | [Subprocesses, pipes, exit codes, and signals](CURRICULUM.md#py-iop-040) | Core | Absent | Not started | — | — | — | — |
| `PY-IOP-050` | [JSON, CSV, TOML, and configuration formats](CURRICULUM.md#py-iop-050) | Core | Absent | Not started | — | — | — | — |
| `PY-IOP-060` | [Pickle, shelve, copying, and object graphs](CURRICULUM.md#py-iop-060) | Professional | Absent | Not started | — | — | — | — |
| `PY-IOP-070` | [Regular expressions, argparse, and command-line processing](CURRICULUM.md#py-iop-070) | Professional | Absent | Not started | — | — | — | — |
| `PY-IOP-080` | [Networking foundations with socket, SSL, HTTP, URL, and email tools](CURRICULUM.md#py-iop-080) | Professional | Absent | Not started | — | — | — | — |
| `PY-IOP-090` | [Streaming large data and bounded processing](CURRICULUM.md#py-iop-090) | Core | Absent | Not started | — | — | — | — |
| `PY-TST-010` | [Testing principles, unittest, and doctest](CURRICULUM.md#py-tst-010) | Core | Absent | Not started | — | — | — | — |
| `PY-TST-020` | [Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020) | Core | Absent | Not started | — | — | — | — |
| `PY-TST-030` | [Parametrization, marks, monkeypatching, and fixture composition](CURRICULUM.md#py-tst-030) | Core | Absent | Not started | — | — | — | — |
| `PY-TST-040` | [Test doubles, mocking, and patching boundaries](CURRICULUM.md#py-tst-040) | Core | Absent | Not started | — | — | — | — |
| `PY-TST-050` | [Property-based testing, coverage, and mutation concepts](CURRICULUM.md#py-tst-050) | Professional | Absent | Not started | — | — | — | — |
| `PY-TST-060` | [Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060) | Core | Absent | Not started | — | — | — | — |
| `PY-TST-070` | [Formatting, linting, static analysis, and maintainability](CURRICULUM.md#py-tst-070) | Core | Absent | Not started | — | — | — | — |
| `PY-CON-010` | [Concurrency, parallelism, scheduling, and the GIL model](CURRICULUM.md#py-con-010) | Core | Draft | Not started | — | — | — | [Unit note](units/concurrency/PY-CON-010-concurrency-parallelism-scheduling-and-the-gil-model/README.md) |
| `PY-CON-020` | [Threads, lifecycle, context, and thread-safe boundaries](CURRICULUM.md#py-con-020) | Core | Draft | Not started | — | — | — | [Unit note](units/concurrency/PY-CON-020-threads-lifecycle-context-and-thread-safe-boundaries/README.md) |
| `PY-CON-030` | [Synchronization, queues, races, and deadlocks](CURRICULUM.md#py-con-030) | Core | Draft | Not started | — | — | — | [Unit note](units/concurrency/PY-CON-030-synchronization-queues-races-and-deadlocks/README.md) |
| `PY-CON-040` | [Multiprocessing, IPC, shared memory, and process isolation](CURRICULUM.md#py-con-040) | Professional | Draft | Not started | — | — | — | [Unit note](units/concurrency/PY-CON-040-multiprocessing-ipc-shared-memory-and-process-isolation/README.md) |
| `PY-CON-050` | [Futures and executors](CURRICULUM.md#py-con-050) | Core | Draft | Not started | — | — | — | [Unit note](units/concurrency/PY-CON-050-futures-and-executors/README.md) |
| `PY-CON-060` | [Asyncio event loop, coroutines, tasks, and context](CURRICULUM.md#py-con-060) | Core | Draft | Not started | — | — | — | [Unit note](units/concurrency/PY-CON-060-asyncio-event-loop-coroutines-tasks-and-context/README.md) |
| `PY-CON-070` | [Structured concurrency, cancellation, and timeouts](CURRICULUM.md#py-con-070) | Core | Draft | Not started | — | — | — | [Unit note](units/concurrency/PY-CON-070-structured-concurrency-cancellation-and-timeouts/README.md) |
| `PY-CON-080` | [Async queues, backpressure, async iteration, and blocking boundaries](CURRICULUM.md#py-con-080) | Core | Draft | Not started | — | — | — | [Unit note](units/concurrency/PY-CON-080-async-queues-backpressure-async-iteration-and-blocking-boundaries/README.md) |
| `PY-CON-090` | [Free-threaded CPython, subinterpreters, and version-specific GIL changes](CURRICULUM.md#py-con-090) | Advanced | Draft | Not started | — | — | — | [Unit note](units/concurrency/PY-CON-090-free-threaded-cpython-subinterpreters-and-version-specific-gil-changes/README.md) |
| `PY-MPR-010` | [Object lifetime, reference counting, finalization, and weak references](CURRICULUM.md#py-mpr-010) | Core | Absent | Not started | — | — | — | — |
| `PY-MPR-020` | [Cyclic garbage collection and gc inspection](CURRICULUM.md#py-mpr-020) | Professional | Absent | Not started | — | — | — | — |
| `PY-MPR-030` | [Stack, frame, heap, call, and local-variable mental models](CURRICULUM.md#py-mpr-030) | Core | Absent | Not started | — | — | — | — |
| `PY-MPR-040` | [Object sizing, interning, caches, and shallow measurements](CURRICULUM.md#py-mpr-040) | Professional | Absent | Not started | — | — | — | — |
| `PY-MPR-050` | [CPython small-object allocation and fragmentation](CURRICULUM.md#py-mpr-050) | Advanced | Absent | Not started | — | — | — | — |
| `PY-MPR-060` | [Memory-growth and leak diagnosis](CURRICULUM.md#py-mpr-060) | Professional | Absent | Not started | — | — | — | — |
| `PY-MPR-070` | [Algorithmic and memory complexity](CURRICULUM.md#py-mpr-070) | Core | Absent | Not started | — | — | — | — |
| `PY-MPR-080` | [Responsible benchmarking](CURRICULUM.md#py-mpr-080) | Core | Absent | Not started | — | — | — | — |
| `PY-MPR-090` | [Profiling and tracing](CURRICULUM.md#py-mpr-090) | Core | Absent | Not started | — | — | — | — |
| `PY-MPR-100` | [Performance optimization strategy](CURRICULUM.md#py-mpr-100) | Core | Absent | Not started | — | — | — | — |
| `PY-SEC-010` | [Validation, trust boundaries, and resource exhaustion](CURRICULUM.md#py-sec-010) | Core | Absent | Not started | — | — | — | — |
| `PY-SEC-020` | [Deserialization, command, path, and temporary-file security](CURRICULUM.md#py-sec-020) | Core | Absent | Not started | — | — | — | — |
| `PY-SEC-030` | [Randomness, secrets, hashes, HMAC, UUIDs, and sensitive logs](CURRICULUM.md#py-sec-030) | Core | Absent | Not started | — | — | — | — |
| `PY-SEC-040` | [Dependency, credential, configuration, and supply-chain security](CURRICULUM.md#py-sec-040) | Professional | Absent | Not started | — | — | — | — |
| `PY-SEC-050` | [Production configuration, observability, logging, and graceful shutdown](CURRICULUM.md#py-sec-050) | Core | Absent | Not started | — | — | — | — |
| `PY-SEC-060` | [Backend API, database, network, validation, and error boundaries](CURRICULUM.md#py-sec-060) | Core | Absent | Not started | — | — | — | — |
| `PY-SEC-070` | [Async-service deadlines, backpressure, pools, and shutdown](CURRICULUM.md#py-sec-070) | Core | Absent | Not started | — | — | — | — |
| `PY-CPY-010` | [CPython source tree, builds, and focused tests](CURRICULUM.md#py-cpy-010) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-020` | [Tokenizer, PEG parser, grammar, and AST creation](CURRICULUM.md#py-cpy-020) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-030` | [Symbol tables, scope analysis, and compilation](CURRICULUM.md#py-cpy-030) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-040` | [Code objects and CPython bytecode](CURRICULUM.md#py-cpy-040) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-050` | [Frames and the evaluation loop](CURRICULUM.md#py-cpy-050) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-060` | [Function-call mechanics and vectorcall](CURRICULUM.md#py-cpy-060) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-070` | [PyObject, type objects, slots, descriptors, and runtime dispatch](CURRICULUM.md#py-cpy-070) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-080` | [Dictionary, set, list, tuple, and string internals](CURRICULUM.md#py-cpy-080) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-090` | [Allocator, reference-count, garbage-collector, and finalization internals](CURRICULUM.md#py-cpy-090) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-100` | [Adaptive specialization, inline caches, instrumentation, and JIT boundaries](CURRICULUM.md#py-cpy-100) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-110` | [GIL, free-threading, subinterpreters, and extension compatibility](CURRICULUM.md#py-cpy-110) | Advanced | Absent | Not started | — | — | — | — |
| `PY-CPY-120` | [Python/C API, Limited API, and Stable ABI](CURRICULUM.md#py-cpy-120) | Reference | Absent | Not started | — | — | — | — |
| `PY-CPY-130` | [Alternative interpreters and portability](CURRICULUM.md#py-cpy-130) | Advanced | Absent | Not started | — | — | — | — |
| `PY-INT-010` | [Python traps and output-prediction reasoning](CURRICULUM.md#py-int-010) | Core | Absent | Not started | — | — | — | — |
| `PY-INT-020` | [Debugging, refactoring, and senior code review](CURRICULUM.md#py-int-020) | Core | Absent | Not started | — | — | — | — |
| `PY-INT-030` | [Pythonic implementation exercises](CURRICULUM.md#py-int-030) | Core | Absent | Not started | — | — | — | — |
| `PY-INT-040` | [Senior backend and API design interviews in Python](CURRICULUM.md#py-int-040) | Core | Absent | Not started | — | — | — | — |
| `PY-INT-050` | [Performance, concurrency, memory, and CPython interviews](CURRICULUM.md#py-int-050) | Core | Absent | Not started | — | — | — | — |
| `PY-INT-060` | [Integrated Python mastery capstone](CURRICULUM.md#py-int-060) | Professional | Absent | Not started | — | — | — | — |


## Project tracker

Project state is separate from curriculum learning state. Project completion may provide linked transfer evidence, but it never automatically advances a curriculum-unit learning state.

| Project ID | Project name | Project state | Branch | Last evidence date | Evidence link | Remaining weakness or unfinished requirement |
|---|---|---|---|---|---|---|
| [`PY-PRJ-010`](PROJECTS.md#py-prj-010) | [Streaming Log Investigator CLI](PROJECTS.md#py-prj-010) | Planned | `project/PY-PRJ-010` | — | — | — |
| [`PY-PRJ-020`](PROJECTS.md#py-prj-020) | [Typed and Packaged Data-Normalization Library](PROJECTS.md#py-prj-020) | Planned | `project/PY-PRJ-020` | — | — | — |
| [`PY-PRJ-030`](PROJECTS.md#py-prj-030) | [Typed Rule and Plugin Engine](PROJECTS.md#py-prj-030) | Planned | `project/PY-PRJ-030` | — | — | — |
| [`PY-PRJ-040`](PROJECTS.md#py-prj-040) | [Asynchronous Job Runner](PROJECTS.md#py-prj-040) | Planned | `project/PY-PRJ-040` | — | — | — |
| [`PY-PRJ-050`](PROJECTS.md#py-prj-050) | [Performance and Memory Optimisation Clinic](PROJECTS.md#py-prj-050) | Planned | `project/PY-PRJ-050` | — | — | — |
| [`PY-PRJ-060`](PROJECTS.md#py-prj-060) | [CPython Behaviour Explorer](PROJECTS.md#py-prj-060) | Planned | `project/PY-PRJ-060` | — | — | — |

Project states:

```text
Planned → Active → Complete
```

- `Planned`: no project folder is required.
- `Active`: the exact project branch and just-in-time folder exist.
- `Complete`: the project definition of done is satisfied and concrete evidence is linked.
- A project may remain complete locally without being published.
- Update unit learning states separately and only against their own evidence rules.

## Update rules

- Use complete canonical IDs everywhere.
- On initialization, set artifact state to `Draft`; do not advance learning state merely because notes were generated.
- Link evidence only after the target file or heading exists.
- Record precise weaknesses such as “Confuses rebinding with mutating the referenced list.”
- A failed review may move a unit backward.
- Domain progress is a count-based roll-up; domains do not receive separate mastery claims.
