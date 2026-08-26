<!--
Create as:
units/{{DOMAIN_SLUG}}/{{TOPIC_ID}}-{{TOPIC_SLUG}}/REVIEW.md

This file stores learner-specific evidence and weaknesses.
Do not copy the full canonical note into it.
The validated initialized branch is already remote; later review changes remain local until the completion publication choice.
-->

# Review record — {{TOPIC_ID}} {{TOPIC_TITLE}}

| Field | Value |
|---|---|
| Unit note | [{{TOPIC_ID}}](README.md) |
| Progress record | [PROGRESS.md](../../../PROGRESS.md) |
| Topic branch | `topic/{{TOPIC_ID}}` |
| Artifact state | Absent / Draft / Approved |
| Learning state | Not started / Learning / Practiced / Recalled / Demonstrated / Retained |
| Last evidence date | {{YYYY_MM_DD}} |
| Recommended next review | {{YYYY_MM_DD_OR_NONE}} |
| Mastery badge | No / Yes with linked evidence |
| Strongest area | {{SPECIFIC_CAPABILITY}} |
| Weakest area | {{SPECIFIC_MISSING_REASONING_STEP}} |

## Evidence checklist

Keep only applicable items.

- [ ] Explains the simple mental model.
- [ ] States the formal mechanism.
- [ ] Reconstructs the key visual.
- [ ] Predicts representative code.
- [ ] Handles important edge cases.
- [ ] Debugs a faulty example.
- [ ] Completes required code or design work.
- [ ] Explains performance implications.
- [ ] Explains production relevance.
- [ ] Distinguishes language guarantees from implementation details.
- [ ] Transfers the idea to a new scenario.

## Review session — {{YYYY_MM_DD}}

### Conditions

| Field | Value |
|---|---|
| Closed book | Yes / No |
| Time since study | {{DURATION}} |
| Hints used | None / {{COUNT_AND_TYPE}} |
| Python baseline | {{VERSION}} |

### Blank-page reconstruction

- One-sentence model:
- Important visual:
- Three invariants:
- Counterexample:
- Code trace:
- Production use or trade-off:

### One-question-at-a-time record

#### Question 1

{{EXACT_QUESTION}}

**Learner answer summary**

{{FAITHFUL_SUMMARY}}

**What was correct**

- {{SPECIFIC_POINT}}

**Exact missing or incorrect reasoning step**

- {{SPECIFIC_STEP}}

**Correction**

{{CONCISE_CORRECTION}}

**Follow-up required**

Yes / No

Repeat for additional questions.

### Practice and experiment evidence

| Evidence link | Result | What it proves | Remaining limitation |
|---|---|---|---|
| {{VALID_RELATIVE_LINK}} | {{RESULT}} | {{EVIDENCE}} | {{LIMITATION}} |

### Demonstrated weaknesses

| Weakness | Evidence | Severity | Corrective action | Owning note section |
|---|---|---|---|---|
| {{PRECISE_WEAKNESS}} | {{QUESTION_TEST_OR_TRACE}} | Critical / Important / Minor | {{ACTION}} | {{SECTION}} |

Avoid vague entries such as “revise more.”

### Durable clarification decision

| Clarification | Canonical note? | Reason |
|---|---|---|
| {{CLARIFICATION}} | Yes / No | {{GENERAL_LESSON_OR_PERSONAL_ERROR}} |

### Status evaluation

Recommended learning state:

**{{STATE}}**

Evidence-based reason:

{{REFERENCE_THE_OBJECTIVE_TRANSITION_RULE}}

Evidence link for `PROGRESS.md`:

{{VALID_RELATIVE_LINK}}

### Completion and publication choice

Record one:

- Keep new changes local; do not push or merge.
- Push the latest changes and merge the topic branch into `main`.
- Not yet decided.

Never infer publication authorization. The initialized version may already exist on the remote topic branch.

### Next review

- Date: {{YYYY_MM_DD}}
- Target weakness:
- Transfer scenario:
- No-hint requirement:
