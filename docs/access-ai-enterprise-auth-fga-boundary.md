# Access AI Enterprise Auth and FGA Boundary

| Item | Value |
|---|---|
| Status | Static design map, fake-provider posture only |
| Date | 2026-07-06 |
| Programme | Programme 2F / Access AI API; Programme 2G / API Spine |
| Scope | External enterprise identity and FGA concepts mapped into EMR4-owned Access AI roles, capabilities, and permission checks |

## Boundary Classification

This is a security and entitlement design artifact. It does not add an identity
provider, runtime FGA client, provider invocation path, database policy, route,
memory store, RAG pipeline, GraphRAG pipeline, H15/H-series import, historical
diary trove access, or model write path.

The API Spine pattern remains:

- external identity can assert who a user is and what external groups or org
  roles they have;
- EMR4 maps those assertions into EMR4-owned roles and scopes;
- Access AI entitlement checks decide whether a capability/method is allowed;
- provider adapters are reachable only after EMR4 authorization, audit, cost,
  environment, PHI, and provider policy checks pass;
- high-risk or external effects remain command-plane operations, not GraphQL
  mutations or provider-side privileges.

## Existing EMR4 Anchors

The current static seam already has the right shape:

| Artifact | Current Role |
|---|---|
| `app/services/ai/external_identity.py` | Maps external groups/org roles into `AiAccessRole`; unknown groups grant nothing. |
| `app/services/ai/entitlements.py` | Makes fail-closed Access AI decisions from actor roles, capability, method, and environment. |
| `app/services/ai/contracts.py` | Defines stable EMR4 capability, method, modality, risk-tier, and provider-class names. |
| `app/services/ai/registry.py` | Keeps capability metadata static and fail-closed for provider class, environment, PHI, risk, cost, and audit posture. |
| `orchestration/access_ai_api_design.md` | Defines Access AI as the backend choke point and preserves future WorkOS/OpenFGA/Auth0 compatibility. |
| `orchestration/api_spine_adr.md` | Requires GraphQL read-only boundaries and command-plane ownership for external/provider actions. |
| `docs/api-spine/security/permission-matrix.yaml` | Provides prototype ABAC default-deny examples for role/action/resource decisions. |
| `access_ai/setup_paths/*.yaml` | Declares setup/IAM/provider readiness inputs without becoming an authorization engine. |

## Enterprise Concept Map

| Enterprise Concept | Example Source | EMR4-Owned Target | Rule |
|---|---|---|---|
| Organization or tenant | WorkOS organization, Cloud Identity customer, internal practice | `practice_id` plus environment | External organization identity never replaces EMR4 practice tenancy checks. |
| Human identity | OIDC subject, SAML NameID, internal user id | EMR4 authenticated user | Provider identity is an input to login/session only; Access AI receives an EMR4 actor context. |
| Directory group | Cloud Identity group, Entra/Google group | `AiAccessRole` through explicit mapping | Unknown groups grant no Access AI role. |
| Organization role | WorkOS-style role such as `access_ai:reception` | `ai.reception_user` or another `AiAccessRole` | External role names are not used directly in provider calls or command authorization. |
| Fine-grained permission | OpenFGA/Auth0 FGA tuple/check | EMR4 action/resource decision | Future FGA may answer a decision, but EMR4 still owns action names, resource scopes, audit, and fallback deny. |
| Relationship | user manages practice, user belongs to location, GP owns encounter | EMR4 resource-scope evidence | Relationship evidence narrows access; it must not broaden an AI agent beyond the invoking surface. |
| Service identity | GCP service account, workload identity, AWS role | Provider adapter runtime identity | Infrastructure IAM permits provider API use only after product entitlement allows the request. |
| Agent principal | *bernie*, *scribe*, *consultant*, *davida* | Delegated EMR4 principal with narrower capability | Agents inherit a bounded action context, not the human's full authority. |

## Role Mapping

External identity should feed the existing Access AI role vocabulary:

| External Assertion | EMR4 Role | Intended Capability Surface |
|---|---|---|
| `access-ai-clinical@littlestardigital.com` or `access_ai:clinical` | `ai.clinical_user` | Clinical extraction, audio scribe, letter drafting, licensed knowledge query where policy allows. |
| `access-ai-reception@littlestardigital.com` or `access_ai:reception` | `ai.reception_user` | Bernie read-only and proposal capabilities. |
| `access-ai-reception-supervisors@littlestardigital.com` or `access_ai:reception_supervisor` | `ai.reception_supervisor` | Higher-risk Bernie proposal review surfaces, still no autonomous final write. |
| `access-ai-dev-operators@littlestardigital.com` | `ai.dev_operator` | Dev-only diagnostics such as non-PHI live smoke when that gate is explicitly open. |
| `access-ai-platform-admins@littlestardigital.com` | `ai.platform_admin` | Capability/provider/policy configuration, subject to command audit and environment gates. |
| `access-ai-disabled@littlestardigital.com` or `access_ai:disabled` | `ai.disabled` | Explicit deny overriding grants. |

Two invariants matter most:

- external identity maps to EMR4 roles; it does not call providers directly;
- `ai.disabled` must remain an overriding deny no matter which external group
  or role is also present.

## FGA Shape For Access AI

