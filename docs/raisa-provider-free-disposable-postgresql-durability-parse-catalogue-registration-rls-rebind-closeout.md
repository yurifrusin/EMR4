# Disposable PostgreSQL parse/catalogue registration-RLS rebind closeout

Date: 2026-08-08

Result:
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`

Source artifact commit:
`2c22d6f56d0081ebfae5a5585088381e1219d7f8`

## Exact result

The corrected lifecycle-registration RLS artifact parsed and installed
atomically in PostgreSQL 16 and reproduced every exact catalogue and privilege
digest. The canonical artifact remains 412 statements and 1,402,659 LF bytes
with SHA-256
`sha256:34d321adce220a94473e3cd74173f7b0ffc37441b2e4dd24699ca18b86c7e760`.

The parse contract is canonical SHA-256
`sha256:b88de787d50869b2a8366d0f3d02c387cbbcf7462102e5c70def8dad80992aa9`.
The exact pass evidence has file SHA-256
`sha256:44f4ba03cc25abfc437ca3385b7f8e0c335477dec0724d3726058f78d37170bc`.

## Characterization and correction boundary

PostgreSQL's canonical `pg_policies` projection changed exactly as expected
for the six repaired policy predicates. One nonpassing characterization bound
the revised policy digest as
`sha256:7c847b9d0e153bb02101bc3704d33d72e8aefdf4cfc911e0b092149393cc1b37`.
Its immutable evidence is SHA-256
`sha256:d46af8f0ae45f0b79b0ca81a8a09728b046747486399c8ac0646772073657726`.
Every other exact digest matched the accepted predecessor. Both disposable
containers were removed by captured ID and absence was verified.

The repaired policy set adds only the `LIFECYCLE` principal to the exact
`SELECT` or `INSERT` policies required by generation registration. Matching
`UPDATE` policies, direct grants, roles, functions, triggers, relations and
the 44-policy population remain unchanged.

## Verification and claim boundary

The complete parse/catalogue and plan-test packet passes, together with Ruff
and `git diff --check`. The accepted claim remains limited to PostgreSQL 16
parse, rollback, atomic installation, exact catalogue/privilege shape and
exact cleanup. It proves no function, trigger, RLS enforcement, transaction
or behavior scenario.

The next dependency is to rebind the unchanged twenty-scenario behavior
contract to this exact pass evidence and corrected parents, run the complete
deterministic and hostile packet, obtain one fresh exact-HEAD Gemini 3.6
Flash/high veto, and only then execute attempt 019.

Applied migration, operational credentials or persistence, source watcher or
listener, application/API/Diary wiring, product or patient data, provider,
tool, command, deployment, production, release, Pages and protected refs
remain closed.
