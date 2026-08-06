# Independent veto packet: provider-free Practice Context Fabric and Bureau Memory Bank contract

Date: 2026-08-06

You are the independent Gemini 3.6 Flash/high veto reviewer. Review only the
exact committed candidate below. Do not edit any file and do not implement a
repair.

## Exact candidate

- Worktree: `C:\Users\sarashera\EMR4-worktrees\raisa-context-fabric-bureau-memory-review`
- Branch: `codex/review-context-fabric-bureau-memory-1289f9b8`
- Required HEAD: `1289f9b822c571341b224ab9c6b5caaeefaf0c71`
- Candidate branch is non-protected and must remain clean and unchanged.
- Accepted C5 ancestor and task-branch base:
  `8812d584721df3f96981e218e74433004f683bce`.

## Review objective

Determine whether the first provider-free authored-synthetic Context Fabric
and Bureau Memory Bank contract safely proves its narrow claim. Look for any
material defect that permits a candidate to supply authority, widens tenant,
role, purpose, source, field, time or result scope, exposes raw audit or command
material, treats memory as current truth, permits stale/superseded/tampered
release, fails to bind the selector and same packet, opens a runtime/API write
surface, or overstates provider/product behavior.

Inspect at least:

- `docs/raisa-provider-free-practice-context-fabric-bureau-memory-contract-plan.md`
- `docs/raisa-provider-free-practice-context-fabric-bureau-memory-contract-design.md`
- `docs/security/raisa-provider-free-practice-context-fabric-bureau-memory-contract-threat-model-delta.md`
- `docs/api-spine/graphql/practice-context-fabric-read.graphql`
- `orchestration/continuity/raisa-provider-free-practice-context-fabric-bureau-memory-contract/context-fabric-contract.schema.json`
- `orchestration/continuity/raisa-provider-free-practice-context-fabric-bureau-memory-contract/context-fabric-contract.example.json`
- `orchestration/continuity/raisa-provider-free-practice-context-fabric-bureau-memory-contract/provider-free-acceptance-evidence.json`
- `scripts/raisa_provider_free_practice_context_fabric_bureau_memory_contract.py`
- `scripts/raisa_provider_free_practice_context_fabric_bureau_memory_acceptance.py`
- `tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py`
- `tests/test_raisa_practice_context_fabric_direction.py`

Adversarially verify:

1. the candidate cannot supply principal, role, practice, location, consent,
   retention, command, write or raw-audit authority;
2. every candidate, binding, need, selector, grant, frame, frame set, selector
   trace, weave and proofreader object is closed and correctly digest-bound;
3. deterministic policy can only preserve or narrow Bureau, purpose, frame,
   source, requestable field, action, actor, outcome, time, freshness,
   cardinality and byte scope;
4. selection admits only exact allowed, current, half-open-window items in
   canonical order, removes disallowed optional opaque references and binds the
   selected ids and source references;
5. proofreading independently revalidates the exact sealed packet and blocks a
   resealed but out-of-scope item, expiry, supersession, wrong source, wrong
   authority or digest substitution;
6. memory remains a derived lossy `recent_collective_work` read projection,
   never raw audit, current truth, identity evidence, command authority or
   provider-model memory;
7. the GraphQL extension composes with the existing read schema, accepts only
   a non-authoritative candidate, and adds no resolver, route, standalone memory
   root, Mutation or Subscription;
8. the engine has no provider, network, database, subprocess, filesystem-write,
   product runtime or command surface; and
9. the evidence and documentation claim only provider-free authored-synthetic
   component behavior and do not set production retention or open any patient,
   clinical, product, deployment, release, Pages or protected-ref boundary.

Provider-free tests are permitted. Use the primary checkout's Python runtime
while keeping this review worktree as cwd:

`C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B -m pytest -q tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py tests/test_raisa_practice_context_fabric_direction.py tests/test_api_spine_artifacts.py tests/test_bernie_context_frames.py tests/test_ariadne_orchestrator_preflight.py tests/test_agents_acceptance_index.py tests/test_ariadne_agent_error_register.py`

Do not use or request cloud authentication; do not call any provider or external
retrieval; do not inspect protected holdouts, historical diary material,
patient/clinical/product data or `docs/branding/`; do not start a product
runtime, database or browser; do not write, commit, push, deploy, release,
rebuild Pages or move any Git ref.

## Decision contract

Report concise evidence and every material finding with file and line. If any
material uncertainty remains, require revision. Complete and synchronously wait
for every command, test and background notification before returning the final
object. Put the complete evidence and findings in the `review` string and set
`decision` exactly once to `pass` or `revision_required`. Return only the closed
schema-constrained object. Do not write a `DECISION:` marker, provisional verdict,
post-final status or background-completion follow-up inside `review`.
