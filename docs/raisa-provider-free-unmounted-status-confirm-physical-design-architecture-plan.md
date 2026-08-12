# Provider-free unmounted status-confirm physical-design architecture plan

Date: 2026-08-12

Source HEAD: `fad85e038b7168c3323075024dba7f9d5709eff5`

Status: `frozen_for_provider_free_unmounted_architecture`

Reasoning level: material architecture / Extra High

## Purpose

Freeze the narrowest additive physical contract that can embody the accepted
status-confirm convergence semantics before any application, model, migration,
service or route source is edited or executed.

This tranche selects representation and transaction semantics only. It does
not implement them, lower executable DDL, import application modules, open a
database, acquire a real lock or mount a route.

## API Spine classification

This is a REST/OpenAPI command security, audit and idempotency design. GraphQL
remains read-only, events remain non-authoritative acceleration hints, and the
public `AppointmentStatusResult`/`AppointmentConfirmResultEnvelope` remains
unchanged. All new correlation is private backend state.

## Exact source allowlist

Only the following exact non-protected sources may be read, hashed or searched
for this tranche:

| SHA-256 | File |
|---|---|
| `a587fe03ee8a4a0b51ae1f17308c31dc9660bb96c17e3f508bbb2692b5339189` | `docs/raisa-provider-free-read-only-status-confirm-physical-representability-review-closeout.md` |
| `72997a4b0358b15201c36da976eff827fba49f4bd14de3b354dfa0eb4738d659` | `orchestration/agent_inbox/codex/raisa-status-confirm-physical-representability-review-sol-acceptance.md` |
| `c255e52d5b2c8a90ad2e975b8b55d87b8248aa571811eb1ad3b1049a326e786d` | `orchestration/continuity/raisa-provider-free-read-only-status-confirm-physical-representability-review/physical-representability-review-contract.json` |
| `6f2c970a4ab9234e72d6ffb08b2aa9b8738b779b94cee1885dbf262bfb5306ce` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/convergence-architecture-contract.json` |
| `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` | `orchestration/api_spine_adr.md` |
| `c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6` | `docs/api-spine/openapi/appointment-commands.yaml` |
| `af00f7318da3f19732843c75b56721db89a3fa0c94b6e0feeb12a614850c4952` | `app/models/appointments.py` |
| `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` | `app/services/appointment_idempotency.py` |
| `a77be7e159614a579eb2dec2d3d8e5b401f1c1d1722f5f740367ae74e6a8a59a` | `alembic/versions/h8i9j0k1l2m3_add_appointment_audit_log.py` |
| `da6493f60b8a8d39186c273db0b9615758b3927cc913d1117d12df0003f245fd` | `alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py` |
| `78d730ddf07051f5595c268fc031dea7d454c166a930250255de6aa26e2938ae` | `alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py` |

No source expansion is expected. If an essential fact is absent, stop and
revise this plan with the exact path and hash before opening it. Directory-root
content or filename-metadata discovery is prohibited by AER-0292.

## Frozen physical contract

### Appointment state version

- Add `appointments.appointment_state_version` as PostgreSQL `BIGINT`.
- The domain is `1..9223372036854775807`; `NULL`, zero, negative values and
  overflow fail the transaction.
- Every inserted appointment begins at version `1`.
- PostgreSQL, not route code, owns increments. A `BEFORE UPDATE` trigger
  replaces any submitted version with `OLD.appointment_state_version + 1`.
  Thus every successfully committed row update advances exactly once; a
  direct caller cannot suppress, repeat or choose the version.
- The trigger is a synchronous row invariant, not an event watcher, async cue,
  command authority or durability mechanism.
- Status confirmation reads the version while holding the appointment lock.
  A first status write from version `n` must complete with version `n + 1`.

### Migration and backfill

The future migration must use this order:

1. add the column nullable and without a table-rewriting default;
2. establish server default `1` for subsequent inserts;
3. backfill every existing `NULL` to baseline `1` without claiming historical
   revision chronology;
4. add a positive-range check as `NOT VALID`, validate it, then set `NOT NULL`;
5. install the version-owner trigger before any runtime exposes the version;
6. prove no `NULL`, non-positive or over-range row remains; and
7. keep the server default for new appointments.

No runtime may consume `appointment_state_version` until this sequence is
complete. Schema-only rollback is allowed only before any runtime receipt uses
the contract. After first use, recovery is forward-only; automatic downgrade
must fail closed rather than erase version or receipt meaning.

### Versioned private completed receipt

Reuse `appointment_command_idempotency` and add exactly these private fields:

- `completed_receipt_version SMALLINT NULL`;
- `session_binding_digest BYTEA NULL`;
- `pre_state_version BIGINT NULL`;
- `post_state_version BIGINT NULL`; and
- `response_body_canonical_bytes BYTEA NULL`.

`completed_receipt_version = 1` denotes this contract. Existing rows remain
`NULL`; they are not backfilled, inferred or disclosed as v1 receipts. A
matching legacy row stops without effect as `legacy_receipt_not_replayable`.

For a completed v1 `confirmAppointmentStatusProposal` / `status-confirm`
confirmed write, database constraints require all five fields, a 32-byte
session digest, positive versions, `post_state_version = pre_state_version +
1`, a non-empty stored response, the existing target/audit/status/hash/JSON
fields and the existing completed state. Other operation families retain their
existing contract.

The session binding is the 32 raw bytes of domain-separated HMAC-SHA-256 over
the authenticated practice, actor and server session identity using a
server-held secret. The raw session identity and HMAC secret are never stored
in the receipt or exposed publicly. Actor, role, target, operation, route,
request digest and hashed idempotency key retain their existing private
columns.

### Canonical public response bytes

The v1 response body consists only of the five accepted public fields in this
fixed order: `appointment_id`, `status`, `status_reason_code`,
`waiting_area_id`, `warning_codes`.

Canonicalization is UTF-8 JSON with no byte-order mark or insignificant
whitespace, fixed field order, RFC 8259 string escaping, JSON `null` for absent
nullable values, and warning codes in their already-validated canonical order.
Non-finite numbers, duplicate keys and non-contract fields are impossible and
must be rejected. The existing response hash is lowercase hexadecimal
SHA-256 of these exact stored bytes. JSONB remains an inspection primitive;
the byte field is the delivery authority.

Both the initial response and replay use the exact byte buffer assigned to the
completed receipt. Neither path reserializes JSON. Before replay, the backend
recomputes SHA-256 over stored bytes and uses constant-time digest comparison;
an integrity mismatch releases no body and fails closed.

### One transaction and ordered locks

The backend status-confirm kernel owns one PostgreSQL `READ COMMITTED`
transaction with this order and strength:

1. practice row `FOR SHARE`;
2. appointment row scoped by `(practice_id, appointment_id)` `FOR UPDATE`;
3. idempotency row `FOR UPDATE`, inserting the target-bound in-progress row
   only after the first current-authority check when no row exists.

`FOR SHARE` keeps practice commands mutually concurrent while preventing a
practice update or deletion from crossing the command. `NOWAIT` and
`SKIP LOCKED` are forbidden. All three acquisitions use one positive bounded
lock-wait budget. Lock timeout, deadlock, serialization or connection loss
rolls back the whole transaction, discloses no receipt and returns the existing
generic transient/rolled-back command outcome; there is no hidden server
effect retry.

The exact decision sequence is:

1. reject malformed, non-status or incomplete server-authority ingress before
   the transaction;
2. lock practice; absence/inactive practice stops;
3. lock the practice-scoped appointment; absence stops before idempotency
   access;
4. perform a first current-authority check before any idempotency insert;
5. select the matching idempotency row for update, or insert a target-bound
   in-progress row and hold it;
6. recheck current authority while all three locks are held;
7. classify only exact operation, route, target, actor, role, request digest
   and session-digest bindings;
8. replay only a complete, integrity-valid v1 receipt; conflict, legacy,
   in-progress or corrupt records release no stored body;
9. for a new command, compare the locked source version, recompute warnings,
   verify signed confirmation and apply terminal policy;
10. stage the status mutation, attributable audit and complete v1 receipt;
11. require the database-owned post version to equal pre version plus one;
12. commit all three records atomically; and
13. deliver only the stored canonical byte buffer.

A current-authority loser receives no replay or conflict detail. A concurrent
revocation or command is ordered by the locked transaction and current check;
there is no claim that races disappear, only that exactly one committed order
and attributable result survives.

## Deterministic artifacts

The tranche will add one closed JSON contract and schema, a provider-free
validator, minimized evidence and focused tests. The validator will:

- verify all eleven exact hashes;
- validate the complete state-version, migration, receipt, canonicalization,
  transaction, lock/wait, API and authority decisions;
- reject at least fifty hostile mutations, including timestamp substitution,
  application-owned increments, fabricated legacy backfill, JSONB replay,
  raw session storage, reordered/weakened locks, authority-after-disclosure,
  hidden retries, public-field expansion and any runtime/provider opening; and
- import no application, migration, database or provider module.

## Acceptance

Pass only if:

1. the five-source receipt and all eleven hashes pass;
2. every frozen design field is closed and schema-valid;
3. every hostile mutation fails closed;
4. the API Steward boundary remains REST-command/private-receipt with no
   public response or GraphQL/event authority change;
5. focused, lineage, API Spine, baton and whitespace checks pass;
6. `implementation_authorized` remains false; and
7. protected refs and every unrelated untracked path remain unchanged.

## Forbidden surfaces

No edit or import of application/model/migration/service/route source; no
executable DDL, database driver, SQL execution, real transaction or lock; no
provider, ADC, credential/IAM/browser authorization, network, product/patient
data, source watcher/event, product command, deployment, production, release,
Pages or protected-ref movement. Preserve and never stage `docs/branding/` or
any unrelated untracked file. Use explicit-path staging only.

## Recovery and next candidate

One mechanical correction to contract/schema/validator/test artifacts is
allowed if it changes no frozen semantic, source scope, authority or claim.
Any material contradiction returns `revision_required` and preserves the
candidate without implementation.

If this architecture passes, the next narrow candidate is a provider-free
unmounted status-confirm physical schema-and-transaction scaffold
implementation. That future tranche may edit only an exact frozen source set;
route mounting, database execution and product data remain separately gated.
