# Threat-model delta: Davida advisory proofreader

Date: 2026-08-03

Parent: `provider_free_practice_administration_pure_read_pass`

## Assets and boundary

Assets are the accepted authored-synthetic minimal context, opaque resource
references and the released structured advisory draft. Database truth remains
authoritative. The proofreader is deterministic and unmounted; Davida/model
occupancy, credentials and product egress are absent.

## Threats and controls

| Threat | Control |
|---|---|
| Operation smuggles proposal/apply authority | Two-code literal discriminated union and pre-interpretation allowlist. |
| Candidate injects prose, facts, counts or effectful fields | Selector-only extra-forbid models plus raw/canonical equality. |
| Boolean/numeric coercion reverses an authority flag | Raw candidate must exactly equal its canonical validated JSON; output schemas use literal false. |
| Cross-practice or stale context is used | Exact practice/principal/correlation/revision binding and caller-supplied half-open freshness check. |
| Context is tampered | Exact parent shape, blocked-source/label/ceiling checks and independent content-revision recomputation. |
| Recomputed malformed context broadens semantics | Count/row equality, global opaque-ref uniqueness, two-minute lifetime and default-location resolution are revalidated. |
| Wrong-kind or ambiguous target leaks a row | Exact-kind single match; missing, duplicate, wrong-kind and dangling references reject. |
| Ungrounded model-style output is released | Every output field is derived by trusted code; grounding binds context revision, source paths and payload. |
| Partial output survives failure | Discriminated atomic result; rejection has no draft; repair/retry are false. |
| Data or authority leaks to evidence | Evidence allowlists fixed labels, counts, booleans and hashes only. |

## Residual risks

- This unoccupied proof does not evaluate natural-language interpretation
  quality or provider behaviour.
- Opaque references are bounded handles, not authentication capabilities; the
  eventual mounted backend must reauthorize every fresh context acquisition.
- Structured fields still require safe UI encoding when a future presentation
  layer renders them. This tranche returns no HTML or Markdown.

## Gates preserved

No provider/model, memory/RAG, database/network/clock, route/GraphQL change,
event, command, proposal/apply/confirmation/write, real identity/data,
patient/clinical/document data, deployment, production, release, protected
evidence/ref or branding authority is added.
