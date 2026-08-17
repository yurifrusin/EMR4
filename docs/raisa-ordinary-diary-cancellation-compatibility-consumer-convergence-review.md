# Ordinary Diary cancellation compatibility-consumer convergence review

Date: 2026-08-17

Timestamp: 2026-08-17T17:11:11.6150802+10:00 (Australia/Brisbane)

Status: `candidate_ready_for_deterministic_verification`

Result:
`raisa_ordinary_diary_cancellation_compatibility_consumer_convergence_review_pass`

Evidence label: `repository_static_authored_synthetic`

## Decision

The ordinary Diary cancellation consumer is not currently compatible with the
accepted canonical delete-only response contract. The smallest later
convergence is one provider-free client-only composition in
`docs/diary/diary.js` plus its focused browser/source tests and cache reference
if required.

That later tranche must remove the 404-to-status semantic fallback, admit only
the canonical delete proposal/confirm family, share the strict proposal and
minimal public-receipt validation already used by Reception One, and require a
fresh authorised Diary read after every terminal or uncertain result before it
claims success or allows another attempt. It requires no backend, route,
OpenAPI, schema, migration or database change.

## Findings by severity

### 1. High compatibility/correctness defect — a successful canonical commit is reported as a failed response

The mounted canonical and hidden hyphenated confirm aliases both return
`AppointmentConfirmDeleteProposalOut`, whose recursively closed public shape
contains a minimal `receipt` and deliberately no `appointment` read model
(`app/routers/appointments.py:5553-5561`,
`app/schemas/appointments.py:746-773`). On committed or replay outcomes the
route serializes that public envelope and explicitly keeps private receipt
bytes out of HTTP (`app/routers/appointments.py:5591-5601`).

The delete proposal now advertises canonical
`/api/v1/appointments/proposals/delete/confirm`
(`app/routers/appointments.py:5470` and
`app/services/diary/confirm_actions.py:77-81`). The ordinary dispatcher posts
there, admits `safe=true` and `autonomy_tier=confirmed_write`, but then requires
`confirmResult.appointment` and throws when it is absent
(`docs/diary/diary.js:10993-11015`).

Therefore the backend can correctly commit, audit and return its accepted
minimal receipt while the ordinary client displays an error. Because the error
path does not run the success-only `loadDiary(true)` at
`docs/diary/diary.js:10525-10529`, the screen may retain the stale appointment
and permit a confusing retry. This is a product-consumer correctness defect and
unknown-outcome handling gap; it is not evidence of database corruption or a
second backend effect.

### 2. Medium semantic downgrade — delete 404 becomes a different status command

`deleteBooking()` first requests the dedicated delete proposal and preserves
both structured and free-text reasons
(`docs/diary/diary.js:10455-10465`). A literal 404 or any caught error message
containing `404` switches to a status proposal for `Cancelled`
(`:10466-10490`). The fallback intentionally omits `cancellation_reason`, then
the shared dispatcher chooses status-versus-delete idempotency from the returned
endpoint (`:10993-10998`).

The fallback still passes through visible staff interaction and signed status
confirmation; it is not a raw or confirmation-free write. It nevertheless
changes command family, audit/evidence/idempotency vocabulary and reason
preservation. New/converged clients must not silently change meaning when the
dedicated route is unavailable.

### 3. Medium admission widening — proposal and endpoint meaning are not bound before confirm

The canonical Reception One bridge binds appointment id, exact structured and
free-text reasons, warnings, blocks, autonomy tier, confirmation requirement
and canonical endpoint before it opens confirmation
(`docs/diary/diary.js:7721-7760`). The ordinary path checks none of that exact
proposal identity before calling the dialog. Its dispatcher uses the global
confirm allowlist and expressly accepts status-confirm, canonical delete
confirm and the hyphenated delete alias (`:3212-3226`, `:10993-10999`). The
`cancellationReason` and `statusReasonCode` dispatcher arguments are not used
to validate the proposal or response.

The later convergence should not narrow the global allowlist needed by other
legacy consumers. It should make the cancellation-specific dispatcher require
the exact canonical delete endpoint and exact expected command binding.

### 4. Medium truth-display gap — reconciliation is success-only

The ordinary modal reloads the Diary only after the dispatcher returns success
(`docs/diary/diary.js:10518-10526`). Staff cancellation, a blocked proposal,
stale/current-authority denial, transport loss, malformed public response and
the post-commit response mismatch do not all force a fresh read before the
control becomes usable again. This is weaker than the accepted adapter-neutral
contract, under which a client may vary presentation but not fresh
reconciliation after a terminal or uncertain command outcome.

The later consumer must distinguish:

