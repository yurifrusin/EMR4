# S7 Lane 1: Acceptance Gate Required Revision 2

Role: implementation owner, same lane
Resource: `deepseek-flash-workers`
Model: `deepseek-v4-flash`
Reasoning: high
Revision artifact: `orchestration/agent_inbox/codex/review-deepseek-s7-contract-audit-v2-repair-revision-2.md`

Sol independently reproduced 75/75 focused tests passing. The gate remains
`REVISION_REQUIRED` because those tests still miss four executable-contract
requirements. Revise the same candidate; do not commit, push, or change scope.

## Required Corrections

1. Marker parsing must actually match `runner.mjs::validArtifact()`. The current
   whole-line regex accepts a one-cell row (`| DECISION: pass |`) but rejects a
   normal multi-column row such as `| Verdict | **DECISION: pass** | Notes |`.
   Iterate each line, split on `|` when present, trim each cell, strip surrounding
   `*`, backticks, and underscores, then apply the exact case-insensitive
   decision/completion regex. Add multi-column positive tests for both kinds and
   wrong-kind negatives.

2. The JSON contract still omits declared `artifact` and `artifact_kind`, which
   the prior packet explicitly required. Add stable relative artifact and kind
   fields to `ReviewAcceptance`/JSON and assert exact values in API and CLI
   tests. Do not add `artifact_path` to receipt expectations.

3. Restore `orchestration_harness/__init__.py` byte-for-byte to HEAD. It still
   has an out-of-scope line-wrap diff despite the artifact claiming it was
   reverted. Final `git diff --name-only` must not include this file.

4. Type aliases are not runtime validation. A direct API caller can currently
   pass an invalid `review_mode`. Reject review modes other than
   `executable|static_evidence` deterministically. Also reject a receipt JSON
   value that is not an object instead of raising an uncaught `.get` error. Add
   API and CLI-facing tests.

5. Keep both Pro fallback quirks. Preserve relative path/worktree containment,
   direct CLI bootstrap, strict collection parsing, branch/ancestry checks, and
   all 75 existing focused cases.

Do not rely on the adjacent PTY/mailbox run for this revision: its database
fixture is contaminated by the earlier parallel enum-create race, and the prior
artifact's reported failure count is not authoritative. Sol will validate those
unchanged suites later from a clean integration sequence.

## Verification

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_review_acceptance.py -q --tb=short
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/ariadne_review_acceptance.py --help
git diff --check
git diff --name-only
```

Report exact collection/execution counts. End with `STATUS: complete` only if
the focused suite and direct CLI pass and `__init__.py` is absent from the diff;
otherwise use `STATUS: revision_required`.
