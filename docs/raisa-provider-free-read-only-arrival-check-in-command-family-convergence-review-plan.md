# Provider-free read-only arrival/check-in command-family convergence review plan

Date: 2026-08-18

Timestamp: 2026-08-18T06:20:30.8340302+10:00 (Australia/Brisbane)

Status: `frozen_for_read_only_execution`

Task baseline: `fb39d235c5dc4de2440a5b0e4685ee5da5b4f4d0`

Target result:
`raisa_provider_free_read_only_arrival_check_in_command_family_convergence_review_pass`

Reasoning level: Extra High. This tranche changes no product or runtime source,
but it chooses the durable semantic relationship between two mounted command
families that can currently produce the same `Arrived` appointment state.

## Objective

Compare the exact general status, waiting-area and A5.1 check-in contracts and
choose one canonical product-facing meaning for arrival, or a strict justified
non-overlap, before any route, grammar or first-party client is changed.

The review must distinguish:

- appointment `Arrived` as a database state;
- check-in as the domain command that ordinarily creates that state;
- a waiting-area assignment as an optional check-in effect, not proof of
  arrival by itself;
- a general status command used for other lifecycle transitions; and
- a default-off authored-synthetic A5.1 admission gate from the reusable
  deterministic check-in kernel represented behind it.

## Exact evidence sources

Read only:

1. `AGENTS.md`, the accepted post-cancellation orientation plan, finding,
   closeout and Sol acceptance, and the active operation latch;
2. `docs/emr4-model-required-bureau-a5-b4-command-runtime-plan.md`, its
   closeout and Sol acceptance;
3. `orchestration/api_spine_adr.md`, `orchestration/api_spine_programme.md`
   and `docs/api-spine/openapi/appointment-commands.yaml`;
4. `app/config.py`, `app/routers/appointments.py`, appointment schemas,
   idempotency/event services and the status product/physical seams as
   repository source only;
5. `app/services/diary/action_grammar.py`, `confirm_actions.py`,
   `action_route_contract.py` and `planned_action_promotion.py`;
6. `docs/diary/diary.js`, `docs/diary/meta-grid.js` and the exact first-party
   status/check-in tests; and
7. the accepted status-confirm route, PostgreSQL adapter and visible native
   Diary closeouts.

Historical Diary/PHI, live source or database state, product data, provider
output, external channel state and protected evidence are ineligible.

## Required comparison

For general status, waiting-area-only and A5.1 check-in, record:

1. request and confirmation envelope;
2. role, practice and admission gate;
3. signed evidence, freshness and replay posture;
4. accepted source and target state;
5. waiting-area behavior and validation;
6. transaction, audit, event, receipt and fresh-read behavior;
7. ordinary Diary and Reception One consumer posture; and
8. static action grammar, route-contract and promotion posture.

## Decision rule

Prefer a dedicated canonical check-in command if current evidence proves that
check-in carries materially stronger domain meaning than the bare assignment
of `Arrived`. Prefer generic status only if it can record the same check-in
meaning without losing authority, waiting-area, replay, audit, event or receipt
properties. Retain both only if their allowed callers, intents, effects and
audit meaning are non-overlapping and mechanically enforceable.

The selected relationship must not infer product admission from route
existence. Any future cutover must avoid a period in which first-party clients
have no valid check-in path and must not leave two canonical paths for the same
ordinary check-in intent.

## Acceptance

The tranche passes only if it:

1. produces the complete contract matrix;
2. identifies the reusable deterministic kernel and the A5.1-only
   gate/provenance layer;
3. classifies each static grammar/route-contract claim as current,
   scope-qualified or superseded;
4. explains the `{appointment_id}` versus `{appointment_id:uuid}` route
   spelling and the resulting literal-shadow false positive without editing
   either source;
5. chooses exactly one canonical product-facing arrival meaning or a strict
   mechanically enforceable non-overlap;
6. freezes one narrowest later architecture/implementation tranche;
7. keeps A5.1 default-off, uncalled and unmodified and changes no product,
   backend, API/OpenAPI, schema, service, migration or product test;
8. passes focused factual/plan assertions, API Spine/static checks, the
   canonical fast profile, latch/baton/Compass checks and Git whitespace; and
9. receives one fresh Gemini 3.7 Flash/high exact-candidate read-only veto
   because this review freezes material command-family meaning.

## Parallelism-efficacy allocation

- **Sol:** owns the coupled semantic comparison, selection, admission,
  acceptance and Git.
- **DeepSeek V4 Flash/high — declined:** the review has no stable separable
  implementation package; dispatch overhead would not shorten the coupled
  decision.
- **Gemini 3.7 Flash/high — reserved:** one fresh exact-candidate veto follows
  deterministic admission.
- **Native subagents — declined:** current developer policy prohibits
  proactive native delegation.

Reassess after the report is frozen, before verifier dispatch and at closeout.

## Expected successor boundary

If dedicated check-in is selected, the narrowest successor is an unmounted,
provider-free product-adapter extraction rehearsal. It separates reusable
check-in admission, current-authority/state validation, waiting-area policy,
idempotency, effect/audit/event/receipt composition and readback from the
Rayleen-named default-off gate. It does not yet change a route, enable a
practice, register a grammar action, wire a UI or exclude `Arrived` from the
general status family.

## Closed surfaces

No product behavior, FastAPI/OpenAPI/GraphQL/schema/service/migration/database
source, route mounting, raw compatibility behavior, action grammar or route
contract repair, feature flag, live route/database/source/watcher access,
external client, product/patient/clinical/historical/protected data,
provider/ADC, credential/IAM/network, executable model tool, command/write,
deployment, production, release, Pages or protected-ref action is authorised.
Preserve `docs/branding/` and every unrelated untracked file; use explicit-path
staging only.
