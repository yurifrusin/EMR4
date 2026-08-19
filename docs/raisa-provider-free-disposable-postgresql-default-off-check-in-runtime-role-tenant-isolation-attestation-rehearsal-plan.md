# Provider-free disposable PostgreSQL default-off check-in runtime-role and tenant-isolation attestation rehearsal plan

Date: 2026-08-19

Timestamp: 2026-08-19T15:57:14.2434422+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `455e41b8b9038813b290e67c43ce0b3190120988`

Accepted environment architecture source: `a1f309a6d52d01f9866432f7e9abb8095788d023`

Target result:
`raisa_provider_free_disposable_postgresql_default_off_check_in_runtime_role_tenant_isolation_attestation_rehearsal_pass`

Reasoning level: Extra High freezes a database-security and tenant-isolation
evidence boundary. High is sufficient for the fixed implementation, one
disposable run, deterministic verification and check-gated closeout while this
plan remains unchanged.

## Objective

Close only the `tenant_isolation_and_runtime_database_role` operational-
evidence gap identified by the accepted check-in readiness review. In one
uniquely named, locally controlled, disposable PostgreSQL 16 container, bind an
ephemeral normalized authored-synthetic environment manifest to the exact
logical role `appointment_check_in_ordinary_runtime_v1`; create one uniquely
named physical login role; prove that it is non-owner, `NOBYPASSRLS` and owns
no product or probe relation; and prove exact same-tenant access plus cross-
tenant denial under forced RLS.

The run creates no ordinary environment, selected practice, real credential,
product row, admission record, command receipt or runtime configuration. The
manifest is declarative evidence input under the API Spine. Typed code and
PostgreSQL policy enforce the rehearsal; the manifest never becomes a policy
engine or activation authority.

## Exact source boundary

The rehearsal decodes strict UTF-8, canonicalizes CRLF to LF, rejects bare CR
bytes and verifies SHA-256 before any Docker or PostgreSQL action.

