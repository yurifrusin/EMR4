# plan-codex-ariadne-sprint-s1-signed-confirm-evidence-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | orchestrator |
| Source Task | `claude-sprint-s1-signed-confirm-evidence-contract` |
| Status | accepted |
| Created | 2026-07-03 |
| Source HEAD | `8659e7d` |

## Plan Summary

Claude hit the five-hour session cap before producing the S1 backend plan, so
Ariadne replaces that lane with a backend/domain plan for versioned HMAC-signed
Bernie confirmation evidence. The implementation should add a signed evidence
envelope beside the existing unsigned freshness ids, require it on the new S1
confirmation path, and keep legacy unsigned compatibility explicit, named, and
auditable rather than treating missing evidence as silently fresh.

## My Understanding

The current code already has useful evidence primitives:

- `app/services/bernie_turn_evidence.py` computes deterministic candidate and
  proposal freshness ids from typed slot/proposal coordinates.
- `/proposals/bernie/supervised-booking` stamps candidate and proposal
  freshness ids and prepares `staff_review.confirm_payload`.
- `/proposals/create/confirm-bernie` recomputes expected freshness ids and
  blocks stale/mismatched ids, but only when the client echoes a `turn_ref` or
  freshness id.
- `check_staleness(None, ...)` currently returns fresh for Sprint 104
  compatibility.
- `app/services/diary/confirm_gate.py` is already the backend-owned
  confirm-affordance gate, but it does not yet know whether signed evidence is
  present.

The safety gap is that the old ids are deterministic hashes, not server-signed
authority. They are good cache/freshness labels, but not trust-bearing tokens.
S1 should not jump to persisted server-side sessions or a universal write
grammar yet. It should create the stateless signed-evidence layer that gives
the present Bernie confirm path a firmer foundation and becomes compatible
with later persisted session/event state.

## Intended Surface / Boundary

Backend/domain surface:

- `app/services/bernie_turn_evidence.py` remains the implementation home for
  this sprint, with `app/services/bernie/evidence.py` re-exporting any new
  helpers for bounded-package stability.
- `app/schemas/appointments.py` gains additive optional signed-evidence fields
  on Bernie confirmation-ready payloads and confirmation input.
- `app/routers/appointments.py` mints signed evidence at the same point it
  prepares confirmation-ready `selection_proposal`/`confirm_payload`, verifies
  it before write, and records bounded audit/response evidence.
- `app/services/diary/confirm_gate.py` may gain a small optional
  signed-evidence-present/verified gate input if needed, but should stay pure
  and free of HMAC implementation details.
- Tests should be focused in a new signed-evidence suite plus minimal updates
  to existing turn/confirm/domain-package tests.

Boundary:

- The UI may echo server-signed evidence and toggle `confirmed=true` after
  explicit staff action. It must not mint, repair, infer, or verify signatures
  as authority.
- HMAC verification belongs in backend tests. UI smoke tests prove courier
  behaviour only.
- Do not introduce a persisted Bernie session table, GraphRAG retrieval, or
  unified raw appointment write-path redesign in S1.

## Out Of Scope

- No persisted server-side Bernie session/event storage or Alembic migration.
- No GraphRAG/practice-knowledge route or UI integration.
- No limited Bernie auto-mode or auto-confirm.
- No broad root-to-branch API-spine review.
- No replacement of every raw appointment write endpoint.
- No production secret-management migration beyond using an existing settings
  secret or a narrowly named dev fallback with tests.
- No user-facing UI redesign or diary grid/layout change.

## Files I Expect To Edit

- `app/services/bernie_turn_evidence.py`
- `app/services/bernie/evidence.py`
- `app/services/bernie/__init__.py`
- `app/schemas/appointments.py`
- `app/routers/appointments.py`
- `app/services/diary/confirm_gate.py` only if the confirm-affordance decision
  needs a pure boolean/enum input for signed evidence.
- `tests/test_bernie_signed_confirmation_evidence.py` as the main new suite.
- Targeted updates to `tests/test_bernie_turn_contract.py`,
  `tests/test_bernie_confirm_create_proposal.py`,
  `tests/test_bernie_evidence_contract.py`, `tests/test_diary_confirm_gate.py`,
  and `tests/test_bernie_domain_package.py` as needed.
- `docs/diary/diary.js` and `review/test_diary_smoke.py` only after the backend
  envelope name/shape is settled and implementation is approved.

## Implementation Steps

1. Add a pure, versioned signed-evidence model/helper layer.
   - Suggested envelope fields: `schema_version`, `purpose`,
     `issued_for`/`author` (`bernie_confirm_create_proposal`), `practice_id`,
     `staff_user_id`, `session_id`, `turn_id`, `reference_date`, patient id or
     provisional patient marker, practitioner id, appointment date, start/end
     or local start/duration, appointment type id, location id,
     `candidate_freshness_id`, `proposal_freshness_id`, and optional
     `diary_freshness_marker`.
   - Use deterministic canonical JSON serialization and HMAC-SHA256 with a
     server secret. Verification must use constant-time comparison.
   - Keep raw patient instruction text out of signed payloads.

2. Preserve legacy freshness ids as descriptive freshness labels.
   - Keep `compute_candidate_freshness_id()` and
     `compute_proposal_freshness_id()` stable for existing tests.
   - Do not make those hashes the final trust boundary.
   - Add new helpers such as `mint_signed_confirmation_evidence()` and
     `verify_signed_confirmation_evidence()`.

