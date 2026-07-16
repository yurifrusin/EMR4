# LC4V8 Gemini Pre-Content Framework Veto

Status: `assigned`

Reviewer: Gemini 3.5 Flash/medium through a fresh Antigravity project

Worktree: `C:\Users\sarashera\EMR4-worktrees\lc4v8-gemini-framework-review`

Branch: `antigravity/lc4v8-framework-review`

Source head: set to the exact `handoff/current` containing this packet. Record
the full hash in the durable review.

## Decision surface

Independently decide whether the content-blind LC4V8 framework is fail-closed
and safe to freeze before any V8 corpus content exists. Do not inherit a prior
worker's acceptance framing. Review the implementation itself against the two
frozen Sol documents.

Named readable files only:

- `AGENTS.md`;
- `orchestration/agent_inbox/codex/lc4v8-sol-contract.md`;
- `orchestration/agent_inbox/codex/lc4v8-one-shot-acceptance-rule.md`;
- `app/services/bernie/certification_decision_taxonomy.py`;
- `tests/test_bernie_certification_decision_taxonomy.py`;
- `app/services/bernie/lc4v8_content_blind_framework.py`;
- `tests/test_bernie_lc4v8_content_blind_framework.py`; and
- this packet.

Do not list, search, open, import, hash, or infer any protected v1-v7 fixture,
support/authoring module, manifest, seal, receipt, test, filename, or per-case
evidence. Do not inspect the rejected worker closeout or Sol recovery framing.
No actual V8 fixture, authoring surface, manifest, seal, or report exists and
none may be created during this review.

## Required audit

Check, at minimum:

1. exact nested schemas, fixed shape, and unknown-field rejection;
2. direct source ancestry/blob binding rather than trusted caller assertions;
3. manifest, thresholds, seal, attempt ID, and exclusive marker binding;
4. irreversible consumption on every post-marker pass, fail, invalid, missing-
   dimension, exception, and report-write path;
5. that the evaluator callback receives no Gold value or case/group/form ID;
6. raw-output two-repeat variance and all thirteen dimensions;
7. aggregate-only report completeness, absence of case/oracle content, and a
   final hash binding evidence, product gates, public group/form failures, and
   decision;
8. evidence-invalid versus product-fail taxonomy, especially policy and
   integration failures; and
9. runtime isolation and absence of real corpus or prior holdout imports.

Run serially:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_lc4v8_content_blind_framework.py tests/test_bernie_certification_decision_taxonomy.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_interpretation_runtime_isolation.py --deselect tests/test_bernie_interpretation_runtime_isolation.py::test_runtime_app_code_does_not_import_interpretation_harness_tooling -q
git diff --check
```

The exact deselected node is the documented pre-existing baseline in
`AGENTS.md`; do not reinterpret or edit it.

## Write authority and decision

Create only:

`orchestration/agent_inbox/antigravity/lc4v8-gemini-framework-review.md`

Do not edit code/tests, create content, commit, move refs, or push. End with one
of:

- `DECISION: pass`
- `DECISION: fail`

For `fail`, name each concrete fail-open path with file and line evidence.
