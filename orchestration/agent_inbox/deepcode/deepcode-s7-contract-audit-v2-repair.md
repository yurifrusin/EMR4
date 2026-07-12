# S7 Lane 1: Executable Review-Acceptance Contract

Role: implementation owner
Resource: `deepseek-flash-workers`
Model: `deepseek-v4-flash`
Reasoning: high
Conductor plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s7-contract-audit-v2.md`
Completion artifact: `orchestration/agent_inbox/codex/review-deepseek-s7-contract-audit-v2-repair.md`

Work only in this disposable worktree. Do not commit, push, merge, rebase, or
modify master. Do not edit EMR4 runtime code. Writable implementation surface:

- `orchestration/harness_settings/worker_pool.yaml`
- `orchestration_harness/review_acceptance.py`
- `scripts/ariadne_review_acceptance.py`
- `tests/test_ariadne_deepcode_adapter_settings.py`
- `tests/test_ariadne_review_acceptance.py`
- the completion artifact above

## 1. Reconcile Approved Pro Fallback

The observed baseline is six failures in
`tests/test_ariadne_deepcode_adapter_settings.py`, not seven. Update stale
two-resource/Flash-only assertions for the approved third resource
`deepseek-pro-conductor-fallback`. Only that conductor fallback may default to
`deepseek-v4-pro`; verifier and ordinary workers must remain Flash. Add
`permission_prompts_are_not_authority` to the Pro fallback's transport quirks.
Keep all integration-authority denials intact.

## 2. Implement Executable Acceptance Gate

Create a small standard-library-only module and thin CLI. The public validator
must take, at minimum:

- declared artifact path and kind (`decision|completion`);
- adapter receipt path;
- review worktree path;
- exact expected branch;
- candidate commit;
- a path containing captured `pytest --collect-only -q` output; and
- review mode (`executable|static_evidence`).

It must return/print deterministic JSON with `accepted|rejected`, reasons,
observed branch/HEAD, ancestry result, canonical marker/decision, receipt
cross-check, authoritative pytest count, optional worker-reported count and
mismatch flag, review mode, and `scratch_outputs_ignored: true`.

Fail closed unless all applicable checks pass:

1. Artifact and receipt exist as ordinary files inside the declared review
   worktree.
2. Receipt uses current fields and values: `status: completed`, exact relative
   `artifact`, matching `artifact_kind`, `artifact_observed: true`,
   `permission_prompt_observed: false`, and `process_cleanup_confirmed: true`.
   Do not introduce `artifact_path`.
3. Decision artifacts contain a canonical line
   `DECISION: pass|revision_required`; completion artifacts contain
   `STATUS: complete`. Match the adapter's line/cell semantics. Wrong-kind
   markers and `VERDICT` alone fail.
4. `git branch --show-current` equals the exact expected branch.
5. `git rev-parse HEAD` succeeds and
   `git merge-base --is-ancestor <candidate> HEAD` returns zero. Use subprocess
   argument arrays with `shell=False` and the declared worktree cwd.
6. Parse the supplied collection-output file, accepting current pytest forms
   such as `review/test_diary_smoke.py: 139`, `139 tests collected`, or
   `1 test collected`. Reject missing, zero, ambiguous, or conflicting counts.
   Collection evidence is authoritative. A worker `N passed` claim may be
   reported and mismatch-flagged but must never replace collection evidence.
7. Never search other files for a substitute artifact. A valid scratch file at
   another path cannot rescue an invalid/missing declared artifact.

The CLI must accept a collection-output **file path only** (for example
`--pytest-collect-output`). It must not accept or execute a command string.
Exit 0 for accepted, 1 for rejected, 2 for input/internal errors. JSON must not
include terminal output or file contents.

`static_evidence` is the permission-safe fallback used when DeepCode shell
execution is blocked: Sol runs deterministic commands and supplies the captured
collection file; the LLM performs static veto. It does not auto-answer prompts,
broaden permissions, or bypass artifact/receipt/worktree checks.

## 3. Focused Tests

Use temporary Git repositories/worktrees and synthetic artifacts/receipts.
Cover accepted decision/completion, revision-required decision, `VERDICT`-only,
wrong kind, receipt artifact/kind/status mismatch, permission prompt, cleanup
failure, wrong branch, non-ancestor candidate, outside-worktree paths, missing
artifact, scratch substitute, all supported collection formats, conflicting
counts, worker count mismatch, both review modes, CLI exit codes, and strict
permission settings unchanged.

Do not weaken/remove/skip/xfail existing tests. Do not edit `runner.mjs`.

## Verification

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_review_acceptance.py -q --tb=short
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_ariadne_deepcode_pty.py tests/test_ariadne_deepcode_mailbox_settings.py -q --tb=short
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/ariadne_review_acceptance.py --help
git diff --check
git diff --stat
```

Report exact results. If shell execution is permission-blocked, do not request
interactive approval and do not claim tests passed; finish
`STATUS: revision_required` with the blocked command. Otherwise end with exactly
one terminal marker:

```text
STATUS: complete
```
