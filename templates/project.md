<!--
Create only when a project starts:
projects/{{PROJECT_ID}}-{{PROJECT_SLUG}}/README.md

Milestone projects integrate completed units; they are not curriculum units.
Use complete canonical unit IDs in every prerequisite and evidence reference.
-->

# {{PROJECT_ID}} — {{PROJECT_TITLE}}

| Field | Value |
|---|---|
| Canonical project plan | [PROJECTS.md](../../PROJECTS.md#{{PROJECT_ANCHOR}}) |
| Progress record | [PROGRESS.md](../../PROGRESS.md) |
| Required unit prerequisites | {{FULL_CANONICAL_UNIT_IDS}} |
| Recommended unit prerequisites | {{FULL_CANONICAL_UNIT_IDS_OR_NONE}} |
| Python baseline | Python 3.14 |
| Interview compatibility | Python 3.11 |
| Project state | Planned / Active / Complete |
| Dedicated project chat | Yes |

## 1. Project problem

{{REALISTIC_PROBLEM_STATEMENT}}

## 2. Interview and learning value

This project should demonstrate:

- {{CROSS_UNIT_CAPABILITY_1}}
- {{CROSS_UNIT_CAPABILITY_2}}
- {{DESIGN_OR_TRADE_OFF_CAPABILITY}}
- {{DEBUGGING_OR_PERFORMANCE_CAPABILITY}}

## 3. Scope

### Included

- {{IN_SCOPE_ITEM}}

### Explicitly excluded

- framework curriculum;
- real cloud infrastructure;
- production database administration;
- distributed-systems expansion;
- unrelated user-interface work;
- {{PROJECT_SPECIFIC_EXCLUSION}}.

## 4. Required capabilities

| Capability | Owning unit IDs | Project evidence |
|---|---|---|
| {{CAPABILITY}} | `{{UNIT_ID}}`, `{{UNIT_ID}}` | {{FILE_TEST_OR_DESIGN_RECORD}} |

## 5. Proposed architecture

```text
{{SMALL_DIRECTORY_OR_COMPONENT_DIAGRAM}}
```

### How to read this visual

{{READING_GUIDE}}

### Key insight

{{KEY_ARCHITECTURAL_INSIGHT}}

### Simplification or limitation

{{WHAT_IS_INTENTIONALLY_NOT_MODELLED}}

## 6. Functional requirements

1. {{REQUIREMENT_1}}
2. {{REQUIREMENT_2}}
3. {{REQUIREMENT_3}}

## 7. Quality requirements

- typed public boundaries where appropriate;
- deterministic automated tests;
- explicit error handling;
- useful logging without sensitive data;
- bounded resource use;
- reproducible commands;
- Python 3.14 canonical implementation;
- Python 3.11 compatibility notes where relevant.

## 8. Tests

| Test layer | Required coverage |
|---|---|
| Unit | {{PURE_COMPONENTS_AND_EDGE_CASES}} |
| Integration | {{BOUNDARY_OR_WORKFLOW}} |
| Property-based | {{INVARIANTS_IF_USEFUL}} |
| Concurrency or timing | {{DETERMINISTIC_STRATEGY_IF_RELEVANT}} |
| Regression | {{SEEDED_BUGS}} |

## 9. Debugging and refactoring checkpoints

### Seeded defect or failure 1

{{DEFECT_WITHOUT_IMMEDIATE_SOLUTION}}

### Seeded defect or failure 2

{{DEFECT_WITHOUT_IMMEDIATE_SOLUTION}}

### Refactoring checkpoint

Explain:

- current design pressure;
- proposed change;
- preserved behaviour;
- rejected alternatives;
- test evidence.

## 10. Design decisions

| Decision | Options considered | Choice | Trade-offs | Evidence |
|---|---|---|---|---|
| {{DECISION}} | {{OPTIONS}} | {{CHOICE}} | {{TRADE_OFFS}} | {{LINK}} |

## 11. Performance or runtime evidence

Include only when relevant.

- Hypothesis:
- Measurement environment:
- Baseline:
- Change:
- Actual result:
- Limitations:

Never invent measurements.

## 12. Definition of done

- [ ] All required functionality is implemented.
- [ ] Required tests pass.
- [ ] Edge cases and failure paths are covered.
- [ ] At least two seeded defects were diagnosed and fixed.
- [ ] At least one meaningful refactoring was defended.
- [ ] Design and trade-offs are documented.
- [ ] Version and compatibility notes are accurate.
- [ ] No secrets, private data, or copied proprietary material exist.
- [ ] Relevant unit evidence links are recorded.
- [ ] A final senior-interview walkthrough was completed.
- [ ] `PROJECTS.md` and `PROGRESS.md` were updated with evidence.

## 13. Final interview walkthrough

Prepare concise answers for:

1. What problem does the project solve?
2. Why was this architecture chosen?
3. Which Python semantics materially affected the design?
4. Which failure was hardest to diagnose?
5. What measurement changed a decision?
6. What would change under different constraints?
7. Which parts are language guarantees and which are CPython-specific?

## 14. Authoritative sources

List only sources actually used for important claims, APIs, compatibility, or security boundaries.
