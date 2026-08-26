# Start Here

This repository has a one-time setup workflow, then a simple daily topic workflow.

## One-time bootstrap: use Local

The existing GitHub repository has a small tracked `README.md`. Extracting the bootstrap ZIP replaces it and adds the remaining files.

1. Extract `python-mastery-bootstrap.zip` directly into the local repository root.
2. Open the first Codex chat using the **Local** checkout, not a Worktree.
3. Paste this exact prompt:

```text
Initialize the Python Mastery repository bootstrap locally.

Read AGENTS.md and START_HERE.md. Inspect Git status and verify that the extracted curriculum, learning paths, progress tracker, projects, templates, configuration, links, and Git workflow are valid.

Create or resume the local branch setup/python-mastery-bootstrap, commit only the validated bootstrap files, and report the validation results and commit.

Do not push, open a pull request, or merge anything. Give me the exact publication prompt when the local bootstrap is ready.
```

Codex must run:

```bash
python scripts/validate_repo.py
```

The bootstrap initialization creates or resumes `setup/python-mastery-bootstrap`, validates the extracted files, and commits only the bootstrap locally. It does not push or merge.

4. After reviewing the local commit, publish with this exact prompt:

```text
Publish the validated Python Mastery bootstrap.

Push setup/python-mastery-bootstrap, create a pull request into main, merge it after validation passes, and synchronize local main.

Never force-push or bypass failed checks. Stop if authentication, conflicts, branch protection, or unrelated changes require my action.
```

Do not initialize a topic or project until the bootstrap is committed and `main` contains the validated baseline.

## Daily topics: use one Worktree per topic

### 1. Choose a path

Open [LEARNING_PATHS.md](LEARNING_PATHS.md). Paths are recommendations; topics may still be studied in another order with a prerequisite bridge.

### 2. Find the topic ID

Keep one permanent curriculum-helper chat and ask naturally:

```text
Which topic should I study for Python decorators?
```

The helper returns the canonical ID, exact topic name, reason, essential prerequisites, related topics, repository folder state, and the exact initialization prompt. It cannot know whether another ChatGPT or Codex chat exists.

### 3. Open and initialize the dedicated topic chat

For every topic:

1. synchronize local `main`;
2. open a new Codex chat using **Worktree** based on that latest `main`;
3. say only:

```text
Initialize <TOPIC-ID>.
```

Example:

```text
Initialize PY-FIT-050.
```

A new Worktree may begin in detached `HEAD`; Codex handles that safely and creates or resumes exactly `topic/<TOPIC-ID>`.

After validation and relevant tests pass, Codex commits the initialized unit and automatically pushes that exact topic branch with a normal non-force push. It sets the upstream on the first push and reports the result. Initialization does not create a pull request, merge, or modify remote `main`.

If the exact remote branch already exists, Codex fetches and compares it safely. It resumes only when no work can be overwritten or lost; divergence, authentication failure, conflicts, branch protection, or failed checks cause it to stop with the smallest required action.

If the topic branch is owned by another worktree, return to the original pinned topic chat and worktree. Codex must not create a lowercase, shortened, suffixed, or duplicate branch.

### 4. Continue naturally

In the same topic chat, ask ordinary questions:

```text
Explain this visually.
Show me another example.
Give me a practice problem.
Create an experiment for this.
Review my attempt.
Quiz me.
```

You do not need to repeat the topic ID or select a mode.

Only the initialized version is pushed automatically. Later notes, exercises, reviews, experiments, and corrections may be committed locally but are not pushed automatically. The topic branch therefore already exists on GitHub while newer learning changes may remain only in the pinned worktree.

### 5. Finish the topic

Keep any changes made after initialization local:

```text
I completed <TOPIC-ID>. Keep any new changes local and do not push or merge.
```

Or publish the latest changes and merge:

```text
I completed <TOPIC-ID>. Finalize it, push the latest changes, and merge the topic branch into main.
```

If you say only that the topic is complete, Codex asks:

```text
Should I keep the latest changes local, or push them and merge the branch into main?
```

Keeping newer changes local does not remove the initialized version already present on GitHub. Keep a chat and worktree pinned while it contains unpushed learning changes. Archive it only after safe merge and confirmation that no local work remains.

## Milestone projects: use a dedicated Worktree

Find the project in [PROJECTS.md](PROJECTS.md), open a dedicated Worktree chat from the latest synchronized `main`, and say:

```text
Initialize project <PROJECT-ID>.
```

After validation and relevant tests pass, Codex commits and automatically pushes exactly `project/<PROJECT-ID>` with a normal non-force push. It sets upstream when needed, but it does not create a pull request, merge, modify remote `main`, or advance any curriculum-unit learning state.

Keep any changes made after initialization local:

```text
I completed project <PROJECT-ID>. Keep any new changes local and do not push or merge.
```

Or publish the latest changes and merge:

```text
I completed project <PROJECT-ID>. Finalize it, push the latest changes, and merge the project branch into main.
```

If completion is stated without a publication choice, Codex asks:

```text
Should I keep the latest changes local, or push them and merge the branch into main?
```

The project branch already has its initialized version on GitHub even when later project changes remain local.

For detailed branch ownership, remote divergence, validation, evidence, and publication rules, read [docs/WORKFLOW.md](docs/WORKFLOW.md).
