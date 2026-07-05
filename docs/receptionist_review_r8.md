# Receptionist-Domain Safety Review: Sprint R8 Confirm-Time Temporal Revalidation

Sprint R8 reviews the wall-clock drift hazard for signed appointment proposals: a receptionist may mint a safe create/update proposal while a same-day slot is still open, then confirm it after the slot has fully elapsed.

## Policy

| Route family | Temporal condition at confirm time | Policy | Rationale |
|---|---|---|---|
| Create/update/Bernie slot-writing confirms | `appointment_date < clinic_today` | Block | The proposal is now for a historical date and must be re-created. |
| Create/update/Bernie slot-writing confirms | Same-day `slot_end <= clinic_now` | Block | The appointment window is fully elapsed; confirming it would create a retrospective slot-consuming write. |
| Create/update/Bernie slot-writing confirms | Same-day `slot_start <= clinic_now < slot_end` | Permit | The appointment is still active; the current guard blocks only fully elapsed windows. |
| Status/delete confirms | Any appointment date/time | Exempt | These routes do not allocate a new slot or reschedule time; retrospective status and cancellation work is operationally necessary. |

## Staff Copy

- `appointment_in_past`: "This proposal is for a past date. Please return to the diary and choose a current or future date."
- `same_day_window_elapsed`: "This appointment window has already elapsed. Please return to the diary and choose a later slot."
- Active same-day slot: no new block in R8; future UX may add a non-blocking warning if staff need extra situational awareness.

## Exemption Notes

Status and delete confirmations remain outside temporal blocking because receptionists must be able to retrospectively mark no-shows, completions, cancellations, and correctional deletions. Their safety model is freshness, signed confirmation evidence, RBAC, and audit trail integrity rather than slot-time eligibility.

## Verification Focus

R8 should prove that slot-writing confirms re-run proposal validation at confirm time and therefore block a same-day proposal that was valid at mint time but fully elapsed before confirmation. The regression suite should cover staff create confirm, Bernie create confirm, and update confirm, while leaving status/delete semantics unchanged.
