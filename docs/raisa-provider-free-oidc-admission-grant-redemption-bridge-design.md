# Raisa provider-free OIDC admission-grant redemption bridge design

Date: 2026-08-02

Result class: provider-free atomic one-use session bridge

## API Spine placement

`POST /api/v1/application-auth/federation/session/redeem` is a one-use REST
session command in the original cookie partition. It is not GraphQL, a product
read, a product command, a provider callback or an asynchronous actuator.

## One transaction, one policy engine

The service computes the versioned HMAC of the raw grant before opening SQL.
One PostgreSQL transaction calls the exact redemption function and, only for
its admitted result, invokes the accepted application-auth runtime against the
same SQLAlchemy session. The persistence coordinator's internal transaction
step is reused; `ApplicationAuthRuntime.create_session` remains the only
session policy implementation.

The database function consumes the grant before the runtime step, but the
change is not externally visible until the enclosing transaction commits. A
runtime denial, required-audit outage, SQL failure or indeterminate commit
rolls back the grant, federation audit and session state together.

## Database authority split

The pool authenticates as one finite `NOINHERIT` redemption login and enters
one no-login redemption-call role. That role may:

- execute the exact redemption function; and
- use the already accepted application-auth generation, parent, surface,
  exchange and audit tables only through exact forced-RLS practice context.

It cannot directly read or update a federation grant, read a binding or fresh
principal row, or append federation audit.

An ungranted no-login redemption owner owns the `SECURITY DEFINER` function.
It receives only exact grant select/terminal-update, binding select, synthetic
principal-truth select, federation-audit insert, sequence and schema privileges.
It receives no application-session table privilege. The function has an empty
search path, fully qualified objects, bounded parameters and no dynamic SQL.
PostgreSQL row locking additionally requires a column-level `UPDATE` grant, so
the owner receives `UPDATE(updated_at)` on binding and truth tables. Exact
owner-only update policies admit the same rows for `FOR KEY SHARE` while
`WITH CHECK (false)` prevents every actual row mutation.

## Fresh authored-synthetic truth

`application_auth_synthetic_principal_truth` is a closed security fixture, not
a product user table. Its composite practice/user key carries current backend
role, optional practitioner reference, user/practice/membership active flags,
practitioner-link state, truth version, update time and the fixed
`authored_synthetic` data class. Checks prohibit live references, free text and
product foreign keys. Forced RLS permits the function owner to lock only the
exact grant-selected practice/user row.

This proves a fresh internal-truth decision shape without claiming a live
identity mapping or product-derived read. A future real source and sync/locking
contract require a new migration and authority decision.

## Exact grant and binding recheck

The function locks the HMAC-selected grant `FOR UPDATE`. It requires active
version one, issue <= now < exact 60-second expiry, and exact request surface,
server-derived origin, configured audience HMAC and federation policy. It then
selects the active binding by the immutable grant-bound binding reference and
requires the same version, user, practice and provider. The preceding callback
is the only code able to create that immutable reference after exact four-HMAC
issuer/tenant/object/subject resolution; redemption does not retain or recreate
raw external claims.

The synthetic principal row is locked before session creation. Any binding or
truth mismatch records one fixed-class rejection with a bounded internal
reason and leaves the grant unconsumed. A committed grant reports only the
generic conflict class; unknown values remain generic authentication failure.

## Commit and cookie boundary

On admission the function writes consumed/version-two state and the required
federation consumed audit. The accepted runtime then locks or creates the
principal generation and writes hash-only parent/surface records plus
session-created and surface-bound audit. The raw parent value remains server
memory only and is discarded. The raw surface value crosses only after commit
as the secure session cookie.

The transport rotates CSRF, and the route sets both accepted `__Host-` Secure,
HttpOnly, Path=/, no-Domain, SameSite=None, Partitioned cookies only after the
service returns from a successful committed transaction. The no-store response
returns the CSRF value once so the same-origin client can retain it in memory.

## Closed descendants

No live provider, real identity/principal table, product authorization or read,
binding command, production credential, hosted resource, distributed limiter,
monitoring/SIEM, deployment, protected integration, production or release is
opened.
