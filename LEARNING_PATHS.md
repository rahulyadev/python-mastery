# Python Mastery Learning Paths

[Back to the canonical curriculum](CURRICULUM.md)

These paths are **recommended views over the same 121 units**. They do not duplicate notes or create new unit IDs. Topics may still be studied in any order; Codex should identify important prerequisites and provide a bridge when needed.

Use the permanent curriculum-helper chat when you are unsure which unit owns a question.

## Choose a path

[Complete Python mastery](#complete-python-mastery) · [Absolute beginner to confident Python programmer](#absolute-beginner) · [Senior Python interview preparation](#python-interview-preparation) · [Backend Python engineer](#backend-python-engineer) · [Standard-library mastery](#standard-library-mastery) · [Async, concurrency, and performance](#async-concurrency-performance) · [CPython and deep internals](#cpython-deep-internals)

<a id="complete-python-mastery"></a>
## Complete Python mastery

**Who it is for:** Experienced learners who want the full language, professional-engineering, performance, concurrency, and CPython curriculum.

**Prerequisite guidance:** Begin with the foundations unless diagnostic evidence shows that a unit is already strong. All 121 units are included, and included prerequisites are ordered before their dependents; the canonical catalog itself remains in its approved order.

### Recommended sequence

#### Foundations and execution

1. [PY-FND-010 — Python syntax and execution](CURRICULUM.md#py-fnd-010)
2. [PY-FND-020 — Objects, names, references, and mutability](CURRICULUM.md#py-fnd-020)
3. [PY-FND-030 — Namespaces, scope, and name resolution](CURRICULUM.md#py-fnd-030)
4. [PY-FND-040 — Expressions, evaluation order, and operators](CURRICULUM.md#py-fnd-040)
5. [PY-FND-050 — Truthiness, comparisons, equality, and identity](CURRICULUM.md#py-fnd-050)
6. [PY-FND-060 — Control flow and structural pattern matching](CURRICULUM.md#py-fnd-060)

#### Built-in types, operations, and functions

7. [PY-BLT-010 — Numbers, booleans, and None](CURRICULUM.md#py-blt-010)
8. [PY-BLT-020 — Strings and Unicode](CURRICULUM.md#py-blt-020)
9. [PY-BLT-030 — Bytes, bytearray, memoryview, and the buffer model](CURRICULUM.md#py-blt-030)
10. [PY-BLT-040 — Lists, tuples, ranges, and sequence behaviour](CURRICULUM.md#py-blt-040)
11. [PY-BLT-050 — Dictionaries and mapping behaviour](CURRICULUM.md#py-blt-050)
12. [PY-BLT-060 — Sets and frozensets](CURRICULUM.md#py-blt-060)
13. [PY-BLT-070 — Unpacking, comprehensions, and generator expressions](CURRICULUM.md#py-blt-070)
14. [PY-BLT-080 — Equality, ordering, hashing, and hashability](CURRICULUM.md#py-blt-080)
15. [PY-BLT-090 — Protocol-facing built-in functions and container complexity](CURRICULUM.md#py-blt-090)

#### Functions, callables, iteration, and laziness

16. [PY-FIT-010 — Function definitions, calls, returns, and first-class behaviour](CURRICULUM.md#py-fit-010)
17. [PY-FIT-020 — Parameter binding and argument evaluation](CURRICULUM.md#py-fit-020)
18. [PY-FIT-030 — Higher-order functions, callable objects, and side effects](CURRICULUM.md#py-fit-030)
19. [PY-FIT-040 — Closures, free variables, and late binding](CURRICULUM.md#py-fit-040)
20. [PY-FIT-050 — Decorators](CURRICULUM.md#py-fit-050)
21. [PY-FIT-060 — Recursion and iterative alternatives](CURRICULUM.md#py-fit-060)
22. [PY-FIT-070 — Iterable and iterator protocols](CURRICULUM.md#py-fit-070)
23. [PY-FIT-080 — Generators, yield, and delegation](CURRICULUM.md#py-fit-080)
24. [PY-FIT-090 — Lazy pipelines and streaming transformations](CURRICULUM.md#py-fit-090)

#### Object model and object-oriented Python

25. [PY-OBJ-010 — Classes, instances, methods, and construction](CURRICULUM.md#py-obj-010)
26. [PY-OBJ-020 — Properties, encapsulation, and composition](CURRICULUM.md#py-obj-020)
27. [PY-OBJ-030 — Inheritance, MRO, and super](CURRICULUM.md#py-obj-030)
28. [PY-OBJ-040 — Python data model and special methods](CURRICULUM.md#py-obj-040)
29. [PY-OBJ-050 — Attribute lookup, customization, and slots](CURRICULUM.md#py-obj-050)
30. [PY-OBJ-060 — Descriptors](CURRICULUM.md#py-obj-060)
31. [PY-OBJ-070 — Class-creation hooks and class decorators](CURRICULUM.md#py-obj-070)
32. [PY-OBJ-080 — Metaclasses and dynamic class creation](CURRICULUM.md#py-obj-080)
33. [PY-OBJ-090 — Introspection, reflection, and monkey patching](CURRICULUM.md#py-obj-090)

#### Exceptions and resource management

34. [PY-ERR-010 — Exception flow and exception-safe control](CURRICULUM.md#py-err-010)
35. [PY-ERR-020 — Custom exceptions, chaining, warnings, and exception groups](CURRICULUM.md#py-err-020)
36. [PY-ERR-030 — Context managers and resource safety](CURRICULUM.md#py-err-030)

#### Modules, imports, packaging, and environments

37. [PY-MOD-010 — Modules, packages, and executable modules](CURRICULUM.md#py-mod-010)
38. [PY-MOD-020 — Import resolution, sys.path, and module caching](CURRICULUM.md#py-mod-020)
39. [PY-MOD-030 — Circular imports and package boundaries](CURRICULUM.md#py-mod-030)
40. [PY-MOD-040 — Importlib, import hooks, and namespace packages](CURRICULUM.md#py-mod-040)
41. [PY-MOD-050 — Python versions and virtual environments](CURRICULUM.md#py-mod-050)
42. [PY-MOD-060 — Pyproject, dependencies, locking, and reproducibility](CURRICULUM.md#py-mod-060)
43. [PY-MOD-070 — Package layouts, resources, entry points, and plugin boundaries](CURRICULUM.md#py-mod-070)
44. [PY-MOD-080 — Build systems, distributions, publishing, and supply-chain boundaries](CURRICULUM.md#py-mod-080)

#### Static typing and interfaces

45. [PY-TYP-010 — Annotation semantics and static analysis boundaries](CURRICULUM.md#py-typ-010)
46. [PY-TYP-020 — Core annotations, unions, literals, and narrowing](CURRICULUM.md#py-typ-020)
47. [PY-TYP-030 — Generics and type variables](CURRICULUM.md#py-typ-030)
48. [PY-TYP-040 — Variance and safe generic API design](CURRICULUM.md#py-typ-040)
49. [PY-TYP-050 — Protocols, ABCs, and structural versus nominal typing](CURRICULUM.md#py-typ-050)
50. [PY-TYP-060 — Callable typing, overloads, ParamSpec, and Self](CURRICULUM.md#py-typ-060)
51. [PY-TYP-070 — Typed records and advanced narrowing](CURRICULUM.md#py-typ-070)
52. [PY-TYP-080 — Static-analysis tools, stubs, and gradual adoption](CURRICULUM.md#py-typ-080)

#### Standard-library data and utility tools

53. [PY-LIB-010 — Collections: counting, defaults, mappings, and records](CURRICULUM.md#py-lib-010)
54. [PY-LIB-020 — Deque and queue-like patterns](CURRICULUM.md#py-lib-020)
55. [PY-LIB-030 — Iterator algebra with itertools](CURRICULUM.md#py-lib-030)
56. [PY-LIB-040 — Callable transformation with functools and operator](CURRICULUM.md#py-lib-040)
57. [PY-LIB-050 — Heap, bisection, and compact-array tools](CURRICULUM.md#py-lib-050)
58. [PY-LIB-060 — Dataclasses, enums, types, and generated data models](CURRICULUM.md#py-lib-060)
59. [PY-LIB-070 — Mathematics, precision, fractions, and statistics](CURRICULUM.md#py-lib-070)
60. [PY-LIB-080 — Dates, times, time zones, and calendars](CURRICULUM.md#py-lib-080)

#### Files, operating systems, formats, and networking

61. [PY-IOP-010 — Text and binary files, streams, buffering, and encodings](CURRICULUM.md#py-iop-010)
62. [PY-IOP-020 — Pathlib, os, glob, and portable path handling](CURRICULUM.md#py-iop-020)
63. [PY-IOP-030 — Filesystem operations, temporary files, and atomicity](CURRICULUM.md#py-iop-030)
64. [PY-IOP-040 — Subprocesses, pipes, exit codes, and signals](CURRICULUM.md#py-iop-040)
65. [PY-IOP-050 — JSON, CSV, TOML, and configuration formats](CURRICULUM.md#py-iop-050)
66. [PY-IOP-060 — Pickle, shelve, copying, and object graphs](CURRICULUM.md#py-iop-060)
67. [PY-IOP-070 — Regular expressions, argparse, and command-line processing](CURRICULUM.md#py-iop-070)
68. [PY-IOP-080 — Networking foundations with socket, SSL, HTTP, URL, and email tools](CURRICULUM.md#py-iop-080)
69. [PY-IOP-090 — Streaming large data and bounded processing](CURRICULUM.md#py-iop-090)

#### Testing, debugging, and engineering quality

70. [PY-TST-010 — Testing principles, unittest, and doctest](CURRICULUM.md#py-tst-010)
71. [PY-TST-020 — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
72. [PY-TST-030 — Parametrization, marks, monkeypatching, and fixture composition](CURRICULUM.md#py-tst-030)
73. [PY-TST-040 — Test doubles, mocking, and patching boundaries](CURRICULUM.md#py-tst-040)
74. [PY-TST-050 — Property-based testing, coverage, and mutation concepts](CURRICULUM.md#py-tst-050)
75. [PY-TST-060 — Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060)
76. [PY-TST-070 — Formatting, linting, static analysis, and maintainability](CURRICULUM.md#py-tst-070)

#### Object-lifecycle prerequisite for free-threaded CPython

77. [PY-MPR-010 — Object lifetime, reference counting, finalization, and weak references](CURRICULUM.md#py-mpr-010)

#### Concurrency, parallelism, and asynchronous Python

78. [PY-CON-010 — Concurrency, parallelism, scheduling, and the GIL model](CURRICULUM.md#py-con-010)
79. [PY-CON-020 — Threads, lifecycle, context, and thread-safe boundaries](CURRICULUM.md#py-con-020)
80. [PY-CON-030 — Synchronization, queues, races, and deadlocks](CURRICULUM.md#py-con-030)
81. [PY-CON-040 — Multiprocessing, IPC, shared memory, and process isolation](CURRICULUM.md#py-con-040)
82. [PY-CON-050 — Futures and executors](CURRICULUM.md#py-con-050)
83. [PY-CON-060 — Asyncio event loop, coroutines, tasks, and context](CURRICULUM.md#py-con-060)
84. [PY-CON-070 — Structured concurrency, cancellation, and timeouts](CURRICULUM.md#py-con-070)
85. [PY-CON-080 — Async queues, backpressure, async iteration, and blocking boundaries](CURRICULUM.md#py-con-080)
86. [PY-CON-090 — Free-threaded CPython, subinterpreters, and version-specific GIL changes](CURRICULUM.md#py-con-090)

#### Memory, object lifecycle, and performance

87. [PY-MPR-020 — Cyclic garbage collection and gc inspection](CURRICULUM.md#py-mpr-020)
88. [PY-MPR-030 — Stack, frame, heap, call, and local-variable mental models](CURRICULUM.md#py-mpr-030)
89. [PY-MPR-040 — Object sizing, interning, caches, and shallow measurements](CURRICULUM.md#py-mpr-040)
90. [PY-MPR-050 — CPython small-object allocation and fragmentation](CURRICULUM.md#py-mpr-050)
91. [PY-MPR-060 — Memory-growth and leak diagnosis](CURRICULUM.md#py-mpr-060)
92. [PY-MPR-070 — Algorithmic and memory complexity](CURRICULUM.md#py-mpr-070)
93. [PY-MPR-080 — Responsible benchmarking](CURRICULUM.md#py-mpr-080)
94. [PY-MPR-090 — Profiling and tracing](CURRICULUM.md#py-mpr-090)
95. [PY-MPR-100 — Performance optimization strategy](CURRICULUM.md#py-mpr-100)

#### Security and production Python

96. [PY-SEC-010 — Validation, trust boundaries, and resource exhaustion](CURRICULUM.md#py-sec-010)
97. [PY-SEC-020 — Deserialization, command, path, and temporary-file security](CURRICULUM.md#py-sec-020)
98. [PY-SEC-030 — Randomness, secrets, hashes, HMAC, UUIDs, and sensitive logs](CURRICULUM.md#py-sec-030)
99. [PY-SEC-040 — Dependency, credential, configuration, and supply-chain security](CURRICULUM.md#py-sec-040)
100. [PY-SEC-050 — Production configuration, observability, logging, and graceful shutdown](CURRICULUM.md#py-sec-050)
101. [PY-SEC-060 — Backend API, database, network, validation, and error boundaries](CURRICULUM.md#py-sec-060)
102. [PY-SEC-070 — Async-service deadlines, backpressure, pools, and shutdown](CURRICULUM.md#py-sec-070)

#### CPython internals

103. [PY-CPY-010 — CPython source tree, builds, and focused tests](CURRICULUM.md#py-cpy-010)
104. [PY-CPY-020 — Tokenizer, PEG parser, grammar, and AST creation](CURRICULUM.md#py-cpy-020)
105. [PY-CPY-030 — Symbol tables, scope analysis, and compilation](CURRICULUM.md#py-cpy-030)
106. [PY-CPY-040 — Code objects and CPython bytecode](CURRICULUM.md#py-cpy-040)
107. [PY-CPY-050 — Frames and the evaluation loop](CURRICULUM.md#py-cpy-050)
108. [PY-CPY-060 — Function-call mechanics and vectorcall](CURRICULUM.md#py-cpy-060)
109. [PY-CPY-070 — PyObject, type objects, slots, descriptors, and runtime dispatch](CURRICULUM.md#py-cpy-070)
110. [PY-CPY-080 — Dictionary, set, list, tuple, and string internals](CURRICULUM.md#py-cpy-080)
111. [PY-CPY-090 — Allocator, reference-count, garbage-collector, and finalization internals](CURRICULUM.md#py-cpy-090)
112. [PY-CPY-100 — Adaptive specialization, inline caches, instrumentation, and JIT boundaries](CURRICULUM.md#py-cpy-100)
113. [PY-CPY-110 — GIL, free-threading, subinterpreters, and extension compatibility](CURRICULUM.md#py-cpy-110)
114. [PY-CPY-120 — Python/C API, Limited API, and Stable ABI](CURRICULUM.md#py-cpy-120)
115. [PY-CPY-130 — Alternative interpreters and portability](CURRICULUM.md#py-cpy-130)

#### Interview synthesis and capstones

116. [PY-INT-010 — Python traps and output-prediction reasoning](CURRICULUM.md#py-int-010)
117. [PY-INT-020 — Debugging, refactoring, and senior code review](CURRICULUM.md#py-int-020)
118. [PY-INT-030 — Pythonic implementation exercises](CURRICULUM.md#py-int-030)
119. [PY-INT-040 — Senior backend and API design interviews in Python](CURRICULUM.md#py-int-040)
120. [PY-INT-050 — Performance, concurrency, memory, and CPython interviews](CURRICULUM.md#py-int-050)
121. [PY-INT-060 — Integrated Python mastery capstone](CURRICULUM.md#py-int-060)

### Project milestones

- Consider [PY-PRJ-010 — Streaming Log Investigator CLI](PROJECTS.md#py-prj-010) after the file, streaming, testing, and complexity foundations. Projects are integration evidence and are not curriculum units.
- Consider [PY-PRJ-020 — Typed and Packaged Data-Normalization Library](PROJECTS.md#py-prj-020) after typing, packaging, and reusable-library work. Projects are integration evidence and are not curriculum units.
- Consider [PY-PRJ-030 — Typed Rule and Plugin Engine](PROJECTS.md#py-prj-030) after the object model, protocols, imports, and plugin boundaries. Projects are integration evidence and are not curriculum units.
- Consider [PY-PRJ-040 — Asynchronous Job Runner](PROJECTS.md#py-prj-040) after structured concurrency, cancellation, and production cleanup. Projects are integration evidence and are not curriculum units.
- Consider [PY-PRJ-050 — Performance and Memory Optimisation Clinic](PROJECTS.md#py-prj-050) after memory diagnosis, benchmarking, profiling, and optimization. Projects are integration evidence and are not curriculum units.
- Consider [PY-PRJ-060 — CPython Behaviour Explorer](PROJECTS.md#py-prj-060) after the CPython compiler, runtime, object, and memory units. Projects are integration evidence and are not curriculum units.

### How to use this path

From the latest synchronized `main`, open a new Codex **Worktree** chat for the current unit and say `Initialize PY-FND-010.` Continue naturally in that same chat afterwards.

<a id="absolute-beginner"></a>
## Absolute beginner to confident Python programmer

**Who it is for:** A learner who is new to Python or wants a careful first pass before deeper professional and runtime material.

**Prerequisite guidance:** Follow this path mostly in order. Later units assume the object/name model, control flow, functions, containers, exceptions, and basic modules.

**Omitted-prerequisite policy:** Any canonical prerequisite not listed in this specialized path is **assumed prior knowledge**. If it is not already strong, study it first or request a **prerequisite bridge** before continuing.

### Recommended sequence

1. [PY-FND-010 — Python syntax and execution](CURRICULUM.md#py-fnd-010)
2. [PY-FND-020 — Objects, names, references, and mutability](CURRICULUM.md#py-fnd-020)
3. [PY-FND-030 — Namespaces, scope, and name resolution](CURRICULUM.md#py-fnd-030)
4. [PY-FND-040 — Expressions, evaluation order, and operators](CURRICULUM.md#py-fnd-040)
5. [PY-FND-050 — Truthiness, comparisons, equality, and identity](CURRICULUM.md#py-fnd-050)
6. [PY-FND-060 — Control flow and structural pattern matching](CURRICULUM.md#py-fnd-060)
7. [PY-BLT-010 — Numbers, booleans, and None](CURRICULUM.md#py-blt-010)
8. [PY-BLT-020 — Strings and Unicode](CURRICULUM.md#py-blt-020)
9. [PY-BLT-040 — Lists, tuples, ranges, and sequence behaviour](CURRICULUM.md#py-blt-040)
10. [PY-BLT-050 — Dictionaries and mapping behaviour](CURRICULUM.md#py-blt-050)
11. [PY-BLT-060 — Sets and frozensets](CURRICULUM.md#py-blt-060)
12. [PY-BLT-070 — Unpacking, comprehensions, and generator expressions](CURRICULUM.md#py-blt-070)
13. [PY-BLT-080 — Equality, ordering, hashing, and hashability](CURRICULUM.md#py-blt-080)
14. [PY-BLT-090 — Protocol-facing built-in functions and container complexity](CURRICULUM.md#py-blt-090)
15. [PY-BLT-030 — Bytes, bytearray, memoryview, and the buffer model](CURRICULUM.md#py-blt-030)
16. [PY-FIT-010 — Function definitions, calls, returns, and first-class behaviour](CURRICULUM.md#py-fit-010)
17. [PY-FIT-020 — Parameter binding and argument evaluation](CURRICULUM.md#py-fit-020)
18. [PY-FIT-030 — Higher-order functions, callable objects, and side effects](CURRICULUM.md#py-fit-030)
19. [PY-FIT-070 — Iterable and iterator protocols](CURRICULUM.md#py-fit-070)
20. [PY-FIT-080 — Generators, yield, and delegation](CURRICULUM.md#py-fit-080)
21. [PY-FIT-090 — Lazy pipelines and streaming transformations](CURRICULUM.md#py-fit-090)
22. [PY-FIT-040 — Closures, free variables, and late binding](CURRICULUM.md#py-fit-040)
23. [PY-FIT-050 — Decorators](CURRICULUM.md#py-fit-050)
24. [PY-FIT-060 — Recursion and iterative alternatives](CURRICULUM.md#py-fit-060)
25. [PY-ERR-010 — Exception flow and exception-safe control](CURRICULUM.md#py-err-010)
26. [PY-OBJ-010 — Classes, instances, methods, and construction](CURRICULUM.md#py-obj-010)
27. [PY-ERR-020 — Custom exceptions, chaining, warnings, and exception groups](CURRICULUM.md#py-err-020)
28. [PY-OBJ-020 — Properties, encapsulation, and composition](CURRICULUM.md#py-obj-020)
29. [PY-OBJ-030 — Inheritance, MRO, and super](CURRICULUM.md#py-obj-030)
30. [PY-OBJ-040 — Python data model and special methods](CURRICULUM.md#py-obj-040)
31. [PY-ERR-030 — Context managers and resource safety](CURRICULUM.md#py-err-030)
32. [PY-OBJ-050 — Attribute lookup, customization, and slots](CURRICULUM.md#py-obj-050)
33. [PY-MOD-010 — Modules, packages, and executable modules](CURRICULUM.md#py-mod-010)
34. [PY-MOD-020 — Import resolution, sys.path, and module caching](CURRICULUM.md#py-mod-020)
35. [PY-MOD-050 — Python versions and virtual environments](CURRICULUM.md#py-mod-050)
36. [PY-MOD-060 — Pyproject, dependencies, locking, and reproducibility](CURRICULUM.md#py-mod-060)
37. [PY-TYP-010 — Annotation semantics and static analysis boundaries](CURRICULUM.md#py-typ-010)
38. [PY-TYP-020 — Core annotations, unions, literals, and narrowing](CURRICULUM.md#py-typ-020)
39. [PY-TYP-050 — Protocols, ABCs, and structural versus nominal typing](CURRICULUM.md#py-typ-050)
40. [PY-TYP-080 — Static-analysis tools, stubs, and gradual adoption](CURRICULUM.md#py-typ-080)
41. [PY-LIB-010 — Collections: counting, defaults, mappings, and records](CURRICULUM.md#py-lib-010)
42. [PY-LIB-020 — Deque and queue-like patterns](CURRICULUM.md#py-lib-020)
43. [PY-LIB-030 — Iterator algebra with itertools](CURRICULUM.md#py-lib-030)
44. [PY-LIB-040 — Callable transformation with functools and operator](CURRICULUM.md#py-lib-040)
45. [PY-LIB-060 — Dataclasses, enums, types, and generated data models](CURRICULUM.md#py-lib-060)
46. [PY-LIB-080 — Dates, times, time zones, and calendars](CURRICULUM.md#py-lib-080)
47. [PY-IOP-010 — Text and binary files, streams, buffering, and encodings](CURRICULUM.md#py-iop-010)
48. [PY-IOP-020 — Pathlib, os, glob, and portable path handling](CURRICULUM.md#py-iop-020)
49. [PY-IOP-050 — JSON, CSV, TOML, and configuration formats](CURRICULUM.md#py-iop-050)
50. [PY-IOP-070 — Regular expressions, argparse, and command-line processing](CURRICULUM.md#py-iop-070)
51. [PY-TST-010 — Testing principles, unittest, and doctest](CURRICULUM.md#py-tst-010)
52. [PY-TST-020 — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
53. [PY-TST-030 — Parametrization, marks, monkeypatching, and fixture composition](CURRICULUM.md#py-tst-030)
54. [PY-TST-040 — Test doubles, mocking, and patching boundaries](CURRICULUM.md#py-tst-040)
55. [PY-TST-060 — Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060)
56. [PY-TST-070 — Formatting, linting, static analysis, and maintainability](CURRICULUM.md#py-tst-070)
57. [PY-MPR-070 — Algorithmic and memory complexity](CURRICULUM.md#py-mpr-070)
58. [PY-SEC-010 — Validation, trust boundaries, and resource exhaustion](CURRICULUM.md#py-sec-010)

### Project milestones

- Consider [PY-PRJ-010 — Streaming Log Investigator CLI](PROJECTS.md#py-prj-010) after this path plus `PY-IOP-090`; use a bridge or study that unit first. Projects are integration evidence and are not curriculum units.

### How to use this path

From the latest synchronized `main`, open a new Codex **Worktree** chat for the current unit and say `Initialize PY-FND-010.` Continue naturally in that same chat afterwards.

<a id="python-interview-preparation"></a>
## Senior Python interview preparation

**Who it is for:** An experienced Python or backend engineer preparing for screening, live coding, debugging, code review, concurrency, performance, and senior design interviews.

**Prerequisite guidance:** Start with the semantic core. Add professional, backend, and CPython units according to the role. Use the interview-synthesis units only after their listed prerequisites are reasonably strong.

**Omitted-prerequisite policy:** Any canonical prerequisite not listed in this specialized path is **assumed prior knowledge**. If it is not already strong, study it first or request a **prerequisite bridge** before continuing.

### Recommended sequence

1. [PY-FND-010 — Python syntax and execution](CURRICULUM.md#py-fnd-010)
2. [PY-FND-020 — Objects, names, references, and mutability](CURRICULUM.md#py-fnd-020)
3. [PY-FND-030 — Namespaces, scope, and name resolution](CURRICULUM.md#py-fnd-030)
4. [PY-FND-040 — Expressions, evaluation order, and operators](CURRICULUM.md#py-fnd-040)
5. [PY-FND-050 — Truthiness, comparisons, equality, and identity](CURRICULUM.md#py-fnd-050)
6. [PY-FND-060 — Control flow and structural pattern matching](CURRICULUM.md#py-fnd-060)
7. [PY-BLT-010 — Numbers, booleans, and None](CURRICULUM.md#py-blt-010)
8. [PY-BLT-020 — Strings and Unicode](CURRICULUM.md#py-blt-020)
9. [PY-BLT-030 — Bytes, bytearray, memoryview, and the buffer model](CURRICULUM.md#py-blt-030)
10. [PY-BLT-040 — Lists, tuples, ranges, and sequence behaviour](CURRICULUM.md#py-blt-040)
11. [PY-BLT-050 — Dictionaries and mapping behaviour](CURRICULUM.md#py-blt-050)
12. [PY-BLT-060 — Sets and frozensets](CURRICULUM.md#py-blt-060)
13. [PY-BLT-070 — Unpacking, comprehensions, and generator expressions](CURRICULUM.md#py-blt-070)
14. [PY-BLT-080 — Equality, ordering, hashing, and hashability](CURRICULUM.md#py-blt-080)
15. [PY-BLT-090 — Protocol-facing built-in functions and container complexity](CURRICULUM.md#py-blt-090)
16. [PY-FIT-010 — Function definitions, calls, returns, and first-class behaviour](CURRICULUM.md#py-fit-010)
17. [PY-FIT-020 — Parameter binding and argument evaluation](CURRICULUM.md#py-fit-020)
18. [PY-FIT-030 — Higher-order functions, callable objects, and side effects](CURRICULUM.md#py-fit-030)
19. [PY-FIT-040 — Closures, free variables, and late binding](CURRICULUM.md#py-fit-040)
20. [PY-FIT-050 — Decorators](CURRICULUM.md#py-fit-050)
21. [PY-FIT-060 — Recursion and iterative alternatives](CURRICULUM.md#py-fit-060)
22. [PY-FIT-070 — Iterable and iterator protocols](CURRICULUM.md#py-fit-070)
23. [PY-FIT-080 — Generators, yield, and delegation](CURRICULUM.md#py-fit-080)
24. [PY-FIT-090 — Lazy pipelines and streaming transformations](CURRICULUM.md#py-fit-090)
25. [PY-ERR-010 — Exception flow and exception-safe control](CURRICULUM.md#py-err-010)
26. [PY-OBJ-010 — Classes, instances, methods, and construction](CURRICULUM.md#py-obj-010)
27. [PY-ERR-020 — Custom exceptions, chaining, warnings, and exception groups](CURRICULUM.md#py-err-020)
28. [PY-OBJ-020 — Properties, encapsulation, and composition](CURRICULUM.md#py-obj-020)
29. [PY-OBJ-030 — Inheritance, MRO, and super](CURRICULUM.md#py-obj-030)
30. [PY-OBJ-040 — Python data model and special methods](CURRICULUM.md#py-obj-040)
31. [PY-ERR-030 — Context managers and resource safety](CURRICULUM.md#py-err-030)
32. [PY-OBJ-050 — Attribute lookup, customization, and slots](CURRICULUM.md#py-obj-050)
33. [PY-MOD-010 — Modules, packages, and executable modules](CURRICULUM.md#py-mod-010)
34. [PY-MOD-020 — Import resolution, sys.path, and module caching](CURRICULUM.md#py-mod-020)
35. [PY-MOD-030 — Circular imports and package boundaries](CURRICULUM.md#py-mod-030)
36. [PY-TYP-010 — Annotation semantics and static analysis boundaries](CURRICULUM.md#py-typ-010)
37. [PY-TYP-020 — Core annotations, unions, literals, and narrowing](CURRICULUM.md#py-typ-020)
38. [PY-TYP-030 — Generics and type variables](CURRICULUM.md#py-typ-030)
39. [PY-TYP-040 — Variance and safe generic API design](CURRICULUM.md#py-typ-040)
40. [PY-TYP-050 — Protocols, ABCs, and structural versus nominal typing](CURRICULUM.md#py-typ-050)
41. [PY-TYP-060 — Callable typing, overloads, ParamSpec, and Self](CURRICULUM.md#py-typ-060)
42. [PY-TYP-080 — Static-analysis tools, stubs, and gradual adoption](CURRICULUM.md#py-typ-080)
43. [PY-LIB-010 — Collections: counting, defaults, mappings, and records](CURRICULUM.md#py-lib-010)
44. [PY-LIB-020 — Deque and queue-like patterns](CURRICULUM.md#py-lib-020)
45. [PY-LIB-030 — Iterator algebra with itertools](CURRICULUM.md#py-lib-030)
46. [PY-LIB-040 — Callable transformation with functools and operator](CURRICULUM.md#py-lib-040)
47. [PY-LIB-050 — Heap, bisection, and compact-array tools](CURRICULUM.md#py-lib-050)
48. [PY-TST-010 — Testing principles, unittest, and doctest](CURRICULUM.md#py-tst-010)
49. [PY-TST-020 — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
50. [PY-TST-030 — Parametrization, marks, monkeypatching, and fixture composition](CURRICULUM.md#py-tst-030)
51. [PY-TST-040 — Test doubles, mocking, and patching boundaries](CURRICULUM.md#py-tst-040)
52. [PY-TST-050 — Property-based testing, coverage, and mutation concepts](CURRICULUM.md#py-tst-050)
53. [PY-TST-060 — Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060)
54. [PY-TST-070 — Formatting, linting, static analysis, and maintainability](CURRICULUM.md#py-tst-070)
55. [PY-MPR-070 — Algorithmic and memory complexity](CURRICULUM.md#py-mpr-070)
56. [PY-MPR-080 — Responsible benchmarking](CURRICULUM.md#py-mpr-080)
57. [PY-MPR-090 — Profiling and tracing](CURRICULUM.md#py-mpr-090)
58. [PY-IOP-010 — Text and binary files, streams, buffering, and encodings](CURRICULUM.md#py-iop-010)
59. [PY-IOP-040 — Subprocesses, pipes, exit codes, and signals](CURRICULUM.md#py-iop-040)
60. [PY-IOP-050 — JSON, CSV, TOML, and configuration formats](CURRICULUM.md#py-iop-050)
61. [PY-IOP-060 — Pickle, shelve, copying, and object graphs](CURRICULUM.md#py-iop-060)
62. [PY-IOP-090 — Streaming large data and bounded processing](CURRICULUM.md#py-iop-090)
63. [PY-CON-010 — Concurrency, parallelism, scheduling, and the GIL model](CURRICULUM.md#py-con-010)
64. [PY-MPR-100 — Performance optimization strategy](CURRICULUM.md#py-mpr-100)
65. [PY-CON-020 — Threads, lifecycle, context, and thread-safe boundaries](CURRICULUM.md#py-con-020)
66. [PY-CON-030 — Synchronization, queues, races, and deadlocks](CURRICULUM.md#py-con-030)
67. [PY-CON-040 — Multiprocessing, IPC, shared memory, and process isolation](CURRICULUM.md#py-con-040)
68. [PY-CON-050 — Futures and executors](CURRICULUM.md#py-con-050)
69. [PY-CON-060 — Asyncio event loop, coroutines, tasks, and context](CURRICULUM.md#py-con-060)
70. [PY-CON-070 — Structured concurrency, cancellation, and timeouts](CURRICULUM.md#py-con-070)
71. [PY-CON-080 — Async queues, backpressure, async iteration, and blocking boundaries](CURRICULUM.md#py-con-080)
72. [PY-SEC-010 — Validation, trust boundaries, and resource exhaustion](CURRICULUM.md#py-sec-010)
73. [PY-SEC-020 — Deserialization, command, path, and temporary-file security](CURRICULUM.md#py-sec-020)
74. [PY-SEC-050 — Production configuration, observability, logging, and graceful shutdown](CURRICULUM.md#py-sec-050)
75. [PY-SEC-060 — Backend API, database, network, validation, and error boundaries](CURRICULUM.md#py-sec-060)
76. [PY-SEC-070 — Async-service deadlines, backpressure, pools, and shutdown](CURRICULUM.md#py-sec-070)
77. [PY-INT-010 — Python traps and output-prediction reasoning](CURRICULUM.md#py-int-010)
78. [PY-INT-020 — Debugging, refactoring, and senior code review](CURRICULUM.md#py-int-020)
79. [PY-INT-030 — Pythonic implementation exercises](CURRICULUM.md#py-int-030)
80. [PY-INT-040 — Senior backend and API design interviews in Python](CURRICULUM.md#py-int-040)
81. [PY-CPY-040 — Code objects and CPython bytecode](CURRICULUM.md#py-cpy-040)
82. [PY-CPY-050 — Frames and the evaluation loop](CURRICULUM.md#py-cpy-050)
83. [PY-CPY-070 — PyObject, type objects, slots, descriptors, and runtime dispatch](CURRICULUM.md#py-cpy-070)
84. [PY-CPY-080 — Dictionary, set, list, tuple, and string internals](CURRICULUM.md#py-cpy-080)
85. [PY-CPY-100 — Adaptive specialization, inline caches, instrumentation, and JIT boundaries](CURRICULUM.md#py-cpy-100)
86. [PY-CPY-110 — GIL, free-threading, subinterpreters, and extension compatibility](CURRICULUM.md#py-cpy-110)
87. [PY-INT-050 — Performance, concurrency, memory, and CPython interviews](CURRICULUM.md#py-int-050)

### Project milestones

- Consider [PY-PRJ-040 — Asynchronous Job Runner](PROJECTS.md#py-prj-040) after the included concurrency, testing, and production-safety units. Projects are integration evidence and are not curriculum units.
- Consider [PY-PRJ-010 — Streaming Log Investigator CLI](PROJECTS.md#py-prj-010) after adding `PY-IOP-020` and `PY-IOP-070`. Projects are integration evidence and are not curriculum units.

### How to use this path

From the latest synchronized `main`, open a new Codex **Worktree** chat for the current unit and say `Initialize PY-FND-010.` Continue naturally in that same chat afterwards.

<a id="backend-python-engineer"></a>
## Backend Python engineer

**Who it is for:** Backend engineers who need strong Python semantics, reliable API and service boundaries, packaging, testing, async work, observability, security, and performance.

**Prerequisite guidance:** The path deliberately stays Python-focused. Framework, database, distributed-system, and cloud curricula belong in separate repositories.

**Omitted-prerequisite policy:** Any canonical prerequisite not listed in this specialized path is **assumed prior knowledge**. If it is not already strong, study it first or request a **prerequisite bridge** before continuing.

### Recommended sequence

1. [PY-FND-020 — Objects, names, references, and mutability](CURRICULUM.md#py-fnd-020)
2. [PY-FND-030 — Namespaces, scope, and name resolution](CURRICULUM.md#py-fnd-030)
3. [PY-FND-040 — Expressions, evaluation order, and operators](CURRICULUM.md#py-fnd-040)
4. [PY-FND-050 — Truthiness, comparisons, equality, and identity](CURRICULUM.md#py-fnd-050)
5. [PY-FND-060 — Control flow and structural pattern matching](CURRICULUM.md#py-fnd-060)
6. [PY-BLT-020 — Strings and Unicode](CURRICULUM.md#py-blt-020)
7. [PY-BLT-030 — Bytes, bytearray, memoryview, and the buffer model](CURRICULUM.md#py-blt-030)
8. [PY-BLT-040 — Lists, tuples, ranges, and sequence behaviour](CURRICULUM.md#py-blt-040)
9. [PY-BLT-050 — Dictionaries and mapping behaviour](CURRICULUM.md#py-blt-050)
10. [PY-BLT-060 — Sets and frozensets](CURRICULUM.md#py-blt-060)
11. [PY-BLT-070 — Unpacking, comprehensions, and generator expressions](CURRICULUM.md#py-blt-070)
12. [PY-BLT-080 — Equality, ordering, hashing, and hashability](CURRICULUM.md#py-blt-080)
13. [PY-BLT-090 — Protocol-facing built-in functions and container complexity](CURRICULUM.md#py-blt-090)
14. [PY-FIT-010 — Function definitions, calls, returns, and first-class behaviour](CURRICULUM.md#py-fit-010)
15. [PY-FIT-020 — Parameter binding and argument evaluation](CURRICULUM.md#py-fit-020)
16. [PY-FIT-040 — Closures, free variables, and late binding](CURRICULUM.md#py-fit-040)
17. [PY-FIT-050 — Decorators](CURRICULUM.md#py-fit-050)
18. [PY-FIT-070 — Iterable and iterator protocols](CURRICULUM.md#py-fit-070)
19. [PY-FIT-080 — Generators, yield, and delegation](CURRICULUM.md#py-fit-080)
20. [PY-FIT-090 — Lazy pipelines and streaming transformations](CURRICULUM.md#py-fit-090)
21. [PY-ERR-010 — Exception flow and exception-safe control](CURRICULUM.md#py-err-010)
22. [PY-OBJ-010 — Classes, instances, methods, and construction](CURRICULUM.md#py-obj-010)
23. [PY-ERR-020 — Custom exceptions, chaining, warnings, and exception groups](CURRICULUM.md#py-err-020)
24. [PY-OBJ-020 — Properties, encapsulation, and composition](CURRICULUM.md#py-obj-020)
25. [PY-OBJ-030 — Inheritance, MRO, and super](CURRICULUM.md#py-obj-030)
26. [PY-OBJ-040 — Python data model and special methods](CURRICULUM.md#py-obj-040)
27. [PY-ERR-030 — Context managers and resource safety](CURRICULUM.md#py-err-030)
28. [PY-OBJ-050 — Attribute lookup, customization, and slots](CURRICULUM.md#py-obj-050)
29. [PY-OBJ-090 — Introspection, reflection, and monkey patching](CURRICULUM.md#py-obj-090)
30. [PY-MOD-010 — Modules, packages, and executable modules](CURRICULUM.md#py-mod-010)
31. [PY-MOD-020 — Import resolution, sys.path, and module caching](CURRICULUM.md#py-mod-020)
32. [PY-MOD-030 — Circular imports and package boundaries](CURRICULUM.md#py-mod-030)
33. [PY-MOD-050 — Python versions and virtual environments](CURRICULUM.md#py-mod-050)
34. [PY-MOD-060 — Pyproject, dependencies, locking, and reproducibility](CURRICULUM.md#py-mod-060)
35. [PY-MOD-070 — Package layouts, resources, entry points, and plugin boundaries](CURRICULUM.md#py-mod-070)
36. [PY-MOD-080 — Build systems, distributions, publishing, and supply-chain boundaries](CURRICULUM.md#py-mod-080)
37. [PY-TYP-010 — Annotation semantics and static analysis boundaries](CURRICULUM.md#py-typ-010)
38. [PY-TYP-020 — Core annotations, unions, literals, and narrowing](CURRICULUM.md#py-typ-020)
39. [PY-TYP-030 — Generics and type variables](CURRICULUM.md#py-typ-030)
40. [PY-TYP-050 — Protocols, ABCs, and structural versus nominal typing](CURRICULUM.md#py-typ-050)
41. [PY-TYP-060 — Callable typing, overloads, ParamSpec, and Self](CURRICULUM.md#py-typ-060)
42. [PY-TYP-070 — Typed records and advanced narrowing](CURRICULUM.md#py-typ-070)
43. [PY-TYP-080 — Static-analysis tools, stubs, and gradual adoption](CURRICULUM.md#py-typ-080)
44. [PY-LIB-010 — Collections: counting, defaults, mappings, and records](CURRICULUM.md#py-lib-010)
45. [PY-LIB-020 — Deque and queue-like patterns](CURRICULUM.md#py-lib-020)
46. [PY-LIB-030 — Iterator algebra with itertools](CURRICULUM.md#py-lib-030)
47. [PY-LIB-040 — Callable transformation with functools and operator](CURRICULUM.md#py-lib-040)
48. [PY-LIB-060 — Dataclasses, enums, types, and generated data models](CURRICULUM.md#py-lib-060)
49. [PY-LIB-080 — Dates, times, time zones, and calendars](CURRICULUM.md#py-lib-080)
50. [PY-IOP-010 — Text and binary files, streams, buffering, and encodings](CURRICULUM.md#py-iop-010)
51. [PY-IOP-020 — Pathlib, os, glob, and portable path handling](CURRICULUM.md#py-iop-020)
52. [PY-IOP-030 — Filesystem operations, temporary files, and atomicity](CURRICULUM.md#py-iop-030)
53. [PY-IOP-040 — Subprocesses, pipes, exit codes, and signals](CURRICULUM.md#py-iop-040)
54. [PY-IOP-050 — JSON, CSV, TOML, and configuration formats](CURRICULUM.md#py-iop-050)
55. [PY-IOP-060 — Pickle, shelve, copying, and object graphs](CURRICULUM.md#py-iop-060)
56. [PY-IOP-070 — Regular expressions, argparse, and command-line processing](CURRICULUM.md#py-iop-070)
57. [PY-IOP-080 — Networking foundations with socket, SSL, HTTP, URL, and email tools](CURRICULUM.md#py-iop-080)
58. [PY-IOP-090 — Streaming large data and bounded processing](CURRICULUM.md#py-iop-090)
59. [PY-TST-010 — Testing principles, unittest, and doctest](CURRICULUM.md#py-tst-010)
60. [PY-TST-020 — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
61. [PY-TST-030 — Parametrization, marks, monkeypatching, and fixture composition](CURRICULUM.md#py-tst-030)
62. [PY-TST-040 — Test doubles, mocking, and patching boundaries](CURRICULUM.md#py-tst-040)
63. [PY-TST-050 — Property-based testing, coverage, and mutation concepts](CURRICULUM.md#py-tst-050)
64. [PY-TST-060 — Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060)
65. [PY-TST-070 — Formatting, linting, static analysis, and maintainability](CURRICULUM.md#py-tst-070)
66. [PY-CON-010 — Concurrency, parallelism, scheduling, and the GIL model](CURRICULUM.md#py-con-010)
67. [PY-CON-020 — Threads, lifecycle, context, and thread-safe boundaries](CURRICULUM.md#py-con-020)
68. [PY-CON-030 — Synchronization, queues, races, and deadlocks](CURRICULUM.md#py-con-030)
69. [PY-CON-040 — Multiprocessing, IPC, shared memory, and process isolation](CURRICULUM.md#py-con-040)
70. [PY-CON-050 — Futures and executors](CURRICULUM.md#py-con-050)
71. [PY-CON-060 — Asyncio event loop, coroutines, tasks, and context](CURRICULUM.md#py-con-060)
72. [PY-CON-070 — Structured concurrency, cancellation, and timeouts](CURRICULUM.md#py-con-070)
73. [PY-CON-080 — Async queues, backpressure, async iteration, and blocking boundaries](CURRICULUM.md#py-con-080)
74. [PY-MPR-010 — Object lifetime, reference counting, finalization, and weak references](CURRICULUM.md#py-mpr-010)
75. [PY-MPR-020 — Cyclic garbage collection and gc inspection](CURRICULUM.md#py-mpr-020)
76. [PY-MPR-060 — Memory-growth and leak diagnosis](CURRICULUM.md#py-mpr-060)
77. [PY-MPR-070 — Algorithmic and memory complexity](CURRICULUM.md#py-mpr-070)
78. [PY-MPR-080 — Responsible benchmarking](CURRICULUM.md#py-mpr-080)
79. [PY-MPR-090 — Profiling and tracing](CURRICULUM.md#py-mpr-090)
80. [PY-MPR-100 — Performance optimization strategy](CURRICULUM.md#py-mpr-100)
81. [PY-SEC-010 — Validation, trust boundaries, and resource exhaustion](CURRICULUM.md#py-sec-010)
82. [PY-SEC-020 — Deserialization, command, path, and temporary-file security](CURRICULUM.md#py-sec-020)
83. [PY-SEC-030 — Randomness, secrets, hashes, HMAC, UUIDs, and sensitive logs](CURRICULUM.md#py-sec-030)
84. [PY-SEC-040 — Dependency, credential, configuration, and supply-chain security](CURRICULUM.md#py-sec-040)
85. [PY-SEC-050 — Production configuration, observability, logging, and graceful shutdown](CURRICULUM.md#py-sec-050)
86. [PY-SEC-060 — Backend API, database, network, validation, and error boundaries](CURRICULUM.md#py-sec-060)
87. [PY-SEC-070 — Async-service deadlines, backpressure, pools, and shutdown](CURRICULUM.md#py-sec-070)
88. [PY-INT-020 — Debugging, refactoring, and senior code review](CURRICULUM.md#py-int-020)
89. [PY-INT-040 — Senior backend and API design interviews in Python](CURRICULUM.md#py-int-040)
90. [PY-INT-050 — Performance, concurrency, memory, and CPython interviews](CURRICULUM.md#py-int-050)

### Project milestones

- Consider [PY-PRJ-010 — Streaming Log Investigator CLI](PROJECTS.md#py-prj-010) after the streaming, file, test, and complexity units. Projects are integration evidence and are not curriculum units.
- Consider [PY-PRJ-040 — Asynchronous Job Runner](PROJECTS.md#py-prj-040) after the async, cancellation, backpressure, and shutdown units. Projects are integration evidence and are not curriculum units.

### How to use this path

From the latest synchronized `main`, open a new Codex **Worktree** chat for the current unit and say `Initialize PY-FND-020.` Continue naturally in that same chat afterwards.

<a id="standard-library-mastery"></a>
## Standard-library mastery

**Who it is for:** Developers who know basic Python and want to select, combine, and reason about high-value standard-library tools confidently.

**Prerequisite guidance:** Complete the container, iterator, function, exception, module, and file foundations first. This path intentionally groups modules by learning value rather than API count.

**Omitted-prerequisite policy:** Any canonical prerequisite not listed in this specialized path is **assumed prior knowledge**. If it is not already strong, study it first or request a **prerequisite bridge** before continuing.

### Recommended sequence

1. [PY-BLT-040 — Lists, tuples, ranges, and sequence behaviour](CURRICULUM.md#py-blt-040)
2. [PY-BLT-050 — Dictionaries and mapping behaviour](CURRICULUM.md#py-blt-050)
3. [PY-BLT-060 — Sets and frozensets](CURRICULUM.md#py-blt-060)
4. [PY-BLT-080 — Equality, ordering, hashing, and hashability](CURRICULUM.md#py-blt-080)
5. [PY-BLT-090 — Protocol-facing built-in functions and container complexity](CURRICULUM.md#py-blt-090)
6. [PY-FIT-030 — Higher-order functions, callable objects, and side effects](CURRICULUM.md#py-fit-030)
7. [PY-FIT-050 — Decorators](CURRICULUM.md#py-fit-050)
8. [PY-FIT-070 — Iterable and iterator protocols](CURRICULUM.md#py-fit-070)
9. [PY-FIT-080 — Generators, yield, and delegation](CURRICULUM.md#py-fit-080)
10. [PY-FIT-090 — Lazy pipelines and streaming transformations](CURRICULUM.md#py-fit-090)
11. [PY-ERR-020 — Custom exceptions, chaining, warnings, and exception groups](CURRICULUM.md#py-err-020)
12. [PY-ERR-030 — Context managers and resource safety](CURRICULUM.md#py-err-030)
13. [PY-MOD-010 — Modules, packages, and executable modules](CURRICULUM.md#py-mod-010)
14. [PY-MOD-020 — Import resolution, sys.path, and module caching](CURRICULUM.md#py-mod-020)
15. [PY-LIB-010 — Collections: counting, defaults, mappings, and records](CURRICULUM.md#py-lib-010)
16. [PY-LIB-020 — Deque and queue-like patterns](CURRICULUM.md#py-lib-020)
17. [PY-LIB-030 — Iterator algebra with itertools](CURRICULUM.md#py-lib-030)
18. [PY-LIB-040 — Callable transformation with functools and operator](CURRICULUM.md#py-lib-040)
19. [PY-LIB-050 — Heap, bisection, and compact-array tools](CURRICULUM.md#py-lib-050)
20. [PY-LIB-060 — Dataclasses, enums, types, and generated data models](CURRICULUM.md#py-lib-060)
21. [PY-LIB-070 — Mathematics, precision, fractions, and statistics](CURRICULUM.md#py-lib-070)
22. [PY-LIB-080 — Dates, times, time zones, and calendars](CURRICULUM.md#py-lib-080)
23. [PY-IOP-010 — Text and binary files, streams, buffering, and encodings](CURRICULUM.md#py-iop-010)
24. [PY-IOP-020 — Pathlib, os, glob, and portable path handling](CURRICULUM.md#py-iop-020)
25. [PY-IOP-030 — Filesystem operations, temporary files, and atomicity](CURRICULUM.md#py-iop-030)
26. [PY-IOP-040 — Subprocesses, pipes, exit codes, and signals](CURRICULUM.md#py-iop-040)
27. [PY-IOP-050 — JSON, CSV, TOML, and configuration formats](CURRICULUM.md#py-iop-050)
28. [PY-IOP-060 — Pickle, shelve, copying, and object graphs](CURRICULUM.md#py-iop-060)
29. [PY-IOP-070 — Regular expressions, argparse, and command-line processing](CURRICULUM.md#py-iop-070)
30. [PY-IOP-080 — Networking foundations with socket, SSL, HTTP, URL, and email tools](CURRICULUM.md#py-iop-080)
31. [PY-IOP-090 — Streaming large data and bounded processing](CURRICULUM.md#py-iop-090)
32. [PY-TST-010 — Testing principles, unittest, and doctest](CURRICULUM.md#py-tst-010)
33. [PY-TST-040 — Test doubles, mocking, and patching boundaries](CURRICULUM.md#py-tst-040)
34. [PY-TST-060 — Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060)
35. [PY-SEC-030 — Randomness, secrets, hashes, HMAC, UUIDs, and sensitive logs](CURRICULUM.md#py-sec-030)

### Project milestones

- Consider [PY-PRJ-010 — Streaming Log Investigator CLI](PROJECTS.md#py-prj-010) after completing the project’s omitted language, file, testing, and security prerequisites. Projects are integration evidence and are not curriculum units.

### How to use this path

From the latest synchronized `main`, open a new Codex **Worktree** chat for the current unit and say `Initialize PY-BLT-040.` Continue naturally in that same chat afterwards.

<a id="async-concurrency-performance"></a>
## Async, concurrency, and performance

**Who it is for:** Senior engineers who need to reason about threads, processes, asyncio, cancellation, backpressure, memory, measurement, and optimization.

**Prerequisite guidance:** Do not skip iterator/generator semantics, exception-safe cleanup, imports, or the object-lifecycle model. They are central to correct concurrent and performance-sensitive code.

**Omitted-prerequisite policy:** Any canonical prerequisite not listed in this specialized path is **assumed prior knowledge**. If it is not already strong, study it first or request a **prerequisite bridge** before continuing.

### Recommended sequence

1. [PY-FND-020 — Objects, names, references, and mutability](CURRICULUM.md#py-fnd-020)
2. [PY-FND-030 — Namespaces, scope, and name resolution](CURRICULUM.md#py-fnd-030)
3. [PY-FIT-010 — Function definitions, calls, returns, and first-class behaviour](CURRICULUM.md#py-fit-010)
4. [PY-FIT-070 — Iterable and iterator protocols](CURRICULUM.md#py-fit-070)
5. [PY-FIT-080 — Generators, yield, and delegation](CURRICULUM.md#py-fit-080)
6. [PY-FIT-090 — Lazy pipelines and streaming transformations](CURRICULUM.md#py-fit-090)
7. [PY-ERR-010 — Exception flow and exception-safe control](CURRICULUM.md#py-err-010)
8. [PY-ERR-020 — Custom exceptions, chaining, warnings, and exception groups](CURRICULUM.md#py-err-020)
9. [PY-ERR-030 — Context managers and resource safety](CURRICULUM.md#py-err-030)
10. [PY-LIB-020 — Deque and queue-like patterns](CURRICULUM.md#py-lib-020)
11. [PY-LIB-030 — Iterator algebra with itertools](CURRICULUM.md#py-lib-030)
12. [PY-LIB-040 — Callable transformation with functools and operator](CURRICULUM.md#py-lib-040)
13. [PY-IOP-010 — Text and binary files, streams, buffering, and encodings](CURRICULUM.md#py-iop-010)
14. [PY-IOP-040 — Subprocesses, pipes, exit codes, and signals](CURRICULUM.md#py-iop-040)
15. [PY-IOP-090 — Streaming large data and bounded processing](CURRICULUM.md#py-iop-090)
16. [PY-CON-010 — Concurrency, parallelism, scheduling, and the GIL model](CURRICULUM.md#py-con-010)
17. [PY-CON-020 — Threads, lifecycle, context, and thread-safe boundaries](CURRICULUM.md#py-con-020)
18. [PY-CON-030 — Synchronization, queues, races, and deadlocks](CURRICULUM.md#py-con-030)
19. [PY-CON-040 — Multiprocessing, IPC, shared memory, and process isolation](CURRICULUM.md#py-con-040)
20. [PY-CON-050 — Futures and executors](CURRICULUM.md#py-con-050)
21. [PY-CON-060 — Asyncio event loop, coroutines, tasks, and context](CURRICULUM.md#py-con-060)
22. [PY-CON-070 — Structured concurrency, cancellation, and timeouts](CURRICULUM.md#py-con-070)
23. [PY-CON-080 — Async queues, backpressure, async iteration, and blocking boundaries](CURRICULUM.md#py-con-080)
24. [PY-MPR-010 — Object lifetime, reference counting, finalization, and weak references](CURRICULUM.md#py-mpr-010)
25. [PY-CON-090 — Free-threaded CPython, subinterpreters, and version-specific GIL changes](CURRICULUM.md#py-con-090)
26. [PY-MPR-020 — Cyclic garbage collection and gc inspection](CURRICULUM.md#py-mpr-020)
27. [PY-MPR-030 — Stack, frame, heap, call, and local-variable mental models](CURRICULUM.md#py-mpr-030)
28. [PY-MPR-040 — Object sizing, interning, caches, and shallow measurements](CURRICULUM.md#py-mpr-040)
29. [PY-MPR-050 — CPython small-object allocation and fragmentation](CURRICULUM.md#py-mpr-050)
30. [PY-MPR-060 — Memory-growth and leak diagnosis](CURRICULUM.md#py-mpr-060)
31. [PY-MPR-070 — Algorithmic and memory complexity](CURRICULUM.md#py-mpr-070)
32. [PY-MPR-080 — Responsible benchmarking](CURRICULUM.md#py-mpr-080)
33. [PY-MPR-090 — Profiling and tracing](CURRICULUM.md#py-mpr-090)
34. [PY-MPR-100 — Performance optimization strategy](CURRICULUM.md#py-mpr-100)
35. [PY-SEC-050 — Production configuration, observability, logging, and graceful shutdown](CURRICULUM.md#py-sec-050)
36. [PY-SEC-070 — Async-service deadlines, backpressure, pools, and shutdown](CURRICULUM.md#py-sec-070)
37. [PY-CPY-050 — Frames and the evaluation loop](CURRICULUM.md#py-cpy-050)
38. [PY-CPY-090 — Allocator, reference-count, garbage-collector, and finalization internals](CURRICULUM.md#py-cpy-090)
39. [PY-CPY-100 — Adaptive specialization, inline caches, instrumentation, and JIT boundaries](CURRICULUM.md#py-cpy-100)
40. [PY-CPY-110 — GIL, free-threading, subinterpreters, and extension compatibility](CURRICULUM.md#py-cpy-110)
41. [PY-INT-050 — Performance, concurrency, memory, and CPython interviews](CURRICULUM.md#py-int-050)

### Project milestones

- Consider [PY-PRJ-040 — Asynchronous Job Runner](PROJECTS.md#py-prj-040) after adding the project’s testing and production-safety prerequisites. Projects are integration evidence and are not curriculum units.
- Consider [PY-PRJ-050 — Performance and Memory Optimisation Clinic](PROJECTS.md#py-prj-050) after completing its omitted memory, testing, and profiling prerequisites. Projects are integration evidence and are not curriculum units.

### How to use this path

From the latest synchronized `main`, open a new Codex **Worktree** chat for the current unit and say `Initialize PY-FND-020.` Continue naturally in that same chat afterwards.

<a id="cpython-deep-internals"></a>
## CPython and deep internals

**Who it is for:** Learners pursuing interpreter-level understanding, runtime experiments, source navigation, free-threading, portability, or extension work.

**Prerequisite guidance:** This path assumes strong language semantics, object-model knowledge, import mechanics, testing, memory models, and responsible benchmarking. CPython observations must never be taught as universal Python guarantees.

**Omitted-prerequisite policy:** Any canonical prerequisite not listed in this specialized path is **assumed prior knowledge**. If it is not already strong, study it first or request a **prerequisite bridge** before continuing.

### Recommended sequence

1. [PY-FND-020 — Objects, names, references, and mutability](CURRICULUM.md#py-fnd-020)
2. [PY-FND-030 — Namespaces, scope, and name resolution](CURRICULUM.md#py-fnd-030)
3. [PY-FND-040 — Expressions, evaluation order, and operators](CURRICULUM.md#py-fnd-040)
4. [PY-FIT-010 — Function definitions, calls, returns, and first-class behaviour](CURRICULUM.md#py-fit-010)
5. [PY-FIT-020 — Parameter binding and argument evaluation](CURRICULUM.md#py-fit-020)
6. [PY-FIT-040 — Closures, free variables, and late binding](CURRICULUM.md#py-fit-040)
7. [PY-FIT-070 — Iterable and iterator protocols](CURRICULUM.md#py-fit-070)
8. [PY-FIT-080 — Generators, yield, and delegation](CURRICULUM.md#py-fit-080)
9. [PY-OBJ-010 — Classes, instances, methods, and construction](CURRICULUM.md#py-obj-010)
10. [PY-OBJ-030 — Inheritance, MRO, and super](CURRICULUM.md#py-obj-030)
11. [PY-OBJ-040 — Python data model and special methods](CURRICULUM.md#py-obj-040)
12. [PY-OBJ-050 — Attribute lookup, customization, and slots](CURRICULUM.md#py-obj-050)
13. [PY-OBJ-060 — Descriptors](CURRICULUM.md#py-obj-060)
14. [PY-OBJ-070 — Class-creation hooks and class decorators](CURRICULUM.md#py-obj-070)
15. [PY-OBJ-080 — Metaclasses and dynamic class creation](CURRICULUM.md#py-obj-080)
16. [PY-OBJ-090 — Introspection, reflection, and monkey patching](CURRICULUM.md#py-obj-090)
17. [PY-MOD-010 — Modules, packages, and executable modules](CURRICULUM.md#py-mod-010)
18. [PY-MOD-020 — Import resolution, sys.path, and module caching](CURRICULUM.md#py-mod-020)
19. [PY-MOD-040 — Importlib, import hooks, and namespace packages](CURRICULUM.md#py-mod-040)
20. [PY-MOD-050 — Python versions and virtual environments](CURRICULUM.md#py-mod-050)
21. [PY-MOD-070 — Package layouts, resources, entry points, and plugin boundaries](CURRICULUM.md#py-mod-070)
22. [PY-MOD-080 — Build systems, distributions, publishing, and supply-chain boundaries](CURRICULUM.md#py-mod-080)
23. [PY-TST-020 — Pytest fundamentals and fixtures](CURRICULUM.md#py-tst-020)
24. [PY-TST-060 — Debugging, tracebacks, pdb, logging, and controlled reproduction](CURRICULUM.md#py-tst-060)
25. [PY-CON-010 — Concurrency, parallelism, scheduling, and the GIL model](CURRICULUM.md#py-con-010)
26. [PY-CON-020 — Threads, lifecycle, context, and thread-safe boundaries](CURRICULUM.md#py-con-020)
27. [PY-CON-040 — Multiprocessing, IPC, shared memory, and process isolation](CURRICULUM.md#py-con-040)
28. [PY-MPR-010 — Object lifetime, reference counting, finalization, and weak references](CURRICULUM.md#py-mpr-010)
29. [PY-CON-090 — Free-threaded CPython, subinterpreters, and version-specific GIL changes](CURRICULUM.md#py-con-090)
30. [PY-MPR-020 — Cyclic garbage collection and gc inspection](CURRICULUM.md#py-mpr-020)
31. [PY-MPR-030 — Stack, frame, heap, call, and local-variable mental models](CURRICULUM.md#py-mpr-030)
32. [PY-MPR-040 — Object sizing, interning, caches, and shallow measurements](CURRICULUM.md#py-mpr-040)
33. [PY-MPR-050 — CPython small-object allocation and fragmentation](CURRICULUM.md#py-mpr-050)
34. [PY-MPR-060 — Memory-growth and leak diagnosis](CURRICULUM.md#py-mpr-060)
35. [PY-MPR-080 — Responsible benchmarking](CURRICULUM.md#py-mpr-080)
36. [PY-CPY-010 — CPython source tree, builds, and focused tests](CURRICULUM.md#py-cpy-010)
37. [PY-CPY-020 — Tokenizer, PEG parser, grammar, and AST creation](CURRICULUM.md#py-cpy-020)
38. [PY-CPY-030 — Symbol tables, scope analysis, and compilation](CURRICULUM.md#py-cpy-030)
39. [PY-CPY-040 — Code objects and CPython bytecode](CURRICULUM.md#py-cpy-040)
40. [PY-CPY-050 — Frames and the evaluation loop](CURRICULUM.md#py-cpy-050)
41. [PY-CPY-060 — Function-call mechanics and vectorcall](CURRICULUM.md#py-cpy-060)
42. [PY-CPY-070 — PyObject, type objects, slots, descriptors, and runtime dispatch](CURRICULUM.md#py-cpy-070)
43. [PY-CPY-080 — Dictionary, set, list, tuple, and string internals](CURRICULUM.md#py-cpy-080)
44. [PY-CPY-090 — Allocator, reference-count, garbage-collector, and finalization internals](CURRICULUM.md#py-cpy-090)
45. [PY-CPY-100 — Adaptive specialization, inline caches, instrumentation, and JIT boundaries](CURRICULUM.md#py-cpy-100)
46. [PY-CPY-110 — GIL, free-threading, subinterpreters, and extension compatibility](CURRICULUM.md#py-cpy-110)
47. [PY-CPY-120 — Python/C API, Limited API, and Stable ABI](CURRICULUM.md#py-cpy-120)
48. [PY-CPY-130 — Alternative interpreters and portability](CURRICULUM.md#py-cpy-130)
49. [PY-INT-050 — Performance, concurrency, memory, and CPython interviews](CURRICULUM.md#py-int-050)
50. [PY-INT-060 — Integrated Python mastery capstone](CURRICULUM.md#py-int-060)

### Project milestones

- Consider [PY-PRJ-060 — CPython Behaviour Explorer](PROJECTS.md#py-prj-060) after the required compiler, frame, object, container, memory, and specialization units. Projects are integration evidence and are not curriculum units.

### How to use this path

From the latest synchronized `main`, open a new Codex **Worktree** chat for the current unit and say `Initialize PY-FND-020.` Continue naturally in that same chat afterwards.

## Find a unit without choosing a path

Use the permanent helper chat:

```text
Which topic should I study for Python decorators?
```

The helper returns the canonical ID, exact title, reason, prerequisites, related units, folder state, and an initialization prompt such as:

```text
Initialize PY-FIT-050.
```
