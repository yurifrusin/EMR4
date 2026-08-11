# Threat-model delta — CF-D2 restart and unknown-commit recovery rehearsal

Date: 2026-08-11

Status: `frozen_provider_free_planning_runtime_closed`

## Assets and trust boundaries

Protected assets are the exact accepted inert SQL bytes, authored-synthetic
fixture scope, least-privilege role/RLS boundary, atomic transition state,
independent recovery anchors, minimized evidence, captured container identity,
all unrelated workspace files and protected Git refs.

New trust boundaries are the one-shot client terminal-result boundary, the
container process-crash boundary, same-cluster restart identity and the pure
post-restart recovery classifier. Docker control remains Sol-owned and may act
only on the exact nonce-labelled captured container ID.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Connection loss is treated as success | `CONNECTION_LOST_WITHOUT_ALLOWLISTED_TERMINAL_RESULT` carries no outcome; complete post-restart durable classification is mandatory. |
| Connection loss is treated as rollback and blindly retried | Retry is forbidden until exact zero-residue and prior-anchor equality prove `ROLLED_BACK_RECOVERED`. |
| A partial transaction is accepted | Every receipt, checkpoint, lifecycle, audit, watermark, frame and obligation member must match one complete committed packet; mixed state is terminal failure. |
| Harness schedule leaks the expected answer into recovery | The pure classifier accepts no scenario id, cutpoint, timing, output or expected class; it receives only canonical post-restart durable facts. |
| A graceful restart substitutes for crash recovery | Each scenario requires exact `SIGKILL`, stopped-state proof and start of the same captured ID/cluster. |
| Restart silently creates a fresh cluster | System-identifier digest, catalogue/role identity and pre/post relation digests are bound; cluster drift fails. |
| The official image creates an orphan anonymous volume | The declared default volume path is shielded by tmpfs; the actual `PGDATA` is in the owned writable layer; Docker metadata must show zero bind/named/anonymous volumes. |
| Weak durability settings make the evidence misleading | `fsync`, `synchronous_commit`, `full_page_writes` and data checksums are exact preconditions before and after each restart. |
| Coordinator infers or self-authorizes a recovery anchor | Only `context_lifecycle` may call the accepted anchor entry point, which rederives the complete committed state; the next transition remains fenced by exact `CF303`. |
| Superuser readback becomes participant authority | Owner-only observation is fixed to canonical counts/digests and cannot call measured entry points; participants use exact least-privilege session identities. |
| Raw client/server/WAL material leaks into evidence | Evidence schema admits only closed labels, counts, SHA-256 digests, bounded durations and stable reasons; stdout/stderr fragments, logs, WAL, query text and PIDs are forbidden. |
| Crash cleanup damages unrelated resources | Kill, start and removal require exact name/nonce/image/network/port/mount/storage/state reverification of the captured ID; no global deletion is allowed. |
| The rehearsal is mistaken for operational recovery | Claim boundary explicitly excludes drivers, pools, arbitrary crash points, power loss, availability, migration, application wiring and real data. |

## STRIDE delta

- **Spoofing:** exact container nonce/ID, cluster identity and session-user
  markers prevent substitution.
- **Tampering:** exact parent hashes, immutable SQL, whole-document schemas and
  canonical row digests expose changed source or partial state.
- **Repudiation:** closed client observation and crash/restart lifecycle labels
  preserve whether a terminal result existed without retaining raw output.
- **Information disclosure:** only opaque authored-synthetic coordinates and
  minimized digests are admissible; all product, patient and provider surfaces
  remain closed.
- **Denial of service:** fixed four crashes, timeouts and one container bound
  resource use; no restart loop or automatic retry exists.
- **Elevation of privilege:** measured transactions retain accepted dedicated
  roles/RLS; lifecycle anchor authority is separate from coordinator authority.

## Residual risk and claim limit

The fixed post-commit hold occurs after PostgreSQL has processed `COMMIT`, and
the pre-commit hold occurs before it. This gives two lost-terminal-result
branches without claiming instruction-level uncertainty inside WAL flush or
wire acknowledgement. Host power loss, storage caches, filesystem behavior,
driver cancellation, pools, replicas, backup/restore and operational recovery
remain untested.

Passing evidence therefore supports only the four frozen authored-synthetic
same-cluster PostgreSQL process-restart cases. It grants no real source,
patient/product data, provider, application command, migration, deployment,
production, release, Pages or protected-ref authority.
