# Provider-free durability behavior support-function execute-grant recovery

Date: 2026-08-10

Status: bounded renderer recovery candidate; behavior runtime remains closed

Behavior attempt 030 stopped safely at `BTR-E03` with PostgreSQL `42501`,
completed zero of the frozen twenty scenarios and removed its exact owned
container with absence verified. The immutable failure is
`provider-free-behavior-transaction-failure-evidence-030.json`.

No diagnostic PostgreSQL run was needed. Exact source mapping proves that the
accepted function/body contract names eight `executor_roles` for
`session_binding_allows_v1`, including the non-login
`context_admission_receiver` that owns the proofread-admission security-definer
function. The inert artifact revokes `PUBLIC` execute on the support function,
but the renderer looked for the absent field name `execute_roles` and therefore
emitted none of the eight already-specified grants. The admission owner could
not call the helper used by its body and forced-RLS policies.

The bounded repair changes that renderer lookup to the effective contract's
exact `executor_roles` field. It emits one signature-qualified grant for each
of the eight ordered contract roles and no other grantee. This does not invent
a role, privilege, function, entry point or authority: it faithfully lowers the
accepted structural contract whose support-function execute surface was
previously omitted.

Before another behavior attempt, hostile tests must prove exact grant equality
and reject missing, duplicated, reordered or additional grantees; the inert
artifact must be resealed; fresh PostgreSQL parse/catalogue characterization
and distinct exact reproduction must pass; the behavior parents must be
rebound with all twenty scenarios unchanged; the complete deterministic packet
and a fresh Gemini 3.6 Flash/high exact-HEAD veto must pass.

This recovery grants no migration, operational database, source,
watcher/listener/feed, patient/product data, provider, command, application/API/
Diary wiring, deployment, production, release, Pages or protected-ref
authority.
