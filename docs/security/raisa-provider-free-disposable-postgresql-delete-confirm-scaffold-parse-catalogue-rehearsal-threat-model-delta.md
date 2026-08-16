# Threat-model delta — disposable PostgreSQL delete-confirm scaffold parse/catalogue rehearsal

Date: 2026-08-16

Timestamp: 2026-08-16T10:31:22+10:00 (Australia/Brisbane)

Source HEAD: `274c42adf575f7f07aea759e79a6bd3f2ec25e54`

## Scope

This delta covers exact offline lowering and one empty-instance installation of
migration `x3y4z5a6b7c8` in an owned networkless tmpfs PostgreSQL 16 container,
allowlisted catalogue inspection, zero-row proof and verified cleanup.

## Threats and controls

| Threat | Frozen control |
|---|---|
| An operational database is reached | No host URL or port exists; SQL goes only through exact-ID `docker exec` to one networkless owned container. |
| Docker pulls or contacts a registry | Exact local image inspection precedes `--pull=never`; absence is terminal. |
| Workspace or durable data is mounted | No bind or named volume; the data directory is one container-local tmpfs. |
| Cleanup removes another resource | Reverify exact ID, name, image, labels, containment and bounds; remove only the captured ID; otherwise refuse. |
| Ambient Alembic configuration selects a database | Offline range generation gets one fixed synthetic dialect URL and is checked to make no connection. |
| Another migration enters the proof | Exact range `w2x3y4z5a6b7:x3y4z5a6b7c8`, source hash, generated tokens and resulting head are mandatory. |
| Synthetic prerequisites overstate compatibility | Create only minimum empty referenced columns/constraints and label the claim parse/catalogue representation, not full-chain or product compatibility. |
| Migration partially installs | Stream through `--file=-`, `ON_ERROR_STOP=1` and `--single-transaction`; any error fails the run. |
| Catalogue names hide wrong object semantics | Bind exact schema, type, nullability, defaults, constraints, index, function attributes/definitions and trigger definitions; reject extras in the owned object families. |
| The migration silently manufactures authority | All four authority/receipt/audit relations must remain at zero rows; no provisioned grant or behavior probe is admitted. |
| Trigger behavior is inferred from representation | The claim is explicitly representation-only; behavior remains a later tranche rather than being inferred. |
| Raw logs disclose details | Evidence retains allowlisted object names, counts, lifecycle states and digests only. |
| Database representation is mistaken for route safety | No model/service/route/API/UI edit or invocation occurs; the claim excludes application transaction behavior. |
| Risk-tier review expands back into review stacking | Tier 2 permits exactly one final independent veto after deterministic admission and occupied evidence, with no intermediate review chain. |

## Residual risks

The rehearsal does not prove the full historical migration chain, full
application-schema compatibility, DML behavior, nested trigger-depth semantics,
grant generation changes, duplicate inserts, update rejection, downgrade after
use, service/ORM integration, lock waits, concurrency, restart, unknown commit,
performance, route safety or production operations.

## Authority boundary

No existing/product database, row-bearing fixture, durable storage,
route/application command, patient/product/protected data, provider/ADC/
credential/browser authorization, external network, watcher/event, deployment,
production, release, Pages or protected-ref action is opened. `docs/branding/`
and every unrelated untracked path remain excluded.
