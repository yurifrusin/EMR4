# Threat-model delta — native Harness useful-worker coordinate recovery

Date: 2026-08-22

Operation: `raisa-native-harness-bounded-occupied-useful-worker-coordinate-recovery-rehearsal`

| Threat | Control |
|---|---|
| A recovery silently retries or overwrites the consumed attempt | Use a separately named operation, attempt, work order, lease, root and evidence namespace; require predecessor terminal byte identity and forbid retry/resume. |
| A late conclusion marker recreates an ambiguous terminal | Derive the runner from the accepted provider-free coordinate result; call `concludeTurn()` after the exact pre-execute boundary and before dispatch, then observe post-execute decision and authoritative `tools/result`. |
| An early failure cannot satisfy the lifecycle schema | Admit `tool_lifecycle: null` only for a failed terminal before lifecycle observation; observed lifecycle values are confined to five closed coordinates. |
| A successful-looking event sequence masks a failed edit | Require the one success coordinate, one request/edit/result, completed turn, exact changed path and exact canonical candidate together. |
| A second request turns containment into an implicit retry | Broker, runner and authority cap provider calls at one; the consumed lease and terminal cannot be resumed and the post-ceiling rejection is evidence only. |
| Free-form model output escapes a box-ticking task | Permit only one literal edit of one JSON member and reject duplicate keys, unknown keys/values, size drift and noncanonical semantics. |
| The worker reaches product or unrelated files | Use a one-file disposable Git workspace, absolute target checks, one-call hooks, changed-path inventory and exact-root cleanup. |
| A read, glob, shell or subagent expands authority | Although the preset exposes `edit`, `glob`, `read`, the runner admits only one direct top-level edit; all other tools and calls deny. Shell, workflow plugins and subagents are absent. |
| Raw model or credential material becomes durable evidence | Retain only byte counts, SHA-256 hashes, typed counts/coordinates and a validated candidate; remove raw streams, session, environment and exact disposable root before interpretation. |
| The candidate self-authorizes adoption | Treat it as untrusted; require deterministic Sol readback and a fresh serial Gemini 3.7 Flash/high veto before adoption. No candidate means no Gemini request. |
| A valid runbook is mistaken for activation authority | Schema and semantic validator require every activation, feature-flag, allowlist, route, runtime, data and protected-ref effect false. |
| Git shorthand or recalled state misbinds evidence | Machine-resolve full 40-character Git object identities in receipts and checkpoints; reject abbreviations and verify task/origin plus all protected refs before launch. |
| Cleanup removes unrelated user data | Resolve and verify the exact named disposable root beneath the worker-root parent before recursive removal; preserve all repository untracked paths including `docs/branding/`. |
| One pass is overstated as general Harness reliability | Claim only one bounded typed useful-worker result and compare ambiguity/rerun pressure with the predecessor; preserve provider, Harness, model and verifier coordinates separately. |

Residual risk: a successful single edit would show that the clockwork can govern
one useful native-Harness turn, not that unconstrained DeepSeek development or
the Harness is generally reliable. A failed terminal remains useful only when
its typed coordinate and cleanup are complete.
