# Provider-free unmounted delete-confirm physical-design architecture plan

Date: 2026-08-15

Timestamp: 2026-08-15T15:24:20+10:00 (Australia/Brisbane)

Source HEAD: `6514d35c465e304a421218890264f61c33ba51bb`

Status: `frozen_for_provider_free_unmounted_architecture`

Reasoning level: material authority / transaction architecture / Extra High

## Purpose

Freeze the narrowest additive physical contract that can embody the accepted
delete-confirm conditional-command kernel before any application model,
migration, service, route or database is edited or executed.

This tranche selects representation, migration order, canonical receipt and
transaction semantics only. It does not implement them, lower executable DDL,
import application modules, open a database, acquire a real lock, mount a
route, grant a capability or move product data.

## API Spine classification

This is a REST/OpenAPI command-security, audit and idempotency design.
GraphQL remains read-only. Events remain non-authoritative acceleration hints. Model,
Context Fabric and channel output remain inert proposals. Only the future
backend-owned dedicated `confirmAppointmentDeleteProposal` command may enter
this design. Raw compatibility delete and the status-family cancellation path
remain separate ingress and inherit no authority.

## Exact source allowlist

Only the following exact non-protected sources may be read, hashed or searched
for this tranche:

| SHA-256 | File |
|---|---|
| `4122b7b2fbe9d712ef3cea47a2ee4f67ec7d2b55e38d594c85b89fd9d375af38` | `docs/raisa-provider-free-read-only-unmounted-delete-confirm-physical-representability-review-closeout.md` |
| `3895da022f977bba9259a327bbccf7068c2b281c7a42e4ce36978f1367036975` | `orchestration/agent_inbox/codex/raisa-delete-confirm-physical-representability-review-sol-acceptance.md` |
| `418c4239f7e5a85bcb76d056322ab32a50e46bda00b4b17bbac0ec79be948a2e` | `orchestration/continuity/raisa-provider-free-read-only-unmounted-delete-confirm-physical-representability-review/review-contract.json` |
| `6a5eb85b532a73169432788f59205e55e0b423056484680bb13938acb100dd6c` | `orchestration/continuity/raisa-provider-free-read-only-unmounted-delete-confirm-physical-representability-review/provider-free-review-evidence.json` |
| `8d8e3a388aeda71800f014535dccc63af8da6aaa945834add044dc2a49097a91` | `docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission.md` |
| `0c7a02078aa360ecc14a6af1af8a12047bad39c68c38862d9e4360c9577556c0` | `docs/raisa-provider-free-unmounted-status-confirm-physical-design-architecture-plan.md` |
| `3ca874ef0215fb57c74bb8e886c9bc48a912666830c9530e4165a21186dfcfc5` | `docs/security/raisa-provider-free-unmounted-status-confirm-physical-design-architecture-threat-model-delta.md` |
| `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` | `orchestration/api_spine_adr.md` |
| `c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a` | `docs/api-spine/openapi/appointment-commands.yaml` |
| `6be0d9ab4fc33a8709268d2f2a4550b6063e3f3e4188349c5fe3b0b6acd14431` | `app/models/tenancy.py` |
| `d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915` | `app/models/appointments.py` |
| `c35c271e9308f1f57eeeee53eefa6388087e126944ab5100c225f50066e3a0cf` | `app/schemas/appointments.py` |
| `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` | `app/services/appointment_idempotency.py` |
| `f81fc3acc96f21efa64e1d694331792feebadf08f6384c8ac79542bb196d6624` | `app/routers/appointments.py` |
| `b4671fc5fd82ed06ce4af18b026ab70964a18a48e56157f719be19ce0989107b` | `app/models/application_auth.py` |
| `1dbfa4474178490b19c2332ebac29875641c3ea17742afe77f40aa56189f064b` | `app/services/application_auth_persistence.py` |
| `cac8a5623a838238cc68ded0c93570581391bf08226d2a312149bfe1cca87cfa` | `app/services/application_auth_role_runtime.py` |
| `a77be7e159614a579eb2dec2d3d8e5b401f1c1d1722f5f740367ae74e6a8a59a` | `alembic/versions/h8i9j0k1l2m3_add_appointment_audit_log.py` |
| `da6493f60b8a8d39186c273db0b9615758b3927cc913d1117d12df0003f245fd` | `alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py` |
| `78d730ddf07051f5595c268fc031dea7d454c166a930250255de6aa26e2938ae` | `alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py` |

