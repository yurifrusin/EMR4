# S6 Amended Lane 1: Diary Runtime And Smoke Repair

Role: implementation owner
Resource: `deepseek-flash-workers`
Model: `deepseek-v4-flash`
Reasoning: high
Conductor plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s6-scope-delta.md`
Completion artifact: `orchestration/agent_inbox/codex/review-deepseek-s6-scope-delta-repair.md`

You are working in a disposable worktree. Do not commit, push, merge, rebase,
or modify master. Do not edit harness policy or planning files. Your writable
implementation surface is limited to:

- `docs/diary/diary.js`
- `docs/diary/diary.html` only for the matching `diary.js` cache-bust version
- `review/test_diary_smoke.py`
- the completion artifact named above

The previous Lane 1 attempt was rejected: it weakened a network-contract test
and falsely claimed the suite passed. Start from the current files and preserve
all signed-confirm assertions, test names, skips, and test count.

## Repair A: Runtime ReferenceError

`saveBooking()` resolves the selected practitioner but later references the
removed local `ahpra`, causing `booking-error: "ahpra is not defined"` before
signed create/update confirmation.

Immediately after resolving and validating `practitioner`, derive a nullable
AHPRA value from authoritative existing mappings. A directory practitioner ID
must never itself be treated as an AHPRA number. The legacy selector path must
still work. Prefer a small local derivation such as finding the key in
`ahpraToPractitionerMap` whose mapped practitioner `id` matches
`practitioner.id`; a matching `activeTemplate.columns` entry may be a fallback.
Use that derived value for the existing break check and smoke fixture fields.
Do not expose AHPRA in the GraphQL directory projection and do not change API
contracts.

Bump the `diary.js?v=` reference in `docs/diary/diary.html` by one so the runtime
repair is delivered. Do not change CSS or any other asset version.

## Repair B: Default-On GraphQL Test Contract

Update `route_practitioner_directory_consumer_api()` and its four consumer tests
to model the current default request:

- `POST /api/v1/graphql`
- request body contains the approved practitioner query
- variables are exactly `activeOnly: true`, `limit: 200`, `offset: 0`
- response body is
  `{"data":{"practice":{"practitioners":[...]}}}`

Capture and assert the GraphQL URL, method, authorization header, query, and
variables. Assert the query does not request sensitive practitioner fields.
Keep the REST handler as a fallback surface, but a successful default GraphQL
test must not call it. For the authorization-expiry test, fulfill the GraphQL
request with HTTP status `401`; a GraphQL error body with HTTP `200` does not
exercise `apiFetch()` token clearing and is not acceptable. Keep the existing
smoke-mode test proving `?smoke=true` makes no practitioner-directory request.

The four currently stale tests are:

- `test_practitioner_directory_route_data_populates_booking_selector`
- `test_practitioner_directory_selector_keeps_legacy_fallback_for_unmapped_ahpra`
- `test_practitioner_directory_401_fails_closed_with_auth_banner`
- `test_practitioner_directory_limit_200_cap_renders_all_returned_rows`

## Required Verification

Use the repository virtual environment:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest review/test_diary_smoke.py -q --tb=short
node --check docs/diary/diary.js
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/check_frontend_versions.py
git diff --check
git diff --stat
```

Acceptance requires the full diary smoke suite to have zero failures, no xfail
or skip additions, intact signed-confirm network assertions, and a diff limited
to the three implementation files plus your completion artifact. If tests do
not pass, report the exact failures and use `STATUS: revision_required`; never
claim success from a partial or hypothetical run.

Write the completion artifact with changed files, root cause, exact verification
commands/results, boundary statement, and one terminal marker:

```text
STATUS: complete
```

or

```text
STATUS: revision_required
```
