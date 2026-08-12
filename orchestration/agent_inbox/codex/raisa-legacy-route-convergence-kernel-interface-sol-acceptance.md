# Sol acceptance — legacy-route convergence kernel interface

Date: 2026-08-12

Decision: `accepted`

Accepted result:
`raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface_pass`

I accept exact source `47e08eada878d8f6dd2a9b100e706404d3594e5a`.
The closed contract binds four raw, six proposal and five confirm routes to
four canonical operation families, preserves the exact eight outcomes and
authority-first disclosure order, and keeps all raw routes explicitly
ineligible today. Forty-eight hostile mutations fail closed; 110 focused tests,
the full register suite and the canonical 191-test repository profile pass.

The key safety decision is accepted: an authenticated raw request is not
silently relabelled as separate confirmation, and a same-transaction read is
not proof that the user's earlier view was current. Confirmation, freshness,
idempotency and audit remain independent admission requirements. Create remains
blocked on a separate database-owned schedule-domain fence.

AER-0290 preserves the preplanning receipt vocabulary failure and its distinct
passing correction. It did not authorise planning or any runtime action. No
external verifier was used because this tranche was expressly provider-free;
the deterministic contract, source hashes, semantic validation, hostile
mutations and API Spine tests were complete.

This acceptance opens no route, database/source, event, watcher, provider,
product/patient data, credential, command/write, deployment, Pages or protected
ref. The provider-free unmounted pure route-adapter differential rehearsal is
the next safe descendant under standing continuation authority.
