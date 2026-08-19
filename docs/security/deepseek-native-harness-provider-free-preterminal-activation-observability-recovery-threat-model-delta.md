# Threat-model delta: provider-free preterminal activation observability recovery

Date: 2026-08-20

Timestamp: 2026-08-20T06:01:41.6545833+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`deepseek-native-harness-provider-free-preterminal-activation-observability-recovery`

## New bounded surface

This tranche adds deterministic future-runner construction and one offline
non-Harness Node module-import probe. It starts no native Harness CLI, agent,
session, turn, broker, model, provider or occupied worker.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| The consumed attempt is silently retried | Its evidence path, attempt id and source digest are immutable inputs; native Harness process count must remain zero. |
| A generic coordinate again hides the failed stage | Every admitted activation stage has one closed coordinate; unknown exceptions map to a stage-specific unclassified coordinate, never a single whole-process bucket. |
| Timing again remains zero on failure | The deterministic design assigns elapsed time in the started-process `finally` path and tests each early rejection. |
| Readiness and runner events race in one ledger | Sentinel readiness and runner activation have separate single-owner files with exact schemas and exclusive/atomic writes. |
| Top-level imports fail before any trace | The bootstrap has Node built-ins only, records apply entry first, then performs caught dynamic imports. |
| Service injection prevents runner entry | A minimal HMR-only bootstrap is distinct from the service-dependent composition runner and gives a bounded activation boundary. |
| Dynamic errors leak paths or credentials | Retention admits only finite coordinates, booleans, exact package identities, counts and digests; messages, stacks, paths and environment values are discarded. |
| The import probe accidentally starts the Harness | The command and source reject `lib/bin.js`, `--profile`, child Harness entry points and any native process count above zero. |
| Offline materialisation reaches the registry | npm offline mode, lifecycle/audit/fund denial and the accepted Node network guard are mandatory; any network-attempt ledger entry rejects. |
| Mock success is overclaimed as native success | Evidence distinguishes mock scenario count, non-Harness Node import count and native Harness process count zero. |
| A later process is treated as a retry | Closeout can only select a separately named operation and new attempt id after independent review; attempt 001 remains immutable. |

## Unchanged closed surfaces

Protected holdouts and historical diary PHI remain inaccessible. Attempts 004,
005 and `native-composition-attempt-001` remain closed. Product, API,
configuration, ordinary-practice, data, Docker/database, native Harness,
production, deployment, release, Pages and protected-ref authority remain
closed. `docs/branding/` and all unrelated untracked files remain preserved.
