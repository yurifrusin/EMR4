# Raisa provider-free OIDC binding and admission-grant boundary design

Date: 2026-08-02

Result class: HMAC-only external-identity resolution and short-lived bearer
admission boundary

## API Spine placement

The provider callback remains an external REST protocol endpoint. The new
resolver and grant issuer are internal security services beneath that endpoint;
they are not GraphQL reads, product commands, asynchronous actuators or
application-session authorities.

## PostgreSQL authority split

The operational pool connects as one finite `NOINHERIT` login. Code must enter
one of two credential-free capabilities with `SET LOCAL ROLE`:

- the resolver-call capability can execute only the exact resolver function;
- the grant-issuer capability can inspect only its exact-practice grant metadata
  needed for the transactional capacity bound and insert a practice-scoped
  grant, but cannot read a binding or insert an audit row directly.

A third credential-free role owns the `SECURITY DEFINER` resolver. The owner is
not granted to the deployment login. It receives only binding `SELECT`, audit
`INSERT`, required sequence access and schema usage. All roles are no-superuser,
no-create, no-inherit, no-replication and no-bypass-RLS.

The resolver function has an empty search path, fully qualified objects,
bounded exact arguments and a single-row return. Forced-RLS policies admit its
binding read only when every row HMAC equals a transaction-local function
argument. Its audit policy admits only the same correlation/external HMACs and
the resolved practice, or the exact null-principal rejection shape.

## HMAC-only resolution

The service owns referenced HMAC keys outside PostgreSQL. It canonicalizes the
configured tenant-specific issuer and audience and hashes issuer, tenant,
object, subject, external tuple and correlation independently. The database
function compares all four identity components, not merely tenant/object.

An active exact match returns only binding reference/version and authored-
synthetic user/practice references after appending
`federation.binding_resolved`. A miss appends
`federation.binding_rejected` with no principal and returns no row. Required
audit and resolution share the caller transaction.

## Admission grant

The service generates 32 random bytes and encodes the bearer as an opaque URL-
safe value. Only a separately keyed, versioned HMAC is stored. The grant is
bound to the returned binding/version, user/practice, external and audience
HMACs, exact surface/origin/return target, policy and correlation. Its lifetime
is exactly 60 seconds, initial status is `active`, version is one, and the table
has a bounded active-row capacity enforced transactionally.

After resolver success the same transaction enters the grant-issuer role, sets
the exact practice and HMAC policy context, and inserts the grant. An
after-insert security-definer trigger owned by the ungranted no-login resolver
owner appends `federation.admission_grant_issued`; the issuer has no direct
audit privilege. Trigger or audit failure aborts the grant insert. The
transaction commits before the raw bearer is released. Rollback or
indeterminate commit releases nothing.

## Callback bridge

`OIDCStartCallbackTransport` accepts an optional typed admission port. Without
an explicitly injected port the historical parent proof remains an enum-only
verification bridge; the application router is still default 404 and no
composition root selects either mode. With the port injected, successful
callback completion must issue a grant or fail unavailable—there is no fallback
to the enum-only success. The bridge posts the raw grant only to its exact
stored origin under the existing nonce CSP and no-store headers.

## Closed descendants

The grant cannot create an application session. Redemption, binding-version
recheck, fresh internal user/practice truth, atomic consume, session/audit
commit, cookie delivery, product access, live Microsoft, deployment and
production remain closed.
