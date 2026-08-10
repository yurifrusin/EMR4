# EMR4 bounded codebase conformance repair plan

Date: 2026-08-11

Source HEAD: `8ce3a591fa0e63ad2d68bf95a8d7e24369dd872f`

Status: `frozen_for_provider_free_execution`

## Purpose

Close the exact P1/P2 verification and lifecycle defects accepted by the
architectural-health review before AES-C0 begins. This is a repository
conformance repair, not a product refactor. It changes no route behavior,
authority, database state, model/provider path or user-visible workflow.

## Frozen repair slices

### CR-1 — maintained Python 3.11 source state

Add one machine-readable source-state manifest and deterministic validator.
The manifest must:

- select ordinary maintained application roots and exact current Bernie-domain
  modules without recursively entering the mixed historical/protected Bernie
  evaluation tree;
- distinguish recursive safe roots, top-level-only roots and exact files;
- declare Python 3.11 as the target;
- reject duplicate, absent, escaping, `local_data`, holdout-named or otherwise
  forbidden selected paths; and
- compile selected source in memory without creating `__pycache__` evidence.

Protected holdouts v1-v10 and every fixture, support, manifest, seal and per-
case artifact remain invisible to the manifest and validator. The repair must
not enumerate them to prove exclusion.

`scripts/verify_repository.py` will derive its Ruff paths from this manifest.
The local `fast` profile validates/compiles with the installed interpreter and
Ruff's configured `py311` grammar. A new `ci-correctness` profile additionally
requires the running interpreter to be Python 3.11, then runs the bounded
static correctness tests. The protected-branch Python workflow will run this
profile on its existing Python 3.11 runner before dependency and Bandit scans.

The only product-source edit admitted is removal of the already diagnosed
unused `pydantic.Field` import in the mounted Bernie UI view-model module.

### CR-2 — API Spine lifecycle supersession

Preserve the July 8 external-read-model gap inventory unchanged as historical
evidence. Add one machine-readable current external-read-model status index
that records separately:

- implementation/composition status;
- authority kind;
- deployment/production readiness; and
- the exact historical row or later artifact it supersedes.

The practitioner directory REST and GraphQL surfaces are implemented and
mounted reads, but remain neither deployment nor production claims. Patient
reminders, patient messages, RACGP and licensed Cochrane lookup remain future
gaps. Tests must consume the current index for current assertions and treat the
old five-row inventory as immutable historical posture rather than live truth.

This slice creates no resolver, route, provider, external evidence adapter,
patient read or write authority.

### CR-3 — baton and plan consistency

Add a deterministic current-baton consistency test binding:

- Continuity graph revision and node;
- Compass map/source revision and current node;
- the live AGENTS Current result, Required Git relation and Next
  implementation rows; and
- the current master-plan handoff paragraph.

Remove the two already diagnosed stale prose statements that still describe
the completed architecture review as future work. Historical ledgers and
accepted evidence are not rewritten.

## Owned files

- `docs/raisa-codebase-conformance-repair-plan.md`
- `orchestration/harness_settings/python_source_state.json`
- `scripts/python_source_state.py`
- `scripts/verify_repository.py`
- `.github/workflows/python-security.yml`
- `requirements-dev.txt`
- `app/services/bernie/ui_view_model.py`
- `docs/api-spine/external-read-model-current-surface-status.json`
- `docs/api-spine/external-read-model-current-surface-status.schema.json`
- `tests/test_python_source_state.py`
- `tests/test_repository_maintenance.py`
- `tests/test_api_spine_external_read_model_gap_inventory.py`
- `tests/test_api_spine_external_read_model_current_surface_status.py`
- `tests/test_current_baton_consistency.py`
- `AGENTS.md`
- `implementation_plan.md`
- tranche receipts, closeout, mailbox, Continuity/Compass and their focused
  tests/updater at final acceptance.

## Forbidden surfaces

- no protected holdout enumeration, search, import, hash, run or inference;
- no historical Diary/local-data access;
- no patient, clinical, product-derived or financial data;
- no provider, external retrieval, credential, IAM or model call;
- no database behavior rehearsal, migration application, watcher/listener,
  source read or operational persistence;
- no product route, GraphQL field, REST command, UI behavior or fallback-policy
  runtime change;
- no deployment, production, release, Pages or protected-ref movement; and
- no broad Git staging or staging of `docs/branding/` or unrelated untracked
  files.

## Deterministic acceptance

The tranche passes only when:

1. source-state hostile tests reject path escape, missing paths, recursive
   Bernie-root selection, holdout-named paths, duplicates and target-runtime
   mismatch without enumerating protected contents;
2. every selected maintained source compiles in memory and passes Ruff under
   the `py311` target;
3. `ci-correctness` is wired to the Python 3.11 workflow and its static test
   packet can run using pinned developer dependencies;
4. the historical API Spine gap packet remains present and bounded while the
   current status index accurately records implemented practitioner reads and
   four still-closed gaps;
5. the previously failing focused API Spine packet passes;
6. the baton-consistency test rejects the known stale review-next and attempt-
   016 patterns and binds Continuity 235 / Compass 217 before closeout
   advancement;
7. the full local `fast` verification profile, focused conformance tests, Ruff
   and `git diff --check` pass; and
8. tracked scope is exact, protected refs remain
   `2e34bdad732fdab32fbf778280b3d3c70d66d602`, and every unrelated untracked
   file remains preserved.

Local Python is newer than 3.11, so local evidence combines in-memory host
compilation with Ruff's explicit `py311` parser. The GitHub workflow supplies
the exact Python 3.11 runtime and must fail if that runtime changes.

## Recovery and next work

A deterministic failure is repaired only within the exact three slices. A
finding that requires opening protected evidence, altering product behavior or
choosing between materially different user outcomes stops the tranche.

After acceptance, AES-C0 architecture and contract begins automatically. It
must consume the source-state, no-fallback, route-classification and command-
separation fitness direction from the architectural-health review. No user
decision fork is present.
