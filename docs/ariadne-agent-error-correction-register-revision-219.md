# Ariadne agent error and correction register — revision 219

Date: 2026-08-11

Revision 219 records AER-0254 and brings the register to 254 bounded known
incidents.

## AER-0254 — register peer-link and count correction

The first AER-0253 draft correctly preserved the refused AES-C3 dispatch
receipt, but it added AER-0080 as a one-way `related_incident_ids` peer and did
not yet advance the maintained population assertions. The validator rejected
the asymmetric link with `attempt peer linkage mismatch for AER-0253`, while
the focused test exposed the stale expected agent-incident count. Pattern
generation stopped and no worker, provider or model call followed.

The corrected register leaves AER-0253's peer list empty and uses its exact
historical recurrence signature—
`orchestrator.worker_dispatch_continuation_event_and_assignment_envelope`—for
grouping. This distinct incident preserves the failed validation, advances the
register to revision 219 and updates maintained population assertions before a
fresh pattern-report generation and full focused validation.

Neither incident changes candidate source, authority, provider state,
protected refs or the clean isolated AES-C3 worktree.
