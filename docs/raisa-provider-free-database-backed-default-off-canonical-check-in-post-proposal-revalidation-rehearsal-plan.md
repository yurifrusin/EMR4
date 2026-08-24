# Default-off canonical check-in post-proposal revalidation rehearsal plan

Date: 2026-08-24

Timestamp: 2026-08-24T17:48:07.2584918+10:00 (Australia/Brisbane)

Status: `frozen_two_scenario_plan`

Operation: `raisa-provider-free-database-backed-default-off-canonical-check-in-post-proposal-revalidation-rehearsal`

## Objective

Add exactly two authored-synthetic database-backed HTTP-route witnesses for
state that changes after a safe check-in proposal and before confirmation:

1. the authenticated user no longer has current Receptionist authority; and
2. the proposal's selected waiting area is no longer active.

The rehearsal is product assurance only. It does not reopen any repository
prerequisite for ordinary-practice admission.

## Frozen implementation boundary

The owned product-test surface is
`tests/test_model_required_bureau_a5_1_check_in_runtime.py`. Add exactly two
focused tests using its existing authored-synthetic fixtures and ordinary HTTP
proposal/confirmation helpers.

The authority-revocation test must:

- obtain a safe proposal while the user is a Receptionist;
- persist a different current role before the confirmation request;
- observe the existing authentication/authorization boundary deny the request;
- prove the appointment remains in its prior state; and
- prove zero check-in audit, event and idempotency rows.

The waiting-area test must:

- obtain a safe proposal that assigns one active same-practice/same-location
  waiting area;
- persist that area's inactive state before confirmation;
- observe the unchanged confirmation contract return a fail-closed blocked
  result with `waiting_area_not_active`;
- prove signed evidence was verified before the current-area rejection; and
- prove zero appointment, waiting-area assignment, audit, event or completed
  idempotency effect.

No product source may change unless either exact test exposes a real bounded
defect. If it does, stop before broad repair, reassess parallelism and freeze
the narrowest correction inside the same route/adapter contract.

## Acceptance

1. Both new focused tests pass against the unchanged product source.
2. The existing default-off feature flag and authored-synthetic practice
   allowlist remain byte-identical and disabled/empty by default.
3. Request/response models, status codes and client-visible block codes remain
   unchanged.
4. The denied requests persist zero appointment effect, audit, committed event
   or completed check-in command.
5. Existing A5.1 runtime, adapter, route-convergence and API Spine tests pass
   serially against their shared database boundary.
6. No historical/trove input, provider, model, external network or product data
   enters the rehearsal.

## API Spine boundary

The existing REST confirmation command remains explicit, practice-scoped,
idempotent and audited. Current authorization is mandatory at execution time;
the signed proposal cannot confer it. Current waiting-area truth is re-read at
confirmation. GraphQL remains read-only, committed events remain evidence and
not actuators, and no OpenAPI or schema artifact changes.

## Parallelism assessment

- DeepSeek: declined with negative leverage. The native occupied lane remains
  paused, Claude Code is not a silent fallback, and two tests share one serial
  database/runtime boundary.
- Gemini: not applicable with neutral leverage while product source remains
  unchanged and exact assertions decide acceptance. Reassess if a real product
  defect requires source repair.
- Native subagents: declined with negative leverage. The two scenarios share
  fixtures and mutable test-schema state, and developer policy supplies no
  separable parallel package.
- GPT Sol owns plan, two test witnesses, serial verification, acceptance,
  clockwork closeout and task-branch publication.

Reassess before any worker/provider dispatch, on a product-source defect, at a
material recovery, or at the next named tranche boundary.

## Closed authority

No ordinary-practice enablement, feature-flag default or allowlist change,
generic-status `Arrived` change, action grammar, client, waiting-area movement
feature, live practice, product/patient/clinical/protected data, historical
data, provider, production runtime, deployment, release, Pages or protected-ref
movement is authorised.

All unrelated untracked files, especially `docs/branding/`, remain preserved.
Use explicit-path staging only; never `git add .` or `git add -A`.
