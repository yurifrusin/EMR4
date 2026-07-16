# LC4V10 Exact-File Final Pre-Content Veto

Use a fresh Antigravity project in
`C:\Users\sarashera\EMR4-worktrees\lc4v10-gemini-framework-review-5` on branch
`gemini/lc4v10-framework-review-5`. Review the exact bound carrier head. Do not
reuse any prior project.

You may read only these exact files:

- `AGENTS.md`;
- `orchestration/agent_inbox/codex/lc4v10-sol-contract.md`;
- `orchestration/agent_inbox/codex/lc4v10-one-shot-acceptance-rule.md`;
- `orchestration/agent_inbox/codex/lc4v10-framework-sol-recovery.md`;
- `orchestration/agent_inbox/codex/lc4v10-framework-review-4-metadata-incident.md`;
- `app/services/bernie/lc4v10_content_blind_framework.py`;
- `tests/test_bernie_lc4v10_content_blind_framework.py`;
- `app/services/bernie/certification_decision_taxonomy.py`;
- `app/services/bernie/semantic_extraction.py`;
- `app/services/bernie/lc4v4d3_policy_resolution.py`;
- `app/services/bernie/interpretation_harness.py`;
- `tests/test_bernie_certification_decision_taxonomy.py`;
- `tests/test_bernie_lc4v9d1_development.py` only if its test fails; and
- `tests/test_agents_handover_archive.py` only if its test fails.

Do not list any directory. Do not call `Glob`, directory `ls`, `Get-ChildItem`,
`find`, broad `Grep`/`rg`, `git diff --name-only`, or any command that enumerates
filenames. Do not inspect prior review packets/artifacts or inbox contents.
All holdouts v1-v9 and every protected filename/content surface are forbidden.

Reconfirm all eight recovery defects and no actual V10 content from the exact
authorized source only. Run exactly:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_lc4v10_content_blind_framework.py tests\test_bernie_certification_decision_taxonomy.py tests\test_bernie_lc4v9d1_development.py tests\test_agents_handover_archive.py
git diff --exit-code d56db482..HEAD -- app/services/bernie/lc4v10_content_blind_framework.py tests/test_bernie_lc4v10_content_blind_framework.py app/services/bernie/certification_decision_taxonomy.py app/services/bernie/semantic_extraction.py app/services/bernie/lc4v4d3_policy_resolution.py app/services/bernie/interpretation_harness.py orchestration/agent_inbox/codex/lc4v10-sol-contract.md orchestration/agent_inbox/codex/lc4v10-one-shot-acceptance-rule.md
git diff --check d56db482^..d56db482 -- app/services/bernie/lc4v10_content_blind_framework.py tests/test_bernie_lc4v10_content_blind_framework.py
git diff --check HEAD^..HEAD
```

Require 114/114, no output/change from the exact source-drift command, and both
diff checks clean. Any failure or filename-enumeration breach returns
`DECISION: revision_required`.

Write and commit only
`orchestration/agent_inbox/antigravity/lc4v10-framework-review-5.md`. Before
commit run `git diff --check` only on that exact path. Include all five
rehydration sources, exact heads, 114/114, the exact source-drift result, eight
defects, no-content finding, access-method compliance, and final line exactly
`DECISION: pass` or `DECISION: revision_required`. Do not push.
