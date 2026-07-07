# plan-claude-claude-sprint152-create-proposal-minlength-readiness

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint152-create-proposal-minlength-readiness` |
| Status | pending_plan_review |
| Created | 2026-07-07 13:41 +1000 |
| Source HEAD | `8d711a8d` |

## Plan Summary

Sprint 152 API-spine readiness review: keep create-proposal Idempotency-Key non-blank-only at runtime; DEFER OpenAPI minLength 8 enforcement until intended clients actually send a valid header, and keep the guard tests that lock the deferred posture.

## My Understanding

POST /api/v1/appointments/proposals/create is a non-mutating proposal route using deterministic re-evaluation: no proposal ledger, no stored envelope replay, no appointment/audit writes, no slot reservation (Sprint 149 decision). Sprint 150 wired syntactic enforcement only: missing or blank Idempotency-Key returns 400 idempotency_key_required. Sprint 151 recorded a split contract: OpenAPI marks Idempotency-Key required with minLength 8 and maxLength 128 plus x-emr4-proposal-header-posture.runtime_validation=non_blank_only, while FastAPI enforces non-blank only. A one-char key currently returns 200 (test_short_nonblank_key_is_accepted_until_minlength_client_readiness_decision). Sprint 152 decides: enforce minLength 8 at runtime now, or keep compatibility and preflight the next proposal-only surface.

## Intended Surface / Boundary

API-spine / replay-semantics readiness lane only for the create-proposal REST route (app/routers/appointments.py propose_create_appointment and _normalize_create_proposal_idempotency_key) and its OpenAPI header contract. No diary grid, booking-slot card, waiting-room, or status UI behavior changes. No confirmation-ledger or raw-compat route changes. Antigravity owns the client-compatibility lane; Codex/DeepSeek owns the adversarial lane.

## Out Of Scope

No production code or test edits during this plan gate. No minLength wiring, no OpenAPI header-shape change, no confirmation idempotency ledger changes, no raw compatibility route changes, no update/status/delete/waiting-area enforcement, no providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, or historical diary trove access. No diary UI or taskpane edits.

## Files I Expect To Edit

Plan gate now: only orchestration plan/review packets. If a later sprint is approved to implement the recommended deferral: a decision doc orchestration/api_spine_appointment_idempotency_create_proposal_minlength_readiness.md and a guard assertion in tests/test_api_spine_create_proposal_header_alignment.py (or a sibling). No app/ or migration edits under the recommended deferral.

## Implementation Steps

1. RECOMMENDATION: keep runtime non-blank-only; DEFER OpenAPI minLength 8 enforcement this sprint. 2. Rationale A (client-readiness not met): the primary human client, the diary booking modal at docs/diary/diary.js line 7392, posts to /appointments/proposals/create via apiFetch with NO Idempotency-Key header; apiFetch (diary.js line 2417) injects only Content-Type, ngrok-skip, and Authorization. Per the Sprint 149 replay-model definition, client readiness means all intended clients can send a non-blank header. That bar is not yet met, so a stricter minLength bar is premature. 3. Rationale B (low value on this route): create-proposal is deterministic re-evaluation with no ledger and no replay authority, so short keys cause no same-key/different-body correctness harm today; minLength 8 adds negligible safety while adding client-break risk. 4. Rationale C (error-contract consistency): enforcing via FastAPI Header(min_length=8) would emit a 422 validation error, inconsistent with the typed 400 idempotency_key_required used for missing/blank; if enforced later it should be an explicit typed check returning a typed code, not raw 422. 5. GUARDRAIL: keep the existing header-alignment guard and test_short_nonblank_key_is_accepted... contract test that lock the deferred posture so the OpenAPI/runtime split stays intentional and documented. 6. NEXT proposal-only preflight: lowest-risk continuation is update/status proposal-only header discipline (they do not yet require the header per gates-closed), not rolling the shared header across raw-compat writes. 7. CROSS-LANE HANDOFF: flag to Antigravity/Ariadne that the diary create-proposal client sends NO Idempotency-Key; closing that (client sends a key of 8+ chars, e.g. reuse generateEventId) fixes non-blank readiness AND satisfies minLength 8 automatically, which is the natural trigger to later enforce minLength.

## Visual / Behavioural Acceptance Checks

No runtime behavior change this sprint: a one-char non-blank key still returns 200 with a fresh proposal envelope and zero AppointmentCommandIdempotency rows; missing/blank still returns 400 idempotency_key_required; OpenAPI still documents minLength 8 with the non_blank_only posture annotation; guard tests remain green. Ariadne can pick either verdict from the packet: enforce-now (only after the diary client sends a valid 8+ char key, with regression tests) or defer-with-guard (recommended).

## Risks / Ambiguities

1. If live diary booking already reaches the real endpoint in non-smoke mode it may ALREADY be failing the Sprint 150 non-blank 400 because it sends no header; this is a pre-existing client gap independent of minLength and should be confirmed by the client-compatibility lane. 2. Deferring keeps an OpenAPI-vs-runtime split that could confuse SDK generators; mitigated by the x-emr4-proposal-header-posture annotation and guard test. 3. Recommendation depends on the route staying deterministic (no ledger); revisit if a proposal marker is ever added. 4. No tests were run during the plan gate; before any change Ariadne should run pytest for tests/test_api_spine_create_proposal_header_alignment.py, tests/test_api_spine_create_proposal_idempotency_route_contract.py, and tests/test_appointment_proposals.py to confirm the current posture.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
