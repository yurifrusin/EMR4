# Reception One Default-off Dual-planner Runtime — Provider-free Sol Acceptance

**Date:** 2026-07-30
**Disposition:** `accepted_for_exact_occupied_route_preflight`

## Accepted result

The provider-free descendant passes. The authenticated, development-only,
authored-synthetic Reception One proposal route now has a closed
`planner_mode` enum:

- `deterministic` is the default and performs zero provider calls;
- `isolated_vertex` is separately default-off and may enter only the exact
  approved Bernie Sydney Vertex lane;
- once `isolated_vertex` is selected, neither provider nor deterministic
  planner fallback is permitted;
- both modes terminate at the existing proposal-only API Spine adapters;
- neither mode receives appointment write or confirmation authority.

The frozen v6.8 prompt, pre-printed form, response schema and credential-free
cell packet remain unchanged. A separate runtime policy binds the proofreader
to request wall time: current context admits and expired context edge-aborts
without release.

## Evidence reviewed

- `orchestration/continuity/reception-one-default-off-dual-planner-runtime/provider-free-evidence.json`
- `orchestration/continuity/reception-one-default-off-dual-planner-runtime/real-isolation-evidence.json`
- `docs/bernie-reception-one-default-off-dual-planner-runtime-plan.md`
- `docs/security/bernie-reception-one-default-off-dual-planner-runtime-threat-model-delta.md`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `docs/api-spine/manifests/agent-capability-charters.yaml`
- `tests/test_reception_one_default_off_dual_planner_runtime.py`

## Deterministic gates

- 8 focused dual-planner tests passed.
- 23 inherited route, proofreader and context tests passed.
- 25 API Spine tests passed.
- Python compilation and YAML parsing passed.
- The provider-free real-isolation run passed twice through non-root,
  network-none, read-only, capability-dropped, resource-bounded containers.
- The cell received no credentials, project, service-account identifier,
  provider hostname, database access, full Diary or unselected appointment.
- Owned containers, images and temporary contexts were absent after cleanup.
- Provider calls and credential reads were both zero.

## Remaining exact gate

An occupied route call may proceed only after Continuity and Compass bind this
accepted readiness result and the rendered Compass report validates, followed
by a fresh exact Bernie ADC/control/residue preflight. The occupied request must
remain authored-synthetic, Sydney-bound, proposal-only, proofreader-gated and
within the authorised USD 1 and two-call ceilings.

## Claim limits

This acceptance proves the local route seam, typed contracts, wall-clock
freshness behavior and provider-free isolation. It does not prove an occupied
route result, real-data safety, Australian physical or sovereign processing,
production suitability, appointment mutation, deployment or release.
