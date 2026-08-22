# Ariadne agent error and correction register — revision 614

Date: 2026-08-22

Timestamp: 2026-08-22T11:54:17.2967942+10:00 (Australia/Brisbane)

Status: **943 bounded incidents; all corrected or contained; none open**

<!-- ariadne-agent-error-register-reading
revision: 614
incident_count: 943
new_incident_ids: AER-0938,AER-0939,AER-0940,AER-0941,AER-0942,AER-0943
open_incident_count: 0
-->

This revision adds AER-0938 through AER-0943. It preserves every preceding
entry unchanged.

## AER-0938 — focused complete-runner expectations drifted from the contract

The first focused collection expected relative edges in a different traversal
order, forty rather than thirty-nine exact sidecar keys, and treated the word
`fixture` in safe envelope field names as though raw fixture content had been
retained. All three failures occurred before commit or process execution.

The tests now bind the actual deterministic module traversal, exact sidecar
cardinality and absence of raw-content fields. No runtime behavior changed.

Recurrence signature:
`orchestrator.complete_runner_focused_expectations_drifted_from_exact_contract`

## AER-0939 — result validator reused evidence canonicalization for wire bytes

The one authorised Node process exited zero with empty stderr, complete cleanup
and the exact 1,567-byte successful runner sidecar. Its 129-byte fixture line
also matched the frozen fixture source exactly. The controller nevertheless
emitted `complete_runner_result_rejected` because it compared the declared
`schema_version`, `result`, `app_exit_code` wire order against a generic
alphabetically sorted evidence serializer.

This immediately repeated the general wire/evidence-serializer mistake already
recorded in AER-0936. The earlier control corrected only its mock helper and did
not eliminate the same mistake from the new production validator. The consumed
terminal remains immutable and no retry occurred. A separate process-free
reconciliation derived both exact preimages from frozen source, matched their
byte counts and hashes to the envelope, and accepted the runner result without
another process.

The stronger recurrence control is now architectural: wire contracts require
a dedicated serializer and golden byte/hash assertion shared by fixture and
validator; generic evidence canonicalization is not admissible at a wire
comparison boundary.

Recurrence signature:
`orchestrator.complete_runner_validator_used_evidence_canonicalization_for_wire_contract`

## AER-0940 — recovery leaked the parent exception domain

Five hostile reconciliation tests changed schema-constant fields. The parent
schema correctly rejected them, but its `CompleteRunnerError` escaped instead
of the recovery's closed `ReconciliationError`. This was caught before the
process-free reconciliation was published.

The recovery now translates imported parent validation errors at its boundary;
all hostile cases pass and no process was launched.

Recurrence signature:
`orchestrator.reconciliation_leaked_parent_validation_exception_domain`

## AER-0941 — closeout omitted one exact boundary-floor literal

The first clockwork dry-run carried a broader boundary forbidding live product
runtime, production, deployment, release and Pages, but omitted the clockwork's
exact canonical `no_production_runtime_deployment_release_or_pages` token. The
typed validator rejected the intent with `tick_next_boundaries_floor` before
generation or publication.

The exact required literal was added without weakening the broader boundary.
The corrected dry-run then progressed to live-state validation. No canonical
projection, latch or protected ref changed in the rejected run.

Recurrence signature:
`orchestrator.clockwork_next_boundary_floor_literal_omitted`

## AER-0942 — closeout used an unregistered live acceptance label

The first live clockwork publication used a descriptive complete-runner
acceptance label rather than the closed `Current DeepSeek native Harness
acceptance` rolling slot. The renderer therefore inserted a second live
DeepSeek acceptance row. The broad post-publication clockwork test rejected
that state with `tick_baton_compaction_unindexed`.

The first generation and report remain preserved. The clockwork restored its
immediately previous generation byte exactly, with no Harness, worker, provider
or protected-ref process. The corrected intent now uses the exact rolling
label. The clockwork compactor also rejects every acceptance label absent from
the closed active-label manifest before rendering, with focused positive and
hostile tests.

Recurrence signature:
`orchestrator.clockwork_closeout_used_unregistered_live_acceptance_label`

## AER-0943 — successor latch omitted an exact closed-surface floor token

The second live closeout generation retained a broader combined
ordinary-practice restriction but omitted the exact
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`
token required by the Baton consistency contract. The post-publication suite
rejected the successor latch.

The second generation and report remain preserved. The clockwork again restored
its immediately previous generation byte exactly, without Harness, worker,
provider or protected-ref activity. The exact ordinary-practice and product/data
floor tokens now belong to the clockwork's required-boundary set and hostile
intent tests; the corrected intent separately retains the generic-status
`Arrived` prohibition.

Recurrence signature:
`orchestrator.clockwork_successor_latch_omitted_exact_closed_surface_floor`

## Control reading

AER-0939 is the material incident. The useful runner capability passed in one
process, but an already-known class of serializer-boundary lapse consumed a
reconciliation cycle because the prior fix was local rather than structural.
AER-0938, AER-0940 and AER-0941 were pre-execution test/control defects.
AER-0942 was a live governance-projection defect that the broad post-publication
test contained through the clockwork's byte-exact rollback. AER-0943 was a
second live successor-latch projection defect contained by the same rollback
gear and moved into the pre-generation boundary validator. Revision 614
therefore does not count the recovery paperwork as Harness capability progress;
it records one substantive runner pass and one avoidable post-processing rerun
of procedure plus two corrected governance projections, with zero Node retry,
provider activity or product authority.
