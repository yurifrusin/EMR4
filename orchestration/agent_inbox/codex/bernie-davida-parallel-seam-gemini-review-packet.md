# Fresh Gemini review: Bernie/Davida parallel seam

Role: independent architecture and security verifier only

Model/effort: exact `gemini-3.6-flash-high` / explicit `high`

Candidate branch: `codex/review-bernie-davida-parallel-seam`

Candidate HEAD: `9b4d7dcce2d18182fb0b5f31f010496a1ef983dd`

Baseline HEAD: `f2cacad682fddd6c0db4cfeced77b23fc40d9990`

Settings fingerprint:
`sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`

## Authority and independence

Review only in the exact bound worktree. Do not edit, create, delete, stage,
commit, push, deploy or access another worktree. Do not inspect or reuse a prior
Antigravity project, prior model review or worker output. Do not access
protected refs/evidence/holdouts, historical Diary material, credentials,
patient/clinical/product-derived data or `docs/branding/`.

This candidate is an architecture-only shared seam. It grants no model runtime,
provider product path, database or product read, command/write, real identity,
cloud/IAM, deployment, production, release or protected-ref authority.

## Required source pass

Read `AGENTS.md` completely, then inspect only the candidate diff and these
named context files:

- `docs/bernie-davida-parallel-seam-plan.md`
- `docs/bernie-davida-shared-agent-boundary.md`
- `docs/security/bernie-davida-parallel-seam-threat-model-delta.md`
- `orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.json`
- `orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.schema.json`
- `tests/test_bernie_davida_parallel_seam.py`
- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/access_ai_api_design.md`
- `orchestration/bernie_release_gates.md`
- `docs/api-spine/manifests/agent-capability-charters.yaml`
- `docs/api-spine/manifests/practice-onboarding-example.yaml`
- `app/services/practice_knowledge/facts.py`
- `app/services/practice_knowledge/envelopes.py`
- `app/services/practice_knowledge/boundary.py`
- `app/services/application_auth_office_consumer.py`
- `docs/diary/diary.js`
- `orchestration/harness_settings/verifier_execution_policy.yaml`
- `orchestration/harness_settings/worker_pool.yaml`

Do not list or search protected directories. Review the exact diff from the
baseline to candidate HEAD.

## Adversarial focus

Attempt to falsify the seam's claims:

- Does “shared kernel” accidentally route the deterministic native Diary read
  through a probabilistic work cell or proofreader?
- Does the Diary lane mistakenly create a new directory API, reuse the Office
  terminal lifecycle, replace the existing bearer path when off or weaken the
  current GraphQL/REST fallback?
- Can Davida become the owner of database truth, promote advisory knowledge,
  reuse a `writes_authorized=true` envelope, emit an open-ended operation or
  bypass human-confirmed REST commands?
- Are container/service identities and agent-specific policies actually
  separate, or can the shared proofreader create a union capability?
- Can a model receive a DB session, credentials, generic API client or arbitrary
  GraphQL control?
- Are the three authority classes and event/fresh-read boundary mechanically
  preserved?
- Can two lanes edit a shared file, run shared PostgreSQL or Gemini concurrently,
  use unsafe staging or let a worker/reviewer accept/integrate?
- Does standing tranche authority silently open any provider, data, identity,
  write, deployment, protected-evidence or protected-ref gate?

## Deterministic reproduction

Run serially:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_davida_parallel_seam.py tests\test_ariadne_verifier_execution_policy.py tests\test_api_spine_artifacts.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check tests\test_bernie_davida_parallel_seam.py
git diff --check f2cacad682fddd6c0db4cfeced77b23fc40d9990..9b4d7dcce2d18182fb0b5f31f010496a1ef983dd
git status --short --branch
git rev-parse HEAD
```

You may run additional read-only static checks within the allowed files when
needed for a concrete finding. Do not run browser, provider, database-mutating
or broad repository discovery commands.

## Required response

List findings first with severity and precise file/line evidence. If none,
state that explicitly. Name checks actually run and confirm the exact HEAD and
clean unchanged worktree. End with exactly one terminal line:

`DECISION: pass`

or

`DECISION: revision_required`
