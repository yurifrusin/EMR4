# DeepSeek native Harness post-sentinel exit-coordinate diagnosis closeout

Date: 2026-08-21

## Outcome

Accepted at exact reviewed source
`07b371090e0f8efe045f9ff39aab409c74244c1b`.

The source-repaired sentinel boot did not expose a mysterious rc.7 crash. Our
frozen proof launched the headless profile with zero inner task arguments while
leaving the mandatory `headless-startup` provider mounted. After the sentinel
activated, that provider rejected the empty task, Commander supplied exit code
`1`, and the launcher disposed the tree through `ctx.appExit` before HMR could
register both watched patch paths.

This is an EMR4 Harness-integration rehearsal-shape defect. It is not evidence
of a DeepSeek model/provider failure and it does not show that the native Harness
cannot reach readiness.

## Evidence

- Every repository and pinned rc.7 input matched its frozen SHA-256; every Git
  source was a full 40-character ancestral commit.
- The retained terminal remains exactly `sentinel_activated`, exit `1`,
  readiness false, retry zero and raw streams absent.
- All eight static control-path links passed, from the empty inner argument
  snapshot through headless startup, Commander, `ctx.appExit` and profile
  shutdown.
- Nine hostile tests cover task, mount, startup, exit-code, routing, terminal,
  binding and raw-stream boundaries.
- Thirty-seven current/applicable predecessor tests passed; four exact immutable
  pre-repair selectors are named and deselected. Ruff, bytecode compilation and
  diff checks passed.
- The fresh pre-verifier receipt passed with protected refs unchanged and zero
  manually supplied Git object IDs.

No destroyed stderr text, raw path, stack, environment or stream was recovered
or guessed. No Node, Harness, broker, worker, model, provider or network process
or request ran during this diagnosis.

## Efficacy

Canonical diagnosis evidence was generated once. Two construction predicates
failed closed before evidence and were corrected. Two widened verification
selections repeated historical-selector discovery; the final set makes all four
immutable exclusions explicit. The important workflow improvement remains: the
diagnosis replaced another opaque native retry with one hash-bound source
reading. A generated applicability manifest is the next obvious clockwork gear
for removing selector-memory reruns.

## Successor

Proceed under standing authority with
`deepseek-native-harness-provider-free-inert-task-sentinel-readiness-native-boot-proof`.
Freeze a fresh attempt identity that adds exactly one inert authored-synthetic
task argument while keeping `headless-runner` disabled. Admit at most one
provider-free Node/Harness process, no retry, no broker/worker/model/provider or
network activity, and terminate after stock HMR readiness. This closeout does
not itself launch that process.
