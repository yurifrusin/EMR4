# DeepSeek native Harness repaired-sentinel preactivation source-coordinate diagnosis closeout

Date: 2026-08-21

## Outcome

Accepted at reviewed source `d1e60a59a0b0cf600721850b96d2914059fe7ca3`.

The diagnosis names one narrow source transformation sufficient to explain why the repaired sentinel could not activate: `sentinel_source()` returned an ordinary Python bytes literal whose single-escaped JavaScript carriage-return and newline spellings were translated into raw line terminators. The generated module therefore contains lexical violations inside a regular-expression literal and a quoted string before rc7 can call `apply()`.

This is an EMR4 harness-integration authoring defect. It is not evidence of a DeepSeek model or provider failure.

## Evidence

- The exact failed terminal remains `failed_closed`: exit `1`, readiness false, zero HMR events, zero retries and zero broker/worker/model/provider/network activity.
- Python AST extraction reproduces the exact sentinel SHA-256 bound by that terminal without importing or executing the failed author.
- The first fatal generated coordinate is the raw carriage return inside the JavaScript regular-expression literal; the same one-source literal also emits downstream raw newlines.
- The accepted passing control double-escapes the spellings, has zero lexical violations and previously emitted both `sentinel_activated` and `stock_headless_hmr_ready` on the same pinned rc.7 materialisation.
- Fifty focused and predecessor tests passed, plus Ruff and bytecode compilation.
- The fresh pre-verifier receipt passed with protected refs unchanged and zero manually supplied Git object IDs.

No raw stderr message, path, stack, environment or stream was reconstructed or guessed from the retained digest. No Node, Harness, broker, worker, model, provider or network process/request ran in this tranche.

## Efficacy

The static tranche avoided another opaque native attempt and reduced the failure to a source-level coordinate. One focused rerun corrected an overbroad provider-counter assertion. A transient pre-verifier draft also repeated the exact class of guessed-Git-ID lapse discussed with Yuri; it was caught before preflight, removed from Git narrative evidence and recorded for clockwork allocation. The first clockwork dry run then rejected path strings in a structured `contract_evidence` field without publishing; the intent now uses the accepted empty-list form while retaining the paths in ordinary evidence. The final receipt delegates Git binding exclusively to the machine snapshot.

## Successor

Proceed under standing authority with `deepseek-native-harness-provider-free-sentinel-source-escape-repair`: repair only the diagnosed sentinel-source escaping, prove generated-byte validity and preserve every consumed attempt. It authorises no Node/Harness process and no later boot proof; any new boot requires a separately frozen attempt contract.
