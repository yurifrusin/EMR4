# DeepSeek Sprint 166 Review - Context Threading

## Scope

Read-only review of Sprint 166 context-threading changes:

- `tests/fixtures/bernie_scenarios/interpret_context_frames_auto_thread_vs_empty.yaml`
- `tests/fixtures/bernie_scenarios/README.md`
- `orchestration/agent_inbox/claude/claude-sprint166-context-threading.md`
- `orchestration/agent_inbox/antigravity/antigravity-sprint166-context-threading.md`

## Verdict

Accept. The fixture correctly proves both harness branches:

- omitted `context_frames` auto-threads prior `requested_appointment` context;
- explicit `context_frames: []` clears that thread and re-clarifies.

The fixture remains fake-provider, route-level, and no-write. It does not open
provider/live backend, H15/H-series, historical trove, memory, RAG, GraphRAG, or
write gates.

## Findings

- Low: turn 3 asserts `missing_fields.0` and `missing_fields.1`, which depends
  on current route emission order. This matches current behavior and is
  non-blocking.
- Low: DeepSeek suggested a future `preserved_fields` guard for duration, but
  the current fixture already explicitly asserts `command_candidate.duration_minutes`
  on turn 2 and deliberately clears context on turn 3, so no change was made.
- Trivial: `safe: false` on `clarification_required` follows existing route
  convention.

## Deferred Suggestions

- Add a future partial-context override fixture, such as changing only the
  practitioner while preserving patient/date/time/duration.
- Add a future temporal-drift threading fixture.
- Consider unordered missing-field assertions only if the scenario harness gains
  support for unordered field checks.

