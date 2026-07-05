# plan-claude-claude-sprint-r1-bernie-scenario-replay-harness

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-r1-bernie-scenario-replay-harness` |
| Status | pending_plan_review |
| Created | 2026-07-05 11:35 +1000 |
| Source HEAD | `dde0e36` |

## Plan Summary

Test-only backend pytest replay harness for Bernie receptionist scenarios: a version-controlled scenario loader plus pytest driver that runs ordered backend/session turns, asserts structured outcomes/preserved fields/forbidden outcomes, and supports xfail scenarios for known behaviour R2 will fix. Claude owns harness mechanics (R1-A); Antigravity owns corpus content (tests/fixtures/bernie_scenarios/); DeepSeek owns fixture-integrity. Add only 1-2 harness-owned demo fixtures to prove mechanics.

## My Understanding

R1-A backend replay harness only. Reuse tests/conftest.py fixtures (client, db, gp_user, practitioner, patient, schedule) and the deterministic route flow already proven by test_bernie_confirmed_flow_review_harness.py: normalize -> normalized-search -> selection -> confirm-bernie. Encode the known clarification merge bug as an xfail scenario; do NOT fix it (that is R2). Do not author the full corpus.

## Intended Surface / Boundary

Test-only. New package tests/bernie_scenarios/. No Diary frontend/UI, no docs/diary/*, no production app/ code, no migrations, no prompt rewrites, no GraphRAG. 'Scenario/turn/corpus/fixture' here mean test data files and a pytest driver, NOT diary grid cards, booking slots, panels, or status UI - none of those adjacent surfaces change.

## Out Of Scope

Diary UI, broad prompt rewrite, GraphRAG, production PHI/log ingestion, auto-mode, unconfirmed writes, fixing the clarification merge bug (R2), owning the full scenario corpus beyond 1-2 harness-owned demo fixtures, any app/ production code, migrations, live-provider interpret scenarios.

## Files I Expect To Edit

tests/bernie_scenarios/__init__.py (new); tests/bernie_scenarios/loader.py (new: scenario dataclass + JSON loader + schema validation); tests/bernie_scenarios/replay.py (new: turn executor mapping action->backend endpoint, forbidden-AI-provider guard, row-count/forbidden-outcome tracking); tests/bernie_scenarios/test_scenario_replay.py (new: parametrized pytest, xfail support, outcome/preserved/forbidden assertions, compact evidence); tests/bernie_scenarios/fixtures/*.json (new: 1 passing + 1 xfail demo scenario); tests/bernie_scenarios/README.md (new: schema reference + authorship boundary). All test-only, no production code.

## Implementation Steps

1) Reuse conftest fixtures and deterministic route helpers (normalize/search/select/confirm URLs + auth). 2) loader.py: dataclass + strict JSON schema validation (required keys, unique ids, known categories/actions); discover from harness fixtures/ and, when present, the Antigravity corpus dir tests/fixtures/bernie_scenarios/, tolerating that dir being absent/empty so lanes integrate independently. Schema fields: id, category, reference_date, initial_state (controlled vocabulary: named conftest fixtures + optional simple pre-seeded appointments, no free-form PHI), turns (ordered; each action in normalize|search|select|confirm|interpret, input, expect), expected, preserved_fields (dotted paths asserted equal/immutable across turns e.g. reference-date immutability), forbidden_outcomes (appointment_written, audit_written, provider_called, forbidden block/state codes), optional xfail:{reason}. 3) replay.py: install forbidden-AI-provider guard by default; execute turns; interpret turns use only the existing disabled/fake provider seam (never live); track Appointment/AppointmentAuditLog row deltas to enforce forbidden_outcomes; capture per-turn JSON for expect/preserved_fields. 4) test_scenario_replay.py: parametrize with pytest id = scenario id; apply pytest.param(marks=xfail(reason)); assert final expected + preserved fields + forbidden outcomes; print compact PASS/XFAIL evidence. 5) Add 1 passing demo (deterministic normalize->confirm happy path) and 1 xfail demo (known clarification/merge behaviour, reason references R2). 6) README.md documents schema + Antigravity authorship boundary.

## Visual / Behavioural Acceptance Checks

py_compile clean on all new files; git diff --check clean; pytest tests/bernie_scenarios -q loads fixtures deterministically, >=1 scenario passes, the xfail scenario reports xfailed (not error), forbidden-outcome/preserved-field assertions demonstrably fire on a deliberately broken local scenario during dev; adjacent existing Bernie tests untouched and still pass (test_bernie_confirmed_flow_review_harness.py); no app/, docs/diary/, or migrations touched.

## Risks / Ambiguities

Corpus-dir coupling: harness must not hard-fail if Antigravity tests/fixtures/bernie_scenarios/ has not landed - mitigated by tolerant discovery. Interpret turns need a provider: R1 restricts them to the disabled/fake seam; live-provider scenarios are out of scope/xfail. Schema drift across R1-B/R1-C: schema is the shared contract, kept minimal + documented; Codex may want to ratify field names before corpus authoring. initial_state scope creep constrained to a controlled vocabulary to avoid arbitrary DB/PHI construction.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
