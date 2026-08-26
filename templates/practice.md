<!--
Create only when separate practice is useful:
units/{{DOMAIN_SLUG}}/{{TOPIC_ID}}-{{TOPIC_SLUG}}/practice/README.md

Exercises begin unsolved.
Do not pre-populate final solutions or all hints.
The validated initialized branch is already remote; later practice changes remain local until the completion publication choice.
-->

# Practice — {{TOPIC_ID}} {{TOPIC_TITLE}}

| Field | Value |
|---|---|
| Unit note | [{{TOPIC_ID}}](../README.md) |
| Curriculum | [CURRICULUM.md](../../../../CURRICULUM.md#{{TOPIC_ANCHOR}}) |
| Topic branch | `topic/{{TOPIC_ID}}` |
| Evidence target | E / C / D / X / R |
| Attempt required before solution | Yes |
| Test command | `{{TEST_COMMAND_OR_NOT_APPLICABLE}}` |
| Status | Not attempted / In progress / Reviewed / Closed |

## Practice rules

1. Record a prediction or design before running code when relevant.
2. Preserve the original attempt.
3. Ask for one progressive hint at a time.
4. A passing test is not enough when the reasoning is wrong.
5. Final comparison code appears only after the exercise is closed.
6. Do not push later practice changes automatically.

## Exercise index

| Exercise ID | Type | Difficulty | Objective | Files | Status |
|---|---|---:|---|---|---|
| `{{TOPIC_ID}}-P01` | Predict / Implement / Debug / Review / Design | 1–5 | {{OBJECTIVE}} | `{{PATH}}` | Not attempted |

## {{TOPIC_ID}}-P01 — {{EXERCISE_TITLE}}

### Problem

{{EXACT_TASK_WITHOUT_SOLUTION_LEAKAGE}}

### Learning evidence

This exercise should demonstrate:

- {{CAPABILITY_1}}
- {{CAPABILITY_2}}

### Constraints

- {{CONSTRAINT_1}}
- {{CONSTRAINT_2}}

### Examples

```text
Input:
{{INPUT}}

Expected observable behaviour:
{{BEHAVIOUR}}
```

### Required edge cases

- {{EDGE_CASE_1}}
- {{EDGE_CASE_2}}

### Acceptance criteria

- [ ] Behaviour is correct.
- [ ] Required tests pass.
- [ ] Important edge cases are handled.
- [ ] Complexity or trade-offs are explained.
- [ ] The learner can explain why the design works.
- [ ] No unrelated abstraction was added.

### Prediction before execution

- Expected result:
- Reasoning:
- Uncertainty:

### Learner attempt

- Attempt file:
- Learner’s reasoning:
- Test command:
- Observed result:

### Progressive hints

Do not write hints until requested.

#### Hint 1

{{ADD_AFTER_REQUEST: SMALLEST_CONCEPTUAL_NUDGE}}

#### Hint 2

{{ADD_AFTER_ANOTHER_ATTEMPT: NARROW_THE_FALSE_ASSUMPTION}}

#### Hint 3

{{ADD_AFTER_ANOTHER_ATTEMPT: SUGGEST_AN_OPERATION_OR_INVARIANT}}

### Review

#### What is correct

- {{SPECIFIC_POINT}}

#### First incorrect assumption or missing reasoning step

{{EXACT_STEP}}

#### Smallest edge case that exposes it

{{EDGE_CASE_AND_EXPLANATION}}

#### Next attempt

{{ONE_TARGETED_CHANGE_OR_QUESTION}}

### Test evidence

Record only actual execution.

```text
Command:
{{COMMAND}}

Result:
{{ACTUAL_RESULT}}
```

### Closure

Add only after the learner closes the exercise.

- Final learner solution:
- Optional comparison solution:
- Trade-offs:
- Remaining weakness:
- Evidence link for `PROGRESS.md`:
