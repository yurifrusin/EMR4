# Threat-model delta: disposable PostgreSQL durability behavior/transaction rehearsal

Date: 2026-08-08

Status: candidate planning control; runtime closed

## Scope change

The accepted parent created and catalogued the exact Context Fabric durability
objects but invoked no behavior. This descendant proposes the first execution
of selected security-definer entry points, trigger functions and RLS policies
against closed authored-synthetic rows in one disposable local PostgreSQL 16
container.

No application route, operational database, provider, external network,
patient/product data, deployment or production surface is added.

## Assets

- exact accepted SQL bytes and parent catalogue/privilege identity;
- principal separation across producer, observer, coordinator, lifecycle,
  retention and application-read roles;
- tenant/practice/source/stream binding integrity;
- atomic update-confirm and Fabric projection membership;
- immutable alias, source position and admission/receipt identity;
- checkpoint/watermark/frame/obligation/lifecycle/audit atomicity;
- minimized scenario evidence and exact cleanup ownership.

## Trust boundaries

1. host harness to local Docker client;
2. Docker client to the exact owned networkless container;
3. container initialization superuser to each scenario login;
4. scenario login to security-definer entry point;
5. entry point/trigger owner to RLS-protected Fabric relations;
6. fixture application relations to payload-free Fabric relations; and
7. database readback to minimized repository evidence.

Bootstrap authority is outside the claimed behavior boundary. Only statements
run after exact session authorization under the named runtime role count as
role/RLS behavior evidence.

## Threats and controls

| Threat | Control | Required evidence |
|---|---|---|
| Parent SQL or function drift changes behavior under test | Exact source-head, byte, hash, manifest, catalogue and privilege binding before Docker and again before scenarios | All six parent bindings and catalogue digests match |
| Caller selects image, SQL, scenario, role, path or cleanup target | Fixed paths/constants, no CLI scenario input, argv-only `shell=False` | Hostile static mutations fail; runtime records closed profile |
| Container contacts registry, provider or host service | `--pull=never`, `--network=none`, no ports/mounts and no later join | Exact inspect facts before SQL and before cleanup |
| Fixture contains patient, product-derived or narrative data | Position-closed opaque UUID/time/digest namespace and exact event-key allowlist | Schema/static scan finds no patient/name/free-text fixture field |
| Superuser setup is mistaken for RLS evidence | Fresh connection plus one `SET SESSION AUTHORIZATION` before each transaction; record `session_user`/`current_user` | Every scenario identity matches its contract principal |
| Fixture grants silently broaden Fabric authority | Grants limited to four synthetic `public.*` relations; zero Fabric grant change | Pre/post privilege digest and explicit forbidden matrix |
| Forged practice/stream locator widens authority | Session-bound exact binding rederivation, forced RLS and beta-locator attack | `BTR-R01/R02` prove invisibility/denial and zero effect |
| Another role executes a foreign entry point or trigger function | Exact execute grants, `PUBLIC` revocation, no inheritance/role membership/bypass | `BTR-R03` observes `42501`/false for every cell |
| Partial update-confirm produces an outbox or partial application commit | Immediate/deferred fences plus one top-level transaction | `BTR-T01/T02/T04` roll back all application/Fabric members |
| Alias or source position is caller-chosen/reused | Owner-private generated alias, locked stream head and immutable guards | Positive readback plus `BTR-T03/I04` zero-delta failures |
| Replay duplicates admission or coordinator effects | Retained-evidence-first comparison and exact stored-locator replay | `BTR-I01/I03` preserve exact counts/digests |
| Mismatch overwrites primary or grows without bound | Receiver-authored PRIMARY plus at most one CONFLICT | `BTR-I02` proves stable two-row set and immutable primary |
| Entry-point success leaks after outer transaction abort | Fixed `P0001` before commit and fresh-connection readback | `BTR-B01/B02/B03` prove complete selected-set rollback |
| Expected failure is accepted under wrong reason | Exact SQLSTATE plus stable failure ID; no broad exception matching | Per-scenario expected/observed equality |
| Raw logs, payloads or credentials enter evidence | Allowlisted counts/digests only; bounded stable reason | Evidence-schema rejection and static forbidden-field tests |
| Cleanup removes another object or leaves owned state | Captured exact ID, nonce/label/name/image/network/mount reverification | Exact-ID removal and exact-ID absent post-inspect |

## STRIDE summary

- **Spoofing:** principal substitution is challenged by exact session identity,
  beta-locator and foreign-entry tests.
- **Tampering:** parent hashes, immutable triggers, per-scenario row digests and
  pre/post catalogue equality detect unauthorized changes.
- **Repudiation:** closed scenario IDs, exact SQLSTATEs and minimized before/
  after readback bind each result without exposing raw records.
- **Information disclosure:** forced RLS, alpha/beta isolation, opaque fixtures
  and allowlisted evidence bound disclosure.
- **Denial of service:** one serial sequence and fixed resource/time ceilings
  contain runaway SQL; concurrency and load are outside the claim.
- **Elevation of privilege:** no inheritance, `SET ROLE`, `BYPASSRLS`, schema
  create, Fabric DML or trigger execute is granted; actual denied statements
  supplement catalogue assertions.

## Residual risks deliberately deferred

- multi-session races, deadlocks and serializable anomalies;
- crash/unknown-commit readback and restart reconstruction;
- key rotation, retention eligibility/purge and recovery pins;
- operational credentials, long-lived storage and migration rollback;
- watcher/listener/source-feed behavior and application integration;
- performance, capacity and adversarial product-schema drift; and
- patient/clinical/product safety, provider, deployment and production.

The closeout must not claim those properties.

## Stop conditions

Runtime remains forbidden until the planning packet passes deterministic tests
and fresh exact-HEAD independent veto. During later execution, stop without
broadening if parent/catalogue/privilege drift, unexpected SQLSTATE, wrong
session identity, cross-practice visibility, unclassified partial effect,
container containment mismatch or cleanup ownership uncertainty appears.

No failure authorizes superuser substitution for a scenario, disabling RLS or
triggers, editing the parent artifact, omitting a scenario, using an
operational database, pulling an image, opening network access or contacting a
provider/product surface.
