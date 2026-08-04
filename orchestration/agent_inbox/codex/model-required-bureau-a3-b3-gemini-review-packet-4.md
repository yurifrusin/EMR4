# Independent source-only veto 4: A3/B3 identity and freshness controls

Review date: 2026-08-04

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\model-required-bureau-a3-b3-gemini-review-4`

Bound branch:
`codex/review-model-required-bureau-a3-b3-4`

Exact candidate HEAD:
`c95a0ee1a235843fe8498a8979e43151f7f4277e`

This is a genuinely fresh Gemini 3.6 Flash/high Antigravity project on the
exact clean read-only candidate. Earlier source reviews are historical and do
not review the final identity/freshness patch. Candidate-runtime provider-call
count remains zero.

Do not quote, reproduce or discuss any prior terminal-decision line. Use the
terminal-decision prefix exactly once in your own output, only on its last
line.

## Review task

Read `AGENTS.md`, then the A3/B3 plan, threat model, authority, contracts,
schemas, broker, live harness, acceptance, tests and all three candidate
commits. Verify worktree, branch, exact HEAD and cleanliness first. Do not edit,
create, stage, commit, push, invoke Docker/provider/cloud/product/database/
runtime, inspect credentials, deploy or move refs. Temporary test output must
remain outside the worktree.

Adversarially review the full candidate and especially the final change from
`ae94cee0b694f1a130fcf1671b3b411db258db5e` to
`c95a0ee1a235843fe8498a8979e43151f7f4277e`:

- live HTTP success must release nothing unless the sanitized observed
  `modelVersion` is exactly `gemini-2.5-flash`; missing, versioned, different,
  dry-run or malformed values must fail before provider-body parsing and
  proofreading while preserving terminal ledger/audit/cost accounting;
- dry-run identity must remain exactly `provider-free-selector-fixture` and
  cannot be accepted in live mode;
- Rayleen `generated_at` and Davida `observed_at` must satisfy the half-open
  interval through the explicit timezone-aware `evaluation_time`, with
  `evaluation_mode` fixed to `authored_synthetic_fixed_clock`; equality at the
  lower bound passes and equality at expiry fails;
- the release must bind that evaluation instant/mode and claims must not imply
  fixture freshness against execution wall-clock time;
- Davida content revision and every regenerated request/evidence/audit hash
  must remain internally consistent;
- provider-free and occupied ledger/audit/evidence paths remain disjoint, one-
  use and bounded by schema-only correction, per-lane/total calls and USD 1;
- provider/model/project/identity/Sydney host+path, request hash, redirect/proxy
  denial, host-only ADC, raw-content nonretention and cleanup remain exact;
- selector-only model fields cannot mint context, provenance, dry-run truth,
  authority, command, write, success or readback;
- no product imports, API route, database, event, actuator, deployment or
  protected-ref effect exists; and
- evidence distinguishes this non-zero source-review transport from the still-
  zero candidate-runtime provider-call count.

## Exact provider-free commands

```powershell
git status --short --branch
git rev-parse HEAD
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\model_required_bureau_a3_b3_acceptance.py --require-dry-run
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_serial_pytest.py --timeout-seconds 240 -- tests\test_model_required_bureau_a3_b3.py tests\test_model_required_bureau_gate_zero.py tests\test_model_required_bureau_gate_zero_continuity.py tests\test_model_required_bureau_successor_lanes.py tests\test_model_required_bureau_successor_lanes_continuity.py tests\test_model_required_bureau_c3_d3.py tests\test_model_required_bureau_c3_d3_continuity.py tests\test_model_required_bureau_standing_continuation.py tests\test_ariadne_autonomous_continuation.py tests\test_api_spine_artifacts.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_verifier_worktree_preflight.py tests\test_ariadne_antigravity.py -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-a3-b3-gemini-review-4
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\model_required_bureau_a3_b3_contracts.py scripts\model_required_bureau_a3_b3_broker.py scripts\model_required_bureau_a3_b3_live.py scripts\model_required_bureau_a3_b3_acceptance.py tests\test_model_required_bureau_a3_b3.py
git diff --check ae94cee0b694f1a130fcf1671b3b411db258db5e..c95a0ee1a235843fe8498a8979e43151f7f4277e
git diff --check 2de467e23ce44574395ad6115e7205ca27c96fb2..c95a0ee1a235843fe8498a8979e43151f7f4277e
git status --short --branch
git rev-parse HEAD
```

Report actionable findings first with severity and exact file/line evidence.
Separate observed facts from inference. If there are no findings, say so once.
After all analysis, emit exactly one last line beginning with `DECISION:` and
choose exactly one value: `pass` or `revision_required`. Never use that prefix
anywhere else in the response.
