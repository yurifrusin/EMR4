# plan-codex-codex-bernie-interpret-booking-instruction

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-interpret-booking-instruction` |
| Branch | `codex/bernie-interpret-booking-instruction` |
| Source Task | `codex-bernie-interpret-booking-instruction` |
| Status | pending_plan_review |
| Created | 2026-06-27 10:32 +1000 |
| Source HEAD | `1008341` |

## Plan Summary

Sprint 63 Cicero plan: read-only Bernie booking-instruction interpreter boundary

## My Understanding

Role: codex-worker. Worker Name: Cicero. Worker Branch: codex/bernie-interpret-booking-instruction. After approval only, add the first read-only Bernie AI runway slice that accepts staff natural-language booking text and returns validated structured booking intent suitable for the existing deterministic Bernie supervised booking flow. The new slice should introduce a provider boundary with a fake/default provider for tests, keep any live model provider disabled by default, and prove the endpoint performs no appointment writes, audit writes, or live LLM/provider calls in default/test mode.

## Intended Surface / Boundary

Backend-only API/provider boundary for interpreting booking instructions. The affected surface is JSON contract and Python service/router code that turns staff text into structured intent fields such as slot constraints, confidence, missing fields, safety flags, and clarifying question. Visually loaded terms like cards, slots, panels, waiting room, diary grid, booking slot, and status refer only to returned backend data; no diary grid, waiting-room UI, taskpane, Command Centre, cards, panels, or visible status controls change.

## Out Of Scope

No frontend UI, diary/taskpane/Command Centre changes, real appointment/proposal creation, confirmation, audit writes, database writes, migrations, provider credentials, live Gemini/Vertex calls in tests, prompt-tuning beyond a minimal interface, PHI logging, patient/resource admin, SMS, billing, or broad refactors of existing slot-search/selection/confirm contracts.

## Files I Expect To Edit

Expected production files after approval: app/config.py for default-off Bernie interpretation/provider settings; app/schemas/appointments.py for strict request/response intent schemas; likely app/services/bernie_booking_interpreter.py or app/services/ai/bernie_booking_interpreter.py for provider protocol, disabled/fake providers, validation helpers, and redacted/no-logging posture; app/routers/appointments.py for a thin authenticated read-only endpoint under /api/v1/appointments/proposals/bernie or adjacent route. Expected tests: new focused tests/test_bernie_interpret_booking_instruction.py plus adjacent Bernie supervised wrapper/normalized-search tests only if shared code is touched. Coordination-only plan-gate files: source task packet and generated plan packet.

## Implementation Steps

1. Define strict schemas for raw staff instruction input, interpreted booking intent output, parsed slot-search command fields, confidence, missing_fields, safety_flags/blocks/warnings, clarifying_question, and provider metadata that does not expose PHI or prompts. 2. Add config toggles that keep the interpreter disabled or fake-only by default, with live provider unavailable unless explicitly configured later; tests should assert this default-off posture. 3. Implement a small provider boundary/protocol and deterministic fake/default provider that maps constrained non-PHI test phrases into SlotSearchCommandIn-like structured fields and returns blocked/clarifying output for ambiguous or unsafe text. 4. Add a thin authenticated endpoint that validates input, resolves the configured provider, returns structured intent, and does not call slot search, selection, confirm-Bernie, appointment writes, audit writes, network, or live Gemini/Vertex. 5. Keep logging out of the path or limited to non-PHI operational metadata; avoid logging raw staff text. 6. Add deterministic tests for auth, response shape, valid fake interpretation, missing fields/clarifying question, unsafe/default-disabled fallback, no DB/audit writes, no live provider call by default, source-level no mutation/confirm checks, and compatibility of parsed command fields with the existing supervised booking wrapper.

## Visual / Behavioural Acceptance Checks

Plan-gate acceptance now: only coordination packets changed and no production code edited. After approval, the endpoint returns validated structured booking intent from a fake provider in tests, returns safe blocked/clarifying output when disabled/ambiguous, includes confidence/missing_fields/safety_flags/clarifying_question, never creates or confirms appointments, never writes audit rows, never calls live LLM/provider by default, and preserves all existing Bernie normalize/search/selection/supervised/confirm behaviours. Verification after approval: py_compile touched backend files; focused pytest for the interpret endpoint/provider fake; adjacent tests/test_bernie_supervised_booking_wrapper.py, tests/test_slot_search_normalized_execution.py, and tests/test_bernie_wrapper_confirmation_review_harness.py if shared contracts change; no-write/no-audit/no-LLM proof; git diff hygiene.

## Risks / Ambiguities

Main ambiguity is exact response naming and whether the output should be directly SlotSearchCommandIn-compatible or wrapped in a richer intent envelope; I prefer a richer envelope with a nested command candidate so future UI can display confidence/missing fields without coupling to the slot-search schema. Need Ariadne to confirm endpoint placement and whether disabled-default should return 200 blocked intent or 503 unavailable; I prefer 200 with safe=false/blocked for reviewability and deterministic tests. Avoid overfitting fake natural-language parsing; this slice should prove the boundary and validation contract, not real LLM understanding.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
