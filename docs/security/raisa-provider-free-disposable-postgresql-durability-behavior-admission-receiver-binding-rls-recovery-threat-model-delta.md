# Threat-model delta — admission-receiver binding RLS

Date: 2026-08-10

Behavior attempt 031 exposed a fail-closed availability defect: forced RLS
contradicted the accepted admission receiver's exact binding-table `SELECT`.
No admission or tenant-crossing row was released.

The repair preserves these security invariants:

- `current_user` is limited to exactly `context_schema_owner` and the existing
  non-login `context_admission_receiver`;
- `database_login = session_user` remains mandatory, so security-definer
  ownership cannot select another login's binding;
- both active-time predicates remain mandatory;
- the receiver remains `NOLOGIN`, `NOINHERIT` and `NOBYPASSRLS`, owns only the
  admission function, and gains no role membership or new direct grant;
- the observer remains the authenticated `session_user`, receives no binding-
  table grant and cannot become the admission owner;
- missing, duplicate, inactive, cross-practice, cross-source, cross-stream or
  wrong-capability rows continue to fail before effect; and
- hostile tests reject removal of receiver visibility, addition of any third
  owner, loss of the session-user fence or loss of either time fence.

Changing function ownership, disabling or bypassing RLS, adding a runtime
principal to the owner allowlist, or weakening strict cardinality is outside
the repair. Every runtime, product/patient, provider, application, command,
deployment, release, Pages and protected-ref surface remains closed.
