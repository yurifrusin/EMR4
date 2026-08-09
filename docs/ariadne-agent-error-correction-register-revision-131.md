# Ariadne agent error and correction register revision 131

Date: 2026-08-09

Status: bounded register correction candidate

Revision 131 adds AER-0156 and brings the register to 156 bounded incidents
with zero open incidents.

## AER-0156 — repeated unapproved pre-execution continuation event

The first RLS lock-visibility parse-characterization runtime state used the
descriptive event `pre_execution`. The deterministic Ariadne preflight rejected
it as `continuation_event_missing_or_unapproved` before any Docker or
PostgreSQL contact, returned no rehydration sources and granted no dispatch.

The failed state and receipt remain immutable. The distinct corrected state
uses the admitted `pre_worker_dispatch` event while preserving the exact
characterization-only contract, networkless/no-pull containment, five sources
and exact-ID cleanup boundary. This recurs from AER-0152; the prevention rule is
therefore strengthened to copy the event directly from
`orchestration/harness_settings/orchestrator_requirements.yaml` before drafting
the rest of any execution state.
