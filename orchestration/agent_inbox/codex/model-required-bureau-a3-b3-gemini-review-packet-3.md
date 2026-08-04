# Independent source-only veto 3: corrected A3/B3 candidate

Review date: 2026-08-04

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\model-required-bureau-a3-b3-gemini-review-2`

Bound branch:
`codex/review-model-required-bureau-a3-b3-2`

Exact candidate HEAD:
`ae94cee0b694f1a130fcf1671b3b411db258db5e`

This is a genuinely fresh Gemini 3.6 Flash/high Antigravity project on the
same unchanged clean read-only candidate. The preceding review transport was
discarded solely because it emitted two terminal-decision lines. It established
no accepted source finding or verdict and made no candidate/runtime call.

Do not quote, reproduce or discuss any prior terminal-decision line. Your final
response must contain exactly one line beginning with the terminal-decision
keyword, and that line must occur only as the last line of your response.

## Review task

Read `AGENTS.md`, then the A3/B3 plan, threat model, authority, contracts,
schemas, broker, live harness, acceptance, tests and both candidate commits.
Verify worktree, branch, exact HEAD and cleanliness first. Do not edit, create,
stage, commit, push, invoke Docker/provider/cloud/product/database/runtime,
inspect credentials, deploy or move refs. Temporary test output must remain
outside the worktree.

Adversarially review the full candidate and especially the repair from
`09218f638d31d7b8241c6e4c3bea54d25b0f2b76` to
`ae94cee0b694f1a130fcf1671b3b411db258db5e`:

- provider-free and occupied ledger/audit/evidence paths must be disjoint for
  both lanes and both turns, while the corresponding turn's preflight stays
  exactly bound;
- no prior dry-run artifact may block, overwrite or be reused by occupancy;
- no second turn may bypass schema-only correction eligibility, per-lane/totals
  or USD-1 reservation;
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
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_serial_pytest.py --timeout-seconds 180 -- tests\test_model_required_bureau_a3_b3.py tests\test_model_required_bureau_gate_zero.py tests\test_model_required_bureau_successor_lanes.py tests\test_model_required_bureau_standing_continuation.py tests\test_api_spine_artifacts.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_verifier_worktree_preflight.py tests\test_ariadne_antigravity.py -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-a3-b3-gemini-review-3
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\model_required_bureau_a3_b3_contracts.py scripts\model_required_bureau_a3_b3_broker.py scripts\model_required_bureau_a3_b3_live.py scripts\model_required_bureau_a3_b3_acceptance.py tests\test_model_required_bureau_a3_b3.py
git diff --check 09218f638d31d7b8241c6e4c3bea54d25b0f2b76..ae94cee0b694f1a130fcf1671b3b411db258db5e
git diff --check 2de467e23ce44574395ad6115e7205ca27c96fb2..ae94cee0b694f1a130fcf1671b3b411db258db5e
git status --short --branch
git rev-parse HEAD
```

Report actionable findings first with severity and exact file/line evidence.
Separate observed facts from inference. If there are no findings, say so once.
After all analysis, emit exactly one terminal line, as the final line only,
using the wrapper's required prefix. If there is no blocking finding, that
final line is `DECISION: pass`. If revision is required, use the same prefix
once with the value `revision_required`; never print both forms.
