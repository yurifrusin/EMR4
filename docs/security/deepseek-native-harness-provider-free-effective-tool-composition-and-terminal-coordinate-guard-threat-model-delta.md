# DeepSeek native Harness provider-free effective-tool composition and terminal-coordinate guard threat-model delta

Date: 2026-08-20

Timestamp: 2026-08-20T04:41:52.2950895+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`80d9e69c3dee0ddeb4b7fc620cbd0673d7ad0fa4`

Operation:
`deepseek-native-harness-provider-free-effective-tool-composition-and-terminal-coordinate-guard`

## Changed trust boundary

The outer broker already rejects a composed request containing a tool outside
`edit`, `glob`, `read`. The missing boundary is earlier: the rc.7 custom runner
must prove the preset tools occupy the inherited/restrictable surface before it
uses `tools.restrict()`, and must preserve a safe attributable coordinate if
that proof fails before a provider request.

The new guard remains orchestration-only. It is not a sandbox, authorization
service or substitute for the broker.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A scope-local preset tool is named to the inherited restriction surface | Reject any `knownNames - restrictableNames` value before `restrict()` and return `EFFECTIVE_TOOL_COMPOSITION_SCOPE_LOCAL_TOOL_PRESENT`. |
| Mount is not awaited and restriction races preset assembly | Generated helper has one awaited mount before the first registry view; structural tests reject changed ordering. |
| Selected tool is absent or misspelled | Require all exact selected names in `restrictableNames` before restriction; retain only sorted safe missing names. |
| Surplus schema remains model-facing | Sort the final schema names and require exact equality with `edit`, `glob`, `read`. |
| A restriction exception collapses to an untraceable generic terminal | Map it to `EFFECTIVE_TOOL_COMPOSITION_RESTRICTION_FAILED`; never retain raw exception text or stack. |
| Malformed schema or tool name smuggles a path, prompt or secret into evidence | Accept only unique lower-case underscore names; otherwise emit the closed schema-view coordinate with no detail. |
| Package/source drift changes rc.7 semantics | Verify exact cache-blob registry identity and accepted runtime-source digests before deriving the guard evidence. |
| Static proof is overclaimed as a native or occupied run | Evidence records zero Node/Harness boots, sessions, broker requests, model requests and provider calls; claim is limited to deterministic guard construction. |
| The guard is treated as the authority boundary | Contract states the broker's exact independent allowlist remains mandatory. |
| Historical failure is rewritten or retried | Consumed attempt artifacts are read-only inputs; attempt 004 and attempt 005 execution remain forbidden. |

## Data, secret and retention posture

Inputs are repository governance artifacts and exact public npm package bytes
already present in the local cache. The script reads only bounded package
metadata and runtime source members in memory. It retains digests, closed
semantic predicates, generated helper digest, safe tool names and zero-count
readbacks. It retains no package source, prompt, response, reasoning, tool
payload, stack, dynamic error text, path, environment value or credential.

No patient, appointment, product, clinical, historical Diary, protected
holdout or real-person data is permitted. No network or provider route is
permitted.

## Residual boundary

Passing proves that the deterministic guard is correctly bound to exact rc.7
source semantics and fails closed in all tested registry projections. It does
not prove an actual native Harness composition boot, an agent session, a model
request, DeepSeek coding quality, provider reliability, production isolation
or general future-version compatibility. A separately frozen provider-free
native boot is required before any later occupied worker can rely on the guard.
