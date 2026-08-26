# Python Mastery Workflow

[Start here](../START_HERE.md) · [Curriculum](../CURRICULUM.md) · [Learning paths](../LEARNING_PATHS.md) · [Progress](../PROGRESS.md) · [Projects](../PROJECTS.md)

This document contains detailed procedures intentionally kept out of the lean `AGENTS.md`.

## 1. Operating model

- Use the Local checkout for the one-time bootstrap.
- Use one dedicated Worktree chat per learning unit or milestone project.
- Keep one permanent curriculum-helper chat.
- Use ordinary language after a topic or project is established.
- Create unit and project folders only when initialized.
- Keep the bootstrap local until its separate publication prompt.
- Push only the successfully validated initialization commit for an exact topic or project branch; keep later learning changes local until an explicit completion choice.
- Run `python scripts/validate_repo.py` during bootstrap, initialization, completion, and publication.
- Treat notes, practice, experiments, reviews, and projects as evidence tools rather than automatic completion badges.

## 2. One-time bootstrap in Local

Extract the ZIP directly into the existing local repository root. The tracked minimal `README.md` will be replaced and the remaining bootstrap files will appear as untracked files.

Open the first Codex chat in **Local** and paste exactly:

```text
Initialize the Python Mastery repository bootstrap locally.

Read AGENTS.md and START_HERE.md. Inspect Git status and verify that the extracted curriculum, learning paths, progress tracker, projects, templates, configuration, links, and Git workflow are valid.

Create or resume the local branch setup/python-mastery-bootstrap, commit only the validated bootstrap files, and report the validation results and commit.

Do not push, open a pull request, or merge anything. Give me the exact publication prompt when the local bootstrap is ready.
```

This authorizes local branch creation or resumption, validation, and local commits only.

### Bootstrap branch procedure

1. Inspect `git status`, the current branch, local branches, and worktrees.
2. Use exactly `setup/python-mastery-bootstrap`.
3. If the branch exists in the current Local checkout, resume it.
4. If it is checked out in another worktree, stop and identify that worktree rather than creating a duplicate.
5. Preserve unrelated changes; never stash, reset, discard, or commit them automatically.
6. Verify the extracted inventory against `BUNDLE_MANIFEST.md`.
7. Run:

   ```bash
   python scripts/validate_repo.py
   ```

8. Inspect the diff and commit only validated bootstrap files.
9. Report the validation results, branch, commit hash and subject, and changed files.
10. Provide the exact publication prompt below.

Do not initialize a topic or project until the bootstrap is committed and `main` contains the validated baseline.

## 3. Bootstrap publication

The only bootstrap publication command is:

```text
Publish the validated Python Mastery bootstrap.

Push setup/python-mastery-bootstrap, create a pull request into main, merge it after validation passes, and synchronize local main.

Never force-push or bypass failed checks. Stop if authentication, conflicts, branch protection, or unrelated changes require my action.
```

This authorizes:

1. rerunning repository validation;
2. confirming the bootstrap commit and clean intended diff;
3. pushing `setup/python-mastery-bootstrap`;
4. creating a pull request into `main` when supported;
5. merging only after checks pass;
6. preferring squash merge unless repository policy says otherwise;
7. synchronizing the Local `main` checkout;
8. reporting the branch, commits, pull request, checks, merge, main synchronization, and changed files.

Never force-push, bypass checks or branch protection, silently delete conflicting work, or claim remote work succeeded when it did not.

## 4. Permanent curriculum-helper chat

Suggested permanent instruction:

```text
Find the best curriculum unit for my topic or question. Return the canonical unit ID, exact title, why it is the correct unit, essential prerequisites, closely related units, whether its unit folder exists according to the repository, and the exact initialization prompt. Do not create or modify the unit unless I ask. If the topic spans units, choose one primary unit and explain where the remaining parts belong. Never claim to know whether another ChatGPT or Codex chat exists.
```

Natural request:

```text
Which topic should I study for Python decorators?
```

Expected result:

```text
Primary unit: PY-FIT-050 — Decorators
Why: ...
Essential prerequisites: PY-FIT-030, PY-FIT-040
Related units: ...
Folder state: absent or existing
Initialization prompt: Initialize PY-FIT-050.
```

