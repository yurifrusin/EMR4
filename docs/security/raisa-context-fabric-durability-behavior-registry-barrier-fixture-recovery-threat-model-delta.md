# Context Fabric behavior registry-barrier fixture recovery threat-model delta

Date: 2026-08-08

Status: provider-free recovery candidate

## Security boundary

This correction changes only authored-synthetic bootstrap and private behavior
proof logic. It does not change the accepted body contract, inert SQL,
database privileges, RLS, scenario population, runtime role, Docker profile or
evidence claim boundary.

Bootstrap runs under its already separate disposable setup authority and is
not evidence that `context_lifecycle` can insert Fabric rows directly. The
measured behavior still begins only after fresh session authorization to the
named runtime role.

## Threats and controls

| Threat | Control | Required proof |
|---|---|---|
| A missing prerequisite is mistaken for entry-point rejection | Reconcile every pre-effect `SELECT_EXACT`/`LOCK_EXACT` with the closed bootstrap fixture | Alpha barrier exists at revision 0 before BTR-E01 |
| Bootstrap silently grants lifecycle direct barrier authority | No grant changes; setup authority remains outside the behavior claim | Existing privilege catalogue and denied role matrix remain exact |
| Fixture creation is counted as a runtime effect | Barrier row delta is exactly zero during BTR-E01 | Before/after count is stable and digest changes only on the allowlist |
| Registration fails to serialize or advance the barrier | Private readback requires one exact alpha barrier at revision 3 | Three separate successful serializable registrations and exact revision proof |
| The repair weakens scenarios or accepted SQL | Contract digest and scenario objects remain byte-semantically unchanged; parent hashes remain exact | Deterministic contract tests and exact baseline diff |
| Prior failure evidence is overwritten | Attempt 016 is immutable and byte-equal to the former mutable evidence | SHA-256 `f5b7a272d52586ec1772f4906a6f7a26f58620efea944f61199b99c3ab4215ef` |

## Residual boundary

This proof remains serial and authored-synthetic. It does not prove
multi-session races, load, operational migration, live watcher behavior,
product data, provider/model execution, deployment or production suitability.
The future Agent Execution Surface and Containment Gate remains a separate
prerequisite before any occupied Bureau may execute tools or commands.
