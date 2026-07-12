# S7 Lane 1: Acceptance Gate Required Revision

Role: implementation owner, same lane
Resource: `deepseek-flash-workers`
Model: `deepseek-v4-flash`
Reasoning: high
Prior artifact: `orchestration/agent_inbox/codex/review-deepseek-s7-contract-audit-v2-repair.md`
Revision artifact: `orchestration/agent_inbox/codex/review-deepseek-s7-contract-audit-v2-repair-revision.md`

Sol independently ran the focused suite: 61 passed. The candidate remains
`REVISION_REQUIRED` because static/runtime review found acceptance gaps not
covered by those tests. Revise the existing candidate in the same worktree. Do
not commit, push, broaden scope, or change EMR4 runtime code.

## Required Corrections

1. `worker_pool.yaml` replaced `no_integration_authority` with
   `permission_prompts_are_not_authority`. The packet required adding the new
   quirk while preserving all integration-authority denials. Keep **both** and
   update the Pro fallback contract test accordingly. Do not assert that
   `no_integration_authority` is absent.

2. Revert the out-of-scope `orchestration_harness/__init__.py` edit. The module
   and CLI can import `orchestration_harness.review_acceptance` directly.

3. Relative `--artifact`, `--receipt`, and `--pytest-collect-output` paths must
   resolve relative to the declared review worktree, not the caller's process
   cwd. Require all three resolved files to remain inside that worktree. Add
   tests invoking the public API and CLI from a different cwd with worktree-
   relative paths.

4. Match `runner.mjs::validArtifact()` semantics exactly: split lines into
   Markdown table cells on `|`, trim, strip surrounding `*`, backticks, and
   underscores, then apply case-insensitive canonical regex. Add decision and
   completion table-cell/bold/backtick tests plus wrong-kind negatives.

5. The required JSON contract needs `schema_version:
   ariadne.review_acceptance.v1`, `status: accepted|rejected`, declared
   `artifact`, `artifact_kind`, and the existing observed fields. Keep the bool
   if useful, but do not emit only `accepted: true|false`.

6. Direct invocation currently fails:
   `python scripts/ariadne_review_acceptance.py --help` raises
   `ModuleNotFoundError: orchestration_harness`. Bootstrap the repository root
   on `sys.path` using the established script pattern, then test direct script
   invocation without `PYTHONPATH`.

7. Remove the ineffective `isinstance(Path, str)` command-string check. The CLI
   must simply treat `--pytest-collect-output` as a path and never execute it.
   Paths containing spaces are valid. Test a collection file with spaces.

8. Tighten the path-count form to pytest file output (for example a `.py: N`
   line) rather than accepting any arbitrary colon-number line. Preserve the
   singular/plural `N test(s) collected` forms and conflicting-count rejection.

9. Report the actual focused count in the revised artifact. Do not state
   `47 tests` if collection/execution is 61 across the two files.

The earlier adjacent PTY/mailbox batch error was a PostgreSQL enum-create race
caused by Sol launching database-backed test modules in parallel. It is not a
candidate failure. Run adjacent modules sequentially, not concurrently.

## Verification

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_review_acceptance.py -q --tb=short
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/ariadne_review_acceptance.py --help
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_ariadne_deepcode_pty.py tests/test_ariadne_deepcode_mailbox_settings.py -q --tb=short
git diff --check
git diff --stat
```

If a command is permission-blocked, do not request interactive approval or
claim it passed. End the revision artifact with `STATUS: complete` only after
the focused suite and direct CLI pass; otherwise use
`STATUS: revision_required`.
