# Bernie Stage 2 Durable Authority — Extra High Sol Acceptance

Date: 2026-07-19

Reasoning level: `Sol Extra High`

Decision: `stage2_pass`

Claim scope: `local_synthetic_provider_free_appointment_create_durable_authority`

## Final decision

All fifteen frozen Stage 2 product, database, recovery, security, API Spine,
regression, and scope gates pass on the exact bounded candidate. The accepted
Stage 1 appointment-create vertical now stores Bernie session state and events
durably in PostgreSQL, serializes revisions and command claims, correlates the
session, command, appointment, append-only audit, and receipt, and recovers
safely across restart, concurrency, transaction failure, and replay.

The result is local, synthetic, provider-disabled development evidence only.
It is not production readiness, PII authority, deployment or release authority,
a production database-role or field-encryption design, Stage 3 authority, a new
appointment action, a GraphQL mutation, or autonomous confirmation.

## Authority and five-source binding

Yuri explicitly approved the bounded Stage 2 scope and chose:

- sliding 24-hour retention for incomplete sessions;
- 30-day retention for completed session/event detail; and
- development-database-lifetime retention for the appointment, append-only
  audit, completed command/receipt, and minimal correlation chain.

The frozen contract is
`docs/bernie-stage2-durable-authority-recovery-security-plan.md`, SHA-256
`f104bf3bb2daf1828cd0aad5d7cd9aac22891361bebcd22bb6dca58581af6af2`.
The focused threat-model delta is
`docs/security/bernie-stage2-threat-model-delta.md`, SHA-256
`15c5019a2cbee6053084adbef85ea042465cd7291b4f69b41fa95b64bd94969b`.

Fresh rehydration, pre-plan, verifier-acceptance, and post-restoration
pre-integration receipts all pass and name:

1. `live_handover_current_baton`;
2. `current_authority_allocation`;
3. `active_plan_and_acceptance`;
4. `protected_evidence_boundaries`; and
5. `git_refs_and_worktree`.

The verifier-acceptance receipt SHA-256 is
`12c736eae8d10fb174933ae717527ff372cb88ed291d65a6c79e318db1f76f82`.
The restored pre-integration receipt SHA-256 is
`6350c3fdfab90be8cdace947d0d29f17eada7b13e21be5c7360b5e7baf8279b0`.
The protected-integration receipt SHA-256 is
`9b589c638bcabe034603df62972da9ea015b17a2e650453510b62d7727a95be8`.
The pre-commit receipt SHA-256 is
`451d12450f222ab5d497054c6da80c171e30975d4afca285ca8ad2bf812721da`.
The pre-push receipt SHA-256 is
`e7f080008230b47a12ed08bcd4cae692bedd13d6f6502e177576a783823bed75`.
Before integration, `HEAD`, local `master`, local `handoff/current`,
`origin/master`, and `origin/handoff/current` were all
`8cadc64c56d014a7f3fbd70d82ac5c041e63fed8`.

One early broad local filename inventory exposed protected fixture/support path
names only. No protected file was opened, content-searched, hashed, run, or
used. The metadata-only incident was contained immediately; all later reads
and test selection used exact protected-safe paths and nodes.

## Accepted implementation

### Durable session and event authority

Migration `m2n3o4p5q6r7` adds `bernie_booking_sessions` and
`bernie_session_events`. The runtime uses `DatabaseBernieSessionStore`; the
in-memory store remains only a pure statechart reference. Session append locks
the owned row, requires an exact expected revision, stores bounded allowlisted
structured evidence, hashes raw idempotency identities with HMAC/SHA-256, and
never persists the raw key or instruction text.

Incomplete expiry slides 24 hours from the latest accepted transition.
Completed expiry is 30 days from terminal completion. Batch-bounded cleanup
uses locked rows and `SKIP LOCKED`; deleting an expired session cascades event
detail only.

### Atomic confirmation and complete correlation

