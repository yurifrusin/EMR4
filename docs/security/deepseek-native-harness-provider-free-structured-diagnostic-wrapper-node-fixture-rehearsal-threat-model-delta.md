# Threat-model delta: structured diagnostic wrapper Node fixture rehearsal

Date: 2026-08-21

Timestamp: 2026-08-21T08:51:17.1239113+10:00 (Australia/Brisbane)

Operation:
`deepseek-native-harness-provider-free-structured-diagnostic-wrapper-node-fixture-rehearsal`.

| Threat | Fail-closed control |
|---|---|
| Authored rehearsal accidentally imports installed DSH | The generated wrapper target must resolve under the exact disposable scenario root as `fixture-package/lib/bin.js`; source and command validation reject `@deepseek-ai`, `node_modules`, `dsh` and every outside-root URI. |
| Observer changes the rejection identity | The authored fixture stores the exact object on a scenario-only global before throwing; the observer compares strict identity after the wrapper rethrows and retains only a boolean. |
| Observer suppresses a wrapper failure | A caught non-identical value, absent catch or observer-artifact failure is a terminal scenario rejection; success cannot be inferred from process exit alone. |
| Wrapper retains authored secret/path-shaped text | Safe sidecar validation admits only the existing closed vocabulary, and retained evidence is scanned against exact newly authored sentinels before cleanup. |
| JavaScript property order creates noncanonical evidence | The existing reader remains authoritative. Only the plan's bounded recursive key-sorting serializer correction is admissible, followed by a new exact-source run. |
| `wx` failure overwrites or masks the original rejection | The preexisting-sidecar scenario hashes the sentinel before and after, accepts no diagnostic, and independently requires identical rejection at the observer. |
| Node output becomes a new raw-stream store | stdout/stderr are bounded in memory only for process lifecycle, are never included in evidence or reports, and are destroyed with the scenario result after retaining byte counts and fixed exit coordinates only. |
| Disposable source or sidecar survives | Each root must be a non-symlink child of the exact operation parent, cleanup targets are resolved and checked before recursive deletion, and terminal acceptance requires complete absence. |
| Scenario concurrency confuses evidence | Exactly four Node processes run serially with distinct fixed scenario IDs and roots. |
| Rehearsal is mistaken for Harness readiness | Evidence labels all imported modules as authored fixtures and records Harness, broker, worker, model and provider counts as zero. |
| Product or protected authority expands | The tranche touches orchestration diagnostics only and retains every product, practice, data, deployment, Pages and protected-ref closure. |

The rehearsal can prove the wrapper gear's local Node behavior. It cannot prove
DSH boot, native Harness readiness, DeepSeek execution, provider reliability or
authority for another occupied attempt.

