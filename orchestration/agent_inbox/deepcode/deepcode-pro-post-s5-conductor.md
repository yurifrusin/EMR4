# DeepSeek 4 Pro Conductor Fallback: Post-S5 Sprint

Role: Conductor fallback
Resource: `deepseek-pro-conductor-fallback`
Model: `deepseek-v4-pro`
Reasoning: high
Trigger: Claude subscription reported a real session limit; Fable and Opus share
that unavailable account window.
Completion plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-post-s5-next-sprint.md`

Act as Ariadne Conductor under `operating_model.yaml`, `role_preferences.yaml`,
and `cost_controls.yaml`. You have sprint planning and worker-allocation
authority only. You cannot integrate, commit, push, or modify master.

Read the S5 closeout and accepted evidence. Sol's advisory direction offers two
post-S5 priorities:

1. Eight reproducible diary smoke failures caused by GraphQL-vs-REST mock drift
   and smoke-mode network assertions.
2. Yuri's requested bounded Ariadne cross-boundary contract audit, focused on
   duplicated operational facts such as artifact path, packet/lane identity,
   worktree/branch, settings fingerprint, model/reasoning, and authority state.

Decide whether to combine or sequence them, then define exactly one next sprint
with a clear EMR4 development benefit. Allocate available workers from current
settings and create concrete worker packets in their proper inboxes. Keep all
runtime gates closed; do not revisit terminal-status product policy. Include
regular Sol commit/push checkpoints. Deterministic plan checks are mandatory;
request independent LLM verification only if a configured risk trigger applies.
Do not add monetary or wall-clock caps.

The completion plan must include settings fingerprint, direction disposition,
scope, assignments, ownership, acceptance evidence, cross-review if useful,
closed gates, and the fallback reason/reduced independence. End the final plan
with:

```text
STATUS: complete
```