Command claims use PostgreSQL `INSERT ... ON CONFLICT DO NOTHING RETURNING`
followed by a row lock. One successful transaction owns the command claim,
current revalidation, `confirm_submitted` transition, appointment insert,
correlated audit insert, confirmation outcome, stored typed receipt, and
completed command result. An unexpected pre-commit failure rolls all of those
effects back. A new database session replay returns the stored response without
a second mutation or event.

Completed create commands have one target appointment, one direct audit link,
one reciprocal audit command id, response hash/body, and server-derived receipt
coordinates. Composite `(practice_id, id)` keys prevent otherwise same-practice
rows from grafting a foreign session, appointment, command, or audit identifier.
Session purge preserves the opaque minimal correlation stored on the retained
appointment/audit/command evidence.

### Tenant and audit controls

Authentication rejects a signed JWT practice claim that differs from the
current database user's practice, then sets transaction-local tenant context
from that database identity. The migration enables and forces RLS on sessions,
events, appointments, appointment command idempotency, and appointment audit.
Audit has read/insert policy paths plus a database trigger that rejects update
and delete with SQLSTATE `55000`.

The local application owner is a PostgreSQL superuser, so direct RLS acceptance
uses a temporary `NOLOGIN`, `NOSUPERUSER`, `NOBYPASSRLS` role in the disposable
database. This does not provision or claim a production runtime role.

### API Spine

The existing REST confirmation command remains the sole appointment mutation.
Bernie remains proposal-only; staff confirmation and backend revalidation are
mandatory. GraphQL remains read-only, async integration remains observational,
and no provider/client path receives write authority. The OpenAPI receipt adds
optional server-derived `correlation_id`, `audit_event_id`, and `session_id`
without treating a client draft correlation header as authoritative.

## Migration and database evidence

The migration source SHA-256 is
`0836c40fe51e9aa3d908967f4875174dfd04edcff6a7aa88f1476c7b0398113b`.

The disposable `gp_pms_stage2_migration` database passed:

1. upgrade from `l1m2n3o4p5q6` to `m2n3o4p5q6r7`;
2. downgrade back to `l1m2n3o4p5q6`;
3. re-upgrade to `m2n3o4p5q6r7`; and
4. `alembic check` with no model drift.

The preserved `gp_pms_dev` database was upgraded additively and was never
downgraded. Its final readback is 12 appointments, 9 audit rows, 4 completed
create command rows, 0 session rows, and 0 session-event rows. All four
historical completed create commands now have exact direct and reciprocal
same-practice audit correlation. The two new tables exist, all five scoped
tables have forced RLS, and the audit immutability trigger is active.

A truly empty database remains blocked in the older historical migration
`d4787...`, which attempts to truncate tables not yet created. That pre-existing
Alembic-history limitation predates and is outside this additive Stage 2
migration; it did not prevent the frozen upgrade/downgrade/re-upgrade gate from
the current accepted head.

The restricted-role acceptance script SHA-256 is
`2283c83413d12820a64c097e040566b6fd21974c01d363713d74e1a742ce15e0`.
Its fresh result is `status=pass`:

- missing tenant context returned zero rows on all five tables;
- own-practice context returned exactly one fixture row on every table;
- foreign rows were invisible and a foreign update affected zero rows;
- foreign insert failed with SQLSTATE `42501`;
- event-to-session, audit-to-appointment, audit-to-command,
  command-to-appointment, and command-to-audit cross-practice grafts each
  failed with SQLSTATE `23503`;
- audit update and delete each failed with SQLSTATE `55000`;
- own-practice insert/read succeeded;
- retained-session deletion removed its event detail but not the other
  practice's session; and
- the complete fixture/probe transaction and temporary role were rolled back.

## Gate decision

