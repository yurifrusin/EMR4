# plan-claude-claude-sprint108-bernie-access-ai-backend-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/sprint108-bernie-access-ai-backend` |
| Source Task | `claude-sprint108-bernie-access-ai-backend-contract` |
| Status | superseded_by_deepseek_implementation |
| Created | 2026-07-06 23:54 +1000 |
| Source HEAD | `7581696f` |

## Plan Summary

Sprint 108 Bernie Access AI backend contract plan: test-only hardening proving
the live path crosses `AccessAiService` and disabled/fake paths stay local,
no-write, and no-audit.

## My Understanding

Bernie booking-instruction interpretation is already migrated onto
`AccessAiService`. `app/services/bernie_booking_interpreter.py` has three
providers: disabled (default) and fake never construct a provider or append
`audit_events`; `GeminiVertexBookingInstructionInterpreter._generate()` builds
an `AccessAiRequest` with capability `BERNIE_BOOKING_INTERPRET`, method
`INVOKE`, and source surface `DIARY`, then extends the caller's audit events
with `result.audit_events`.

The route `interpret_bernie_booking_instruction` only calls
`persist_access_ai_audit_events` and `db.commit` when `access_ai_audit_events`
is non-empty. `AccessAiAuditEvent` metadata validation already rejects raw,
prompt, transcript, and PHI-like key fragments. Existing tests cover the
disabled no-audit case and the live +1-audit case. This is therefore minimal
hardening: add focused tests for uncovered invariants rather than duplicating a
migration that already exists.

## Intended Surface / Boundary

Test file only: `tests/test_bernie_interpret_booking_instruction.py`.
Verification should also run `tests/test_access_ai_service.py` and
`tests/test_ai_audit_events.py` unchanged. No route, service, schema, model, or
migration edits unless a new test surfaces a genuine defect in the reviewed
audit path, in which case the sprint should stop and flag before touching
production code.

## Out Of Scope

No live provider enablement; no GCP/ADC changes; no autonomous booking writes;
no proposal/confirm route rewrites; no GraphQL mutations; no DB migrations; no
H15/trove; no memory/RAG/GraphRAG; no runtime FGA; no UI/taskpane/diary files.

## Files Expected To Edit

`tests/test_bernie_interpret_booking_instruction.py` only.

## Implementation Steps

1. Add explicit assertion or a dedicated test that fake-mode interpret writes
   zero `AccessAiAuditLog` rows, matching the existing disabled-mode assertion.
2. Strengthen the mocked-live-provider test to assert raw instruction text and
   raw provider-payload strings do not appear in persisted audit metadata values.
3. Keep disabled-mode no-audit assertion explicit and ensure fake
   do-not-call-live-provider also implies no audit rows.
4. Run py_compile on touched Python, then the three verification test modules,
   then `git diff --check`.

## Visual / Behavioural Acceptance Checks

`pytest tests/test_bernie_interpret_booking_instruction.py tests/test_access_ai_service.py tests/test_ai_audit_events.py -q`
passes; new assertions prove fake writes zero `AccessAiAuditLog` rows; live
path writes allowed audit rows via `AccessAiService` with no raw instruction,
prompt, or provider-payload text in metadata. No response-shape or diary UI
change.

## Risks / Ambiguities

If a new test unexpectedly fails, it may indicate a real audit leak or
fake-path audit-write bug; per scope, stop and flag rather than expand into
production code. Instruction-text-absent assertions must tolerate short
interpreter tag strings in metadata; scope them to raw instruction/prompt
content, not arbitrary substrings.

## Codex Plan Review

- Review result: accepted for scope, superseded for implementation by the
  DeepSeek Flash backend-hardening lane to avoid same-file overlap.
- Required changes before implementation: none; accepted gaps were covered by
  Ariadne-reviewed DeepSeek test additions.
- Approved to proceed: no separate Claude implementation required.
