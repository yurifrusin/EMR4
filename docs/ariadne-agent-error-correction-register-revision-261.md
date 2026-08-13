# Ariadne agent error and correction register — revision 261

Date: 2026-08-14

Timestamp: 2026-08-14T07:25:00+10:00 (Australia/Brisbane)

Revision 261 records AER-0294 through AER-0298. The register now contains 298
bounded known incidents. All five are corrected. AER-0295 and AER-0296 closed
only after the required API and UI maps were freshly reproduced with literal
reads after the corrected passing orchestration receipt.

AER-0294 records a main-lane content search that was incorrectly scoped to a
broad tests tree during appointment-reschedule discovery. Protected-fixture
match output appeared. It was immediately discarded and is prohibited from
planning, implementation, tests and acceptance. No repository, runtime,
database, provider, product data, command or ref changed. Subsequent discovery
uses one exact `Get-Content -LiteralPath` read per already-known non-protected
file and no directory-root search.

AER-0295 separately records a read-only UI-mapping worker's report that two
intended exact-file search commands emitted repository-wide lines beyond its
assigned allowlist. The worker stopped, discarded that output and changed no
file. A distinct post-receipt turn has now repeated the mapping with literal
reads only.

AER-0296 records that three native read-only subagents were started after
semantic rehydration but before the distinct preplanning receipt had passed.
This recurs the process-order family first recorded by AER-0043. Their first
results are quarantined. The useful API and UI results were freshly reproduced
after the corrected passing receipt and are recorded in separate sanitized
result receipts.

AER-0297 records the independent output-contract failure in that same dispatch
episode: the first runtime state used an unadmitted native-subagent observation
method and unmatched assigned-agent identifiers, so deterministic preflight
returned `revision_required`. The corrected state uses admitted synthetic
observation vocabulary, no unmatched assignments and the exact five named
rehydration sources; its distinct receipt passes.

AER-0298 records a further semantic freshness error found before either rerun
was admitted: the schema-valid receipt still embedded the already-closed
truth-parity operation rather than the live rescheduling latch. Both follow-up
turns were interrupted. The corrected `pre_worker_dispatch` state now embeds
the exact live operation, reports `in_progress`, requires no user attention,
forbids terminal handback and passes with all five named sources.

No protected output, prompt, secret, credential, patient, clinical, document or
product-derived value is retained in this revision or its sanitized receipts.
