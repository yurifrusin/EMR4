# plan-antigravity-antigravity-sprint-r1-reception-scenario-corpus

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-r1-reception-scenario-corpus` |
| Status | integrated |
| Created | 2026-07-05 11:34 +1000 |
| Source HEAD | `dde0e36` |

## Plan Summary

Scenario corpus foundation containing 9 structured receptionist scenarios under tests/fixtures/bernie_scenarios/

## My Understanding

Define the first 9 scenarios in YAML format under tests/fixtures/bernie_scenarios/ using the compact schema. These scenarios model receptionist multi-turn conversations, preserving state across turns, stating expected outcomes, preserved facts, forbidden behaviors, and flagging known bugs with xfail.

## Intended Surface / Boundary

YAML scenario files under tests/fixtures/bernie_scenarios/ and README.md. No production code or tests will be modified.

## Out Of Scope

No backend replay harness code. No production app logic or UI changes. No GraphRAG or prompt changes.

## Files I Expect To Edit

tests/fixtures/bernie_scenarios/*.yaml, tests/fixtures/bernie_scenarios/README.md

## Implementation Steps

1. Create tests/fixtures/bernie_scenarios/ directory. 2. Author 9 YAML scenarios mapping receptionist interactions. 3. Document the schema in README.md. 4. Run parse check to verify YAML validity.

## Visual / Behavioural Acceptance Checks

YAML files are valid, parse successfully, and no code is modified.

## Risks / Ambiguities

Risk of schema drift. Mitigation: align fields and outcome names precisely with existing test code.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
