# review-claude-claude-sprint-r1-bernie-scenario-replay-harness

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-r1-bernie-scenario-replay-harness` |
| Status | queued |

## Review Request

claude-sprint-r1-bernie-scenario-replay-harness ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - NEW tests/bernie_scenarios/__init__.py — package marker
  - NEW tests/bernie_scenarios/loader.py — YAML loader, Scenario dataclasses, schema validation (required fields, known actions/forbidden-outcomes, duplicate-id check, tolerant discovery for missing corpus dir)
  - NEW tests/bernie_scenarios/replay.py — ReplayContext turn executor (normalize/search/select/confirm dispatch), {var} template resolution, forbidden-AI-provider monkeypatch guard, row-count outcome checks, preserved-field drift detection, ReplayResult evidence/failures
  - NEW tests/bernie_scenarios/test_scenario_replay.py — parametrized pytest, xfail marks applied at collection time from YAML, compact PASS/FAIL evidence output
  - NEW tests/bernie_scenarios/README.md — schema reference, state-threading rules, authorship boundary table
  - NEW tests/fixtures/bernie_scenarios/harness_demo_happy_path.yaml — 1 passing demo: normalize->search->select->confirm, appointment_written+audit_written=True, provider_called forbidden
  - NEW tests/fixtures/bernie_scenarios/harness_demo_clarification_merge_xfail.yaml — 1 xfail demo: asserts constraint.time_of_day="afternoon" (field does not exist in current normalize output); xfail reason references Sprint R2 clarification merge semantics
  - No app/, docs/diary/, migrations, taskpane, or Antigravity-owned corpus files touched

- Verification run:
  - py_compile tests/bernie_scenarios/loader.py replay.py test_scenario_replay.py — OK
  - git diff --check — OK
  - pytest tests/bernie_scenarios/ -v — 1 passed (harness-demo-happy-path), 1 xfailed (harness-demo-clarification-merge-xfail)
  - Pre-existing failure confirmed: test_bernie_confirmed_flow_review_harness.py::test_confirmed_bernie_flow_writes_only_at_explicit_successful_confirmation was already failing before this branch (audit_evidence mismatch: legacy_unsigned_confirmation_compat vs expected); not caused by R1 changes
  - Existing slot flow harness: 7 passed
  - YAML amendment applied: corpus dir is tests/fixtures/bernie_scenarios/ (YAML-only), no JSON demo fixtures created

- Remaining risks:
  - If Antigravity corpus YAML files use schema fields not validated by loader.py (e.g. nested initial_state seeding, non-standard categories), they will be loaded without error but the fields will be silently ignored. Schema is intentionally minimal for R1; Codex may want to ratify before Antigravity authors the corpus (R1-B).
  - The test function always requests all standard conftest fixtures (practice, practitioner, gp_user, patient, schedule). Scenarios that need a different patient or additional appointments must rely on R2 initial_state seeding extensions.
  - The pre-existing test_bernie_confirmed_flow_review_harness audit_evidence failure is not resolved here (out of R1 scope).

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint-r1-bernie-scenario-replay-harness.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
