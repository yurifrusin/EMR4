# Threat-model delta — check-in server start/attach created-state failure-coordinate diagnosis

Date: 2026-08-23

Timestamp: 2026-08-23T02:11:15.3452260+10:00 (Australia/Brisbane)

Status: `frozen`

Reasoning level: `high`

## Scope

This delta covers exact source and immutable-terminal inspection, two fixed
read-only local Docker CLI metadata commands, deterministic process fakes and
one closed sanitised diagnostic coordinate. It adds no Docker object,
PostgreSQL process, SQL, database attempt, provider, product, data, ordinary-
practice, production, deployment, release, Pages or protected-ref surface.

## Threats and controls

| Threat | Control | Fail-closed result |
|---|---|---|
| A model invents a plausible root cause from a generic nonzero process | One closed coordinate vocabulary distinguishes observation from attribution | `insufficient_closed_evidence` or reject |
| CLI inspection accidentally starts or names an object | Fixed command manifest admits only `docker.exe version` and `docker.exe start --help`; reject all caller arguments and object tokens | Stop before subprocess |
| Raw help, stderr, paths or environment leak into evidence | Retain only fixed booleans, bounded version token, return codes and SHA-256 digests | Reject evidence |
| Attempt 006 is retried, overwritten or reclassified | Byte-exact terminal hashes, exclusive output creation and no executable database path | Reject tranche |
| A deterministic fake silently invokes a real process | Dependency-injected runner plus hostile tests asserting zero real Docker, PostgreSQL, network and provider calls | Reject test/evidence |
| Contradictory host-process and OCI facts choose a confident coordinate | Exact predicate matrix; missing, extra or contradictory relations become insufficient or invalid | Reject classification |
| CLI version or source drift is ignored | Bind exact source SHA-256, full Git ancestry, closed argv AST and recorded CLI metadata | Reject source mapping |
| Diagnosis smuggles in a repair or attempt 007 | Report may name only the smallest future repair surface; implementation and occupied-run fields are forbidden | Reject closeout |
| Product or API authority expands through rehearsal language | Static path and exact-boundary tests deny product/API/configuration/ordinary-practice mutations | Stop before commit |
| Unrelated worktree data is damaged | Explicit-path staging and preservation checks; no broad cleanup | Stop without mutation |

## Residual boundary

The diagnosis can prove that a valid advertised composite start/attach command
returned nonzero while the captured OCI state remained `created`. Without a
future closed observer or a separately repaired phase boundary it cannot prove
whether the engine rejected start, attach failed, the container initialization
path failed before transition, or the host platform supplied another pre-
running condition. It proves no database, transaction, product or production
readiness.
