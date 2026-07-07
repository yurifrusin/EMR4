# plan-claude-claude-sprint153-diary-create-proposal-header-readiness

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint153-diary-create-proposal-header-readiness` |
| Status | pending_plan_review |
| Created | 2026-07-07 13:56 +1000 |
| Source HEAD | `82ae0106` |

## Plan Summary

Plan/review to make the live (non-smoke) diary create-proposal caller send an 8+ character Idempotency-Key header, closing the Sprint 152 client-readiness gap, WITHOUT changing create-proposal runtime enforcement (stays non-blank-only), OpenAPI, confirmation-ledger semantics, or any diary visual surface.

## My Understanding

Sprint 152 decided to DEFER runtime OpenAPI minLength:8 enforcement on POST /api/v1/appointments/proposals/create and keep non-blank-only compatibility with guard tests. Backend _normalize_create_proposal_idempotency_key (app/routers/appointments.py:1041) raises a typed 400 idempotency_key_required when the Idempotency-Key header is blank/missing; the OpenAPI parameter declares minLength 8 / maxLength 128 / required, but runtime only enforces non-blank. The live diary booking modal caller (docs/diary/diary.js:7389-7395) POSTs /appointments/proposals/create (and /proposals/update/{id}) via apiFetch with NO Idempotency-Key header, so a live non-smoke create booking currently 400s before the visual save flow. apiFetch (diary.js:2417) forwards opts.headers alongside Content-Type/ngrok-skip/Authorization. bernieSession.generateEventId() (diary.js:174) returns crypto.randomUUID() (36 chars) or an evt-... fallback (>8 chars), either of which satisfies both the non-blank bar and the deferred minLength 8. propose_update_appointment (appointments.py:1503) takes NO Idempotency-Key param, so a header on the shared caller is required for create and harmlessly ignored for update. The natural fix is a client-only change: have the create-proposal request send an 8+ char Idempotency-Key.

## Intended Surface / Boundary

docs/diary/diary.js booking-modal save flow, network-header only: the /appointments/proposals/create POST at diary.js:7389-7395 (the create branch of needsProposal), plus a small local idempotency-key generator and a diary asset cache-bust bump. NOTHING visual changes: diary grid, booking-slot cards, appointment stacking/lanes, status colours, waiting-room feed, and the booking modal layout all stay exactly as-is. This is a request-header change inside an existing flow, not a UI change.

## Out Of Scope

Do NOT add runtime minLength enforcement (create-proposal stays non-blank-only). Do NOT change the OpenAPI header shape/schema. Do NOT alter confirmation idempotency-ledger semantics, the staff/Bernie confirm routes, or freshness-id logic. Do NOT touch raw compatibility routes, PUT/{id} write routes, providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, or historical diary trove material. Do NOT change the update-proposal contract. No new backend route params. No diary visual/DOM/card/slot/status changes.

## Files I Expect To Edit

docs/diary/diary.js — add an 8+ char Idempotency-Key header to the create-proposal POST (create branch only, so update stays untouched), add a tiny crypto.randomUUID-with-fallback key generator (avoid hard dependency on bernieSession being initialised in the plain booking path), and bump the diary ?v=N cache-bust. Optionally a structural/static assertion under review/ (e.g. review/test_diary_smoke.py or a node/regex check) proving the create-proposal call attaches an >=8 char Idempotency-Key, since smoke mode uses simulateProposal and never hits the endpoint. No edits to app/, OpenAPI YAML, migrations, backend runtime, or providers.

## Implementation Steps

1. In docs/diary/diary.js, add a small helper generateProposalIdempotencyKey() returning crypto.randomUUID() with an evt-<rand>-<ts> fallback (both >=8 chars). 2. In the booking-modal save flow, build a headers object only on the CREATE branch: { "Idempotency-Key": generateProposalIdempotencyKey() }; pass it via apiFetch(url, { method: "POST", headers, body }). Leave the update-proposal branch header-free (route ignores it) to keep the change tightly scoped. 3. Confirm apiFetch merges opts.headers (it does) so Authorization/Content-Type are preserved. 4. Bump the diary asset ?v=N cache-bust per the diary deploy discipline. 5. Add a structural review check that the create-proposal request carries an Idempotency-Key of length >=8. 6. Run the verification commands and record results in the packet before submit.

## Visual / Behavioural Acceptance Checks

(a) A live non-smoke diary CREATE booking sends an Idempotency-Key header of >=8 chars and the backend returns a create proposal instead of 400 idempotency_key_required. (b) Backend runtime still accepts any non-blank key — no minLength enforcement added — and the OpenAPI parameter is unchanged (guard tests test_api_spine_create_proposal_header_alignment.py + test_api_spine_create_proposal_idempotency_route_contract.py still pass, including the short-non-blank-key-accepted case). (c) No write/replay authority change: create-proposal remains a non-mutating deterministic re-evaluation with no ledger entry; sending different keys across attempts changes nothing server-side. (d) Update-proposal behaviour is unchanged. (e) Diary grid, booking-slot cards, status colours, waiting-room, and modal layout are visually identical. (f) node --check docs/diary/diary.js passes and review/test_diary_smoke.py stays green.

## Risks / Ambiguities

(1) bernieSession may not be initialised in the plain booking-modal path, so prefer a standalone crypto.randomUUID generator over bernieSession.generateEventId() to avoid a runtime error. (2) The create/update proposal caller is shared (diary.js:7389-7395); scoping the header to the create branch avoids any behavioural change to update, which takes no Idempotency-Key param. (3) Smoke mode (simulateProposal) never exercises the endpoint, so header coverage needs a structural/static check rather than the existing smoke path. (4) The OpenAPI-vs-runtime split (minLength 8 declared, non-blank enforced) persists by design; the Sprint 152 guard tests lock it and the x-emr4 posture annotation documents it — this sprint deliberately does not resolve that split. (5) If Ariadne later wants minLength enforced at runtime, this client change is the enabling precondition (client now sends a UUID key that already satisfies minLength 8), and enforcement can follow in a separate sprint. (6) Verification note: no tests run during this plan gate; Ariadne should run node --check, the two API-spine guard test files, and the diary smoke harness before/after implementation.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