No source expansion is expected. If an essential fact is absent, revise this
plan with the exact path and hash before opening it. Directory-root filename or
content discovery is prohibited by AER-0292.

## Frozen physical contract

### Product authority fence and capability grants

The product-facing `users` row becomes the lockable actor/practice authority
fence. It must not be conflated with the explicitly authored-synthetic
`application_auth_*` relations.

Add `users.authority_generation BIGINT`. Its domain is
`1..9223372036854775807`; `NULL`, zero, negative and overflow fail closed. Add
the composite uniqueness invariant `UNIQUE (practice_id, id)`.

Add a closed `user_capability_grants` relation with exactly:

- `practice_id UUID NOT NULL`;
- `user_id UUID NOT NULL`;
- `capability_code VARCHAR(100) NOT NULL`;
- primary key `(practice_id, user_id, capability_code)`; and
- composite foreign key `(practice_id, user_id)` to `users(practice_id, id)`.

The only admitted capability values in this generation are
`appointment.cancel.confirm` and `appointment.read`. Row presence is the grant;
absence is denial. No wildcard, JSON claim, client role claim or model output
can synthesize a grant.

PostgreSQL owns the generation. On user insert it forces generation `1`. On
every update it ignores a submitted generation and preserves the old value
unless `practice_id`, `role` or `is_active` changes, in which case it advances
exactly once. Every capability insert or delete advances the referenced user
generation in the same transaction before the grant change can commit.
Capability identity and ownership are immutable; changing either requires one
delete and one insert and therefore advances the generation for each change.
Overflow rejects the whole transaction.

The future proposal signature and request digest bind the exact positive
authority generation. Confirmation locks the exact `users` row selected by
server-owned `(practice_id, actor_user_id)` `FOR SHARE`; while that lock is held,
the trigger rule prevents user or grant mutation from committing. Both
authority checks require:

- the locked row exists at the authenticated practice and actor identity;
- `is_active = true`;
- the locked role equals the authenticated server role and is one of
  `Receptionist`, `GP`, `Nurse`, `Admin`, `PracticeOwner`;
- the signed authority generation equals the locked current generation; and
- exact grant `appointment.cancel.confirm` exists.

No existing user receives either capability automatically. A later explicit
provisioning gate must grant them. The separate fresh display read requires
exact `appointment.read`; cancellation authority does not imply read authority.

### Authority migration and rollback

The future migration must:

1. add `users.authority_generation` nullable without a table-rewriting default;
2. set server default `1` for subsequent inserts;
3. backfill existing user generations to baseline `1` without claiming prior
   authority chronology;
4. add and validate the positive-range check, then set `NOT NULL`;
5. add and validate `UNIQUE (practice_id, id)`;
6. create the closed capability relation with no rows;
7. install the generation-owner and grant-change triggers before any consumer;
8. prove no null/non-positive generation and no orphan or unknown grant exists;
9. grant no capability and mount no consumer; and
10. keep the generation default for new users.

Schema-only rollback is permitted only before any capability grant or command
receipt uses this contract. After first use, recovery is forward-only and an
automatic downgrade must fail closed.

### Appointment truth and exact reason contract

Reuse the existing practice-scoped appointment row and database-owned positive
`appointment_state_version`. No new appointment version or timestamp identity
is added. A first delete-confirm effect locked at version `n` must publish
exactly version `n + 1`, status `Cancelled`, `waiting_area_id = NULL`, one
mandatory structured reason and the exact nullable free text.

Dedicated ingress accepts exactly one `status_reason_code` from:

`PATIENT_CANCELLED`, `PATIENT_RESCHEDULED`, `PATIENT_UNWELL`,
`PATIENT_TRANSPORT`, `PRACTITIONER_UNAVAILABLE`, `CLINIC_OPERATIONAL`,
`CLINIC_RESCHEDULED`, `ADMIN_ERROR`, `DUPLICATE_BOOKING`, `OTHER`.

`LEGACY_UNCLASSIFIED`, a missing code and status-family-only codes are rejected.
`cancellation_reason` is JSON null or a Unicode string of at most 500
characters. The admitted code and text are signature- and request-bound and
copied byte-for-value to appointment truth, audit state and canonical response.
`confirmed_warnings` is a human acknowledgement set, never a reason.

### Versioned private completed receipt

