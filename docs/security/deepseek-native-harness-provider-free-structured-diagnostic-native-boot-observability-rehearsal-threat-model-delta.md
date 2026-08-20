# Threat-model delta — structured diagnostic native-boot observability rehearsal

Date: 2026-08-21

Timestamp: 2026-08-21T09:41:43.2918015+10:00 (Australia/Brisbane)

Operation:
`deepseek-native-harness-provider-free-structured-diagnostic-native-boot-observability-rehearsal`

## New boundary

One real pinned rc.7 JavaScript entrypoint executes inside a controller-owned
disposable root through the accepted structured-diagnostic wrapper. The only
durable runtime output is one validated v2 terminal outside that root plus a
closed canonical evidence projection after cleanup.

No task argument, worker session, broker, tool call, model or provider request
is present. The authored absent profile forces rejection before Cordis boot and
the first HMR event.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Wrong or mutable package source | Bind the accepted materialization root, package locks, rc.7 package/version set and installed-source SHA-256 values before and after Python-only copying. |
| Wrapper targets another module | Resolve `lib/bin.js` under the exact copied package, require one dynamic import and bind wrapper SHA-256 before launch. |
| A task, session or tool surface is accidentally opened | Exact argv ends at the authored missing profile; static and runtime evidence reject every surplus argument and require prompt/session/tool counts zero. |
| Network or credential escape | Use the accepted credential/proxy scrubber and preloaded fail-closed network guard; any network ledger record rejects acceptance. |
| Raw error text becomes durable evidence | Raw streams and sidecar remain under the disposable root; durable terminal retains only counts, digests and closed coordinates; cleanup destroys all raw bytes. |
| Secret-shaped message reaches the structured sidecar | The wrapper projects only closed enums and fixed source-backed message coordinates; exact schema/canonical-byte validation rejects arbitrary values. |
| Sidecar write masks the native rejection | Exclusive `wx` write and identical-value rethrow remain byte-shape tested; any missing/invalid sidecar falls back to v1 and fails tranche acceptance. |
| Stale or aliased terminal is trusted | Refuse pre-existing output, symlink parents, paths inside the disposable root, wrong identities and noncanonical readback; use exclusive creation. |
| Process retries after failure | The first and only `Popen` consumes the attempt; source inspection and runtime counters require one Node process and zero retry. |
| Cleanup deletes the wrong path or leaves a process | Require an exact direct child of the accepted disposable parent, verify resolved parent before removal, terminate only the owned process tree, and prove process/root absence. |
| A post-HMR event is mislabeled pre-HMR | The authored profile absence and pinned source ordering precede `boot(...)`; any observed HMR evidence or a zero exit rejects the v2 relationship. |
| Historical failure evidence is reclassified | Attempts 001, 002 and 003 remain immutable, digest-bound inputs and are neither opened for raw reconstruction nor used as this attempt's namespace. |

## Residual claim boundary

A pass establishes one safe provider-free pre-HMR diagnostic composition for
the pinned local rc.7 entrypoint. It does not establish worker creation,
DeepSeek reasoning or coding quality, provider reliability, production
isolation, future-version behavior or product suitability.

Product, data, ordinary-practice, database, deployment, release, Pages,
protected-evidence and protected-ref authorities remain unchanged and closed.
