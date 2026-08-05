# Ariadne agent-error register revision 17

Date: 2026-08-05

Status: AER-0023 corrected; no incident remains open

## AER-0023 C4 pre-planning continuation event

The first C4 pre-planning runtime state used the intuitive but unsupported
continuation event `pre_plan`. The deterministic receipt builder rejected it as
`continuation_event_missing_or_unapproved`, emitted no five-source rehydration
claim and prohibited worker dispatch. No external review, implementation,
product/runtime operation, stage, commit or ref movement followed that receipt.

The failed runtime state and receipt remain preserved. A distinct runtime state
selected the exact approved `pre_sprint_planning` event and `sprint_planning`
action from `orchestration/harness_settings/orchestrator_requirements.yaml`,
repeated all five sources and passed before C4 planning continued.

AER-0023 is a recurrence of AER-0013's orchestrator event-name contract error,
not a repository, transport or model-reasoning failure. The durable control is
to choose event names from the requirements file rather than paraphrasing them.

Revision 17 contains 23 bounded incidents and no open incident.
