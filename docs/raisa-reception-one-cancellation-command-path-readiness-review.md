# Reception One cancellation command-path readiness review

Date: 2026-08-15

Timestamp: 2026-08-15T11:22:14+10:00 (Australia/Brisbane)

Status: `candidate_ready_for_deterministic_verification`

Result: `raisa_reception_one_cancellation_command_path_readiness_review_pass`

Evidence label: `repository_static_authored_synthetic`

## Decision

Reception One must **not** compose the current cancellation path unchanged.
The next narrow prerequisite is a **provider-free, unmounted delete-confirm
conditional-command kernel architecture and admission rehearsal**.

That tranche should define one future dedicated cancellation transaction with
a locked practice-scoped appointment read, an in-transaction current-authority
check, signed proposal binding, explicit confirmation, exact cancellation
reason preservation, idempotent audit/receipt completion and fresh readback.
It should change no mounted route or product client.

The current dedicated delete proposal/confirm family already contains much of
the required safety envelope. It is not yet at parity with the accepted status
conditional-command kernel, and the ordinary Diary still has a second semantic
path through `Cancelled` status. UI composition should wait until those facts
are converged deliberately.

## Findings by severity

### 1. High readiness blocker — delete confirmation does not hold current truth and authority inside one locked command transaction

The confirm handler reads the appointment through `_get_appointment()`, whose
query has no `FOR UPDATE` lock (`app/routers/appointments.py:575-588`). It then
compares freshness and waiting-area state (`:5604-5648`) before calling
`_apply_appointment_delete()` (`:5662-5673`). That helper performs another
ordinary `_get_appointment()`, mutates status and waiting area, writes audit,
flushes and returns another ordinary read (`:5494-5532`).

The request dependency authenticates an active user and checks role before the
handler, but the delete transaction contains no fresh, explicit current-authority
recheck. The accepted compatibility-write reorientation requires update,
status and delete to lock and recheck the current appointment and to check
current authority inside the mutation transaction.

Consequences:

- the path rejects state changed before its freshness read, but no repository
  proof covers an overlapping different-key write after that read and before
  commit;
- actor deactivation, role revocation or practice-authority change after the
  dependency check is not explicitly rechecked at the write boundary; and
- the test named as concurrent different-key coverage executes two requests
  serially (`tests/test_api_spine_delete_confirm_idempotency_route_contract.py:764-782`).

This is a readiness and proof blocker, not a claim that a production exploit
has been demonstrated. No live concurrency or production evidence was used.

### 2. Medium semantic blocker — the ordinary Diary owns two cancellation meanings

The native Diary first requests the dedicated delete proposal and sends both
`cancellation_reason` and `status_reason_code`
(`docs/diary/diary.js:10191-10200`). On HTTP 404 it instead requests a
`Cancelled` status proposal and intentionally omits `cancellation_reason`
(`:10202-10224`). The shared dispatcher accepts either the status-confirm or
delete-confirm endpoint and derives a different idempotency key accordingly
(`:10716-10739`). Its `cancellationReason` and `statusReasonCode` parameters
are not used to restore omitted command meaning.

Both branches still require the Diary's affirmative cancellation interaction,
proposal review when required, signed backend confirm payload and fresh Diary
reload. The fallback is therefore not an explicit-confirmation bypass.
However, it changes:

- dedicated delete audit action versus status-change audit action;
- preservation versus omission of free-text cancellation reason; and
- delete-family versus status-family idempotency and evidence vocabulary.

Reception One should not inherit that duality. A future product client should
use one dedicated cancellation family and fail closed if it is unavailable.

### 3. Medium contract blocker — the OpenAPI delete contract and mounted runtime are not shape-compatible

The OpenAPI draft declares:

- proposal `POST /appointments/proposals/delete` with required body fields
  `meta`, `appointment_id` and `delete_reason`;
- confirm `POST /appointments/proposals/delete/confirm` with required `meta`,
  `confirmer`, `confirmed`, `delete_proposal`, `confirmed_warnings` and
  `freshness`.

The mounted runtime instead exposes:

- proposal `POST /api/v1/appointments/proposals/delete/{appointment_id}` with
  an optional body containing optional `cancellation_reason`, optional
  `status_reason_code` and warnings; and
- confirm `POST /api/v1/appointments/proposals/delete-confirm`, deriving actor
  and practice from authentication and using delete-specific freshness and
  signed-evidence fields.

The hyphenated confirm mismatch is recorded as a deliberate alias candidate,
but no canonical delete-confirm alias is mounted. The proposal path and payload
shape difference is not represented in the drift tuple. OpenAPI is therefore
an architecture draft here, not an exact callable client contract.

The next architecture tranche must choose an exact internal command envelope
without changing either public surface. Canonical route or schema alignment is
a later separately verified integration step.

### 4. Low documentation/policy drift — cancellation reason requirements are inconsistent

The Diary action grammar says staff must supply a valid cancellation reason
before confirmation (`app/services/diary/action_grammar.py:194-198`). The
runtime schema permits both `cancellation_reason` and `status_reason_code` to be
absent (`app/schemas/appointments.py:646-671`), while the native UI requires an
administrative status reason code but permits blank free text
(`docs/diary/diary.js:10172-10181`). Existing tests deliberately permit null
reason codes for some historical scenarios.

