# Ariadne agent error and correction register — revision 228

Date: 2026-08-11

Revision 228 adds AER-0262 and AER-0263. The register now contains 263 bounded
known incidents.

## AER-0262 — repeated orchestrator receipt event mismatch

The first AES-C5 pre-planning runtime state repeated the already registered
`pre_plan` vocabulary error from AER-0259. The deterministic orchestrator
preflight returned `revision_required` with
`continuation_event_missing_or_unapproved`; it supplied no rehydration or
planning authority. No product read, provider call or external mutation
occurred.

Sol preserved that rejected state/receipt, read the configured continuation
event vocabulary and repeated the complete five-source receipt using exact
`pre_sprint_planning`. The corrected receipt passed. Future receipt events must
be copied from `orchestrator_requirements.yaml`, never inferred from prose.

## AER-0263 — protected holdout traversal during broad source search

The first repository inspection for AES-C5 used one broad recursive search over
application, API-documentation, test and orchestration roots. That command
crossed the protected-evidence boundary by traversing protected holdout fixture
paths and returning matches. No result from that search is admitted or used,
and this revision does not reproduce any protected filename, label, case,
value or content.

The worktree remained unchanged, and no product database, application route,
provider, prompt, credential, network adapter, command or write was touched.
The corrected inspection is restricted to an explicit allowlist of named
non-protected route, schema, service, authorization, API Spine and focused test
files. Future source discovery for protected repositories must never include a
broad test, fixture, support, holdout, manifest, receipt or report root.

The prohibited traversal cannot be undone; AER-0263 is contained rather than
claimed erased. Its output supplies no evidence and cannot shape AES-C5.
