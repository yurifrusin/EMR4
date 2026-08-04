# A3/B3 exact-HEAD checkout-stability veto 9

Review only this fresh clean read-only worktree:

- worktree: `C:\Users\sarashera\EMR4-worktrees\model-required-bureau-a3-b3-gemini-review-9`
- branch: `codex/review-model-required-bureau-a3-b3-9`
- HEAD: `063153b9a799b32d125084fb77134588c9a6ac76`
- model: Gemini 3.6 Flash/high, effort high

Do not edit/create files, stage, commit, push, invoke the live harness, Docker,
credentials, Vertex/cloud controls, product, database, runtime, deploy, Pages
or protected refs. Use only committed source and authored-synthetic or
sanitized evidence. Put test temporaries outside the worktree.

Review `794748c06b9a7c0d990ea5197d24e7cb859ae1e8..063153b9a799b32d125084fb77134588c9a6ac76`
and the underlying A3/B3 reconciliation from provider-call source
`61ca38545ad01d2470f8b5b668dd746b88d113a2`. Read Review 8, AER revision 11,
`.gitattributes`, the new checkout regression, terminal evidence and acceptance
source/tests.

Verify:

- the fresh-worktree defect is exactly CRLF conversion of hash-bound audit JSONL under `core.autocrlf=true`, not mutation of the immutable original audit/hash;
- the scoped A3/B3 JSONL rule enforces LF without changing unrelated formats;
- in this genuinely fresh worktree, the occupied audit SHA-256 is exactly `27d665f162ead5ee70d9db9cb39500bbe621e63b5bc0168b91ec6fb43d82bcad`, `git check-attr eol` is `lf`, acceptance and tests pass, and the worktree stays clean;
- exactly one historical Rayleen call ended before proofreading with no release, correction or Davida; reconciliation and acceptance make zero provider calls;
- parent/attempt/tranche evidence, source-head distinctions, canonical tracked-input guards, strict broker metadata allowlist and all closed API Spine/authority/data/runtime/write/deploy/protected boundaries remain exact;
- AER-0018 truthfully contains Review 7 and AER-0017/AER-0019 remain open only pending this veto.

Run:

```powershell
git status --short --branch
git rev-parse HEAD
git check-attr eol -- orchestration/continuity/model-required-bureau-a3-b3/rayleen-a3-attempt-1-occupied-audit.jsonl
(Get-FileHash -Algorithm SHA256 orchestration/continuity/model-required-bureau-a3-b3/rayleen-a3-attempt-1-occupied-audit.jsonl).Hash.ToLower()
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\model_required_bureau_a3_b3_acceptance.py --require-dry-run
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_agent_error_register.py
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_serial_pytest.py --timeout-seconds 300 -- tests\test_model_required_bureau_a3_b3.py tests\test_model_required_bureau_gate_zero.py tests\test_model_required_bureau_gate_zero_continuity.py tests\test_model_required_bureau_successor_lanes.py tests\test_model_required_bureau_successor_lanes_continuity.py tests\test_model_required_bureau_c3_d3.py tests\test_model_required_bureau_c3_d3_continuity.py tests\test_model_required_bureau_standing_continuation.py tests\test_ariadne_autonomous_continuation.py tests\test_api_spine_artifacts.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_verifier_worktree_preflight.py tests\test_ariadne_antigravity.py -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-a3-b3-gemini-review-9
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\model_required_bureau_a3_b3_contracts.py scripts\model_required_bureau_a3_b3_broker.py scripts\model_required_bureau_a3_b3_live.py scripts\model_required_bureau_a3_b3_acceptance.py scripts\ariadne_agent_error_register.py tests\test_model_required_bureau_a3_b3.py tests\test_ariadne_agent_error_register.py
git diff --check 794748c06b9a7c0d990ea5197d24e7cb859ae1e8..063153b9a799b32d125084fb77134588c9a6ac76
git diff --check 61ca38545ad01d2470f8b5b668dd746b88d113a2..063153b9a799b32d125084fb77134588c9a6ac76
git status --short --branch
git rev-parse HEAD
```

Report actionable findings first with severity and exact file/line evidence.
Separate observed fact from inference. If there are no findings, say so once.

Output contract: never write the substring `DECISION:` before the final line.
The final line must be exactly `DECISION: pass` when there is no blocking
finding, or exactly `DECISION: revision_required` otherwise. Do not quote,
preview, explain or repeat that final line.
