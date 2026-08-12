# Threat-model delta — disposable PostgreSQL status-confirm scaffold parse/catalogue rehearsal

Date: 2026-08-12

Source HEAD: `163e0403cc3f18ebb2fbd0e47e14d01abf2554b6`

## Scope

This delta covers one owned networkless tmpfs PostgreSQL 16 container, exact
offline Alembic lowering, catalogue inspection, rolled-back authored-synthetic
invariant probes and verified cleanup.

## Threats and controls

| Threat | Frozen control |
|---|---|
| An operational database is reached | No host URL or port exists; all SQL goes through exact-ID `docker exec` to one networkless owned container. |
| Docker pulls or contacts a registry | Exact local image inspect precedes `--pull=never`; absence is terminal. |
| Workspace or durable data is mounted | No bind/named volume and one container-local tmpfs only. |
| Cleanup removes another resource | Reverify exact ID, name, image, labels, containment and bounds; remove only captured ID; otherwise refuse. |
| Ambient Alembic configuration selects a database | Offline range generation receives one fixed synthetic dialect URL and is separately checked to make no connection. |
| Another migration enters the proof | Exact range `v1w2x3y4z5b6:w2x3y4z5a6b7`, source hash and resulting head are mandatory. |
| Synthetic prerequisites overstate compatibility | Create only minimum referenced pre-migration columns and label the claim as parse/catalogue/invariant evidence, not full application-schema compatibility. |
| Migration partially installs | Stream through `--file=-`, `ON_ERROR_STOP=1` and `--single-transaction`; any error fails the run. |
| Trigger/version behavior is inferred from text | Catalogue binding plus fixed rolled-back default/increment/overflow probes test the database invariant directly. |
| Invalid v1 receipt bypasses constraints | Exact bad version/digest/adjacency probes must fail with SQLSTATE 23514. |
| Probe values escape | Fixed authored-synthetic values only; rollback where possible and unconditional container removal. |
| Raw logs disclose detail | Evidence retains allowlisted facts, SQLSTATEs and digests only. |
| Database behavior is mistaken for route safety | No app/route/helper/audit invocation; claim boundary explicitly excludes command behavior. |

## Residual risks

The rehearsal does not prove the full historical migration chain, complete
application schema compatibility, service/ORM integration, real transaction
composition, lock waits/concurrency, restart, unknown commit, downgrade after
real use, performance or production operations.

## Authority boundary

No existing/product database, durable storage, route/application command,
patient/product/protected data, provider/ADC/credential/browser authorization,
external network, watcher/event, deployment, production, release, Pages or
protected-ref action is opened. `docs/branding/` and unrelated untracked paths
remain excluded.
