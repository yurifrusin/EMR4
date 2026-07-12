# S6 Amended Lane 2: Independent Review And Veto

Role: independent code/security/test reviewer
Resource: `deepseek-flash-workers`
Model: `deepseek-v4-flash`
Reasoning: high
Conductor plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s6-scope-delta.md`
Candidate commit: `38d95ed0404831b0f7eba4e3c9de2733cb975ef1`
Review artifact: `orchestration/agent_inbox/codex/review-deepseek-s6-scope-delta-review.md`

You are in a fresh disposable review worktree containing the Lane 1 candidate.
Read the plan, all Lane 1 artifacts, and the candidate diff. You have veto
authority but no implementation ownership. Do not modify production or test
files, commit, push, merge, or rebase. Write only the review artifact above.

Review the candidate against these requirements:

1. `saveBooking()` must retain the existing invalid-practitioner guard before
   dereferencing `practitioner`.
2. A selected GraphQL directory UUID must never be stored or used as an AHPRA
   number. AHPRA may come from a known practitioner map/template match and must
   be nullable when no mapping exists.
3. Signed create/update-confirm tests and their network assertions remain at
   full strength; no skip, xfail, renamed test, or silent assertion removal.
4. Default practitioner-directory tests must assert `POST /api/v1/graphql`,
   authorization, exact variables (`activeOnly`, `limit`, `offset`), approved
   projection, no sensitive fields, no successful REST fallback, HTTP 401 token
   clearing, 200-row rendering, and zero directory traffic in `?smoke=true`.
5. Runtime edit delivery includes only the required `diary.js` cache bust.
6. No adjacent gate, backend, provider, database, H-series, historical diary,
   RAG, deployment, or product-policy change.

Lane 1's final artifact says `138 passed`; Sol independently collected 139 and
ran all 139 successfully. Resolve and explicitly report this evidence-count
discrepancy. Fail the candidate if collection or execution does not independently
show 139 passing tests.

Run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest review/test_diary_smoke.py --collect-only -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest review/test_diary_smoke.py -q --tb=short
node --check docs/diary/diary.js
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/check_frontend_versions.py
git diff --check master...HEAD
git diff --stat master...HEAD
```

The artifact must list findings first, exact command results, boundary review,
the test-count resolution, and one final verdict:

```text
VERDICT: PASS
STATUS: complete
```

or

```text
VERDICT: REVISION_REQUIRED
STATUS: complete
```
