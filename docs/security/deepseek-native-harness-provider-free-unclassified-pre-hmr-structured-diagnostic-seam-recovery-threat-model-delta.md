# Threat-model delta: unclassified pre-HMR structured diagnostic seam recovery

Date: 2026-08-21

Timestamp: 2026-08-21T08:07:16.9546464+10:00 (Australia/Brisbane)

Operation:
`deepseek-native-harness-provider-free-unclassified-pre-hmr-structured-diagnostic-seam-recovery`.

| Threat | Fail-closed control |
|---|---|
| Reclassifying consumed attempt 003 | Its terminal, digest and destroyed raw streams are read-only predecessor evidence. The new seam is explicitly future-only. |
| Leaking dynamic stderr/error content | The wrapper emits enums and booleans only. Raw message, stack, path and arbitrary properties are never serialized. |
| Secret-shaped message influencing evidence | Message inspection can select only a frozen literal coordinate. The original string never enters the projection. |
| Getter, proxy or unusual thrown value breaking sanitization | Every property read is bounded and caught; unknown values collapse to closed enums. Diagnostic failure never replaces the original rejection. |
| Deep or cyclic cause graph exhausting the wrapper | Cause traversal is identity-cycle checked and capped at six nodes. |
| Aggregate errors leaking child values or cardinality | Children are not traversed or serialized; only `zero`, `one`, `multiple` or `unreadable` is retained. |
| Sidecar overwrite or stale evidence | The wrapper uses one `wx` exclusive write. The controller accepts only the exact non-symlink path inside the disposable root and an exact schema/identity match. |
| Diagnostic sidecar changing Harness behavior | The wrapper rethrows the identical caught value after either successful or failed diagnostic writing. |
| Wrapper changing launcher argv semantics | Node still receives `--expose-internals`; wrapper is argv element 1 and the untouched launcher continues to parse `process.argv.slice(2)`. |
| Wrapper accidentally turning a failure into success | There is no success terminal or exit call in the wrapper. A rejected import is always rethrown. |
| Treating absent/invalid sidecar as diagnosis | Absence retains the accepted v1 byte-signature fallback. Invalid sidecars are rejected and cannot supply a cause. |
| Raw sidecar surviving cleanup | The validated safe projection is embedded outside the attempt root; the sidecar and wrapper remain inside the exact root and are destroyed with it. |
| Provider or runtime activity during proof | Acceptance runs Python source inspection and hostile fixtures only; subprocess entry points are forbidden and asserted unused. |
| Product or protected-boundary expansion | The tranche touches orchestration diagnostics only and preserves all product, data, deployment, Pages and protected-ref prohibitions. |

The seam improves the causal resolution of a future pre-first-HMR failure. It
does not prove DeepSeek execution, Harness operational readiness, coding
quality, provider reliability or authority for another occupied attempt.