## 5. Worktree model for topics and projects

After the bootstrap is on `main`:

1. synchronize the Local `main` checkout;
2. create a new Codex chat using **Worktree** based on that latest `main`;
3. keep that chat and worktree dedicated to one topic or project.

A new Worktree may begin in detached `HEAD`. Detached `HEAD` is acceptable before initialization because the selected commit is the candidate baseline.

Before branch creation or resumption, inspect:

```bash
git status --short
git rev-parse HEAD
git symbolic-ref --short -q HEAD
git branch --list
git branch --remotes
git worktree list --porcelain
```

A read-only fetch of `origin/main` is allowed when needed to verify the selected baseline:

```bash
git fetch origin main
```

Compare the selected `HEAD` with local `main` and `origin/main`.

- For a new topic or project branch, the selected commit must be the latest synchronized `main` commit.
- If the new-branch baseline is stale, stop and say: `Synchronize local main, create a fresh Worktree from main, and run the initialization prompt again.`
- Do not silently move a stale detached worktree to a newer commit.
- An existing exact topic or project branch is a resumption case; do not recreate it from `main`.

### Exact remote-branch comparison

Before creating or resuming a branch, check whether the exact remote branch exists. A read-only lookup and fetch are allowed:

```bash
git ls-remote --heads origin "refs/heads/topic/<TOPIC-ID>"
git ls-remote --heads origin "refs/heads/project/<PROJECT-ID>"
```

Fetch only the applicable exact branch when it exists:

```bash
git fetch origin "refs/heads/topic/<TOPIC-ID>:refs/remotes/origin/topic/<TOPIC-ID>"
git fetch origin "refs/heads/project/<PROJECT-ID>:refs/remotes/origin/project/<PROJECT-ID>"
```

Apply these rules before editing:

- If neither local nor remote exact branch exists, create the exact branch from the verified latest `main` commit.
- If only the remote exact branch exists, attach a clean, unowned worktree to a local branch tracking that exact remote branch.
- If local and remote exact branches are identical, resume them.
- If the remote branch is an ancestor of the local branch, resume locally; a later normal push may fast-forward the remote branch.
- If the local branch is an ancestor of the remote branch, fast-forward the clean local branch before editing.
- If local and remote branches have diverged, stop and report the smallest required reconciliation action. Never reset, force, or choose a side automatically.
- If uncommitted or unrelated changes make comparison or checkout unsafe, stop instead of overwriting or moving them.

### Branch ownership

Git permits one branch to be checked out in only one worktree.

- If already on the exact branch, resume it.
- If the exact branch exists and is owned by another worktree, stop and direct Rahul to the original pinned chat and worktree.
- If the original worktree no longer exists and the exact branch is unowned, attach the current clean worktree to that exact branch.
- Never create `-2`, `-new`, lowercase, shortened, or otherwise suffixed duplicates.
- Never delete a worktree or branch merely to acquire it.

A successful initialization later authorizes one normal push of the exact topic or project branch. The read-only checks above do not authorize a pull request, merge, remote `main` change, force-push, or publication of any other branch.

Keep a topic or project chat and worktree pinned while it contains unmerged or unpushed later work. Archive a worktree only after its branch is safely merged, the merge is verified, and no local work remains.

## 6. Dedicated topic chat

The first prompt is only:

```text
Initialize <TOPIC-ID>.
```

After initialization, continue naturally:

```text
Explain this visually.
I still do not understand this part.
Give me a debugging exercise.
Create an experiment for this.
Review my attempt.
Quiz me.
```

The topic ID does not need to be repeated in the same chat.

## 7. Topic initialization

`Initialize <TOPIC-ID>.` authorizes:

- reading relevant instructions;
- validating the exact ID in `CURRICULUM.md`;
- inspecting only the relevant curriculum and progress entries;
- verifying the latest synchronized `main` baseline for a new branch;
- safely fetching and comparing any existing exact remote branch;
- creating or resuming exactly `topic/<TOPIC-ID>`;
- creating the just-in-time unit folder;
- generating complete default unit content;
- updating only the matching tracker row and valid index links;
- running repository validation and all relevant topic code and tests;
- committing the initialized content locally;
- performing one normal non-force push of the exact topic branch after all checks pass;
- setting the upstream branch on the first push;
- reporting the branch, commit, validation, tests, push result, and changed files.

