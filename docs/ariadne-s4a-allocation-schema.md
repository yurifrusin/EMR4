# Ariadne S4a Allocation Schema

Date: 2026-07-11

S4a establishes a strict, portable configuration surface for the proposed
Conductor and Verifier. It is deliberately data-only: it does not probe an
agent, invoke a CLI, launch a worker, alter a worktree, or change EMR4 runtime
behaviour.

## Settings

| Artifact | Purpose |
|---|---|
| `orchestration/harness_settings/project.yaml` | Project authority split and allocation protocol flags. |
| `orchestration/harness_settings/worker_pool.yaml` | Stable user-declared resources: provider/account, access mode, transport, transport quirks, model/reasoning default, concurrency ceiling, quota class, capabilities, and cost tier. |
| `orchestration/harness_settings/role_preferences.yaml` | Ranked SSDLC role preferences, with rationale and review date. |
| `orchestration/harness_settings/user_overrides.yaml` | Explicit, durable user overrides. Empty by default. |
| `orchestration/harness_settings/generalist.yaml` | Single-resource fallback and its compensating controls. |

Transport is not availability. The worker pool records how a resource is
reached; a future `AvailabilityProbe` records a time-bounded observation of
reachability and quota state. A bridge result must never be interpreted as a
capability, authority, or subscription-quota result.

## Typed Exchange Records

`orchestration_harness.allocation` validates these exact records:

- `WorkerResource`, `RolePreference`, `UserOverride`, and `GeneralistProfile`
  for settings;
- `AvailabilityProbe` for separately observed reachability and availability;
- `AssignmentRecord` and `ConductorPlan` for a reproducible allocation;
- `VerifierResult` whose decision is only `pass` or `revision_required`.

Every submitted plan carries a settings fingerprint. The verifier result must
repeat it so the orchestrator can reject a plan checked against different
settings. `orchestrator_substituted` is an explicit false-by-default field:
the intended later verifier rejects a true value, rather than allowing silent
assignment drift.

## Boundary

S4a is advisory schema and tests only. The next proposed slice, S4b, is a pure
allocator/replay engine over synthetic availability probes and the settings
above. It remains closed until the user authorizes that next slice. No live
adapter, model execution, sandbox provisioning, credential handling, worktree
write, commit, push, database, provider, deployment, or release authority is
enabled by these files.
