# PY-FND-010 — Python syntax and execution

[Curriculum entry](../../../CURRICULUM.md#py-fnd-010) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-FND-010`

## Physical Notebook Core

### Problem this concept solves

Python needs an unambiguous way to turn readable source text into grouped instructions and to run those instructions in the intended context: interactively, as a script, or as a module.

### One-sentence mental model

> Python reads source as structured tokens and statements, then executes code blocks in a context chosen by how the interpreter was invoked.

### One important visual

```text
source text
    │
    ├─ decode and tokenize ── NEWLINE / INDENT / DEDENT
    │
    ├─ parse into statements and suites
    │
    └─ execute a code block in one context
          ├─ REPL: run an interactive command and echo non-None expressions
          ├─ script: run file top level with __name__ == "__main__"
          └─ import: run module top level with __name__ == its module name
```

#### How to read this visual

Read from top to bottom. The first two stages determine structure; the final branch shows that the same valid source can have different observable behaviour because the execution context changes.

#### Key insight

Indentation participates in syntax, while invocation determines execution context; neither is merely cosmetic.

#### Simplification or limitation

This is a language-level conceptual pipeline. It omits the concrete parser, code objects, bytecode, import cache, frames, and implementation-specific optimisations covered by later units.

### Governing rules or invariants

1. Leading whitespace on logical lines determines statement grouping and produces `INDENT` and `DEDENT` structure.
2. A bare expression may be displayed by the REPL, but a script must perform output explicitly, commonly with `print()`.
3. A file executed as the top-level program has `__name__ == "__main__"`; when imported, its module name is used instead.

### Minimal example

```python
"""Expose a reusable greeting and an explicit script entry point."""


def greet(name: str) -> str:
    """Return a greeting for name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    print(greet("Rahul"))
```

Expected reasoning:

1. The first string is the module docstring because it is the module's first statement.
2. Defining `greet` creates the function but does not call it.
3. Direct execution satisfies the guard and prints once; importing the file defines `greet` but skips the guarded call.

### One failure or misconception

**Mistake:** “Indentation is just formatting, and Python can infer the intended block from braces or keywords.”

**Correction:** Python uses indentation as part of its grammar. A missing, unexpected, or inconsistent indentation level changes the structure or prevents parsing.

### Important trade-offs

- The REPL gives fast feedback, while a script gives repeatable, reviewable execution.
- Direct file execution is simple; `python -m` is usually a better entry point when package-aware module resolution matters.
- Comments explain source to readers; docstrings can also describe runtime objects to tools through `__doc__`.

### Interview-revision cues

- Reconstruct: source characters → tokens → statements and suites → code-block execution.
- Predict: bare expression in the REPL versus the same expression in a script.
- Explain: why a `__main__` guard separates reusable definitions from command-line effects.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Foundations and execution |
| Canonical ID | `PY-FND-010` |
| Learning outcome | Run and explain Python programs: lexical basics, indentation, statements, REPL, scripts, modules, comments, docstrings, simple I/O, and style |
| Hard prerequisites | None |
| Soft prerequisites | None |
| Co-requisites | None |
| Priority | Core |
| Interview frequency | High |
| Backend relevance | High |
| Depth | D1 |
| Scope | Language |
| Size | S |
| Evidence profile | E+C |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | CPython 3.14.4 on Linux x86_64 |
| Last source audit | 2026-08-27 |
| Artifact state | Draft |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. Read a small Python program and explain its tokens, logical lines, statements, suites, and indentation structure.
2. Choose and use the REPL, direct script execution, import, `-c`, or `-m`, then predict the visible output and the value of `__name__` where relevant.
3. Write a small, readable program with comments, docstrings, simple text input/output, reusable logic, and a guarded entry point.

Required evidence:

- Reconstruct the source-to-execution mental model without notes and correctly explain why indentation and invocation context matter.
- Run one program directly and by import, capture the actual output, and explain every difference without relying on trial-and-error alone.
- Complete and review one small implementation or debugging exercise that keeps reusable logic separate from terminal I/O.

Initialization creates this learning scaffold but does not itself satisfy the evidence or advance the learning state.

## 3. Vocabulary and professional English

### Lexical

| Item | Content |
|---|---|
| Pronunciation | LEK-si-kuhl |
| Simple English meaning | Related to the words or smallest meaningful pieces of a language |
| Hindi cue | शब्द-स्तर |
| Meaning in this Python context | Related to how source characters become tokens such as names, literals, `NEWLINE`, `INDENT`, and `DEDENT` |

Natural examples:

1. The tokenizer reports a lexical error before the program can execute.
2. A comment is recognized during lexical analysis and ignored by the syntax.
3. Parentheses allow implicit line joining at the lexical level.
4. **Interview:** “I would first separate the lexical rule from the later parsing rule.”
5. **Engineering discussion:** “The formatter changed layout, but it preserved the program's lexical structure.”

### Suite

| Item | Content |
|---|---|
| Pronunciation | sweet |
| Simple English meaning | A related group treated as one unit |
| Hindi cue | समूह |
| Meaning in this Python context | The statement group controlled by a compound-statement header such as `if`, `for`, or `def` |

Natural examples:

1. The indented suite belongs to the preceding `if` header.
2. A function body is written as a suite after its colon.
3. Nested compound statements need an indented suite.
4. **Interview:** “The colon starts the header-to-suite boundary; indentation identifies the suite.”
5. **Engineering discussion:** “This suite performs I/O, so I would keep it outside the reusable function.”

### Entry point

| Item | Content |
|---|---|
| Pronunciation | EN-tree point |
| Simple English meaning | The place where a process begins |
| Hindi cue | प्रारंभ-बिंदु |
| Meaning in this Python context | The controlled path that starts application behaviour when a file or module is executed |

Natural examples:

1. The script has a small `main()` entry point.
2. Importing the module should not accidentally run its terminal entry point.
3. `python -m package.tool` executes the selected module as the top-level entry point.
4. **Interview:** “I would protect the entry point with a `__name__` guard.”
5. **Engineering discussion:** “Keeping the entry point thin makes the core logic easier to test and reuse.”

## 4. Deep explanation

### 4.1 Why the mechanism exists

Source code must answer two different questions: “What structure did the author write?” and “In what context should that structure run?” Python makes much of the first answer visible. Newlines usually end statements, a colon introduces a suite for a compound statement, and leading indentation groups that suite. It makes the second answer explicit through interpreter invocation: an interactive command, a file, a `-c` command, a module selected with `-m`, or an import.

Keeping those questions separate prevents several common mistakes. A program can be syntactically valid yet appear to “do nothing” because its expression value is not automatically displayed in script mode. A module can be correct when run directly yet troublesome when imported because unguarded top-level I/O executes during import.

### 4.2 Formal semantics or API contract

#### From characters to logical structure

Python decodes source text before tokenizing it; UTF-8 is the default source encoding when there is no valid encoding declaration. Physical lines can combine into a logical line through explicit backslash joining or, preferably for ordinary code, implicit joining inside parentheses, brackets, or braces. A `#` outside a string begins a comment that ends at the physical line boundary. These are lexical rules, not style guesses. See the Python 3.14 Language Reference on [line structure, comments, and joining](https://docs.python.org/3.14/reference/lexical_analysis.html#line-structure).

Leading whitespace on each logical line is compared with an indentation stack. A deeper level produces `INDENT`; returning to an earlier valid level produces one or more `DEDENT` tokens. Inconsistent tab/space use that makes indentation meaning ambiguous raises `TabError`. The exact stack rules are specified in [Lexical analysis — Indentation](https://docs.python.org/3.14/reference/lexical_analysis.html#indentation).

#### Statements and suites

A simple statement fits within one logical line. Python permits multiple simple statements separated by semicolons, but ordinary maintainable code normally keeps one statement per line. In interactive mode, a non-`None` expression-statement result is rendered with `repr()` and written automatically. The same language rule does not make a script echo every expression. See [Simple statements](https://docs.python.org/3.14/reference/simple_stmts.html).

A compound statement has one or more clauses; each clause has a keyword-and-colon header plus a suite. Although a suite can sometimes be placed on the header line, only an indented suite on following lines can contain nested compound statements. The formal grammar uses `NEWLINE INDENT statement+ DEDENT`; see [Compound statements](https://docs.python.org/3.14/reference/compound_stmts.html).

#### Comments are not docstrings

Comments are removed from syntactic consideration after their lexical role. A docstring is different: it is a string literal used as the first statement of a module, function, class, or method, and it becomes that object's `__doc__` attribute. A later standalone string is not automatically that object's docstring. PEP 257 defines the [docstring convention and placement](https://peps.python.org/pep-0257/#what-is-a-docstring).

Use comments to explain intent, constraints, or a surprising decision that the code itself cannot express clearly. Use docstrings to state the public purpose, behaviour, inputs, outputs, or important failure contract of a documented object. Neither should narrate obvious syntax.

#### Code blocks and execution modes

The Language Reference defines modules, function bodies, class definitions, interactive commands, script files, `-c` commands, and modules selected with `-m` as code blocks in their respective contexts. A code block executes in an execution frame; deeper frame mechanics belong to later units. See [Execution model — Structure of a program](https://docs.python.org/3.14/reference/executionmodel.html#structure-of-a-program).

The most useful command forms are:

```text
python                         # interactive mode when attached to a terminal
python -c 'print(2 + 3)'       # execute a command string
python path/to/tool.py         # execute a file as the top-level program
python -m package.tool         # locate a module, then execute it as top level
```

The interpreter documents these distinctions under [Invoking the interpreter](https://docs.python.org/3.14/tutorial/interpreter.html#invoking-the-interpreter). The shell chooses which executable the command name resolves to, so professional workflows verify it with `python --version` and, when ambiguity matters, `python -c 'import sys; print(sys.executable)'`.

A `.py` file is a module containing Python definitions and statements. On import, its top-level statements execute and `__name__` identifies the module. When the file or selected module is the top-level program, `__name__` is `"__main__"`. A guard therefore separates import-safe definitions from direct-execution behaviour. See [Executing modules as scripts](https://docs.python.org/3.14/tutorial/modules.html#executing-modules-as-scripts).

```python
def main() -> None:
    """Run the command-line behaviour."""
    print("ready")


if __name__ == "__main__":
    main()
```

This guard is not a security boundary and does not make all top-level code lazy. Definitions, imports, assignments, and any other unguarded statements still execute when the module is imported.

#### Simple terminal input and output

`input(prompt)` writes the prompt without a trailing newline, reads one line, strips its trailing newline, and returns a `str`; end-of-file raises `EOFError`. It does not infer an integer or validate domain data. `print()` converts its positional objects to text, separates them with `sep`, appends `end`, and writes to `sys.stdout` by default. These are standard-library contracts documented under [`input()`](https://docs.python.org/3.14/library/functions.html#input) and [`print()`](https://docs.python.org/3.14/library/functions.html#print).

At real backend boundaries, parsing and validation should follow input explicitly. Keep domain logic independent of terminal I/O so tests can call it without patching global streams.

#### Style is a shared constraint, not syntax

PEP 8 recommends spaces for indentation and implicit continuation inside delimiters rather than backslashes for most wrapping. More importantly, a project's established style takes precedence, and readability is the purpose of the convention rather than mechanical compliance. See [PEP 8 — Code layout](https://peps.python.org/pep-0008/#code-lay-out) and [A Foolish Consistency](https://peps.python.org/pep-0008/#a-foolish-consistency-is-the-hobgoblin-of-little-minds).

### 4.3 Execution sequence

| Step | Event | Relevant state |
|---:|---|---|
| 1 | A shell or host launches a particular Python interpreter with a command, file, or module request. | Executable, arguments, current directory, environment |
| 2 | Python decodes source and the tokenizer emits names, literals, operators, `NEWLINE`, `INDENT`, and `DEDENT` as applicable. | Source encoding, logical lines, indentation stack |
| 3 | The parser checks grammar and forms statements and suites; the implementation prepares executable code. | Syntax is accepted or an error stops execution |
| 4 | The selected top-level code block executes in order. | Top-level namespace and `__name__` |
| 5 | Definitions bind names; calls and explicit I/O create observable effects. | Current bindings, input stream, output stream |
| 6 | Normal completion or an uncaught exception determines the process result. | Exit status and any traceback/output |

## 5. Additional visual models

### One source file, four entry modes

```text
                         selected source                    visible expression result
python              → interactive command, one at a time → echoed when result is not None
python tool.py      → file tool.py as __main__            → not echoed automatically
python -m app.tool  → located app.tool as __main__        → not echoed automatically
import app.tool     → app.tool as app.tool                 → not echoed automatically
```

#### How to read this visual

Read each row from command to selected source, then to its name/expression-display behaviour. The two top-level execution forms agree on `__name__` even though one starts from a path and the other from module lookup.

#### Key insight

REPL display is a service of interactive mode, while `print()` is an explicit program effect; `__name__` describes execution role, not the physical filename alone.

#### Simplification or limitation

This model omits standard input that is not a terminal, package-relative import details, `sys.path`, import caching, reloads, console-script entry points, notebooks, and IDE-specific consoles. Those boundaries belong mainly to `PY-MOD-010` and `PY-MOD-020`.

## 6. Worked examples

### 6.1 Small example: expression display is context-dependent

Interactive session:

```python
>>> 2 + 3
5
>>> print(2 + 3)
5
```

Script body:

```python
2 + 3
print(2 + 3)
```

Prediction before execution:

The REPL visibly displays both results: once through interactive expression display and once through `print()`. The script visibly writes only the second result because evaluating its first expression has no output side effect.

Observed result, run with CPython 3.14.4:

```text
REPL:
5
5

script:
5
```

### 6.2 Realistic Python example: thin I/O entry point

The runnable file is [`examples/execution_demo.py`](examples/execution_demo.py).

```python
"""Demonstrate reusable logic and an explicit script entry point."""


def build_status(service: str) -> str:
    """Return a synthetic one-line status for a service."""
    normalized_service = service.strip() or "api"
    return f"{normalized_service}: ok"


def main() -> None:
    """Read a service name and print its synthetic status."""
    service = input("Service name: ")
    print(build_status(service))


if __name__ == "__main__":
    main()
```

Prediction before execution:

Direct execution asks for a service and prints a normalized synthetic status. Importing the module defines `build_status` and `main` but performs no terminal I/O because the guard is false.

Observed result, run with CPython 3.14.4:

```text
$ printf 'worker\n' | python examples/execution_demo.py
Service name: worker: ok

$ python -c 'import execution_demo; print(execution_demo.__name__)'
execution_demo
```

The second command was run with the example directory as its current directory.

Explain:

- The pure `build_status()` function is reusable and easy to call in a test.
- `main()` owns terminal I/O and remains thin.
- The guard prevents command-line behaviour during import, but it does not suppress other unguarded top-level statements.
- `input()` still needs explicit validation for real untrusted data; this synthetic example only demonstrates the boundary.
- A production service would normally use structured logging rather than `print()` for operational events.

### 6.3 Debugging example

Keep the repair hidden until an attempt. Identify the first parser-reported issue. After repairing only that issue, predict whether direct script execution visibly writes the returned value and explain why.

```python
def status(service: str) -> str:
"""Return a synthetic status."""
    return f"{service}: ok"


status("api")
```

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| Treating a physical newline as always ending a statement | Most short examples use one physical line per statement | Delimiters can join physical lines into one logical line; an explicit backslash can also join under stricter rules | Tokenize or run an expression split inside parentheses |
| Writing a comment after an explicit continuation backslash | Comments usually work at line ends | A line-ending continuation backslash cannot carry a comment | Compile the smallest two-line example and inspect the `SyntaxError` |
| Mixing indentation tabs and spaces | The editor may align them visually | Ambiguous inconsistent indentation raises `TabError`; use spaces consistently | Enable visible whitespace and compile the file |
| Assuming `#` always starts a comment | `#` commonly introduces comments | Inside a string literal it is string content | Compare `print("#")` with `# print()` |
| Calling any standalone string a docstring | Triple-quoted strings look like documentation | Placement as the first statement determines the object's primary docstring | Inspect the object's `__doc__` |
| Expecting a script to echo a bare expression | The REPL does so | Automatic `repr()` display is interactive-mode behaviour | Run the same expression in a REPL and a file |
| Assuming `input()` returns the requested domain type | The prompt may ask for a number | `input()` returns text; parsing and validation are separate | Inspect `type(input())` with controlled input |
| Believing a `__main__` guard prevents every import side effect | The guarded call is skipped | All unguarded top-level statements still execute during import | Put a temporary observable statement above the guard and import once |
| Using semicolons because they are legal | They resemble compact syntax in other languages | Multiple simple statements can share a logical line, but separate lines are normally clearer | Expand the line and compare review/debugging clarity |
| Treating a blank REPL line like a blank file line | Both look empty | In the standard REPL, an entirely blank logical line terminates a multi-line command | Enter a `def` interactively and finish it with a blank line |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| Preparing source for execution | Grows with the amount and structure of source processed | Exact tokenizer, parser, compiler, and cache costs are implementation- and version-dependent |
| Import-time top-level work | Includes every executed top-level operation on the first effective load | Import lookup and caching details are deferred to `PY-MOD-020` |
| `input()` or `print()` | Usually dominated by stream and terminal or pipe I/O | Buffering, encoding, destination, and flushing affect latency; no benchmark is claimed here |
| Thin entry point calling pure logic | Small delegation overhead | The maintainability and testability gain usually matters more than this unmeasured call cost |

Do not optimize away clear structure based on imagined startup savings. Measure a representative command when startup latency actually matters, and distinguish source preparation from imported dependencies and application work.

## 9. Production relevance and trade-offs

- **Correctness:** Treat indentation, source encoding, and execution context as explicit inputs to program behaviour.
- **Readability:** Prefer one statement per line, spaces for indentation, descriptive names, and implicit continuation inside delimiters.
- **API stability:** Keep importable definitions separate from command-line effects so callers can reuse a module without unexpected prompts or output.
- **Testing:** Put parsing and I/O at a thin boundary; test deterministic functions directly and test the entry point separately.
- **Error handling:** `input()` can reach EOF and conversions can fail. A real program should report an actionable error and return an intentional exit status.
- **Observability:** `print()` suits small command output and learning examples; production services generally need leveled, contextual, configurable logging.
- **Portability:** Do not assume `python` selects the same interpreter on every machine. Verify the runtime and use the project's environment tooling.
- **Security:** Python source is executable content. Do not execute untrusted files or construct `eval()`/`exec()` input from untrusted text.
- **Maintainability:** Comments should preserve non-obvious reasoning; docstrings should describe useful contracts rather than duplicate the implementation.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| Syntax used by the required examples | Language | 3.6 | Same code | The newest required syntax here is an f-string; annotations used here are also supported |
| REPL, script, import, `-c`, `-m`, indentation, and `__main__` model | Language and tooling | Before 3.11 | Same model | Exact launcher names, prompts, paths, and diagnostics vary by platform and implementation |
| PEP 8 and PEP 257 recommendations | Convention | Not version-gated | Apply the same project-aware guidance | Conventions are not parser rules |
| `t`-prefixed template string literal | Language | 3.14 | No drop-in equivalent; choose an ordinary string, f-string, or explicit template API for the actual need | Not required by this unit's examples; do not use on a 3.11 interview platform |
| Exact tokens, code objects, bytecode, and startup optimisations | CPython implementation detail where applicable | Version-dependent | Reason from language behaviour, not opcode memory | Deferred to CPython-internals units |

The examples were executed locally on CPython 3.14.4. The repository's canonical baseline remains Python 3.14 and its pin remains `3.14.7`; no Python 3.11 interpreter was available in this environment, so 3.11 compatibility was reviewed from the syntax/API boundary rather than claimed as an observed run.

## 11. Practice brief

Exercises begin unsolved. Make a prediction before running code and preserve the first attempt.

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-FND-010-P01` | Predict | 1 | Distinguish REPL display from explicit script output | Inline |
| `PY-FND-010-P02` | Implement | 2 | Build a small input/output program with a docstring, pure function, `main()`, and guard | Inline until attempted |
| `PY-FND-010-P03` | Debug | 2 | Locate indentation and logical-line failures in the order Python exposes them | Inline |
| `PY-FND-010-P04` | Review | 2 | Separate syntax requirements from PEP 8 style and justify each suggested edit | Inline |
| `PY-FND-010-P05` | Explain | 3 | Compare direct execution, `-m`, import, `-c`, and interactive execution without running them | Inline |

## 12. Interview prompts

Answer one at a time without executing code first.

1. Why can typing `2 + 3` at a Python prompt display `5` while a file containing only `2 + 3` appears to produce no output?
2. In what sense is indentation syntax in Python, and how do logical lines differ from physical lines?
3. You want one file to be both importable and executable. How would you structure it, and which side effects can a `__main__` guard prevent or fail to prevent?

A strong answer should eventually demonstrate:

- the distinction between tokenization, parsing, and execution context;
- the boundary between language guarantees, interpreter behaviour, style conventions, and CPython details;
- the trade-off between a convenient interactive workflow and reproducible, import-safe program structure.

## 13. Closed-book revision cues

Without reading the note:

1. Reconstruct the source-to-execution mental model in one sentence.
2. Draw the four execution-mode rows and label expression-display and `__name__` behaviour.
3. Predict all visible output when the same two expression statements run in a REPL and in a script.
4. Diagnose a block whose indentation looks aligned in the editor but mixes tabs and spaces inconsistently.
5. Defend where terminal I/O, validation, reusable logic, `main()`, and the `__main__` guard should live in a small production CLI module.

## 14. Authoritative sources

All sources were accessed on 2026-08-27.

1. [Python 3.14.7 Language Reference — Lexical analysis](https://docs.python.org/3.14/reference/lexical_analysis.html), especially Line structure, Indentation, Names, and String prefixes.
2. [Python 3.14.7 Language Reference — Simple statements](https://docs.python.org/3.14/reference/simple_stmts.html), especially Expression statements.
3. [Python 3.14.7 Language Reference — Compound statements](https://docs.python.org/3.14/reference/compound_stmts.html), especially clause and suite grammar.
4. [Python 3.14.7 Language Reference — Execution model](https://docs.python.org/3.14/reference/executionmodel.html), especially Structure of a program.
5. [Python 3.14.7 Tutorial — Using the Python Interpreter](https://docs.python.org/3.14/tutorial/interpreter.html), especially invocation and interactive mode.
6. [Python 3.14.7 Tutorial — Modules](https://docs.python.org/3.14/tutorial/modules.html), especially Executing modules as scripts.
7. [Python 3.14.7 Standard Library — Built-in Functions](https://docs.python.org/3.14/library/functions.html), entries for `input()` and `print()`.
8. [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/), especially Code layout and consistency guidance.
9. [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/), especially What is a Docstring? and one-line docstrings.
