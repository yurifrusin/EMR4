# LC4V9D1 Fresh Amended Independent Review

Review product source head `a58538e03dc68678b563ff1788daf6a699eff72a` from a
fresh Antigravity project in bound worktree
`C:\Users\sarashera\EMR4-worktrees\lc4v9d1-gemini-2` on branch
`gemini/lc4v9d1-review-2`. The packet-carrying commit may be a descendant of
that exact source head but must contain no later product-code change.

Read only:

- `AGENTS.md`;
- `orchestration/agent_inbox/codex/lc4v9d1-sol-contract.md`;
- `orchestration/agent_inbox/codex/lc4v9d1-sol-recovery.md`;
- `orchestration/agent_inbox/codex/lc4v9d1-preservation-amendment.md`;
- `app/services/bernie/lc4v9d1_development_evidence.py`;
- `tests/fixtures/bernie_lc4v9d1_development/probes.json`;
- `tests/test_bernie_lc4v9d1_development.py`;
- `app/services/bernie/semantic_extraction.py`;
- `app/services/bernie/lc4v4d3_policy_resolution.py`; and
- the five named test modules in the commands below, only as needed to
  understand a failure.

All holdouts v1-v9 and their fixtures, framework/support/authoring modules,
manifests, seals, receipts, tests, markers, and per-case evidence are
forbidden. Do not list or search for them. Do not use broad repository search
or any historical Antigravity project.

Independently re-audit all 30 D1 utterance/Gold rows, exact six language
structures per action, full patient identity, oracle separation,
classification taxonomy, contained patient grammar changes, safety, hashes,
and zero variance. Confirm that source head `a58538e0` contains no product
change after recovered head `5b27db4f`; its later commits preserve the first
review and amend only the explicit historical-equality preservation contract.

Run serially with the integration virtual environment:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_lc4v9d1_development.py
```

Then run the amended broader preservation gate exactly:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_lc4v4d3_policy_resolution.py tests\test_bernie_lc4v2r2_safety_language.py tests\test_bernie_lc4v9d1_development.py tests\test_bernie_lc4v3_content_blind_framework.py tests\test_bernie_lc4v4d1_development_diagnostic.py -k "not test_d3_all_20_cases_pass and not test_committed_reports_match_recovered_source and not test_live_post_audit_invariants"
```

The three deselections are immutable historical report/live equality nodes;
do not rewrite, xfail, or update them. Treat any other failure as a veto.

Write and commit only
`orchestration/agent_inbox/antigravity/lc4v9d1-review-2.md`. Include the five
named Ariadne rehydration sources, exact reviewed source and carrier heads,
test counts, hashes, audit findings, and one final line exactly
`DECISION: pass` or `DECISION: revision_required`. Do not push or edit
implementation, contracts, fixtures, handover, or historical evidence.
