# S13 Protected-Master Integration Manifest

Status: authorization requested. This document does not authorize a merge,
push, protected-ref update, S14, or S15.

## Exact Authorization Request

| Field | Value |
| --- | --- |
| Source branch | `codex/terra-validation-2` |
| Accepted pre-manifest source head | `06a6fc53a8aa762ad439b76109fc4db6840eb622` |
| Required protected base | `master` and `handoff/current` at `72b0999ae21fe48da090ededb98a87048a0aa1ea` |
| Method if later authorized | Conflict-free merge of the final source branch after all preconditions below pass |
| Scope | S13 registered-envelope authority hardening, accepted worker evidence, recovery evidence, and this manifest only |

The final authorized source head is the commit adding this manifest, with no
additional file or commit beyond the ordered S13 patch set below. A changed
protected base, source head, diff scope, test result, conflict, or security/
authority implication is a manifest variance and must stop integration.

## Ordered S13 Patch Set

1. `4ac8abe7` `docs(ariadne): plan S13 envelope authority hardening`
2. `2fb0d661` `docs(ariadne): record S13 worker lifecycle recovery`
3. `ebaf4349` `wip(ariadne): preserve stalled S13 worker candidate`
4. `06a6fc53` `fix(diary): enforce registered envelope authority`
5. This manifest closeout commit, including the S13 handover update.

`ebaf4349` is preserved as the untrusted stalled-worker candidate. Terra's
accepted direct-registry correction is in `06a6fc53`; do not substitute the
candidate commit for the accepted source head.

## Expected Diff Scope

- `AGENTS.md`
- `app/services/diary/__init__.py`
- `app/services/diary/capability_manifest.py`
- `app/services/diary/envelope_capability_policy.py`
- `app/services/diary/envelopes.py`
- `tests/test_envelope_capability_policy.py`
- `docs/ariadne-s13-s15-registered-envelope-authority-tranche.md`
- `orchestration/agent_inbox/codex/plan-terra-s13-registered-envelope-authority.md`
- `orchestration/agent_inbox/codex/s13-dispatch-record.md`
- `orchestration/agent_inbox/codex/s13-w1-lifecycle-recovery.md`
- `orchestration/agent_inbox/codex/review-terra-s13-envelope-authority.md`
- `orchestration/agent_inbox/deepcode/deepcode-flash-s13-envelope-authority.md`
- `orchestration/agent_inbox/deepcode/s13-envelope-authority-completion.md`
- this manifest.

No router, REST/OpenAPI command, GraphQL schema/resolver, provider, database
model/migration, deployment/release configuration, external client, H15/H-series,
historical-trove, memory/RAG/GraphRAG, confirmation action/route, terminal-to-
active policy, or new write authority is in scope.

## Required Acceptance Evidence

```text
C:\\Users\\sarashera\\emr4\\.venv\\Scripts\\python.exe -m pytest tests/test_envelope_capability_policy.py -q
C:\\Users\\sarashera\\emr4\\.venv\\Scripts\\python.exe -m pytest tests/test_diary_action_envelopes.py tests/test_diary_action_boundary_contracts.py tests/test_bernie_diary_capability_manifest.py tests/test_diary_action_grammar.py tests/test_diary_action_route_contract.py tests/test_diary_action_route_endpoint_coverage.py tests/test_bernie_workflow_chain.py tests/test_api_spine_artifacts.py -q
C:\\Users\\sarashera\\emr4\\.venv\\Scripts\\python.exe -m py_compile app/services/diary/envelope_capability_policy.py app/services/diary/envelopes.py app/services/diary/capability_manifest.py
git diff --check 72b0999a...<final-source-head>
```

Recorded result: 22 policy tests plus 195 focused envelope/Diary/workflow/API-
Spine tests passed. The accepted worker receipt is local-only evidence with one
mailbox event, a canonical artifact marker, released owner lock, no permission
prompt, and `artifact_deadline_active: false`.

## S13 Process Metrics

One Sol intervention authorized progress-based recovery. One worker stall and
one same-lane retry occurred. Terra corrected the initial 1800-second deadline
to disabled (`--timeout 0`) and made one final direct-registry acceptance
correction. There were zero Conductor/verifier consultations, invalid
integrations, manifest variances, and duplicated-context events. The accepted
retry duration is advisory only: about 211 seconds from durable receipt
timestamps.
