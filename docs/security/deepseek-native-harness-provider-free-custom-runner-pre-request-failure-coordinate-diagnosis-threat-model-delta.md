# Threat-model delta — native Harness custom-runner pre-request failure-coordinate diagnosis

Date: 2026-08-21

Timestamp: 2026-08-21T20:13:19.9793090+10:00 (Australia/Brisbane)

Status: `frozen`

Reasoning level: `high`

## Scope

This delta covers offline source inspection and a future-only sanitized
post-HMR diagnostic sidecar design. It adds no occupied runtime, provider,
product, data, command, deployment, release, Pages or protected-ref surface.

## Threats and controls

| Threat | Control | Fail-closed result |
|---|---|---|
| LLM invents a plausible stage or state label | One ordered enum constant generates schema, helper and validator admission | Reject before evidence or publication |
| Sidecar stage overclaims provider position | Stage is a runner source coordinate only; pre-request conclusion also requires independent broker count zero | Reject unsupported conclusion |
| Dynamic error leaks secrets, paths or raw text | Inspect only closed constructor/name identity; forbid message, code, stack, cause, path and stream fields | `unknown` kind or reject |
| Diagnostic changes the primary failure | Exclusive sidecar write is best-effort and the identical caught value is rethrown | Existing generic terminal remains authoritative fallback |
| Partial or duplicate sidecar | `wx`, bounded bytes, canonical JSON, exact keys and identity/path validation | Reject sidecar |
| Stale or substituted package source | Bind pinned rc.7 tarball-member SHA-256 and exact source fragments | Reject source mapping |
| Consumed attempt is reclassified | Attempt 005 remains byte-immutable; this tranche produces future-only design evidence | Reject mutation |
| Hidden execution or spend | Zero Node/Harness/broker/worker/model/provider/network counts in contract and evidence | Reject tranche |
| Unrelated worktree damage | Explicit-path staging and preservation checks | Stop without broad cleanup |

## Residual boundary

The sidecar can identify the runner operation active when a rejection escaped.
It cannot prove an internal sub-operation inside rc.7, a provider request
position, DeepSeek quality, general Harness reliability or EMR4 readiness.
