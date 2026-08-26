<!--
Copy to:
units/{{DOMAIN_SLUG}}/{{TOPIC_ID}}-{{TOPIC_SLUG}}/README.md

Use complete canonical IDs.
Populate real content during initialization.
Remove every non-applicable section.
Do not expose solutions to unattempted exercises.
-->

# {{TOPIC_ID}} — {{TOPIC_TITLE}}

[Curriculum entry](../../../CURRICULUM.md#{{TOPIC_ANCHOR}}) · [Progress](../../../PROGRESS.md) · Local branch: `topic/{{TOPIC_ID}}`

## Physical Notebook Core

Keep this section concise enough to reconstruct by hand. It is not a duplicate of the deep note.

### Problem this concept solves

{{CONCISE_PROBLEM}}

### One-sentence mental model

> {{ONE_SENTENCE_MODEL}}

### One important visual

```text
{{CONCISE_VISUAL}}
```

#### How to read this visual

{{READING_ORDER_SYMBOLS_AND_STATE}}

#### Key insight

{{ONE_CONCLUSION_TO_RETAIN}}

#### Simplification or limitation

{{WHAT_THE_VISUAL_OMITS_AND_WHETHER_IT_IS_CONCEPTUAL_OR_LITERAL}}

### Governing rules or invariants

1. {{RULE_1}}
2. {{RULE_2}}
3. {{RULE_3}}

### Minimal example

```python
# Replace with the smallest runnable example that reveals the mechanism.
```

Expected reasoning:

1. {{REASONING_STEP_1}}
2. {{REASONING_STEP_2}}

### One failure or misconception

**Mistake:** {{COMMON_MISTAKE}}

**Correction:** {{CORRECT_MODEL}}

### Important trade-offs

- {{TRADE_OFF_1}}
- {{TRADE_OFF_2}}

### Interview-revision cues

- {{MENTAL_MODEL_CUE}}
- {{PREDICTION_CUE}}
- {{TRADE_OFF_CUE}}

## Unit metadata

| Field | Value |
|---|---|
| Domain | {{DOMAIN_TITLE}} |
| Canonical ID | `{{TOPIC_ID}}` |
| Learning outcome | {{OBSERVABLE_OUTCOME}} |
| Hard prerequisites | {{FULL_CANONICAL_IDS_OR_NONE}} |
| Soft prerequisites | {{FULL_CANONICAL_IDS_OR_NONE}} |
| Co-requisites | {{FULL_CANONICAL_IDS_OR_NONE}} |
| Priority | Core / Professional / Advanced / Reference |
| Interview frequency | High / Medium / Low |
| Backend relevance | High / Medium / Low |
| Depth | D1 / D2 / D3 / D4 |
| Scope | Language / Standard library / Tooling / CPython / Platform-specific / Third-party |
| Size | S / M / L / XL |
| Evidence profile | E / C / D / X / (X) / R |
| Canonical Python | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Initially tested runtime | {{IMPLEMENTATION_AND_VERSION}} |
| Last source audit | {{YYYY_MM_DD}} |
| Artifact state | Draft / Approved |

## 1. Learning outcome and evidence

After this unit, the learner should be able to:

1. {{CAPABILITY_1}}
2. {{CAPABILITY_2}}
3. {{CAPABILITY_3}}

Required evidence:

- {{EXPLANATION_OR_RECONSTRUCTION_EVIDENCE}}
- {{CODE_TEST_OR_DEBUG_EVIDENCE}}
- {{EXPERIMENT_OR_PRODUCTION_TRANSFER_IF_REQUIRED}}

## 2. Prerequisite bridge

Include only when a prerequisite is missing.

| Type | Unit | Why it matters | Minimum bridge |
|---|---|---|---|
| Hard / Soft / Co-requisite | `{{PREREQUISITE_ID}}` | {{REASON}} | {{MINIMUM_CORRECT_MODEL}} |

A bridge does not replace or complete the prerequisite unit.

## 3. Vocabulary and professional English

Select normally two to five genuinely useful words. Remove this section when no difficult vocabulary adds value.

### {{WORD}}

| Item | Content |
|---|---|
| Pronunciation | {{IPA_OR_CLEAR_PHONETIC_GUIDE}} |
| Simple English meaning | {{PLAIN_MEANING}} |
| Hindi cue | {{OPTIONAL_SHORT_HINDI_CUE_OR_DASH}} |
| Meaning in this Python context | {{CONTEXTUAL_MEANING}} |

Natural examples:

1. {{GENERAL_EXAMPLE_1}}
2. {{GENERAL_EXAMPLE_2}}
3. {{GENERAL_EXAMPLE_3}}
4. **Interview:** {{INTERVIEW_EXAMPLE}}
5. **Engineering discussion:** {{ENGINEERING_EXAMPLE}}

Repeat only for selected words.

## 4. Deep explanation

### 4.1 Why the mechanism exists

{{EXPLANATION}}

### 4.2 Formal semantics or API contract

{{PRECISE_MECHANISM_WITH_NEARBY_CITATIONS_FOR_SUBTLE_CLAIMS}}

### 4.3 Execution sequence

| Step | Event | Relevant state |
|---:|---|---|
| 1 | {{EVENT}} | {{STATE}} |
| 2 | {{EVENT}} | {{STATE}} |

## 5. Additional visual models

Use only visuals that reveal otherwise hidden state.

### {{VISUAL_TITLE}}

```text
{{VISUAL}}
```

#### How to read this visual

{{READING_GUIDE}}

#### Key insight

{{KEY_INSIGHT}}

#### Simplification or limitation

{{LIMITATION_AND_SCOPE}}

Repeat the complete four-part structure for every non-trivial visual.

## 6. Worked examples

### 6.1 Small example

```python
# Replace with runnable code.
```

Prediction before execution:

{{PREDICTION_AND_REASONING}}

Observed result, only when actually run:

```text
{{ACTUAL_OUTPUT_OR_NOT_RUN}}
```

### 6.2 Realistic Python or backend example

```python
# Keep frameworks and infrastructure secondary to the Python concept.
```

Explain:

- why this design fits;
- alternatives;
- failure modes;
- maintainability implications.

### 6.3 Debugging example

Keep the correction hidden until the learner attempts it.

```python
# Replace with a focused broken example.
```

## 7. Edge cases and misconceptions

| Mistake or edge case | Why it seems plausible | Correct model | How to expose it |
|---|---|---|---|
| {{CASE}} | {{WHY}} | {{CORRECTION}} | {{TEST_TRACE_OR_COUNTEREXAMPLE}} |

## 8. Complexity and performance

| Operation or design | Typical complexity or cost | Qualification |
|---|---:|---|
| {{OPERATION}} | {{COST}} | {{INPUT_VERSION_OR_IMPLEMENTATION_CAVEAT}} |

Separate asymptotic reasoning from measured performance. Never invent measurements.

## 9. Production relevance and trade-offs

Discuss only relevant concerns:

- correctness;
- readability;
- API stability;
- typing;
- testing;
- error handling;
- concurrency;
- memory;
- latency;
- security;
- observability;
- portability.

## 10. Version and implementation boundaries

| Claim or feature | Classification | First supported Python | Python 3.11-compatible alternative | Notes |
|---|---|---:|---|---|
| {{CLAIM}} | Language / Standard library / CPython / Tooling / Platform | {{VERSION}} | {{ALTERNATIVE_OR_NOT_APPLICABLE}} | {{PORTABILITY_NOTE}} |

Clearly distinguish modern Python recommendations from code likely to run on older interview platforms.

## 11. Practice brief

List exercises without solutions.

| Exercise ID | Type | Difficulty | Evidence target | Artifact |
|---|---|---:|---|---|
| `{{TOPIC_ID}}-P01` | Predict / Implement / Debug / Review / Design | 1–5 | {{EVIDENCE}} | {{PATH_OR_INLINE}} |

Create `practice/README.md` only when a separate work area is useful.

## 12. Interview prompts

Do not include full answers before an attempt.

1. {{QUESTION_1}}
2. {{QUESTION_2}}
3. {{SENIOR_TRADE_OFF_QUESTION}}

A strong answer should eventually demonstrate:

- {{MECHANISM}}
- {{BOUNDARY}}
- {{TRADE_OFF}}

## 13. Closed-book revision cues

Without reading the note:

1. {{MENTAL_MODEL_QUESTION}}
2. {{VISUAL_RECONSTRUCTION_QUESTION}}
3. {{PREDICTION_QUESTION}}
4. {{DEBUGGING_QUESTION}}
5. {{PRODUCTION_DECISION_QUESTION}}

## 14. Authoritative sources

Cite important claims near the relevant paragraph. Keep this list compact and include only sources actually read.

1. {{SOURCE_TITLE}}, {{EXACT_SECTION}}, Python {{VERSION}}, accessed {{YYYY_MM_DD}}.
2. {{SOURCE_TITLE}}, {{EXACT_SECTION}}, accessed {{YYYY_MM_DD}}.

## 15. Open technical questions

- {{REAL_UNCERTAINTY_OR_UNRESOLVED_SOURCE_QUESTION}}

Remove this section when there are no open questions.

## 16. Durable clarification log

| Date | Clarification | Why it belongs in canonical notes | Source or evidence |
|---|---|---|---|
| {{YYYY_MM_DD}} | {{CLARIFICATION}} | {{GENERAL_VALUE}} | {{SOURCE_OR_TEST}} |
