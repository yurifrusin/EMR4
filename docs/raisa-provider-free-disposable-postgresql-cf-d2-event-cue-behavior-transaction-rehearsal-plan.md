# Provider-free disposable PostgreSQL CF-D2 event and cue behavior/transaction rehearsal plan

Date: 2026-08-13

Timestamp: 2026-08-13T20:21:19+10:00 (Australia/Brisbane)

Status: `frozen_for_six_group_serial_postgresql_16_execution`

Planning baseline: `6e5fedb0fc54dff5d82a098bfbcad1bef0bccb3c`

Accepted parse/catalogue source: `579e9e0e86bd92469d82eb1199e8b3120808844e`

Target result: `raisa_provider_free_disposable_postgresql_cf_d2_event_cue_behavior_transaction_pass`

Reasoning level: High. The parent architecture already fixes the five
protocols and authority ceiling; this tranche is their bounded mechanical
serial execution, not a new runtime or product decision.

## Objective

Exercise only the five accepted CF-D2 transaction protocols against the exact
accepted 12,022-byte PostgreSQL 16 artifact in one newly owned, networkless,
portless and tmpfs-backed server:

1. `admit_terminal`;
2. `coalesce_pending`;
3. `advance_contiguous_checkpoint`;
4. `record_dispatch_attempt`; and
5. `record_reconciliation`.

Use only fixed authored-synthetic digests, opaque IDs, enums, booleans and
positive positions. Observe committed effects, refused-transition
non-effects, deliberately induced transaction rollback and uncontended lock
footprints, then destroy the exact owned server.

Events and cues remain acceleration hints. They are not current Diary truth,
Context Frames, confirmation evidence, command receipts or command authority.
Reconciliation booleans are synthetic claims used to exercise the row truth
table; they do not prove a real authorisation decision or fresh product read.

## Exact source bindings

| SHA-256 | Path |
|---|---|
| `3eebbe132b195ccab2f00283ad20f04c521fa6116bb30d0f38ab49158db1ebd6` | `orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering/event-cue-schema.sql.inert` |
| `ff72cb2b6458193fb723b19209ac0ca487d3fdda5846d43ccdfafb6986957f64` | `orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture/representation-contract.json` |
| `6b410a707279a093e2874eb3e22eeef1ab1f8b89c196f7864d0132da59ff3ef1` | `orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal/admission-contract.json` |
| `e524b40c23e3735a7a94f8d5d6a790a66857718ee85e22eb736d2a4991c4025f` | `docs/api-spine/async/durable-diary-event-cue-observability.yaml` |
| `aa89d239cff54635488224e1199c40233c5a571e92724cf84cafa9eb7079aa2f` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal/rehearsal-contract.json` |
| `f1bb8a80541a6345d0258a528426b37f00caeb5cefa1841536849e34e1d4ea3d` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal/provider-free-parse-catalogue-evidence.json` |
| `ca66a12388b9677dcd9f5c3f13e4ca680d130cd001c321bd5dfa7b0e30497ca8` | `orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering/inert-ddl-manifest.json` |
| `6824661959101f332611db9f0edaf28aa59d5cc63403a101499fb88379d7eb5e` | `docs/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal-closeout.md` |
| `161a48f275163fc5ad16f07a02ed00a54d26221859591e50cb27ea14ebace2c9` | `orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-parse-catalogue-sol-acceptance.md` |

The harness accepts no caller-selected SQL, fixture, database URL, image,
container, output path or scenario. It installs the exact artifact unchanged;
all behavior statements are fixed repository constants and never become a
migration, route or reusable database API.

## Six fixed serial scenario groups

### 1. Admission identity, fencing and atomic rollback

- Current generation admits one `cue_required` terminal position together
  with one pending obligation and advances the checkpoint before delivery.
- An exact duplicate reuses the original receipt and obligation with an
  unchanged canonical state digest.
- A divergent duplicate and stale generation fail with unchanged state.
- A forced error after obligation mutation but before receipt completion rolls
  back the whole transaction; neither range extension nor receipt survives.

### 2. Pending-only coalescing boundaries

- An adjacent pending obligation with identical partition, epoch, consumer and
  reason extends exactly once.
- A different reason creates a separate obligation.
- Once delivery is recorded, an adjacent same-reason position creates a new
  pending obligation and cannot mutate the delivered range.
- Gap, overlap and cross-reason extension candidates fail without mutation.

### 3. Contiguous checkpoint movement

- An out-of-order terminal receipt leaves the checkpoint at explicit `none`.
- Filling the gap advances across the complete contiguous run.
- Suppressed and rejected terminal positions require no obligation.
- Every `cue_required` position must reference an obligation whose range
  covers it, but delivery is deliberately not a checkpoint prerequisite.
