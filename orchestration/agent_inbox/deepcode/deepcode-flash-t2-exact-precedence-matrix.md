# DeepSeek Flash T2.2 - Exact-Match Precedence Matrix

Role: bounded backend test implementation worker
Model: `deepseek-v4-flash` / high
Parent: `docs/bernie-t2-deterministic-behaviour-matrix.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-deepseek-t2-exact-precedence-matrix.md`

## Mission

Extend the economical generated classifier matrix across interacting exact-match
dimensions: practitioner, appointment type, location, duration, and temporal
evidence. Inventory current classifier, generated-matrix, and authored tests
first. Do not duplicate the T2.1 interval geometry matrix or DB-backed tests.

Use the public `classify_existing_booking()` function. Prefer one generated
matrix execution with labelled failures and hundreds of deterministic
combinations, rather than hundreds of pytest nodes with repeated fixture setup.
A query-only session stub is acceptable for this service-level matrix, provided
that any attempted write fails and the document states that terminal filtering
and persistence truth remain covered by DB-backed authored tests.

## Required Acceptance

- combine matching/mismatching practitioner, optional matching/mismatching
  appointment type, optional matching/mismatching location, optional
  matching/mismatching duration, and temporal modes (both bounds,
  earliest-only, latest-only, no bounds, and outside window);
- exact duplicate occurs only when practitioner, supplied dimensions, and
  mandatory temporal evidence all satisfy the independent contract table;
- non-exact cases retain the correct overlap or same-day-distinct outcome;
- at least 200 labelled combinations execute through the public classifier;
- the matrix has a stable count guard and completes in a routine-gate budget;
- no production code or DB is changed; and
- report current authored DB-backed coverage deliberately reused for terminal
  statuses, roster, breaks, location query filtering, normalized bounds, stale
  confirmation, no-write, and tenancy.

## Ownership

- new focused test under `tests/`
- expected artifact above

Do not edit `app/`, `review/`, `docs/diary/`, AGENTS, roadmap documents,
orchestration policy, providers, schemas, migrations, or unrelated tests.
Create one candidate commit only. Do not push, integrate master, or move
`handoff/current`.

## Verification

```powershell
pytest <new-focused-test> tests\test_bernie_booking_generated_matrix.py tests\test_bernie_booking_classifier.py -q
git diff --check
```

Write the expected artifact with matrix axes/count, changed files, candidate
commit resolution, test results, reused DB-backed coverage, findings,
boundaries, and `STATUS: complete`.
