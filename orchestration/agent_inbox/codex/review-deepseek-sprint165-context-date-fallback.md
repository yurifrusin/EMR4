# DeepSeek Sprint 165 Review - Context Date Fallback

## Scope

Read-only review of Sprint 165 context-date fallback changes:

- `tests/fixtures/bernie_scenarios/interpret_context_date_missing_no_context.yaml`
- `tests/fixtures/bernie_scenarios/README.md`
- `orchestration/agent_inbox/claude/claude-sprint165-context-date-fallback.md`
- `orchestration/agent_inbox/antigravity/antigravity-sprint165-context-date-fallback.md`

## Verdict

Pass. The fixture correctly proves the no-context omitted-date fallback:
`date.ask_missing_context` leads to `clarification_required`,
`command_candidate.date_from` remains null, `missing_fields` contains
`date_from`, and no provider, write, memory, H15/H-series, or historical trove
gates are opened.

## Findings

- Blocking: none.
- High observation: both the date transition table and the route fallback can
  produce the same "Which day would you like me to check?" copy. This is not a
  bug, but future copy changes should keep both paths aligned.
- Medium deferred: this single-turn fixture uses explicit `context_frames: []`.
  A future multi-turn fixture should lock the difference between omitted
  `context_frames` auto-threading and explicit empty context.
- Low: explicit `appointment_written: false` and `audit_written: false` are
  redundant with loader defaults but helpful and should remain.

## Deferred Suggestions

- Add a multi-turn fixture for auto-threaded prior context vs explicit
  `context_frames: []`.
- Add a multi-field missing fixture where practitioner and date are both absent.
- Keep clarifying-question wording aligned between the transition table and
  route fallback if copy changes later.