- failure before any confirm request, where no delete effect was requested;
- staff cancellation or a typed block, which still requires refreshed current
  truth before another action; and
- a confirm request followed by transport or response uncertainty, where the
  client must claim neither success nor non-commit until fresh truth is read.

If reconciliation itself fails, the cancellation control must remain disabled
with an explicit refresh-required state.

### 5. Low evidence drift — smoke mode models status cancellation and optimistic removal

The ordinary smoke branch constructs a status proposal and removes the local
appointment directly (`docs/diary/diary.js:10447-10453`, `:10514-10516`). That
is clearly synthetic client behavior, not live-backend evidence, but it no
longer rehearses the canonical delete receipt and fresh-read semantics. The
later focused browser fixture should represent the delete-only envelope and
source-backed reconciliation without relabelling route-intercepted evidence as
live.

## Controls already present

- The first click exposes destructive wording and requires a second deliberate
  click before any proposal route (`docs/diary/diary.js:10407-10421`).
- A safe dedicated proposal always has `autonomy_tier=proposal`, so the current
  path also opens a proposal dialog before confirm (`:10495-10512`).
- No raw compatibility `DELETE` call appears in either ordinary consumer.
- Backend delete confirmation retains current-authority/source-truth recheck,
  idempotency, audit and private/public receipt separation.
- The strict proposal checks and `validateDeleteConfirmPublicEnvelope()` needed
  by the later source already exist in the same client file.

## Verification recovery

The first broader verification packet exposed one pre-existing test drift:
`tests/test_api_spine_delete_confirm_idempotency_route_contract.py` built its
ordinary valid proposals without a structured reason, so thirteen cases now
correctly received `reason_code_not_dedicated` from the accepted default-deny
adapter. A reason-only test edit was tried, but a second excluded packet then
showed that the file also assumes the pre-adapter session/current-authority
path and historical HTTP conflict shapes. The edit was reverted. The legacy
suite is contained as future harness debt; the accepted route-convergence and
product-adapter tests remain the current backend controls. Both failing packets
are excluded from acceptance evidence and preserved through AER-0387.

## Frozen smallest later source convergence

Open one provider-free authored-synthetic ordinary Diary client composition
with this exact boundary:

1. Extract or reuse one pure canonical delete-proposal validator shared with
   the Reception One bridge; do not duplicate or weaken its exact identity,
   reason, warning, block, tier and endpoint checks.
2. Remove the status-proposal branch from `deleteBooking()`. Any unavailable,
   malformed or failed dedicated proposal is terminal and fail-closed.
3. Narrow `applySignedDeleteProposal()` to canonical
   `/appointments/proposals/delete/confirm`, clone the prepared payload, set
   explicit confirmation/warning acknowledgements, and derive only the delete
   idempotency key.
4. Validate only `raisa.delete_confirm_public_envelope.v1` and its exact minimal
   receipt against appointment id, reason code and optional note. Never require
   or retain an appointment read model.
5. Reconcile with one fresh authorised Diary read after success, replay, block,
   staff cancellation, denial, transport failure or malformed response. Make
   no outcome claim before that read; a failed read enters refresh-required and
   disables cancellation.
6. Replace the synthetic status/optimistic-removal fixture with an exact
   route-intercepted canonical delete fixture and fresh-read result.
7. Preserve the visible destructive-intent step and contained post-proposal
   confirmation; do not add another backend command or broaden the global
   endpoint allowlist.

Permitted product files for that later tranche are only
`docs/diary/diary.js`, the exact cache reference in `docs/diary/diary.html` if
the script changes, and focused source/browser tests. Backend and API contract
files remain read-only controls.

## API Spine finding

- Boundary classification: destructive REST/OpenAPI command consumer.
- Accepted pattern: dedicated proposal → exact explicit confirmation →
  canonical confirm → backend revalidation/write/audit → strict receipt →
  fresh scoped read.
- Required security/audit/idempotency fields remain backend-owned and are not
  reimplemented in the client.
- Blocked gates avoided: GraphQL mutation, raw compatibility write, provider,
  external patient client, model-to-database write, database/source access,
  deployment and production.
- Open Yuri decision: none. The accepted canonical delete-only family fixes the
  meaning; the later client-only convergence is dependency-satisfied.

## Claim boundary

This review proves repository facts and freezes a later client boundary. It
does not execute or alter a route, prove a live outcome, change product
behavior, or establish representative usability, external-adapter compliance,
deployment or production readiness.

No product/API source, provider, database, patient/product/clinical data,
protected evidence, deployment, release, Pages or protected ref changed.
`docs/branding/` and unrelated untracked files remain preserved.
