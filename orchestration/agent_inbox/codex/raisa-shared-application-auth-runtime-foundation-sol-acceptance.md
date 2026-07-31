# GPT Sol acceptance — Raisa shared application-auth runtime foundation

Date: 2026-07-31

Verdict: **accepted**

Result: `raisa_shared_application_auth_runtime_foundation_pass`

The authorised authored-synthetic runtime foundation satisfies its bounded
plan and inherited threat boundary.

The accepted implementation is `app/services/application_auth_runtime.py`.
It has no module-level instance or route, cookie, database, provider, network
or process wiring. Construction requires an explicit authored-synthetic
in-memory store, metadata audit sink and exact three-surface origin map.

Acceptance grounds the following claims:

1. opaque parent and surface values are stored and audited only as SHA-256
   references;
2. absolute/idle expiry, explicit revocation and principal-generation
   revocation fail closed across all three surfaces;
3. Word desktop and Word Online each create one native-Diary binding through a
   60-second maximum, exact-bound, state/nonce/S256-PKCE exchange;
4. concurrent redemption admits exactly one caller;
5. required-audit failure leaves create, redemption and revocation state
   unchanged; and
6. validated output is a synthetic server-principal snapshot, not a reusable
   product authorization decision or data capability.

The provider-free evidence passes all ten acceptance checks. All 32 focused
tests and the corrected 145-case expanded no-database-fixture suite pass.
Compilation and Ruff pass. Every recorded external/product side-effect count
is zero.

No live login, route, cookie, persistence, external identity, Microsoft/Office
federation, product-derived read, clinical authority, database access,
appointment command, microphone capture, document mutation, deployment,
production or release authority is created by this acceptance.

A durable PostgreSQL transaction/migration tranche is the next safe candidate,
still with authored-synthetic fixtures and no route/cookie/product read, but it
requires fresh authority.
