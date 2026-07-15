# Product Platform, API, and Security Ledger

## Product architecture

EMR4 Centaur is an AI-native Australian General Practice management system.
FastAPI/PostgreSQL provides clinical and diary authority; the Microsoft Word
Office.js add-in is the clinical workspace. Word Online is the target Office
surface. The native browser diary grid supersedes the retired Word-table diary
for interactive scheduling.

The definitive phase and architecture plan is `implementation_plan.md`.
Current language-coverage work does not authorize unrelated route, GraphQL,
database, UI, deployment, or release changes.

## API Spine

Use the `docs/api-spine/` contracts and the EMR4 API steward rules whenever a
sprint touches GraphQL/read models, REST/OpenAPI commands, appointment
proposals/confirmations, Access AI boundaries, context frames, manifests,
async contracts, audit, security, or idempotency. A sprint must not claim API
Spine compatibility without running the relevant contract guards.

## Security posture

Production settings fail closed for default secrets and CORS uses an
allowlist. Open structural work includes PostgreSQL RLS defense-in-depth, the
full audit-log surface, JWT storage hardening, and field-level encryption.
Dependabot alert 5 remains open; do not force dependency overrides. Security,
deployment, external-patient access, and release gates remain explicit user
decision boundaries.

## Environment and deployment orientation

- Full local stack: `run_dev.ps1` (`-Down` stops it).
- Backend: `.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001`.
- Migrations: `.venv\Scripts\python.exe -m alembic upgrade head`.
- Taskpane source: `EMR4 Sidebar/src/taskpane/`; published copy:
  `docs/taskpane/`; synchronize with `sync_taskpane.py`.
- Command Centre: `docs/command-centre/`.
- Native Diary: `docs/diary/`.

GitHub Pages must deploy from canonical `master`; a stale worker-branch deploy
can overwrite the live artifact. Word Online is strict about OOXML element
order, so raw OOXML insertions must respect schema ordering.

The immutable pre-compaction handover preserves detailed phase history,
environment credentials guidance, file maps, historical defects, and deploy
gotchas. Treat source and current docs as authority when old narrative and live
code differ.
