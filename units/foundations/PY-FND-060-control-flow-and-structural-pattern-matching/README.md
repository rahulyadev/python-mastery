# PY-FND-060 — Control flow and structural pattern matching

[Curriculum entry](../../../CURRICULUM.md#py-fnd-060) · [Progress](../../../PROGRESS.md) · Local branch: `topic/PY-FND-060`

## Physical Notebook Core

### Problem this concept solves

A program must choose one path, repeat work, stop or skip deliberately, and dispatch differently shaped data without hiding why a path was selected.

### One-sentence mental model

> Control flow is an ordered graph: Python evaluates one decision point at a time, follows exactly one outgoing edge, and resumes at the edge's defined destination.

### One important visual

```text
branch:  test 1 ──false──> test 2 ──false──> else ──> after
             │ true             │ true
             v                  v
          suite 1            suite 2
             └──────────────────┴────────────────────> after

loop:    next item / true test ──> body ──continue──> next cycle
                    │                └──break────────> after loop
                    └──natural stop────────> else ──> after loop

match:   subject once ─> pattern 1 ─> guard 1 ─> selected suite ─> after
                              │ fail       │ false
                              └────────────┴─────────> next case
```

#### How to read this visual

Read each row left to right. A vertical arrow enters a selected suite. `continue` returns to the nearest loop's next cycle, `break` jumps past that loop's `else`, and a failed pattern or false guard advances to the next case.

#### Key insight

Predict behavior by naming the current decision point and the exact destination of each possible exit; indentation alone is not a sufficient model.

#### Simplification or limitation

This is a language-level control-flow map, not CPython bytecode. It omits exceptions, `return`, `yield`, `try`/`finally`, asynchronous iteration, and the internal operations used by individual patterns.

### Governing rules or invariants

1. `if`/`elif` tests and `match` cases are considered in source order; the first selected suite wins.
2. A `for` loop consumes an iterator, while a `while` loop retests a truth-valued expression before each cycle.
3. `continue` skips the remainder of the nearest loop body; `break` exits only the nearest loop and suppresses its `else`.
4. Loop `else` means “the loop reached its natural stopping condition without executing `break`,” not “the loop body never ran.”
5. A successful pattern may bind names; a guard runs only after that pattern succeeds, and a bare name in a pattern captures rather than compares.

### Minimal example

```python
for record in records:
    if not record.valid:
        continue
    if record.key == wanted_key:
        selected = record
        break
else:
    selected = None
```

Expected reasoning:

1. Invalid records jump directly to the next iteration.
2. The first valid matching record executes `break`, so the loop `else` is skipped.
3. Exhaustion—including an initially empty iterable—reaches `else` and binds `selected` to `None`.

### One failure or misconception

**Mistake:** “A loop's `else` runs when the loop condition was false or when no iteration succeeded.”

**Correction:** It runs after natural exhaustion or a false `while` test, provided that this loop did not execute `break`; `continue` does not suppress it, and `return` or an exception can leave the construct before it is reached.

### Important trade-offs

- Early `continue` and `return` can flatten nested code, but too many transfer points can make invariants hard to see.
- `match` can make shape-based dispatch explicit, but an ordered `if` chain or a dispatch table is often clearer when decisions are predicates or extensible keys rather than structures.

### Interview-revision cues

- Draw `continue`, `break`, normal termination, and `else` as distinct edges.
- For `match`, say “subject once; cases in order; pattern first; guard second; first selection wins.”
- Before predicting a bare name in `case`, ask whether it is a capture, wildcard, literal, or qualified value pattern.

## Unit metadata

| Field | Value |
|---|---|
| Domain | Foundations and execution |
| Canonical ID | `PY-FND-060` |
| Learning outcome | Design and trace conditional flow, loops, loop `else`, `break`, `continue`, and structural pattern matching |
| Hard prerequisites | `PY-FND-040`, `PY-FND-050` |
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

1. Trace `if`/`elif`/`else`, `while`, and `for` flow from expression evaluation through the selected suite and the following statement.
2. Explain and correctly place `break`, `continue`, and loop `else`, including empty input, nested loops, early returns, and exceptions.
3. Design `match` statements using literal, capture, wildcard, value, OR, AS, sequence, mapping, and class patterns with deliberate case ordering and guards.
4. Distinguish matching from equality tests, unpacking, type switching, and general Boolean predicates.
5. Review production control flow for correctness, readability, termination, side effects, extensibility, and version portability.

Required evidence for `E+C+D`:

- **E — Explain:** reconstruct the control-transfer visual and predict representative branch, loop, and match traces without running them.
- **C — Code:** implement at least one bounded search and one shape-based dispatcher, with deterministic tests for natural termination, `break`, `continue`, guard fallthrough, and an unmatched subject.
- **D — Debug:** diagnose a misplaced `else`, an incorrect nested-loop `break`, or an over-broad capture pattern, then explain the smallest counterexample and repair.

The included [examples](examples/), [focused tests](tests/test_examples.py), [practice brief](practice/README.md), and [runtime experiment](experiments/EXP-01-control-flow-dispatch-trace/README.md) support those targets. They are canonical materials, not learner evidence by themselves.

## 2. Prerequisite bridge

The tracker currently records both hard prerequisites as `Not started`, although their canonical notes are approved. This bridge is enough to read this unit but does not complete either prerequisite.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard | `PY-FND-040` — Expressions, evaluation order, and operators | Conditions, iterable expressions, match subjects, and guards are expressions whose order and side effects matter. | Assume left-to-right source order where specified; evaluate only the expression reached by the current control edge; remember that short-circuiting may skip later work. |
| Hard | `PY-FND-050` — Truthiness, comparisons, equality, and identity | `if`, `while`, guards, and comparison-based patterns consume truth or equality semantics. | A condition truth-tests its result; `==` asks for a value relation; `is` asks for the same object. Do not collapse missing, falsy, equal, and identical states. |

Recommended dedicated review: revisit `PY-FND-040` and `PY-FND-050` before claiming learning evidence for this unit.

## 3. Vocabulary and professional English

### Suite

| Item | Content |
|---|---|
| Pronunciation | sweet |
| Simple English meaning | A group of statements controlled by one header |
| Hindi cue | किसी header के नीचे statements का block |
| Meaning in this Python context | The statement or indented block belonging to an `if`, loop, `case`, function, or another compound-statement clause |

Natural examples:

1. The `else` suite records that the search exhausted its input.
2. Only the first true branch's suite executes.
3. A one-line suite is legal but usually less readable for production control flow.
4. **Interview:** “The guard is evaluated before the selected case suite runs.”
5. **Engineering discussion:** “Keep each dispatch suite small and delegate domain work to a named function.”

### Exhaustion

| Item | Content |
|---|---|
| Pronunciation | ig-ZAWS-chun |
| Simple English meaning | Reaching the point where nothing remains |
| Hindi cue | सभी items समाप्त होना |
| Meaning in this Python context | An iterator reporting that it has no next item, which naturally terminates a `for` loop |

Natural examples:

1. Exhaustion after three items enters the loop `else`.
2. An empty iterator is already exhausted.
3. `break` terminates the loop without waiting for exhaustion.
4. **Interview:** “`for`/`else` distinguishes iterator exhaustion from a `break` in that loop.”
5. **Engineering discussion:** “The exhausted path becomes our explicit not-found result.”

### Guard

| Item | Content |
|---|---|
| Pronunciation | gard |
| Simple English meaning | An extra condition that controls entry |
| Hindi cue | प्रवेश से पहले अतिरिक्त शर्त |
| Meaning in this Python context | The `if` expression after a case pattern, evaluated only after that pattern succeeds |

Natural examples:

1. The pattern checks the shape, and the guard checks the allowed range.
2. A false guard lets matching continue with the next case.
3. An exception in a guard propagates.
4. **Interview:** “Captured names are available to the guard because binding happens first.”
5. **Engineering discussion:** “Keep guards pure so routing does not hide state changes.”

### Irrefutable

| Item | Content |
|---|---|
| Pronunciation | ir-rih-FYOO-tuh-bul |
| Simple English meaning | Impossible to disprove in the stated form |
| Hindi cue | जो pattern अवश्य match करे |
| Meaning in this Python context | A pattern known from its syntax to always succeed, such as `_` or an unguarded capture pattern |

Natural examples:

1. The wildcard is irrefutable and binds nothing.
2. A bare capture is irrefutable and binds the whole subject.
3. An unguarded irrefutable case must be last.
4. **Interview:** “`case status:` is a capture, so it is irrefutable; it does not compare with the earlier variable.”
5. **Engineering discussion:** “Use one final irrefutable fallback to make unsupported events observable.”

## 4. Deep explanation

### 4.1 Control flow is ordered selection plus transfer

Python normally executes statements in sequence. A control-flow construct introduces decision points and named transfer operations:

- `if` selects a suite from truth-valued tests;
- `while` repeats while one test remains true;
- `for` requests successive items from one evaluated iterable;
- `continue` transfers to the nearest loop's next cycle;
- `break` transfers past the nearest loop and its optional `else`;
- `match` selects a case from the structure and values inside one subject.

The useful review question is not merely “what is indented under this line?” It is “which expression runs next, which suite owns this transfer, and where does control resume?” That model scales to nested loops, guards, early exits, and later exception-handling units.

### 4.2 `if`/`elif`/`else`: first true test wins

Python evaluates branch tests in source order. When one result is truthy, its suite runs and the rest of that `if` statement is neither evaluated nor executed. If every test is falsy, the optional `else` suite runs. This is the language contract in [Python 3.14.7 Language Reference — the `if` statement](https://docs.python.org/3.14/reference/compound_stmts.html#the-if-statement).

```python
if request.is_internal:
    route = "internal"
elif request.customer_tier == "premium":
    route = "priority"
else:
    route = "standard"
```

Case order is policy. An internal premium request selects `"internal"`; changing the order changes the result. For mutually exclusive ranges, order can remove repetition, but it can also hide overlaps. State the precedence explicitly in tests.

Prefer a chain when each test is a general predicate. Prefer a lookup table when an already-normalized key maps independently to behavior. Prefer `match` when decomposition of a value's shape is central.

### 4.3 `while`: retest before every cycle

A `while` loop truth-tests its expression before the first cycle and before every later cycle. A false first result means zero body executions followed by the optional `else`. A true result enters the body. Reaching the bottom or executing `continue` returns to the test; `break` exits without the `else`. The precise transitions are specified in [Python 3.14.7 Language Reference — the `while` statement](https://docs.python.org/3.14/reference/compound_stmts.html#the-while-statement).

```python
attempt = 0
while attempt < limit:
    attempt += 1
    if poll(attempt) == "retry":
        continue
    break
else:
    record_limit_reached()
```

Termination is a design obligation. Identify the variant that moves toward a false test—here `attempt` increases toward `limit`—and check that every `continue` path preserves that progress. A `while True` loop can be correct when all intended paths have an explicit exit, but reviewers must be able to prove that exit policy.

### 4.4 `for`: one iterable expression, then iterator-driven cycles

For a `for` statement, Python evaluates the iterable expression once, creates an iterator, repeatedly requests an item, assigns it to the target, and executes the body. Exhaustion enters the optional `else`. `break` skips it; `continue` asks for the next item. These guarantees and the persistence of the last assigned loop target appear in [Python 3.14.7 Language Reference — the `for` statement](https://docs.python.org/3.14/reference/compound_stmts.html#the-for-statement).

```text
evaluate iterable expression once
             │
             v
       create iterator
             │
      ┌──── next item? <──────────────┐
      │          │ yes                │
      │ no       v                    │
      │      assign target → body ────┘
      v                   │
   loop else              └── break → after loop
      │
      v
  after loop
```

#### How to read this visual

Start at the top. Only iterator exhaustion takes the left edge into `else`. Normal body completion and `continue` return to `next item?`; `break` bypasses `else`.

#### Key insight

`for` is an iterator protocol consumer, not a C-style counter loop. The target is assigned from each produced item, and rebinding that target inside the body does not control the iterator.

#### Simplification or limitation

This is a language-level iteration model. It omits the `iter()`/`next()` special-method details, generator suspension, exceptions, mutation of the underlying iterable, and asynchronous `for`.

The loop target remains bound to its last assigned item after a non-empty loop. If the iterable is empty and no earlier binding exists, reading that target afterward raises `NameError`/`UnboundLocalError` according to scope. Do not use the loop target as a reliable “found” flag; bind the result deliberately.

### 4.5 `break`, `continue`, and loop `else`

The simple-statement reference says `break` terminates the nearest enclosing loop, preserves the current `for` target, and skips that loop's `else`. `continue` begins the next cycle of the nearest enclosing loop. When either crosses a `try` with `finally`, cleanup runs on the way out. See [Python 3.14.7 Language Reference — `break` and `continue`](https://docs.python.org/3.14/reference/simple_stmts.html#the-break-statement).

| Exit from this loop | Remaining body runs? | Another cycle? | This loop's `else` runs? | Next location |
|---|---|---|---|---|
| Body reaches bottom | Yes | If another item/test succeeds | On eventual natural stop | Loop decision point |
| `continue` | No | Yes, if possible | On eventual natural stop | Loop decision point |
| `break` | No | No | No | First statement after loop |
| Empty `for` input | Not applicable | No | Yes | `else`, then after loop |
| False first `while` test | Not applicable | No | Yes | `else`, then after loop |
| `return` from containing function | No | No | No | Caller, after required cleanup |
| Propagating exception | No | No | No | Handler/unwinding path |

Loop `else` is especially good for a search where `break` means “witness found” and exhaustion means “no witness.” If readers repeatedly misread the construct, a helper function with an early `return` may communicate the same policy more directly.

For nested loops, `break` affects only the syntactically nearest loop. Common ways to exit a multi-level search are a helper function with `return`, an explicit result propagated through outer conditions, or a domain-specific exception when truly exceptional. A flag can work but often duplicates the state already represented by a result.

### 4.6 `match`: ordered structural dispatch

Structural pattern matching was added in Python 3.10 and is available on the Python 3.11 interview baseline. The language evaluates the subject expression, then considers case blocks in source order. For each case it attempts the pattern; only after success does it evaluate the guard. The first successful pattern with no guard or a truthy guard executes, and there is no fallthrough. If no case is selected, the statement completes without executing a case suite. See [Python 3.14.7 Language Reference — the `match` statement](https://docs.python.org/3.14/reference/compound_stmts.html#the-match-statement) and [PEP 634 — Structural Pattern Matching: Specification](https://peps.python.org/pep-0634/).

```text
subject expression
       │ evaluate once
       v
    subject value
       │
       ├─> case P1: pattern fails ─────────────────────────┐
       │                                                  │
       ├─> case P2 if G2: pattern succeeds → bind names   │
       │                                  │               │
       │                              guard false ─────────┤
       │                                                  │
       ├─> case P3: pattern succeeds → suite → after match
       │
       └─> case _: fallback (if reached)
```

#### How to read this visual

Follow the cases from top to bottom. A failed pattern skips its guard. A successful pattern establishes captures before its guard. A false guard resumes with the next case; a selected suite exits the whole match afterward.

#### Key insight

Pattern and guard have different jobs: use the pattern to recognize and decompose structure, then use a guard for a residual predicate that the pattern language does not express clearly.

#### Simplification or limitation

This is the specified selection pipeline, not a promise that every internal comparison, length check, attribute lookup, or cached value is performed a particular number of times. Pattern-specific operations may invoke user code and may be optimized within documented limits.

### 4.7 Pattern families

| Pattern family | Example | Success condition | Binding behavior | Important boundary |
|---|---|---|---|---|
| Literal | `case 404:` | Subject compares equal to the literal; `None`, `True`, and `False` use identity semantics | None | Literal equality can invoke value semantics. |
| Capture | `case payload:` | Always succeeds | Binds the entire subject to `payload` | A bare name does not compare with an existing variable. |
| Wildcard | `case _:` | Always succeeds | Binds nothing | An unguarded wildcard must be the final case. |
| Value | `case Signal.STOP:` | Subject compares equal to the resolved dotted name | None | Use a qualified name; the lookup may be cached during one match execution. |
| OR | `case "cancel" \| "delete":` | First successful alternative wins | Every alternative must bind the same set of names | Only the final alternative may be irrefutable. |
| AS | `case ("cancel" \| "delete") as action:` | Left pattern succeeds | Also binds the whole matched subject to `action` | The right side cannot be `_`. |
| Sequence | `case [head, *tail]:` | Subject is an eligible sequence and elements match | Subpatterns bind; starred capture receives a list | `str`, `bytes`, and `bytearray` deliberately do not match sequence patterns. |
| Mapping | `case {"id": job_id, **rest}:` | Required keys exist and value subpatterns match | Captures matched values and remaining items | Extra keys are allowed unless design logic rejects them; matching uses the mapping's two-argument `get()`. |
| Class | `case RetryCommand(job_id, attempts):` | Subject passes `isinstance` and requested attributes match | Attribute subpatterns may capture | Positional fields come from `__match_args__`; attribute access can execute descriptors or raise. |

The detailed pattern rules—including equal-name requirements for OR alternatives, the exclusion of text and byte strings from sequence patterns, mapping lookup behavior, and `__match_args__` conversion—are in [Python 3.14.7 Language Reference — Patterns](https://docs.python.org/3.14/reference/compound_stmts.html#patterns).

Patterns are not assignment unpacking with a different keyword. Assignment unpacking either succeeds or raises and generally expects the requested structure. Pattern matching reports success or failure, can ignore extra mapping keys, can ask `isinstance`, can compare literals and qualified values, can combine alternatives, and can continue to another case.

### 4.8 Bindings, guards, and failure boundaries

A capture pattern binds in the surrounding local, global, or nonlocal scope—there is no case-local scope. Names bound by a successful selected pattern remain available after the case suite. When a pattern succeeds, its bindings exist before the guard runs, even if that guard is false and matching continues.

Do not inspect or depend on partial bindings from a failed pattern. The language intentionally leaves their state unspecified so implementations can optimize. Initialize state explicitly outside the match or return from selected suites instead of trying to infer which subpattern partially succeeded.

Guards are ordinary expressions and may have side effects. They are evaluated in case order only for successful patterns; exceptions propagate. A pure guard such as `if attempts > 0` is easy to reason about. A guard that consumes an iterator, mutates shared state, or performs I/O turns routing into an effectful sequence whose retries and failures become much harder to test.

### 4.9 Choosing the construct

| Decision shape | Usually clearest | Reason |
|---|---|---|
| Ordered, overlapping Boolean predicates | `if`/`elif`/`else` | Precedence and arbitrary expressions are explicit. |
| Repeat until a state changes | `while` | The continuation predicate is central. |
| Process every item from an iterable | `for` | Iteration protocol and exhaustion are central. |
| Search for a witness | `for` plus early `return`, or `for`/`else` | Found and exhausted paths are explicit. |
| Decompose a small, closed family of data shapes | `match` | Recognition, extraction, and case order stay together. |
| Map independent normalized keys to callables | Dictionary/registry dispatch | Extension does not require editing one ordered branch chain. |
| Type-specific polymorphic behavior owned by classes | Methods/protocols | Behavior stays with the abstraction rather than a central type switch. |

`match` is not automatically more Pythonic than `if`. Use it when the structural pattern is the clearest statement of the domain rule, not merely because several conditions exist.

### 4.10 Execution sequences

#### A `for` search that finds a candidate

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Evaluate the iterable expression and create an iterator. | No loop target assigned yet. |
| 2 | Receive a blocked job and assign the target. | `continue` skips selection logic. |
| 3 | Receive a ready job and assign the target. | Predicate succeeds. |
| 4 | Bind the selected result and execute `break`. | Current loop target remains the ready job. |
| 5 | Resume after the loop. | Loop `else` was bypassed. |

#### A guarded match that falls through

| Step | Event | Relevant state |
|---:|---|---|
| 1 | Evaluate the subject expression once. | One subject value is retained for matching. |
| 2 | First pattern succeeds. | Captures are available. |
| 3 | First guard evaluates false. | First suite is not selected. |
| 4 | Next pattern is attempted against the same subject. | New case ordering still matters. |
| 5 | Pattern and guard succeed; its suite runs. | Match ends with no fallthrough. |

## 5. Additional visual models

### Nearest-loop ownership in a nested search

```text
outer for row
│
├─ inner for cell
│    ├─ continue ───────────────> next cell
│    ├─ break ──────────────────> after inner loop
│    └─ inner exhaustion ───────> inner else → after inner loop
│
└─ outer body reaches bottom ───> next row
     outer break ───────────────> after outer loop
     outer exhaustion ──────────> outer else → after outer loop
```

#### How to read this visual

Indentation shows ownership. Every `break`, `continue`, and `else` belongs to the nearest loop at the same structural level; an inner `break` lands inside the outer loop body.

#### Key insight

There is no built-in “break all loops” statement. Multi-level exit must be modeled explicitly.

#### Simplification or limitation

This conceptual topology omits `return`, exceptions, `finally`, generators, and labeled control flow—which Python does not provide.

### Pattern recognition versus residual validation

```text
incoming value
     │
     ├─ structural facts ──> pattern
     │   kind, keys, length, class, attributes, literals
     │
     └─ domain predicate ──> guard
         range, permission, cross-field relation, current policy

pattern failure ───────────> next case without guard
pattern success + guard false ─> next case with captures established
pattern success + guard true ──> selected suite
```

#### How to read this visual

Split each rule into facts visible in the subject's structure and predicates requiring a Boolean expression. Put the former in the pattern and the latter in the guard.

#### Key insight

This separation keeps case shapes readable and makes guard-specific policy testable.

#### Simplification or limitation

The boundary is a design heuristic, not a grammar rule. A literal comparison can appear in a pattern, and some validations may be clearer inside the selected suite with explicit error reporting.

## 6. Worked examples

### 6.1 Small example: search termination

Runnable source: [`examples/control_flow.py`](examples/control_flow.py)

```python
jobs = (
    Job("job-1", "blocked", 3),
    Job("job-2", "ready", -1),
    Job("job-3", "ready", 5),
    Job("job-4", "ready", 9),
)
report = select_first_ready_job(jobs)
```

Prediction before execution:

- `job-1` and `job-2` execute `continue` for different reasons;
- `job-3` is selected and executes `break`;
- `job-4` is never requested;
- the loop `else` is skipped, so `exhausted_without_break` is false.

Observed result on CPython 3.14.4:

```text
SearchReport(selected_job_id='job-3',
             inspected_job_ids=('job-1', 'job-2', 'job-3'),
             skipped_reasons=('job-1:state=blocked',
                              'job-2:negative-priority'),
             exhausted_without_break=False)
```

### 6.2 Realistic backend example: event-shape routing

Runnable source: [`examples/pattern_matching.py`](examples/pattern_matching.py)

```python
def dispatch_event(event: object) -> DispatchResult:
    match event:
        case {"kind": "job.created", "job_id": str(job_id), **remaining}:
            return DispatchResult("create", job_id, f"extra-fields={len(remaining)}")

        case RetryCommand(job_id, attempts) if attempts > 0:
            return DispatchResult("retry", job_id, f"attempts={attempts}")

        case RetryCommand(job_id, _):
            return DispatchResult("reject", job_id, "attempts must be positive")

        case (("cancel" | "delete") as operation, str(job_id)):
            return DispatchResult("remove", job_id, f"operation={operation}")

        case _:
            return DispatchResult(
                "unsupported",
                None,
                f"subject-type={type(event).__name__}",
            )
```

Why this design fits:

- the inputs genuinely have different structures: mappings, domain objects, and command sequences;
- captures remove repeated indexing and casting from the selected suite;
- a guard handles the cross-field domain rule after the class shape succeeds;
- source order lets a valid retry precede a broader invalid-retry case;
- the fallback converts unknown input into an explicit result rather than silently doing nothing.

Alternatives and boundaries:

- a dictionary from normalized event name to handler is easier to extend across plugins;
- methods on command classes are better when behavior belongs to those classes;
- schema validation should happen at an untrusted network boundary before deep domain dispatch;
- mapping patterns accept extra keys, so strict payload rejection needs an explicit policy;
- descriptors and custom mappings can execute code during matching, so do not assume matching is effect-free.

### 6.3 Debugging example: which `else` owns this block?

Keep the correction hidden until an attempt is recorded.

```python
def locate(records, wanted):
    for record in records:
        if record.key == wanted:
            return record
        else:
            return None
```

Debugging brief:

1. Predict the result when the second record matches.
2. Identify which statement owns `else` from indentation and grammar.
3. Give the smallest input that exposes the bug.
4. Repair the function without a redundant mutable `found` flag.
5. Explain whether `for`/`else` or an early return is clearer for this team.

### 6.4 Debugging example: capture or comparison?

```python
expected_status = "ready"

match actual_status:
    case expected_status:
        route = "accepted"
    case _:
        route = "rejected"
```

Do not run this first. Explain why the compiler rejects the later case as unreachable, then propose a literal, qualified value pattern, or guard according to the domain design. The important reasoning step is that `expected_status` is a capture pattern, not an expression lookup.

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| “Loop `else` means zero iterations.” | `else` sounds like the opposite of entering the loop. | It means natural stop without `break`; the body may have run many times and may have used `continue`. | Trace a three-item miss and observe `else`. |
| `continue` suppresses loop `else`. | It skips the rest of the body. | It returns to the loop decision; later natural termination still reaches `else`. | Use one ignored item and then exhaust. |
| Inner `break` exits every enclosing loop. | The desired operation is often “stop searching.” | It exits only the nearest loop. | Search a matrix and log the next outer-row event. |
| A `for` target is always defined afterward. | The target is visible after a non-empty loop. | Empty input performs no target assignment. | Delete any earlier binding, loop over `()`, then read the target. |
| Rebinding the target changes the next `for` item. | The name appears to control the loop. | The iterator supplies and reassigns the next target. | Set the target inside a `range(3)` loop and log every value. |
| `match` is a switch on equality. | Literal and value patterns can compare. | It is structural matching with multiple pattern families and possible bindings. | Compare a mapping pattern with `event == {...}` when extra keys exist. |
| A bare name in `case` refers to an existing constant. | That is how names work in expressions. | A bare name is a capture; use a literal, qualified value, or guard. | Compile an irrefutable capture followed by another case. |
| `_` stores the ignored subject. | It resembles a conventional discard variable. | In a pattern it is a wildcard and binds nothing. | Give `_` an earlier value and observe that matching does not rebind it. |
| Sequence patterns match every iterable. | `for` accepts any iterable. | Sequence patterns require eligible sequence subjects and exclude `str`, `bytes`, and `bytearray`. | Match a tuple, generator, and string against `[first, *rest]`. |
| Mapping patterns require exact keys. | Sequence patterns often require exact length. | Required keys must exist, but extra keys are permitted and can be captured with `**rest`. | Add an unrelated key to a matching dictionary. |
| Case captures disappear after the suite. | Blocks in some languages create scopes. | A successful binding follows the containing Python scope. | Return a capture after the match statement. |
| Failed partial bindings are predictable. | Some subpatterns visibly succeeded first. | Their final state after overall failure is intentionally unspecified. | Review the language rule; do not encode a runtime-specific observation as a guarantee. |
| A false guard undoes every capture. | The case was not selected. | Captures existed for guard evaluation; design should not depend on their later residual values. | Initialize or return explicit state instead of reading a fallthrough capture. |
| A wildcard fallback makes dispatch exhaustive in the type-system sense. | Every runtime subject selects a suite. | It is a runtime catch-all, not a proof that every domain variant received intentional handling. | Add a new domain variant and see it land in the generic fallback. |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| `if`/`elif` chain with `k` reached tests | `O(k)` test evaluations | Each test can have arbitrary cost or side effects; evaluation stops at the first truthy result. |
| `while` loop with `n` cycles | `O(n × body/test cost)` | `n` can be unbounded or infinite if progress is not guaranteed. |
| `for` loop over `n` produced items | `O(n × next/body cost)` | Iterator production can be lazy, blocking, stateful, or exception-raising. |
| Early `break` or `return` search | Best case `O(1)`, worst case `O(n)` | Assumes constant-cost predicate and iterator steps. |
| Ordered `match` over `k` attempted cases | Depends on attempted pattern work; commonly grows with reached cases | Do not claim hash-table or constant-time dispatch from syntax alone. |
| Fixed sequence pattern with `p` subpatterns | Up to `O(p)` matching work after eligibility/length checks | Element operations and nested patterns can add cost; implementations may cache the length. |
| Mapping pattern with `p` required keys | Roughly `p` key lookups plus nested matching | Hash/equality and custom `get()` behavior can dominate; exact operations are not a portable benchmark. |
| Class pattern with `p` requested attributes | Roughly `p` attribute resolutions plus nested matching | Descriptors, properties, `__match_args__`, and exceptions can make access effectful or expensive. |

These are reasoning bounds, not measurements. The included experiment records event order only and makes no latency or allocation claim. Optimize first for correct branch policy and readable termination. Measure representative workloads only when dispatch or iteration appears in a verified profile.

## 9. Production relevance and trade-offs

### Correctness and readability

- Put validation before irreversible effects and make overlapping branch precedence explicit.
- Use early `continue` for a small number of rejection filters; extract a predicate when the body becomes a forest of transfers.
- Name loop `else` intent in a nearby function or result (`exhausted_without_break`) when the construct is unfamiliar to the team.
- Keep selected `case` suites small. Matching should expose dispatch, not contain an entire request workflow.

### Error handling and observability

- Decide whether an unsupported event is ignored, returned, logged, quarantined, or raised; a bare `case _: pass` can hide schema drift.
- Guards and patterns may invoke user code through truth testing, equality, mappings, attributes, and descriptors. Treat exceptions as real boundary behavior.
- Log stable domain identifiers and selected routes, not raw secrets or entire untrusted payloads.
- Preserve the distinction between “no item matched,” “input was invalid,” and “processing failed.” One falsy result should not erase those states.

### API stability and extensibility

- A central match works well for a small closed protocol owned by one module.
- A registry or polymorphic method reduces merge conflicts and central edits when third parties add handlers.
- Class positional patterns couple consumers to `__match_args__`. Keyword class patterns are often more explicit and resilient when public attribute names are the intended contract.
- Mapping patterns are tolerant of extra fields, which helps forward compatibility but can conflict with strict-schema security requirements.

### Testing and maintenance

- Test every control edge: first branch, later branch, fallback, zero cycles, natural termination, `continue`, `break`, guard false, unknown shape, and exceptions from boundary code.
- For ordered cases, include an input that matches more than one candidate rule and assert the intended first winner.
- Avoid tests that assert unspecified failed-pattern bindings or exact CPython bytecode.
- Make termination evidence deterministic; do not use timing to prove a loop exits.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| `if`, `while`, `for`, `break`, `continue`, and loop `else` semantics used here | Language | Long-standing | Same syntax and model | Audited against Python 3.14.7 and 3.11.15 language references. |
| Structural `match`/`case` | Language | 3.10 | Same syntax | Fully available on the 3.11 interview baseline. |
| Literal, capture, wildcard, value, OR, AS, sequence, mapping, class patterns, and guards | Language | 3.10 | Same syntax | Individual application types still define equality, mapping, and attribute behavior. |
| Starred elements in a `for` expression list | Language | 3.11 | Explicitly construct or chain an iterable on older runtimes | This grammar expansion is not required by the included examples. |
| Possible caching of repeated value-pattern lookups or sequence lengths | Implementation freedom allowed by language spec | 3.10 pattern matching | Do not depend on an exact lookup count | The active CPython observation does not generalize an opcode or cache strategy. |
| Pattern captures after an overall failed pattern | Intentionally unspecified | 3.10 | Never depend on them | Code must work whether partial bindings remain or not. |
| Exact bytecode and specialized dispatch | CPython implementation detail | Version-specific | Reason from language behavior | Not inspected or claimed in this D2 unit. |

All repository code in this unit uses syntax supported by Python 3.11. The canonical documentation baseline is Python 3.14.7; examples and the experiment were executed on the available CPython 3.14.4 runtime, so observations are labelled accordingly.

## 11. Practice brief

Exercises begin unsolved in [`practice/README.md`](practice/README.md). Do not inspect or add a final solution before preserving an attempt.

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `PY-FND-060-P01` | Predict | 2 | Trace `continue`, `break`, natural exhaustion, and loop `else` exactly. | [`practice/README.md`](practice/README.md) |
| `PY-FND-060-P02` | Implement | 3 | Build a bounded candidate search with explicit result states. | [`practice/README.md`](practice/README.md) |
| `PY-FND-060-P03` | Debug | 3 | Repair nested-loop exit without confusing inner and outer ownership. | [`practice/README.md`](practice/README.md) |
| `PY-FND-060-P04` | Implement | 4 | Route mapping, sequence, and class subjects with safe guards and fallback. | [`practice/README.md`](practice/README.md) |
| `PY-FND-060-P05` | Review | 4 | Find capture, ordering, side-effect, strictness, and extensibility risks. | [`practice/README.md`](practice/README.md) |

Focused verification command:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s units/foundations/PY-FND-060-control-flow-and-structural-pattern-matching/tests -v
```

## 12. Interview prompts

Answer one at a time without running code:

1. Exactly when does a loop `else` execute, and how do `continue`, `break`, `return`, and an exception differ?
2. Why can `case READY:` change program behavior even when a variable named `READY` already exists?
3. Trace subject evaluation, pattern attempts, bindings, guards, and suite selection when an earlier pattern succeeds but its guard is false.
4. When would you replace a nested-loop flag with a helper function and `return`?
5. Compare an `if` chain, `match`, registry dispatch, and polymorphic method for an event-routing boundary that third parties will extend.

A strong answer should eventually demonstrate:

- exact control-transfer destinations and nearest-loop ownership;
- first-match/first-truth source ordering and natural termination;
- the difference between capture, wildcard, literal, and qualified value patterns;
- pattern-versus-guard responsibilities and binding scope;
- a production trade-off involving readability, side effects, schema evolution, or extensibility.

## 13. Closed-book revision cues

Without reading the note:

1. Draw the three paths out of a loop body: normal bottom, `continue`, and `break`; add natural termination and `else`.
2. Explain why a three-item search can execute its loop `else` even though the body ran three times.
3. Predict the target name after a non-empty `for` loop and after an empty one.
4. Reconstruct the `match` pipeline from subject expression to selected suite.
5. Give one example each of literal, capture, wildcard, qualified value, OR, sequence, mapping, and class patterns.
6. Explain why `case status:` captures while `case Status.READY:` compares.
7. State what is guaranteed and unspecified about pattern bindings.
8. Choose between `if`, `match`, a registry, and polymorphism for one backend dispatch scenario.

## 14. Runtime experiment

[`EXP-01 — Control-flow and dispatch trace`](experiments/EXP-01-control-flow-dispatch-trace/README.md) records:

- the event edge skipped by `continue`;
- the different paths produced by `break` and exhaustion;
- one subject-expression evaluation;
- ordered guard fallthrough after a successful pattern;
- guard omission for patterns that fail;
- a successful capture remaining available after its case suite.

The experiment is additional observation requested for this unit. The canonical evidence profile remains `E+C+D`; running supplied code alone does not advance learning state.

## 15. Authoritative sources

1. [Python 3.14.7 Language Reference — Compound statements: `if`, `while`, `for`, and `match`](https://docs.python.org/3.14/reference/compound_stmts.html), accessed 2026-08-29.
2. [Python 3.14.7 Language Reference — Simple statements: `break` and `continue`](https://docs.python.org/3.14/reference/simple_stmts.html#the-break-statement), accessed 2026-08-29.
3. [PEP 634 — Structural Pattern Matching: Specification](https://peps.python.org/pep-0634/), accessed 2026-08-29.
4. [Python 3.11.15 Language Reference — Compound statements](https://docs.python.org/3.11/reference/compound_stmts.html), accessed 2026-08-29.

## 16. Durable clarification log

| Date | Clarification | Why it belongs in canonical notes | Source or evidence |
|---|---|---|---|
| 2026-08-29 | Loop `else` encodes natural termination without `break`; it is not a zero-iteration branch. | This is a recurring source of incorrect search logic. | Python 3.14.7 Language Reference and focused loop traces. |
| 2026-08-29 | A bare pattern name captures, while a dotted name is a value pattern. | Expression-name intuition otherwise causes over-broad or unreachable cases. | Python 3.14.7 pattern rules and PEP 634. |
| 2026-08-29 | Do not rely on partial bindings from an overall failed pattern. | The language intentionally permits implementation variation. | Python 3.14.7 `match` overview. |
