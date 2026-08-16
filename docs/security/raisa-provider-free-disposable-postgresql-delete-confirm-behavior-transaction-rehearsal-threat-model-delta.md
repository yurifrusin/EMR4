# Threat-model delta — disposable PostgreSQL delete-confirm behavior/transaction rehearsal

Date: 2026-08-16

Timestamp: 2026-08-16T11:52:20+10:00 (Australia/Brisbane)

Source HEAD: `87f352aa1d2a9bc9366e20032f6c9a2fd1b6fe67`

## Scope

This delta covers one serial authored-synthetic execution of exact migration
`x3y4z5a6b7c8`, its database-owned authority/grant triggers and the exact
unmounted delete-confirm SQLAlchemy transaction seam in one owned internal-
network, tmpfs PostgreSQL 16 container through a fixed loopback relay.

## Threats and controls

| Threat | Frozen control |
|---|---|
| The harness reaches an operational database | The SQLAlchemy URL is internally constructed from one operating-system-selected `127.0.0.1` relay port and fixed synthetic credentials; each relay child targets only the captured container ID and literal container-loopback PostgreSQL endpoint. Caller URLs, hosts and ports are rejected. |
| The container or relay becomes external network authority | The container's sole Docker network is uniquely owned and `--internal`; no Docker port is published; the only host listener is exact IPv4 loopback; `--pull=never` forbids registry retrieval. |
| The relay becomes a generic command surface | Its argv, `shell=False`, captured container ID and container-side Bash command are frozen. No caller value enters executable text. |
| Data or runtime state persists | PostgreSQL uses container-local tmpfs only. Bind, named-volume, workspace and Docker-socket mounts are forbidden. The relay stops and exact owned resources are removed in `finally`. |
| Cleanup removes another object | Reverify exact captured IDs, names, image, labels, internal-network membership, tmpfs, bounds and emptiness. Remove container first and network second; otherwise refuse. |
| The minimum schema overstates compatibility | The claim is limited to selected mapped columns/correlation constraints and exact migration behavior. Full historical-chain, application-schema, route and production compatibility remain excluded. |
| Fixture grant DML becomes product provisioning | Only fixed partitioned synthetic cases may create transient rows in the owned database. No application administration path, product user or durable grant exists. |
| Caller claims or role membership grant cancellation | PostgreSQL row presence is the only grant; absent grant, stale generation, inactive user and role mismatch all fail before idempotency access. |
| Generation can be selected, skipped or wrapped | Insert forces one; direct submitted generations are ignored; each qualifying membership/grant change advances once; duplicates do not advance; overflow aborts and rollback digests must match. |
| Capability identity is broadened or reassigned silently | The closed check admits two exact codes, updates are rejected, and reassignment is delete then insert with each parent independently fenced. |
| Receipt bytes leak after revocation or corruption | Both complete current-authority checks precede classification; replay requires exact family-qualified complete v1 fields and constant-time canonical-byte integrity; denial cases retain zero disclosure. |
| Lock order is inferred from source rather than exercised | The real SQLAlchemy connection records only value-free statement classes and must reproduce user, appointment, grant, select-first idempotency, insert-if-absent, winner-lock and second-authority order. |
| The 2000 ms timeout resets per statement | A controlled monotonic-clock case exhausts the one cumulative deadline before a later access and must roll back the claim. No contention or concurrency claim is made. |
| A partial or mismatched write survives | Empty, partial and cross-artifact-mismatched sets must trigger the seam's completeness guard and restore exact before digests; a complete-set outer abort must also restore all three artifacts. |
| Replay performs a second cancellation | Response-loss retry must return only the stored canonical-byte digest with unchanged appointment version and audit/receipt counts. |
| Evidence retains credentials or sensitive fixture values | Evidence is schema-closed to fixed IDs, categorical results, counts, state versions, hashes, value-free statement tokens and cleanup facts. Raw SQL, URLs, passwords, session digests, response bodies, logs and rows are forbidden. |
| Workflow reform removes a hard Tier-2 control | The pre-edit baseline, semantic freeze, deterministic admission, immutable failures, exact cleanup, protected-ref checks and exactly one final independent veto remain mandatory; only redundant reruns and stacked reviews are removed. |

## Residual risks

This serial rehearsal does not prove contention, deadlock behavior, concurrent
idempotency races, restart, crash, unknown commit, durable recovery,
administrative provisioning, full migration-chain compatibility, route/adaptor
behavior, public response transition, UI behavior, performance, retention or
production operations. Controlled monotonic exhaustion proves deadline use, not
real lock-wait timing under contention.

## Authority boundary

No existing/product database, durable product data, route mount/call, public API
or UI change, patient/clinical/product/protected data, provider/ADC/credential/
IAM/browser authority, external network, watcher/event authority, deployment,
production, release, Pages or protected-ref action is opened. `docs/branding/`
and every unrelated untracked path remain preserved and excluded.
