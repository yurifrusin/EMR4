# Threat-model delta — CF-D2 event and cue disposable PostgreSQL behavior/transaction rehearsal

Date: 2026-08-13

Timestamp: 2026-08-13T20:21:19+10:00 (Australia/Brisbane)

Status: `provider_free_networkless_tmpfs_authored_synthetic_serial_only`

## Assets protected

- source-owned Diary truth and current command authority;
- exact CF-D2 protocol meaning and the parse/catalogue source chain;
- existing databases, Docker resources and unrelated worktree content;
- protected, historical Diary, patient, product and credential data; and
- the distinction between serial transaction evidence and a durable runtime.

## New boundary

The tranche opens fixed authored-synthetic row writes and transaction-local SQL
inside one newly created, networkless, tmpfs PostgreSQL 16 server. It opens no
existing database/source, port, external network, migration, watcher,
application route, provider or product data.

## Threats and controls

| Threat | Frozen control |
|---|---|
| Existing data is reached | No host URL or published port; all SQL targets the exact captured owned container over its local Unix socket. |
| Registry or external network contact | Exact cached image identity; `--pull=never`; `--network=none`; absence or drift fails without fallback. |
| Behavior SQL becomes a generic execution tool | Fixed repository constants, no caller SQL/fixture/path/database arguments, `shell=False`, bounded output and time. |
| Partial terminal admission survives | Receipt/obligation/checkpoint share one transaction; a forced post-write failure must restore the exact pre-state digest. |
| Coalescing mutates a delivered or unrelated cue | Exact partition/epoch/consumer/reason/adjacency/pending predicates plus locked-row verification. |
| Checkpoint crosses a gap or uncovered cue | Next-position-only contiguous loop; required cues must reference a covering obligation; denied movement preserves state. |
| Stale ownership writes | Current partition generation is locked and compared inside admission/dispatch transactions. |
| Dispatch history forks or regresses | Locked obligation, exact next ordinal, immutable attempt rows, stable failure class and no delivered-to-pending transition. |
| Reconciliation claims authority or freshness | Only the accepted synthetic truth-table fields are stored; acknowledgement means one read attempt, never future freshness; no source/product access exists. |
| Lock evidence is overstated as concurrency | Only granted uncontended relation-lock subsets are claimed; contention, fairness, deadlocks and multi-session behavior remain closed. |
| Raw rows leak into evidence | Evidence retains fixed result codes, counts and canonical digests, not raw row values or PostgreSQL logs. |
| Cleanup affects another object | Exact captured ID, name, image, labels and full profile are reverified before exact-ID removal; prefix search/prune is forbidden. |
| Worktree collateral is staged | Explicit-path staging only; `docs/branding/` and every unrelated untracked path remain excluded. |

## Residual risk

The locally cached image remains a pre-existing supply-chain dependency. A
single serial server cannot establish behavior under races, failover, crash or
unknown commit. Anonymous transaction blocks demonstrate these exact scripts,
not a production API or migration. External authority and fresh-read truth are
deliberately untested.

If exact cleanup ownership cannot be reverified, automated deletion stops and
the captured ID becomes a human-attention condition.

## Closed surfaces

No protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient identity/client/channel, existing database/source,
watcher/listener/worker/queue runtime, operational persistence/retention,
concurrency, restart/crash/unknown commit, provider/ADC,
credential/IAM/external network, product route/read/tool/command/write,
deployment, production, release, Pages or protected-ref authority is opened.
