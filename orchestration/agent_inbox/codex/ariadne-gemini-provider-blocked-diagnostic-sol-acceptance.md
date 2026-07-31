# Sol Acceptance — Ariadne Gemini Provider-Blocked Diagnostic

Date: 2026-07-24
Decision:
`ariadne_gemini_provider_blocked_request_contract_diagnostic_pass`

I accept the repository-local provider-blocked diagnostic and audit-export
repair.

The diagnostic establishes that attempt 003 contained the Gemini
3.x-unsupported `candidateCount` generation setting and removes it from the
shared request constructor. The unretained raw 400 prevents exact historical
causal attribution, so this acceptance does not claim that every possible
request-contract cause has been excluded.

The trusted audit exporter is now lossless for allowlisted fields and fails
closed on an unknown field. Historical attempt-003 evidence remains unchanged
and revision-required.

No provider/model request, retry, credential read, prompt transmission,
container, network, database, product API, event feed, mailbox or command
surface was exercised or opened. A repaired occupied attempt remains a fresh
Yuri decision.
