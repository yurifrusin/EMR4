# S14 Protected-Master Integration Manifest

Status: authorization requested. This document does not authorize a merge,
push, protected-ref update, or S15.

## Exact Authorization Request

| Field | Value |
| --- | --- |
| Source branch | `codex/terra-validation-2` |
| Accepted pre-manifest source head | `caa71944c92c437ec006c96b1e6fdf4bd4ee120d` |
| Required protected base | `master` and `handoff/current` at `b52914566665f9be55fe4bba96be48b5e1bb16be` |
| Method if later authorized | Conflict-free merge of the final source branch after all preconditions below pass |
| Scope | S14 envelope cross-contract hardening, Gemini artifact, Terra acceptance evidence, handover update, and this manifest only |

The final authorized source head is the commit adding this manifest, with no
additional file or commit beyond the ordered S14 patch set. A changed protected
base, source head, diff scope, test result, conflict, or security/authority
implication is a manifest variance and must stop integration.

## Ordered S14 Patch Set

1. `0dbfed54` `docs(ariadne): plan S14 envelope authority hardening`
2. `20b3f1ee` `Add completion report for Gemini S14`
3. `24cbf5a7` `Hardening registered-envelope authority policy seam for Gemini S14`
4. `caa71944` `fix(diary): keep confirm aliases staff-only`
5. This manifest closeout commit.

The Gemini artifact records candidate `3dc11eb9`; it is preserved unchanged.
Terra's acceptance correction in `caa71944` is authoritative for the final
source: registered confirm-tier aliases cannot inherit Bernie authorship from
their adjacent proposal capability.

## Expected Diff Scope

- `AGENTS.md`
- `app/services/diary/envelope_capability_policy.py`
- `app/services/diary/envelopes.py`
- `docs/ariadne-s13-s15-registered-envelope-authority-tranche.md`
- `orchestration/agent_inbox/antigravity/antigravity-gemini-s14-envelope-authority.md`
- `orchestration/agent_inbox/antigravity/s14-envelope-authority-completion.md`
- `orchestration/agent_inbox/codex/plan-terra-s14-envelope-authority-cross-contract.md`
- `orchestration/agent_inbox/codex/s14-dispatch-record.md`
- `orchestration/agent_inbox/codex/review-terra-s14-envelope-authority.md`
- this manifest
- `tests/test_envelope_capability_policy.py`

No router, REST/OpenAPI command, GraphQL schema/resolver, provider, database
model/migration, deployment/release configuration, external client, H15/H-series,
historical-trove, memory/RAG/GraphRAG, confirmation action/route, terminal-to-
active policy, or new write authority is in scope.

## Required Acceptance Evidence

```text
C:\\Users\\sarashera\\emr4\\.venv\\Scripts\\python.exe -m pytest tests/test_envelope_capability_policy.py tests/test_diary_action_envelopes.py tests/test_diary_action_boundary_contracts.py tests/test_bernie_diary_capability_manifest.py tests/test_diary_action_grammar.py tests/test_diary_action_route_contract.py tests/test_diary_action_route_endpoint_coverage.py tests/test_bernie_workflow_chain.py tests/test_api_spine_artifacts.py -q
C:\\Users\\sarashera\\emr4\\.venv\\Scripts\\python.exe -m py_compile app/services/diary/envelope_capability_policy.py app/services/diary/envelopes.py
git diff --check b5291456...<final-source-head>
```

Recorded result: 31 policy tests plus 195 focused envelope/Diary/workflow/API-
Spine tests passed. The completed Gemini lane ran in the disposable S14
worktree with local captured output and a durable artifact; no S14 process or
owner record remained at acceptance.

## S14 Process Metrics

No Sol intervention, Conductor, verifier, invalid integration, manifest
variance, or duplicated-context event occurred. One no-work CLI argument-order
attempt and one local prompt probe preceded the completed Gemini lane; they
changed no worktree file and created no artifact. Terra corrected that transport
invocation, then corrected one confirmation-author regression and whitespace
defect during acceptance. The completed lane duration is advisory only: about
233 seconds from durable local timestamps.
