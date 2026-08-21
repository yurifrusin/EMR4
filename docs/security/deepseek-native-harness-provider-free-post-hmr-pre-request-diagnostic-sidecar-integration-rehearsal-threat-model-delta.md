# Threat-model delta — native Harness post-HMR pre-request diagnostic-sidecar integration

Date: 2026-08-21

Timestamp: 2026-08-21T21:22:46.8865274+10:00 (Australia/Brisbane)

Status: `frozen`

Reasoning level: `high`

## Scope

This delta covers a provider-free future-runner derivation and deterministic
controller fixture join. It opens no runtime, model, provider, product, data,
command, deployment, release, Pages or protected-ref surface.

## Threats and controls

| Threat | Control | Fail-closed result |
|---|---|---|
| Transformer silently rewrites accepted runner semantics | Exact accepted hash, unique marker roster and closed transformation validator | Reject derivation |
| Failure after the first turn is mislabeled pre-request | `diagnosticActive` becomes false immediately after first-turn idle and gates the sole write | Generic terminal only |
| Model invents stage/cause prose | Runner assigns only the accepted constant vocabulary at exact source coordinates | Reject source or sidecar |
| Error details leak through diagnostic | Accepted helper inspects only closed constructor/name identity; fixed false raw flags | `unknown` or no sidecar |
| Sidecar alone overclaims request position | Pre-request result requires a separate canonical broker reading with all counters zero | Unresolved boundary |
| Stale or substituted broker reading joins | Exact schema, canonical bytes, full Git identity and operation/attempt equality | Reject join |
| Boolean or negative counter passes as integer zero | Explicit `type(value) is int` and non-negative validation | Reject broker reading |
| Invalid sidecar erases existing terminal | Invalid/absent sidecar selects the unchanged generic failure coordinate | Preserve fallback |
| Partial, linked or escaped evidence is ingested | Exact disposable-root containment, regular-file, size, symlink and canonical checks | Reject file |
| Rehearsal accidentally launches the subject | Contract/evidence fix every process, request, network, database and Docker count at zero | Reject tranche |
| Unrelated worktree content is staged | Explicit-path staging and preserved-untracked checks | Stop before commit |

## Residual boundary

Passing evidence will prove representability and deterministic integration
semantics only. It will not prove that rc.7 loads the future files, that the
sidecar captures a real failure, that broker counters are available in an
occupied controller, that DeepSeek makes a request or performs useful work, or
that the native Harness is ready for EMR4 development.
