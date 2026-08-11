# Independent veto packet — AES-C5 product-runtime admission

Review id: `raisa-aes-c5-gemini-36-high-veto-001`

Model: Gemini 3.6 Flash/high in one fresh Antigravity project

Exact source: `4e5d96ada19c51432fa4db46c76e23c952147c52`

Bound worktree: `C:\Users\sarashera\EMR4-worktrees\aes-c5-gemini-review`

Bound branch: `codex/aes-c5-gemini-review`

## Start and scope

Read `AGENTS.md` completely first. Verify the exact root, clean branch and HEAD.
This is a read-only veto. Do not edit, create, delete, stage, commit, switch,
merge, push or contact any provider, database, application route, credential,
cloud service or network destination.

Inspect only these exact files:

- `docs/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-plan.md`
- `docs/security/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-threat-model-delta.md`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/product-runtime-envelope.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/product-runtime-envelope.schema.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.schema.json`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission.py`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c5.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c5_plan.py`
- `app/dependencies.py`
- `app/routers/practice.py`
- `app/schemas/practice.py`
- `app/services/practice/practitioner_directory_read.py`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/local-fake-core-evidence.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/local-fake-lifecycle-evidence.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/local-fake-ledgers/source-ledger.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/local-fake-ledgers/provider-ledger.json`
- `orchestration/agent_inbox/codex/raisa-aes-c5-single-generation-destination-conflict-analysis.md`

Do not list or search repository roots, tests, orchestration, fixtures, support,
holdouts, reports, receipts or untracked paths. Do not inspect `docs/branding/`.
Do not open any file not named above except an exact direct import required to
understand a reviewed line; if that becomes necessary, stop with
`revision_required` and name the missing path without opening it.

## Required review

Decide whether this exact source is safe to proceed to a single authored-
synthetic occupied rehearsal. Veto on any material uncertainty. In particular:

1. prove that the source and provider operations use two separately immutable,
   single-grant, single-destination AES-C0 generations and that both complete
   packets pass `c1.validate_attempt` before evaluation;
2. prove there is no lease or AES-C0 budget transfer, the source generation is
   exhausted before the provider generation exists, and the later immutable
   system-contract digest binds the fresh ContextFrameSet digest;
3. verify the exact ordinary bearer-auth, active-user, token/practice equality,
   practice-scoped read and active-only/limit/offset route path;
4. verify nullable `roleLabel`, nullable or closed `{id,name}`
   `defaultLocation`, strict three-row/overflow behavior and minimization to
   only opaque practitioner ref, display name and optional role label;
5. verify the provider request excludes UUID, active, location, alias map,
   route, source digest and timing metadata; the response schema offers only
   grounded aliases; the deterministic proofreader requires the exact target,
   frame digest and `command_authority: false`;
6. verify local harness schema-name validation, no pre-existing-schema drop,
   setup/teardown outside both generations, SELECT/WITH-only measured route,
   count invariance, one route call and exact cleanup;
7. verify the occupied adapter can make no more than one Sydney Vertex call,
   has no retry/redirect/fallback/tool/command path and treats any provider
   failure as terminal;
8. verify the four evidence/ledger files contain no display name, UUID, JWT,
   database URL, raw prompt/response/provider text or schema name, and that
   their counts/decisions accurately support the local provider-free claim;
9. identify any code path, exception path, stale-clock issue, cleanup issue,
   evidence overclaim or test blind spot that could invalidate the one-call
   occupied gate.

## Allowed commands

Run only these commands from the bound worktree, substituting the exact root
interpreter because the review worktree has no `.venv`:

```powershell
git status --short --branch
git rev-parse HEAD
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_raisa_agent_execution_surface_containment_gate_aes_c5.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c5_plan.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission.py scripts\raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c5.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile scripts\raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission.py scripts\raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c5.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py
git diff --check
git status --short --branch
```

Do not run any acceptance/evidence generator or live/local harness.

Return `pass` only if there is no material finding. In `review`, report exact
HEAD, commands/results, reviewed files, findings with precise file/line support,
and explicit provider calls/product reads/database operations performed by the
review (all must be zero). Return `revision_required` for any material defect,
scope gap, command deviation or uncertainty. The wrapper will enforce the
schema-constrained decision object.
