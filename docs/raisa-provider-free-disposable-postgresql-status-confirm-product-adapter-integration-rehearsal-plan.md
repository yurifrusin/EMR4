# Provider-free disposable PostgreSQL status-confirm product-adapter integration rehearsal plan

Date: 2026-08-13

Timestamp: 2026-08-13T11:03:40+10:00 (Australia/Brisbane)

Status: frozen

Revision: 3

Task HEAD: `73d41c6f9da2d82970310f475d1858f311bded38`

Accepted adapter source: `b728b903c99fa35f231df04ba68263533261121a`

Reasoning level: material database/RLS integration evidence — Extra High

## Objective

Exercise the exact accepted status-confirm product adapter and physical
transaction seam against one newly owned, disposable PostgreSQL 16 database.
The tranche remains off-route. It may add the minimum authored-synthetic
practice, user, practitioner and appointment rows needed to prove
transaction-local tenant context, two fresh actor checks, one complete atomic
status/audit/private-receipt write, adjacent version, rollback and exact replay.

The plan authorizes only its owned disposable authored-synthetic database
write/readback/cleanup. It opens no product/runtime command or database.

## Frozen source boundary

After this freeze, existing-source reads, imports and hashes are limited to the
following exact non-protected files. The accepted product adapter is the only
existing application source that may receive a narrow repair; every other
existing source is read-only.

| Existing source | SHA-256 |
|---|---|
| `app/services/appointment_status_product_adapter.py` | `4c6351352a0c3af9f392f4cfb424db926b9acb475cdf4864b4c46ec8fb65963e` |
| `docs/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-closeout.md` | `ff975620aa9dc531b04389f89963759a5decc0e80ab853d6688e5501924e3366` |
| `app/services/appointment_status_composition.py` | `42221f72df9290b663b81bd8925afc448d4857733a8029914e09e0b905e9774a` |
| `app/services/appointment_status_physical.py` | `4ab9d0ff3816d85d7eb374e97fec7618e0b922354b104766b2898b0989e56f1b` |
| `app/models/appointments.py` | `d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915` |
| `app/models/tenancy.py` | `6be0d9ab4fc33a8709268d2f2a4550b6063e3f3e4188349c5fe3b0b6acd14431` |
| `app/schemas/appointments.py` | `d721c94dece8a60fec9f36a542a3c9cc3e6964ef394da8d76f099332c1c6806d` |
| `app/services/bernie_turn_evidence.py` | `e72e4052ce4f9bc2d3e6f308401a439b84987422b4003ddfbed34059a98cd467` |
| `scripts/raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal.py` | `875afd5bdfcac9e8cdbc5deb000645c638b68d1eb2239d3cd55f130366c08bd9` |
| `orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-behavior-transaction-rehearsal/rehearsal-contract.json` | `bdc848e2033715eb110f3d55425e06894abbc3a492c0a35fea0a2daf2c55d19b` |
| `orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.json` | `00b094830c5f1a0cea19be40cb6761ed5350b6b2ed3fecb53e37ae255333eadd` |
| `alembic/versions/w2x3y4z5a6b7_add_status_confirm_physical_scaffold.py` | `bfa72b627061b8e477903ec9fc2cfbb35a4970b26ab7115db18c3daef1d3696c` |
| `app/routers/appointments.py` | `59c2923f9cb4dcad75e727fd7614231a0ac5888d30a79f3d1b7949e4fb483ddb` |
| `docs/api-spine/openapi/appointment-commands.yaml` | `c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6` |
| `tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter_plan.py` | `5b9731262c028eea9a741174c80adf9fd722d2531f0c5ac8b5b0135ebe9ec0f4` |

No repository-wide or directory-wide discovery is permitted after freeze.
Protected evidence paths remain excluded and must not be enumerated.

## Exact owned outputs

- this plan and its threat-model delta;
- the narrow practice-context repair in
  `app/services/appointment_status_product_adapter.py`;
- one closed contract, contract schema, evidence schema and generated evidence
  under the matching continuity directory;
- `scripts/raisa_provider_free_disposable_postgresql_status_confirm_product_adapter_integration_rehearsal.py`;
- two focused test files; and
- one narrow predecessor-lineage test repair in
  `tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter_plan.py`
  so its immutable evidence remains checked against accepted source
  `b728b903c99fa35f231df04ba68263533261121a` after this descendant changes the
  adapter; and
- the eventual timestamped closeout, Sol acceptance, Yuri summary, receipt
  pairs and Continuity/Compass updater/test.

No migration, model, schema, composition, physical seam, route or public API
source may change.

## Narrow adapter repair

The fresh command session starts with no tenant setting. The physical seam
locks the exact practice before it invokes `practice_is_active`, then locks the
appointment. Therefore the product adapter must make its injected
`practice_is_active` callback set transaction-local
`app.current_practice_id` before returning the exact practice check. This is
the earliest existing in-transaction callback and ensures the appointment,
user, idempotency and audit operations all occur under the tenant setting.
The existing current-authority callback must continue to restore the same local
setting immediately before each user re-read. Session-level setting and nested
transactions are forbidden.

