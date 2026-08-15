# Provider-free read-only unmounted delete-confirm physical representability review plan

Date: 2026-08-15

Timestamp: 2026-08-15T13:34:23+10:00 (Australia/Brisbane)

Status: `frozen_for_exact_file_read_only_review`

Task baseline: `d031f67ac971d583b8b3a9f2cae5d8c4d780e70f`

Target result: `raisa_provider_free_read_only_unmounted_delete_confirm_physical_representability_review_pass`

Reasoning level: Extra High for source and verdict freeze; High for mechanical
inventory, validation and closeout within this frozen boundary.

## Purpose

Determine whether the accepted delete-confirm semantic practice-authority
fence, ordered `practice -> appointment -> idempotency_record` locks, exact
structured and nullable free-text reasons, atomic appointment/audit/receipt
completion and separately authorised readback can be represented faithfully by
the existing application and migration structures.

This is a representability review, not a physical design or implementation. It
may describe exact existing capabilities and missing primitives. It may not
select a column type, default, backfill, migration revision, SQL expression,
ORM/service composition, isolation level or route integration.

## API Spine classification

- Boundary: destructive REST/OpenAPI appointment command mutation.
- Canonical operation: future `confirmAppointmentDeleteProposal`.
- Canonical family: dedicated `delete-confirm`; raw compatibility delete and
  status-confirm remain separate ingress families.
- GraphQL: read-only and outside command authority.
- Events and Context Frames: acceleration or expiring evidence only.
- Evidence label: `provider_free_exact_file_read_only_unmounted_review`.

## Protected-scope correction

AER-0325 is registered before this plan. The first filename-metadata query used
scoped directory roots and still surfaced two prohibited protected-authoring
path names. No protected content was opened. The output is discarded and may
not inform this plan, implementation, tests or acceptance.

The corrected allowlist below is copied only from already accepted,
non-protected exact documents and their exact artifact indexes. Every source
command must name literal paths. A source expansion is permitted only when an
allowlisted file contains an exact import or migration link essential to one
of the frozen questions; the review must first revise this plan with the new
literal path and hash. Directory enumeration remains forbidden.

## Exact accepted inputs and source allowlist

Only these exact non-protected artifacts may be read, hashed or
content-searched:

| SHA-256 | File | Purpose |
|---|---|---|
| `8d8e3a388aeda71800f014535dccc63af8da6aaa945834add044dc2a49097a91` | `docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission.md` | Exact abstract transaction contract |
| `202da8412733af4fa3c86df69acbac590e42e80b74ca69b19d63d0d02e7787fb` | `docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-rehearsal-closeout.md` | Accepted claim and next boundary |
| `066587bd4b48630a3f59345a873dbe755c839e1f33acc2ea8368ccd9ad057efe` | `orchestration/agent_inbox/codex/raisa-delete-confirm-conditional-command-kernel-architecture-admission-sol-acceptance.md` | Sol acceptance and closed authority |
| `c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a` | `docs/api-spine/openapi/appointment-commands.yaml` | Existing public command, receipt and compatibility boundary |
| `d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915` | `app/models/appointments.py` | Existing appointment, waiting-area, reason, state-version and audit representation |
| `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` | `app/services/appointment_idempotency.py` | Existing operation-scoped idempotency, lock and private receipt representation |
| `f81fc3acc96f21efa64e1d694331792feebadf08f6384c8ac79542bb196d6624` | `app/routers/appointments.py` | Existing transaction, authority, cancellation and fresh-read boundaries |
| `b4671fc5fd82ed06ce4af18b026ab70964a18a48e56157f719be19ce0989107b` | `app/models/application_auth.py` | Existing persisted practice-session authority representation |
| `1dbfa4474178490b19c2332ebac29875641c3ea17742afe77f40aa56189f064b` | `app/services/application_auth_persistence.py` | Existing current-session persistence and revocation boundary |
| `cac8a5623a838238cc68ded0c93570581391bf08226d2a312149bfe1cca87cfa` | `app/services/application_auth_role_runtime.py` | Existing current role/action/practice authorization evaluation |
| `a77be7e159614a579eb2dec2d3d8e5b401f1c1d1722f5f740367ae74e6a8a59a` | `alembic/versions/h8i9j0k1l2m3_add_appointment_audit_log.py` | Existing audit physical lineage |
| `da6493f60b8a8d39186c273db0b9615758b3927cc913d1117d12df0003f245fd` | `alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py` | Existing confirmation-evidence audit lineage |
| `78d730ddf07051f5595c268fc031dea7d454c166a930250255de6aa26e2938ae` | `alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py` | Existing idempotency physical lineage |

The three accepted-input documents may support semantic requirements only.
Line-bounded physical observations must come from the ten API, application and
migration sources.

## Review domains and closed verdict vocabulary

Each domain returns exactly one verdict:

- `already_represented`;
- `representable_with_additive_change`;
- `not_representable_without_contract_change`; or
- `insufficient_exact_evidence`.

