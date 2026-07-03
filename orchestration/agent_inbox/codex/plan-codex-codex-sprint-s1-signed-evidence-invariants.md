# plan-codex-codex-sprint-s1-signed-evidence-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Codex S1 signed evidence invariants |
| Worker Branch | `codex/current` |
| Source Task | `codex-sprint-s1-signed-evidence-invariants` |
| Status | accepted |
| Created | 2026-07-03 |
| Source HEAD | `master` |

## Plan Summary

Plan an adversarial invariant lane for Sprint S1 so Bernie confirmation-grade writes require server-signed evidence and fail closed for missing, tampered, mismatched, stale, replayed, or UI-created authority.

## My Understanding

Sprint S1 should upgrade the current deterministic freshness-id contract into confirmation evidence that is authoritative because the server signed it, not because the browser echoed friendly-looking JSON. Today the backend has useful foundations: deterministic candidate/proposal freshness IDs in `app/services/bernie_turn_evidence.py`, wrapper/confirm endpoints in `app/routers/appointments.py`, fail-closed confirm-affordance logic in `app/services/diary/confirm_gate.py`, persistence-shaped Bernie session/event contracts in `app/services/bernie/session.py`, and review harness coverage in `tests/` and `review/test_diary_smoke.py`. But the freshness IDs are unsalted hashes, staleness evidence remains optional for legacy compatibility, and the UI can still transport unsigned `confirm_payload` fields. S1 needs a narrow invariant plan proving that signed evidence is mandatory on the new signed path and that legacy compatibility is explicit, isolated, audited, and not mistaken for signed confirmation authority.

## Intended Surface / Boundary

Primary eventual implementation surface is backend contract and adversarial tests, not a UI redesign. The likely signed-evidence domain surface is `app/services/bernie/evidence.py` or the legacy implementation file it re-exports, `app/services/bernie_turn_evidence.py`, plus `app/schemas/appointments.py` and the Bernie proposal/confirm routes in `app/routers/appointments.py` where evidence is minted, echoed, and verified. Focused tests should live alongside current suites such as `tests/test_bernie_turn_contract.py`, `tests/test_bernie_confirm_create_proposal.py`, `tests/test_bernie_evidence_contract.py`, `tests/test_diary_confirm_gate.py`, `tests/test_bernie_domain_package.py`, and possibly a new `tests/test_bernie_signed_confirmation_evidence.py`.

The UI surface, if touched by the implementation lane, is only the Bernie review/confirm panel inside `docs/diary/diary.js` and its deterministic smoke harness in `review/test_diary_smoke.py`. The browser must only echo server evidence; it must not mint, alter, infer, or repair confirmation authority. Nearby visual surfaces that must not change: diary grid geometry, appointment cards, booking slot rendering, appointment stacking/overlap, waiting room panels, appointment status controls, create/edit modal layout, taskpane, Command Centre, Resource Administration, and broader Pages deployment mechanics.

## Out Of Scope

No production implementation during this plan gate. For the later S1 implementation, keep out: persisted Bernie session tables/migrations, broad GraphRAG or practice-knowledge route/UI wiring, auto-mode, root-to-branch API-spine redesign, UI redesign, live PHI, autonomous booking, weakening staff confirmation, and any client-only or LLM-created write authority. Do not make retrieval, visible diary copy, DOM state, route-intercept smoke fixtures, or unsigned freshness hashes sufficient for confirmation-grade writes.

## Files I Expect To Edit

After implementation approval, I expect the invariant lane to edit:

- `tests/test_bernie_signed_confirmation_evidence.py` as the preferred new adversarial suite.
- `tests/test_bernie_turn_contract.py` for targeted updates if signed evidence replaces or wraps current freshness-id checks.
- `tests/test_bernie_confirm_create_proposal.py` and `tests/test_bernie_evidence_contract.py` for route-level no-mutation, audit, mismatch, and legacy-compat assertions.
- `tests/test_diary_confirm_gate.py` if the confirm-affordance gate gains a distinct signed-evidence-required mode.
- `tests/test_bernie_domain_package.py` if new evidence helpers are exported through `app.services.bernie`.
- `review/test_diary_smoke.py` only if the UI echo contract changes or needs deterministic confirmation-payload assertions.

