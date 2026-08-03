# Fresh Gemini review: Davida practice-administration architecture

Role: independent architecture, API Spine and security veto reviewer only

Model/effort: exact `gemini-3.6-flash-high` / explicit `high`

Worktree:
`C:\Users\sarashera\EMR4-worktrees\davida-practice-administration-gemini-review`

Candidate branch: `codex/review-davida-practice-administration-architecture`

Candidate HEAD: `19444399778dbd07b62223ca9b8a118a03d92d5b`

Baseline HEAD: `bb8a6f554b417df019727345ba91a7d555b0bd41`

Settings fingerprint:
`sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`

## Authority and independence

Review only in the exact bound worktree and a genuinely fresh Antigravity
project. Do not edit, create, delete, stage, commit, push, deploy or access
another worktree. Do not inspect or reuse prior model reviews or worker output.
Do not access protected evidence/holdouts, historical Diary material,
credentials, patient/clinical/product-derived data or `docs/branding/`.

This is architecture-only, provider-free and non-executing. It grants no
product/database read, provider, probabilistic runtime, command/write, real
identity, cloud/IAM, deployment, production, release or protected-ref authority.

## Required source pass

Read `AGENTS.md` completely, then inspect only the exact candidate diff and:

- the six files added by the candidate;
- `docs/bernie-davida-parallel-seam-plan.md`;
- `docs/bernie-davida-shared-agent-boundary.md`;
- `docs/security/bernie-davida-parallel-seam-threat-model-delta.md`;
- `orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.json`;
- `orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.schema.json`;
- `tests/test_bernie_davida_parallel_seam.py`;
- `orchestration/api_spine_adr.md`;
- `orchestration/api_spine_programme.md`;
- `orchestration/access_ai_api_design.md`;
- `docs/api-spine/graphql/appointment-diary-read.graphql`, limited to relevant
  practice/practitioner/location/room/waiting read definitions;
- `docs/api-spine/manifests/agent-capability-charters.yaml`, limited to
  declarative agent-boundary patterns;
- `docs/api-spine/security/permission-matrix.yaml`, limited to practice-scoped
  read/proposal/confirmation patterns;
- `app/services/practice/practitioner_directory_read.py`;
- `app/routers/diary.py`, limited to `get_rooms`, `get_waiting_areas` and their
  normalization helpers; and
- `app/routers/appointments.py`, limited to the waiting-room GET boundary.

Do not list or search protected directories. Review the exact baseline-to-
candidate diff.

## Adversarial focus

Attempt to falsify, with particular attention to:

- whether Davida remains a separate identity and custodian interface rather
  than owner of truth, memory or a database actor;
- whether “shared kernel” can become a union of Bernie and Davida policy,
  fields, credentials, scopes or release authority;
- whether any model output can become confirmation, signed command,
  `writes_authorized=true`, database/API authority or mutating release;
- whether the read/context desk admits only pure practice-scoped reads and
  correctly blocks nominal GETs that normalize/commit and patient-linked data;
- whether the operation enum is genuinely closed and conservative;
- whether future REST proposal/confirmation fields keep command construction
  backend-owned, least-privilege, fresh, idempotent, auditable and explicitly
  human-confirmed;
- whether events are only hints requiring a fresh authorized read;
- whether the four-tranche sequence accidentally claims runtime/apply authority;
- whether the JSON schema is strong enough to reject authority-bearing or
  structurally incomplete mutations, rather than merely accepting the supplied
  instance; and
- any contradiction between docs, JSON, schema and tests.

## Deterministic reproduction

Run serially:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_davida_practice_administration_boundary.py tests\test_bernie_davida_parallel_seam.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check tests\test_davida_practice_administration_boundary.py
git diff --check bb8a6f554b417df019727345ba91a7d555b0bd41..19444399778dbd07b62223ca9b8a118a03d92d5b
git status --short --branch
git rev-parse HEAD
```

You may run additional read-only static/schema mutation checks within the
allowlist. Do not run providers, browsers, database-mutating commands or broad
repository discovery.

## Required response

List findings first with severity and precise file/line evidence. If none,
state that explicitly. Name checks actually run, confirm the exact HEAD and a
clean unchanged worktree, and identify claims not established. End with exactly
one terminal line:

`DECISION: pass`

or

`DECISION: revision_required`