The domains are:

1. **Practice authority fence.** Can one physical row or equivalent exact
   lockable generation stabilize the actor's active state, exact practice
   binding, current role and `appointment.cancel.confirm` capability through
   the transaction, including both accepted current-authority checks?
2. **Appointment truth and lock.** Does one practice-scoped appointment row
   carry lockable positive monotonic state, current status, waiting-area state,
   structured status reason and nullable cancellation text without using a
   timestamp as state identity?
3. **Operation-scoped idempotency and private receipt.** Can one locked record
   distinguish new execution, same-digest replay and different-digest conflict
   while privately correlating practice, operation, target, actor, session
   digest, request digest, audit identity, pre/post version and canonical
   response digest/bytes?
4. **Attributable audit and exact reasons.** Can one audit row bind delete
   action, practice, actor, session/correlation, pre/post state, exact
   structured and nullable free-text reasons, warnings and receipt identity
   without widening public response disclosure?
5. **Ordered atomic boundary.** Can one backend-owned transaction acquire and
   retain the practice, appointment and idempotency locks in that order,
   recheck authority before replay disclosure and before first effect, and
   atomically publish exactly one appointment change, audit and receipt or none?
6. **Fresh readback separation.** Is there a separately authorised,
   practice/action/resource-scoped read path capable of reconciling current
   appointment truth without becoming transaction-success evidence?

The overall verdict is always `implementation_not_admitted`. Positive
representability proves only that a later physical design can be formed.

## Deterministic evidence

The provider-free validator must:

- validate one closed review contract and schema;
- verify all thirteen exact source hashes;
- require line-bounded observations from only the ten physical/API sources;
- bind every observation to one frozen semantic obligation;
- distinguish existing representation, additive need and deliberately
  unselected design choices;
- require one closed verdict for all six domains and an explicit overall
  `implementation_not_admitted` result;
- reject at least forty hostile changes to hashes, observations, verdicts,
  authority, source membership or next work; and
- emit minimized evidence without importing application or database modules.

## Acceptance

The review passes only if:

1. AER-0325, revision 286 and the fresh five-source receipt validate;
2. all thirteen hashes pass and no source outside the literal allowlist is
   opened;
3. all six domains receive one closed verdict supported by exact line evidence;
4. no timestamp is accepted as monotonic appointment or authority identity;
5. practice authority is not inferred from request claims, historical session
   admission, a route-role precheck or the appointment row;
6. public response compatibility is separated from private receipt fields;
7. current authority and target non-disclosure precede idempotency receipt
   disclosure;
8. exact structured and nullable free-text reasons are traced independently
   through appointment, audit and receipt obligations;
9. readback remains a fresh authorised reconciliation path and never proves
   transaction success;
10. at least forty hostile mutations fail closed;
11. focused register, API Spine, baton and whitespace gates pass; and
12. protected refs, `docs/branding/` and all unrelated untracked files remain
   unchanged.

## Parallelism-efficacy allocation

- **Sol:** owns the literal allowlist, semantic questions, verdicts, source
  admission, recovery, acceptance, continuity and Git.
- **DeepSeek V4 Flash/high:** after this plan is committed, receives one bounded
  mechanical package to report line-bounded candidate observations from only
  the ten physical/API sources. It may not choose verdicts, design, authority
  meaning or edit repository source.
- **Gemini 3.6 Flash/high:** reserved for a fresh exact-candidate veto if the
  completed map makes any material positive authority/transaction
  representability claim after deterministic admission.
- **Native subagents:** declined; they duplicate the same literal-source surface
  without adding a separable implementation artifact or fresh verifier class.

Reassess at the exact worker packet, material evidence conflict, pre-verifier
gate and closeout.

## Recovery

One mechanical inventory correction is permitted only for an omitted line
anchor, hash or closed output field. A source outside the allowlist, unsupported
semantic inference, protected-path observation or physical-design choice
rejects the inventory and transfers synthesis to Sol. Missing essential
evidence returns `insufficient_exact_evidence`; it never authorizes broader
search.

## Forbidden surfaces and claim boundary

No application/model/migration/service/route/OpenAPI/GraphQL edit or import,
database/SQL/real-lock execution, column/default/backfill/migration revision,
physical design, runtime composition, watcher/event/source/provider/product
runtime, patient/product/clinical/protected data, credential/IAM/network,
command/write, deployment, production, release, Pages or protected-ref action.
Preserve and never stage `docs/branding/` or any unrelated untracked file. Use
explicit-path staging only.

A pass proves only an exact-file read-only representability map. It does not
prove a selected PostgreSQL design, migration safety, real locking or
concurrency, mounted-route convergence, product behavior, Reception One
cancellation UI, external adapter behavior or production readiness. If every
domain is at least `representable_with_additive_change`, the next safe gate is
a provider-free unmounted delete-confirm physical-design architecture.
