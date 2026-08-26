# NotebookLM Handoff

Use NotebookLM for retrieval practice, flashcards, mixed quizzes, and mock interviews after unit notes are approved.

## Upload

Upload:

- approved unit `README.md` files;
- the relevant part of [CURRICULUM.md](CURRICULUM.md);
- approved project explanations when useful;
- [docs/SOURCE_AND_VERSION_POLICY.md](docs/SOURCE_AND_VERSION_POLICY.md) for version-sensitive or CPython notebooks.

Do not upload drafts, `PROGRESS.md`, `REVIEW.md`, raw attempts, solutions, caches, profiler dumps, temporary files, or private material.

## Grouping

Prefer notebooks containing 5–12 related units, such as:

- Functions, iterators, and generators
- Object model and data model
- Imports, packaging, and typing
- Concurrency and `asyncio`
- Memory and performance
- CPython compiler and runtime

Use a single-unit notebook only when the unit is unusually deep or immediately interview-relevant.

## Return weaknesses to Codex

Bring the complete unit ID, exact question, your answer, NotebookLM’s correction, cited source section, and what remains unclear back to the dedicated unit chat.

Detailed prompts and procedures are in [docs/NOTEBOOKLM.md](docs/NOTEBOOKLM.md).
