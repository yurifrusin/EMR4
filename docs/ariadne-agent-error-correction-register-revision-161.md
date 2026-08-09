# Ariadne agent error and correction register revision 161

Date: 2026-08-10

## Change

Revision 161 adds `AER-0187`. The first attempt-033 recovery pre-planning state
used descriptive `continuation_event: pre_plan` and omitted the complete
declared adapter and managed-worker-slot inventory. The generic Ariadne
preflight rejected it as `revision_required` before any further database,
provider, commit or dispatch action.

The rejected state and receipt remain preserved. A distinct v2 state copied
`pre_sprint_planning` from the active requirements, supplied all six adapter
observations and the `deepseek-flash-workers` inventory, named all five
rehydration sources and passed.

## State

The register contains 187 incidents with none open. This recurrence reinforces
that receipt enum and inventory fields are copied from the active requirements;
task-specific phase wording belongs only in `planned_action`.
