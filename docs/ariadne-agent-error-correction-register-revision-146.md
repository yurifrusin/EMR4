# Ariadne agent error and correction register revision 146

Date: 2026-08-10

Status: corrected; descendant proof pending

Revision 146 adds AER-0171 and brings the register to 171 bounded incidents
with zero open incidents.

## AER-0171 — support-function execute-role field mismatch

Behavior attempt 030 progressed through `BTR-E02` and failed safely at
`BTR-E03` with `42501`, zero accepted scenarios and verified exact cleanup.
Deterministic source reconciliation proved that the accepted support signature
stores its eight exact grantees as `executor_roles`, while the inert DDL
renderer read the absent key `execute_roles`. `PUBLIC` execute was correctly
revoked, so the renderer emitted no replacement grants and the admission
security-definer owner could not call `session_binding_allows_v1`.

The repaired control renders the exact ordered `executor_roles` population and
tests equality between the accepted signature and the emitted
signature-qualified grants. It permits no new role or authority and rejects
missing, duplicated or additional grantees.

Another behavior runtime remains closed until artifact recognition, fresh
parse/catalogue characterization and exact reproduction, behavior-parent
rebind, the complete deterministic packet and a fresh independent veto pass.
