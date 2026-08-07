# Ariadne agent-error register revision 66

Date: 2026-08-07

Status: exact-veto recovery precommit inventory omission corrected

Revision 66 adds AER-0065. The first exact-veto recovery precommit runtime
state omitted the configured `deepseek-flash-workers` slot because the pool had
no active or stale instance. The orchestrator preflight correctly failed closed
with `worker_slot_inventory_missing:deepseek-flash-workers`; no staging,
commit, worker dispatch or candidate change occurred.

The failed v2 state and receipt remain preserved. The distinct v3 state records
the complete required inventory, including the zero-instance DeepSeek pool and
the zero-instance native recovery pool, and its five-source receipt passes.
Future runtime states must represent required empty pools explicitly.

No SQL, DDL, database, source, provider, runtime, product/patient data,
deployment, Pages or protected-ref boundary opened. Revision 66 contains 65
bounded incidents; counts remain workflow-improvement signals only.
