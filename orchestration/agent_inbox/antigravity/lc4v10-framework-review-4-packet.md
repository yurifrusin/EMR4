# LC4V10 Final Stable Pre-Content Veto

Use a fresh Antigravity project in
`C:\Users\sarashera\EMR4-worktrees\lc4v10-gemini-framework-review-4` on branch
`gemini/lc4v10-framework-review-4`. Review the exact bound source/carrier head.
Do not reuse any prior project.

Use the same exact read allowlist as review 3 plus the third review artifact.
All holdouts v1-v9 and every protected surface remain forbidden; do not list,
search, inspect, import, or infer them.

Verify no framework/product/contract/threshold/protected change after recovered
head `d56db482`. Reconfirm all eight recovery defects remain closed. Run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_lc4v10_content_blind_framework.py tests\test_bernie_certification_decision_taxonomy.py tests\test_bernie_lc4v9d1_development.py tests\test_agents_handover_archive.py
git diff --check d56db482^..d56db482 -- app/services/bernie/lc4v10_content_blind_framework.py tests/test_bernie_lc4v10_content_blind_framework.py AGENTS.md
git diff --check HEAD^..HEAD
```

Require 114/114 and both scoped diff checks clean. Do not apply cumulative
whitespace policy to preserved worker attestations from earlier commits and do
not rewrite them. Any other failure returns `DECISION: revision_required`.

Write and commit only
`orchestration/agent_inbox/antigravity/lc4v10-framework-review-4.md`. Before
commit, run `git diff --check` on your uncommitted review file. Include the five
rehydration sources, exact heads, changed-file scope, 114/114 evidence,
eight-defect audit, no-content finding, and final line exactly
`DECISION: pass` or `DECISION: revision_required`. Do not push.
