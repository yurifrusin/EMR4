# Raisa provider-free Office practitioner-directory consumer design

Date: 2026-08-02

Result class: default-off task-scoped Office product-read consumer

## API Spine classification

This is a GraphQL read consumer. It reuses only
`Query.practice.practitioners`; the taskpane never receives a resolver,
database handle, policy selector or command capability. Logout remains the
accepted explicit REST session command. There is no GraphQL mutation,
subscription, provider call or product write.

## Runtime composition

The task harness owns a disposable database and four generated roles. One
application-auth pool activates only the accepted auth capability. A separate
product pool activates only the accepted exact-column directory capability.
Two surface-bound GraphQL subapplications share the accepted bridge and bind
their Office surface in server code.

At page delivery the harness sets one existing surface-session cookie and its
matching CSRF cookie. The page receives only the matching CSRF value and a
one-use result nonce, removes both from DOM attributes immediately, and retains
them in memory only until terminal cleanup.

## UI flow

`Office.onReady` derives only a coarse host class. A mismatch disables the
consumer. On the visible action, the client sends one compile-time GraphQL
document to its server-selected surface endpoint. It validates the closed
response shape before creating list-item text nodes. Successful rendering is
followed by logout; the terminal card says that the directory was shown and the
session ended.

The flow under test is: the task-specific Word taskpane loads -> the user runs
the directory check -> exactly two active authored-synthetic practitioners are
rendered -> the application session is logged out and rejected on reuse.

## Evidence boundary

Durable evidence records surface, host class, step booleans, exact row count,
projection equality, authorization-audit counts, role-denial booleans and
cleanup. It excludes names, UUIDs, email, session/cookie/CSRF/nonce values,
queries, database/role targets and Office account/document identifiers.

## Closed descendants

The implementation does not create a product mount, real principal mapping,
patient/clinical read, document integration, Microsoft interoperability,
product command, production session/key custody, deployment, production or
release contract.
