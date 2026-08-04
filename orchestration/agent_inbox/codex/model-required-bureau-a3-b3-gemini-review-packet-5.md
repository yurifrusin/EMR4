# Independent source-only veto 5: A3/B3 preflight-reservation recovery

Review date: 2026-08-04

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\model-required-bureau-a3-b3-gemini-review-5`

Bound branch:
`codex/review-model-required-bureau-a3-b3-5`

Exact candidate HEAD:
`61ca38545ad01d2470f8b5b668dd746b88d113a2`

This is a genuinely fresh Gemini 3.6 Flash/high Antigravity project. It reviews
only committed repository source and authored-synthetic/sanitized evidence.
The existing Bernie impersonated ADC is currently unavailable, and the source
review must not inspect, refresh, restore or reconfigure it. Candidate-runtime
provider-call count is zero.

Do not quote or discuss prior terminal-decision lines. Use the terminal prefix
exactly once in your response and only on its final line.

## Review task

Read `AGENTS.md`, the active A3/B3 plan, threat delta, preflight-blocked
checkpoint, AER revision 8, blocked schema/evidence, original open cost ledger,
live harness, acceptance and tests. Verify the worktree, branch, exact HEAD and
cleanliness before and after. Do not edit/create/stage/commit/push, invoke the
live harness, Docker, Vertex/cloud controls, credentials, product, database or
runtime, deploy or move refs. Put temporary pytest output outside the worktree.

Adversarially review the full candidate and especially
`c95a0ee1a235843fe8498a8979e43151f7f4277e..61ca38545ad01d2470f8b5b668dd746b88d113a2`:

- the preserved blocked receipt must truthfully bind
  `impersonated_adc_refresh_failed`, exact source/review HEAD, the canonical
  cost-ledger path and SHA-256, one Rayleen USD 0.25 reservation, zero consumed
  calls, zero prompt/inference/attempt artifacts/cells and zero runtime residue;
- resume must be live-only, require both exact blocked evidence and the exact
  canonical existing ledger, validate both closed schemas and hash equality,
  reject any drift, and reject any preflight/attempt ledger/audit/evidence
  artifact already present;
- the resume loop must reuse Rayleen primary reservation 1 exactly once and
  must not skip reservation for any correction or Davida turn;
- lock acquisition must precede ledger admission/mutation, cleanup must remove
  the lock on all paths, and concurrent or repeated resume cannot double-send;
- after two admitted primaries, total reservations/calls must be exactly two
  and USD 0.50, not three/USD 0.75; existing per-lane/two-turn, four-call and
  USD 1 ceilings remain intact;
- source review 4 is correctly historical for `c95a0ee1…`; this review 5 is
  required for changed recovery source, while neither is candidate-runtime
  evidence;
- AER-0016 origin/category/state and deterministic pattern report are truthful
  and do not blame a provider/model or claim a provider call;
- the checkpoint remains a blocked result, not an A3/B3 pass or Australian
  residency/product/runtime claim; and
- protected evidence, `docs/branding/`, patient/clinical/product data,
  credentials, product/database commands/writes, deployment, Pages and
  protected refs remain untouched.

## Exact provider-free commands

```powershell
git status --short --branch
git rev-parse HEAD
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\model_required_bureau_a3_b3_acceptance.py --require-dry-run
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_agent_error_register.py
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_serial_pytest.py --timeout-seconds 300 -- tests\test_model_required_bureau_a3_b3.py tests\test_model_required_bureau_gate_zero.py tests\test_model_required_bureau_gate_zero_continuity.py tests\test_model_required_bureau_successor_lanes.py tests\test_model_required_bureau_successor_lanes_continuity.py tests\test_model_required_bureau_c3_d3.py tests\test_model_required_bureau_c3_d3_continuity.py tests\test_model_required_bureau_standing_continuation.py tests\test_ariadne_autonomous_continuation.py tests\test_api_spine_artifacts.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_verifier_worktree_preflight.py tests\test_ariadne_antigravity.py -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-a3-b3-gemini-review-5
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\model_required_bureau_a3_b3_contracts.py scripts\model_required_bureau_a3_b3_broker.py scripts\model_required_bureau_a3_b3_live.py scripts\model_required_bureau_a3_b3_acceptance.py scripts\ariadne_agent_error_register.py tests\test_model_required_bureau_a3_b3.py tests\test_ariadne_agent_error_register.py
git diff --check c95a0ee1a235843fe8498a8979e43151f7f4277e..61ca38545ad01d2470f8b5b668dd746b88d113a2
git diff --check 2de467e23ce44574395ad6115e7205ca27c96fb2..61ca38545ad01d2470f8b5b668dd746b88d113a2
git status --short --branch
git rev-parse HEAD
```

Report actionable findings first with severity and exact file/line evidence.
Separate observed fact from inference. If there are no findings, say so once.
On the final line only, begin with `DECISION:` and choose one value: `pass` or
`revision_required`. Do not use that prefix elsewhere.
