# Ariadne agent error and correction register — revision 174

Date: 2026-08-10

Revision 174 records AER-0200 through AER-0202 and raises the bounded incident
population to 202.

AER-0200 records a fail-closed orchestration-envelope error: the first behavior
attempt 036 pre-execution state used unsupported descriptive continuation event
`pre_execution`. The receipt returned `revision_required`, dispatched nothing
and opened no container. The corrected fresh envelope used the approved
`pre_worker_dispatch` event and retained the same closed authority.

AER-0201 records two low-severity local command-construction mistakes during the
post-run exact-ID absence recheck: one incorrect Docker executable path failed
before Docker, and one PowerShell display expression failed after an inspect.
The corrected command resolved Docker, inspected only the exact owned container
ID and confirmed it absent without enumerating or touching unrelated containers.

AER-0202 records the material repository defect exposed by disposable behavior
attempt 036. The anchor existed for an exact plain read but became invisible to
the immediately following `FOR SHARE` under forced RLS because
`context_recovery_anchor` lacked a lock-only UPDATE policy. The bounded repair
adds exact COORDINATOR/LIFECYCLE lock visibility while `WITH CHECK ... AND
FALSE`, zero direct DML and the append-only invariant continue to prohibit
mutation.

No incident remains open. A fresh downstream body rebind, inert regeneration,
parse/catalogue reproduction, independent veto and disposable behavior attempt
are still required before the repaired candidate can be accepted as behavior.
