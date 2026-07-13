# Ariadne Economical DeepSeek Execution

Status: active EMR4 pilot from 2026-07-13.

Sol remains the protected supervisor and integration authority. Routine staging
execution prefers DeepSeek V4 Pro; bounded implementation, tests, review, and
handover work prefer DeepSeek V4 Flash. Gemini 3.5 Flash through Antigravity
remains an economical peer worker, especially for independent cross-checks,
adversarial review, and separable UI or test surfaces. Workers are allocated
only where there is a distinct bounded surface; neither provider has a mandatory
lane quota. Terra is a fallback for unavailable or repeatedly rejected
economical workers and tightly coupled high-risk integration.

The preferred DeepSeek transport is Claude Code `--bare` print mode through the
DeepSeek Anthropic-compatible API. It uses process-local environment variables,
an explicit compact system prompt, JSON output, no session persistence, and an
isolated worktree. It does not depend on a Claude subscription. DeepCode remains
the TUI fallback until comparative evidence justifies retirement.

The 2026-07-13 no-tool smoke comparison returned the required marker through
both Claude Code modes. Ordinary mode consumed about 34,000 input tokens and
reported about USD 0.18. Bare mode consumed 195 input tokens and reported about
USD 0.0036. Therefore ordinary Claude Code mode is prohibited for routine
DeepSeek dispatch; bare mode is required.

Claude Code's `total_cost_usd` is an adapter estimate using its own pricing
model, not DeepSeek billing. For the S16-S18 Pro/high run it estimated
US$2.905994 while Yuri's DeepSeek usage page showed US$0.06-0.08. The provisional
conversion is adapter estimate multiplied by `0.020647-0.027529` (midpoint
`0.024088`), or divided by `36.3-48.4` (midpoint `41.5`). This single sample is
recorded in `deepseek_cost_calibration.yaml` and applies only as an advisory
estimate to similar Pro/high token mixes. Flash requires its own calibration.

Routine evidence follows `evidence_policy.yaml`: one tranche contract, one
generated tranche integration manifest, and one short closeout are committed.
Worker packets, receipts, transcripts, and liveness observations remain local
and ignored unless a rejection, material correction, lifecycle failure, or
authority/security dispute makes the detail necessary. Candidate commits and
compact structured receipts are the worker completion source of truth.

Neither DeepSeek transport may integrate protected master, push, deploy, change
scope, or grant itself authority. Sol authorizes the exact tranche manifest.

Gemini 3.5 Flash dispatch uses `scripts/ariadne_antigravity.py`. The wrapper
refuses protected/detached branches and dirty or non-root worktrees, always
passes `--new-project` and the exact worktree through `--add-dir`, embeds the
root/branch in the packet, and verifies the root/branch again after execution.
OS sandboxing is off by default because the S16-S18 Windows runs that used
`agy --sandbox` coincided with elevation prompts. `--os-sandbox` remains an
explicit option when hard OS isolation is worth interactive Windows approval.
Without it, isolation is Git/worktree plus post-run verification, not a hard
filesystem sandbox.

The Claude Pro subscription was cancelled effective after 2026-07-13. Fable
and Opus remain declared capabilities for portability and any final provider-
permitted access, but allocation requires a live availability probe and must
not assume subscription access. Claude Code used as a DeepSeek shell is a
separate API-key path and remains available independently of that subscription.
