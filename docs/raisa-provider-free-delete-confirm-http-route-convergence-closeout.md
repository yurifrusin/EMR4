# Provider-free delete-confirm HTTP route convergence closeout

Date: 2026-08-17

Timestamp: 2026-08-17T06:42:01.5453490+10:00 (Australia/Brisbane)

Status: accepted

Exact reviewed candidate: `c7a01edd96ebabf3ea2c07be89a5b405c9629853`

Result: `raisa_provider_free_delete_confirm_http_route_convergence_pass`

## Outcome

Delete confirmation now has one canonical authenticated HTTP entry point at
`POST /api/v1/appointments/proposals/delete/confirm`. The historical
`/proposals/delete-confirm` spelling remains a hidden compatibility alias over
the same handler. The handler calls the accepted delete product adapter exactly
once and contains no local claim, source read, mutation, audit, receipt, commit
or fallback path.

Proposal generation server-mints an opaque binding between signed confirmation
evidence and the positive database-owned appointment version. Confirmation
must carry that binding. Only server-owned bearer identity, current user,
command-session factory, normalized idempotency key and five domain-separated
secret derivatives enter the adapter.

The public response is a dedicated recursively closed delete-confirm envelope,
not an appointment read model. Committed and replay outcomes validate and
canonicalize only that public body. Private stored receipt bytes are required
as internal command truth on success, forbidden on non-success, and can never
become HTTP content.

## Evidence

- all twelve frozen DHC scenarios pass;
- 149 hostile contract and public-envelope mutations fail closed;
- 27 focused route/plan tests and 78 static API Spine/Diary tests pass;
- the corrected register revision 319 passes its 274-test focused suite;
- the integrated provider-free closeout profile passes 439/439 tests;
- the deterministic reviewer passes 16/16 checks;
- Ruff, maintained-source compilation and Git whitespace checks pass; and
- one fresh eight-command Gemini 3.7 Flash/high veto returns exactly one
  schema-constrained `pass` and leaves exact HEAD, tree and worktree unchanged.

No database, Docker, SQL, route call or command effect was executed in this
tranche. The accepted adapter, composition and physical transaction files and
raw compatibility DELETE remain unchanged.

## Recovery and workflow correction

The initial DeepSeek candidate was rejected because its OpenAPI delete response
remained generic, its nested receipt schema admitted widened values and its
deterministic reviewer did not prove those exact leaves. Its one permitted
mechanical correction ended without a transferable receipt or commit. AER-0366
and AER-0367 preserve those outcomes. Sol adopted the initial commits only as
untrusted source under the explicit recovery lease, independently repaired the
schema/byte invariants and added exact regression guards before the fresh veto.

AER-0368 preserves a recurrence of AER-0365 in the first pre-verifier runtime:
a tree object ID was placed in the commit-ref evidence field. The existing
fail-closed guard stopped dispatch before any Gemini call. The corrected v2
receipt names only resolvable commit refs and keeps tree identity in the
dedicated worktree-preflight evidence.

## Deliberately closed

This is provider-free route composition evidence only. It does not prove HTTP
execution against PostgreSQL, atomic effect through the mounted route,
concurrency, restart/unknown-commit recovery, raw DELETE convergence, client/UI
behavior, product/patient/clinical data, provider/credential activity,
deployment, production, release, Pages or protected integration.
`docs/branding/` and every unrelated untracked file remain preserved.

## Next tranche

Proceed under standing uninterrupted-development authority to the narrowest
provider-free disposable PostgreSQL delete-confirm HTTP integration rehearsal.
It may exercise this exact canonical route with authored-synthetic rows and the
already accepted transaction seam, prove committed/replay/denial/rollback and
exact cleanup, but it must not change raw DELETE, add capability, use product or
patient data, call a provider, deploy, release, rebuild Pages or move protected
refs. Yuri's attention is not required.
