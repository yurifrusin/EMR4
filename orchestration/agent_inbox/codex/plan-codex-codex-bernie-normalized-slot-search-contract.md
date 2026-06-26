# plan-codex-codex-bernie-normalized-slot-search-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | codex/bernie-normalized-slot-search |
| Branch | `codex/bernie-normalized-slot-search` |
| Source Task | `codex-bernie-normalized-slot-search-contract` |
| Status | integrated |
| Created | 2026-06-26 23:05 +1000 |
| Source HEAD | `508a7f7` |

## Plan Summary

Plan backend-only normalized slot-search execution contract

## My Understanding

After approval, add a backend-only non-mutating contract that accepts SlotSearchCommandIn with an explicit reference_date, normalizes deterministically, and only if the result is safe executes the existing /proposals/slot-search proposal logic to return candidate slots with normalization context. Unsafe normalization must return the blocking context without running slot search. This is a worker plan only; no production code changes in the plan gate.

## Intended Surface / Boundary

Backend API/route-helper surface in appointments only. The affected surface is the appointment proposal/slot-search contract, not the diary grid, cards, panels, waiting room, taskpane, Command Centre, or any visual booking surface. Adjacent proposal routes must retain current auth, response, no-mutation, and scheduling behaviour.

## Out Of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing or invocation, autonomous tool execution, appointment create/edit/status/cancel, audit mutation, SMS, billing, patient demographics, resource admin, migrations unless strictly unavoidable, DB-backed name-to-UUID resolution, broad scheduling redesign, master/handoff push, and any frontend asset changes.

## Files I Expect To Edit

Expected after approval: app/routers/appointments.py for a thin endpoint/helper and possible extraction/reuse of propose_slot_search without duplicating rules; app/schemas/appointments.py only if a small response wrapper schema is needed for normalization context plus proposal output; app/services/bernie_slot_normalizer.py only if reference-date/result metadata needs a backwards-compatible helper adjustment; focused tests such as tests/test_slot_search_normalized_execution.py plus existing tests/test_bernie_slot_normalizer.py, tests/test_slot_search_normalize_endpoint.py, and tests/test_slot_search_proposal.py. During plan gate: only coordination packet/status files.

## Implementation Steps

1. Confirm current normalize endpoint and slot-search proposal route contracts and test coverage. 2. Choose the narrowest route name/helper shape that preserves existing /proposals/slot-search and /proposals/slot-search/normalize behaviour. 3. Add an authenticated endpoint/helper accepting SlotSearchCommandIn plus required Query reference_date. 4. Call normalize_slot_search_command with that explicit reference_date and return immediately with blocks when safe is false. 5. When safe is true, pass the normalized SlotSearchProposalIn constraint into the existing non-mutating proposal path/shared helper so scheduling/auth/scope/conflict rules remain single-sourced. 6. Return candidate slots plus normalization context in a typed response without appointment or audit writes. 7. Add focused tests for auth, missing reference_date, safe execution shape, unsafe no-search short-circuit, compatibility with SlotSearchProposalIn/Out, no appointment/audit mutation, no LLM call, and no duplicated scheduling divergence.

## Visual / Behavioural Acceptance Checks

Plan gate acceptance: this packet names Role codex-worker, Worker Name Cicero, Worker Branch codex/bernie-normalized-slot-search, and keeps scope backend-only/non-mutating. Implementation acceptance after approval: unsafe normalization does not execute slot search; safe normalization reuses existing proposal logic; explicit reference_date is required and deterministic; response includes normalization context plus candidates; existing normalize-only and slot-search proposal endpoints keep compatibility; no frontend/visual behaviour changes; no appointment/audit writes or LLM calls. Verification after approval: py_compile touched backend modules/tests; focused pytest for new endpoint/helper; tests/test_bernie_slot_normalizer.py; tests/test_slot_search_normalize_endpoint.py; tests/test_slot_search_proposal.py if router/schema shared code changes; explicit no-mutation/no-LLM proof; git diff --check.

## Risks / Ambiguities

Main design risk is accidentally duplicating propose_slot_search logic or calling the FastAPI route function in a way that obscures dependencies; I will prefer extracting a small internal helper if needed while preserving the existing route contract. Response schema naming/route naming is an Ariadne integration choice, so I will keep it minimal and adjacent to existing proposal schemas. Authentication roles should match nearby slot-search endpoints. If safe execution requires broad router refactor or migrations, I will stop rather than expand scope.

## Codex Plan Review

- Review result:
- Required changes before implementation: none; plan accepted as backend-only, non-mutating, and correctly plan-gated.
- Approved to proceed: yes; implementation integrated in Sprint 41.