Production files expected for the implementation lane, but not touched by this plan packet: `app/services/bernie_turn_evidence.py`, `app/services/bernie/evidence.py`, `app/schemas/appointments.py`, `app/routers/appointments.py`, and possibly `app/config.py` if the HMAC secret is configured there. This plan-gate submission itself changes only this coordination packet.

## Implementation Steps

1. Inventory the current evidence chain and freeze its known gaps in tests before changing behaviour: server stamps `candidate_freshness_id` and `proposal_freshness_id`; confirm recomputes and compares only when the client supplies turn/freshness fields; missing freshness remains tolerated; no HMAC signing exists; wrapper `staff_review.confirm_payload` starts with `confirmed=false`; UI smoke can click confirm without backend calls unless `bernie_confirm_adapter=true`.
2. Define a signed evidence envelope with stable versioning, purpose, issued-at or monotonic event marker, practice/user/session/turn ids, patient id or provisional identity marker, practitioner id, appointment date, start time, duration, location, selected candidate freshness, proposal freshness, diary event/version marker, and HMAC signature. Keep raw patient text out of the signed payload where a stable UUID or provisional marker is enough.
3. Add pure evidence-helper invariants: canonical JSON serialization is deterministic; equivalent field ordering signs to the same value; any material field change changes verification result; unknown versions fail closed; wrong purpose fails closed; missing signature fails closed; wrong key/tampered HMAC fails closed; comparison uses constant-time HMAC verification.
4. Add route-level missing-evidence tests for the signed path: a confirmation body with `confirmed=true` and no signed evidence must return a blocked response and must not create `Appointment` or `AppointmentAuditLog` rows. If legacy unsigned payloads remain temporarily accepted, tests must prove they are accepted only on a deliberately named legacy path or compatibility mode and produce explicit audit/response evidence such as `legacy_unsigned_confirmation_compat`, not signed-evidence success.
5. Add tamper tests: mutate each signed coordinate one at a time after minting evidence: `patient_id`, `patient_name_provisional` marker, `practitioner_id`, `appointment_date`, `start_time/start_time_local`, `duration_minutes`, `location_id`, `appointment_type_id`, selected candidate freshness, proposal freshness, `turn_ref.session_id`, `turn_ref.turn_id`, and `reference_date`. Each mutation must block before `_create_appointment_from_body` and leave row counts unchanged.
6. Add mismatch tests that distinguish semantic mismatch from HMAC tamper where useful: valid signature for patient A cannot confirm a payload whose `selection_proposal.create_proposal.command.patient_id` is patient B; valid signature for Dr Shera at 09:00 cannot confirm Dr Chen, another date, or a different slot; valid signature for one practice/user cannot confirm under another practice/user token.
7. Add replay/stale diary-event tests: mint signed evidence, then create a conflicting appointment or otherwise advance the diary event/version marker; replaying the old signed evidence must block with a stale/replayed evidence code and no write. Existing conflict revalidation already blocks some stale slot truth; S1 should prove the signed evidence also binds to the diary freshness/audit marker so replay is diagnosed as stale evidence, not merely accidental conflict.
8. Add confirm-affordance tests: the backend-owned `confirm_affordance` should allow confirm-grade UI only when signed evidence is present and verified for the staged proposal in S1 mode. Advisory-only retrieval frames, stale context frames, missing staged proposal, unsigned legacy payloads, or client-created evidence must not set `confirm_grade_allowed=true`.
9. Add UI echo harness checks only after backend contract is clear: route-intercept `confirmation_ready` with signed evidence, click confirm, and assert the POST body contains the exact server-provided signed evidence plus `confirmed=true`; route-intercept a tampered local state and assert the UI does not fabricate a signature or derive authority from selected-slot text. This is a payload-transport check, not proof of backend trust.
10. Preserve and make explicit legacy compatibility: keep current Sprint 104/105 compatibility tests if Ariadne decides old clients still need to reach the revalidation stage, but rename or supplement them so nobody reads "missing signed evidence succeeds" as acceptable on the S1 signed path. Compatibility must be time-boxed, audited, and lower trust than signed confirmation.
11. Verification after implementation approval: run focused pytest suites for signed evidence, turn contract, confirm-create proposal, evidence contract, confirm gate, and domain package exports; run `pytest review/test_diary_smoke.py -q -k "bernie_confirm or confirmation_ready or stale"` if UI echo tests are added; run `node --check docs\diary\diary.js` if the diary asset is touched; run `git diff --check`.

