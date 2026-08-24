# Provider-free read-only waiting-area movement command-family readiness review plan

Date: 2026-08-24

Timestamp: 2026-08-24T18:44:13.5010595+10:00 (Australia/Brisbane)

Status: frozen

Source HEAD: `11317b69c6fcd0e97a002b4196ec92cc33f47110`

Reasoning level: high — read-only API/authority boundary classification

## Objective

Identify the narrowest canonical proposal-confirm boundary for an explicit
waiting-area-only appointment movement. The review must distinguish reusable
accepted foundations from missing family-owned authority and must not overlap
dedicated check-in or general status confirmation.

This tranche reads repository text only. It does not edit product source, add
an API operation, mount or call a route, open a database, or use historical
diary data.

## Exact source boundary

After this freeze, review reads and hashes are limited to the following exact
non-protected UTF-8/LF text sources. Every SHA-256 binding is fail-closed.

| SHA-256 | Exact source |
|---|---|
| `0e0f42290688943bc9dd7d5711826acf10430133be0b309eae94bad15da46ca2` | `app/main.py` |
| `8443bc1d045672f05567a5cb6443a882dfda4946791412c231ce475995f71d08` | `app/routers/appointments.py` |
| `ce7a9819e4947fb288c79009a08b7d9f2502b8d096ff5e2eb005796a250aee90` | `app/schemas/appointments.py` |
| `4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794` | `app/models/appointments.py` |
| `a067e05802a74461fb14571c26e02bb72f34fcdd4624ee2a5ebcadd0266cdf55` | `app/services/appointment_status_product_adapter.py` |
| `4ab9d0ff3816d85d7eb374e97fec7618e0b922354b104766b2898b0989e56f1b` | `app/services/appointment_status_physical.py` |
| `ef6abdfef1b99737c527790be007ab07296bbc0422197858a5ae561012230570` | `app/services/appointment_check_in_product_adapter.py` |
| `0dfbce13f3d8933d0cd2355fb41e70612c1550e75c452b95c1528576ac1c8622` | `docs/api-spine/openapi/appointment-commands.yaml` |
| `fef2ac9d3fcfa954388bc6432206316ac5a9d64e8906b494a012b88c567a67ba` | `docs/api-spine/async/integration-events.yaml` |
| `b874287c039574e8f0aae30a8e1cdd52cd07be31998b2cd8473991f37e49bacf` | `docs/diary/diary.js` |
| `1379b2f506a8388097404c805d9eaa6599c854ea14b3aff4fc26a22f0aa98101` | `tests/test_api_spine_status_confirm_idempotency_route_contract.py` |
| `844477f41caa7b3d85b362dd3ccdc558461aa2cda52d59f0b814d341a6d6d36e` | `tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter.py` |
| `c99782bef15482347b8cc983db8323d89d68c8bf8467053f94af009b6be6b2ca` | `tests/test_model_required_bureau_a5_1_check_in_runtime.py` |
| `69c3bbe767118815663ea4cd1417148be17a83abf1c0203e663ef47571aed528` | `docs/raisa-provider-free-status-confirm-http-route-convergence-closeout.md` |
| `aa2eab6fddc0f8394ea3950965d525222917506a04b0ef10ab22999e2e442363` | `docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture.md` |
| `a386e7c81eba537518a74eb07655bd6f255fc775df2ab37d4223bdbd947939c1` | `orchestration/continuity/raisa-provider-free-database-backed-default-off-canonical-check-in-post-proposal-revalidation-rehearsal/next-tranche-contract.json` |

No repository-wide search is permitted after freeze. The deterministic reviewer
imports no `app` module and executes no route, database, Docker or SQL surface.

## Frozen classification

The machine contract defines twelve ordered dimensions. Each is exactly
`satisfied` or `blocking_gap`. Any blocker yields
`waiting_area_command_family_not_ready`; all satisfied would yield
`waiting_area_command_family_already_complete` and must fail unless supported by
the bound sources.

The expected evidence-led matrix is five satisfied foundations and seven
blocking dimensions. The expected narrow successor is one provider-free,
unmounted waiting-area-confirm command-family architecture tranche—not a route
mount or product implementation.

## Non-overlap invariant

- dedicated check-in alone may combine `Booked -> Arrived` with an initial
  waiting-area assignment; it continues to reject moving an existing area;
- general status confirmation continues to own status transitions and their
  presently accepted waiting-area side effects; and
- the proposed sibling family changes only `waiting_area_id` while status and
  arrival state remain unchanged. It accepts no generic-status authority and
  supplies no check-in authority.

## Exact owned outputs

GPT Sol serially owns the plan, threat delta, contract/schema, deterministic
reviewer/tests, evidence/report, acceptance and closeout. DeepSeek is declined
because the native occupied runner remains paused and this tightly coupled
static evidence join has no bounded mechanical package. Gemini is not
applicable because the frozen predicates decide the result. Native subagents
are declined because there is no separable package and current system policy
does not authorise a dispatch.

Owned review outputs are limited to:

- `scripts/raisa_provider_free_read_only_waiting_area_movement_command_family_readiness_review.py`;
- `tests/test_raisa_provider_free_read_only_waiting_area_movement_command_family_readiness_review.py`;
- `tests/test_raisa_provider_free_read_only_waiting_area_movement_command_family_readiness_review_plan.py`;
- the named contract, schema, evidence and report beneath the tranche's
  Continuity directory; and
- normal non-product acceptance, closeout, human-summary and clockwork files.

## Acceptance

Pass requires all sixteen exact bindings, all twelve dimensions in order, the
expected 5/7 count and verdict, the three-way non-overlap invariant, at least
72 hostile contract mutations rejected, no `app` import or runtime execution,
focused tests, Ruff, maintained-source compilation and Git whitespace checks.

## Non-authority

No product source, API Spine, schema/model/migration, route edit/mount/call,
ordinary-practice enablement, historical data, database/Docker/SQL, provider,
network, patient/clinical/product data, UI behavior, deployment, production,
release, Pages or protected-ref movement is authorised. Preserve
`docs/branding/` and every unrelated untracked file. Stage explicit paths only.
