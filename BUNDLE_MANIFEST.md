# Python Mastery Bootstrap Manifest

Created for extraction directly into the root of `rahulyadev/python-mastery`.

## Files and responsibilities

| Path | Purpose | Primary editor | Creation time | Duplication control |
|---|---|---|---|---|
| `README.md` | Repository overview and prominent entry to `START_HERE.md` | Codex with Rahul’s review | Bootstrap | Links instead of repeating policy |
| `START_HERE.md` | One-time Local bootstrap, validated initialization pushes, and practical topic/project completion choices | Codex with Rahul’s review | Bootstrap | Points to detailed workflow |
| `AGENTS.md` | Lean durable Codex behaviour and Git safety | Rare policy edits | Bootstrap | Repository-wide rules only |
| `CURRICULUM.md` | Canonical 121-unit catalog with stable anchors and full prerequisite IDs | Explicit curriculum changes | Bootstrap | Single source of unit metadata |
| `LEARNING_PATHS.md` | Seven clickable recommended paths and project milestones | Path maintenance | Bootstrap | Links to canonical entries |
| `PROGRESS.md` | Existing unit states plus six-row project tracker | Codex after evidence | Bootstrap | Single source of learner and project state |
| `PROJECTS.md` | Six Python-focused milestone projects, stable anchors, and project Git workflow | Project planning | Bootstrap | Projects remain separate from units |
| `NOTEBOOKLM.md` | Concise NotebookLM handoff | Rare workflow edits | Bootstrap | Links to detailed policy |
| `BUNDLE_MANIFEST.md` | Archive inventory and validation summary | Bootstrap builder | Bootstrap | One inventory |
| `.gitignore` | Environment, cache, secret, private-material, and output exclusions | Repository maintenance | Bootstrap | Central ignore policy |
| `.python-version` | Initially verified CPython runtime pin | Version audit | Bootstrap | One machine-readable pin |
| `pyproject.toml` | Project metadata and recommended tooling configuration | Tooling maintenance | Bootstrap | Central tool configuration |
| `uv.lock` | Dependency-free bootstrap lock | `uv` | Bootstrap | Generated lock data |
| `docs/WORKFLOW.md` | Detailed bootstrap, Worktree, safe initialization push, later-local changes, validation, evidence, and publication procedures | Rare process edits | Bootstrap | Procedures stay out of `AGENTS.md` |
| `docs/SOURCE_AND_VERSION_POLICY.md` | Authoritative sources, Python 3.14 baseline, Python 3.11 compatibility, experiments, and benchmarks | Source/version audit | Bootstrap | One source policy |
| `docs/COPYRIGHT_AND_LICENSE.md` | Public-repository copyright, privacy, quotation, and license decision rules | Explicit owner decisions | Bootstrap | No automatic license |
| `docs/NOTEBOOKLM.md` | Detailed NotebookLM grouping, prompts, and weakness-return workflow | Rare process edits | Bootstrap | Repository remains source of truth |
| `scripts/validate_repo.py` | Standard-library-only repository and optional ZIP validator | Repository maintenance | Bootstrap | One reproducible validation command |
| `templates/unit.md` | Integrated unit note beginning with `Physical Notebook Core` | Codex | Bootstrap | One canonical unit template |
| `templates/practice.md` | Protected exercise, hint, attempt, and review structure | Codex | Bootstrap | Created only when useful |
| `templates/experiment.md` | Reproducible runtime experiment structure | Codex | Bootstrap | Created only when observation is needed |
| `templates/review.md` | Closed-book evidence, weakness, and state record | Codex | Bootstrap | Learner-specific evidence stays separate |
| `templates/project.md` | Project requirements, tests, debugging, refactoring, and design evidence | Codex | Bootstrap | One project template |

## Inventory

- Archive entries: 23 files.
- Files are stored directly at archive root; there is no wrapper directory.
- Unit folders and project folders are intentionally absent until initialized.
- The first Local bootstrap prompt and publication prompt are in `START_HERE.md`.
- Repository validation command: `python scripts/validate_repo.py`.

## Validation summary

Validation statistics are recorded in the external `python-mastery-bootstrap-validation.json` generated from the same archive. The archive SHA-256 is kept in that external report because embedding an archive’s own checksum inside itself would change the checksum.

- Curriculum units: 121 unique IDs.
- Milestone projects: 6 stable IDs.
- Markdown files: 18.
- Markdown tables: 47.
- Balanced fenced-code blocks: 74.
- Markdown links: 860.
- Template-relative links: 10.

## Intentional omissions

- No outer archive directory.
- No `.git/` directory.
- No `units/` or `projects/` directory.
- No `LICENSE`; licensing requires an explicit owner decision.
- No virtual environment, cache, transcript, credential, token, private file, or generated learning material.
