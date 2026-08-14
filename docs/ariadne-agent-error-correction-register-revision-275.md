# Ariadne agent error and correction register — revision 275

Date: 2026-08-15

Timestamp: 2026-08-15T02:39:12+10:00 (Australia/Brisbane)

Revision 275 records AER-0314. The register now contains 314 bounded known
incidents, all corrected or contained by an explicit control.

AER-0314 records a low-severity Ariadne vocabulary mismatch. Sol used
`negative_net` for a lane's `expected_leverage`; the repository-local
preflight rejected the runtime state before integration. The configured value
is `negative`, with any qualified or net assessment carried in rationale text.

Only that value is corrected. A fresh passed pre-integration receipt remains a
hard precondition for the worker cherry-pick. Canonical source, the worker
candidate, external state and all refs remained unchanged by the rejected
receipt.
