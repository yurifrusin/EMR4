# S7 Lane 2: Independent Acceptance-Gate Review And Veto

Role: independent code/security/test reviewer
Resource: `deepseek-flash-workers`
Model: `deepseek-v4-flash`
Reasoning: high
Candidate commit: `7207c12978f20ccccac1997d342babe787f62fb5`
Conductor plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s7-contract-audit-v2.md`
Decision artifact: `orchestration/agent_inbox/codex/review-deepseek-s7-contract-audit-v2-review.md`

This disposable review worktree is branched directly from the candidate commit,
then receives this packet as a docs-only descendant. You have independent veto
authority and no implementation ownership. Do not edit implementation/tests/
settings, commit, push, merge, or rebase. Write only the decision artifact.

Review the candidate diff against its parent and the Lane 1 artifacts. Verify:

1. only `deepseek-pro-conductor-fallback` may default to Pro; Flash verifier and
   workers remain Flash and all integration-authority/permission quirks remain;
2. marker parsing matches `runner.mjs::validArtifact()` including multi-column
   Markdown cells and formatting normalization;
3. receipt cross-check uses `artifact`, exact kind/status/observed/permission/
   cleanup fields, and rejects `artifact_path`;
4. artifact, receipt, and collection paths are worktree-contained and relative
   paths resolve against the declared worktree;
5. exact branch and candidate ancestry are executable checks;
6. collection output, not worker prose, is authoritative and conflicting or
   arbitrary counts fail closed;
7. JSON/CLI contracts include schema/status/artifact/kind, direct invocation
   works, no command string is executed, and invalid modes/non-object receipts
   fail closed;
8. strict permissions are not broadened, prompts are not auto-answered, scratch
   files are never substitute artifacts, and no EMR4 runtime gate is opened;
9. no skip/xfail/assertion weakening or out-of-scope package/runtime edit exists.

If shell commands remain inside the authorized envelope, run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_review_acceptance.py -q --tb=short
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/ariadne_review_acceptance.py --help
git diff --check 7207c129^...7207c129
```

If DeepCode requests permission, do not answer it. The adapter will stop and Sol
will use the approved static-evidence path. Never claim a blocked command passed.

List findings first and exact evidence. End with literal unfenced lines:

```text
VERDICT: PASS
STATUS: complete
DECISION: pass
```

or

```text
VERDICT: REVISION_REQUIRED
STATUS: complete
DECISION: revision_required
```
