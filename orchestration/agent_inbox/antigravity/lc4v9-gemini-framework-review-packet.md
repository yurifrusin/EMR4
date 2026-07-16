# LC4V9 Gemini Fresh Pre-Content Framework Veto

Status: `dispatched`
Date: 2026-07-16
Reviewer: Gemini 3.5 Flash/medium through a fresh Antigravity project
Worktree: `C:\Users\sarashera\EMR4-worktrees\lc4v9-gemini1`
Branch: `gemini/lc4v9-framework-veto`
Exact review head: `4c9283b0a00fcb5a2e3fa44216599fc7efad2abe`

## Decision task

Perform an independent, content-blind veto review of the recovered LC4V9 empty
certification framework. No actual V9 corpus, evaluator, authoring module,
threshold file, manifest, seal, marker, or report exists. Do not create any of
them and do not infer content. Decide whether this exact framework head may
proceed to Sol-only protected authorship.

Read only these named files:

- `AGENTS.md`;
- `orchestration/agent_inbox/codex/lc4v9-sol-contract.md`;
- `orchestration/agent_inbox/codex/lc4v9-one-shot-acceptance-rule.md`;
- `orchestration/agent_inbox/codex/lc4v9-sol-framework-recovery.md`;
- `app/services/bernie/certification_decision_taxonomy.py`;
- `app/services/bernie/lc4v9_content_blind_framework.py`; and
- `tests/test_bernie_lc4v9_content_blind_framework.py`.

Do not use broad search, recursive listing, repository-wide grep, filename
discovery, or any earlier LC4V path. Holdouts v1-v8 and all their fixtures,
evaluators, authoring/support modules, manifests, seals, receipts, markers,
tests, and per-case evidence are forbidden.

## Required independent checks

Audit the exact source rather than trusting the recovery prose. Confirm or veto:

1. the attempt marker is created exclusively, durably, and already consumed
   before any protected input is read, with collision and creation failures
   distinguished and no cleanup/reuse path;
2. fixture, framework, evaluator, threshold, manifest, seal, marker, and report
   paths cannot escape the repository and runtime output paths are sealed;
3. the framework parses and hashes the same bytes it binds, uses real Git
   ancestry/blob checks, and binds both loaded framework and evaluator source
   through `inspect.getsourcefile`;
4. schemas reject missing/unknown fields and frozen threshold values cannot be
   weakened;
5. coverage-cell identity is explicit, all 288 scenarios and both repeats are
   exact, `complete` is the fourteen-way conjunction, and variance is zero;
6. semantic policy behaviour, canonical 14-field projection, clarification,
   policy/integration counters, and cross-field Gold validity are not conflated;
7. evidence invalidity has precedence, valid product misses return
   `certification_fail`, and semantic misses do not automatically become policy
   failures;
8. aggregate reports contain no case/oracle content, are written only to the
   sealed path, and return the hash of exact persisted canonical bytes; and
9. the focused tests exercise adversarial failures rather than merely echoing
   the implementation.

Run serially:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_lc4v9_content_blind_framework.py tests\test_bernie_certification_decision_taxonomy.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_interpretation_runtime_isolation.py --deselect tests/test_bernie_interpretation_runtime_isolation.py::test_runtime_app_code_does_not_import_interpretation_harness_tooling
```

## Write authority

Write only
`orchestration/agent_inbox/antigravity/lc4v9-gemini-framework-review.md`.
Do not edit implementation, tests, contract, acceptance, handover, or any other
file. Commit the review receipt only on the disposable review branch. Do not
push or move protected refs.

The review receipt must record the exact head, commands and counts, findings by
severity, confirmation that no forbidden path/content was accessed, and one
final line exactly:

- `DECISION: pass`; or
- `DECISION: revision_required`.

Any fail-open evidence-integrity defect requires `revision_required`. Style or
non-blocking hardening suggestions may coexist with `pass`. Gemini does not
accept the sprint, create content, move the baton, or grant write authority.

