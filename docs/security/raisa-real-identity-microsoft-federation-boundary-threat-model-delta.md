# Threat-model delta: Raisa real identity and Microsoft federation

Date: 2026-08-01

Scope: Architecture-only Microsoft Entra authentication boundary and the two authorised provider-free authored-synthetic descendants.

Parent: `docs/security/raisa-shared-application-auth-clinician-role-boundary-threat-model-delta.md`

## Assets and security properties

- EMR4 user/practice identity and active binding truth
- Microsoft authorization attempt integrity
- OIDC issuer, audience, tenant, subject, nonce and lifetime integrity
- signing metadata and key-rollover trust
- application-session issuance authority
- binding lifecycle and recovery authority
- hash/HMAC-only identity and audit metadata
- non-enumerating failure behavior

The essential property is: a Microsoft assertion may authenticate only the exact external subject it represents; it cannot select, create or change an EMR4 principal, practice, role, clinician link or product capability.

## New trust boundaries

1. Office/browser to future backend login-start boundary.
2. Backend to one configured tenant-specific Microsoft Entra authority.
3. Backend callback to maintained OIDC verifier and signing metadata cache.
4. Validated assertion to exact external-identity binding lookup.
5. Binding result to fresh EMR4 identity reload and accepted session runtime.
6. Future privileged binding-lifecycle command to durable binding/audit store.

Only repository-local representations of boundaries 4 and 6 are exercised in the authorised descendants. Boundaries 1–3 and 5 remain unwired.

## Threats and required controls

| Threat | Consequence | Frozen control | Residual/later gate |
|---|---|---|---|
| Login CSRF or callback injection | Victim session bound to attacker identity | exact single-use state, nonce, attempt correlation, return surface/origin and bounded expiry | live route, browser and concurrency proof |
| Authorization-code interception or replay | Session theft | backend redemption, S256 PKCE, one-use attempt, no code/token logging or client persistence | maintained library and live Microsoft proof |
| Tenant confusion or permissive `common` authority | Foreign tenant admitted | tenant-specific authority; exact allowlisted `tid` and issuer; reject `common`, `organizations`, `consumers` | tenant onboarding governance |
| Confused-deputy audience | Token for another client accepted | exact configured client `aud`; no Graph token acceptance | live library configuration proof |
| Signature bypass or stale signing key | Forged token admitted or outage | maintained verifier; metadata-derived keys; multiple-key cache; bounded unknown-key refresh; fail closed | network resilience, cache and rollover exercise |
| Email/domain auto-link takeover | Wrong EMR4 user selected | bind only immutable `(tid, oid)`; email/name/domain display-only; no JIT/autolink | authorised binding administration UX |
| Guest/personal-account ambiguity | Unintended consumer identity admitted | organisational tenant only; personal account authorities rejected; guest requires exact tenant-local pre-binding | explicit guest policy review |
| Binding collision or ambiguity | One external identity maps to several principals | database uniqueness and exactly-one active result; ambiguity denies | durable concurrency proof in tranche 3 |
| Stale role or practitioner state | Authenticated user receives obsolete authority | assertion contains no EMR4 role; fresh backend reload and endpoint authorization required | product-read bridge remains closed |
| Inactive/revoked identity | Former staff retains access | active binding and active internal principal required; binding change advances central session generation later | lifecycle command/session bridge authority |
| Required audit outage | Unaccountable admission | audit-before-principal release; failure returns service unavailable | durable cross-store/session atomicity design |
| Identifier leakage | Tenant or user enumeration and privacy harm | versioned keyed HMAC; generic external error; no raw identifier/token audit | production key custody, retention and SIEM |
| Binding recovery abuse | Account takeover | separate command, recent re-authentication, idempotency, expected version and second human for replacement/recovery | exact RBAC, support and break-glass design |
| Office account substitution | Office sign-in becomes application authority | Office identity is an untrusted hint only; explicit EMR4 login required | occupied multi-account UX testing |
| Synthetic runtime accidentally wired | Test verifier becomes authentication bypass | default-off, authored-synthetic type, route import bans, static non-network checks | build/deployment configuration gates |

## Abuse cases

- An attacker changes an email claim to match a GP: no binding lookup uses email, so admission denies.
- A token from another Entra tenant has a valid Microsoft signature: exact `tid` and tenant-specific issuer checks deny.
- A token for Microsoft Graph is presented to EMR4: exact EMR4 client audience check denies.
- An unknown `kid` appears: the future library may refresh configured metadata once within its bounded rollover policy; unresolved trust denies.
- A valid Microsoft subject has two active EMR4 bindings: uniqueness should prevent it; any observed ambiguity denies and is audited.
- A Word Online user is signed into Microsoft but has no EMR4 binding: Office context is ignored and admission denies generically.
- The audit sink fails after a binding is found: no principal candidate or session is released.
- A developer supplies a synthetic verifier object to a route: static and runtime default-off gates reject wiring; no route is authorised.

## Privacy and retention

Raw authorization codes, ID/access/refresh tokens, state, nonce, PKCE verifier, Microsoft tenant/object identifiers, email, name and Office identity must never enter the durable store or general logs. Synthetic persistence uses injected HMAC key material and stores only versioned references. Audit retention, subject-access handling, breach response, production key custody and deletion after unlink remain unresolved and require a later privacy/operational decision.

## Verification required in the authorised descendants

- closed typed architecture cases for every threat above;
- in-memory exact mapping, default-off, audit failure and ambiguity tests;
- static proof of no FastAPI/GraphQL import and no network/provider client;
- reversible migration and exact ORM parity;
- durable uniqueness, active/revoked behavior, keyed-reference non-leakage, append-only audit and atomic rollback in a disposable database; and
- complete cleanup with no source database migration.

## Residual risk and closed gates

No live protocol/library configuration, redirect-origin behavior, Microsoft tenant policy, conditional access, MFA/assurance mapping, rate limiting, distributed replay defense, real identity governance, account-recovery operation, session bridge, product read, SIEM/paging, cloud/IAM change, deployment, production or release is proven. Each remains a separate explicit gate.

---
Reviewed-by: Codex Security threat-model workflow
Review-date: 2026-08-01
Repository: EMR4
Version: 7c618c336baca6c33a4bedcf7e23b50be1bb9c3e
