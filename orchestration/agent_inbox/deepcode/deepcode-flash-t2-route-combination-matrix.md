# DeepSeek Flash T2.3 - DB-Backed Route Combination Matrix

Role: bounded backend route-test implementation worker
Model: `deepseek-v4-flash` / high
Parent: `docs/bernie-t2-deterministic-behaviour-matrix.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-deepseek-t2-route-combination-matrix.md`

## Mission

Add a compact DB-backed matrix for the real slot-search proposal route. Cover
interactions that the fast query-only classifier matrices cannot prove:
appointment status filtering, same/other location conflicts, duration/time
bounds, roster presence/absence, break warnings, candidate ordering/bounds, and
absence of appointment/audit writes.

Inventory `tests/test_slot_search_proposal.py`, route fixtures, and T1/T2 tests
first. Reuse factories/helpers where practical but do not modify existing tests
merely to inflate counts. Prefer a small independent table of representative
pairwise combinations over an expensive full Cartesian product.

## Required Acceptance

- exercise the real authenticated `/api/v1/appointments/proposals/slots/search`
  route against the test DB;
- include active and every terminal status currently relevant to slot blocking;
- include same-location blocking and other-location non-blocking behavior;
- combine representative 15/30-minute appointments with earliest/latest bounds;
- include roster present and roster absent outcomes;
- include a break-overlap warning case without treating the break as an
  authoritative booking conflict;
- for every returned candidate, assert normalized date/time bounds, stable
  ordering, and no occupied same-location practitioner overlap where relevant;
- prove the entire matrix creates no appointment or appointment-audit rows;
- keep the matrix to a routine CI budget and report exact executed scenario
  count and runtime; and
- do not weaken or rewrite existing authored golden expectations.

If a case exposes a product defect, preserve a precise failing case or report
it; do not modify production code in this worker lane.

## Ownership

- one focused test under `tests/`
- expected artifact above

Do not edit `app/`, `review/`, `docs/diary/`, AGENTS, roadmap documents,
orchestration policy, providers, schemas, migrations, or unrelated tests.
Create one candidate commit only. Do not push, integrate master, or move
`handoff/current`.

## Verification

```powershell
pytest <new-focused-test> tests\test_slot_search_proposal.py -q
git diff --check
```

Write the expected artifact with scenario table/count, DB/evidence boundary,
changed files, candidate commit resolution, test results/runtime, reused
coverage, findings, and `STATUS: complete`.
