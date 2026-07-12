# DeepSeek 4 Pro Conductor: S7 Cross-Boundary Contract Audit

Role: Conductor fallback
Resource: `deepseek-pro-conductor-fallback`
Model: `deepseek-v4-pro`
Reasoning: high
Trigger: Claude Fable/Opus remain unavailable until the reported subscription
reset window; do not wait for that window.
Completion plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s7-contract-audit.md`

Act as Ariadne Conductor under `operating_model.yaml`,
`continuous_sprint_engine.yaml`, `role_preferences.yaml`, and
`cost_controls.yaml`. You have sprint-planning and worker-allocation authority
only. You cannot modify product/harness implementation, integrate, commit,
push, or move master.

S6 is published through `43c507dc`. Read:

- `docs/emr4-s6-diary-contract-repair-closeout.md`
- `orchestration/archives/s6-invalid-review-attempt/INVALIDATED.md`
- `orchestration/agent_inbox/codex/review-sol-s6-candidate-verification.md`
- `orchestration/agent_inbox/codex/review-deepseek-s6-scope-delta-review-v3.md`
- current harness settings, adapter code, and focused tests

S7 is Yuri's requested bounded Ariadne cross-boundary contract audit. Keep it a
practical repair sprint, not a documentation-only bureaucracy exercise. Audit
the duplicated facts and executable boundaries that caused real S6 friction:

1. `tests/test_ariadne_deepcode_adapter_settings.py` has six reproducible stale
   failures because it still assumes exactly two DeepCode resources, requires
   Flash defaults for every resource, and prohibits a Pro default. Reconcile it
   with the approved `deepseek-pro-conductor-fallback` without weakening worker
   or verifier restrictions.
2. Packet artifact markers and adapter `--artifact-kind` can disagree
   (`VERDICT` versus canonical `DECISION`), causing completed agents not to be
   recognized.
3. Orchestrator commands can target the wrong worktree when cwd is implicit.
   Require machine-checkable target-worktree/candidate-ancestry evidence before
   accepting review output.
4. Strict DeepCode permissions can block external-venv test commands as
   `unknown`/outside-worktree reads. Preserve strict security; define a seamless
   deterministic-test-plus-static-review path rather than auto-answering or
   broadening filesystem access.
5. Worker scratch outputs escaped declared artifact names and test-count claims
   differed from actual collection. Only canonical artifacts and orchestrator
   receipts should be acceptance-bearing.
6. The prior adapter post-artifact completion behavior and transport stalls
   should be audited without reintroducing arbitrary wall-clock task deadlines.

Define exactly one S7 sprint with the smallest useful implementation surface,
clear owners, independent veto where useful, deterministic acceptance tests,
regular Sol commit/push checkpoints, and automatic transition after closeout.
Prefer one implementation lane and one independent review lane unless the work
has genuinely separable ownership. Do not add monetary or wall-clock caps.
Keep all EMR4 runtime/provider/database/H-series/RAG/deployment/product-policy
gates closed.

The plan must include settings fingerprint, direction disposition, scope,
assignments, concrete worker packet paths, ownership, acceptance evidence,
closed gates, fallback reason/reduced independence, and next-sprint transition.
Request an independent LLM verifier only if a configured risk trigger applies;
deterministic checks are always mandatory.

End with:

```text
STATUS: complete
```
