# Fresh Gemini veto review: Davida pure-read practice-administration context desk

Role: independent architecture, data-boundary, API Spine and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\davida-pure-read-context-desk-gemini-review`

Branch: `codex/review-davida-pure-read-context-desk`

Baseline HEAD: `0d8b2985fdae2ca488ae90e2ae1a5842190b296b`

Candidate HEAD: `24bdb4f0864c2d0fb515596dd204d6414e4c5f5d`

Settings fingerprint: `sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`

Review only in this exact worktree through a genuinely fresh Antigravity
project. Do not edit, create, delete, stage, commit, push, deploy, access another
worktree, or inspect prior DeepSeek/Gemini receipts or review packets. Protected
evidence, credentials, historical provider material, patient/clinical/product-
derived/real-identity data and `docs/branding/` are forbidden.

Read `AGENTS.md` completely and the EMR4 API Steward skill/checklist completely.
Inspect only the baseline-to-candidate diff, its eleven committed paths, the
accepted Davida boundary plan/design/threat/contract/schema/closeout, exact
`PracticeLocation`/`User` model columns, `PractitionerOut`, existing practitioner
pure-read service, current product-read finite role/pool code, and the three
named focused test files. Inspect the Diary room/waiting and appointment waiting-
room implementations only to validate their blocked-source reasons. Do not
perform broad repository discovery.

Adversarially review:

- exact strict `{id,name}` active-location output and actual model fit;
- practice scoping, active-only filter, `name,id` order, fixed 200 bound and
  `db.no_autoflush` with no commit/flush/add/delete/normalization;
- no route, GraphQL field, auth role/action/resource, migration or mounted app;
- composer purity: no SQLAlchemy/model/DB/network/provider/clock dependency;
- caller-supplied authorized projections only, timezone-aware supplied time and
  deterministic two-minute expiry/SHA-256 content revision;
- every internal UUID mapped through a bounded immutable opaque registry, with
  missing/duplicate/wrong-kind/cross-practice failure and zero UUID egress;
- exact two live-api-fact frames, exact blocked sources, minimal/non-authoritative
  labels and every command/write/proposal/apply/provider/event/model-to-DB flag
  structurally false;
- JSON instance/schema strictness at every nested level, including required
  exact values, array bounds and `additionalProperties: false`; independently
  mutate security-critical fields rather than trusting supplied tests;
- SQL-capture repair requires both table reads and rejects DML/DDL;
- evidence accurately proves SELECT-only execution, tenant isolation, bounds,
  table/session integrity, role denials and complete database/two-role cleanup,
  without IDs, names, secrets or raw authority;
- rooms, waiting areas and patient-linked queue stay blocked;
- API Spine read-only/context-frame conformance and absence of command authority.

Run serially and do not run the live acceptance script because that would write
the committed evidence file:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_davida_provider_free_practice_administration_pure_read.py tests\test_davida_practice_administration_boundary.py tests\test_practitioner_directory_graphql_resolver.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check app\schemas\practice_administration.py app\services\practice\active_location_directory_read.py app\services\practice\practice_administration_context_desk.py scripts\davida_provider_free_practice_administration_pure_read_acceptance.py tests\test_davida_provider_free_practice_administration_pure_read.py
git diff --check 0d8b2985fdae2ca488ae90e2ae1a5842190b296b..24bdb4f0864c2d0fb515596dd204d6414e4c5f5d
git status --short --branch
git rev-parse HEAD
```

Additional allowlisted read-only adversarial checks are permitted, but do not
write temp artifacts inside the worktree. List findings first by severity with
exact evidence. Name every check actually run, confirm exact unchanged HEAD and
clean worktree, distinguish observed evidence from inference, and name claims
not established. End with exactly one terminal line:
`DECISION: pass` or `DECISION: revision_required`.
