# Ariadne agent error and correction register — revision 296

Date: 2026-08-15

Timestamp: 2026-08-15T22:21:41+10:00 (Australia/Brisbane)

Revision 296 records AER-0335. At this revision the register contains 335
bounded known incidents, all corrected or contained by an explicit control.

AER-0335 preserves a rejected DeepSeek predispatch draft. It used the invalid
parallelism disposition `active` and omitted the required
`at_handoff_current` workspace field. Deterministic preflight rejected the
draft before dispatch or any worker/model call.

The distinct correction uses the admitted `dispatched` disposition and exact
`at_handoff_current: true` field. Its fresh receipt passed before the worker
launched. This incident joins the existing
`orchestrator.worker_dispatch_runtime_contract` recurrence; future worker
predispatch objects must be copied from a passing stage-equivalent shape and
validated before launch.