| Gate | Result | Accepted evidence |
|---|---|---|
| G1 Authority | pass | Approved bounded scope, protected boundaries, aligned refs, and fresh five-source receipts reproduce |
| G2 Migration | pass | Disposable up/down/up plus drift check; preserved additive upgrade and four exact historical backfills |
| G3 Restart | pass | Fresh SQLAlchemy/store instance reproduces retained snapshot and ordered event tail |
| G4 Revision concurrency | pass | Two independent requests from one revision yield one append and one typed stale-revision result |
| G5 Same-key concurrency | pass | Two independent confirmation transactions leave exactly one appointment, audit, ledger, outcome, and response |
| G6 Pre-commit failure | pass | Injected fault leaves no partial chain; clean retry succeeds once |
| G7 Post-commit retry | pass | Fresh database session returns stored receipt with no second mutation or event |
| G8 Correlation | pass | Command target, audit links, session coordinate, appointment, and receipt ids agree exactly |
| G9 Practice isolation | pass | Cross-practice HTTP rejection plus restricted-role RLS and five composite-FK graft rejections |
| G10 Audit immutability | pass | Direct update/delete rejected; insert/read remain tenant scoped |
| G11 Retention | pass | Sliding 24-hour incomplete and 30-day completed boundaries plus selective bounded purge reproduce |
| G12 Field/JWT protection | pass | Raw/oversized/free-text payloads rejected, raw key absent, practice mismatch fails 401, fixed JWT algorithm preserved |
| G13 API Spine | pass | REST remains sole mutation; GraphQL read-only; provider/async/client paths cannot bypass staff confirmation |
| G14 Regression/security | pass | Exact Stage 2, API Spine, security, Stage 1-compatible, Diary, Bandit, compile, syntax, readiness, and whitespace gates pass |
| G15 Scope | pass | No provider, protected, historical, PII, production, deployment, release, new action, GraphQL mutation, or autonomous confirmation opened |

No failed gate was overridden.

## Fresh verification

All PostgreSQL-loading pytest processes ran serially.

- final explicit Stage 2 runtime/database population: `100 passed`;
- API Spine artifact and drift population: `61 passed`;
- focused authentication, Diary security, receipt, and Ariadne security
  population: `46 passed`;
- Stage 1-compatible core population: `64 passed`;
- supervised booking/interpretation/receipt flow clean rerun: `63 passed`;
- API/accessibility/classifier population: `81 passed`; and
- all 115 explicit hash-bound Diary nodes expanded to `139 passed`, correctly
  labelled `route_intercepted_browser`.

The first wrapper invocation of the 100-test population reached its 60-second
outer process limit without a pytest failure; the identical command with a
120-second wrapper completed `100 passed` in 49.7 seconds. The first 63-node
supervised-flow attempt returned 62 passes and one five-second Enter-key mocked
receipt timeout. No source changed for that node; it passed immediately in
isolation and the complete identical population then passed 63/63. Both
observations are preserved and are not acceptance overrides.

Additional checks passed:

- Python compilation of the changed application, migration, script, and test
  surfaces;
- `node --check docs/diary/diary.js`;
- high-severity Bandit over the exact changed Python product, migration, and
  acceptance-script paths;
