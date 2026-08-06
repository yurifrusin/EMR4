# Threat-model delta: Context Fabric Current operational weave

Date: 2026-08-06

Status: bounded provider-free design/implementation delta

## Trust boundaries and assets

The candidate is untrusted. Backend authority binding and the four ordinary
read authorizers remain trusted. Source envelopes are untrusted until their
closed schema, seals, exact source-contract pairing, practice/session/location
scope and freshness pass. The proofreader is deterministic and independent of
candidate formation.

Protected assets are tenant/principal/session isolation, current operational
truth, source distinctions, freshness, minimal disclosure and command
separation.

## Threats and controls

| Threat | Control |
|---|---|
| Candidate supplies tenant, role, session or authority | Those fields are absent from the closed candidate; backend binding is separately sealed. |
| Cross-practice or cross-session source substitution | Every source must match exact practice and backend-derived session-binding digest. |
| A source claims another source's semantics | Exact allowlisted source-contract/frame/source triple; distinct output types and provenance. |
| Stale source is woven as current | Half-open interval, caller clock, observation-age cap, expiry and supersession checks before assembly and proofreading. |
| Partial bundle hides missing required truth | Required sources are explicit; missing, duplicate or invalid sources return one atomic block. |
| Cross-source references disagree | Appointment, practitioner, location, date and session-focus coherence is deterministic and fail closed. |
| Directory or session leaks excess state | Closed minimal payloads, field intersection and schema prohibition of authority envelopes, transcripts, readers and cached rows. |
| Context becomes command evidence | Constant `read_only: true`, `command_authority: false`, `provider_authority: false`; proofreader rejects alteration; no command code or API surface. |
| Context composition becomes a broad join/query | The pure engine accepts already-produced envelopes and imports no product, database, network or provider module. |
| GraphQL becomes a command/new route | No GraphQL or application source is changed; existing API Spine regression tests remain mandatory. |

## Residual risks deliberately deferred

Real patient/product fields, production RLS/ABAC, database query authorization,
source-specific privacy, real session injection/revocation, persistence,
retention, bitemporal history, runtime performance and model prompt
minimisation require separate descendants. Authored-synthetic coherence cannot
validate those production controls.

## Forbidden openings

No patient, clinical, product-derived, historical-PHI or protected data; raw
audit; real database/session/service; source query; persistence/retention;
provider or external retrieval; GraphQL/REST route, resolver, mutation or
subscription; command/write; product runtime; deployment, production, release,
Pages, protected evidence or protected-ref movement. Preserve and exclude
`docs/branding/` and unrelated untracked artifacts.
