# Independent source-only veto 2: A3/B3 occupied evidence namespace repair

Review date: 2026-08-04

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\model-required-bureau-a3-b3-gemini-review-2`

Bound branch:
`codex/review-model-required-bureau-a3-b3-2`

Baseline HEAD:
`2de467e23ce44574395ad6115e7205ca27c96fb2`

Initial reviewed candidate:
`09218f638d31d7b8241c6e4c3bea54d25b0f2b76`

Exact corrected candidate HEAD:
`ae94cee0b694f1a130fcf1671b3b411db258db5e`

## Reason for the second veto

The first Gemini 3.6 Flash/high source veto passed. Before any occupied call,
Sol found a deterministic namespace collision: provider-free ledgers/audits
already committed at the names the occupied lifecycle would attempt to create.
The live harness would therefore fail closed before provider contact. Candidate
runtime provider calls remain exactly zero.

The correction adds `_attempt_paths`, keeps the committed provider-free names
stable, gives occupied ledgers/audits/evidence an explicit `-occupied` namespace,
shares only the lane/turn preflight path, and adds a regression test proving the
two attempt artifact sets are disjoint. The first review packet, receipt and
pre-verifier evidence are now committed for truthful history.

## Authority and method

This is another genuinely fresh Gemini 3.6 Flash/high source-only Antigravity
project. It is non-zero development review transport, not A3/B3 candidate-
runtime evidence. Use only the bound clean worktree. Read `AGENTS.md`, the A3/B3
plan/threat/contract and both commits. Do not edit, create, stage, commit, push,
invoke Docker/provider/cloud/runtime/product/database, inspect credentials,
deploy or move refs. Keep test caches and temporary output outside the worktree.

Confirm that the correction:

- removes the dry-run/occupied output collision for both lanes and both turns;
- preserves exact preflight-to-attempt binding and cannot reuse an occupied
  ledger, audit or evidence path;
- preserves provider-free historical evidence names and acceptance;
- does not allow a correction turn to bypass primary/call/cost admission;
- leaves cleanup, raw-content nonretention, provider identity, API Spine and
  all authority boundaries unchanged;
- introduces no time-of-check/time-of-use or path-injection issue; and
- leaves no route for provider contact before source review, preflight, exact
  request hash, ledger reservation and cost reservation.

Also rerun the full original adversarial scope and account separately for this
source review transport and the still-zero candidate-runtime provider calls.

## Exact commands

```powershell
git status --short --branch
git rev-parse HEAD
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\model_required_bureau_a3_b3_acceptance.py --require-dry-run
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_serial_pytest.py --timeout-seconds 180 -- tests\test_model_required_bureau_a3_b3.py tests\test_model_required_bureau_gate_zero.py tests\test_model_required_bureau_successor_lanes.py tests\test_model_required_bureau_standing_continuation.py tests\test_api_spine_artifacts.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_verifier_worktree_preflight.py tests\test_ariadne_antigravity.py -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-a3-b3-gemini-review-2
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\model_required_bureau_a3_b3_contracts.py scripts\model_required_bureau_a3_b3_broker.py scripts\model_required_bureau_a3_b3_live.py scripts\model_required_bureau_a3_b3_acceptance.py tests\test_model_required_bureau_a3_b3.py
git diff --check 09218f638d31d7b8241c6e4c3bea54d25b0f2b76..ae94cee0b694f1a130fcf1671b3b411db258db5e
git diff --name-status 09218f638d31d7b8241c6e4c3bea54d25b0f2b76..ae94cee0b694f1a130fcf1671b3b411db258db5e
git diff --check 2de467e23ce44574395ad6115e7205ca27c96fb2..ae94cee0b694f1a130fcf1671b3b411db258db5e
git status --short --branch
git rev-parse HEAD
```

Report actionable findings first with severity and exact file/line evidence.
Separate observation from inference. End with exactly one terminal line:

`DECISION: pass`

or

`DECISION: revision_required`
