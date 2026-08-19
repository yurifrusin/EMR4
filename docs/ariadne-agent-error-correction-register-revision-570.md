# Ariadne agent-error and correction register — revision 570

Date: 2026-08-20

Timestamp: 2026-08-20T00:55:00+10:00 (Australia/Brisbane)

## Revision scope

Revision 570 preserves AER-0660. The first separate clockwork closeout check
rejected the transaction manifest before publication because human-facing
uppercase `AER-0657` through `AER-0659` labels were copied into machine
`incident_id` fields whose grammar requires lowercase identifiers.

The closeout source and candidate remained unchanged. The three incident and
peer keys are now lowercase, the rejected check remains disclosed, and a fresh
read-only check is required before publish. The register now contains 660
incidents, all corrected or contained and none open.

## Prevention

Transaction-manifest incident keys must be rendered or validated against their
machine grammar during intent authoring. Human-facing AER labels belong in
evidence text unless a schema explicitly admits their case and shape.
