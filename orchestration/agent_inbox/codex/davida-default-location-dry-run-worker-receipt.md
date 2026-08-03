# Worker receipt: Davida default-location dry-run proposal

Date: 2026-08-03

Worker: native Codex bounded implementation subagent

Reasoning level: High, bounded implementation/test execution only

Source: `e7d209e6652106c8f69036460223259a33af19c9`

Branch: `codex/davida-default-location-dry-run`

## Rehydration

A fresh `new_session` Ariadne orchestrator receipt passed before
implementation with settings fingerprint
`sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`,
`rehydrated_from_receipt=true`, no reasons and all five required sources:

- `live_handover_current_baton`: complete `AGENTS.md` Current Baton read;
- `current_authority_allocation`: complete authority-allocation read;
- `active_plan_and_acceptance`: exact root packet, accepted Davida boundary,
  pure-read and advisory artifacts, API Spine ADR/programme/prototypes and API
  steward checklist read;
- `protected_evidence_boundaries`: complete sections 5 and 6 read; and
- `git_refs_and_worktree`: assigned worktree clean at exact source; `master`,
  `handoff/current`, `origin/master` and `origin/handoff/current` all observed at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The receipt's authority boundary was
`receipt_only_no_worker_control_or_integration_authority`.

## Exact result

Candidate for
`provider_free_practice_administration_default_location_dry_run_pass`.

The implementation admits exactly
`PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION`, validates the accepted context
and canonical selector-only candidate, resolves one opaque active practitioner
and one opaque active location, and releases only an exact non-authoritative
`proposal_candidate` / `dry_run_only` before/after projection. Current-null is
preserved, same-location rejects as `no_change`, and every command-ready,
confirmation, apply, write, provider, model, database, network and
model-to-database authority remains false.

The proposal and grounding hashes bind the canonical candidate, exact context
revision, source paths and before/after state. Rejection is atomic and contains
no proposal, repair or retry.

## Artifacts

- `app/schemas/practice_administration_default_location_proposal.py`
- `app/services/practice/practice_administration_default_location_dry_run.py`
- `docs/davida-provider-free-practice-administration-default-location-dry-run-plan.md`
- `docs/davida-provider-free-practice-administration-default-location-dry-run-design.md`
- `docs/security/davida-provider-free-practice-administration-default-location-dry-run-threat-model-delta.md`
- `orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/dry-run-contract.json`
- `orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/dry-run-contract.schema.json`
- `scripts/davida_provider_free_practice_administration_default_location_dry_run_acceptance.py`
- `tests/test_davida_provider_free_practice_administration_default_location_dry_run.py`
- this receipt

## Deterministic checks

- Focused in-memory acceptance: 60/60 cases passed; 2 released and 54 rejected;
  no evidence file was created.
- Serial pytest under the root-granted shared PostgreSQL slot: 140 tests passed
  across the new tranche, Davida advisory, Davida pure-read, Davida boundary,
  Bernie/Davida seam and API Spine artifact suites. The slot was explicitly
  released before commit preparation.
- Ruff: all four new Python paths passed.
- `git diff --check`: passed.
- Contract validates against its schema; recursive object closure and every
  contract-leaf mutation are test covered.
- Static checks find no ORM/database/network/clock/provider/model/router/
  GraphQL dependency or call in the new schema/service.
- Fresh `pre_commit` five-source Ariadne receipt passed with no reasons and the
  same settings fingerprint before staging.

## API Spine review

Classification is a non-mutating, unmounted dry-run transform. GraphQL remains
read-only and unchanged. No REST route, confirmation command, event, manifest,
idempotency key, audit/outbox record or write surface is introduced. A future
effectful administrative command remains backend-owned and separately gated.

## Gates and handoff

No final evidence JSON was created; root Sol owns final acceptance execution,
review, evidence, integration and any baton change. Provider/model, memory/RAG,
real identity/data, patient/clinical/document data, database/route, arbitrary
API access, confirmation/apply/write, deployment, production, release,
protected evidence/refs and `docs/branding/` remain closed and untouched.

Next work is root-owned candidate review and acceptance. No unresolved worker
implementation gate remains.

candidate_ready
