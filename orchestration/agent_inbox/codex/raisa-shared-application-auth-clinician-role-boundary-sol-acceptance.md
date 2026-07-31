# Sol acceptance — Raisa shared application-authentication and clinician-role boundary

## Disposition

Accepted as a terminal, evidence-bounded architecture pass:
`raisa_shared_application_auth_clinician_role_boundary_architecture_pass`.

The plan, design, threat-model delta, closed JSON policy, schemas, case
manifest, deterministic evaluator and generated evidence establish one
backend-owned authorization decision across desktop Word, Word Online and the
native Diary. Microsoft or Office identity and every client-supplied role,
practice, document or host claim remain non-authoritative.

The initial clinician-read rule is deliberately narrow: fresh server state
must show an active EMR4 user with the `GP` role, an active same-practice
practitioner link, an active same-practice resource scope, live parent and
surface sessions, current revocation generations and a successful required
audit record before data access. Every unknown or unavailable state denies.

The accepted session design uses opaque server-side parent and surface
sessions, bounded absolute and idle expiry, centralized revocation, and a
60-second single-use cross-surface exchange bound to exact surface, origin,
audience, state, nonce, parent generation and S256 PKCE. It transports neither
bearer authority nor clinical content.

All 23 authorization and 13 exchange cases match their frozen outcomes. All 16
focused tests pass with repository database fixtures disabled. The acceptance
records zero external calls, backend/database access, product or patient data,
commands, microphone access, document mutation, deployment and cloud/IAM
change.

The expanded 165-test no-database-fixture auth/API Spine/Word/Continuity suite
also passes.

This is architecture acceptance only. No runtime application-authentication,
revocation store, external identity provider, product-derived read, clinical
authority, database write, deployment, production or release authority is
created. A runtime implementation remains a separately authorized descendant.
