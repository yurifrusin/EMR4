# Sprint R8 — Confirm Route Temporal Revalidation Inventory

This inventory classifies appointment confirmation endpoints by whether they write appointment date/time and therefore require confirm-time temporal revalidation.

## Slot-Writing Confirms

| Method | Path | Handler | Confirm-time temporal coverage |
|---|---|---|---|
| `POST` | `/api/v1/appointments/proposals/create/confirm` | `confirm_create_proposal_route` | Re-runs `_build_create_appointment_proposal`, which calls `evaluate_raw_mutation_temporal_guard` with the current clinic-local clock. |
| `POST` | `/api/v1/appointments/proposals/create/confirm-bernie` | `confirm_bernie_create_proposal` | Re-runs `_build_create_appointment_proposal` after selection/session/freshness checks. |
| `POST` | `/api/v1/appointments/proposals/update/confirm` | `confirm_update_proposal_route` → `confirm_update_proposal` | Re-runs `propose_update_appointment`, which applies the temporal guard when date/time/duration are present in the command. |

These routes already have confirm-time temporal coverage through full proposal revalidation. R8 codifies that as the expected contract and adds regression tests for the clock-advance case.

## Non-Slot Confirms

| Method | Path | Handler | Temporal policy |
|---|---|---|---|
| `POST` | `/api/v1/appointments/proposals/status-confirm` | `confirm_status_proposal_route` | Exempt; status-only write. |
| `POST` | `/api/v1/appointments/proposals/delete-confirm` | `confirm_delete_proposal_route` | Exempt; cancellation/delete write, no new slot allocation. |

## Guard Chain

Slot-writing confirmation routes are protected by:

1. Explicit `confirmed=true`.
2. Proposal safety/tier checks.
3. Freshness ID verification.
4. Signed confirmation evidence verification.
5. Entity/current-state rechecks.
6. Full proposal revalidation against current conflicts, breaks, and temporal policy.
7. Command shape comparison before the final write.

## Required Regression Cases

- Staff create proposal minted while same-day slot is open, confirmed after the slot fully elapsed: blocked with `create_proposal_revalidation_blocked` and `same_day_window_elapsed`.
- Update proposal minted while same-day target slot is open, confirmed after the slot fully elapsed: blocked with `update_proposal_revalidation_blocked` and `same_day_window_elapsed`.
- Bernie create selection/proposal minted while same-day slot is open, confirmed after the slot fully elapsed: blocked with `create_proposal_revalidation_blocked` and `same_day_window_elapsed`.
- Existing status/delete confirmation tests remain the coverage for the exemption boundary.
