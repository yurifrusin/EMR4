# Ordinary Diary canonical cancellation consumer convergence composition plan

Date: 2026-08-17

Timestamp: 2026-08-17T20:46:15.7583144+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_client_only_execution`

Task baseline: `40e20981f3a4a14856f5dc4d127957ca791b06ad`

Target result:
`raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition_pass`

Reasoning level: High. The accepted Extra High review already fixed the
destructive-command meaning and the smallest source boundary. This tranche is
the bounded mechanical realization of that frozen decision.

## Objective

Make the ordinary Diary booking editor consume exactly the same dedicated
delete proposal, canonical delete-confirm command, strict minimal public
receipt and fresh-truth reconciliation contract already used by Reception One.

The client must never turn delete unavailability into a status command, never
require an appointment read model in the confirm response, never optimistically
remove an appointment, and never claim success or non-commit after a terminal
or uncertain result until a fresh authorised Diary read completes.

## API Spine classification

- Boundary: destructive REST/OpenAPI appointment-command consumer.
- Accepted pattern: dedicated delete proposal -> deterministic proposal
  validation -> visible staff confirmation -> canonical delete-confirm ->
  backend current-authority/source revalidation, idempotency and audit -> strict
  minimal public receipt -> fresh scoped Diary read.
- Backend-owned fields: actor/practice scope, signed confirmation evidence,
  current authority, freshness, idempotency result, audit and private receipt.
- Client-owned duties: preserve the intended reason, admit the exact proposal
  and endpoint, gather explicit confirmation, admit the public receipt and
  render only freshly reconciled truth.
- Gates avoided: GraphQL mutation, raw compatibility write, status fallback,
  provider/model execution, database/source access, external patient client,
  deployment and production.
- Open Yuri decision: none.

## Exact source boundary

Permitted product edits:

1. `docs/diary/diary.js` at baseline blob
   `a01733a6b543c250d7f7db4d7ca93a6e8474143c`;
2. the `diary.js` cache reference only in `docs/diary/diary.html` at baseline
   blob `fc242a64e75038d5c2a8b74492eba0285e03d031`;
3. focused ordinary Diary source and route-intercepted browser tests; and
4. tranche plan, threat, evidence, continuity, acceptance and closeout
   artifacts.

Read-only controls include `app/routers/appointments.py`,
`app/schemas/appointments.py`,
`docs/api-spine/openapi/appointment-commands.yaml`, the accepted Reception One
cancellation tests and the accepted compatibility-review chain.

No backend, REST/OpenAPI, GraphQL, schema, service, migration or database file
may change.

## Frozen implementation contract

### 1. One shared strict delete-proposal admission

Extract or reuse one pure cancellation-specific validator in `diary.js` and use
it from both Reception One and the ordinary booking editor. It must bind:

- exact appointment id;
- one allowlisted administrative reason code;
- exact optional cancellation note, normalized to `null` when empty;
- `intent=delete_appointment`;
- recursively valid warning and block issues;
- `requires_confirmation=true`;
- exactly one of an admissible `safe=true` / `autonomy_tier=proposal` proposal
  or a typed `safe=false` / `autonomy_tier=blocked` result; and
- for an admissible proposal, the canonical normalized endpoint
  `/appointments/proposals/delete/confirm` and an object confirm payload.

Malformed, substituted, widened or non-canonical proposals fail closed before
confirm.

### 2. Delete-only ordinary command path

`deleteBooking()` keeps its existing deliberate first destructive-intent click
and the contained proposal confirmation dialog. After local reason validation,
it may call only the dedicated delete proposal. Remove the 404 string probe,
status-proposal request and all status-confirm idempotency selection. A missing,
404, non-OK or malformed delete proposal is a terminal delete-path failure, not
permission to change command family.

Built-in smoke mode must not perform a simulated status cancellation or mutate
its appointment cache as if source truth changed. Canonical behavior is tested
through an exact route-intercepted browser fixture and labelled accordingly.

### 3. Canonical confirmation and minimal receipt

`applySignedDeleteProposal()` must:

- accept only a proposal admitted by the shared delete validator;
- clone the backend-prepared confirm payload;
- set `confirmed=true` and the exact deduplicated warning acknowledgements;
- POST only `/appointments/proposals/delete/confirm`;
- derive only the delete-confirm idempotency key;
- validate only `raisa.delete_confirm_public_envelope.v1` through
  `validateDeleteConfirmPublicEnvelope()` against appointment id, reason code
  and optional note; and
- return the typed committed/blocked public outcome without reading,
  retaining or requiring an `appointment` object.

No private receipt field or unknown public field is admitted.

### 4. Explicit fresh-read outcome discipline

Make the existing Diary loader expose a backward-compatible boolean result:
`true` only after the full authorised read, caches, render and
`emr4:diary-read-complete` event succeed; `false` on missing auth or any caught
load failure. Existing callers may ignore the return value.

After a proposal block or failure, staff cancellation, confirmation denial,
successful or replay receipt, transport loss, non-OK confirmation or malformed
response, the ordinary cancellation flow must perform exactly one fresh
authorised Diary read before it presents a terminal outcome or permits another
cancellation. Local pre-route validation errors do not create a command outcome
and do not require reconciliation.

After a successful fresh read:

- an absent or `Cancelled` appointment is rendered as current cancelled truth;
- a still-current non-cancelled appointment is rendered as current unchanged
  truth and may be retried only through a new dedicated proposal; and
- a receipt/read contradiction is not described as success.

If the read fails, keep the editor visible, set an explicit `refresh-required`
state, disable the cancellation control and make no success/non-commit claim.
Reopening the editor after a later successful full Diary refresh may clear that
local disabled state from the newly read appointment.

### 5. No optimistic product truth

Neither the ordinary path nor its smoke fixture may remove an appointment from
local state as proof of cancellation. Only the fresh authorised read updates
the displayed Diary and closes a successfully reconciled editor.

## Focused acceptance scenarios

Deterministic source tests must prove the exact source boundary, shared proposal
validation, canonical endpoint, delete-only idempotency, strict public envelope,
boolean loader and absence of status/raw/optimistic fallbacks.

Route-intercepted browser scenarios must cover at least:

1. committed minimal receipt followed by fresh read showing absent/cancelled;
2. replay-equivalent committed receipt;
3. typed proposal block without a confirm request;
4. staff cancellation without a confirm request;
5. typed confirm block/denial;
6. proposal 404 with no status or raw fallback;
7. confirm transport/non-OK uncertainty resolved by fresh current truth;
8. malformed public response resolved by fresh current truth;
9. receipt/read contradiction without a success claim; and
10. reconciliation failure producing disabled `refresh-required` state.

Every fixture must capture proposal, confirm, fresh-read, status-proposal and raw
DELETE requests and prove only the admitted calls occurred. Browser evidence is
`route_intercepted_browser`, never live.

## Verification and acceptance

The tranche passes only if:

1. the exact implementation contract and ten browser scenario families pass;
2. existing Reception One cancellation behavior remains unchanged;
3. API Spine delete proposal/confirm artifact and route-convergence controls
   pass without editing their source;
4. JavaScript syntax, Git whitespace and the canonical fast profile pass;
5. no product source outside the exact allowlist changes;
6. one fresh Gemini 3.7 Flash/high exact-candidate veto returns one terminal
   decision after deterministic admission; and
7. the evidence and closeout state exactly what is and is not proved.

## Parallelism-efficacy allocation

- **Sol:** owns this frozen contract, `diary.js`, cache bump, integration,
  deterministic admission, acceptance and Git.
- **DeepSeek V4 Flash/high:** planned for the separable focused source and
  route-intercepted browser test artifact in an isolated exact-HEAD worktree.
  It receives no product-source, acceptance or integration ownership.
- **Gemini 3.7 Flash/high:** reserved for one fresh exact-candidate read-only
  veto after deterministic admission.
- **Native subagents:** declined because current developer policy prohibits
  proactive native delegation.

The plan freeze precedes worker dispatch; Sol product implementation and the
worker test artifact may then proceed independently. Sol integrates tests,
repository pytest/browser execution remains serial, and Gemini starts only
after the deterministic gate passes. Reassess at dispatch, material recovery,
pre-verifier admission and closeout.

## Claim and closed surfaces

Passing proves provider-free authored-synthetic client composition,
route-intercepted browser behavior and repository regression only. It does not
prove a live backend/database result, representative usability, external client
conformance, deployment or production.

No raw compatibility DELETE, status cancellation fallback, backend/API/schema,
migration, database/source/watcher access, product/patient/clinical/historical
data, provider/ADC, credentials/IAM, executable model tool, deployment,
production, release, Pages or protected-ref movement is authorised.
`docs/branding/` and every unrelated untracked file remain preserved;
explicit-path staging only.
