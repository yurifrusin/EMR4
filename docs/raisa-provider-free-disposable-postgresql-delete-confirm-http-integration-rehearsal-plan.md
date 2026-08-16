# Provider-free disposable PostgreSQL delete-confirm HTTP integration rehearsal plan

Date: 2026-08-17

Timestamp: 2026-08-17T07:05:13.9032501+10:00 (Australia/Brisbane)

Status: frozen

Revision: 2

Source HEAD: `341d89b9a70c85f54247de364baf842b84543c8d`

Accepted HTTP source: `c7a01edd96ebabf3ea2c07be89a5b405c9629853`

Accepted database behavior source: `49dd2aaa72877adb844da4d0d5d5bb28039c90c8`

Reasoning level: Extra High — authenticated database write boundary, tenant
isolation and public/private receipt integration

## Objective

Exercise the canonical
`POST /api/v1/appointments/proposals/delete/confirm` route and its hidden
compatibility alias through the accepted delete product adapter and physical
transaction against one owned, disposable PostgreSQL 16 server containing only
fixed authored-synthetic rows.

Preexecution inspection proved two closed integration preconditions that the
route-only and unmounted database tranches could not observe together:

1. the route-local command encoder omitted the adapter-required `kind=delete`
   discriminator, so a valid route-produced proposal stopped as stale before a
   command session; and
2. the fresh command-owned session did not establish transaction-local
   `app.current_practice_id`, so forced RLS would correctly hide every target.

This tranche repairs only those two seams: route producer helpers delegate to
the accepted adapter canonicalizers, and the physical transaction sets the
already authenticated practice locally after transaction isolation begins and
before any authority or target read. The adapter, composition, migration,
schemas, public envelope, raw compatibility DELETE and command meaning remain
unchanged.

## Frozen source boundary

Hashes are strict UTF-8 canonical-LF SHA-256 with bare-CR rejection. No
repository-wide discovery is permitted after this freeze. Protected evidence
paths remain excluded and may not be enumerated.

### Narrow editable preconditions

| SHA-256 | Exact source | Permitted change |
|---|---|---|
| `9b51623969bfdc657d6af2fda21b36a5ecb4973a3d1146e32460d8ebdaa7634e` | `app/routers/appointments.py` | make delete command, freshness and signed-payload production delegate to the accepted adapter helpers; no route, schema, response or raw DELETE change |
| `8e0f0e06471560b328e5ab7af6cc9981c20ca4a58ec9eec74dbd412979f85533` | `app/services/appointment_delete_physical.py` | set the authenticated practice with transaction-local `set_config` after isolation begins and before the first read; no lock, authority, receipt or effect change |
| `a77b80a81aff7ed18226d31c39413f4287cf44f794152ed2b4001f52b8ba4db2` | `tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py` | add the exact producer-to-adapter regression guard |
| `a12afe1de2ed6b311430f5d81c3098237b12068e0a4550ada60d7619366ad8e4` | `tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py` | add exact transaction-local tenant-context ordering and value guards |

### Read-only semantic and lifecycle inputs

The exact read-only bindings are frozen in
`orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal/rehearsal-contract.json`.
They cover the request dependency/authentication seam, schemas, adapter,
composition, physical models and migration, API Spine/Diary identity, accepted
route and database closeouts, the accepted delete database harness/contract and
the status-confirm HTTP/PostgreSQL lifecycle pattern. Any changed binding stops
before Docker or SQL.

## Exact repairs

1. Route delete command serialization, freshness calculation and signed
   evidence payload construction call the accepted public adapter helpers.
   This removes the duplicate canonicalization that omitted `kind=delete`.
2. `delete_confirm_locked_transaction` executes transaction isolation first,
   then `set_config('app.current_practice_id', authenticated_practice, true)`,
   then creates its cumulative deadline and performs the existing lock plan.
   The practice is the server-owned, UUID-normalized value already passed by
   the authenticated adapter, not a client-selected field.
3. A provider-free pure regression proves a route-produced proposal reaches
   exact verified/exact pre-command ingress. A physical regression proves
   tenant context is local, precedes the first user/appointment/grant read and
   cannot be omitted or made session-persistent.

Revision 2 records two same-boundary facts exposed by the first focused run.
The prepared confirmation's nested proposal must carry the same signed evidence
that the accepted adapter explicitly compares with the top-level evidence.
The historical physical-scaffold test must retain its old API Spine hash as
historical contract evidence while recognizing the already accepted current
route-convergence API hash through this tranche's exact binding; it must not
rewrite the historical scaffold contract or restore obsolete API content.

## Owned disposable lifecycle

- cached `postgres:16-bookworm`; pull policy `never`;
- one labelled `--internal` Docker network and one labelled tmpfs-backed
  container with no published port, bounded memory, CPU and PID resources;
- one fixed in-process `127.0.0.1` relay into container-local PostgreSQL;
- the exact accepted delete scaffold installed over the authored-synthetic
  bootstrap;
- one non-superuser, non-`BYPASSRLS` application role;
- forced RLS on users, appointments, practitioners, patients, appointment
  types, capability grants, command receipts and delete audit;
- real FastAPI routing through `TestClient`, overriding only `get_db` and
  `get_command_session_factory` with fresh sessions bound to the owned server;
