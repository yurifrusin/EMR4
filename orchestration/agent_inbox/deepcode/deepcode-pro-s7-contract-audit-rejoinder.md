# DeepSeek 4 Pro Conductor Rejoinder: S7 Executable Contract Surface

Role: Conductor fallback, final response to orchestrator rejoinder
Model: `deepseek-v4-pro`
Reasoning: high
Prior plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s7-contract-audit.md`
Amended plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s7-contract-audit-v2.md`

Sol agrees with the S7 priorities and two-lane structure but does not accept the
test-only implementation shape. This is the one permitted orchestrator
rejoinder under `direction_collaboration.yaml`; the Conductor has final say.

Please amend or defend the plan against these concrete issues:

1. Tests that merely assert prose or source regexes do not stop the next
   orchestrator from accepting a review from the wrong worktree. S7 should add
   the smallest reusable, platform-neutral acceptance/preflight contract (for
   example in `orchestration_harness/` with a thin script) that can verify the
   declared review worktree, expected branch/HEAD, candidate ancestry, canonical
   artifact path/kind/marker, adapter receipt, and authoritative deterministic
   evidence before review acceptance.
2. Current PTY receipts use the field `artifact`, not `artifact_path`. Do not
   invent a parallel name unless a deliberate schema migration and compatibility
   test is in scope.
3. A settings-payload unit test cannot prove DeepCode will never classify a
   shell call as `unknown`; that classification may be model/tool supplied and
   `unknown` always prompts. Preserve strict deny rules. Codify a practical
   dual path instead: executable review when commands remain in the authorized
   envelope, or static LLM veto over an orchestrator-produced deterministic
   evidence receipt when shell execution is permission-blocked. Neither path
   may auto-answer prompts or broaden filesystem/network access.
4. Marker compatibility should be checked before launch or acceptance, not only
   described after a completed artifact stalls. Reuse the adapter's actual
   `decision`/`completion` canonical markers.
5. Scratch files and worker-reported test counts must be rejected by the same
   executable acceptance contract; only the declared artifact/receipt and
   parsed orchestrator collection evidence are authoritative.
6. Reconcile the six stale Pro-fallback settings assertions, including the
   missing `permission_prompts_are_not_authority` quirk if that omission is real.
   Keep Flash-only restrictions for verifier/ordinary worker resources.

Keep S7 bounded and useful. It may touch a small harness core module, thin CLI,
focused tests, and the stale settings tests, but not EMR4 runtime code. Avoid a
large framework or new mandatory paperwork. Maintain two DeepSeek Flash lanes,
strict permissions, no monetary/wall-clock caps, regular Sol commit/push
checkpoints, and all existing closed gates.

Return a complete amended plan with exact ownership/file surfaces, concrete
worker packet paths, executable acceptance behavior, tests, fallback reason,
and automatic next transition. End with:

```text
STATUS: complete
```
