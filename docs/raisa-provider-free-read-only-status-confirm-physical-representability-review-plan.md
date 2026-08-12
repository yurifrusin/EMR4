# Provider-free read-only status-confirm physical representability review plan

Date: 2026-08-12

Source HEAD: `3af1af85cc3e6ee646f856a1ce6f306495741894`

Status: `frozen_for_exact_file_read_only_review`

## Purpose

Determine whether the accepted semantic `appointment_state_version`, private
completed-receipt correlation and ordered
`practice -> appointment -> idempotency_record` boundary can be represented by
the existing application/migration structure without weakening the accepted
architecture or rehearsal.

This is a representability review, not a physical design or implementation.
It may describe exact existing capabilities and missing primitives, but it may
not select a column type, default/backfill, migration revision, SQL expression,
ORM/service composition or route integration.

## Protected-scope correction

AER-0292 is registered before this plan. The first filename-metadata discovery
used a directory root and enumerated prohibited protected authoring path names.
No content was opened. That output is discarded and prohibited from this
review. Every source below is an exact already-known non-protected path; no
directory-root content or metadata search is permitted.

## Exact accepted inputs and source allowlist

Only these exact non-protected artifacts may be read, hashed or content-
searched:

| SHA-256 | File | Purpose |
|---|---|---|
| `2b379cbaefeac83a79a3776f78c58b48a94b4695de3356d56a57318a5ab594e7` | `docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal-closeout.md` | Accepted claim and next boundary |
| `5aa5cfb2bc7690904fbebcb8ff053b176bb9cb0bea12650a766b8391278a48f5` | `orchestration/agent_inbox/codex/raisa-status-confirm-runtime-convergence-rehearsal-sol-acceptance.md` | Acceptance and closed authority |
| `6f2c970a4ab9234e72d6ffb08b2aa9b8738b779b94cee1885dbf262bfb5306ce` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/convergence-architecture-contract.json` | Exact semantic contract |
| `18c5bf4f6b6c22ab310e1571f794598a4317ff32f9103445b9d23edc5d112918` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal/rehearsal-packet.json` | Exact schedules and expected physical effects |
| `503b8ea4fcd92fa8043ff5caf8fd8440e038470530a90fde9509d7ff126d1e06` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal/provider-free-rehearsal-evidence.json` | Accepted pure behavior evidence |
| `c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6` | `docs/api-spine/openapi/appointment-commands.yaml` | Public command/response and idempotency boundary |
| `af00f7318da3f19732843c75b56721db89a3fa0c94b6e0feeb12a614850c4952` | `app/models/appointments.py` | Existing appointment and audit representation |
| `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` | `app/services/appointment_idempotency.py` | Existing receipt and lock representation |
| `a77be7e159614a579eb2dec2d3d8e5b401f1c1d1722f5f740367ae74e6a8a59a` | `alembic/versions/h8i9j0k1l2m3_add_appointment_audit_log.py` | Existing audit physical lineage |
| `da6493f60b8a8d39186c273db0b9615758b3927cc913d1117d12df0003f245fd` | `alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py` | Existing confirmation audit lineage |
| `78d730ddf07051f5595c268fc031dea7d454c166a930250255de6aa26e2938ae` | `alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py` | Existing idempotency physical lineage |

A source expansion is permitted only if an exact file above contains an exact
import or migration link essential to one of the three review questions. The
review must stop and revise this plan with the new exact path and hash before
opening it. It may not enumerate a directory to find that path.

## Review questions and closed verdict vocabulary

For each domain, the review must return exactly one verdict:

- `already_represented`;
- `representable_with_additive_change`;
- `not_representable_without_contract_change`; or
- `insufficient_exact_evidence`.

The domains are:

1. **Locked state version.** Is there an existing positive monotonic state
   identity read with the appointment, or can the semantic contract be added
   without using a timestamp or weakening increment-on-committed-state-change?
2. **Private completed receipt.** Can the existing idempotency/audit structures
   durably correlate operation, practice, target, actor, opaque session digest,
   key, request digest, audit identity, pre/post versions and canonical public
   response digest/bytes without exposing private fields publicly?
3. **Ordered lock boundary.** Can one backend-owned transaction acquire and
   retain practice, appointment and idempotency-record locks in the accepted
   order, stop on target absence, recheck current authority, and only then
   classify/disclose replay or conflict?

The overall verdict is `implementation_not_admitted`. A positive
representability finding proves only that a later architecture can be formed;
it grants no edit or execution authority.

## Deterministic evidence

A provider-free review validator will:

- validate one closed review contract and schema;
- verify all eleven exact source hashes;
- require line-bounded observations from only the six physical/API sources;
- bind every current-state observation to one accepted contract requirement;
- distinguish existing representation, additive need and deliberately
  unselected design choices;
- reject at least thirty hostile changes to hashes, verdicts, observations,
  authority or next work; and
- emit minimized evidence without importing application or database modules.

## Acceptance

The review passes only if:

1. AER-0292 and the fresh five-source receipt validate;
2. all eleven hashes pass and no source outside the exact allowlist is opened;
3. all three domains have one closed verdict supported by exact line evidence;
4. no timestamp is accepted as the monotonic state identity;
5. public response compatibility is separated from private receipt fields;
6. idempotency disclosure is never placed before current target/authority
   checks;
7. at least thirty hostile mutations fail closed;
8. focused, register, API Spine, baton and whitespace gates pass; and
9. protected refs and unrelated untracked files remain unchanged.

## Forbidden surfaces

No application/model/migration/service edit or import, route/database/SQL/
real-lock execution, physical design selection, column/default/backfill,
migration revision, source/watcher/event access, provider, credential/IAM/
browser authorization, network, product/patient data, command expansion,
deployment, production, release, Pages or protected-ref movement. Preserve and
never stage `docs/branding/` or any unrelated untracked file. Use explicit-path
staging only.

## Recovery and next candidate

One mechanical contract/schema/script/test correction is permitted if it
changes no verdict meaning or authority boundary. Missing essential evidence
or a semantic conflict stops at `revision_required`.

If all three domains are at least `representable_with_additive_change`, the
next candidate is a provider-free unmounted status-confirm physical design
architecture. It may select an exact additive representation and migration/
transaction contract, but still cannot edit or execute application or database
code. Any other verdict determines a narrower evidence-recovery plan.
