# Diary Planned Action Promotion Checklist

Date: 2026-07-06

Sprint: H39

## Purpose

`app/services/diary/planned_action_promotion.py` defines the gates required
before a planned native Diary grammar action may become implemented.

This is static domain metadata only. It does not dispatch actions, add routes,
call providers, touch the database, read historical diary material, or grant
write authority.

## Planned Verbs Covered

- `check_in`
- `waiting_area_move`
- `link_patient`

## Required Promotion Gates

Each planned verb must satisfy all gates before its grammar descriptor can move
from `implemented=False` to `implemented=True`:

- Route contract.
- Signed confirm action.
- Signed evidence.
- Audit contract.
- Staff confirmation affordance.
- Role and tenancy policy.
- UI affordance.
- Regression tests.

## Current Boundary

The current route contract may document adjacent read or proposal surfaces, but
the planned verbs remain non-executable until they have confirm actions,
confirm routes, signed evidence, audit behaviour, role/tenancy policy, and UI
affordances reviewed together.

This matters most for `check_in` and `waiting_area_move`, where nearby status or
waiting-area proposal routes already exist. Those routes are not enough to make
the grammar verbs executable.