- Epoch crossing and uncovered required-cue movement fail without mutation.

### 4. Dispatch ordering and rollback

- The current generation records a failed ordinal 1 with one stable
  allowlisted failure class while the obligation remains pending.
- A forced failure after inserting delivered ordinal 2 but before completing
  its state transition rolls back both changes.
- A fresh ordinal 2 then commits with the obligation becoming delivered in the
  same transaction.
- A stale generation, skipped ordinal and delivered-to-pending regression fail
  without mutation; a repeated delivered request reuses the existing result.

### 5. Delivered-only reconciliation and rollback

- A pending obligation and a failed dispatch cannot reconcile.
- A forced failure after inserting a valid reconciliation rolls it back.
- A delivered attempt permits one truth-table-valid reconciliation.
- An exact duplicate reuses the original reconciliation identity; a conflicting
  second result fails without mutation.
- Invalid scope/fresh-read/display combinations fail closed. No receipt can
  claim future freshness or mutate source truth.

### 6. Uncontended lock footprints

Inside rollback-only probe transactions, fixed `SELECT ... FOR UPDATE` paths
must expose the required granted relation locks for each protocol:

- admission/checkpoint: partition, position/receipt, checkpoint and relevant
  obligation rows;
- coalescing: the selected pending obligation;
- dispatch: partition, obligation and existing attempt sequence; and
- reconciliation: obligation, delivered attempt and existing reconciliation.

Only the required target-relation lock/mode subset is admitted. System/index
locks are ignored. This proves the frozen statements acquire their intended
uncontended locks; it does not prove contention, fairness, deadlock behavior or
multi-session concurrency.

## Owned environment

The containment profile remains the accepted parse/catalogue profile with a
distinct name, label and database. Only locally cached
`postgres:16-bookworm` at exact image ID/repo digest is eligible;
`--pull=never`, `--network=none`, no published port, no bind or named volume,
one tmpfs data directory, capped CPU/memory/processes/time and exact-ID cleanup
remain mandatory. Missing Docker, daemon or exact image is
`environment_unavailable` without fallback.

The exact artifact is installed once. Scenario rows are reset only inside the
owned disposable schema between fixed groups. No existing database, source,
workspace file, Docker network, Docker volume or unrelated container is read,
changed or removed.

## Acceptance

- Fresh five-source receipt and an `in_progress` active-operation latch pass.
- Contract/evidence schemas validate, exact source hashes pass and at least 64
  independent closed-contract mutations fail.
- The exact artifact installs and its empty catalogue baseline is re-admitted.
- All six scenario groups and all five named protocols pass their exact
  effect/non-effect/rollback/lock observations.
- Every forced rollback has identical before/after canonical state digests.
- Every denied transition has identical before/after canonical state digests.
- Final evidence contains only minimized hashes, counts, fixed result codes and
  authored-synthetic state digests.
- Exact captured-ID cleanup passes even after failure.
- Focused tests, CF-D2/API Spine lineage, latch/baton/Compass checks, Ruff,
  maintained-source compilation, canonical fast tests, JavaScript syntax and
  Git whitespace pass serially where required.
- Protected refs and every unrelated untracked file remain unchanged.

Evidence is labelled
`authored_synthetic_provider_free_disposable_postgresql_16_serial_behavior_transaction`.
It proves only this fixed single-server serial behavior slice.

## Recovery

Mechanical harness, fixed SQL, expectation or evidence-shape defects may
receive bounded evidence-backed repair inside this exact envelope, always with
a fresh owned container for an occupied rerun. Preserve each failed evidence
artifact before retry. A semantic conflict with the five accepted protocols,
an unverified cleanup target, any need for another database/source or any need
to open concurrency/restart/runtime/product authority stops for genuine user
attention.

## API Spine classification

This is an async event/cue contract rehearsal. It adds no GraphQL mutation,
REST/OpenAPI command, route, integration principal, product idempotency record
or audit authority. The future consumer still performs a fresh authorised
read; every consequential REST command still rechecks current authority and
source truth inside its own mutation transaction.

## After a pass

Close CF-D2's narrow serial database foundation and run a fresh Compass/baton
orientation before selecting the next dependency-satisfied product tranche.
That orientation is read-only and receives no watcher, source, persistence,
product, provider, command, deployment or protected-ref authority in advance.

## Closed surfaces

No protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient identity/client/channel, existing database/source,
watcher/listener/worker/queue runtime, operational persistence/retention,
concurrency, restart/crash/unknown commit, real delivery, provider/ADC,
credential/IAM/external network, product route/read, executable product tool,
product command/write, deployment, production, release, Pages or protected-ref
action is opened. `docs/branding/` and every unrelated untracked file remain
preserved; staging is explicit-path only.
