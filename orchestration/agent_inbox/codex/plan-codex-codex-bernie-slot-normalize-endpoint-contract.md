# plan-codex-codex-bernie-slot-normalize-endpoint-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | codex/bernie-slot-normalize-endpoint |
| Branch | `codex/bernie-slot-normalize-endpoint` |
| Source Task | `codex-bernie-slot-normalize-endpoint-contract` |
| Status | pending_plan_review |
| Created | 2026-06-26 22:20 +1000 |
| Source HEAD | `6b15b84` |

## Plan Summary

Plan deterministic non-mutating backend normalization endpoint contract

## My Understanding

Add only a backend normalization contract after approval: accept SlotSearchCommandIn, call normalize_slot_search_command with an explicit deterministic reference date, and return SlotSearchCommandResult without executing search, LLM, audit, appointment, or database mutations.

## Intended Surface / Boundary

Backend API/route-helper surface only. No diary grid, waiting room, booking slot UI, taskpane, Command Centre, appointment status, cards, panels, or visible frontend surfaces change.

## Out Of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous tool execution, appointment creation, slot-search execution beyond normalizer invocation, audit mutation, SMS, billing, patient demographics, resource admin, migrations unless strictly unavoidable, and DB-backed name-to-UUID resolution.

## Files I Expect To Edit

Likely app/routers or route-helper file that already owns Bernie/appointment proposal endpoints; existing schemas/services defining SlotSearchCommandIn, SlotSearchCommandResult, SlotSearchProposalIn, and normalize_slot_search_command; focused backend tests for the new endpoint/route helper. No frontend or migration files expected.

## Implementation Steps

1. Locate existing Sprint 38/39 slot proposal and command normalizer schemas/tests. 2. Choose the narrowest existing backend router/helper location and route name consistent with nearby Bernie proposal routes. 3. Add a non-mutating authenticated endpoint/helper that validates SlotSearchCommandIn. 4. Derive/reference an explicit deterministic reference date rather than relying on wall-clock defaults. 5. Invoke only normalize_slot_search_command and return SlotSearchCommandResult. 6. Add focused tests for auth, response shape, invalid input, non-mutation/no DB writes, no LLM/search execution, and SlotSearchProposalIn compatibility. 7. Run py_compile, focused pytest, adjacent normalizer/proposal tests, no-mutation proof, and git diff --check.

## Visual / Behavioural Acceptance Checks

Endpoint requires auth, returns SlotSearchCommandResult shape, rejects invalid input predictably, is deterministic for reference date handling, does not create or update appointments/audit/database rows, does not call LLM/search execution, remains compatible with SlotSearchProposalIn, and leaves all UI behavior unchanged.

## Risks / Ambiguities

Main ambiguity is exact route placement/name; I will follow existing Bernie proposal routing conventions and keep the implementation as a thin adapter. If deterministic reference date semantics are already encoded in the normalizer, I will make the endpoint pass that explicitly rather than changing normalizer behavior. Any DB dependency must be read/auth-only and tests must prove no writes.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