A future FGA model can be useful only if it is a decision input to EMR4, not a
replacement for EMR4's Access AI gate.

Recommended first-pass tuple/check vocabulary:

| Subject | Action | Resource | EMR4 Follow-Up Check |
|---|---|---|---|
| `user:{id}` | `invoke_ai` | `ai_capability:{capability}` | `decide_ai_entitlement(actor, capability, method)` plus registry metadata. |
| `user:{id}` | `read` | `knowledge_source:{id}` | Licensed source, citation, PHI, clinician-facing policy. |
| `user:{id}` | `propose` | `appointment_proposal:{practice}` | Same-practice, session, staff surface, no final write. |
| `user:{id}` | `confirm` | `appointment:{id}` | Signed confirmation evidence, idempotency, freshness, audit, backend revalidation. |
| `agent:bernie` | `propose` | `appointment_proposal:{practice}` | Delegated by allowed human role; final write remains false. |
| `agent:consultant` | `read` | `knowledge_source:{id}` | Delegated by GP; citations required; patient-specific advice remains doctor-reviewed. |
| `service:{provider_identity}` | `call_provider` | `provider_project:{id}` | Product entitlement must already be allowed; infrastructure IAM alone is insufficient. |

Default-deny cases should include unknown role/action/resource, omitted practice
scope, cross-practice resource access, stale confirmation evidence, provider
gate closed, H15/H-series runtime gate closed, and memory/RAG/GraphRAG gate
closed.

## Invocation Context Contract

External identity/FGA output should be reduced to a minimal Access AI actor and
resource context before invocation:

| Field | Source | Required Posture |
|---|---|---|
| `user_id` | EMR4 session | Required for human requests except dedicated integration flows. |
| `practice_id` | EMR4 tenancy | Required before PHI, diary, patient, appointment, or provider work. |
| `roles` | EMR4 role mapping | Derived from internal role defaults plus explicit external mappings. |
| `environment` | runtime/config | Must match capability registry allowlist. |
| `capability` | EMR4 request | Stable `AiCapability`, not provider model name. |
| `method` | EMR4 request | Stable `AiMethod`; unsupported methods fail closed. |
| `resource_scope` | EMR4 authorization layer | Practice/location/patient/appointment/knowledge-source scope as needed. |
| `risk_tier` | capability registry | Controls audit, confirmation, PHI, and provider policy. |
| `correlation_id` | command/API layer | Required for audit and review. |

Provider adapters must not infer permission from prompt text, external group
names, model output, or FGA tuple names.

## Audit And Idempotency

Enterprise-auth/FGA decisions should become auditable metadata when they affect
Access AI:

- actor user id and practice id;
- mapped Access AI roles, not raw directory dumps;
- external provider type, such as `cloud_identity`, `workos`, `oidc`, or `saml`;
- coarse decision source, such as internal role default, external mapping, or
  future FGA check;
- capability, method, risk tier, environment, and resource type;
- decision, reason code, and correlation id;
- provider/project/model metadata only after a provider call is permitted;
- no raw prompt, raw transcript, generated clinical text, or directory payload
  by default.

Mutating or external commands still need idempotency keys and command audit. An
FGA allow result is not confirmation evidence and cannot replace backend
revalidation.

## Blocked Gates

This document keeps these gates closed:

| Gate | Current Decision | Required Future Review |
|---|---|---|
| Live provider runtime expansion | Blocked except already reviewed explicit dev/live-smoke paths | Access AI entitlement, audit, budget, provider, and evidence-label review. |
| Runtime FGA/OpenFGA/Auth0/WorkOS client | Blocked | Design and test a fail-closed adapter with outage semantics, caching rules, and audit metadata. |
| SSO/SAML/OIDC production dependency | Blocked | Auth/session ADR, tenancy migration plan, account-linking rules, and rollback path. |
| SCIM/directory sync writes | Blocked | User lifecycle, deprovisioning, disabled-role precedence, and audit review. |
| GraphQL mutation or provider invocation | Blocked | API Spine exception review; current ADR has no exception. |
| Model-to-database writes | Blocked | Human confirmation, command audit, idempotency, and backend revalidation design. |
| Memory/RAG/GraphRAG runtime wiring | Blocked | Privacy, source-safety, Access AI capability, and retrieval audit review. |
| H15/H-series runtime imports or broad trove access | Blocked | Dedicated historical-diary gate review and approved scope. |
| External patient clients | Blocked | RLS/RLS-equivalent milestone, anti-enumeration, CORS/CSRF, privacy impact, and patient identity review. |

## Next Recommendations

1. Add a static `AccessAiEnterpriseAuthMapping` fixture or YAML example that
   mirrors this document without contacting an identity provider.
2. Add deterministic tests for mapping invariants: unknown external groups deny,
   disabled overrides grants, and provider/FGA names never become Access AI
   roles unless explicitly mapped.
3. Extend the permission matrix with Access AI-specific examples only after the
   current schema prototype artifacts settle, preserving default-deny behavior.
4. Draft a future FGA adapter contract with explicit outage behavior:
   fail-closed for provider invocation and writes; allow only already-authorized
   local fake-provider tests.
5. Before any production SSO/SCIM or runtime FGA client, decide how EMR4 links
   external identities to existing users, practices, locations, and practitioner
   records without cross-practice leakage.

