# Ariadne agent-error register revision 78

Date: 2026-08-08

Status: R7 worker predispatch envelope corrected before dispatch

Revision 78 adds AER-0080. The first R7 worker predispatch runtime state used
the unapproved `pre_dispatch` continuation event and declared an assigned agent
without a workspace receipt. The preflight correctly returned
`revision_required`; no worker was dispatched from that receipt.

The distinct v2 state uses `pre_worker_dispatch`, leaves pre-assignment
`assigned_agent_ids` empty, inventories the managed and native worker slots and
produced a passing five-source receipt before the follow-up task was sent. The
failed envelope remains preserved as workflow evidence.

Revision 78 contains 80 bounded incidents. Incident counts remain
workflow-improvement signals only.
