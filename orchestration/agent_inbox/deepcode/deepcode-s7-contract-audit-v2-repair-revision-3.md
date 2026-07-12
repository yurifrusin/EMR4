# S7 Lane 1: Acceptance Gate Required Revision 3

Role: implementation owner, same lane
Resource: `deepseek-flash-workers`
Model: `deepseek-v4-flash`
Reasoning: high
Revision artifact: `orchestration/agent_inbox/codex/review-deepseek-s7-contract-audit-v2-repair-revision-3.md`

The first real gate invocation correctly verified artifact, receipt, marker,
branch, HEAD, and candidate ancestry, but rejected authoritative collection
evidence containing two normal pytest per-file lines:

```text
tests/test_ariadne_deepcode_adapter_settings.py: 30
tests/test_ariadne_review_acceptance.py: 52
```

It treated `{30, 52}` as conflicting instead of aggregating to 82. This is a
candidate defect. Revise the same lane without changing other contracts.

## Required Aggregation Contract

Parse collection evidence as two distinct forms:

1. Per-file `.py: N` lines: normalize by file path, reject conflicting duplicate
   counts for the same path, and sum unique file counts.
2. Summary `N test(s) collected` lines: all summary counts must agree.

If both forms are present, the summary count must equal the per-file sum. If
only one form is present, use it. Reject zero, missing, conflicting duplicate,
or summary-versus-sum mismatch. Preserve arbitrary-colon rejection.

Add tests for:

- two files `30 + 52 -> 82` accepted;
- one file `139 -> 139` accepted;
- two files plus matching `82 tests collected` accepted;
- two files plus mismatching summary rejected;
- duplicate same path/same count not double-counted;
- duplicate same path/different count rejected.

Add a focused CLI/API test matching the real S7 invocation. Preserve all 82
existing tests and every other gate behavior. Do not edit settings or unrelated
files again.

Run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_review_acceptance.py --collect-only -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_review_acceptance.py -q --tb=short
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/ariadne_review_acceptance.py --help
git diff --check
git diff --name-only
```

Report exact per-file and total counts. End with `STATUS: complete` only when
the multi-file aggregation case passes; otherwise use
`STATUS: revision_required`.
