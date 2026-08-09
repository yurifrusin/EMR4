# Ariadne agent error and correction register revision 147

Date: 2026-08-10

Status: corrected; descendant proof pending

Revision 147 adds AER-0172 and brings the register to 172 bounded incidents
with zero open incidents.

## AER-0172 — admission receiver absent from binding RLS

Behavior attempt 031 progressed to `BTR-E03` and failed safely with `CF004`,
zero completed scenarios and verified exact-container cleanup. Deterministic
source reconciliation proved that the distinct non-login
`context_admission_receiver` had its accepted exact binding-table `SELECT`,
but forced RLS exposed a row only while `current_user` was
`context_schema_owner`. The admission function is deliberately
`SECURITY DEFINER` under the receiver, so its exact session-bound row was
invisible and the strict lookup failed closed.

The corrected control permits exactly the existing two non-login function
owners as `current_user` while retaining `database_login = session_user`, both
active-time fences, forced RLS, existing table privileges and privilege
separation. It adds no role, membership, login, grant, RLS bypass, body program
or scenario authority. Hostile tests reject a missing receiver, any third
owner and loss of either the session or time fence.

Another behavior runtime remains closed until the unchanged typed body is
rebound, the inert artifact is regenerated and recognized, fresh PostgreSQL
parse/catalogue characterization and exact reproduction pass, the behavior
parent is rebound, the complete deterministic packet passes and a fresh
independent veto accepts the exact candidate.
