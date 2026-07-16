# LC4V8D1 DeepSeek Flash Runner Packet

## Workspace and source

- Worktree: `C:\Users\sarashera\EMR4-worktrees\lc4v8d1-dw1`
- Branch: `claude/lc4v8d1-projection-diagnostic`
- Source head: `7cc32932`
- Transport/model: Claude Code `--bare`, DeepSeek V4 Flash/high

## Role and authority

Implement one bounded ordinary-development diagnostic runner and its tests.
You do not own fixture/Gold authorship, taxonomy meaning, baseline acceptance,
adjudication, remediation, recovery, integration, baton movement, or protected
refs. Do not edit product parser/policy code. Do not use DeepSeek Pro.

## Owned files

Create/edit only:

- `app/services/bernie/lc4v8d1_development_evidence.py`
- `tests/test_bernie_lc4v8d1_development.py`
- `orchestration/agent_inbox/claude/lc4v8d1-deepseek-candidate.md`

Commit only those files to your task branch. Do not push protected refs.

## Exact readable files

- `AGENTS.md`
- `orchestration/agent_inbox/codex/lc4v8d1-sol-contract.md`
- `orchestration/agent_inbox/codex/lc4v8d1-preauthoring-protected-search-incident.md`
- `orchestration/agent_inbox/antigravity/lc4v8d1-prebaseline-review.md`
- `tests/fixtures/bernie_lc4v8d1_development/probes.json`
- `tests/test_bernie_lc4v8d1_authorship.py`
- `app/services/bernie/semantic_extraction.py`
- `app/services/bernie/language_normalization.py`
- `app/services/bernie/lc4v4d3_policy_resolution.py`
- `app/services/bernie/lc4v7d1_development_evidence.py`
- `tests/test_bernie_semantic_extraction.py`
- `tests/test_bernie_lc4v4d3_policy_resolution.py`
- `tests/test_bernie_lc4v7d1_development.py`
- this packet

Every protected V8 implementation, evaluator, fixture, authoring module,
manifest, seal, marker, test, report internals, filename discovery, and per-case
surface is forbidden. Do not run broad file listing/search. Holdouts v1-v8
remain sealed. The metadata incident grants no access or reuse authority.

## Required runner behavior

1. Load and fail-closed validate the exact 24-case fixture, four 6-case family
   counts, unique IDs, exact key sets/types, raw hash
   `sha256:ebcfe4bbbd9c89dff00f1ff30643f2b9dc21f5cfba5febf62fd22e041f76269c`,
   and the same semantic/projection cross-field invariants enforced by the
   authorship test. Validation failure must execute no product code and return
   24 `authoring_invalid` with zero observations.
2. For each valid case call ordinary non-intercepted `extract_semantics` then
   explicit Option A `resolve_policy`, passing utterances, every relevant
   extraction field, synthetic diary state/appointments, and reference date.
   Never pass `expected`, family, language form, or probe ID downstream.
3. Project the typed `PolicyResolution` to exactly the 14 JSON-safe fields in
   the contract. Preserve ordered tuples as arrays and explicit nulls. Do not
   branch on probe identity or expected values.
4. Independently derive observed semantic policy invariants from the runtime
   result: `propose_mutation`, `proceed_read`, `clarify`, `refuse`, or
   `no_action`, plus mutation allowance and safety. Do not derive them by
   comparing to Gold.
5. Score normalization fragment/canonical/span, extraction action and temporal
   relation/bounds, semantic policy behavior, and exact projection separately.
6. Apply the frozen classification precedence exactly:
   `authoring_invalid`, `normalization_gap`, `parser_gap`,
   `policy_behavior_gap`, `policy_projection_gap`, `pass`.
7. Execute every case twice. Expose inspectable per-case observations and
   mismatch tuples, exact family/classification/aggregate counts, repeat
   variance, raw fixture hash, canonical non-pass selection hash, and complete
   report hash. Hash the complete report only after final selection insertion.
8. Tests must mutate every structural/cross-field gate, prove no execution on
   invalid input, prove no expected/probe-ID dependency in observation and
   projection functions, prove hash determinism and complete-report binding,
   and assert accounting/safety without assuming the baseline passes.

## Tests

Run serially:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_lc4v8d1_authorship.py tests/test_bernie_lc4v8d1_development.py tests/test_bernie_semantic_extraction.py tests/test_bernie_lc4v4d3_policy_resolution.py --deselect tests/test_bernie_lc4v4d3_policy_resolution.py::TestEvidenceReport::test_d3_all_20_cases_pass --deselect tests/test_bernie_lc4v4d3_policy_resolution.py::TestEvidenceReport::test_committed_reports_match_recovered_source -q
git diff --check
```

## Durable closeout and decision

In `lc4v8d1-deepseek-candidate.md`, record source/branch/commit, exact files,
tests, fixture/report/selection hashes, aggregate and family classifications,
every non-pass probe/mismatch, scope audit, and token/cache/cost data available
from the transport. End with exactly one:

- `DECISION: candidate_ready_for_sol_review`; or
- `DECISION: blocked` with the concrete blocker.

Your self-assessment is candidate evidence only and cannot accept the baseline.
