# Raisa provider-free native-Diary application-session UI composition plan

Date: 2026-08-03

Status: bounded default-off static-UI implementation candidate (Diary lane step 3)

Parent: `provider_free_native_diary_application_session_practitioner_reconciliation_pass`

## Outcome

Publish an LF-canonical copy of the accepted pure client reconciler and wire it
to one trusted injected fixed-read function through a browser ES module. The
native Diary selects this path only when the exact bootstrap property
`enabled` is the boolean `true`. Missing, false, non-object, non-boolean or
otherwise feature-off bootstrap state continues through the existing bearer
GraphQL read and REST fallback. An enabled but incomplete, authority-bearing or
changed-reader bootstrap fails closed before a read and never enters that
legacy fallback.

This is mounted only as static UI code and remains default-off. The evidence
label is `provider_free_default_off_ui_composition_harness`, with
`data_class=authored_synthetic`. It is not browser, live, route-intercepted,
HTTP, backend, PostgreSQL, usability, production or release evidence.

## Frozen implementation boundary

- The only accepted global is
  `window.__EMR4_NATIVE_DIARY_APPLICATION_SESSION_PRACTITIONERS__` with exactly
  `enabled`, `readFixedPractitionerDirectory` and `sessionGeneration`.
- The injected function receives no argument. It owns HTTP, cookie, origin,
  CSRF, session, authentication, authorization and audit details and must
  return the already accepted fixed-read envelope `{status, rows}`.
- The composition accepts no caller-selected cookie, token, CSRF, practice,
  principal, role, surface, policy, action, resource, query, variables,
  projection or arbitrary operation.
- The accepted reconciler is the sole row egress. Its ticket provenance,
  latest-read-wins, stale generation, supersession, invalidation, replay,
  malformed-response and callback-failure controls remain unchanged.
- `invalidateSession`, strictly increasing `advanceSessionGeneration`, and a
  sanitized snapshot are the only lifecycle/observability controls exposed by
  the composition. The snapshot contains no reader, response row, identity,
  secret or authority material.
- The existing `fetchPractitionerDirectoryGraphql` and
  `fetchPractitionerDirectoryRest` functions remain exact. Their fallback is
  reached only after the strict application-session flag is not enabled.
- The enabled branch never calls bearer GraphQL or REST, including after
  reader rejection, malformed output, stale generation or module failure.
- One bounded invalidation/reset helper invalidates every outstanding ticket
  and clears the cached composition/reader when bootstrap becomes disabled or
  malformed, or before an enabled invalid-bootstrap, reader-change,
  stale-generation or read failure is rethrown.
- Enabled-path failures carry one fixed generic marker. The enclosing
  `Promise.all` practitioner catch rethrows that marker so the Diary load cannot
  continue with a partial empty directory; feature-off legacy failures retain
  their established empty-directory swallowing behavior.

## Deterministic acceptance

1. Canonical and published reconciler texts are byte-equivalent after CRLF to
   LF normalization.
2. Missing, false, malformed and non-boolean feature flags select legacy; only
   exact boolean true selects the composition.
3. Enabled exact bootstrap invokes one no-argument reader and renders only an
   admitted fixed-read result.
4. Enabled incomplete, extra/authority-bearing or changed-reader bootstrap
   fails before any read, with no legacy fallback.
5. Latest-read-wins, strict generation advance, invalidation, replay, malformed
   or authority-bearing output and callback failure remain suppressed.
6. Reader failure is consumed and reported by a fixed sanitized reason.
7. Static checks prohibit direct network, storage, cookie, bearer, CSRF,
   provider/model, command or write implementation in both new modules.
8. The recursively closed machine contract rejects every scalar or array
   mutation and the focused parent, seam and API Spine tests pass serially.
9. An outstanding enabled read followed by disable, malformed bootstrap or
   reader change is invalidated before its result can render.
10. The enclosing Diary load rethrows every enabled-path failure while the
    feature-off legacy catch still returns an empty directory on ordinary
    non-401 legacy failure.

## API Spine classification

This is a deterministic consumer of the accepted fixed
`Query.practice.practitioners(activeOnly: true, limit: 200, offset: 0)` read.
GraphQL remains read-only. No query field, mutation, REST surface, command
tunnel, event actuator, manifest, audit authority or idempotency path is added.
The backend continues to own session authentication, practice scope,
authorization, freshness and required read audit.

## Closed gates and residual risk

No `app.main` mount, shared-auth/router change, provider/model, memory/RAG,
real identity, patient/clinical/document data, new read scope, command/write,
cloud/IAM, deployment, production, release, protected evidence/ref or
`docs/branding/` authority is added. The harness does not prove browser load
ordering, real session injection, HTTP/backend behavior, DOM rendering,
cross-tab lifecycle delivery or usability. Default-on or live browser
acceptance remains a separate Yuri-owned gate.
