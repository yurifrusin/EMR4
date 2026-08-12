# Ariadne agent error and correction register — revision 257

Date: 2026-08-12

Revision 257 records and corrects AER-0290. The register now contains 290
bounded known incidents with none open. The first legacy-route convergence
runtime state reused intuitive
`pre_plan` instead of configured `pre_sprint_planning`. The generic Ariadne
preflight returned `revision_required`, emitted no rehydration sources and
authorised no planning or dispatch. No route, database, provider, product data,
network, command, protected ref or external worker was opened.

The failed state and receipt remain immutable. A distinct v2 state copied the
event from `orchestration/harness_settings/orchestrator_requirements.yaml`,
retained the same five-source evidence and authority boundary, and produced a
passing receipt before any plan artifact was created.

This is a recurrence of
`orchestrator.orchestrator_receipt_continuation_event_vocabulary_mismatch`.
The strengthened prevention control is mechanical: list the configured events
through the preflight CLI before writing each runtime state and select from
that output, rather than relying on memory or prose.
