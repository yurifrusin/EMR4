# Ariadne agent error and correction register — revision 312

Date: 2026-08-16

Timestamp: 2026-08-16T20:29:07.4792637+10:00 (Australia/Brisbane)

## Result

Revision 312 preserves 361 bounded known incidents. AER-0359 and AER-0361 are corrected and
AER-0360 is contained by the active Sol recovery lease pending the required
fresh exact-candidate veto; no incident is open.

AER-0359 preserves the original DeepSeek V4 Flash/high advisory pass. Sol's
pre-integration reconciliation found four localized frozen-contract defects:
incomplete public-envelope receipt validation, signed-evidence failures mapped
as authenticated-context failures, deterministic proposal stops opening the
command session, and an extra field in proposal-version HMAC material. The
single plan-authorised mechanical correction closes those four defects without
altering the original commit or its receipt.

AER-0360 preserves the corrected worker advisory pass and the reason it could
not be accepted. Sol found that the proposal and confirmation freshness
coordinates were not both required exact, an absent proposal evidence copy was
admitted when confirmation evidence verified, and the in-memory transaction
double did not reproduce the physical seam's practice-scoped target lookup
order. The external correction budget was exhausted, so Sol invoked the
explicit recovery lease.

The recovery changes only the product-adapter service and its focused test.
Both freshness coordinates and the proposal evidence copy must equal
recomputed signed truth before any command session; the physical double now
returns the same non-disclosing cross-practice 404 as the real seam; and focused
hostile cases prove zero session and zero physical entry on each mismatch. The
provider-free focused/static population, Ruff, compilation, twelve canonical-
LF bindings and forbidden-route/schema diff checks pass. AER-0360 remains
contained until the separately required fresh Gemini 3.7 Flash/high veto.

AER-0361 preserves a continuity-side defect found during that admission. The
new standing self-correction paragraph passed its focused policy test but made
`AGENTS.md` 80,096 bytes, breaching the pre-existing strict 80,000-byte compact
handover ceiling. The paragraph is now shorter without changing authority
meaning, the handover is 79,956 bytes, and
`handover_edits_require_acceptance_index_guard` is an explicit workflow hard
control. The focused policy and acceptance-index tests pass together.

## Boundary

These are bounded implementation-review and continuity-control incidents. Neither candidate was
admitted on its worker advisory result. No route, database, capability,
product/patient/clinical data, provider, network, deployment, Pages or
protected ref was opened. The register remains a workflow-improvement control,
not a provider or model comparison.
