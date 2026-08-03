# Worker packet: Davida default-location dry-run proposal

Date: 2026-08-03

Authority: bounded implementation and focused tests only

Source head: `e7d209e6652106c8f69036460223259a33af19c9`

Worktree:
`C:\Users\sarashera\EMR4-worktrees\davida-default-location-dry-run`

Branch: `codex/davida-default-location-dry-run`

Target result:
`provider_free_practice_administration_default_location_dry_run_pass`

## Frozen boundary

Implement Davida lane step 3 for exactly
`PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION`. Add a route-free, database-free,
provider-free trusted deterministic proofreader/dry-run component over one
already accepted `PracticeAdministrationContextFrame`. It resolves one opaque
active-practitioner reference and one opaque active-location reference and
computes an exact structured before/after default-location projection.

The candidate is frozen, strict and extra-forbid. It binds practice/principal/
correlation references, exact context revision, caller-supplied timezone-aware
evaluation time, exact operation, practitioner target, location target,
`reason_code=PRACTICE_ASSIGNMENT_UPDATE`, `risk_tier=admin_proposal`, and literal
false confirmation/apply/write/command/model/database authority. Reject Python/
Pydantic coercion by canonical input equality.

The released object is a non-authoritative `proposal_candidate` / `dry_run_only`
artifact. It contains exact context/source paths, before/after state, one fixed
changed path, hashes and an expiry no later than the context expiry. It says
human confirmation is required but contains no confirmation evidence/envelope,
command route/payload, idempotency key, aggregate version, audit/outbox event or
apply affordance. `command_ready`, `apply_authorized`, `writes_authorized`,
`provider_executed`, `model_executed`, `database_used`, `network_used` and
`model_to_database` remain literal false. Same-location requests reject as
`no_change`.

Evidence label:
`provider_free_unoccupied_default_location_dry_run`; data class:
`authored_synthetic`.

## Owned paths

- `app/schemas/practice_administration_default_location_proposal.py` (new)
- `app/services/practice/practice_administration_default_location_dry_run.py` (new)
- `docs/davida-provider-free-practice-administration-default-location-dry-run-plan.md` (new)
- `docs/davida-provider-free-practice-administration-default-location-dry-run-design.md` (new)
- `docs/security/davida-provider-free-practice-administration-default-location-dry-run-threat-model-delta.md` (new)
- `orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/dry-run-contract.json` (new)
- `orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/dry-run-contract.schema.json` (new)
- `scripts/davida_provider_free_practice_administration_default_location_dry_run_acceptance.py` (new)
- `tests/test_davida_provider_free_practice_administration_default_location_dry_run.py` (new)
- `orchestration/agent_inbox/codex/davida-default-location-dry-run-worker-receipt.md` (new, durable worker receipt)

Do not create the final evidence JSON; root runs the acceptance script after
review.

## Acceptance cases

- exact valid change, current-null change and deterministic repeated output;
- same-location no-op, missing/wrong-kind practitioner/location, duplicate or
  dangling references and cross-scope tampering fail closed;
- stale/naive/out-of-window evaluation and context revision/content tampering
  fail closed;
- unknown, advisory, other proposal, confirmation, apply and write operation
  codes fail before release;
- coercible values, unknown fields, free text, caller-supplied before/after,
  command/idempotency/confirmation/audit/provider/model/database/network fields
  and authority reversal fail closed;
- released before state is copied exactly from context and after state differs
  only at the fixed default-location path;
- proposal hash and grounding hash bind the canonical candidate, context
  revision, source paths and before/after payload;
- rejection is a closed union with no partial proposal, repair or retry;
- recursive contract schema is closed and every leaf mutation fails;
- source has no ORM/database/network/clock/provider/model/router/GraphQL import
  or call; parent boundary/advisory, seam and API Spine tests pass serially.

## Forbidden paths and claims

Do not edit any accepted parent file, existing schema/service, `app/main.py`,
routers, GraphQL, models, migrations, OpenAPI/manifests, `docs/diary/**`,
`AGENTS.md`, Continuity/Compass global maps, harness settings, workflows,
`docs/branding/**`, protected evidence or the other lane. No provider/model,
memory/RAG, real identity/data, database/route, confirmation/apply/write,
deployment, production, release or protected-ref action.

## Worker mechanics

Use `apply_patch` only. Run focused tests/Ruff/static checks serially. Stage
only owned paths by exact pathname, assert no `docs/branding/` path is cached,
commit to the task branch, and return the exact commit plus one terminal
`candidate_ready` or `revision_required`. Do not push.
