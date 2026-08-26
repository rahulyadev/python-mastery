# Detailed NotebookLM Workflow

[Quick handoff](../NOTEBOOKLM.md) · [Curriculum](../CURRICULUM.md) · [Progress](../PROGRESS.md)

NotebookLM is a review surface. It does not become a second repository or the source of truth for progress.

## Approved inputs

Upload:

- approved unit `README.md` files;
- the relevant domain section of `CURRICULUM.md`;
- approved completed-project explanations;
- `SOURCE_AND_VERSION_POLICY.md` when a notebook includes CPython or version-sensitive behaviour.

Do not upload by default:

- draft notes;
- `PROGRESS.md`;
- `REVIEW.md`;
- raw learner attempts;
- solution files;
- benchmark dumps;
- profiler output;
- `.venv`;
- `uv.lock`;
- caches;
- private data.

## Notebook grouping

Use coherent groups of approximately 5–12 units:

```text
Python Execution and Built-ins
Functions, Iterators, and Generators
Object Model and Data Model
Imports, Packaging, and Typing
Standard-Library Data Tools
Files, Data Processing, and Operating Systems
Testing and Engineering Quality
Concurrency and Asyncio
Memory and Performance
Security and Production Python
CPython Compiler and Runtime
```

A one-unit notebook is appropriate when the unit is exceptionally deep, source-heavy, or being prepared for an immediate interview.

## Physical Notebook Core

Use each unit’s `Physical Notebook Core` for:

- first-pass flashcards;
- mental-model recall;
- visual reconstruction;
- invariant recall;
- quick interview warm-ups.

Use deeper sections for:

- edge cases;
- output prediction;
- debugging;
- version comparisons;
- senior trade-offs;
- CPython-specific follow-ups.

## Flashcards

```text
Create flashcards from the approved unit notes. Prioritize the Physical Notebook Core, then add deeper cards for mechanisms, edge cases, comparisons, code prediction, and production trade-offs. Avoid trivia. Cite the source unit and section for every answer.
```

## Mixed quizzes

```text
Create a mixed quiz from these approved units. Include retrieval, visual reconstruction, output prediction, debugging, comparison, and one senior engineering trade-off. Ask one question at a time and do not reveal the answer before my attempt.
```

## Mock interviews

```text
Run a senior Python interview using only these approved sources. Ask one question at a time, increase difficulty based on my answers, and test semantics, debugging, implementation, performance, and production trade-offs. Cite the source section when reviewing my answer.
```

## Returning weaknesses

Bring back:

1. the complete unit ID;
2. the exact question;
3. Rahul’s answer or a faithful summary;
4. NotebookLM’s correction;
5. the cited source section;
6. what remains confusing.

Use the existing dedicated unit chat:

```text
NotebookLM exposed this weakness in <TOPIC-ID>. Find the first missing reasoning step, test me with one focused question, and update REVIEW.md. Change the canonical note only if the clarification is generally useful.
```

When the owner unit is uncertain, use the curriculum-helper chat first.

NotebookLM does not:

- update progress;
- create repository files;
- decide mastery;
- replace the dedicated topic chat;
- override canonical sources.
