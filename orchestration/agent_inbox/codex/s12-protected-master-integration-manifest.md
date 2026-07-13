# S12 protected-master integration manifest

## Authorization request

This is a staging-only S12 closeout. Do not merge, push, or advance protected
refs until Sol authorizes this manifest.

| Field | Value |
| --- | --- |
| Source branch | `codex/s10-terra-staging` |
| Required protected base | `origin/master` and `handoff/current` at `f377df19` |
| Integration method | Conflict-free merge of the source branch after the stated preconditions |
| Scope | S12 coordination evidence and Deep Code harness path discovery only; no `app/` or product-runtime change |

## Exact S12 patch set

The source graph retains original S11 commit identities that are already
patch-equivalent on protected master. Do not cherry-pick that historical graph.
Merge the source branch and require the expected diff scope below. The ordered
S12 patch-equivalent commits before this manifest are:

1. `957a306e` `docs(ariadne): plan S12 receptionist acceptance`
2. `80a201d2` `docs(ariadne): correct S12 W1 review lane`
3. `f58029a9` `docs(ariadne): record S12 W1 lifecycle escalation`
4. `053c3a4b` `docs(ariadne): clarify S12 W1 liveness evidence`
5. `9eadd667` `docs(ariadne): record S12 lifecycle stop state`
6. `beafd9b4` `docs(ariadne): correct S12 completion marker`
7. `1bae8bd7` `fix(harness): resolve S12 shared toolchain`
8. this manifest closeout commit.

## Expected diff scope

- `AGENTS.md`
- `scripts/ariadne_deepcode_pty.py`
- `orchestration/agent_inbox/codex/plan-terra-s12-receptionist-acceptance.md`
- `orchestration/agent_inbox/codex/review-deepseek-s12-receptionist-acceptance.md`
- `orchestration/agent_inbox/codex/s12-w1-lifecycle-escalation.md`
- `orchestration/agent_inbox/codex/s12-protected-master-integration-manifest.md`
- `orchestration/agent_inbox/deepcode/s12-receptionist-acceptance-review.md`
- `orchestration/agent_inbox/deepcode/s12-receptionist-acceptance-review-correction.md`
- `orchestration/agent_inbox/deepcode/s12-receptionist-acceptance-marker-correction.md`

The lifecycle escalation documents preserve rejected attempts; they are not
claims of accepted worker output. No production module, route, provider,
schema/database, deployment/release, external client, H15/H-series, historical
trove, memory/RAG/GraphRAG, terminal-to-active policy, or write authority is in
scope.

## Required acceptance evidence

Worker W1: DeepSeek 4 Flash/high through the repaired PTY runner. Accepted
artifact marker: `STATUS: complete`; completed receipt:
`local_data/ariadne-harness/s12-w1-r4-marker-receipt.json`, with one mailbox
event, bounded terminal transcript, and released owner lock. The initial
post-repair artifact was preserved as noncanonical; the marker-only same-lane
correction produced the accepted receipt.

Run from the source branch:

```text
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest review\test_webpack_diary_static_config.py tests\test_bernie_workflow_chain.py tests\test_bernie_workflow_chain_report.py tests\test_bernie_workflow_chain_adversarial.py tests\test_api_spine_confirmation_contract_matrix.py tests\test_api_spine_confirmation_family_idempotency_checkpoint.py tests\test_api_spine_artifacts.py tests\test_ariadne_deepcode_pty.py tests\test_ariadne_deepcode_runtime_observability.py -q --tb=short
```

Expected result: `186 passed`. Also require:

```text
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile scripts\ariadne_deepcode_pty.py
git diff --check f377df19...<source-head>
```

## Clean/conflict-free precondition

Before protected integration: the integration worktree is clean, `master` and
`handoff/current` both resolve to `f377df19`, the source branch is at the
authorized source head, no unexpected file appears in the three-dot diff, and
the merge is conflict-free. Stop without mutation on any variance.

## Process metrics

| Sprint | Worker outcome | Executor retries/corrections | Escalations | Invalid integrations | Duplicated-context events |
| --- | --- | ---: | ---: | ---: | ---: |
| S10 | Two accepted provider-free test lanes; rejected runtime candidate preserved | 1 executor retry; 2 Conductor rejoinders | 2 | 0 | 0 |
| S11 | One accepted contract-matrix lane | 2 same-lane recoveries; 1 executor-lifecycle defect | 0 | 0 | 0 |
| S12 | One accepted W1 receipt after the repaired one-owner recovery | 4 attempts/corrections; 1 invalid-concurrency executor defect; 1 final harness correction | 1 | 0 | 0 |

S12's one escalation was resolved by Sol's `f377df19` harness repair. Its
accepted W1 correction was sequential, not concurrent, and no owner lock was
present at final closeout.
