# Bernie Backdated & Past-Date Domain Policy Review

Sprint R4 defines receptionist-safe behavior for dates that are already in the past when Bernie is handling new booking intent.

## Policy Matrix

| Scenario | Definition | Expected Outcome | Reason Code | Staff Copy |
|---|---|---|---|---|
| Absolute past date | `date_from < reference_date` | `blocked` | `requested_date_in_past` | New appointments cannot be booked in the past. Please request today or a future date. |
| Same-day fully-past window | `date_from == reference_date`, but the requested time window has passed | `clarification_required` | `window_fully_past` | That time has already passed today — would you like a later time or another day? |
| Stale reference date | Session `reference_date` is before clinic-local today | `blocked` for mutation/confirmation when stale session guards apply | session/freshness stale reason code | Refresh the booking session before confirming. |

## Acceptance Rules

- Absolute past dates must block before slot search, candidate display, create-proposal evidence, or appointment mutation.
- Same-day fully-past windows remain a clarification path rather than the absolute-past-date guard.
- Partly-past same-day windows may still clamp to the remaining bookable window.
- Existing D8 patient collision semantics must remain unchanged: cap-overflow collisions still warn, and source appointments do not self-collide.
- Stale reference-date confirmation is a broader session-freshness invariant; keep it distinct from `requested_date_in_past`.

## R4 Implementation Mapping

- The shared normalizer emits `requested_date_in_past` when `date_from` is before the supplied `reference_date`.
- The interpret route reports the temporal axis as `block` for the same issue.
- The supervised booking route inherits the normalizer block and does not execute slot search.
- Direct raw appointment mutation surfaces are not changed by this sprint; they remain outside Bernie's new-booking slot-search path.
