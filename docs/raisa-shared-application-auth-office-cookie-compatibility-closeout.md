# Raisa shared application-auth Office cookie compatibility — closeout

## Result

Accepted terminal result:
`raisa_shared_application_auth_office_cookie_compatibility_pass`.

One installed Word taskpane and one signed-in Word Online taskpane each
completed the existing authored-synthetic cookie lifecycle through the exact
reserved HTTPS development origin. Both created, validated, rotated,
revalidated and logged out an independent in-memory session, then proved that
post-logout validation returned the ordinary authentication denial.

No application session remains.

## Desktop host repair

The first installed-Word admission attempt failed before the taskpane loaded.
The Office developer registration had been launched with debugging disabled;
both direct and web debugger flags were zero, so Word correctly rejected the
development add-in. The taskpane page was not delivered, no bootstrap was
consumed and no session was created.

The repair removed that stale registration, confirmed Word was stopped, and
started the same validated manifest with direct developer debugging enabled
and web debugging and live reload disabled. Word then loaded the taskpane and
the visible compatibility action passed. The matching stop command removed
the developer registration. No Trust Center, trusted catalogue, tenant,
administrator or Office policy setting changed.

## Word Online result and successful-run order

Word Online first displayed ngrok's ordinary free-tier safety interstitial.
The user acknowledged that page once, the taskpane loaded, and the visible
compatibility action passed.

The successful Word Online run therefore preceded the repaired successful
desktop run, although the failed-closed desktop admission attempt occurred
first. This differs from the plan's preferred successful-run order and is
recorded explicitly. It does not weaken the cross-host result: the two hosts
used independent synthetic principals, independent one-use bootstraps and
independent result nonces; the failed admission consumed none of them.

## Security and privacy boundary

The harness was a separate FastAPI application with explicit dependency
injection. It exposed only the existing seven application-auth routes and the
task-owned page, assets, closed result and loopback-only evidence endpoints.
It included no product router, database, external identity adapter, provider
client or product command.

The taskpane used ordinary same-origin credentialed fetches. It did not read
cookies, browser storage, Office account/profile state or any document API,
and it used no bearer, query-string, exchange or second-origin fallback.

The durable live-host record contains only closed host/surface/status fields,
step booleans, counts and generic failure codes. It contains no cookie,
bootstrap, nonce, header, account, tenant, document, patient or clinical
identifier.

## Verification

- Twelve focused harness, manifest, route, failure-closure and durable-evidence
  tests pass.
- The expanded shared-auth, API Spine and security-governance regression passes
  175 tests.
- Canonical Ruff, historical Diary leakage and reviewed Bandit gates pass.
- `pip-audit` reports no known Python dependency vulnerabilities.
- The blocking production Node audit reports zero vulnerabilities. The full
  non-blocking development-tool audit reports the existing 19 upstream-only
  vulnerabilities governed by the protected parent register; no force update
  was applied.
- The repository manifest and both task-specific Restricted manifests pass
  Microsoft's Office manifest validator. JavaScript syntax and JSON parsing
  pass.

The expanded regression also exposed two stale SHA-256 fields in the
protected PR 69 runtime-foundation evidence. Only those stored plan/runtime
digests were reconciled to the already accepted source bytes; runtime behavior
did not change.

## Cleanup

The one-use registry closed with two consumed values and none available or
reserved. The server recorded 14 bounded auth audit events and two generic
denials. It retained no raw bootstrap or evidence nonce.

The exact task-owned Python harness and ngrok tunnel were stopped after their
command lines were verified. Ports 8001 and 4040 have no listeners. The Office
developer registration is absent, so the taskpane cannot reload. The
user-visible blank Word process was left for ordinary user closure; its
document was neither inspected, changed nor deleted.

## Claim limit and next gate

This proves one supervised, authored-synthetic, process-local session-cookie
lifecycle in each tested Office host through one exact development origin. It
does not prove every Office/WebView/browser/tenant policy, PostgreSQL or
multi-instance behavior, real identity mapping, Microsoft federation,
product-data safety, distributed abuse resistance, organisational deployment,
production fitness or release readiness.

A next descendant requires fresh authority. The smallest application-auth
candidate is a provider-free, authored-synthetic Office-host exercise through
the already accepted local PostgreSQL persistence and capability-role boundary,
still without real identity or product reads. Real identity and Microsoft
federation remain a later architecture and threat-review decision.