- `alembic check` on disposable and preserved databases;
- `git diff --check`;
- interpretation readiness remains
  `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, and `runtime_gate_decision=blocked`; and
- provider readiness remains `default_provider=disabled`,
  `live_provider_enabled=false`, and `provider_calls_performed=false`.

The handover archive contract initially exposed a pre-existing protected-head
drift: `AGENTS.md` already contained 588 lines against its longstanding
`<500` compact-live-handover assertion. Stage 2 had added only one row. The
duplicated historical chronology was mechanically compacted into its existing
verified ledger routes while preserving the current baton, allocation,
protected/user boundaries, and every test-required certification fact. The
live handover is now 436 lines and all five handover archive/authority tests
pass. This changes no product or Stage 2 acceptance meaning.

During protected integration, GitHub Advanced Security opened three mechanical
review threads: two `except` blocks needed explanatory comments and one test
import was unused. The exception handlers now state their bounded fail-safe
behavior and the unused import is removed. Focused durable-store/recovery tests
pass 9/9; the restricted-role database probe, exact two-item Bandit baseline,
historical-diary leakage lint, compilation, and whitespace checks pass again.
The review-fix pre-commit receipt passes at
`orchestration/agent_inbox/codex/bernie-stage2-review-fix-precommit-receipt.json`,
SHA-256
`451d12450f222ab5d497054c6da80c171e30975d4afca285ca8ad2bf812721da`.
The correction commit is
`84bf27ba3a6ea6f13814cbdc9aed03820fcc0125`; its pre-push receipt passes at
`orchestration/agent_inbox/codex/bernie-stage2-review-fix-prepush-receipt.json`,
SHA-256
`e7f080008230b47a12ed08bcd4cae692bedd13d6f6502e177576a783823bed75`.
The correction changes no product behavior, acceptance meaning, or authority.

## Exact critical hashes

| Artifact | SHA-256 |
|---|---|
| `app/models/bernie_sessions.py` | `a0d5d750aead77ea64c2d9375785f61b2612eee0b0c0119e318941365057f53e` |
| `app/models/appointments.py` | `0a6be841ffe69907a889163f111892fec289ddcc9d77dfa22e4f671dbf3a2c67` |
| `app/services/bernie/session_store.py` | `99ef407a346fa03a03c21a79583681e705497178b5fd8747f20f41fb28dbe2d3` |
| `app/services/appointment_idempotency.py` | `87212e458e65d291810bbb7d289e1151f2c53ac29cfdc73354bf16dbbc754cc8` |
| `app/routers/appointments.py` | `6246eb0799aea71cd3aa1fa2f1a78667ecb3f011c7e32e624c40f71cc5c40446` |
| `tests/test_bernie_stage2_durable_session_store.py` | `8e968be3a3b3f7ec74c473538fd8c5339eb1e40b80c686db481d67601f366ba8` |
| `tests/test_bernie_stage2_confirmation_recovery.py` | `ed1f4f49385986545127c213fed8856352d5927fd837b249629fef04b8880b22` |
| `tests/test_bernie_stage2_database_contract.py` | `7c876a738878cfc53f4efee163a41be4f47b413dd386ab739150495ed2566292` |

## Worker mix, integration, and next boundary

Sol owned planning, implementation, disposable database lifecycle, review,
recovery, acceptance, and integration preparation. This was a serial,
stateful transaction/migration tranche for which an external worker packet or
native subagent would not have saved a meaningful cycle. No provider call or
external prompt occurred.

The accepted implementation/evidence commit is
`cd3a9e056d8553da9ae339896dd28222b6554a57`; the final bounded review-fix branch
head is `7874271aea160e7539bf61cf238d919c9250dc61`. Protected PR 38 passed Python
Security, the Node/Office baseline, both CodeQL language analyses, and the
aggregate CodeQL gate on that exact head. GitHub Advanced Security automatically
resolved all three review threads after the fixes reproduced. No check,
conversation, alert, or branch policy was dismissed or bypassed.

PR 38 squash-merged to protected `master` as
`60940f27d50410172f4132416df5e8a20623815b` on 2026-07-19. Stage 2 therefore
returns final `stage2_pass`. The documentation-only closeout carrier records
that integration and is the sole remaining step before `master` and
`handoff/current` are operationally aligned.

The closeout-carrier integration and pre-commit receipts pass with the same
five-source binding:

- integration:
  `orchestration/agent_inbox/codex/bernie-stage2-protected-closeout-integration-receipt.json`,
  SHA-256
  `9b589c638bcabe034603df62972da9ea015b17a2e650453510b62d7727a95be8`;
- pre-commit:
  `orchestration/agent_inbox/codex/bernie-stage2-protected-closeout-precommit-receipt.json`,
  SHA-256
  `451d12450f222ab5d497054c6da80c171e30975d4afca285ca8ad2bf812721da`.

Even after integration, Stage 3 and every production/provider/PII/deployment
boundary remain a new Yuri decision.
