# Python Mastery Milestone Projects

[Curriculum](CURRICULUM.md) · [Learning paths](LEARNING_PATHS.md) · [Project template](templates/project.md)

Milestone projects integrate completed learning units. They are **not additional curriculum units** and do not change the 121-unit count.

- Project IDs are stable.
- Project folders are created only when a project starts.
- Each project uses one dedicated project chat.
- Projects remain Python-focused and avoid becoming framework, database, cloud, or system-design curricula.

## Project overview

| Project ID | Project | Main integration |
|---|---|---|
| [PY-PRJ-010](#py-prj-010) | [Streaming Log Investigator CLI](#py-prj-010) | Files, generators, parsing, containers, CLI design, testing |
| [PY-PRJ-020](#py-prj-020) | [Typed and Packaged Data-Normalization Library](#py-prj-020) | Functions, typing, packaging, reusable APIs, testing |
| [PY-PRJ-030](#py-prj-030) | [Typed Rule and Plugin Engine](#py-prj-030) | Object model, protocols, imports, registration, extensibility |
| [PY-PRJ-040](#py-prj-040) | [Asynchronous Job Runner](#py-prj-040) | Asyncio, cancellation, backpressure, resource safety |
| [PY-PRJ-050](#py-prj-050) | [Performance and Memory Optimisation Clinic](#py-prj-050) | Profiling, benchmarking, memory diagnosis, refactoring |
| [PY-PRJ-060](#py-prj-060) | [CPython Behaviour Explorer](#py-prj-060) | AST, bytecode, frames, lookup, garbage collection, specialization, portability |

<a id="py-prj-010"></a>
## PY-PRJ-010 — Streaming Log Investigator CLI

**Purpose:** Build a command-line application that incrementally processes large text and JSON-lines log files without loading the complete input into memory.

### Required prerequisites

- [`PY-FND-020` — Objects, names, references, and mutability](CURRICULUM.md#py-fnd-020)
- [`PY-FND-030` — Namespaces, scope, and name resolution](CURRICULUM.md#py-fnd-030)
- [`PY-FND-060` — Control flow and structural pattern matching](CURRICULUM.md#py-fnd-060)
- [`PY-BLT-020` — Strings and Unicode](CURRICULUM.md#py-blt-020)
- [`PY-BLT-040` — Lists, tuples, ranges, and sequence behaviour](CURRICULUM.md#py-blt-040)
- [`PY-BLT-050` — Dictionaries and mapping behaviour](CURRICULUM.md#py-blt-050)
- [`PY-BLT-070` — Unpacking, comprehensions, and generator expressions](CURRICULUM.md#py-blt-070)
- [`PY-FIT-010` — Function definitions, calls, returns, and first-class behaviour](CURRICULUM.md#py-fit-010)
- [`PY-FIT-070` — Iterable and iterator protocols](CURRICULUM.md#py-fit-070)
- [`PY-FIT-080` — Generators, yield, and delegation](CURRICULUM.md#py-fit-080)
- [`PY-FIT-090` — Lazy pipelines and streaming transformations](CURRICULUM.md#py-fit-090)
- [`PY-ERR-010` — Exception flow and exception-safe control](CURRICULUM.md#py-err-010)
- [`PY-ERR-030` — Context managers and resource safety](CURRICULUM.md#py-err-030)
- [`PY-IOP-010` — Text and binary files, streams, buffering, and encodings](CURRICULUM.md#py-iop-010)
- [`PY-IOP-020` — Pathlib, os, glob, and portable path handling](CURRICULUM.md#py-iop-020)
- [`PY-IOP-050` — JSON, CSV, TOML, and configuration formats](CURRICULUM.md#py-iop-050)
- [`PY-IOP-070` — Regular expressions, argparse, and command-line processing](CURRICULUM.md#py-iop-070)
- [`PY-IOP-090` — Streaming large data and bounded processing](CURRICULUM.md#py-iop-090)
- [`PY-TST-020` — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
- [`PY-TST-030` — Parametrization, marks, monkeypatching, and fixture composition](CURRICULUM.md#py-tst-030)
- [`PY-TST-060` — Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060)
- [`PY-MPR-070` — Algorithmic and memory complexity](CURRICULUM.md#py-mpr-070)

### Recommended prerequisites

- [`PY-LIB-010` — Collections: counting, defaults, mappings, and records](CURRICULUM.md#py-lib-010)
- [`PY-LIB-020` — Deque and queue-like patterns](CURRICULUM.md#py-lib-020)
- [`PY-LIB-030` — Iterator algebra with itertools](CURRICULUM.md#py-lib-030)
- [`PY-TYP-020` — Core annotations, unions, literals, and narrowing](CURRICULUM.md#py-typ-020)
- [`PY-SEC-010` — Validation, trust boundaries, and resource exhaustion](CURRICULUM.md#py-sec-010)

### Required functionality

- Stream plain-text and JSON-lines input from files or standard input.
- Filter by level, time range, component, or keyword.
- Aggregate counts and top recurring messages.
- Produce text, JSON, and CSV summaries.
- Apply an explicit malformed-line policy.
- Avoid unbounded application-level buffering.
- Return meaningful exit codes and command-line help.

### Required engineering evidence

- Generator-based pipeline with explicit text and binary boundaries.
- Unit and integration tests using temporary files.
- At least one property-based invariant, such as aggregation totals.
- Complexity and memory explanation.
- Design comparison between eager and lazy processing.

### Debugging and refactoring opportunities

- Accidental full-file materialization.
- Incorrect final-line handling when no newline is present.
- Mutable default configuration state.
- An overly broad exception handler.
- Incorrect Unicode or binary-boundary handling.

### Definition of done

- [ ] Large inputs are processed through a bounded pipeline.
- [ ] Tests cover empty input, malformed records, Unicode, and interrupted output.
- [ ] The architecture and container choices are defended in a senior-interview walkthrough.
- [ ] Required tests pass.
- [ ] At least two seeded defects were diagnosed and fixed.
- [ ] At least one meaningful refactoring was defended.
- [ ] Design decisions and rejected alternatives are documented.
- [ ] Relevant unit evidence links are recorded without automatic status inflation.
- [ ] A final senior-interview walkthrough was completed.

<a id="py-prj-020"></a>
## PY-PRJ-020 — Typed and Packaged Data-Normalization Library

**Purpose:** Build a reusable Python library that validates, transforms, and normalizes dictionary-like records through a configurable pipeline.

### Required prerequisites

- [`PY-FIT-010` — Function definitions, calls, returns, and first-class behaviour](CURRICULUM.md#py-fit-010)
- [`PY-FIT-020` — Parameter binding and argument evaluation](CURRICULUM.md#py-fit-020)
- [`PY-FIT-030` — Higher-order functions, callable objects, and side effects](CURRICULUM.md#py-fit-030)
- [`PY-FIT-050` — Decorators](CURRICULUM.md#py-fit-050)
- [`PY-OBJ-010` — Classes, instances, methods, and construction](CURRICULUM.md#py-obj-010)
- [`PY-OBJ-020` — Properties, encapsulation, and composition](CURRICULUM.md#py-obj-020)
- [`PY-ERR-010` — Exception flow and exception-safe control](CURRICULUM.md#py-err-010)
- [`PY-ERR-020` — Custom exceptions, chaining, warnings, and exception groups](CURRICULUM.md#py-err-020)
- [`PY-MOD-010` — Modules, packages, and executable modules](CURRICULUM.md#py-mod-010)
- [`PY-MOD-050` — Python versions and virtual environments](CURRICULUM.md#py-mod-050)
- [`PY-MOD-060` — Pyproject, dependencies, locking, and reproducibility](CURRICULUM.md#py-mod-060)
- [`PY-MOD-070` — Package layouts, resources, entry points, and plugin boundaries](CURRICULUM.md#py-mod-070)
- [`PY-MOD-080` — Build systems, distributions, publishing, and supply-chain boundaries](CURRICULUM.md#py-mod-080)
- [`PY-TYP-010` — Annotation semantics and static analysis boundaries](CURRICULUM.md#py-typ-010)
- [`PY-TYP-020` — Core annotations, unions, literals, and narrowing](CURRICULUM.md#py-typ-020)
- [`PY-TYP-030` — Generics and type variables](CURRICULUM.md#py-typ-030)
- [`PY-TYP-050` — Protocols, ABCs, and structural versus nominal typing](CURRICULUM.md#py-typ-050)
- [`PY-TYP-080` — Static-analysis tools, stubs, and gradual adoption](CURRICULUM.md#py-typ-080)
- [`PY-LIB-060` — Dataclasses, enums, types, and generated data models](CURRICULUM.md#py-lib-060)
- [`PY-TST-020` — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
- [`PY-TST-030` — Parametrization, marks, monkeypatching, and fixture composition](CURRICULUM.md#py-tst-030)
- [`PY-TST-040` — Test doubles, mocking, and patching boundaries](CURRICULUM.md#py-tst-040)
- [`PY-TST-050` — Property-based testing, coverage, and mutation concepts](CURRICULUM.md#py-tst-050)
- [`PY-TST-070` — Formatting, linting, static analysis, and maintainability](CURRICULUM.md#py-tst-070)

### Recommended prerequisites

- [`PY-IOP-050` — JSON, CSV, TOML, and configuration formats](CURRICULUM.md#py-iop-050)
- [`PY-SEC-040` — Dependency, credential, configuration, and supply-chain security](CURRICULUM.md#py-sec-040)

### Required functionality

- Typed input and output boundaries.
- Composable normalization steps.
- A coherent field-level error model.
- Immutable or copy-on-write transformation where appropriate.
- A stable public API and runnable entry point.
- Wheel and source-distribution builds.
- Installation and testing from the built wheel in an isolated environment.

### Required engineering evidence

- `src/` package layout and `pyproject.toml`.
- Static type checking and public API documentation.
- Unit, integration, and property-based tests.
- Semantic-versioning and compatibility decisions.
- Python 3.11 alternatives for post-3.11 typing syntax.

### Debugging and refactoring opportunities

- A decorator that loses function metadata.
- Internal helpers accidentally exposed as public API.
- Incorrect generic return types.
- Tests patching the wrong import namespace.
- An inheritance-heavy design refactored toward composition or callable protocols.

### Definition of done

- [ ] A clean wheel installs and imports in a fresh environment.
- [ ] Tests run against the installed artifact.
- [ ] The package boundary, type design, compatibility policy, and API stability are defended.
- [ ] Required tests pass.
- [ ] At least two seeded defects were diagnosed and fixed.
- [ ] At least one meaningful refactoring was defended.
- [ ] Design decisions and rejected alternatives are documented.
- [ ] Relevant unit evidence links are recorded without automatic status inflation.
- [ ] A final senior-interview walkthrough was completed.

<a id="py-prj-030"></a>
## PY-PRJ-030 — Typed Rule and Plugin Engine

**Purpose:** Build an extensible Python rule engine that discovers and executes independently developed rule plugins.

### Required prerequisites

- [`PY-OBJ-010` — Classes, instances, methods, and construction](CURRICULUM.md#py-obj-010)
- [`PY-OBJ-020` — Properties, encapsulation, and composition](CURRICULUM.md#py-obj-020)
- [`PY-OBJ-030` — Inheritance, MRO, and super](CURRICULUM.md#py-obj-030)
- [`PY-OBJ-040` — Python data model and special methods](CURRICULUM.md#py-obj-040)
- [`PY-OBJ-050` — Attribute lookup, customization, and slots](CURRICULUM.md#py-obj-050)
- [`PY-OBJ-070` — Class-creation hooks and class decorators](CURRICULUM.md#py-obj-070)
- [`PY-OBJ-090` — Introspection, reflection, and monkey patching](CURRICULUM.md#py-obj-090)
- [`PY-MOD-020` — Import resolution, sys.path, and module caching](CURRICULUM.md#py-mod-020)
- [`PY-MOD-030` — Circular imports and package boundaries](CURRICULUM.md#py-mod-030)
- [`PY-MOD-040` — Importlib, import hooks, and namespace packages](CURRICULUM.md#py-mod-040)
- [`PY-MOD-070` — Package layouts, resources, entry points, and plugin boundaries](CURRICULUM.md#py-mod-070)
- [`PY-TYP-030` — Generics and type variables](CURRICULUM.md#py-typ-030)
- [`PY-TYP-040` — Variance and safe generic API design](CURRICULUM.md#py-typ-040)
- [`PY-TYP-050` — Protocols, ABCs, and structural versus nominal typing](CURRICULUM.md#py-typ-050)
- [`PY-TYP-060` — Callable typing, overloads, ParamSpec, and Self](CURRICULUM.md#py-typ-060)
- [`PY-TYP-070` — Typed records and advanced narrowing](CURRICULUM.md#py-typ-070)
- [`PY-TST-020` — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
- [`PY-TST-040` — Test doubles, mocking, and patching boundaries](CURRICULUM.md#py-tst-040)
- [`PY-TST-050` — Property-based testing, coverage, and mutation concepts](CURRICULUM.md#py-tst-050)
- [`PY-TST-070` — Formatting, linting, static analysis, and maintainability](CURRICULUM.md#py-tst-070)

### Recommended prerequisites

- [`PY-OBJ-060` — Descriptors](CURRICULUM.md#py-obj-060)
- [`PY-OBJ-080` — Metaclasses and dynamic class creation](CURRICULUM.md#py-obj-080)
- [`PY-LIB-040` — Callable transformation with functools and operator](CURRICULUM.md#py-lib-040)
- [`PY-SEC-010` — Validation, trust boundaries, and resource exhaustion](CURRICULUM.md#py-sec-010)

### Required functionality

- A typed rule interface.
- Explicit or documented plugin discovery.
- Rule metadata and dependencies.
- Deterministic execution order.
- Duplicate-registration and dependency-cycle detection.
- An explicit rule-failure policy.
- A synchronous, framework-independent core.

### Required engineering evidence

- Protocol-versus-ABC comparison.
- Registration decorator versus `__init_subclass__` comparison.
- Explicit imports versus dynamic discovery.
- Class-based rules versus callable objects.
- A reasoned rejection or acceptance of metaclasses.

### Debugging and refactoring opportunities

- Import-time side effects causing duplicate registration.
- Circular imports between plugins.
- Registry state leaking between tests.
- Incorrect variance in a rule interface.
- An unnecessary metaclass refactored to a simpler hook.

### Definition of done

- [ ] Multiple plugins load independently and execute deterministically.
- [ ] Tests cover cycles, duplicates, ordering, and failures.
- [ ] The extension mechanism and rejected alternatives are defended.
- [ ] Required tests pass.
- [ ] At least two seeded defects were diagnosed and fixed.
- [ ] At least one meaningful refactoring was defended.
- [ ] Design decisions and rejected alternatives are documented.
- [ ] Relevant unit evidence links are recorded without automatic status inflation.
- [ ] A final senior-interview walkthrough was completed.

<a id="py-prj-040"></a>
## PY-PRJ-040 — Asynchronous Job Runner

**Purpose:** Build a local asynchronous job runner with bounded work, cancellation, timeouts, retries, graceful shutdown, and backpressure.

### Required prerequisites

- [`PY-ERR-020` — Custom exceptions, chaining, warnings, and exception groups](CURRICULUM.md#py-err-020)
- [`PY-ERR-030` — Context managers and resource safety](CURRICULUM.md#py-err-030)
- [`PY-CON-010` — Concurrency, parallelism, scheduling, and the GIL model](CURRICULUM.md#py-con-010)
- [`PY-CON-020` — Threads, lifecycle, context, and thread-safe boundaries](CURRICULUM.md#py-con-020)
- [`PY-CON-030` — Synchronization, queues, races, and deadlocks](CURRICULUM.md#py-con-030)
- [`PY-CON-050` — Futures and executors](CURRICULUM.md#py-con-050)
- [`PY-CON-060` — Asyncio event loop, coroutines, tasks, and context](CURRICULUM.md#py-con-060)
- [`PY-CON-070` — Structured concurrency, cancellation, and timeouts](CURRICULUM.md#py-con-070)
- [`PY-CON-080` — Async queues, backpressure, async iteration, and blocking boundaries](CURRICULUM.md#py-con-080)
- [`PY-IOP-040` — Subprocesses, pipes, exit codes, and signals](CURRICULUM.md#py-iop-040)
- [`PY-TST-020` — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
- [`PY-TST-030` — Parametrization, marks, monkeypatching, and fixture composition](CURRICULUM.md#py-tst-030)
- [`PY-TST-040` — Test doubles, mocking, and patching boundaries](CURRICULUM.md#py-tst-040)
- [`PY-TST-060` — Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060)
- [`PY-SEC-010` — Validation, trust boundaries, and resource exhaustion](CURRICULUM.md#py-sec-010)
- [`PY-SEC-050` — Production configuration, observability, logging, and graceful shutdown](CURRICULUM.md#py-sec-050)
- [`PY-SEC-070` — Async-service deadlines, backpressure, pools, and shutdown](CURRICULUM.md#py-sec-070)

### Recommended prerequisites

- [`PY-CON-040` — Multiprocessing, IPC, shared memory, and process isolation](CURRICULUM.md#py-con-040)
- [`PY-MPR-080` — Responsible benchmarking](CURRICULUM.md#py-mpr-080)
- [`PY-MPR-090` — Profiling and tracing](CURRICULUM.md#py-mpr-090)
- [`PY-TYP-060` — Callable typing, overloads, ParamSpec, and Self](CURRICULUM.md#py-typ-060)

### Required functionality

- A bounded incoming queue and configurable worker count.
- Per-job timeouts and structured task ownership.
- Graceful cancellation and shutdown.
- An explicit retryability boundary.
- Offloading of blocking work.
- Structured job-state events or logs.
- No real distributed queue or cloud service.

### Required engineering evidence

- Deterministic tests for cancellation, timeouts, backpressure, worker failure, retries, and shutdown.
- An event-loop timeline and task-ownership explanation.
- A reasoned blocking-work strategy.
- Clear cleanup and error-propagation trade-offs.

### Debugging and refactoring opportunities

- A blocking function called directly in the event loop.
- Tasks created without retained ownership.
- Cancellation swallowed by broad exception handling.
- Unbounded queue growth.
- Shutdown that cancels tasks without awaiting cleanup.

### Definition of done

- [ ] No orphaned task remains after normal shutdown.
- [ ] Queue growth is bounded.
- [ ] Cancellation and timeout behaviour are proven through tests.
- [ ] The backpressure design is defended in a senior interview.
- [ ] Required tests pass.
- [ ] At least two seeded defects were diagnosed and fixed.
- [ ] At least one meaningful refactoring was defended.
- [ ] Design decisions and rejected alternatives are documented.
- [ ] Relevant unit evidence links are recorded without automatic status inflation.
- [ ] A final senior-interview walkthrough was completed.

<a id="py-prj-050"></a>
## PY-PRJ-050 — Performance and Memory Optimisation Clinic

**Purpose:** Measure, diagnose, and improve an intentionally inefficient Python data-processing program without changing externally observable behaviour.

### Required prerequisites

- [`PY-BLT-040` — Lists, tuples, ranges, and sequence behaviour](CURRICULUM.md#py-blt-040)
- [`PY-BLT-050` — Dictionaries and mapping behaviour](CURRICULUM.md#py-blt-050)
- [`PY-BLT-060` — Sets and frozensets](CURRICULUM.md#py-blt-060)
- [`PY-FIT-090` — Lazy pipelines and streaming transformations](CURRICULUM.md#py-fit-090)
- [`PY-MPR-010` — Object lifetime, reference counting, finalization, and weak references](CURRICULUM.md#py-mpr-010)
- [`PY-MPR-020` — Cyclic garbage collection and gc inspection](CURRICULUM.md#py-mpr-020)
- [`PY-MPR-030` — Stack, frame, heap, call, and local-variable mental models](CURRICULUM.md#py-mpr-030)
- [`PY-MPR-040` — Object sizing, interning, caches, and shallow measurements](CURRICULUM.md#py-mpr-040)
- [`PY-MPR-060` — Memory-growth and leak diagnosis](CURRICULUM.md#py-mpr-060)
- [`PY-MPR-070` — Algorithmic and memory complexity](CURRICULUM.md#py-mpr-070)
- [`PY-MPR-080` — Responsible benchmarking](CURRICULUM.md#py-mpr-080)
- [`PY-MPR-090` — Profiling and tracing](CURRICULUM.md#py-mpr-090)
- [`PY-MPR-100` — Performance optimization strategy](CURRICULUM.md#py-mpr-100)
- [`PY-TST-020` — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
- [`PY-TST-050` — Property-based testing, coverage, and mutation concepts](CURRICULUM.md#py-tst-050)
- [`PY-TST-060` — Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060)

### Recommended prerequisites

- [`PY-MPR-050` — CPython small-object allocation and fragmentation](CURRICULUM.md#py-mpr-050)
- [`PY-CON-010` — Concurrency, parallelism, scheduling, and the GIL model](CURRICULUM.md#py-con-010)
- [`PY-LIB-030` — Iterator algebra with itertools](CURRICULUM.md#py-lib-030)
- [`PY-LIB-040` — Callable transformation with functools and operator](CURRICULUM.md#py-lib-040)
- [`PY-LIB-050` — Heap, bisection, and compact-array tools](CURRICULUM.md#py-lib-050)

### Required functionality

- A preserved behavioural test suite.
- A representative, recorded workload.
- CPU and allocation profiling.
- Explicit optimization hypotheses.
- One meaningful change per measurement cycle.
- A final report with trade-offs and rejected ideas.

### Required engineering evidence

- Environment-recorded benchmarks.
- Profiler and `tracemalloc` evidence.
- Algorithmic-complexity analysis.
- Before-and-after code review.
- A clear distinction between algorithmic and CPython-specific effects.

### Debugging and refactoring opportunities

- Accidental quadratic behaviour.
- Repeated list or string allocation.
- Unnecessary iterator materialization.
- Poor container selection.
- Retained references causing memory growth.
- Misleading use of `sys.getsizeof`.

### Definition of done

- [ ] All behavioural tests remain green.
- [ ] Every claimed improvement has actual recorded evidence.
- [ ] At least one optimization is rejected for lack of evidence or unacceptable trade-offs.
- [ ] Required tests pass.
- [ ] At least two seeded defects were diagnosed and fixed.
- [ ] At least one meaningful refactoring was defended.
- [ ] Design decisions and rejected alternatives are documented.
- [ ] Relevant unit evidence links are recorded without automatic status inflation.
- [ ] A final senior-interview walkthrough was completed.

<a id="py-prj-060"></a>
## PY-PRJ-060 — CPython Behaviour Explorer

**Purpose:** Build a version-labelled toolkit for exploring source transformations and CPython runtime behaviour.

### Required prerequisites

- [`PY-OBJ-050` — Attribute lookup, customization, and slots](CURRICULUM.md#py-obj-050)
- [`PY-OBJ-060` — Descriptors](CURRICULUM.md#py-obj-060)
- [`PY-MOD-020` — Import resolution, sys.path, and module caching](CURRICULUM.md#py-mod-020)
- [`PY-MPR-010` — Object lifetime, reference counting, finalization, and weak references](CURRICULUM.md#py-mpr-010)
- [`PY-MPR-020` — Cyclic garbage collection and gc inspection](CURRICULUM.md#py-mpr-020)
- [`PY-MPR-030` — Stack, frame, heap, call, and local-variable mental models](CURRICULUM.md#py-mpr-030)
- [`PY-CPY-010` — CPython source tree, builds, and focused tests](CURRICULUM.md#py-cpy-010)
- [`PY-CPY-020` — Tokenizer, PEG parser, grammar, and AST creation](CURRICULUM.md#py-cpy-020)
- [`PY-CPY-030` — Symbol tables, scope analysis, and compilation](CURRICULUM.md#py-cpy-030)
- [`PY-CPY-040` — Code objects and CPython bytecode](CURRICULUM.md#py-cpy-040)
- [`PY-CPY-050` — Frames and the evaluation loop](CURRICULUM.md#py-cpy-050)
- [`PY-CPY-060` — Function-call mechanics and vectorcall](CURRICULUM.md#py-cpy-060)
- [`PY-CPY-070` — PyObject, type objects, slots, descriptors, and runtime dispatch](CURRICULUM.md#py-cpy-070)
- [`PY-CPY-080` — Dictionary, set, list, tuple, and string internals](CURRICULUM.md#py-cpy-080)
- [`PY-CPY-090` — Allocator, reference-count, garbage-collector, and finalization internals](CURRICULUM.md#py-cpy-090)
- [`PY-CPY-100` — Adaptive specialization, inline caches, instrumentation, and JIT boundaries](CURRICULUM.md#py-cpy-100)
- [`PY-CON-090` — Free-threaded CPython, subinterpreters, and version-specific GIL changes](CURRICULUM.md#py-con-090)
- [`PY-TST-020` — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
- [`PY-TST-060` — Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060)

### Recommended prerequisites

- [`PY-CPY-110` — GIL, free-threading, subinterpreters, and extension compatibility](CURRICULUM.md#py-cpy-110)
- [`PY-CPY-120` — Python/C API, Limited API, and Stable ABI](CURRICULUM.md#py-cpy-120)
- [`PY-CPY-130` — Alternative interpreters and portability](CURRICULUM.md#py-cpy-130)

### Required functionality

- Display source text and AST structure.
- Show code-object metadata and disassembly.
- Inspect closure cells and free variables.
- Demonstrate descriptor lookup precedence.
- Trace import caching and cyclic-GC behaviour.
- Observe specialization where supported.
- Label every output with interpreter and version information.

### Required engineering evidence

- Structural tests that avoid brittle exact-bytecode assertions.
- Explicit Python-semantics versus CPython-observation labels.
- Python 3.11 and 3.14 comparison notes where meaningful.
- Question, prediction, observation, and limitation for every explorer command.

### Debugging and refactoring opportunities

- An exact-opcode test that breaks across versions.
- Reference-count assumptions used on unsupported interpreters.
- A conceptual frame diagram presented as literal layout.
- Specialization claims made before warm-up or without version context.

### Definition of done

- [ ] Unsupported interpreters or builds fail clearly.
- [ ] Every command records its question, observation, and limitation.
- [ ] The final walkthrough identifies at least one observation that changed an earlier mental model.
- [ ] Required tests pass.
- [ ] At least two seeded defects were diagnosed and fixed.
- [ ] At least one meaningful refactoring was defended.
- [ ] Design decisions and rejected alternatives are documented.
- [ ] Relevant unit evidence links are recorded without automatic status inflation.
- [ ] A final senior-interview walkthrough was completed.


## Project Git workflow

Projects are integration evidence, not curriculum units. Never interpret a `PY-PRJ-...` ID as a curriculum topic ID, and never update a curriculum-unit learning state merely because a project advances.

### Initialize a project

Open a dedicated Codex Worktree chat from the latest synchronized `main` and say:

```text
Initialize project <PROJECT-ID>.
```

This authorizes Codex to:

1. validate the exact ID in `PROJECTS.md`;
2. verify the latest synchronized `main` baseline for a new branch;
3. fetch and compare an existing exact remote branch safely;
4. create or resume exactly `project/<PROJECT-ID>`;
5. create the just-in-time project folder from `templates/project.md`;
6. update only the matching project tracker row in `PROGRESS.md` to `Active`;
7. run `python scripts/validate_repo.py` plus all relevant project tests;
8. commit the initialized project content locally;
9. automatically push the exact project branch with a normal non-force push;
10. set upstream on the first push;
11. report the branch, commit, validation, tests, push result, and changed files.

The initialization push is limited to `project/<PROJECT-ID>`. It does not authorize a pull request, merge, remote `main` change, force-push, failed-check bypass, unrelated-work changes, or a curriculum-state change.

If the exact remote branch already exists, fetch and compare it as described in [`docs/WORKFLOW.md`](docs/WORKFLOW.md). Resume it only when no work can be overwritten or lost. Stop on divergence or any unsafe condition.

Only the successfully validated initialization content is pushed automatically. Later implementation, tests, debugging, refactoring, documentation, and evidence changes may be committed locally but must not be pushed automatically.

### Complete and keep later changes local

```text
I completed project <PROJECT-ID>. Keep any new changes local and do not push or merge.
```

This authorizes final local validation, an accurate project tracker update, and local commits only. The project branch already has its initialized version on GitHub; any newer changes remain in the pinned local worktree.

### Publish the latest changes and merge

```text
I completed project <PROJECT-ID>. Finalize it, push the latest changes, and merge the project branch into main.
```

This authorizes a normal push of the latest `project/<PROJECT-ID>` changes, pull-request creation when supported, and merge after validation and checks pass. Prefer squash merge. Never force-push, bypass failed checks or branch protection, discard unrelated changes, or claim publication succeeded when it did not.

If completion is stated without a publication choice, ask exactly:

```text
Should I keep the latest changes local, or push them and merge the branch into main?
```

After a project is safely merged and no local work remains, its associated worktree may be archived. Keep project chats and worktrees pinned while they contain unpushed later changes.
