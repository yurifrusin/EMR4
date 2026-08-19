# Threat-model delta: provider-free preterminal-observable composition recovery boot

Date: 2026-08-20

Status: `frozen`

This delta is limited to
`deepseek-native-harness-provider-free-preterminal-observable-composition-recovery-boot`.
All repository security policy and protected-evidence boundaries remain in
force.

## Assets and trust boundary

The only admitted executable boundary is one disposable local native Harness
process using exact cached rc.7 package bytes. Its retained assets are the new
attempt identity, predecessor digests, readiness and activation coordinates,
one sanitized terminal, process timing/counts and cleanup facts. No prompt,
agent/session/turn, broker/model/provider exchange, product data, credential,
raw log or reusable runtime is admitted.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Replaying the failed native attempt | The contract rejects `native-composition-attempt-001` and freezes the distinct new ID `preterminal-observable-composition-recovery-boot-attempt-001`. Existing failed evidence is digest-bound and read-only. |
| Starting more than one process | Canonical output non-existence is checked before launch; the first `Popen` consumes the new ID; the controller has one static launch site and no retry/resume path. |
| Registry or provider egress | Exact npm cache blobs are verified before launch; online fallback and lifecycle scripts are disabled; credential/proxy variables are scrubbed; the accepted Node network guard records and denies any network primitive. |
| Accidental agent/model activity | Stock headless runner, code runtime and telemetry are disabled. The patch mounts only the sentinel and corrected composition runner. Evidence requires zero agent/session/turn, broker/model/provider and occupied-worker counts. |
| False readiness or concurrent ledger corruption | The sentinel exclusively owns the separate readiness ledger. Patch mutation occurs only after exact ordered readiness and both watched stock paths. The corrected runner exclusively owns the activation ledger. Duplicate, partial, unsafe and reordered records reject. |
| A preterminal failure collapsing to an opaque error | The accepted corrected runner is byte-bound and exposes only its finite activation vocabulary plus the unchanged finite guard vocabulary. Unknown exception text, stacks and dynamic values are excluded. |
| A stale or forged success terminal | The terminal uses exclusive creation, a closed schema/code/stage, exact sorted tool names and count, and must be causally bracketed by `GUARD_ENTRY_REACHED`, `GUARD_TERMINAL_REACHED`, disposal and exit coordinates. |
| Lost or misleading elapsed time | Start time is captured at the only launch site and duration is assigned in `finally` for every started process before termination and cleanup. A started attempt with missing duration rejects. |
| Process or filesystem escape | The disposable root must be a verified direct child of the fixed disposable parent. Cleanup terminates and waits for the exact process, removes only that root and proves both absent. |
| Evidence leakage | Only bounded digests, sizes, counts, coordinates and booleans are retained. Raw stdout/stderr, environment values, package source, paths, prompts, payloads and credentials are destroyed with the disposable root. |
| Review causing a hidden rerun | Gemini is eligible only after the consumed passing terminal. A review finding may cause bounded deterministic correction but cannot authorize another native process or mutate terminal-bound bytes. |
| Governance drift | The clockwork alone writes canonical continuity, Compass, baton, latch and error-register projections, with separate check and publish commands. |

## Residual claim boundary

A passing result proves only one pinned, local, provider-free rc.7 pre-provider
composition boot with exact `edit`, `glob` and `read` exposure and bounded
preterminal traceability. It proves no DeepSeek reasoning or provider
reliability and authorises no occupied worker, product/runtime use, data,
network, deployment, release, Pages or protected-ref movement.
