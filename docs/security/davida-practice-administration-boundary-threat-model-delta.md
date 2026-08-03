# Threat-model delta: Davida practice-administration boundary

Date: 2026-08-03

Status: architecture-only, provider-free, non-executing

## Boundary change

No product or data boundary opens. This delta freezes how Davida, a separate
custodian work-cell/container/agent identity, may act as the practice-
administration custodian over relatively stable institutional knowledge while
never owning database truth or acting as an autonomous database actor.

| Threat | Control | Failure outcome |
|---|---|---|
| Davida is merged into one combined runtime with Bernie and accumulates both domains' authority | Separate cell/container/agent identities, immutable per-agent policies, manifests and default-off gates | Candidate rejected before dispatch or composition |
| Shared mechanical kernel becomes a union of both agents' allowed fields and actions | Shared kernel is limited to provider-neutral envelopes, proofreader primitives and audit vocabulary; Davida policy is separately pinned | Unknown or cross-agent field/action rejected |
| "Custodian" is interpreted as direct database access | Davida has no database credential, ORM session, generic database client, GraphQL mutation, REST command credential or event actuator | No context delivery; attempt fails closed |
| Current room/waiting GET paths that normalize and commit are reused as pure read context | Pure side-effect-free projections are required; `GET /diary/rooms` and `GET /diary/waiting-areas` are blocked | Context source is ineligible |
| The live appointment waiting-room queue leaks patient-linked context | `GET /appointments/waiting-room` is blocked as patient/clinical closed data | Context source is ineligible |
| Advisory institutional knowledge becomes roster, policy or confirmation truth | Structural advisory-only types plus separate authoritative Practice Administration schemas | Advisory output cannot enter authoritative decision gates |
| Davida emits an existing confirmation envelope or `writes_authorized=true` | Davida output schemas exclude confirmation authority; trusted backend constructs authority after human action | Schema admission fails |
| Open action strings create undeclared administration operations | Closed Davida operation enum; unknown operations fail closed | Unknown operation rejected |
| Conversational/session memory becomes hidden institutional truth | Session/context state is expiring, revision-bound and supersedable | Stale/session output rejected; fresh read required |
| A future location read is sourced from a handler that normalizes or commits | Active-location projection purity gate (no flush/commit/normalize) before admission | Context source is ineligible |
| Event payload becomes a command or cached truth | Publish-after-commit signal followed by practice/role/resource recheck and fresh scoped read; Davida holds no event actuator | Event suppressed or reconciled inertly |
| Model output is mistaken for command authority | Typed drafts and proposal candidates only; backend constructs command authority after explicit human confirmation | No command is constructed; fail closed |
| A proposal skips optimistic-concurrency or idempotency checks | Future command plane requires expected aggregate version/ETag, candidate hash, expiry, idempotency and audit fields | Stale or duplicate command rejected |
| Davida is granted apply authority in the architecture tranche | Four-tranche sequence keeps write vertical last and separately authorised | Apply command never admitted in this tranche |
| Convenience staging captures the user-owned branding directory | Explicit-path staging only; `git add -A`/`.` and helper commit-message staging are forbidden | Pre-commit gate fails |
| Concurrent tests corrupt the shared PostgreSQL test schema | Repository pytest and shared PostgreSQL processes remain serial | Dispatch scheduler withholds the conflicting test run |
| Worker authority is mistaken for acceptance/integration authority | Worker implements only; reviewers return one decision; root Sol alone accepts and integrates | Candidate remains non-authoritative |
| Standing tranche authority silently expands to providers, real data or deployment | Explicit stop conditions and closed-gate list survive every lane packet and receipt | Root pauses for Yuri |

## Residual gates

Live providers, memory/RAG/GraphRAG, real identity, patient/clinical/document
data, autonomous/model-to-database writes, GraphQL mutations, external identity
writes, cloud/IAM, deployment, production, release, protected evidence and
protected refs remain separately closed. No runtime claim is made.
