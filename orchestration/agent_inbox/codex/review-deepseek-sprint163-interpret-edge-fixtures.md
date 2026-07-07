# DeepSeek Sprint 163 Review - Interpret Edge Fixtures

## Scope

Read-only review of the Sprint 163 fixture slice:

- `tests/fixtures/bernie_scenarios/interpret_empty_instruction_fail_closed.yaml`
- `tests/fixtures/bernie_scenarios/interpret_unknown_patient_name_without_id.yaml`
- `tests/fixtures/bernie_scenarios/interpret_visible_diary_date_context.yaml`
- `tests/fixtures/bernie_scenarios/interpret_turn_reference_date_drift.yaml`
- `tests/fixtures/bernie_scenarios/README.md`
- `orchestration/agent_inbox/antigravity/antigravity-sprint163-interpret-edge-fixtures.md`

Claude was unavailable due to session limits, so this replacement DeepSeek lane
covered the final post-polish pass.

## Verdict

Safe to commit after one consistency polish. The fixtures remain fake-provider,
route-level contract tests and do not open provider/live backend, H15/H-series,
historical trove, memory, RAG, GraphRAG, or write gates.

## Findings

- Medium: `interpret_turn_reference_date_drift.yaml` and
  `interpret_visible_diary_date_context.yaml` omitted explicit
  `provider_metadata.provider: fake` and `provider_metadata.live_provider:
  false` assertions, while other 200-response interpret fixtures include them.
  This was a consistency gap, not a gate breach, because `provider_called` was
  still forbidden.

## Codex Follow-Up

- Accepted. Added explicit fake-provider metadata assertions to both turns in
  `interpret_turn_reference_date_drift.yaml` and to
  `interpret_visible_diary_date_context.yaml`.
- Earlier DeepSeek/Antigravity naming feedback was also accepted: the unknown
  patient fixture was renamed from the uncommitted
  `interpret_unknown_patient_name_clarifies.yaml` draft to
  `interpret_unknown_patient_name_without_id.yaml`, with description wording
  changed to "slot-search command candidate" and "unknown sentinel patient
  name."

## Deferred Suggestions

- Add a future fixture for multi-frame date-context precedence.
- Add a future fixture for large reference-date drift.

