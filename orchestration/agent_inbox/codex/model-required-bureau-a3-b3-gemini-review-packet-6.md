# Independent source-only veto 6: A3/B3 reservation recovery

Review date: 2026-08-04

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\model-required-bureau-a3-b3-gemini-review-6`

Bound branch:
`codex/review-model-required-bureau-a3-b3-6`

Exact candidate HEAD:
`61ca38545ad01d2470f8b5b668dd746b88d113a2`

This is a fresh Gemini 3.6 Flash/high Antigravity project and a fresh clean
read-only worktree. Review committed repository source and authored-synthetic or
sanitized evidence only. The existing Bernie impersonated ADC is unavailable.
Do not inspect, refresh, restore, or reconfigure credentials. Candidate-runtime
provider-call count is zero.

## Review task

Read `AGENTS.md`, the active A3/B3 plan, threat delta, preflight-blocked
checkpoint, AER revision 8, blocked schema/evidence, original open cost ledger,
live harness, acceptance, and tests. Verify the exact HEAD, branch, and clean
worktree before and after. Do not edit or create files, stage, commit, push,
invoke the live harness, Docker, Vertex/cloud controls, credentials, product,
database, runtime, deploy, Pages, or protected refs. Put temporary pytest output
outside the worktree.

Adversarially review the full candidate and especially
`c95a0ee1a235843fe8498a8979e43151f7f4277e..61ca38545ad01d2470f8b5b668dd746b88d113a2`:

- blocked evidence must truthfully bind `impersonated_adc_refresh_failed`, the
  exact source/review HEAD, canonical cost-ledger path and SHA-256, one Rayleen
  USD 0.25 reservation, zero consumed calls, zero prompt/inference/attempt
  artifacts/cells, and zero runtime residue;
- resume must be live-only, require the exact blocked evidence and canonical
  existing ledger, validate both closed schemas and hash equality, reject drift,
  and reject any existing preflight/attempt ledger/audit/evidence artifact;
- the loop must reuse the Rayleen primary reservation exactly once and never
  skip a correction or Davida reservation;
- locking must precede ledger admission/mutation; cleanup must remove the lock;
  repeated or concurrent resume must not double-send;
- two admitted primaries must total exactly two reservations, two consumed
  calls, and USD 0.50 while all existing per-lane, four-call, and USD 1 ceilings
  remain intact;
- review 4 is historical for the earlier source; this review covers the changed
  recovery source and is not candidate-runtime evidence;
- AER-0016 must remain truthful and must not blame the provider/model or claim a
  provider call; and
- the result remains blocked, without patient/clinical/product/protected data,
  credentials, product/database writes, deployment, release, Pages, or
  protected-ref effects.

## Exact provider-free commands

```powershell
git status --short --branch
git rev-parse HEAD
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\model_required_bureau_a3_b3_acceptance.py --require-dry-run
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_agent_error_register.py
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_serial_pytest.py --timeout-seconds 300 -- tests\test_model_required_bureau_a3_b3.py tests\test_model_required_bureau_gate_zero.py tests\test_model_required_bureau_gate_zero_continuity.py tests\test_model_required_bureau_successor_lanes.py tests\test_model_required_bureau_successor_lanes_continuity.py tests\test_model_required_bureau_c3_d3.py tests\test_model_required_bureau_c3_d3_continuity.py tests\test_model_required_bureau_standing_continuation.py tests\test_ariadne_autonomous_continuation.py tests\test_api_spine_artifacts.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_verifier_worktree_preflight.py tests\test_ariadne_antigravity.py -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-a3-b3-gemini-review-6
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\model_required_bureau_a3_b3_contracts.py scripts\model_required_bureau_a3_b3_broker.py scripts\model_required_bureau_a3_b3_live.py scripts\model_required_bureau_a3_b3_acceptance.py scripts\ariadne_agent_error_register.py tests\test_model_required_bureau_a3_b3.py tests\test_ariadne_agent_error_register.py
git diff --check c95a0ee1a235843fe8498a8979e43151f7f4277e..61ca38545ad01d2470f8b5b668dd746b88d113a2
git diff --check 2de467e23ce44574395ad6115e7205ca27c96fb2..61ca38545ad01d2470f8b5b668dd746b88d113a2
git status --short --branch
git rev-parse HEAD
```

Report actionable findings first with severity and exact file/line evidence.
Separate observed fact from inference. If there are no findings, say so once.

Your response must end with the wrapper's terminal marker. Emit that marker on
exactly one line and only as the final line. Do not quote, preview, explain, or
repeat the marker anywhere else. Choose the passing value only when there is no
blocking finding; otherwise choose the revision-required value.