- locally minted JWTs for fixed authored-synthetic users; and
- engine disposal, relay stop, captured-container removal, empty-network
  reverification, captured-network removal and exact-ID absence proof.

No existing or product database is read or modified. No Docker resource is
removed unless its captured ID, exact name, nonce, label, image and network
ownership revalidate.

## Frozen serial scenarios

| ID | Required proof |
|---|---|
| `DHI-S01` | authenticated proposal is non-mutating and carries the canonical endpoint, valid signed evidence and one positive database-version binding that passes exact adapter ingress |
| `DHI-S02` | canonical confirm commits one cancellation, adjacent version, waiting-area clearing when present, correlated delete audit and complete private v1 receipt, while HTTP returns only the distinct canonical public envelope |
| `DHI-S03` | hidden compatibility alias reaches the same handler, adapter and transaction behavior with no second implementation |
| `DHI-S04` | simulated lost first response followed by same-key retry returns byte-identical public HTTP bytes, retains byte-identical private stored bytes and creates no second effect |
| `DHI-S05` | missing, blank and conflicting idempotency keys return exact typed outcomes with no unauthorized second effect |
| `DHI-S06` | missing/invalid authentication, inactive user and non-mutating role fail before any command effect |
| `DHI-S07` | a cross-practice target returns the closed unavailable result with no row disclosure or effect |
| `DHI-S08` | absent, malformed and tampered version bindings stop before command-session construction; a valid-but-stale binding opens no effect after a database-owned version advance |
| `DHI-S09` | missing or altered `waiting_area_cleared` acknowledgement blocks atomically and preserves the waiting-area row |
| `DHI-S10` | default absence of the normalized cancel grant and explicit post-proposal revocation both return current-authority denial with zero appointment, audit or receipt effect |
| `DHI-S11` | disabling the disposable adjacent-version trigger for one fixed probe makes receipt/effect completion return 503 and roll back appointment, audit and receipt; the trigger is restored before continuation |
| `DHI-S12` | canonical OpenAPI visibility, hidden alias identity, Diary endpoint, strict public/private byte separation and unchanged raw DELETE inventory remain aligned |

The run is serial. It does not claim concurrent route behavior, crash/restart or
unknown-commit recovery.

## Evidence boundary

The exact evidence label is `live_local_backend_postgres`. Released evidence
may contain only scenario IDs, decisions/codes, HTTP status classes, counts,
versions, hashes, endpoint names, containment booleans, RLS/catalogue facts and
cleanup results. It may not retain JWTs, bearer values, HMACs, secret material,
request/response bodies, private receipt bytes, SQL, connection URLs,
passwords, container/network/runtime IDs, synthetic row values, unrestricted
database output or exception text.

## Outputs and worker allocation

Sol owns the plan, threat boundary, two product-source repairs, source
admission, live serial execution, recovery, acceptance, Continuity/Compass and
publication.

After the two source repairs pass their pure/static gates, DeepSeek V4
Flash/high receives one bounded separable mechanical package for:

- `scripts/raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal_plan.py`; and
- the released/failure evidence writers under the matching Continuity
  directory.

DeepSeek receives no plan, acceptance, live database, integration or Git
publication authority. The occupied database run remains Sol-serial. Gemini
3.7 Flash/high is reserved for one fresh exact-candidate veto only after all
deterministic evidence and cleanup pass. Native subagents are declined by
current developer policy. No parallel live package exists because the route,
application sessions and one disposable database share one mutable lifecycle.

## Acceptance

Pass requires:

- all frozen pre-edit and read-only hashes;
- the two exact precondition regressions;
- all twelve serial scenarios;
- canonical and alias routes sharing one handler and one accepted adapter;
- transaction-local tenant context with no pooled-setting residue;
- atomic current-authority, cancellation, audit and receipt behavior;
- byte-identical replay of both public projection and private stored receipt,
  with public bytes distinct from and unable to expose private bytes;
- at least 120 hostile contract mutations rejected;
- exact application-role, RLS, migration-head and trigger/constraint catalogue
  facts;
- focused route/physical/integration tests, API Spine/Diary checks, canonical
  fast profile, Ruff, maintained-source compilation and Git whitespace;
- exact owned Docker cleanup and independent label-filtered postflight; and
- one fresh clean Gemini 3.7 Flash/high veto on the exact unchanged candidate.

## Claim and recovery boundary

Passing proves only authored-synthetic local HTTP/backend/PostgreSQL integration
for the existing delete-confirm family and its two narrow integration
preconditions. It does not prove raw DELETE convergence, visible Diary/UI
behavior, concurrency beyond the accepted row locks, restart, crash,
unknown-commit recovery, performance, product data, deployment or production.

One mechanical DeepSeek defect may receive at most one bounded same-lane
correction. A need to alter adapter/composition/schema/public meaning, migration
DDL, cancellation semantics, raw DELETE, product data, provider posture,
deployment or protected refs stops the candidate for Sol diagnosis. Routine
in-scope failures do not create a ceremonial Yuri gate.

No patient, clinical, real-person, operational product, historical-diary or
protected data; provider call; ADC, credential or IAM action; browser;
external network; reusable capability; UI; deployment; production; release;
Pages rebuild; or protected-ref movement is authorised. `docs/branding/` and
all unrelated untracked files remain preserved. Staging is explicit-path only.
