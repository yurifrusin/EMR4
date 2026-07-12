# S6 Amended Lane 1: Required Revision 2

Role: implementation owner, same lane
Resource: `deepseek-flash-workers`
Model: `deepseek-v4-flash`
Reasoning: high
Revision artifact: `orchestration/agent_inbox/codex/review-deepseek-s6-scope-delta-repair-revision-2.md`

The prior revision transport stalled and produced no completion artifact. Sol
terminated the idle process tree, preserved the worktree, and independently ran
the full diary smoke suite. Result: 138 passed, exactly 1 failed.

Your runtime correction now satisfies the two static-review requirements: the
null guard precedes practitioner dereference, and the derived AHPRA falls back
to `null` instead of treating a directory UUID as an AHPRA number. The unused
query copy is removed and camelCase sensitive GraphQL names are asserted.

The only remaining failure is your newly added invalid-practitioner guard
assertion in
`test_practitioner_directory_limit_200_cap_renders_all_returned_rows`. Calling
`saveBooking()` with no patient/provisional context correctly stops at the
earlier validation and reports `Please select a patient or book as provisional.`

Repair only that test setup. Before invoking `saveBooking()`:

- establish deterministic provisional or selected-patient context; and
- put/select an option whose value is not present in
  `activePractitionerDirectory` or `ahpraToPractitionerMap`.

Then assert the established `Practitioner ID not found` validation appears.
Do not alter production code again unless the rerun proves it necessary. Do not
weaken, remove, skip, or xfail any test. Do not commit or push.

Run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest review/test_diary_smoke.py -q --tb=short
node --check docs/diary/diary.js
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/check_frontend_versions.py
git diff --check
git diff --stat
```

Report exact results and end with `STATUS: complete` only if the full suite has
zero failures; otherwise end with `STATUS: revision_required`.
