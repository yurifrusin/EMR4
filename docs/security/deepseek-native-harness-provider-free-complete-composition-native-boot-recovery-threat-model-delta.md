# Threat-model delta: DeepSeek native Harness provider-free complete-composition native-boot recovery

Date: 2026-08-20

Timestamp: 2026-08-20T11:24:06.3744524+10:00 (Australia/Brisbane)

Status: `frozen`

This delta is limited to
`deepseek-native-harness-provider-free-complete-composition-native-boot-recovery`.
All repository security policy and protected-evidence boundaries remain in
force.

## Assets and trust boundary

The sole admitted executable boundary is one disposable local rc.7 native
Harness process. Its inputs are exact cached package bytes and four accepted
repository-bound composition artifacts. Retained assets are bounded digests,
package versions, safe service/tool names, readiness and activation
coordinates, one sanitized terminal, timing/counts and cleanup facts. No
prompt, WorkOrder, agent/session/turn, broker/model/provider exchange, product
data, credential, raw log or reusable runtime is admitted.

## Threats and fail-closed controls

| Threat | Control |
|---|---|
| Replaying or reclassifying a consumed native attempt | The new full attempt id is distinct and prior failed controllers, evidence and terminals are digest-bound and read-only. The first `Popen` consumes only the new id. |
| More than one native process | The controller has one static launch site, requires canonical output absence and contains no retry/resume loop. Any result closes the attempt. |
| Registry, provider or network egress | Exact local cache blobs are verified; install is offline with scripts/audit/funding disabled; credential and proxy names are removed; the accepted Node network guard denies and records network primitives. |
| Accidental agent or occupied worker | Stock runner, code runtime and telemetry are disabled before tree mount. No task prompt, work order, broker or provider configuration exists. Zero agent/session/turn and request counts are schema-required. |
| Forged HMR or service readiness | The sentinel alone writes the readiness ledger and must observe both exact watched paths. The controller mutates only after its exact sequence. Runner entry is accepted as service readiness only when both loader row and module declare the identical three names and Cordis's exact dependency-gating source remains bound. |
| Substituted or overbroad preset | The disposable payload is copied byte-for-byte from the accepted repository artifact and checked by fixed digest and path. Raw plugin surplus is recorded; the preset alone is never treated as authority. |
| Tool escape through own-layer or surplus schemas | The accepted guard mounts first, rejects own-layer names, proves all selected names inherited, restricts once and requires final schemas exactly `edit`, `glob`, `read`. The external broker boundary remains independently required for any future worker. |
| Opaque or leaked failure evidence | Activation and terminal vocabularies are finite. Evidence retains safe constants, counts, booleans, digests and sizes only; raw errors, stacks, stdout/stderr, paths, environment, prompts and credentials are destroyed. |
| Stale or forged success terminal | One exclusive runner owns activation and terminal writes. Success must be causally bracketed by exact ordered activation, scope disposal and exit request, with exact schema/stage/code/tool set/count and exit zero. |
| Lost duration or execution handle | Duration is assigned in `finally` before termination and cleanup. The external command result preserves its full execution envelope and polls any yielded session id to final exit. |
| Process or filesystem escape | The root is a verified direct child of the accepted disposable parent. Cleanup targets only that root, terminates and waits for the exact process, removes the root and proves both absent. |
| Review triggering hidden rerun | Gemini starts only after the sole terminal is committed. Review may require deterministic repair but cannot authorize another native process or change terminal-bound bytes. |
| Governance drift | Clockwork alone writes canonical governance; check, publication, dedicated postpublication verification and idempotent reading remain distinct. |

## Residual claim boundary

A pass proves only one pinned local rc.7 provider-free complete-composition path
through exact service gating, preset mount and three-tool projection. It proves
no DeepSeek reasoning, occupied-worker completion, provider reliability,
product suitability or production isolation and authorises no product/data,
network, deployment, release, Pages or protected-ref movement.
