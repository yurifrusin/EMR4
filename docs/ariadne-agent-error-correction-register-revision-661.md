# Ariadne agent error and correction register — revision 661

Date: 2026-08-24

Timestamp: 2026-08-24T10:49:51.2828508+10:00 (Australia/Brisbane)

Register revision: `661`

Incident count: `1153`

Open incidents: `0`

New incidents: `AER-1152`, `AER-1153`

<!-- ariadne-agent-error-register-reading
revision: 661
incident_count: 1153
new_incident_ids: AER-1152,AER-1153
open_incident_count: 0
-->

## AER-1152

The first preplanning continuation intent for the clockwork materialisation
subgate included `orchestration_harness/...` and `tests/...` paths in
`active_evidence_paths`. The receipt schema accepts authority/evidence roots in
that field and rejected with `serial_continuation_evidence_path_root_forbidden`
before planning.

The correction removed only the two implementation pointers. The current
contract, accepted closeout documents and latch remained as active evidence;
the regenerated receipt passed all five sources. No plan, implementation,
private-data, provider or acceptance run was repeated.

Durable prevention: continuation `active_evidence_paths` are selected from
authority and evidence-document roots; implementation/test paths belong in the
plan or worker packet, not the rehydration evidence list.

## AER-1153

The first bound closeout rehearsal rejected at
`tick_incident_revision_reading`. Revision 661 contained the correct human
incident account but omitted the clockwork's exact machine-readable revision,
incident-count, new-ID and open-count comment.

The direct read-only tick diagnostic identified the exact validator. The
required comment and this second incident heading were added before staging or
publication. The correction changes no clockwork implementation, successor
authority or product/privacy boundary.

Durable prevention: construct every incident revision note from the executable
`_validate_incident_revision_artifact` reading shape before the bound rehearsal.
