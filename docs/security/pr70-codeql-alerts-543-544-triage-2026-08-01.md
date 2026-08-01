# PR 70 CodeQL alerts 543-544 triage

Date: 2026-08-01

Branch revision: `2084022e927815b624b91ac377365224a0fa1381`

Pull request: `yurifrusin/EMR4#70`

## Alert 544 - incomplete URL substring sanitization

Verdict: `confirmed`, high severity, narrow test-only boundary.

The Office cookie test asserted that `appsforoffice.microsoft.com` occurred
anywhere in the taskpane Content-Security-Policy header. Although the value was
not used to authorize or redirect a runtime request, this was an incomplete
allowlist assertion: an attacker-controlled or malformed directive containing
the allowed hostname in an arbitrary position could satisfy the test.

The invariant is that the `script-src` directive must contain exactly `self`
and the canonical Office.js HTTPS origin. The minimal repair parses the CSP
into directive tokens and compares the complete `script-src` source list for
equality. The legitimate taskpane header and Office.js load remain unchanged.

## Alert 543 - useless assignment to local variable

Verdict: `confirmed_quality`, CodeQL warning without a security-severity level.

The taskpane assigned an empty string to the local CSRF variable in a `finally`
block immediately before the function returned. JavaScript does not guarantee
that this overwrites the prior string storage, and no later read observed the
assignment. Removing the ineffective assignment changes neither the session
lifecycle nor failure-closed behavior.

## Disposition and proof

Both instances were patched on the task branch without dismissal or other
native alert mutation. Focused tests, JavaScript syntax and canonical
lint/Bandit passed. Fresh CodeQL workflow run `30693354428` then passed both
language analyses and wrapper check; native instances 543 and 544 each report
`fixed`. Alert 544 is remediated as `SF-0021`, and alert 543 remains preserved
in the linked instance ledger as a fixed quality finding.

No authentication, authorization, product, document, identity, provider,
deployment, production or release boundary changes.
