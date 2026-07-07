# DeepSeek Sprint 162 Review - Interpret Replay Harness

## Scope

DeepSeek performed a read-only adversarial review of the Sprint 162 working-tree
changes:

- `tests/bernie_scenarios/loader.py`
- `tests/bernie_scenarios/replay.py`
- `tests/bernie_scenarios/README.md`
- `tests/fixtures/bernie_scenarios/README.md`
- `tests/fixtures/bernie_scenarios/interpret_*.yaml`

## Findings Accepted

### Critical - Fixed

DeepSeek found that `tests/test_bernie_scenario_integrity.py` had a stale
`KNOWN_ACTIONS` allowlist missing `interpret`. Codex added `interpret` to that
allowlist and added the new `booking_interpret_contract` fixture category to the
same validator.

### High - Fixed Or Documented

- `preserved_fields` was undocumented. Codex documented it in both scenario
  READMEs.
- `preserved_fields` skipped missing values after a field had already been
  snapshotted. Codex changed replay so a snapshotted preserved field fails if it
  later disappears.
- First-turn interpret auto-threading was implicit. Codex added a comment
  explaining that the first interpret turn intentionally starts with empty
  context frames.

### Medium - Fixed Or Deferred

- `interpret_change_time_new_reply_wins.yaml` under-asserted its first turn.
  Codex added patient, practitioner, date, and duration assertions.
- `interpret_context_practitioner_change.yaml` overstated external context
  seeding. Codex clarified the description.
- Additional suggested fixtures such as empty instruction, unknown practitioner,
  cross-turn reference-date drift, incomplete context frames, and red-team
  preserved-field behavior are useful follow-up candidates, but are not required
  for the first Fable-directed prompt-thread slice.

## Verdict

DeepSeek's blocking finding was addressed, and the remaining accepted fixes were
integrated. The implemented harness remains fake-provider, route-level,
no-write contract coverage and does not open provider, memory/RAG/GraphRAG,
H15/H-series runtime, or historical diary trove gates.

