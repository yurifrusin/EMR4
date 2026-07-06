# plan-codex-codex-sprint-r1-deepseek-scenario-integrity

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-r1-deepseek-scenario-integrity` |
| Source Task | `codex-sprint-r1-deepseek-scenario-integrity` |
| Status | integrated |
| Created | 2026-07-05 11:43 +1000 |
| Source HEAD | `dde0e36` |

## Plan Summary

DeepSeek Flash scenario integrity validator plan

## My Understanding

DeepSeek Flash will provide a bounded fixture integrity lane for Sprint R1. Claude owns the backend replay harness, Antigravity/Gemini owns receptionist scenario authorship, and this lane validates scenario fixture structure without owning scenario meaning or fixing clarification semantics.

## Intended Surface / Boundary

Test-only fixture integrity surface: tests/test_bernie_scenario_integrity.py and optionally tests/fixtures/bernie_scenarios/README.md. Nearby surfaces that must not change: app/, docs/diary/, scripts/, existing tests/test_bernie_*.py, migrations, and orchestration protocol docs.

## Out Of Scope

No backend replay harness, no scenario corpus authorship, no production code, no Diary UI, no GraphRAG, no production logs or PHI, no auto-mode, no prompt rewrites, no implementation of clarification merge semantics, and no deletion or rewriting of existing tests.

## Files I Expect To Edit

tests/test_bernie_scenario_integrity.py; tests/fixtures/bernie_scenarios/README.md only if useful for fixture authoring guidance.

## Implementation Steps

Create a lightweight pytest validator for tests/fixtures/bernie_scenarios/. Validate YAML parseability, unique ids, required fields, known categories, turn expectation shape, xfail reason metadata, forbidden-list shape, and graceful empty-directory behaviour. Keep optional fields lenient so Antigravity's domain intent is not silently rewritten. Report ambiguity as review notes.

## Visual / Behavioural Acceptance Checks

Focused pytest for tests/test_bernie_scenario_integrity.py passes with an empty fixture directory and with well-formed scenarios, fails clearly for malformed fixtures during dev, py_compile passes, git diff --check passes, and git diff --stat shows only the new validator/optional README.

## Risks / Ambiguities

Schema drift between Claude harness and Antigravity corpus is the main risk. The validator should keep required fields strict but optional fields lenient. Bridge/CLI worker sandbox could not commit directly because git metadata sits outside the disposable worktree; Ariadne converted this DeepSeek Flash output into the official plan packet.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
