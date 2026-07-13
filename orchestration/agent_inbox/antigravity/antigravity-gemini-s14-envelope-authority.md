# Gemini S14 - Envelope Authority Cross-Contract Hardening

You are the sole S14 implementation and adversarial worker. Work only in the
assigned disposable worktree. Commit a focused candidate locally, write the
required durable completion artifact, and do not push, merge, integrate,
advance protected refs, or create worktrees.

## Scope

Independently review the integrated S13 policy seam across the capability
registry, Diary action grammar, and all envelope types. Implement only bounded
pure-domain hardening supported by that review:

1. Ensure direct registered names and grammar aliases use the same registered
   author/tier source of truth.
2. Enforce registered-action author policy for `DiaryActionIntent`; retain its
   generic intent semantics and do not add an intent-tier restriction.
3. Add adversarial/cross-contract tests for direct registered names, aliases,
   unauthorized authors, compatible unknown names, and planned grammar verbs
   with no registered capability.
4. Keep enforcement construction-time only. Do not claim or add router/RBAC,
   command, confirmation, provider, database, or write enforcement.

## Closed Boundaries

Do not edit API routes, REST/OpenAPI or GraphQL artifacts, database schemas or
migrations, provider code, UI/client code, deployment/release configuration,
confirmation actions/routes, terminal-to-active policy, H15/H-series,
historical-trove material, memory/RAG/GraphRAG, or API-Spine command semantics.
Do not add a new endpoint, write path, audit write, provider/network call, or
database access.

## Verification

Run the focused policy/envelope/grammar/manifest tests and the relevant route-
contract, workflow-chain, and API-Spine artifact tests using:

```text
C:\\Users\\sarashera\\emr4\\.venv\\Scripts\\python.exe -m pytest tests/test_envelope_capability_policy.py tests/test_diary_action_envelopes.py tests/test_diary_action_boundary_contracts.py tests/test_bernie_diary_capability_manifest.py tests/test_diary_action_grammar.py tests/test_diary_action_route_contract.py tests/test_diary_action_route_endpoint_coverage.py tests/test_bernie_workflow_chain.py tests/test_api_spine_artifacts.py -q
```

Write `orchestration/agent_inbox/antigravity/s14-envelope-authority-completion.md`
with the candidate commit, changed files, tests, closed-boundary result, and
one final non-empty line:

```text
DECISION: pass
```

Do not write that final marker anywhere else in the artifact.
