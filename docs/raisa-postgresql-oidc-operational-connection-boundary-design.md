# Raisa PostgreSQL OIDC operational connection boundary design

Date: 2026-08-02

Result class: dormant provider-free operational runtime foundation

## API Spine placement

This is infrastructure beneath the accepted non-mounted REST protocol adapter.
It adds no endpoint, GraphQL mutation, async actuator, browser contract or
product permission. The builder can assemble the accepted PostgreSQL attempt
store, but no application router imports or invokes it.

## Principal separation

The deployment principal is an exact finite `emr4_oidc_attempt_login_*` LOGIN.
Its repository contract uses `PASSWORD NULL`, `NOINHERIT`, `NOBYPASSRLS` and a
bounded connection limit. It receives membership in, but does not inherit, the
existing `emr4_oidc_attempt_runtime_*` capability role. The capability remains
NOLOGIN and owns only schema usage plus select/insert/delete on the forced-RLS
attempt table. Supplying a real password remains an external deployment and
secret-lifecycle decision.

## Pool lifecycle

`OIDCAttemptPoolPolicy` bounds `pool_size`, `max_overflow`, checkout timeout,
recycle time and LOGIN connection limit. Pre-ping and LIFO are explicit. The
engine rejects non-PostgreSQL targets, a username other than the exact LOGIN,
and URL parameters capable of selecting a service or injecting session options.

The checkout hook rolls back any driver transaction, returns to the LOGIN,
resets session settings, enters the exact capability role, applies exact RLS
and timeout settings, verifies `session_user`, `current_user` and every setting,
then commits only setup. A custom pool-reset hook replaces the default reset:
it rolls back application work, resets role and all settings, verifies both
identities equal the LOGIN and commits only cleanup. A later checkout therefore
does not trust the state left by an earlier borrower.

## Credential-free key seam

`AuthorizationAttemptSecretProvider` is a structural port. Configuration has
only one provider namespace, bounded opaque secret references, key identifiers,
and active/retained ordering. It contains no secret bytes. At dormant runtime
construction the provider is called once per exact reference; results are
validated, encryption/digest reuse is rejected, and the accepted Fernet cipher
and digest keyring are built before the engine/store bundle is released.

This repository supplies no environment-variable, cloud secret-manager or
production key-custody adapter. Disposable acceptance supplies an in-memory
authored-synthetic provider whose values and references never enter evidence.

## Runtime bundle

`build_postgres_authorization_attempt_runtime` resolves keys first, creates the
finite engine second, then exposes its engine, session factory and accepted
store as one disposable bundle. Resolution failure cannot return a partial
runtime. Disposal closes the pool but does not mutate roles or infrastructure.

## Closed boundaries

No persistent credential, hosted database, secret-manager call, route,
callback page, admission grant, binding lookup, cookie, application session,
product read, live Microsoft call, cloud/IAM change, deployment, protected
integration, production or release is established.
