# Threat-model delta — check-in rollback and unknown-commit recovery rehearsal

Date: 2026-08-19

Timestamp: 2026-08-19T17:02:15.2064647+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `26402cb8667c2dbf62e86c6eb4c0b000d274559e`

## Scope

This delta covers one provider-free, uniquely named, disposable PostgreSQL 16
rehearsal of an authored-synthetic three-member command packet. It proves a
pre-commit rollback has zero effect and a caller-level lost complete response
is resolved by exact restricted-role readback without retry or duplicate
effect. It opens no product, ordinary-practice, provider, deployment or
protected-ref authority.

## Assets

- exact source and full 40-character Git bindings;
- closed transaction manifest and complete-request digests;
- ephemeral runtime-role credential held only in process memory;
- one admin-owned forced-RLS receipt/effect/audit probe;
- one complete-terminal-response boundary;
- authoritative readback and pure fail-closed classifier;
- zero ordinary-admission release invariant; and
- captured role, relay, container and network cleanup identities.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Manifest becomes command or policy authority | Closed declarative schema; typed code and PostgreSQL enforce; manifest cannot dispatch, activate or release. |
| Seven-character or unresolved Git binding | Full lowercase 40-character schema plus exact hash/source verification before Docker. |
| Rollback leaves a partial receipt/effect/audit packet | All three writes share one transaction; post-rollback restricted-role counts and canonical empty digest must be exact. |
| Connection loss is mistaken for commit or rollback | Caller result is `unknown`, success is false, readback is mandatory and retry is false. |
| Timing or known cutpoint leaks into classification | Pure classifier accepts only closed readback packet plus expected request digest; no scenario, timing, PID, log, WAL or raw client input. |
| Automatic retry duplicates an effect | Fixed retry counter remains zero; no command reissue exists; unique identities and exact-one readback are mandatory. |
| Partial or contradictory durable state is accepted | Only exact one receipt/effect/audit with matching identities/digests classifies committed; every other nonzero shape is `unresolved_denied`. |
| Cross-tenant readback or write | Admin-owned forced RLS on all three relations; transaction-local practice; restricted role is non-owner and `NOBYPASSRLS`. |
| Runtime role escalates or owns probe/product objects | Catalogue checks negative capabilities, memberships and ownership; grants are exact and product privileges zero. |
| Backend termination targets an unrelated session | Unique closed application label, exact single PID readback, allowlisted `Timeout/PgSleep`, and one exact `pg_terminate_backend` target. PID is never serialized. |
| Parent joins before consuming the child result and manufactures a liveness timeout | Consume exactly one closed queue result within the existing bound before `Process.join()`, then require exit within five seconds and exit code zero; preserve the first fail-closed artifact and permit only the addendum's one explicit recovery execution. |
| Docker-exec relay sees PostgreSQL EOF but never tells the loopback client | A rehearsal-local relay half-closes the client-facing write side in the downstream copier's `finally`; a provider-free socket/subprocess regression proves EOF propagation while upstream remains open. The shared predecessor relay is unchanged. |
| A later failure overwrites an earlier sanitized attempt | Every failure is written first to the first absent three-digit attempt path and never overwrites a numbered attempt; the generic latest-failure file is only a convenience projection. |
| A post-commit hold is overstated as literal COMMIT uncertainty | Claim explicitly limited to loss of the harness-defined complete terminal response after one commit; no WAL/protocol/crash claim. |
| Credential or runtime identifier leaks into evidence | Recursive forbidden-key/value scanner, closed schemas and digest/count-only release. |
| Cleanup deletes unrelated resources | Captured IDs plus exact label, nonce, image/name/profile reverification; names/discovery are never deletion authority. |
| Failed cleanup is hidden by a pass | Role absence precedes teardown; relay/container/network exact absence is a terminal acceptance condition. |
| Probe evidence activates ordinary practice | Canonical ordinary record/release counts remain zero; no app/config/API/client source is editable. |
| DeepSeek transport silently falls back | Occupied native Harness and Claude Code fallback are both forbidden; lane remains declined until separate boot proof. |
| Protected or user-owned material is swept into Git | Protected evidence remains unopened; explicit-path staging only; `docs/branding/` and all unrelated untracked files remain preserved. |

## Negative-evidence boundary

The stopped CF-D2 crash/restart attempts demonstrate that broad relation and
recovery-anchor packets can obscure the exact failing terminal coordinate.
This tranche deliberately uses three relations, two transaction outcomes and
one closed classifier. It imports no CF-D2 runtime, anchor, restart or success
claim, and it does not reinterpret either stopped attempt.

## Residual risk and closed claims

The rehearsal does not test a crash during COMMIT, wire acknowledgement loss,
container/database restart, WAL or power-loss durability, network partitions,
driver/pool retries, concurrent commands, operational credentials, existing or
product schemas, live rotation/custody, real practices, patients, appointments,
production monitoring or operator recovery.

No GraphQL mutation, REST endpoint, async authority, product database write,
ordinary enablement, feature/allowlist change, generic-status `Arrived`, action
grammar, client, waiting-area behavior, provider, production runtime,
deployment, release, Pages, protected evidence or protected ref is opened.