The prompt explicitly authorizes only the initialization push of `topic/<TOPIC-ID>`. It does not authorize pull-request creation, merge, remote `main` changes, force-push, failed-check bypass, unrelated unit creation, or modification of another branch.

### Exact branch rules

The branch must be:

```text
topic/<TOPIC-ID>
```

Example:

```text
topic/PY-FIT-050
```

Do not create a lowercase, suffixed, shortened, or duplicate variant.

If the remote exact branch exists, follow the comparison rules in section 5. Resume only when the result cannot overwrite or lose work. Stop on divergence, unsafe uncommitted changes, authentication failure, conflicts, branch protection, or a rejected non-fast-forward push, and report the smallest required action.

### Unit initialization procedure

1. Confirm the full ID exists in `CURRICULUM.md`.
2. Read its exact title, outcome, prerequisites, classifications, scope, size, and evidence profile.
3. Verify the worktree baseline and exact local/remote branch state using section 5.
4. Briefly explain essential missing prerequisites and provide the smallest correct bridge without blocking unnecessarily.
5. Create:

   ```text
   units/<domain-slug>/<TOPIC-ID>-<topic-slug>/README.md
   ```

6. Populate it from `templates/unit.md` with final unit content, not an empty shell.
7. Begin with `Physical Notebook Core`.
8. Preserve source, Python 3.14, Python 3.11 interview-compatibility, copyright, privacy, and solution-protection policies.
9. Create optional artifacts only when genuinely needed.
10. Set only that unit’s artifact state to `Draft`; do not advance learning state without evidence.
11. Add links only to paths that exist.
12. Run:

    ```bash
    python scripts/validate_repo.py
    ```

13. Run all relevant Python examples and tests for the initialized topic.
14. Commit the initialized content locally with sensible boundaries.
15. Push normally:

    ```bash
    git push -u origin topic/<TOPIC-ID>
    ```

    When the upstream already exists, use a normal `git push origin topic/<TOPIC-ID>`. Never use a force option.
16. Report the worktree, exact branch, commit hash and subject, repository validation, topic tests, push result, upstream state, and changed files.

Only this validated initialization content is pushed automatically. Subsequent learning changes follow sections 16 and 18–20.

## 8. Prerequisite bridges

Classify a prerequisite as hard, soft, or co-requisite.

When a prerequisite is missing:

1. name its complete canonical ID and title;
2. explain the dependency briefly;
3. give the minimum correct bridge model;
4. recommend the prerequisite’s dedicated chat;
5. continue unless proceeding would make the material materially misleading.

A bridge never marks the prerequisite as learned.

## 9. Teaching sequence

Unless Rahul requests another order:

1. problem solved;
2. one-sentence mental model;
3. minimal example;
4. important visual;
5. rules or invariants;
6. formal semantics or API contract;
7. additional examples;
8. edge cases and misconceptions;
9. performance and production trade-offs;
10. Python 3.11 versus 3.14 compatibility;
11. CPython internals when relevant;
12. practice, retrieval, or experiment evidence.

## 10. Physical Notebook Core

Every unit begins with `Physical Notebook Core`, containing only:

- the problem;
- one-sentence mental model;
- one important visual;
- governing rules;
- one minimal example;
- one failure or misconception;
- trade-offs;
- short interview-revision cues.

It must remain concise enough to reconstruct by hand. Deeper material follows afterwards.

## 11. Visual explanations

Prefer object/reference diagrams, timelines, call stacks, namespace lookup diagrams, iterator-state tables, event-loop timelines, memory-ownership diagrams, before/after comparisons, and small numerical examples.

Every non-trivial visual must be followed by:

### How to read this visual

Explain reading order, symbols, arrows, and state changes.

### Key insight

State the conclusion to retain.

### Simplification or limitation

State what is omitted and whether the visual is conceptual, language-level, CPython-specific, or platform-specific.

