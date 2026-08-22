# Ariadne agent error and correction register — revision 612

Date: 2026-08-22

Timestamp: 2026-08-22T10:27:17.1698176+10:00 (Australia/Brisbane)

Status: **933 bounded incidents; all corrected or contained; none open**

<!-- ariadne-agent-error-register-reading
revision: 612
incident_count: 933
new_incident_ids: AER-0923,AER-0924,AER-0925,AER-0926,AER-0927,AER-0928,AER-0929,AER-0930,AER-0931,AER-0932,AER-0933
open_incident_count: 0
-->

This revision adds AER-0923 through AER-0933. It preserves every preceding
entry unchanged.

## AER-0923 — predecessor evidence constant named incorrectly

The first process-free contract-generation command referenced a plausible but
nonexistent `EVIDENCE_V2_PATH` constant. Import failed before contract creation
or Node execution. The controller now uses the predecessor's actual
`EVIDENCE_PATH`; contract generation and all focused tests pass.

Recurrence signature:
`orchestrator.predecessor_artifact_constant_guessed_instead_of_read_from_source`

## AER-0924 — bridge materialization basename guessed in schema

The first contract schema named the bridge
`preset-mount-sanitizer-runner-bridge.mjs`, while the controller's frozen
inventory used the repository source basename. Schema validation rejected the
contract before any process execution. The schema was corrected to the
controller-derived basename and the exact contract passed.

Recurrence signature:
`orchestrator.module_materialization_basename_guessed_instead_of_derived`

## AER-0925 — patch marker retained in a focused assertion

The first focused suite retained a literal `+` after an embedded newline in
the anti-orbit plan assertion. One test failed and twenty-two passed before the
authorised Node attempt. The literal was corrected; all twenty-three focused
tests and the exact 149-test broader collection passed.

Recurrence signature:
`orchestrator.patch_marker_retained_inside_multiline_test_literal`

## AER-0926 — graph inventory omitted the guard's relative import target

The static gate verified accepted source bytes and an eight-file inventory but
did not verify relative-import closure. The exact guard imports
`./preset-mount-sanitizer-runner-bridge.mjs`; the inventory materialized the
same accepted bridge bytes under the longer repository source basename. The
single authorised Node process exited 1 with zero stdout bytes and 938 stderr
bytes. Its content-free envelope was persisted, the disposable root was
removed, and no retry occurred.

The deterministic source diagnosis proves the absent import target without
reading or retaining raw stderr. The candidate is contained as negative
evidence. A distinct recovery must derive and validate complete import closure
before its own one-process boundary.

Recurrence signature:
`orchestrator.module_graph_file_inventory_passed_without_relative_import_closure`

## AER-0927 — required adapter observations omitted from acceptance state

The first negative-evidence pre-verifier runtime state omitted the required
Deep Code and Claude adapter observations. Preflight returned
`revision_required` without dispatch, commit or external activity. Both exact
declined/not-selected observations were added and the same five-source
preflight then passed.

Recurrence signature:
`orchestrator.pre_verifier_runtime_state_omitted_required_adapter_observations`

## AER-0928 — successor operation identifier exceeded the closed limit

The first clockwork closeout intent proposed a 138-character successor
operation identifier, exceeding the transactional schema's 128-character
limit. The dry-run rejected the intent before publication. The successor was
renamed to the 84-character
`deepseek-native-harness-provider-free-guard-bridge-import-closure-recovery-rehearsal`
identifier and the intent was revalidated.

Recurrence signature:
`orchestrator.successor_operation_identifier_composed_beyond_closed_length`

## AER-0929 — incident tranche field reused the longer operation identifier

After the successor identifier correction, the next dry-run rejected the six
incident observations because their `tranche` field reused the current
127-character operation identifier while the incident vocabulary permits 120.
The observations now use the stable 53-character tranche label
`deepseek-native-harness-guard-bridge-module-graph`; no incident meaning or
operation identity changed.

Recurrence signature:
`orchestrator.incident_tranche_reused_operation_identifier_beyond_closed_length`

## AER-0930 — descriptive incident stages used outside the closed vocabulary

The next dry-run rejected the descriptive `verification` and `review` stage
labels because incident observations accept only the registered stage enum.
They were replaced with exact `deterministic_verification` and `acceptance`
values. No live publication occurred.

Recurrence signature:
`orchestrator.incident_stage_authored_descriptively_outside_closed_vocabulary`

## AER-0931 — revision note omitted the prospective machine reading

After all observation fields validated, the dry-run rejected revision 612
because its human note lacked the exact clockwork-owned comment binding the
prospective revision, total incident count, ordered new IDs and open count. The
note first gained the exact prospective reading; after AER-0932 and AER-0933
the same machine binding was updated atomically to revision 612 / 933
incidents / AER-0923 through AER-0933 / zero open.

Recurrence signature:
`orchestrator.incident_revision_note_omitted_machine_reading_comment`

## AER-0932 — successor latch omitted an exact closed boundary

The first live clockwork generation preserved the general ordinary-practice
closure but omitted the exact historical invariant
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`.
The comprehensive post-publication suite failed its Current Baton boundary
test. Clockwork rolled back byte-exactly to the previous generation before any
canonical commit. The source intent now includes the exact boundary and must
pass the complete suite after corrected republication.

Recurrence signature:
`orchestrator.successor_latch_omitted_exact_closed_surface_boundary`

## AER-0933 — corrected tick attempted before rollback pointer commit

After byte-exact rollback, the physical clockwork pointer carried the new
rollback lease while the corrected source commit still contained the older
pointer. A premature dry-run rejected this as `tick_pointer_physical_drift`.
The rollback pointer is now explicitly committed before the corrected tick is
prepared, restoring source/physical equality without manual pointer editing.

Recurrence signature:
`orchestrator.corrected_tick_attempted_before_rollback_pointer_commit`

## Control reading

Ten incidents were caught before the consumed process or before canonical
clockwork commit publication. AER-0926 is the one
material execution defect: a missing import-closure invariant, not a model or
provider failure. The recovery control is intentionally structural—derive
every relative specifier and prove every resolved target is in the disposable
inventory—rather than adding another narrative reminder.
