# Diary Action Route Contract

Date: 2026-07-06

Sprint: H37

## Purpose

`app/services/diary/action_route_contract.py` records the current static bridge
between `DiaryActionVerb` and backend route authority.

This is not a dispatcher. It does not import routers, call provider clients,
touch the database, read local diary trove material, or grant write authority.
It is documentation-as-code for tests and future Bernie interpretation harness
work.

## Current Authority Classes

- `signed_confirm`: implemented grammar verb backed by proposal routes and
  signed confirm actions.
- `read_only`: implemented read-only grammar verb with no confirm route.
- `meta`: workflow/control verb with no diary mutation route.
- `planned_not_implemented`: known grammar verb with no signed confirm action.

## Important Boundary

Adjacent routes do not make planned actions executable.

For example, `check_in` has nearby read/proposal surfaces such as check-in
defaults and status proposals, and `waiting_area_move` has a waiting-area
proposal surface. They still remain `planned_not_implemented` in the grammar
until a signed confirm action, audit contract, route contract, and staff
confirmation affordance exist.

## Verification

`tests/test_diary_action_route_contract.py` checks:

- Every grammar verb has exactly one route contract.
- Implemented confirm verbs map to existing `DiaryConfirmAction` endpoints.
- Planned verbs have no confirm actions or confirm routes.
- Read-only/meta verbs have no proposal, confirm, raw mutation, or staff
  confirmation authority.
- The route-contract module stays static and side-effect free.
