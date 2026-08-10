# Context Fabric durability behavior generation-lock RLS recovery

Date: 2026-08-10

Behavior attempt 035 stopped fail closed at `BTR-E04` with SQLSTATE `CF004`
inside `apply_durability_transition_v1` line 143. The owned disposable PostgreSQL
container was removed and its exact ID was independently absent. No scenario
committed and the last accepted mutable behavior evidence was restored byte
exact.

Repository-only diagnosis binds the failure to the second exact lock in the
entry point: `context_observer_generation` is read `FOR UPDATE`. The coordinator
already has the sole execute grant for this transition and the typed body has
ten coordinator-owned generation state transitions, but `pol_cf_06_update`
admitted only `LIFECYCLE`. With forced RLS, PostgreSQL therefore hid the row from
the coordinator at lock time even though the SELECT policy admitted it.

The bounded repair adds the existing `COORDINATOR` capability to both the USING
and WITH CHECK predicates of `pol_cf_06_update`, alongside `LIFECYCLE`. It does
not add a role, entry point, direct table SELECT or DML grant. The coordinator
continues to reach the relation only through the existing security-definer
transition function, whose typed program, row predicates and invariants are
unchanged.

The structural contract and schema are resealed, the unchanged typed body is
rebound to that exact parent, and the inert artifact is regenerated. Fresh
parse/catalogue proof, behavior-parent rebind and independent exact-HEAD veto
remain prerequisites to another behavior execution.

This recovery is provider-free and repository-local. It grants no product,
patient, clinical, runtime-wiring, command, deployment, release, Pages or
protected-ref authority.