The admission/kernel packet remains canonical JSON and therefore carries its
target UUID as text. The PostgreSQL ORM reloads the physical target as a UUID.
The product adapter must wrap only the injected physical transaction factory
and normalize that already-admitted target text to an exact UUID before the
physical idempotency comparison. It must not change the signed packet, request
digest, idempotency key or any other physical argument. Invalid target text
fails closed before transaction entry.

## Disposable runtime

Reuse, without editing, the already accepted Docker lifecycle and fixed
loopback-relay helpers from the frozen behavior/transaction harness. Resolve
the repository interpreter and local `docker.exe`; use only the cached
`postgres:16-bookworm` image with `--pull=never`. Create one uniquely labelled
Docker `--internal` network and one uniquely labelled container, no published
port, tmpfs-only PostgreSQL data, no volume/workspace/Docker-socket mount, one
CPU, 512 MiB, 128 processes, no restart and the accepted 90/30/300-second
bounds.

The only host connection is the accepted in-process IPv4 `127.0.0.1` dynamic
relay to the exact captured container ID using argv, `shell=False`, and the
frozen literal container-side `/dev/tcp` command. No registry access, external
routing, global Docker listing, pull, build, login, prune or unrelated removal
is permitted.

## Minimum database and RLS surface

Install the accepted physical scaffold and selected correlation constraints,
then add only mapped `users` and `practitioners` columns required by the product
adapter and public projection. Add exact practice-scoped row-level policies to
appointments, users, practitioners, idempotency and audit, with forced RLS for
the disposable owner. Policies compare `practice_id` only with
`current_setting('app.current_practice_id', true)` parsed as UUID. Practices
remain selectable by their exact server-owned primary key so the callback can
establish tenant context before the appointment lock.

All fixtures use fixed opaque UUIDs and closed authored-synthetic administrative
values. There is no patient, real person, clinical narrative, product-derived
value, provider input or unrestricted row capture.

## Frozen serial scenarios

Exactly twelve independently seeded scenarios are required:

| ID | Expected proof |
|---|---|
| `PGA-S01` | Booked-to-Confirmed commits one mutation, one command-correlated audit and one complete receipt with adjacent version |
| `PGA-S02` | simulated response loss followed by exact retry releases byte-identical stored bytes and no second effect |
| `PGA-S03` | a different tenant setting cannot see another practice's appointment, user, practitioner, audit or idempotency rows |
| `PGA-S04` | database actor inactive at the first fresh check returns 403 with no claim or effect |
| `PGA-S05` | actor revoked between the first and second fresh checks rolls back the claim and revocation simulation |
| `PGA-S06` | authenticated practice/target mismatch returns the closed unavailable outcome with no disclosure or effect |
| `PGA-S07` | a stale bound proposal version stops on changed locked request and rolls back the candidate claim |
| `PGA-S08` | tampered signed evidence or proposal-version binding stops before command-session construction |
| `PGA-S09` | missing practitioner projection after staged effect returns 503 and rolls back mutation, audit and receipt |
| `PGA-S10` | terminal transition with an assigned waiting area requires the exact warning and atomically clears the area |
| `PGA-S11` | wrong current database role fails the fresh authority check with no claim or effect |
| `PGA-S12` | transaction-local tenant context is absent before and after both a commit and a rollback; no pooled-session leakage occurs |

Each scenario starts with and ends on allowlisted counts and selected
status/version values. Expected failures are admitted only by exact public
kind/status/code. Failed sessions are rolled back and never reused.

## Evidence and acceptance

Pass only if:

- all fifteen frozen input hashes match and the adapter repair is exactly
  limited to transaction-local practice-context establishment;
- the contract and schemas are whole-document valid and at least 100 hostile
  mutations fail closed;
- cached-image, internal-network, container, tmpfs, resource, relay and exact-ID
  cleanup controls pass;
- PostgreSQL reports major 16, the accepted migration head, exact RLS policies
  and forced-RLS flags;
- all twelve scenarios pass with exact counts, adjacent versions, zero
  cross-tenant visibility, rollback equality and byte-identical replay;
- evidence contains no raw SQL, connection URL, password, bearer, response
  body, session digest, runtime identifier or unrestricted row;
- the route and all thirteen read-only sources remain hash-exact, the one
  predecessor-lineage test changes only as described above, and the route
  contains no product-adapter import; and
- focused/lineage/baton tests, Ruff, the canonical fast profile and Git
  whitespace pass.

Durable evidence may retain only fixed scenario IDs, decision/error labels,
counts, versions, value-free statement tokens, source/runtime digests,
containment booleans and cleanup results.

## Cleanup and claim boundary

Cleanup runs in `finally`. Stop the relay, dispose the engine, reinspect the
exact captured container ID and remove it only if name, image, labels, internal
network, tmpfs, bounds and mounts still match. Prove its absence; then reinspect
the exact captured empty network ID, remove it and prove its absence. Ownership
ambiguity stops cleanup and requires user attention; no substitute or broad
target is allowed.

Passing proves only the exact off-route product-adapter composition over one
disposable PostgreSQL 16 server with authored-synthetic rows. It does not prove
HTTP/dependency wiring, product data, concurrency, restart, crash,
unknown-commit, performance, deployment, production or UI behavior.

No route edit/mount/call, patient/clinical or operational product data,
provider/ADC/credential/IAM/browser/external network, product/runtime command,
deployment, production, release, Pages or protected-ref movement is authorised.
