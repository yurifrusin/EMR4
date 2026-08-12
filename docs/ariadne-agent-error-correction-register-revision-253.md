# Ariadne agent error and correction register — revision 253

Date: 2026-08-12

Revision 253 records and corrects AER-0285. The register now contains 285
bounded known incidents with none open.

The first preplanning state for the CF-D2 workflow diagnosis used intuitive
continuation event `pre_plan`. The deterministic receipt returned
`revision_required` with `continuation_event_missing_or_unapproved`, admitted
no rehydration sources and authorised no action. The configured event is
`pre_sprint_planning`; a distinct v2 five-source receipt passed before the plan
was frozen.

This is the fifth occurrence of the exact continuation-event vocabulary
mismatch. Repeating an instruction to consult configuration did not prevent
recurrence. The workflow repair therefore makes the configured values
discoverable at the point of use through
`python -m scripts.ariadne_orchestrator_preflight --list-continuation-events`
and tests the list against the same settings file used by receipt admission.
