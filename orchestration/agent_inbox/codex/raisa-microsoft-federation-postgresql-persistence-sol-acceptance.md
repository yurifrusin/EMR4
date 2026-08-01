# Sol acceptance — Raisa Microsoft-federation PostgreSQL persistence

Date: 2026-08-01

Decision: `pass`

Result: `raisa_microsoft_federation_postgresql_persistence_pass`

## Review

- The reversible migration advances the single Alembic head and adds exactly two product-detached authored-synthetic tables.
- Raw external identity is structurally absent; issuer, tenant, object, subject, correlation and external lookup values use versioned keyed HMAC references.
- Composite uniqueness admits exactly one concurrent external-key binding.
- Revocation is exact-versioned and terminal; audit is append-only.
- Required audit failure rolls back its associated mutation.
- Forced practice RLS passes through a disposable no-login/no-bypass role that is absent after rollback.
- The route-free repository is not imported by any FastAPI/GraphQL router and adds no provider, session or product path.

## Verification

- `python scripts/raisa_microsoft_federation_postgresql_persistence_acceptance.py` — pass; upgrade/downgrade/re-upgrade, concurrency, atomicity, guards, RLS, raw-value scan and cleanup all pass.
- `pytest -q tests/test_raisa_microsoft_federation_postgresql_persistence.py` — 10 passed.
- `ruff check` over the new model, migration, runtime/persistence services, acceptance runner and tests — pass.

Only the uniquely named disposable local database was mutated, then removed. No real identity, Microsoft/provider, route, session, product, cloud/IAM, deployment or production action occurred.
