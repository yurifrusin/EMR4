# S6 Amended Lane 1: Required Revision

Role: implementation owner, same lane
Resource: `deepseek-flash-workers`
Model: `deepseek-v4-flash`
Reasoning: high
Prior artifact: `orchestration/agent_inbox/codex/review-deepseek-s6-scope-delta-repair.md`
Revision artifact: `orchestration/agent_inbox/codex/review-deepseek-s6-scope-delta-repair-revision.md`

Sol independently reproduced your full result: 139 diary smoke tests pass, the
JavaScript syntax check passes, and the asset-version check passes. The
candidate is nevertheless `REVISION_REQUIRED` because static review found two
correctness defects outside the exercised fixture paths. Revise your existing
candidate in the same worktree. Do not commit, push, or change scope.

## Required Corrections

1. `practitioner.ahpra_number` is currently read before the existing
   `if (!practitioner || !practitioner.id)` guard. An invalid selection now
   throws a TypeError instead of displaying the established validation error.
   Keep the null/id guard before any practitioner property dereference.

2. The final `|| practitionerSelection` fallback can write a GraphQL directory
   practitioner UUID into `ahpra_number`. The packet explicitly prohibited
   treating a directory ID as an AHPRA number. Derive the nullable AHPRA from
   known mappings only: reverse-match `practitioner.id` in
   `ahpraToPractitionerMap` and/or use a matching active-template column's
   `practitioner_ahpra`. If neither mapping exists, use `null`. The legacy path
   remains supported because its selection resolves through
   `ahpraToPractitionerMap`.

3. Remove the unused local
   `PRACTITIONER_DIRECTORY_GRAPHQL_QUERY_FRAGMENT`; the live request body is the
   contract under test and duplicating the query in the fixture adds drift.

4. The sensitive-field assertion currently checks mainly REST snake_case names.
   Assert the actual prohibited GraphQL projection names too:
   `providerNumber`, `prescriberNumber`, `ahpraNumber`, and `hpiI`, as well as
   `email`, `phone`, and `address`. Do not remove the response/page canaries.

Add or strengthen a focused assertion for the invalid-practitioner guard if it
can be done without weakening or skipping any existing check. Preserve all
signed-confirm assertions and the exact three-file implementation boundary.

## Required Verification

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest review/test_diary_smoke.py -q --tb=short
node --check docs/diary/diary.js
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/check_frontend_versions.py
git diff --check
git diff --stat
```

Report exact results and end the revision artifact with exactly one marker:

```text
STATUS: complete
```

or

```text
STATUS: revision_required
```