Never present a conceptual diagram as literal CPython memory layout unless version-specific and sourced.

## 12. Vocabulary and English support

Keep vocabulary in the integrated unit `README.md`.

Normally select two to five genuinely useful technical or professional words. For each include pronunciation, simple meaning, optional short Hindi cue, meaning in the current Python context, and five natural examples. At least two examples must suit an interview or engineering discussion.

## 13. Practice and solution protection

1. Exercises begin unsolved.
2. Preserve the learner’s attempt.
3. Ask for a prediction before execution when appropriate.
4. Give one progressive hint at a time.
5. Do not leak solutions through comments, tests, examples, fixtures, or filenames.
6. Identify the first incorrect assumption before offering replacement code.
7. Passing tests are insufficient when reasoning is wrong.
8. Add a comparison solution only after the learner closes the exercise.

## 14. Runtime experiments

Use an experiment when observation reveals hidden behaviour such as aliasing, lookup, closures, descriptors, imports, frames, bytecode, garbage collection, races, event-loop scheduling, cancellation, allocation, profiling, specialization, or free-threading.

Record the question, hypothesis, environment, controls, exact command, prediction, actual output, interpretation, classification, and limitations. Never invent an observation.

## 15. Quizzes and interviews

Ask one question at a time and wait. After each answer, state what was correct, identify the exact missing reasoning step, give a concise correction, and increase difficulty according to performance. Do not reveal the expected answer before the attempt.

## 16. Durable clarifications

Update canonical notes only when a clarification fixes an error, removes ambiguity, explains a recurring misconception, adds a missing boundary, or improves a visual or example for future readers.

Keep personal confusion history in `REVIEW.md`. Make the smallest correct edit, validate it, and commit locally on the same topic branch. Do not push later learning changes automatically; the remote branch keeps its initialized version until the completion publication choice.

## 17. Progress evaluation

Use the evidence thresholds in `PROGRESS.md`.

- Initialization may set artifact state to `Draft`; it does not change learning state.
- Record actual attempts, tests, review dates, exact weaknesses, experiments, and project-transfer evidence.
- A failed review may lower the state.
- Self-reported confidence is insufficient.

## 18. Complete a topic and keep later changes local

```text
I completed <TOPIC-ID>. Keep any new changes local and do not push or merge.
```

This authorizes final local validation, honest evidence updates, and remaining local commits. It authorizes no new push, pull request, or merge.

Run:

```bash
python scripts/validate_repo.py
```

The exact topic branch already has its successfully initialized version on GitHub. Any notes, exercises, reviews, experiments, corrections, evidence updates, or other commits made after initialization remain only in the pinned local worktree.

Report the worktree, branch, local commits, changed files, validation, tests, states, remaining weakness, the remote initialized version, and confirmation that newer changes were not pushed or merged.

## 19. Publish the latest topic changes and merge

```text
I completed <TOPIC-ID>. Finalize it, push the latest changes, and merge the topic branch into main.
```

This authorizes final validation, accurate evidence updates, remaining commits, a normal push of the latest `topic/<TOPIC-ID>` changes, pull-request creation when supported, merge after checks, and `main` synchronization.

Prefer squash merge. Never force-push, bypass checks or protection, discard unrelated changes, or invent a remote result. If authentication, divergence, conflicts, failed checks, or branch protection blocks publication, stop and state the smallest action required.

After safe merge and synchronization, the completed topic worktree may be archived when no local work remains.

## 20. Ambiguous topic completion

If Rahul states only that a topic is complete, ask exactly:

```text
Should I keep the latest changes local, or push them and merge the branch into main?
```

Do not infer publication permission. The initialized topic version remains on its remote branch regardless of this later choice.

## 21. Dedicated project chat

Projects are integration evidence and are never curriculum units.

Open a dedicated Worktree chat from latest synchronized `main` and say:

```text
Initialize project <PROJECT-ID>.
```

Never route a `PY-PRJ-...` ID through curriculum-unit initialization.

## 22. Project initialization

`Initialize project <PROJECT-ID>.` authorizes:

