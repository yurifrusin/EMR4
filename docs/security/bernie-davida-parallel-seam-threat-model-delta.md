# Threat-model delta: Bernie/Davida parallel seam

Date: 2026-08-03

Status: architecture-only

## Boundary change

No product or data boundary opens. This delta freezes how two future bounded
agent lanes may share deterministic infrastructure while retaining separate
domain authority and execution identities.

| Threat | Control | Failure outcome |
|---|---|---|
| One combined agent runtime accumulates Diary and administration authority | Separate probabilistic work cells, identities, manifests, policies and default-off gates | Candidate rejected before dispatch or composition |
| Shared proofreader becomes the union of both agents' capabilities | Shared engine code with separately pinned agent policy instances and exact schema/port admission | Unknown or cross-agent field/action rejected |
| A deterministic native Diary read is unnecessarily routed through an agent or proofreader | Separate deterministic consumer branch over the lower application-session/product-read bridge | Composition rejected before product wiring |
| Office terminal lifecycle is reused in the long-lived native Diary | Surface-specific composition; Office adapter remains Office-only | Static contract or lifecycle test fails |
| The default-off composition silently replaces the existing bearer path or its REST fallback | Existing native Diary behaviour is frozen when the feature is off | Candidate rejected as a material product fork |
| “Native” is interpreted as direct database access | Work cells receive only typed minimal frames and have no database credentials/session | No context delivery; attempt fails closed |
| Advisory practice knowledge becomes roster, policy or confirmation truth | Structural advisory-only types plus separate authoritative Practice Administration schemas | Advisory output cannot enter authoritative decision gates |
| Davida emits an existing confirmation envelope carrying `writes_authorized=true` | Davida output schemas exclude confirmation authority; trusted backend constructs authority after human action | Schema admission fails |
| Open action strings create undeclared administration operations | Closed Davida operation enum and exact agent-specific proofreader policy | Unknown operation rejected |
| A read frame is sourced from a GET handler that normalizes and commits | Pure side-effect-free Practice Administration projections are required | Context source is ineligible |
| Conversational memory becomes hidden institutional truth | Session state is expiring, revision-bound and supersedable | Stale/session output rejected; fresh read required |
| Davida deactivation or location changes silently disrupt Diary | Dry-run diff, effective date, expected version, explicit risk-tier confirmation, backend revalidation and committed event | No write; typed stale/blocked outcome |
| Event payload becomes a command or cached truth | Publish-after-commit signal followed by practice/role/resource recheck and fresh scoped read | Event suppressed or reconciled inertly |
| Two parallel lanes edit shared policy or handover files inconsistently | Root-only shared paths, exact owned-path packets and serial reconciliation | Worker candidate rejected without integration |
| Convenience staging captures the user-owned branding directory | Explicit-path staging only; `git add -A`/`.` and helper commit-message staging are forbidden | Pre-commit gate fails |
| Legacy allocation advice selects the wrong verifier | Current deterministic-first verifier policy is authoritative; Gemini 3.6 Flash/high is selected directly | Dispatch is rejected or corrected before a call |
| Concurrent tests corrupt the shared PostgreSQL test schema | Repository pytest and shared PostgreSQL processes remain serial | Dispatch scheduler withholds the conflicting test run |
| Two verifier sessions contaminate independence or exceed the single verifier slot | One fresh Antigravity project at a time, exact read-only candidate, prior review artifacts excluded | Review is queued or discarded |
| Worker authority is mistaken for acceptance/integration authority | Workers implement only; reviewers return one decision; root Sol alone accepts and integrates | Candidate remains non-authoritative |
| Standing tranche authority silently expands to providers, real data or deployment | Explicit stop conditions and closed-gate list survive every lane packet and receipt | Root pauses for Yuri |
| Manual Office/browser action consumes excessive computer-use tokens | Root identifies a bounded manual step and requests exact user action/evidence | Automated work pauses only at that step |

## Residual gates

Live providers, memory/RAG/GraphRAG, real identity, patient/clinical/document
data, autonomous/model-to-database writes, GraphQL mutations, external identity
writes, cloud/IAM, deployment, production, release, protected evidence and
protected refs remain separately closed.