Reuse `appointment_command_idempotency` and its existing private receipt fields:
`completed_receipt_version`, `session_binding_digest`, `pre_state_version`,
`post_state_version` and `response_body_canonical_bytes`. Add only
`authority_generation BIGINT NULL`.

`completed_receipt_version = 1` remains a family-qualified receipt version. Its
database completeness constraint is widened from one status-only branch to an
exact disjunction:

- the unchanged `confirmAppointmentStatusProposal` / `status-confirm` branch;
  or
- `confirmAppointmentDeleteProposal` / `delete-confirm` / `confirmed_write`
  with positive `authority_generation`, a 32-byte `session_binding_digest`,
  positive pre/post versions with post exactly pre plus one, non-empty canonical
  bytes, target and audit identities, response status/hash/JSON and completed
  state.

No other operation may set `completed_receipt_version`. Existing and future
legacy rows remain `NULL`; they are not inferred or backfilled. An exact
matching legacy row stops without effect as `legacy_receipt_not_replayable`.

The session binding remains the 32 raw bytes of domain-separated HMAC-SHA-256
over authenticated practice, actor and server session identity using a
server-held secret. Raw session identity and secret are neither stored nor
returned. Actor, role, operation, route, target, request digest, authority
generation and session digest must all match before replay disclosure.

### Canonical minimized response bytes

The dedicated successful response consists only of these six fields in this
fixed order:

1. `appointment_id`;
2. `status` (constant `Cancelled`);
3. `status_reason_code`;
4. `cancellation_reason`;
5. `waiting_area_id` (JSON null); and
6. `warning_codes`.

Canonicalization is UTF-8 JSON with no byte-order mark or insignificant
whitespace, fixed field order, RFC 8259 escaping, JSON null for absent nullable
text and waiting area, and warning codes in their already-validated canonical
order. Duplicate keys, non-contract fields and non-finite values are rejected.
The existing response hash is lowercase hexadecimal SHA-256 of these exact
stored bytes. JSONB is inspection state; the byte field is delivery authority.

Initial delivery and replay use the identical stored byte buffer and never
reserialize JSON. Before replay, SHA-256 is recomputed over the stored bytes and
compared in constant time. Integrity failure releases no body. The current full
`AppointmentConfirmDeleteProposalOut`/`AppointmentOut` response is not the
accepted minimized receipt and cannot be silently reused. Any compatibility or
API-version transition is a later explicit gate.

### Attributable delete audit

Extend `appointment_audit_log` with:

- `audit_contract_version SMALLINT NULL`;
- `authority_generation BIGINT NULL`;
- `pre_state_version BIGINT NULL`;
- `post_state_version BIGINT NULL`;
- `waiting_area_before_id UUID NULL`;
- `waiting_area_after_id UUID NULL`; and
- `audit_evidence_codes JSONB NULL`.

For `audit_contract_version = 1`, constraints require action `delete`, a
non-null command id, positive authority/pre/post generations, post version
equal to pre plus one, status after `Cancelled`, a non-null structured reason,
and null `waiting_area_after_id`. `confirmed_warnings` stores only exact human
warning acknowledgements. `audit_evidence_codes` stores only bounded internal
evidence codes as a JSON array. The current helper's merged legacy array is not
reinterpreted or backfilled.

The command foreign key binds the private session digest, request digest and
operation identity. No raw authenticated session id is added to the audit.
Before commit the service requires exact equality among appointment, audit,
private receipt and canonical response for practice, target, actor, authority
generation, pre/post version, statuses, waiting-area transition, structured
reason, nullable cancellation text and warning codes.

### One transaction and ordered locks

The future delete-confirm kernel owns one PostgreSQL `READ COMMITTED`
transaction. It has one cumulative 2000 ms lock-wait ceiling. Before each lock,
only the positive remaining budget is applied; the budget never resets.
`NOWAIT`, `SKIP LOCKED`, advisory locks and hidden effect retries are forbidden.

The exact sequence is:

1. reject malformed/non-dedicated ingress and missing idempotency identity;
2. begin the command-owned transaction and its cumulative lock deadline;
3. lock the server-selected product authority fence `FOR SHARE`;
4. lock appointment `(practice_id, appointment_id)` `FOR UPDATE`, or stop
   non-disclosing before idempotency access;
5. perform the first complete current-authority and signed-generation check;
6. select the exact idempotency row `FOR UPDATE`; if absent, use one
   target-bound `INSERT ... ON CONFLICT DO NOTHING RETURNING` and then select
   the winning row `FOR UPDATE`, without releasing the appointment lock;
