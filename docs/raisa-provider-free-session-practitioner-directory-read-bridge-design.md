# Raisa provider-free application-session practitioner-directory read bridge design

Date: 2026-08-02

Result class: default-off authored-synthetic GraphQL product-read bridge

## API Spine classification

This is a GraphQL scoped read/context change. It reuses
`Query.practice.practitioners`; it adds no mutation, command, provider call,
event actuator or manifest-selected authority. The existing shared service
continues to own the REST/GraphQL projection and practice filter.

## Request and authority path

The explicitly constructed router binds one surface in server code. Exact
origin, application-session cookie and CSRF pair cross into the adapter. The
accepted application-auth runtime resolves and validates the opaque surface
session. A closed process-local mapping identifies one disposable product user
and practice; the product database reloads current user truth before the
endpoint policy can admit.

The field resolver invokes a server-provided authorization callback before it
calls `list_practitioner_directory`. The callback fixes policy, action and
resource in code and denies `activeOnly=false`. It cannot accept an arbitrary
client role/action/resource triple. A successful runtime decision and durable
audit are current-request-only and immediately followed by the shared read.

The explicit router also owns a bounded operation-shape admission step before
session validation. It accepts JSON POST only, one query operation, the exact
`practice.practitioners` path, fixed arguments and the display-safe fields.
Aliases, fragments, directives, introspection, health, practice-id-only,
multiple operations, GET and mutation shapes never reach authentication or
product SQL. The ordinary shared GraphQL router is unchanged.

## Audit boundary

The application-auth audit table remains append-only and forced-RLS. The new
exact policy admits only `auth.authorization_allowed` and the already accepted
denial event. Audit contains hashed session reference, synthetic user/practice
references, current role, fixed surface/action/resource/policy, decision and a
bounded reason. It contains no product UUID, practitioner name, email, cookie,
CSRF value or query body.

The allow audit is committed before the GraphQL response can release product
data. Audit unavailability fails closed. The event records authorization, not
a claim that the later HTTP response was received or displayed.

An unresolvable surface reference has no practice context under forced RLS, so
it cannot truthfully create a practice-scoped denial row. If required-audit
admission fails during validation, the role-scoped resolver is consulted once
more only to classify that case: an absent binding becomes the same generic
401 as every unknown session; an identifiable binding remains 503. The lookup
returns only a boolean, never a principal, and every identifiable denial keeps
the required audit contract.

## Synthetic mapping boundary

The mapping exists only in the injected service instance and accepts bounded
synthetic references plus UUID values. Acceptance creates every referenced
practice, user, practitioner and location in a uniquely named disposable
database and removes the database afterward. No table, external identifier,
provider claim or real mapping is introduced.

## Product projection

Only active practitioners from the mapped user's practice are read. The
existing outer join admits only same-practice active default locations. The
GraphQL projection remains the five already accepted display-safe fields.
Existing deterministic order, offset and maximum 200-row limit remain intact.

## Closed descendants

No patient or clinical read, general session-backed GraphQL mount, product RLS
claim, real user mapping, provider interoperability, binding administration,
command/write, production secret, hosted resource, deployment, protected
integration, production or release is opened.