1. validating the exact ID in `PROJECTS.md` and never treating it as a curriculum unit ID;
2. verifying the latest synchronized `main` baseline for a new branch;
3. safely fetching and comparing any existing exact remote branch;
4. creating or resuming exactly `project/<PROJECT-ID>`;
5. creating the just-in-time project folder from `templates/project.md`;
6. updating only the matching project tracker row to `Active`;
7. running repository validation and all relevant project tests;
8. committing the initialized project content locally;
9. performing one normal non-force push of the exact project branch after all checks pass;
10. setting the upstream branch on the first push;
11. reporting the branch, commit, validation, tests, push result, and changed files.

The initialization prompt authorizes only the initialization push of `project/<PROJECT-ID>`. It does not authorize pull-request creation, merge, remote `main` changes, force-push, failed-check bypass, or automatic curriculum-unit learning-state changes.

Project path:

```text
projects/<PROJECT-ID>-<project-slug>/
```

Follow the remote comparison and branch-ownership rules in section 5. Stop on divergence or any condition that could overwrite or lose work.

Run:

```bash
python scripts/validate_repo.py
```

Run all relevant project tests, commit locally, and then push normally:

```bash
git push -u origin project/<PROJECT-ID>
```

When the upstream already exists, use a normal `git push origin project/<PROJECT-ID>`. Never force-push.

Only this validated initialization content is pushed automatically. Later project changes may be committed locally but remain unpushed until the completion choice.

## 23. Complete a project and keep later changes local

```text
I completed project <PROJECT-ID>. Keep any new changes local and do not push or merge.
```

This authorizes final local validation, an evidence-based project-state update, and remaining local commits only. It authorizes no new push, pull request, or merge.

The exact project branch already has its initialized version on GitHub. Any newer implementation, tests, debugging, refactoring, documentation, evidence, or tracker changes remain only in the pinned local worktree.

Project completion must not automatically advance any curriculum-unit learning state. Link project evidence to units and evaluate those units separately.

## 24. Publish the latest project changes and merge

```text
I completed project <PROJECT-ID>. Finalize it, push the latest changes, and merge the project branch into main.
```

This authorizes final validation, remaining commits, a normal push of the latest `project/<PROJECT-ID>` changes, pull-request creation when supported, merge after checks, and `main` synchronization. Prefer squash merge and apply the same remote-safety rules as topics.

After safe merge and synchronization, the completed project worktree may be archived when no local work remains.

## 25. Ambiguous project completion

If Rahul states only that a project is complete, ask exactly:

```text
Should I keep the latest changes local, or push them and merge the branch into main?
```

Do not infer publication permission. The initialized project version remains on its remote branch regardless of this later choice.

## 26. Reproducible repository validation

Run from the repository root:

```bash
python scripts/validate_repo.py
```

The validator uses only the Python standard library and checks:

- required bootstrap files;
- 121 unique curriculum IDs;
- prerequisite existence and cycles;
- progress-row consistency;
- learning-path IDs, titles, anchors, duplicates, numbering, and prerequisite order;
- six projects, detailed anchors, tracker rows, and links;
- Markdown table column counts;
- balanced code fences;
- internal and template-relative links;
- unexpected placeholders outside templates;
- shortened IDs;
- forbidden generated, archive, credential, secret, and privacy-sensitive paths.

For an archive validation and JSON report:

```bash
python scripts/validate_repo.py --archive python-mastery-bootstrap.zip --json python-mastery-bootstrap-validation.json
```

Use repository validation during bootstrap, topic initialization, project initialization, local completion, and publication. Run relevant unit or project tests in addition to the repository validator.

## 27. Markdown and link conventions

- Use complete canonical IDs.
- Use stable anchors from `CURRICULUM.md` and `PROJECTS.md`.
- Use repository-relative links.
- Do not link to an uncreated unit or project folder.
- Use template placeholders only inside files under `templates/`.
- Balance code fences.
- Use four tildes outside when documenting Markdown containing triple-backtick fences.
- Keep table headers, separators, and rows at the same column count.
- Escape literal table-cell pipes as `\|`.

## 28. Structural changes

Curriculum or repository-structure changes require an explicit reason, preservation of stable IDs unless deliberately approved, updates to affected references, repository validation, preservation of unrelated changes, and a clear report before publication.
