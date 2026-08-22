# Ariadne agent error and correction register — revision 613

Date: 2026-08-22

Timestamp: 2026-08-22T11:14:21.3006188+10:00 (Australia/Brisbane)

Status: **937 bounded incidents; all corrected or contained; none open**

<!-- ariadne-agent-error-register-reading
revision: 613
incident_count: 937
new_incident_ids: AER-0934,AER-0935,AER-0936,AER-0937
open_incident_count: 0
-->

This revision adds AER-0934 through AER-0937. It preserves every preceding
entry unchanged.

## AER-0934 — fixture patch markers made the predecessor diagnosis non-exclusive

Fresh recovery preplanning inspected the exact predecessor fixture generator
and found 103 literal leading `+` patch markers embedded in its JavaScript.
The predecessor's absent bridge target remained source-proved, but raw stderr
had deliberately not been retained, so the accepted statement that this target
explained the process terminal was too exclusive: fixture parsing could have
failed first.

The recovery plan explicitly withdrew exclusivity without altering the
immutable terminal or reading raw stderr. Its controller now derives the
corrected fixture by removing exactly those 103 prefixes, binds both source
identities, rejects any residual patch-marker line and proves the full static
import closure before its one distinct process. That process passed.

Recurrence signature:
`orchestrator.fixture_patch_markers_made_source_diagnosis_nonexclusive`

## AER-0935 — plan assertion ignored Markdown line wrapping

The first focused recovery collection expected one exact plan phrase as a
single physical line even though Markdown wrapped it across two lines. The
test failed before commit or process execution. It now flattens plan lines
before checking semantic phrases, preserving the same acceptance meaning.

Recurrence signature:
`orchestrator.plan_assertion_treated_line_wrap_as_semantic_change`

## AER-0936 — mocked fixture output used sorted rather than contract key order

The first focused recovery collection built its mocked successful fixture
output with the controller's canonical evidence serializer, which sorts keys.
The actual fixture contract deliberately requires insertion order
`schema_version`, `result`, `cases`, so the otherwise-correct mock was rejected.
The helper now serializes the frozen fixture object without sorting. No
production or process behavior changed, and the one authorised Node process
had not started.

Recurrence signature:
`orchestrator.fixture_mock_used_evidence_canonicalization_instead_of_wire_order`

## AER-0937 — closeout command omitted the required module switch

The first clockwork dry-run rejected the persisted-check command because its
arguments began with the script path rather than the closed command grammar's
required `-m` module switch. No live clockwork publication occurred. The
manifest now invokes the same controller through its exact Python module name;
the exercised verification and accepted product evidence are unchanged.

Recurrence signature:
`orchestrator.clockwork_command_manifest_omitted_module_switch`

## Control reading

AER-0934 is the material acceptance correction: the failed predecessor remains
valid negative evidence, but its causal claim is narrowed to two source-proved
defects rather than one exclusive explanation. AER-0935 and AER-0936 were
focused-test construction defects caught before the process boundary. AER-0937
was a closeout command-manifest shape defect rejected before publication. Their
corrections added no tranche, retry, provider activity or product authority.