3. Add additive schema fields.
   - Candidate/proposal outputs may expose a signed evidence object/token where
     needed, but the main signed object should be attached to the confirmation
     payload prepared in `staff_review.confirm_payload`.
   - `BernieCreateProposalConfirmationIn` should accept
     `confirmation_evidence` or similarly named signed evidence.
   - Retain existing optional fields for one compatibility window.

4. Mint signed evidence only after a deterministic proposal is ready.
   - In supervised booking's `confirmation_ready` branch, compute both old
     freshness ids, then mint signed evidence from the final selected candidate,
     create proposal command, authenticated practice/staff user, and turn/ref
     context.
   - Include that evidence in the backend-prepared confirm payload. The browser
     should not assemble it field by field.

5. Verify signed evidence before any write.
   - In `confirm_bernie_create_proposal`, if signed evidence is supplied, verify
     purpose/version/signature and every semantic coordinate against the posted
     `selection_proposal` and authenticated user/practice before entity checks,
     revalidation, and appointment creation.
   - On failure, return the existing structured blocked response with typed
     codes such as `signed_evidence_missing`, `signed_evidence_tampered`,
     `signed_evidence_mismatch`, `signed_evidence_wrong_purpose`,
     `signed_evidence_wrong_actor`, or `signed_evidence_stale`.
   - Appointment and audit row counts must remain unchanged on every block.

6. Make legacy compatibility explicit.
   - If the endpoint still accepts old Sprint 104/105 unsigned payloads, that
     path must be deliberately named in code/tests and emit response/audit
     evidence such as `legacy_unsigned_confirmation_compat`.
   - Missing signed evidence must not be described as fresh signed evidence.
   - Prefer a small compatibility helper rather than spreading `None means
     fresh` logic into new signed code.

7. Bind to replay/staleness as far as current architecture allows.
   - Since S1 is not adding persisted sessions, pure HMAC proves server origin
     but not by itself that the diary has not changed.
   - Continue to rely on deterministic create-proposal revalidation for
     conflicts.
   - If a current diary freshness marker already exists, include it. If not,
     document that replay-after-diary-event is blocked by revalidation now and
     will become signed event-version evidence in the N4 session/event sprint.

8. Update confirm-affordance semantics.
   - If backend responses claim `confirm_grade_allowed=true`, they should also
     have a staged proposal and signed confirmation evidence in S1 mode.
   - Add a pure gate input if needed, for example
     `signed_evidence_state: absent | present | verified | legacy_compat`, but
     keep HMAC operations outside `confirm_gate.py`.

9. Add adversarial tests before/with implementation.
   - Pure helper tests: deterministic canonicalization, signature verifies,
     tampered field fails, wrong purpose/version/key fails, missing signature
     fails, constant-time compare path used.
   - Route tests: missing signed evidence on the S1 path blocks; tampering each
     material coordinate blocks; wrong practice/user/session/turn blocks;
     replay/conflict revalidation blocks without writes; legacy unsigned path
     remains explicit if retained.
   - Domain/export tests: new helpers are exported through `app.services.bernie`.

10. Add UI courier tests only after backend shape is fixed.
    - Route-intercept `confirmation_ready` with signed evidence.
    - Click confirm and assert the POST body contains exactly the server-provided
      signed evidence plus `confirmed=true`.
    - Assert missing/malformed `confirm_affordance` still suppresses confirm UI.

## Visual / Behavioural Acceptance Checks

- A normal Bernie confirmation-ready response includes server-minted signed
  evidence in its confirm payload.
- Confirming with valid signed evidence reaches the existing create-proposal
  revalidation path and can still create exactly one appointment plus one audit
  row.
- Missing, malformed, wrong-version, wrong-purpose, wrong-actor, tampered, or
  mismatched signed evidence returns a structured blocked response and writes
  no appointment/audit rows.
- Existing stale freshness-id blocks continue to work.
- If legacy unsigned payloads are still accepted, they are clearly labelled as
  legacy compatibility and cannot set signed-evidence audit/affordance flags.
- The UI only echoes signed evidence; it does not manufacture it.
- No visible diary grid, booking modal, appointment card, Waiting Room,
  taskpane, Command Centre, or practice-knowledge UI behaviour changes.

## Risks / Ambiguities

- Secret source: choose the existing app secret if available and appropriate, or
  add a narrowly named settings value with a dev fallback. Do not hard-code a
  production secret.
- Replay semantics: stateless HMAC proves origin and integrity, but replay after
  diary mutation still needs either current revalidation or a future event
  marker. Do not overclaim full persisted-session replay resistance in S1.
- Legacy compatibility: the current test suite expects missing freshness ids to
  be tolerated. S1 must either keep that compatibility explicitly or update
  tests with a clear migration boundary.
- Payload size/readability: raw HMAC material should stay out of main
  receptionist copy and live in technical payload/details only.

## Codex Plan Review

- Review result: Accepted. This replaces the failed Claude backend plan lane
  after Claude hit the five-hour session cap. Implement the backend/domain
  slice first so UI work can echo a concrete server-owned evidence shape.
- Required changes before implementation: preserve existing unsigned freshness
  ids as compatibility/freshness labels; do not present them as signed
  authority. If legacy unsigned confirmations remain accepted, mark the path
  explicitly in response/audit evidence.
- Approved to proceed: yes
