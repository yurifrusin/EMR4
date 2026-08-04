# A3/B3 exact-HEAD recovery veto 8

Review only this clean read-only worktree:

- worktree: `C:\Users\sarashera\EMR4-worktrees\model-required-bureau-a3-b3-gemini-review-8`
- branch: `codex/review-model-required-bureau-a3-b3-8`
- HEAD: `794748c06b9a7c0d990ea5197d24e7cb859ae1e8`
- model: Gemini 3.6 Flash/high, effort high

Do not edit or create files, stage, commit, push, invoke the live harness,
Docker, credentials, Vertex/cloud controls, product, database, runtime, deploy,
Pages or protected refs. Use only committed source and authored-synthetic or
sanitized evidence. Put test temporaries outside the worktree.

Review `61ca38545ad01d2470f8b5b668dd746b88d113a2..794748c06b9a7c0d990ea5197d24e7cb859ae1e8`.
Read the active A3/B3 plan/threat/checkpoint, Review 7 packet and sanitized
failure, AER revisions 9-10, interruption evidence, child ledger/audit,
reconciled parent/attempt/tranche evidence, acceptance, broker/live/acceptance
source and tests.

Verify:

- exactly one historical Rayleen call ended `provider_content_invalid` before proofreading; no release, correction or Davida start;
- reconciliation made zero provider calls, consumes exactly one reserved USD 0.25 call, binds canonical tracked exact-source inputs, rejects later attempts/copies/partial state and writes only after all guards;
- terminal evidence is full-object exact, no-release, metadata-unknown where not retained, with truthful current-versus-original cleanup claims;
- provider-call source `61ca3854...`, reconciliation source `b5d08bf5...` and current candidate `794748c0...` remain distinct and correctly bound;
- acceptance records one historical candidate-runtime call separately from zero acceptance-runtime calls and validates ancestry/source hashes;
- broker rejection metadata uses a strict allowlist;
- AER-0017 remains open pending this veto and AER-0018 truthfully contains Review 7's duplicate-decision envelope without claiming a candidate finding;
- no API Spine, authority, data, runtime, write, deployment, Pages or protected-ref boundary expanded.

Run these provider-free commands:

```powershell
git status --short --branch
git rev-parse HEAD
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\model_required_bureau_a3_b3_acceptance.py --require-dry-run
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_agent_error_register.py
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_serial_pytest.py --timeout-seconds 300 -- tests\test_model_required_bureau_a3_b3.py tests\test_model_required_bureau_gate_zero.py tests\test_model_required_bureau_gate_zero_continuity.py tests\test_model_required_bureau_successor_lanes.py tests\test_model_required_bureau_successor_lanes_continuity.py tests\test_model_required_bureau_c3_d3.py tests\test_model_required_bureau_c3_d3_continuity.py tests\test_model_required_bureau_standing_continuation.py tests\test_ariadne_autonomous_continuation.py tests\test_api_spine_artifacts.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_verifier_worktree_preflight.py tests\test_ariadne_antigravity.py -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-a3-b3-gemini-review-8
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\model_required_bureau_a3_b3_contracts.py scripts\model_required_bureau_a3_b3_broker.py scripts\model_required_bureau_a3_b3_live.py scripts\model_required_bureau_a3_b3_acceptance.py scripts\ariadne_agent_error_register.py tests\test_model_required_bureau_a3_b3.py tests\test_ariadne_agent_error_register.py
git diff --check 61ca38545ad01d2470f8b5b668dd746b88d113a2..794748c06b9a7c0d990ea5197d24e7cb859ae1e8
git status --short --branch
git rev-parse HEAD
```

Report actionable findings first with severity and exact file/line evidence.
Separate observed fact from inference. If there are no findings, say so once.

Output contract: never write the substring `DECISION:` before the final line.
The final line must be exactly `DECISION: pass` when there is no blocking
finding, or exactly `DECISION: revision_required` otherwise. Do not quote,
preview, explain or repeat that final line.
