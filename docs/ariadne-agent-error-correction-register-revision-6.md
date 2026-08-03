# Ariadne agent-error correction register revision 6

Date: 2026-08-04

Result: `ariadne_agent_error_correction_register_revision_6_pass`

## New incident

`AER-0013` records a Sol orchestrator envelope error during the model-required
Bureau architecture planning closeout. Root supplied the unapproved
`pre_acceptance` continuation event. The deterministic preflight returned
`revision_required`, omitted rehydration claims and prohibited dispatch before
any subagent, provider, model, integration, staging, commit or ref action.

The failed runtime state and receipt remain immutable evidence. A distinct
corrected packet uses the settings-approved `pre_verifier_acceptance` event and
the exact five rehydration sources.

## Control

Receipt construction must select `continuation_event` directly from
`orchestration/harness_settings/orchestrator_requirements.yaml`. An unapproved
event is not an alias and cannot be repaired by editing or overwriting the
failed receipt. The corrected attempt receives a new runtime-state and receipt
path.

## Register posture

Revision 6 contains 13 incidents: 11 agent-behavior observations, one harness
failure and one transport timeout. `AER-0013` resembles `AER-0009` at the
general event-admission level and shares its output-contract category, but they
are different attempts with different exact role/resource/signature composites
and therefore are not linked attempt peers. It creates no new exact recurrence.
The only exact recurring composite remains
`verifier.multiple_terminal_decisions` with two observations.

Counts remain workflow-improvement signals only. They are not comparative
model, provider or role quality evidence.
