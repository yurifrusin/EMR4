# Threat-model delta — durability support-function execute grants

Date: 2026-08-10

The observed `42501` is a fail-closed availability defect in the inert DDL
renderer. It released no admission, crossed no tenant boundary and widened no
command authority. The repair restores only the eight support-function execute
grants already fixed by the accepted function/body contract.

Security invariants:

- `PUBLIC` execute remains revoked from `session_binding_allows_v1`;
- the emitted grantee population equals the contract's ordered
  `executor_roles` set exactly, with no missing, duplicate or additional role;
- every grant names the exact support-function signature, so overload drift
  cannot broaden it;
- the support helper remains security-definer, strict and owned by
  `context_schema_owner`; entry-point owners, RLS, tables, DML and function
  bodies remain unchanged;
- hostile recognition rejects grant removal, substitution or addition; and
- all runtime, patient/product, provider, application, command, deployment,
  release, Pages and protected-ref surfaces remain closed.
