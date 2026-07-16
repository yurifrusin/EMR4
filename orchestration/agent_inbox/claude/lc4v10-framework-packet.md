# LC4V10 Content-Blind Framework Candidate

## Identity and source

- Worker: DeepSeek V4 Flash/high through Claude Code `--bare`.
- Worktree: `C:\Users\sarashera\EMR4-worktrees\lc4v10-dw1`.
- Branch: `claude/lc4v10-content-blind-framework`.
- Source head: supplied by the bound worktree; verify it before work.
- Decision format: final line exactly `DECISION: candidate_ready` or
  `DECISION: blocked`.

Read only `AGENTS.md`, the V10 Sol contract, the V10 one-shot acceptance rule,
`app/services/bernie/certification_decision_taxonomy.py`, ordinary public
semantic/policy/interpretation/replay interface definitions needed for type
shape, and the D1 acceptance/closeout. Do not read D1 fixture content.

All holdouts v1-v9 and all their filenames, fixtures, frameworks, evaluators,
authoring/support modules, manifests, seals, markers, thresholds, reports,
receipts, tests, and per-case evidence are forbidden. Do not list, glob, grep,
search, import, compare, or inspect them. Do not use repository-wide search.

## Owned files

Create or edit only:

- `app/services/bernie/lc4v10_content_blind_framework.py`;
- `tests/test_bernie_lc4v10_content_blind_framework.py`; and
- `orchestration/agent_inbox/claude/lc4v10-deepseek-framework-candidate.md`.

Do not edit contracts, handover, parser/policy/runtime code, existing tests, or
any other file. Do not create actual corpus content or any fixture, authoring
module, evaluator sidecar, manifest, seal, marker, threshold file, or report.

## Task

Implement a genuinely fresh generic framework from the V10 contract and rule.
Use only opaque in-memory placeholder objects and temporary paths in tests.
Enforce exact fixed shape, exact schemas, 14-field projection/cross-field Gold
validation, observation-oracle separation, evidence/product taxonomy, source
and Git binding, exclusive marker ordering, exception consumption,
aggregate-only reporting, deterministic hashing, threshold gates, and zero
repeat variance.

Tests must fail the framework for missing/unknown fields, duplicate identities,
wrong populations/slices/turn counts, contradictory Gold, projection drift,
oracle leakage, wrong decision precedence, invalid source/blobs, stale or
consumed seals, marker collisions, protected reads before marker, exception
rollback, case-level aggregate leakage, missing dimensions, and variance.
Tests must also prove a fully valid opaque pass path and a valid-evidence
product-fail path.

The framework must import the generic certification classifier rather than
reimplementing it. It must not import or branch on any earlier holdout, future
scenario ID, group, language form, utterance, or expected value.

Run serially:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_lc4v10_content_blind_framework.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_certification_decision_taxonomy.py tests\test_bernie_lc4v9d1_development.py
git diff --check
```

The second command uses named ordinary preservation surfaces only; do not open
or infer any protected corpus. Record exact changed files, test counts, commit,
limitations, and why no actual V10 content exists. Commit only the three owned
files on the disposable branch. Do not push.