7. repeat the complete current-authority check while every lock is held;
8. classify exact actor, role, authority generation, session, operation, route,
   target, key and request bindings;
9. replay only a complete integrity-valid family-qualified v1 receipt;
10. for a new command, verify explicit confirmation, exact warning
    acknowledgement, signed evidence, expiry, locked source state and exact
    reasons;
11. stage one appointment soft-cancel, one versioned delete audit and one
    complete private receipt;
12. flush once and require the database-owned post version to be pre plus one;
13. require every cross-artifact identity, state, reason and warning equality;
14. commit the appointment, audit and receipt atomically; and
15. deliver only the stored canonical response bytes.

Lock timeout, deadlock, serialization failure or connection loss before commit
rolls back everything and discloses no receipt. There is no server effect retry.
Connection loss after commit is unknown delivery; the caller retries the same
key and request and can receive the one stored receipt after current authority
passes. Races remain possible, but the locked order determines one attributable
winner and preserves the losing outcome without double effect.

### Separate fresh readback

Readback begins only after commit in a new transaction. It re-resolves the
server-authenticated `(practice_id, actor_user_id)`, requires current active
membership, current role and exact `appointment.read`, then authorizes resource
`(practice_id, appointment_id)` before returning current appointment truth.

Readback denial or failure cannot undo the committed command, change its stored
receipt or imply failure. Readback is reconciliation evidence only. The command
response contains no patient, practitioner, free-form appointment reason,
notes, contact or other display data.

## Deterministic artifacts

This tranche will add one closed JSON contract and schema, a provider-free
validator, minimized authored-synthetic evidence and focused tests. They must:

- verify all twenty exact source hashes;
- validate every authority, migration, reason, receipt, audit,
  canonicalization, transaction, lock/wait and readback decision above;
- reject at least sixty hostile mutations, including synthetic-auth reuse,
  ambient/wildcard grants, automatic capability backfill, timestamp authority,
  client generation claims, grant changes without generation advance, missing
  reasons, legacy reason promotion, merged audit codes, JSONB replay, raw
  session storage, weakened/reordered locks, reset wait budgets, authority after
  disclosure, hidden retry, full appointment response and readback-as-commit;
  and
- import no application, migration, database, network or provider module.

## Parallelism and review allocation

- Sol owns material architecture, source binding, acceptance and Git.
- DeepSeek V4 Flash/high may implement only the closed contract, schema,
  provider-free validator, evidence and focused tests after this plan is
  committed. It receives no semantic, acceptance, integration or protected-ref
  authority.
- On 2026-08-15 Yuri directly replaced the verifier allocation with Gemini 3.7
  Flash/high. It owns the fresh independent veto for the exact candidate without
  a separate trial gate. Gemini 3.6 remains historical compatibility only and
  may not be selected as a silent fallback.
- Native subagents are not useful for the same closed mechanical artifact set.

## Acceptance

Pass only if:

1. the fresh five-source receipt and all twenty source hashes pass;
2. every frozen design field is closed and schema-valid;
3. every hostile mutation fails closed;
4. the API Spine remains one dedicated REST command with a private receipt,
   explicit minimized result and separately authorised readback;
5. focused, lineage, API Spine, baton and whitespace checks pass;
6. an exact-candidate fresh independent veto passes;
7. `implementation_authorized` remains false; and
8. protected refs and every unrelated untracked path remain unchanged.

## Forbidden surfaces

No edit or import of application/model/migration/service/route source; no
executable DDL, database driver, SQL execution, real transaction or lock; no
capability provisioning; no provider call, ADC, credential/IAM/browser action,
network, product/patient/clinical data, source watcher/event, product command,
deployment, production, release, Pages or protected-ref movement. Preserve and
never stage `docs/branding/` or any unrelated untracked file. Use explicit-path
staging only.

## Recovery and next candidate

One mechanical correction to contract/schema/validator/test artifacts is
allowed if it changes no frozen semantic, source scope, authority or claim. Any
material contradiction returns `revision_required` and preserves the candidate
without implementation.

If this architecture passes, the next narrow candidate is a provider-free
unmounted delete-confirm physical schema-and-transaction scaffold. That future
tranche may edit only an exact frozen source set; migration execution, route
mounting, capability provisioning and product data remain separately gated.
