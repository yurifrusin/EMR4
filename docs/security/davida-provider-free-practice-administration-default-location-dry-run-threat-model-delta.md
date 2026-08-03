# Threat-model delta: Davida default-location dry run

Date: 2026-08-03

## Boundary

This tranche adds only an unmounted deterministic proposal transform over an
already accepted authored-synthetic context. Database truth remains
authoritative. No provider/model call, route, command, confirmation, apply or
write boundary opens.

| Threat | Control | Failure outcome |
|---|---|---|
| Unknown/advisory/apply operation reaches proposal logic | One-code allowlist before schema interpretation | `operation_not_allowed` |
| Pydantic coercion reverses a false authority field | Strict extra-forbid model plus canonical raw/validated equality | Closed rejection |
| Candidate injects facts, prose, before/after state or effectful metadata | Selector-only schema; trusted code constructs every released field | Schema rejection |
| Stale or foreign context is used | Exact practice/principal/correlation/revision binding and caller-supplied half-open freshness check | Closed rejection |
| Context is tampered or internally inconsistent | Exact parent shape/revision/source/ceiling/count/reference validation | Closed rejection |
| Missing, duplicate, wrong-kind or dangling opaque reference is selected | Global reference uniqueness and exact kind-specific resolution | Closed rejection |
| No-op is presented as a change | Requested location must differ from current context value | `no_change` |
| Before state is caller-controlled | Before value is copied only from the resolved practitioner row | Candidate field is impossible |
| Released diff broadens beyond default location | One literal changed path and strict before/after schemas | Internal construction fails closed |
| Proposal is mistaken for confirmation/apply authority | `proposal_candidate`/`dry_run_only`; human confirmation required; all effect authority false | No command can be constructed |
| Hash omits grounding inputs | Proposal and grounding hashes bind context revision, source paths and exact states; proposal hash also binds canonical candidate | Hash check fails |
| Rejection leaks partial proposal | Discriminated atomic result; rejected arm has no proposal field, repair or retry | No partial release |
| Source gains hidden DB/network/provider/clock access | AST/static tests forbid effectful imports and calls | Acceptance fails |
| Concurrent pytest corrupts the shared PostgreSQL schema | Root grants one serialized pytest slot | Worker waits |
| Branding is staged accidentally | Explicit-path staging and cached-path assertion | Commit gate fails |

## Residual gates

No occupied model, memory/RAG, real identity/data, patient/clinical/document
data, database/route, arbitrary API, confirmation/apply/write, cloud/IAM,
deployment, production, release, protected evidence/ref or branding authority
is established. Any effectful command remains a separate Yuri decision.
