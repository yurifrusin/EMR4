# Independent source-only veto: model-required Bureau A3/B3 rehearsal

Review date: 2026-08-04

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\model-required-bureau-a3-b3-gemini-review`

Bound branch:
`codex/review-model-required-bureau-a3-b3`

Baseline HEAD:
`2de467e23ce44574395ad6115e7205ca27c96fb2`

Exact candidate HEAD:
`09218f638d31d7b8241c6e4c3bea54d25b0f2b76`

## Authority and accounting

This is a fresh Gemini 3.6 Flash/high source-only independent veto through a
new Antigravity project. The source-review transport is deliberately non-zero
and is not A3/B3 candidate-runtime provider evidence. The committed candidate
contains a provider-free Docker rehearsal with exactly zero inference calls.

Use only the bound worktree. Begin by reading `AGENTS.md` completely, then the
active A3/B3 plan, exact authority, contract, threat-model delta, source,
schemas, fixtures, evidence and tests. Verify the exact worktree, branch, HEAD
and tracked cleanliness. Do not inspect another worktree or historical
Antigravity project. Do not edit, create, delete, stage, commit, push, deploy,
move refs, invoke a provider/runtime harness, inspect credentials or make cloud,
database, product or network calls. Tests listed below are provider-free and
must run with bytecode/cache output disabled or outside the worktree.

## Review scope

Adversarially review the candidate diff and exact implementation for:

- selector-only model bodies versus broker-owned scope, revision, provenance,
  dry-run truth and denied authority;
- A3 unique-longest-wait grounding and B3 deterministic dry-run/hash/resource-
  kind grounding;
- prompt injection, unknown fields, stale/cross-lane/cross-kind substitution,
  authority forgery, ambiguous correction and semantic retry;
- exact `gemini-2.5-flash`, `bernie-emr4-dev`, impersonated service account,
  `australia-southeast1`, regional host/path and no-fallback equality;
- explicit redirect/proxy denial, strict hostile-byte parsing, raw prompt/
  response nonretention and sanitized provider errors/metadata;
- race-free one-use broker admission, exact ledgers, four-call/USD-1 parent
  ceiling, no call after admission and correction-only second turns;
- credential-free container policy, exact build context, host-only ADC,
  task-scoped cleanup and residue evidence;
- API Spine classification and absence of product imports/routes, GraphQL
  invocation, database access, commands, writes, events or actuators;
- whether the provider-free audit/evidence truthfully proves zero candidate-
  runtime calls and avoids overstating Sydney physical/sovereign processing,
  product safety, production fitness or clinical/admin authority.

Pay particular attention to any route that could send before request-hash or
budget admission, reuse a consumed ledger, follow a redirect, copy model-
authored authority, retain hostile raw material, skip cleanup, or convert a
proofreader admission into an operational claim.

## Exact commands

Run these read-only/provider-free commands in the bound worktree:

```powershell
git status --short --branch
git rev-parse HEAD
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\model_required_bureau_a3_b3_acceptance.py --require-dry-run
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B scripts\ariadne_serial_pytest.py --timeout-seconds 180 -- tests\test_model_required_bureau_a3_b3.py tests\test_model_required_bureau_gate_zero.py tests\test_model_required_bureau_successor_lanes.py tests\test_model_required_bureau_standing_continuation.py tests\test_api_spine_artifacts.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_verifier_worktree_preflight.py tests\test_ariadne_antigravity.py -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-a3-b3-gemini-review
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\model_required_bureau_a3_b3_contracts.py scripts\model_required_bureau_a3_b3_broker.py scripts\model_required_bureau_a3_b3_live.py scripts\model_required_bureau_a3_b3_acceptance.py tests\test_model_required_bureau_a3_b3.py
git diff --check 2de467e23ce44574395ad6115e7205ca27c96fb2..09218f638d31d7b8241c6e4c3bea54d25b0f2b76
git diff --name-status 2de467e23ce44574395ad6115e7205ca27c96fb2..09218f638d31d7b8241c6e4c3bea54d25b0f2b76
git status --short --branch
git rev-parse HEAD
```

Additional checks must remain read-only, source-only and provider-free. Report
actionable findings first with severity and exact file/line evidence. Separate
observed facts from inference, and separately account for source-review
transport and candidate-runtime provider calls.

End with exactly one terminal line:

`DECISION: pass`

or

`DECISION: revision_required`
