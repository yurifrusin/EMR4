# Sol acceptance — status-confirm product-adapter PostgreSQL integration

Date: 2026-08-13

Timestamp: 2026-08-13T11:39:46+10:00 (Australia/Brisbane)

Decision: accepted

Result: `raisa_provider_free_disposable_postgresql_status_confirm_product_adapter_integration_rehearsal_pass`

Accepted source: `553d38c37af86ceefc7b4315b8eaa171d405ab95`

The exact accepted product adapter passes all twelve scenarios against a
restricted, forced-RLS disposable PostgreSQL 16 database. Transaction-local
practice context precedes every practice-scoped lock/read/write, both actor
checks use current database truth, the complete effect/audit/private-receipt
write is atomic, a lost-response retry releases byte-identical stored bytes,
and pooled tenant context does not survive either commit or rollback.

The two integration defects exposed by the database are repaired narrowly:
column-only practice-lock privilege in the disposable role, and canonical-text
to UUID normalization only between admitted request and physical seam. The
signed request and its digest remain unchanged.

All 104 hostile mutations, 12 database scenarios, 112 focused current-lineage
tests and the 193-test canonical fast profile pass. Cleanup is exact. No route
was changed, mounted or called by this tranche, and no product/patient data,
provider, credential, external network, deployment or protected ref was
opened.

The next safe descendant is the provider-free authored-synthetic convergence
of the existing status-confirm HTTP route onto this accepted adapter, including
opaque proposal-version carriage and exact stored-byte replay delivery.
