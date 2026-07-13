# DeepSeek Flash W2 - S10 Test-Only Workflow Chain Adversarial Review

Role: independent adversarial review
Resource: `deepseek-flash-workers` (instance 2)
Model: `deepseek-v4-flash` / high
Parent plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s10-receptionist-workflow-v2.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-deepseek-s10-w2-workflow-chain-adversarial.md`

Review the accepted W1 staging base. Do not edit W1-owned files, any `app/`
file, `app/config.py`, or `tests/test_bernie_interpretation_runtime_isolation.py`.

## Ownership

- `docs/adversarial/s10_workflow_chain_review_v2.md` (new)
- `tests/fixtures/bernie_workflow_chain_review/` (new, adversarial only)
- `tests/test_bernie_workflow_chain_adversarial.py` (new)

Challenge context propagation, frame coherence, refusal propagation, aggregate
report safety, and test-only isolation. Use authored synthetic data only. Do not
call routes/providers/DB, access trove/H15/memory/RAG/GraphRAG, write runtime
state, or change the user-owned terminal-status policy.

The runtime-isolation test has one documented baseline failure from unchanged
`app/config.py`; it must have zero new failures. Report `revision_required` for
any new isolation failure, forbidden import, protected-file edit, or safety
leak. Create a candidate commit only; do not push or integrate.

Run focused W2 tests, the W1/W2 combined suite, existing interpretation-harness
regressions, the report CLI, the isolation baseline comparison, and
`git diff --check`. Write the exact expected artifact with candidate SHA,
findings, commands/results, boundary confirmation, and `STATUS: complete`.
