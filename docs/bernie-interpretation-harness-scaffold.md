# Bernie Interpretation Harness Scaffold

Date: 2026-07-06

Sprint: H40

## Purpose

`app/services/bernie/interpretation_harness.py` is the first provider-free
Bernie Interpretation Harness scaffold after H39.

It maps authored synthetic receptionist utterances to native
`DiaryActionVerb` decisions, then uses the H37 route-authority inventory to
choose a non-executing dispatch class.

## Boundaries

The harness does not:

- Call LLM or provider clients.
- Import FastAPI routes or `TestClient`.
- Touch database models or sessions.
- Persist memory.
- Read raw historical diary files, ignored local outputs, H-series profiles, or
  H15 semantic fixtures.
- Create appointments, audits, proposals, signed evidence, or route calls.

## Dispatch Classes

- `route_to_confirm`: implemented mutating grammar verb with signed-confirm
  authority. The harness only labels it; it does not call the confirm route.
- `route_read_only`: implemented read-only grammar verb.
- `route_meta`: meta workflow control.
- `refuse_planned_not_implemented`: known planned grammar verb such as
  `check_in`, `waiting_area_move`, or `link_patient`.
- `refuse_unknown_utterance`: no deterministic authored rule matched.

## Verification

`tests/test_bernie_interpretation_harness.py` loads
all JSON fixtures under `tests/fixtures/bernie_interpretation_harness/` and
checks the expected grammar verb, route authority, and dispatch for each
synthetic utterance.

## H41 Adversarial Coverage

H41 adds `adversarial_utterance_actions.json` and the
`refuse_unsafe_instruction` dispatch class. The harness refuses unsafe wording
before grammar matching when an utterance attempts to:

- Bypass guardrails or staff confirmation.
- Call route endpoints directly.
- Write directly to a database/raw mutation path.
- Invoke a provider or LLM.

Mixed planned-action phrases remain planned. For example, "check in ... and
mark arrived" maps to `check_in` and dispatches
`refuse_planned_not_implemented`, not to the implemented `status_change` path.
