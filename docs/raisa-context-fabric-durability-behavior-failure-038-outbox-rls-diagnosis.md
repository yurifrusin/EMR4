# Context Fabric durability behavior failure 038: outbox RLS diagnosis

Date: 2026-08-08

Status: deterministic repository diagnosis complete; no further PostgreSQL run opened.

Attempt 038 stopped safely in `BTR-E04`. The coordinator call changed the
observer generation instead of applying the admitted observation, so the
relation-delta gate rejected the run. The exact failure evidence is preserved
immutably and the disposable container was removed with exact-ID absence
verified.

The accepted typed body requires `apply_durability_transition_v1` to read the
exact source position from
`emr4_context_fabric.diary_context_observation_outbox_v1`. That relation has
forced row-level security, while `pol_cf_03_select` currently admits only the
`PRODUCER`, `OBSERVER` and `RETENTION` logical capabilities. It omits the
`COORDINATOR` capability used by this security-definer call. The source set is
therefore empty inside the protected function; its closed source-ambiguity path
truthfully applies `REBASE_APPLIED`, including the observed generation change.

The bounded repair is to add `COORDINATOR` to the existing outbox SELECT policy
only. It adds no direct table grant or DML, preserves forced RLS, changes no
function body or scenario population, and requires deterministic regeneration
and fresh catalogue/behavior proof. The behavior harness must also require the
exact result kinds `RECEIPT_APPLIED` for `BTR-E04` and `RECEIPT_REPLAYED` for
`BTR-I03`; widening the allowed relation-delta set would conceal a safety
failure and is explicitly rejected.

This is provider-free, unmounted repository work. It grants no application,
API, Diary, product-data, patient-data, operational database, deployment,
release, Pages or protected-ref authority.
