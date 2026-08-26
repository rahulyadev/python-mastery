<!--
Create only when observation reveals hidden behaviour:
units/{{DOMAIN_SLUG}}/{{TOPIC_ID}}-{{TOPIC_SLUG}}/experiments/{{EXPERIMENT_ID}}-{{EXPERIMENT_SLUG}}/README.md

Never claim the experiment ran unless actual output was captured.
The validated initialized branch is already remote; later experiment changes remain local until the completion publication choice.
-->

# {{EXPERIMENT_ID}} — {{EXPERIMENT_TITLE}}

| Field | Value |
|---|---|
| Owning unit | [{{TOPIC_ID}}](../../README.md) |
| Curriculum | [CURRICULUM.md](../../../../../CURRICULUM.md#{{TOPIC_ANCHOR}}) |
| Topic branch | `topic/{{TOPIC_ID}}` |
| Precise question | {{ONE_QUESTION}} |
| Classification | Language / Standard library / CPython / Tooling / Platform-specific |
| Status | Planned / Run / Interpreted / Reproduced |
| Risk | None / Resource / Concurrency / Filesystem / Process / Other |

## 1. Why an experiment is necessary

{{WHAT_PROSE_ALONE_CANNOT_REVEAL}}

## 2. Hypothesis

Before execution:

> {{PRECISE_EXPECTED_BEHAVIOUR_AND_REASON}}

Alternative outcome:

> {{PLAUSIBLE_ALTERNATIVE}}

## 3. Environment

Record actual values.

```text
Date:
Operating system:
Architecture:
Python version:
sys.version:
sys.implementation:
Build type:
Free-threaded build:
Dependencies:
CPU:
Relevant environment variables:
```

For a benchmark, also record:

```text
Power mode:
Background workload:
Warm-up policy:
Trial count:
Input size and distribution:
Timing method:
```

## 4. Controls and variables

### Controlled

- {{CONTROLLED_ITEM}}

### Changed

- {{INDEPENDENT_VARIABLE}}

### Measured

- {{OBSERVABLE_RESULT}}

## 5. Files

```text
{{EXPERIMENT_DIRECTORY_TREE}}
```

## 6. Reproduction command

```bash
{{EXACT_COMMAND}}
```

## 7. Prediction

```text
{{PREDICTED_OUTPUT_OR_PATTERN}}
```

## 8. Observed output

Add only after execution.

```text
{{ACTUAL_OUTPUT}}
```

Do not edit observed output to match the hypothesis. For large output, keep only the relevant excerpt and state what was omitted.

## 9. Interpretation

1. {{WHAT_THE_OUTPUT_DIRECTLY_SHOWS}}
2. {{WHAT_CAN_REASONABLY_BE_INFERRED}}
3. {{WHAT_CANNOT_BE_INFERRED}}

## 10. Visual interpretation

```text
{{OPTIONAL_STATE_TIMELINE_OR_MEMORY_VISUAL}}
```

### How to read this visual

{{READING_GUIDE}}

### Key insight

{{KEY_INSIGHT}}

### Simplification or limitation

{{LIMITATION}}

Remove this section if no visual is useful.

## 11. Language and implementation conclusion

| Conclusion | Classification | Python or implementation version | Portability note |
|---|---|---|---|
| {{CONCLUSION}} | Language / Standard library / CPython / Platform | {{VERSION}} | {{NOTE}} |

## 12. Limitations and threats to validity

- {{LIMITATION_1}}
- {{LIMITATION_2}}
- {{LIMITATION_3}}

## 13. Follow-up

- Related unit: `{{FULL_CANONICAL_UNIT_ID}}`
- Improved experiment:
- Remaining question:

## 14. Authoritative sources

1. {{SOURCE_TITLE}}, {{EXACT_SECTION}}, accessed {{YYYY_MM_DD}}.
