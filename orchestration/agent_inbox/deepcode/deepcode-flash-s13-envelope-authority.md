# DeepSeek Flash S13 - Registered Envelope Authority

You are the sole S13 implementation worker. Work only in the assigned
disposable worktree and return a durable completion artifact. Do not push,
merge, alter protected refs, create worktrees, or claim integration authority.

## Scope

Implement the approved pure Diary-envelope hardening:

1. Add a small deterministic policy seam that looks up registered names in
   `BERNIE_CAPABILITY_REGISTRY` and validates author plus envelope compatibility.
2. Apply it to existing envelope validation without a top-level import cycle.
3. For a registered name, reject an unauthorized author. Reject a registered
   `proposal` when it is not a propose-tier capability, a registered
   `suggestion` when it is not read-only/meta compatible, and a registered
   `confirmation` when it is not a confirm-tier capability.
4. Keep unknown free-string `action_name` values accepted so generic envelope
   compatibility remains intact. Intent envelopes may retain their current
   generic semantics but must reject a registered action from an unauthorized
   author.
5. Update the source-derived manifest wording so it accurately describes
   registered-envelope enforcement without claiming router/RBAC/live-command
   enforcement.

## Closed Boundaries

Do not edit routers, REST/OpenAPI or GraphQL artifacts, schemas/models,
migrations, provider code, UI/client code, deployment/release configuration,
confirmation actions/routes, terminal-to-active policy, H15/H-series,
historical-trove material, memory/RAG/GraphRAG, or API-Spine command semantics.
Do not add a new write path, confirm action, endpoint, audit write, provider
call, database access, or network call.

## Required Tests

Add focused deterministic tests for permitted and rejected registered
author/tier combinations, unknown-name compatibility, source import purity,
and manifest posture. Run at least:

```text
C:\\Users\\sarashera\\emr4\\.venv\\Scripts\\python.exe -m pytest tests/test_diary_action_envelopes.py tests/test_diary_action_boundary_contracts.py tests/test_bernie_diary_capability_manifest.py tests/test_diary_action_grammar.py -q
```

Use the shared tools injected for this worker:

```text
PYTHON_EXE=C:\\Users\\sarashera\\emr4\\.venv\\Scripts\\python.exe
NODE_EXE=C:\\Program Files\\nodejs\\node.exe
```

Commit the candidate changes locally with a focused commit. Then write exactly
one final non-empty completion marker in
`orchestration/agent_inbox/deepcode/s13-envelope-authority-completion.md`:

```text
STATUS: complete
```

Before that final marker, state the candidate commit, changed files, tests run,
and the closed-boundary result. Do not include `STATUS: complete` anywhere else
in the artifact.