The delete proposal docstring also says its command is ready for raw `DELETE`
after confirmation (`app/routers/appointments.py:5704-5709`), although the
current route contract says cancellation is executable through signed delete
confirmation and the native client uses the confirm endpoint.

This does not block the read-only result, but the next architecture must use
unambiguous terms:

- `status_reason_code`: the structured administrative category;
- `cancellation_reason`: optional bounded free text unless a later product
  policy explicitly makes it required; and
- `confirmed_warnings`: acknowledgements, not reasons.

## Controls already present and worth preserving

The dedicated family is not a blank slate:

- practice scope and mutating staff roles are enforced;
- the proposal does not mutate and always requires confirmation;
- `confirmed=true` is mandatory at confirm;
- HMAC evidence binds practice, actor, command, current appointment state and
  freshness, and tampering or missing evidence blocks;
- freshness includes status, waiting area, existing cancellation fields and
  the proposed command;
- waiting-area side effects are warned and revalidated;
- confirmation requires an idempotency key and atomically completes the
  idempotency record with the appointment mutation and audit;
- same-key/same-body replay returns the stored response without a second audit;
- cancellation text and reason code are preserved on the dedicated path; and
- success returns the resulting appointment and the ordinary client performs a
  fresh Diary reload.

These controls make convergence smaller than a new command family. The next
tranche should adapt and strengthen this family, not replace it with a second
implementation.

## Exact current route inventory

| Surface | Current role | Readiness disposition |
|---|---|---|
| `POST /api/v1/appointments/proposals/delete/{appointment_id}` | Non-mutating dedicated cancellation proposal | Preserve; future internal envelope must make reason policy exact. |
| `POST /api/v1/appointments/proposals/delete-confirm` | Dedicated signed confirmation and soft-cancel write | Preferred family, but requires locked truth/current-authority convergence before Reception One reuse. |
| `DELETE /api/v1/appointments/{appointment_id}` | Mounted raw compatibility write | Keep visible and mounted under current policy; never use for new Reception One composition. Future convergence must account for it without silently inventing confirmation. |
| `POST /api/v1/appointments/proposals/status/{appointment_id}` followed by status confirm | Native Diary 404 fallback for `Cancelled` | Do not carry into Reception One; later remove or constrain only under a separately verified compatibility/client change. |
| Reception One bridge and four-control console | Status plus time/duration/practitioner update only | No cancellation method or control exists; presentation-only cancellation review remains non-operational. |

## Narrowest next tranche

Freeze and execute a provider-free, unmounted architecture/admission rehearsal
with no mounted code changes. It should prove an exact typed transaction
contract for dedicated cancellation:

1. authenticate a practice-scoped actor, but treat that precheck as insufficient;
2. claim or resolve operation-scoped idempotency before destructive work;
3. open a command-owned transaction and lock the exact practice-scoped
   appointment;
4. freshly recheck actor activity, role, practice binding and cancellation
   authority inside that transaction;
5. validate explicit confirmation, signed actor/practice/command/state evidence,
   expiry/freshness, source status, waiting-area state and reason fields;
6. on any denial, roll back both command claim and all domain/audit effects;
7. on success, atomically soft-cancel, clear waiting area, preserve structured
   and free-text reasons, append one audit row and complete one receipt;
8. return a minimized result followed by a fresh authorised readback; and
9. model raw compatibility and status-fallback callers only as separately
   labelled ingress candidates—neither may weaken the dedicated confirmation
   contract or become a second kernel.

Admission scenarios must include overlapping different-key attempts, stale
truth, revoked authority, cross-practice access, missing/tampered/expired
evidence, reason mismatch, response loss, same-key replay and rollback. The
rehearsal remains unmounted and authored-synthetic; disposable PostgreSQL,
route convergence and UI composition remain later gates.

## API Spine classification

- Boundary: destructive REST/OpenAPI command mutation.
- Accepted pattern: dedicated proposal/confirm; no GraphQL mutation.
- Audit/idempotency/security: explicit confirmer, practice/actor binding,
  command-owned transaction, current-authority and source-truth recheck,
  operation-scoped idempotency, append-only audit intent and exact replay.
- Avoided gates: no provider, external patient client, model-to-database write,
  source watcher, event authority, product/runtime mutation or real data.
- Yuri decision: none required. Yuri already selected cancellation; the
  unmounted conditional-command prerequisite is the narrowest fail-closed
  descendant of that choice.

## Claim boundary

This review proves repository facts and selects a prerequisite. It proves no
live concurrency safety, current-authority revocation behavior, PostgreSQL
transaction behavior, runtime route convergence, cancellation UI, patient or
delegated-channel cancellation, product usability or production readiness.

No product, API, OpenAPI, GraphQL, route, schema, database, event, watcher,
provider or UI source changed. Patient/product/clinical data, protected
evidence, provider/ADC, credentials/IAM/network, command execution, deployment,
production, release, Pages and protected refs remain closed.
