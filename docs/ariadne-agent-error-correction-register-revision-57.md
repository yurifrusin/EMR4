# Ariadne agent-error register revision 57

Date: 2026-08-06

Status: recovery-7 veto dispatch contract corrected; acceptance pending

## Failed-closed dispatch receipt preserved

The seventh migration/transaction architecture candidate remains unchanged at
`b9de77ce09ab36edc61e43aa5294a78180460660`. Its first independent-veto
predispatch state incorrectly used the invented event name `pre_dispatch` and
named an assigned reviewer without the exact matching workspace receipt
required by the live protocol. The deterministic orchestrator receipt returned
`revision_required`, denied dispatch and started no reviewer.

This is recorded as AER-0055. The failed runtime state and receipt remain
immutable evidence; they are not reused or overwritten.

## Corrected control

The replacement attempt is a distinct receipt that:

- copies the approved `pre_worker_dispatch` event verbatim from
  `orchestration/harness_settings/orchestrator_requirements.yaml`;
- keeps `assigned_agent_ids` empty until the native reviewer actually exists;
- binds the already-passed clean `r30` exact-HEAD review worktree evidence; and
- mirrors the previously admitted native-review workspace receipt shape rather
  than inventing assignment or event vocabulary.

No provider, database, product-data, patient-data, runtime, SQL, migration,
deployment, Pages or protected-ref boundary changed. AER-0051 remains open
until a genuinely fresh exact-head veto accepts the seventh candidate.

Revision 57 contains 55 bounded incidents: 43 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
Counts are workflow-improvement signals, not model, provider, transport or role
causation.
