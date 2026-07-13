# DeepSeek Flash W1 - S10 Test-Only Workflow Chain Harness

Role: implementation owner
Resource: `deepseek-flash-workers` (instance 1)
Model: `deepseek-v4-flash` / high
Parent plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s10-receptionist-workflow-v2.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-deepseek-s10-w1-workflow-chain-v2.md`

## Sol Boundary

Implement only the V2 W1 allocation. The harness belongs exclusively in the
test-only `tests/workflow_chain/` surface. Do not create or modify any
`app/services` file, do not edit `tests/test_bernie_interpretation_runtime_isolation.py`
or `app/config.py`, and do not reuse or integrate rejected V1 candidate
`ae0fb775`.

Create a candidate commit only on this disposable branch. Do not push,
integrate, alter protected master, advance `handoff/current`, or claim final
acceptance.

## Ownership

- `tests/workflow_chain/__init__.py` (new)
- `tests/workflow_chain/harness.py` (new)
- `tests/fixtures/bernie_workflow_chains/` (new, entire directory)
- `tests/test_bernie_workflow_chain.py` (new)
- `scripts/bernie_workflow_chain_report.py` (new)
- `tests/test_bernie_workflow_chain_report.py` (new)

W2 owns its own adversarial fixture directory, test, and review document. Do
not edit existing interpretation harness, route, provider, DB, UI, H15/H-series,
trove, memory/RAG/GraphRAG, or protected runtime-isolation files.

## Implementation and Safety

Implement the deterministic, in-memory multi-step receptionist workflow-chain
harness from the parent plan. Use only authored synthetic fixture data, preserve
refusal propagation, and emit aggregate-only reporting with no utterance text or
payload identifiers. Tests may import the existing interpretation harness; no
runtime `app/` module may be changed or introduced.

No route dispatch, provider call, database access/write, audit write,
confirmation authority, or terminal-status policy decision is permitted.

## Required Verification

Use the injected shared tools. The runtime-isolation command has exactly one
known baseline failure on unchanged `b05ee20a` from `app/config.py`; do not edit
around it. Your candidate is valid only if it adds zero failures and modifies no
file under `app/` or the protected isolation test.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_runtime_isolation.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile tests\workflow_chain\harness.py scripts\bernie_workflow_chain_report.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_workflow_chain.py tests\test_bernie_workflow_chain_report.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_workflow_chain_report.py
git diff --check
```

Write the final artifact at the exact expected path. Include candidate commit,
changed files, baseline comparison, verification results, boundary confirmation,
and `STATUS: complete`.
