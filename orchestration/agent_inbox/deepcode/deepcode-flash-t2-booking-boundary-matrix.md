# DeepSeek Flash T2.1 - Booking Boundary and Invariant Matrix

Role: bounded backend test implementation worker
Model: `deepseek-v4-flash` / high
Parent: `docs/bernie-t2-deterministic-behaviour-matrix.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-deepseek-t2-booking-boundary-matrix.md`

## Mission

Add missing deterministic generated boundary and invariant coverage for Bernie
booking behavior. First inventory `tests/test_bernie_booking_classifier.py`,
the T1 scenario corpus, slot-search tests, and idempotency tests. Do not duplicate
an existing assertion merely to increase counts.

Prefer a new focused module such as
`tests/test_bernie_booking_boundary_matrix.py`. Keep a small authored golden
table independent of production branching, plus generated/parametrized cases
for invariants rather than copying the classifier algorithm into the test.

## Required Coverage

- half-open interval edges: end equals start, start equals end, one-minute
  intersection, containment, and duration extension;
- date and active/terminal-status boundaries;
- stable result under insertion/query ordering where more than one appointment
  exists;
- read-only behavior: no appointment or audit-row mutation;
- route candidates remain within normalized bounds and avoid occupied
  practitioner intervals for representative generated cases; and
- explicit cross-reference showing which requested invariant was already
  covered and therefore intentionally not duplicated.

Use deterministic authored integer/time tables; do not add Hypothesis or another
dependency. If a generated case exposes a product defect, preserve the failing
case as an honest xfail or report it precisely; do not change `app/` production
code in this worker lane.

## Ownership

- new focused tests under `tests/`
- optional authored synthetic fixture/table under `tests/fixtures/`
- optional bounded update to `docs/bernie-t2-deterministic-behaviour-matrix.md`
- expected artifact above

Do not edit `app/`, `review/`, `docs/diary/`, AGENTS, phase programmes,
orchestration policy, providers, schemas, migrations, or unrelated tests.

Create one candidate commit only. Do not push, integrate master, or move
`handoff/current`.

## Verification

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_booking_boundary_matrix.py tests\test_bernie_booking_classifier.py tests\test_slot_search_proposal.py -q
git diff --check
```

Write the expected artifact with changed files, candidate commit as resolved by
Git/receipt (do not embed a self-referential final SHA if the artifact is in the
same commit), coverage added versus intentionally reused, test results, findings,
boundaries, and `STATUS: complete`.
