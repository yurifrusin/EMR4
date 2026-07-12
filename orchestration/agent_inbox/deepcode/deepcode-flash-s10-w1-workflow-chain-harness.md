# DeepSeek Flash W1 - S10 Workflow Chain Harness

Role: implementation owner
Resource: `deepseek-flash-workers` (instance 1)
Model: `deepseek-v4-flash` / high
Parent plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s10-receptionist-workflow.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-deepseek-s10-w1-workflow-chain.md`

## Authority

Implement only this allocated W1 surface. Create a candidate commit on the
assigned disposable branch, but do not push, integrate, alter protected master,
advance `handoff/current`, or claim acceptance. Terra owns acceptance and
staging integration. Do not edit W2-owned files or change S10 scope.

## Ownership

- `app/services/bernie/workflow_chain.py` (new)
- `tests/fixtures/bernie_workflow_chains/` (new, entire directory)
- `tests/test_bernie_workflow_chain.py` (new)
- `scripts/bernie_workflow_chain_report.py` (new)
- `tests/test_bernie_workflow_chain_report.py` (new)
- Candidate-only handover notes where required to truthfully describe this W1
  submission; do not claim final S10 acceptance or integration.

Do not edit `tests/fixtures/bernie_workflow_chain_review/`,
`tests/test_bernie_workflow_chain_adversarial.py`,
`docs/adversarial/s10_workflow_chain_review.md`, existing interpretation-harness
files, any route/provider/database/UI file, or any H15/H-series, trove, RAG, or
memory surface.

## Implementation

Implement the deterministic, in-memory workflow-chain harness defined by the
parent plan. It must resolve authored synthetic multi-step receptionist utterance
sequences through the existing interpretation harness and frame projection,
carry only in-memory context between steps, preserve planned/unsafe refusal
propagation, and emit an aggregate-only report.

Use only clearly authored synthetic fixtures. Do not include raw or real patient,
practitioner, appointment, slot, address, or other identifying data. The report
must omit utterance text and all payload identifiers. The module and tests must
prove they do not import or invoke routes, providers, database access, H15/
H-series, historical diary trove, memory, RAG, or GraphRAG.

The user-owned terminal-to-active appointment status policy remains untouched.
No route dispatch, provider call, database write, audit write, or confirmation
authority is permitted.

## Required Verification

Use the injected shared tools before declaring them unavailable:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile app\services\bernie\workflow_chain.py scripts\bernie_workflow_chain_report.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_workflow_chain.py tests\test_bernie_workflow_chain_report.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_workflow_chain_report.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_interpretation_readiness_check.py -q
git diff --check
```

Write the final artifact exactly to the expected path. Include the candidate
commit SHA, changed files, commands/results, closed-gate confirmation, and
`STATUS: complete` only after all work is complete.
