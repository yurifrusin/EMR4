# Fresh Gemini review 2: hardened Davida practice-administration architecture

Role: independent architecture, API Spine and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\davida-practice-administration-gemini-review-2`

Branch: `codex/review-davida-practice-administration-architecture-2`

Candidate HEAD: `2c9fe167af22c01660b55407f115daf50c7fa30f`

Baseline HEAD: `bb8a6f554b417df019727345ba91a7d555b0bd41`

Settings fingerprint: `sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`

Review only in the exact worktree through a genuinely fresh Antigravity project.
Do not edit, create, delete, stage, commit, push, deploy, access another
worktree, or inspect any prior worker/reviewer output. Protected evidence,
historical Diary material, credentials, patient/clinical/product/identity data
and `docs/branding/` are forbidden. This candidate is architecture-only,
provider-free and non-executing and grants no runtime/read/write/deploy authority.

Read `AGENTS.md` completely. Then inspect only the baseline-to-candidate diff,
the six candidate artifacts, `docs/bernie-davida-parallel-seam-plan.md`,
`docs/bernie-davida-shared-agent-boundary.md`, the seam threat delta and JSON
contract/schema, `tests/test_bernie_davida_parallel_seam.py`,
`orchestration/api_spine_adr.md`, `orchestration/api_spine_programme.md`,
`orchestration/access_ai_api_design.md`, relevant definitions in
`docs/api-spine/graphql/appointment-diary-read.graphql`, relevant declarative
patterns in `docs/api-spine/manifests/agent-capability-charters.yaml` and
`docs/api-spine/security/permission-matrix.yaml`,
`app/services/practice/practitioner_directory_read.py`, only `get_rooms`,
`get_waiting_areas` and their normalization helpers in `app/routers/diary.py`,
and only the waiting-room GET boundary in `app/routers/appointments.py`.
Do not perform broad repository discovery.

Adversarially test separation from Bernie, no DB/API/model-to-command authority,
the pure-read/context-desk boundary, the exact closed operation enum, backend-
owned post-human-confirmation envelopes, hint-only events and the four-tranche
authority ceiling. Independently mutate every security-critical JSON field and
array. Confirm the Draft 2020-12 schema rejects arbitrary/reordered/missing
operations, reversed authority/identity/emission/event booleans, missing command
preconditions or human-confirmation binding, altered tranches/gates, incomplete
nested objects and unknown nested fields. Do not infer schema rigor merely from
the supplied instance or test assertions.

Run serially:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_davida_practice_administration_boundary.py tests\test_bernie_davida_parallel_seam.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check tests\test_davida_practice_administration_boundary.py
git diff --check bb8a6f554b417df019727345ba91a7d555b0bd41..2c9fe167af22c01660b55407f115daf50c7fa30f
git status --short --branch
git rev-parse HEAD
```

Additional allowlisted read-only mutation checks are permitted. List findings
first with severity and exact evidence, name checks actually run, confirm exact
HEAD and a clean unchanged worktree, and name claims not established. End with
exactly one terminal line: `DECISION: pass` or
`DECISION: revision_required`.
