# AES-C5 product-runtime admission threat-model delta

Date: 2026-08-11

Status: frozen for the exact practitioner-directory / Reception One purpose

Parent boundaries: the accepted Agent Execution Surface gate and AES-C0 through
AES-C4 contracts, threat models and closeouts.

## New assets and trust crossings

AES-C5 adds one real local application-route crossing and one minimized product-
runtime-derived ContextFrameSet before the already proven provider data-plane
crossing. Assets are one disposable PostgreSQL schema, one synthetic active
Receptionist identity/JWT, five synthetic practitioner sentinels across two
synthetic practices, one route lease, one provider lease, one broker-only alias
map, one expiring ContextFrameSet, one provider call reservation and one
minimized hash-chain evidence packet.

The first crossing is external broker to the in-process FastAPI route backed by
the isolated local PostgreSQL schema. The second is broker to the exact Sydney
Vertex `generateContent` endpoint. The work cell receives neither route nor
provider credentials and cannot choose either operation.

## Threats and required controls

| Threat | Required control | Failure disposition |
|---|---|---|
| Real practitioner or practice data enters the rehearsal | fresh isolated schema; fixed authored-synthetic population; no connection to operational database; content allowlist and exact expected names | stop before provider |
| Wrong or inactive human principal | ordinary signed bearer dependency; active synthetic Receptionist; token user/practice equality; broker principal/role/tenant digest | revoke route lease |
| Cross-practice or inactive row leak | route predicates plus foreign/inactive sentinels; exact three-row expectation; active invariant and tenant-bound source digest | no frame; quarantine |
| Pagination truncates a larger directory | request `limit=4` while maximum admitted choices is three; a fourth result is overflow and denial | no frame |
| Sensitive route field reaches model | exact route response schema; minimizer emits only opaque ref, display name and optional role; UUID, active and location dropped; unknown/sensitive keys rejected | no frame |
| JWT, UUID, alias map or database credential reaches work cell/evidence | broker-only custody; secret/UUID scans; digest/count-only evidence; zero raw route/prompt retention | revoke and quarantine |
| Route readiness fixture becomes runtime authority | harness calls route directly and never imports static readiness scripts/fixtures; current one-run Yuri selection is the authority | revision required |
| Stale directory context is treated as current truth | source observation bound into frame; 30-second dispatch age; 60-second TTL; same-packet proofreader; no command authority | `intelligence_unavailable` |
| Model chooses source, provider or operation | closed candidate excludes route/URL/method/capability/lease/adapter/destination/credential/SQL/path/tool/command fields; broker registry resolves both | deny before I/O |
| Database write during measured read | statement observer allows only expected SELECT/control statements; DML/DDL denied; counts unchanged | rollback, cleanup, no provider |
| Provider exfiltration or tool use | exact one-host POST, zero redirect, bounded bytes, no tools/functions/grounding/retrieval/code/fallback, no second call | consume ledger; no release |
| Provider retention exceeds claim | request/response logging and in-memory cache disabled by read-only preflight; payload synthetic; no platform-wide zero-retention claim | stop on uncertain controls |
| Schema-valid but wrong practitioner selection | deterministic proofreader checks target display name against admitted alias and exact context digest | `intelligence_unavailable` |
| Product read or provider replay | separate single-use ledgers, cumulative budgets, current-authority recheck, generation-wide revocation | terminal stop |
| Cleanup drops wrong data | random AES-C5-prefixed schema validated before exact `DROP SCHEMA`; engine disposed; no broad/glob target | quarantine; never pass |
| Regional claim overreach | claim configured/observed Sydney endpoint only; cite Google's endpoint limitation | revision required |

## API and command boundary

The existing practitioner-directory GET is the only product operation. The
provider result is a non-authoritative booking-context match with
`command_authority: false`. GraphQL is not called. No appointment, practitioner,
practice, audit or other product mutation exists. Any future command still
requires its own typed REST/OpenAPI authorization, confirmation, idempotency,
audit and readback path.

## Residual risk and claim limit

Application-layer practice filtering is not PostgreSQL RLS, and the provider,
OS, auth libraries, HTTP stack and PostgreSQL server remain outside complete
formal verification. Synthetic route evidence therefore proves only the exact
tested runtime/admission path. It does not authorize real-person, patient,
clinical, operational-practice, reusable-runtime, command, deployment or
production use.