| SHA-256 | Exact source |
|---|---|
| `07e80eb431f664a1f0f2bcd9ac978e6071c7dbd0d004f684001a2a6e80e41e11` | `docs/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture-plan.md` |
| `13a7b267df199e85d841ee927bb6ce06dcdc6bfff202d32a346d965c3099f2a3` | `docs/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture.md` |
| `3e4d9b9e5ed19d624cfed2a3643ca1b75dab8ce5f30a2434eeb98baf78207c94` | `docs/security/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture-threat-model-delta.md` |
| `e9aab3504520d955a0ce2c94c32a5f9a6ae25d7bbf129c7f2bd21951201c34d8` | `orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/contract.json` |
| `786cab3b19231c391d281cf36568b4206fe5f11b2a2ac51469f0996c3e718e88` | `orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/environment-manifest.schema.json` |
| `35f09c1118734d6b40ae267732a168343e2b76ebd9dd00fd901a7d891a831018` | `orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/architecture-report.md` |
| `0858486ff6cd173a6b3b397585e7b1ff74c578b341a8e34b8425e114e0520b5e` | `docs/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture-closeout.md` |
| `ecac18824503953828d876eda863f40c419af5d5b92b0ef1fd180730452570ea` | `orchestration/agent_inbox/codex/raisa-check-in-environment-manifest-secret-posture-architecture-sol-acceptance.md` |
| `875afd5bdfcac9e8cdbc5deb000645c638b68d1eb2239d3cd55f130366c08bd9` | `scripts/raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal.py` |
| `9dbc172af43d1f858335d747def4c520643790b89646e2bfeef1a15124ab600d` | `scripts/raisa_provider_free_disposable_postgresql_status_confirm_scaffold_parse_catalogue_rehearsal.py` |
| `dcacab90f9d785229604e0cd3eab6f185430d4e5c1cd146fc4144858d3aa3540` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal/rehearsal-contract.json` |

The last three sources contribute only the already accepted disposable Docker,
loopback relay and captured-ID cleanup machinery. Their product schema,
application role, rows, product adapter and behavioral claims are not imported.

## Fixed containment profile

One run must use:

- the already cached exact image `postgres:16-bookworm`, with pull policy
  `never`;
- a cryptographically random suffix on one harness-labelled internal Docker
  network and one harness-labelled container;
- no published port, no external network attachment, one fixed in-process
  IPv4 loopback relay and no fallback transport;
- container-local tmpfs at `/var/lib/postgresql/data` with
  `rw,noexec,nosuid,size=268435456`, 512 MiB memory, 1 CPU, 128 PIDs and restart
  policy `no`;
- a uniquely named database-local physical role and a 32-byte random
  authored-synthetic password held in process memory only; and
- captured container/network IDs, ownership labels and nonce equality for all
  teardown actions. Names or discovery output can never be teardown authority.

No image pull, Docker volume, host data mount, local `.env`, process credential
read, cloud/hosted/existing PostgreSQL server, provider call or product runtime
is permitted.

## Ephemeral manifest fixture

The in-memory fixture must validate against the accepted closed normalized
schema and bind exactly:

- schema `emr4.check-in-ordinary-environment-manifest.v1`;
- environment class `test` and one fixed authored-synthetic environment ID;
- authority Git object `a1f309a6d52d01f9866432f7e9abb8095788d023`;
- one opaque authored-synthetic practice reference and snapshot generation 1;
- logical role `appointment_check_in_ordinary_runtime_v1` and the exact dynamic
  physical role identifier;
- the three ordered opaque `secret-ref:` slots and structurally valid rotation
  evidence references; and
- deny-only break glass in exact state `inactive`.

The role password is deliberately not the database-credential reference and
is never serialized. The manifest's rotation records are shape fixtures only:
this run does not verify key custody or rotation and may not release
`evidence_gate_satisfied` or an ordinary admission record. The manifest digest,
not the manifest as authority, binds the role attestation.

## Exact database object and role boundary

The admin-owned probe schema contains one table with `practice_id`, a synthetic
row identifier and a non-PHI marker. It is not an EMR4 product relation. The
table has RLS enabled and forced and one closed policy using transaction-local
`app.current_practice_id` for both `USING` and `WITH CHECK`.

The dynamic login role must have exactly:

- `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOINHERIT`,
  `NOREPLICATION`, `NOBYPASSRLS` and no role membership;
- `CONNECT` on the disposable database, `USAGE` on the probe schema and only
  `SELECT`, `INSERT`, `UPDATE`, `DELETE` on the probe table;
- zero owned databases, schemas, relations, sequences, functions or policies;
  and
- no grant, membership or ability to `SET ROLE` to the admin role.

It receives no privilege on `public`, no product relation, no migration
ownership and no default privilege.

## Fixed scenario matrix

All scenarios are serial against the same captured instance:

1. closed manifest validation binds its logical and physical role plus full
   authority object;
2. catalogue proves every negative role attribute, empty memberships and zero
   owned objects;
3. catalogue proves admin ownership, enabled/forced RLS and one exact policy;
4. tenant A transaction sees only A and can insert/update an A probe row;
5. tenant B transaction sees only B;
6. tenant A's explicit read of tenant B returns zero rows;
7. tenant A's attempted tenant B insert fails with exact RLS SQLSTATE `42501`;
8. tenant A's attempted update and delete of tenant B each affect zero rows;
9. an absent transaction-local tenant setting yields zero rows;
10. the tenant setting is absent after transaction completion;
11. `SET ROLE` to the admin role fails with SQLSTATE `42501`; and
12. the physical role is dropped and observed absent before captured-ID
    container/network teardown.

Same-tenant success prevents a universal-denial false positive. Cross-tenant
read, write, update and delete checks prevent a select-only false claim.

## Evidence and redaction boundary

The run emits two committed non-PHI JSON artifacts:

1. a typed tenant-role attestation containing only non-secret IDs, role
   catalogue booleans, ownership/grant counts, policy facts and scenario
   outcomes; and
2. a parent rehearsal evidence record that binds the attestation artifact's
   SHA-256, manifest digest, exact source hashes, contained runtime profile,
   cleanup proof and claim boundary.

Neither artifact may contain a password, connection URL, Docker environment,
raw command output, raw exception, container/network name, local path, process
environment value or secret-material hash. Failure evidence is sanitized to
stage, reason code, exception class and SQLSTATE only. A recursive forbidden-
field/value scanner and closed schemas enforce this boundary before release.

The evidence label is
`authored_synthetic_provider_free_disposable_postgresql_role_tenant_attestation`.
It is operational evidence for physical representability of the synthetic role
and isolation contract only. It is not product, ordinary-practice, secret-
custody, rotation, rollback, unknown-commit, production or deployment evidence.

## Cleanup and recovery

On success, the admin revokes/drops owned probe privileges, drops the physical
role, queries its exact absence, disposes both engines and stops the relay
before container teardown. On any failure, engines and relay still close and
captured-ID container/network cleanup runs. Success requires exact container ID
absence and exact network ID absence after empty-network reverification.

If Docker, the cached image, ownership labels, internal network, tmpfs profile,
readiness, relay, role creation, scenario evidence, redaction or cleanup cannot
be proved, the result is failure. No retry is implicit. A residual owned
container/network or role is a cleanup recovery issue, not evidence to accept.

## Exact owned outputs

Sol may create or update only:

- this plan and its threat-model delta;
- one closed rehearsal contract, contract schema, attestation schema and parent
  evidence schema under the named Continuity directory;
- one provider-free harness, focused provider-free/unit tests and one plan
  test;
- one successful attestation plus parent evidence, or one sanitized failure
  artifact;
- the narrow clockwork test-fixture correction that pins historical fault
  replay to exact full-Git source
  `f98baaa5c57cfcf00f8d2e6cd0d1113d4a59ed6e` instead of mutable HEAD;
- required Ariadne and exact-candidate review receipts; and
- closeout, Sol acceptance, Yuri summary and clockwork-owned closeout surfaces.

No `.env*`, `app/**`, migrations, `docs/api-spine/**`, API/OpenAPI/GraphQL,
product test, client, deployment or provider source is editable.

## Deterministic acceptance

Pass requires:

1. the fresh five-source receipt and all three lane dispositions pass;
2. all eleven source hashes match before environment use;
3. closed contract/evidence schemas and the accepted manifest schema validate;
4. at least 192 hostile contract mutations and 64 hostile manifest/evidence
   mutations fail with zero escapes;
5. Docker containment and cached-image admission pass without pull or published
   port;
6. the dynamic role matches every frozen negative attribute, membership,
   grant and zero-ownership assertion;
7. RLS is enabled and forced on the admin-owned probe and the exact policy is
   catalogue-observed;
8. all twelve scenarios pass with exact SQLSTATE and row-count expectations;
9. the released attestation and parent evidence contain no forbidden value or
   field and bind only full 40-character Git objects;
10. the role is absent before teardown and the captured container/network IDs
    are absent after teardown;
11. canonical ordinary manifests, admission records and releases remain zero;
12. focused tests, accepted architecture/readiness/kernel/latch/Baton/API Spine
    tests, Ruff, compilation and `git diff --check` pass;
13. one fresh Gemini 3.7 Flash/high exact-candidate read-only veto passes with a
    clean unchanged worktree; and
14. one clockwork tick closes the tranche without bespoke updater or protected-
    ref movement while all unrelated untracked paths remain preserved.

Validation correction at 2026-08-19T16:21:38.4733557+10:00 and
2026-08-19T16:23:23.6088940+10:00: five historical
mutable-current assertions may be deselected from the material surrounding
suite. The readiness-plan test
`test_current_latch_and_five_source_receipt_are_exact` requires obsolete atom
`no_ordinary_practice_enablement`, while the current validated latch preserves
the stricter combined atom
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`.
The two readiness and two kernel Continuity assertions that require their
historical graph revisions and historical Compass successor text are likewise
generation-stale after the accepted live clockwork advanced to Continuity 333
/ Compass 315. Their immutable tranche nodes remain tested by the other
Continuity assertions.
The current latch and its full protected-boundary semantics remain covered by
the dedicated latch suites, current-Baton tests, the zero-drift clockwork check
and the fresh five-source receipt; no canonical state is changed to satisfy a
historical literal or predecessor-current projection.

## Parallelism assessment

- **DeepSeek:** declined. The active latch forbids occupied DeepSeek HMR, the
  native Harness still requires its separate provider-free boot proof and
  Claude Code is not a fallback.
- **Gemini:** reserved for one independent exact-candidate read-only veto after
  deterministic database, evidence-redaction and cleanup admission.
- **Native subagents:** declined under current developer policy and because one
  mutable disposable PostgreSQL lifecycle is indivisible.

## Claim and successor

Passing closes only the runtime-role/tenant-isolation operational-evidence gap
for a disposable authored-synthetic environment. It does not close environment
secret/rotation custody or rollback/unknown-commit recovery, and it does not
make ordinary-practice admission ready.

The next dependency-satisfied tranche is
`raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal`. It must receive its own narrow plan and may
not infer activation authority from this attestation.

No ordinary-practice enablement, feature/allowlist change, product/config/API
change, route mount, generic-status `Arrived`, grammar/client change, waiting-
area movement, product/patient/clinical/protected data, live secret, occupied
DeepSeek HMR, production runtime, deployment, release, Pages or protected-ref
movement is authorized. Preserve `docs/branding/`; stage explicit paths only.
