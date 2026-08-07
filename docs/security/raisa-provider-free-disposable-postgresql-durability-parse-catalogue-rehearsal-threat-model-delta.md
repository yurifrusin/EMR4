# Threat-model delta: disposable PostgreSQL durability parse/catalogue rehearsal

Date: 2026-08-07

Status: accepted for the bounded disposable rehearsal only

## Scope and assets

This delta covers one local disposable PostgreSQL 16 admission and catalogue
readback of the exact accepted inert durability SQL against four empty
authored-synthetic prerequisite tables. Protected assets are the parent bytes
and manifest, local Docker state, unrelated containers/images/volumes/networks,
the workspace, operational databases and credentials, application object
ownership, exact role/privilege/RLS boundaries, bounded evidence and complete
owned cleanup.

## Trust boundaries

Trust boundaries are repository contracts to the harness; the harness to the
local Docker CLI; host stdin to an owned container-local `psql`; accepted SQL to
PostgreSQL parser/catalogues; catalogue output to the evidence normalizer; and
captured container identity to destructive cleanup. No trust boundary reaches
an operational source, product service, provider product route or external
network.

## Threats and mitigations

| Threat | Mitigation | Residual risk |
|---|---|---|
| A missing image silently causes a registry pull | Exact local image inspect plus `--pull=never`; missing image is terminal. | A previously cached image's supply-chain provenance is not established by this gate. |
| Container reaches a network or host service | `--network=none`, no ports, no network joins, no Docker socket, and post-create configuration verification before SQL. | Docker daemon/host compromise is outside this tranche. |
| Rehearsal persists data or reads workspace files | PGDATA is tmpfs; no bind/named volume or workspace mount; SQL streams over stdin. | Container writable-layer implementation is trusted until exact removal. |
| Synthetic password becomes an operational secret | One fixed authored-synthetic initialization value in a networkless disposable container; never reused or treated as a credential; no trust auth. | Process metadata may expose the explicitly non-secret synthetic value locally. |
| Harness targets another container | Closed unique name, captured ID, two labels and random nonce; exact ID/name/labels/image/config reverified before cleanup. | If verification fails, an owned container may require human cleanup; unrelated state remains safe. |
| Broad cleanup removes user resources | Only exact captured-ID removal is callable; list, prune, prefix and label-query deletion are forbidden and hostile-tested. | Manual activity outside the harness is out of scope. |
| SQL artifact or manifest drifts | Exact path, accepted parent HEAD, planning baseline, canonical UTF-8/LF SHA-256, byte count, statement count and manifest assertions are verified before daemon contact. Git-managed Windows CRLF is the sole permitted normalization; lone CR or any other drift rejects. | Repository/Git compromise remains a higher-level control. |
| Prerequisite stubs overclaim application compatibility | Closed empty four-table contract with exact referenced columns/types and minimum keys; claim explicitly excludes full migration compatibility. | ORM/default/index differences remain for later integration. |
| Artifact partially installs after an error | Fixed invalid-copy runs first through psql `--file=-`, `ON_ERROR_STOP=1` and single transaction; it verifies database-local fabric absence and cluster-wide role absence before success is eligible. Plain stdin is forbidden because psql single-transaction mode requires `-c`/`-f`. | Nontransactional future DDL would require a new plan and must fail this contract. |
| A successful database masks rollback because roles are cluster-wide | Rollback database runs before success while accepted roles are absent; role absence is read from the cluster catalogue, not inferred from database-local schema absence. | The whole cluster is disposable and is removed after the succeeding catalogue rehearsal. |
| Function creation is mistaken for body correctness | Claim is parse/catalogue only; no function/trigger behavior is invoked and closeout must preserve that limitation. | Deferred PL/pgSQL statement planning may reveal errors in behavior rehearsal. |
| Catalogue normalization hides a privilege or expression difference | Exact fixed pg_catalog queries, stable ordered fields, PostgreSQL identity/deparse functions, counts and digests; mismatch pointers fail closed. | Server deparse stability is tied to PostgreSQL major 16. |
| Security-definer or RLS posture is widened | Exact owner, `prosecdef`, `proconfig`, role attributes, ACLs, forced-RLS and policy readback against manifest; unexpected objects fail. | Runtime `SET ROLE`/policy enforcement remains unproved. |
| Application tables are mutated | Empty row counts and owners checked before/after; no application DML in prerequisite or harness; no behavior calls. | Trigger installation itself references application tables by design. |
| Raw logs leak data or drive commands | Runtime has no patient/product data; evidence retains only allowlisted facts, SQLSTATE/stage/exit and capped digests; output never selects commands. | Local Docker diagnostics may still contain environmental implementation detail before redaction. |
| Timeout leaves a container running | Bounded calls enter `finally`; exact owned cleanup is attempted and must verify absence for pass. | Daemon failure can prevent cleanup and yields a non-pass human-inspection result. |
| Review worker executes the gate | Worker allocation forbids container start; only Sol owns the serial runtime and cleanup. | Sol implementation remains subject to independent exact-HEAD veto. |

## Residual risks deliberately deferred

Function and trigger behavior, RLS enforcement, concurrency, idempotency,
application transaction rollback, unknown commit, migration upgrade/downgrade,
complete real application-schema compatibility, operational key/credential
custody, watcher/source integration, performance, deployment, production and
incident response remain later gates.

## Forbidden openings

This delta grants no image pull/build/login, package installation, external
network, application database, Alembic migration, durable database object,
operational credential, source/outbox/feed/watcher/listener contact,
application/API/Diary change, behavior execution, patient/product/protected
data, provider product call, command/write authority, runtime wiring,
deployment, production, release, Pages rebuild or protected-ref movement.
`docs/branding/` and unrelated untracked artifacts remain preserved and
excluded.
