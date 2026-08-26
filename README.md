# Python Mastery

> **Start here:** [Open `START_HERE.md`](START_HERE.md)

A long-term, evidence-based repository for rebuilding Python knowledge from language foundations through senior backend practice and CPython internals.

## One-time setup and daily use

- Use the **Local** checkout once to validate and commit the extracted bootstrap on `setup/python-mastery-bootstrap`.
- Publish that bootstrap only with the separate exact prompt in [`START_HERE.md`](START_HERE.md).
- After `main` contains the validated baseline, use one **Worktree** chat for each topic or project.
- Initialize a topic with `Initialize <TOPIC-ID>.`
- Initialize a project with `Initialize project <PROJECT-ID>.`
- Successful initialization commits and normally pushes only the exact topic or project branch; it never opens a pull request, merges, or changes remote `main`.
- Later learning changes remain local until an explicit completion choice.

Run repository validation with:

```bash
python scripts/validate_repo.py
```

## What this repository provides

- A canonical catalog of [121 learning units](CURRICULUM.md)
- Seven [recommended learning paths](LEARNING_PATHS.md)
- One dedicated Codex chat and worktree per learning unit
- Just-in-time unit and project folders
- Integrated, NotebookLM-ready learning notes
- Protected exercises, runtime experiments, and closed-book reviews
- Evidence-based [unit and project progress tracking](PROGRESS.md)
- Six Python-focused [milestone projects](PROJECTS.md)
- Reproducible standard-library-only [repository validation](scripts/validate_repo.py)
- Explicit source, version, copyright, licensing, privacy, and Git-safety rules

## Important rules

- Python 3.14 is canonical; Python 3.11 compatibility is shown when interview platforms may lag.
- Generated material does not prove learning.
- The initialized topic or project branch is pushed only after validation and relevant tests pass.
- Questions and later learning edits may be committed locally but are not pushed automatically.
- Project completion does not automatically advance curriculum-unit learning states.
- Unit and project folders are created only when initialized.
- No license has been selected. See [docs/COPYRIGHT_AND_LICENSE.md](docs/COPYRIGHT_AND_LICENSE.md).

## Repository map

| Path | Purpose |
|---|---|
| [`START_HERE.md`](START_HERE.md) | One-time bootstrap and shortest daily workflow |
| [`CURRICULUM.md`](CURRICULUM.md) | Canonical units, IDs, prerequisites, classifications, order, and anchors |
| [`LEARNING_PATHS.md`](LEARNING_PATHS.md) | Clickable recommended sequences and project milestones |
| [`PROGRESS.md`](PROGRESS.md) | Unit states, project states, reviews, and evidence |
| [`PROJECTS.md`](PROJECTS.md) | Six substantial integration projects and their workflow |
| [`AGENTS.md`](AGENTS.md) | Lean durable repository-wide Codex behaviour |
| [`docs/WORKFLOW.md`](docs/WORKFLOW.md) | Detailed Local, Worktree, branch, validation, teaching, initialization-push, and publication procedures |
| [`scripts/validate_repo.py`](scripts/validate_repo.py) | Reproducible repository validator using only the standard library |
| [`templates/`](templates/unit.md) | Just-in-time unit, practice, experiment, review, and project templates |
| [`NOTEBOOKLM.md`](NOTEBOOKLM.md) | Concise NotebookLM handoff |
| [`BUNDLE_MANIFEST.md`](BUNDLE_MANIFEST.md) | Bootstrap archive inventory and validation expectations |

## Environment

The bootstrap pins the initially verified runtime in [`.python-version`](.python-version) and uses `uv` with [`pyproject.toml`](pyproject.toml) and [`uv.lock`](uv.lock).

No `units/` or `projects/` directory exists until the first unit or project is initialized.