## Visual / Behavioural Acceptance Checks

Backend acceptance:

- Missing signed evidence on the S1 signed confirmation path blocks with a typed reason and writes no appointment or audit rows.
- Tampered HMAC, wrong purpose, wrong version, missing signature, or any signed-field mutation blocks before appointment creation.
- Valid evidence for patient/practitioner/date/slot A cannot confirm patient/practitioner/date/slot B.
- Valid evidence for one user/practice/session/turn cannot be replayed from another user/practice/session/turn.
- Valid but stale evidence after a diary event/version change, conflict creation, roster change marker, or refresh marker blocks and writes nothing.
- Legacy unsigned compatibility, if retained, is clearly separate from signed evidence and cannot set signed-confirm audit evidence or confirm-affordance authority.
- No AI provider, practice-knowledge retriever, visible UI copy, DOM state, or client-side generated field is consulted as confirmation authority.

UI/review acceptance:

- The Bernie review panel may display a Confirm control only from backend-owned confirm-affordance state backed by signed evidence.
- The Diary UI echoes the server-provided signed evidence exactly; it may toggle `confirmed` after explicit staff click, but does not create, patch, or recalculate a signature.
- Navigation, Today/Prev/Next/date picker, Refresh, new staff instruction, choose-another-time, and stale proposal cleanup remove or disable confirm-grade state rather than preserving old signed evidence.
- Technical evidence can remain in Details/debug surfaces, but the main receptionist panel stays calm and does not show raw HMACs as user-facing clinical text.
- No layout or behaviour changes occur in diary grid geometry, appointment cards, stacking, waiting room, status controls, booking modal, taskpane, or Command Centre.

## Risks / Ambiguities

The main design choice is whether S1 should be purely stateless HMAC over a canonical payload or should also bind to a server-side diary event/version marker. Pure stateless HMAC proves the payload came from the server but does not by itself prove the diary has not changed; replay resistance needs a deterministic freshness marker or revalidation block that Ariadne can inspect. The repo currently has persistence-shaped Bernie session contracts but no persisted session table, so session replay checks must not accidentally require a new table unless Ariadne expands scope.

There is also a legacy compatibility tension: current tests intentionally allow missing freshness fields so Sprint 104 clients keep working. S1 can preserve that only if the signed confirmation path is distinct and fail-closed. If a single endpoint must serve both old and new clients, response/audit codes need to make unsigned compatibility impossible to confuse with signed confirmation evidence.

Finally, route-intercepted UI tests can prove exact payload echo and stale-button behaviour, but not cryptographic enforcement. The cryptographic and no-write invariants belong in backend tests; the UI is merely the courier.

## Codex Plan Review

- Review result: Accepted as S1 invariant guidance. Ariadne may implement these
  tests directly or release a Codex worker after the backend evidence shape is
  finalized; backend tests own cryptographic/no-write proof, UI tests own
  courier/exact-echo proof only.
- Required changes before implementation: keep legacy compatibility tests
  explicitly labelled so old unsigned success cannot be mistaken for signed
  authority.
- Approved to proceed: yes
