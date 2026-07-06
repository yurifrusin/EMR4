# Sprint R26 Receptionist Review

Date: 2026-07-06
Scope: H-series neutral profiles as source-safe product input
Decision: use a separate profile layer; do not promote neutral deltas into
Bernie booking scenarios yet.

## Summary

The H-series results are useful, but only as **neutral movement profiles**. They
show that ordinary diary snapshots usually preserve a stable grid while small
aggregate counts move. They do not show why those changes occurred.

For receptionist-domain work, the correct use is to create a small, safe middle
layer that reminds future sprints what kinds of deterministic invariants matter:
backend authority, refresh stability, no unconfirmed writes, no semantic
inference from neutral count movement, and clear separation between fake
scenario data and H-series evidence.

## What H-Series Profiles Are Useful For

- Preserving the fact that ordinary diary operation is mostly stable-grid,
  small-delta movement.
- Driving source-safe tests that prevent raw historical diary data from entering
  committed fixtures.
- Guiding future synthetic scenario design: if we later author fake examples,
  those examples should stress refresh stability, no-write boundaries, and
  backend-confirmed authority.
- Reminding Bernie/Diary work that visual or textual movement in a diary does
  not by itself prove a booking, cancellation, arrival, or roster change.

## What They Must Not Infer

Neutral H-series event classes must not be translated into receptionist meaning:

| Neutral class | Blocked inference |
|---|---|
| `no_structural_change` | A receptionist opened, searched, or viewed a specific patient |
| `small_content_delta` | A note was added, an appointment was booked, or a status changed |
| `time_grid_delta` | A roster changed or a clinician started early/late |
| `large_unexplained_delta` | A template was pasted, a blockout was added, or leave was entered |

Those may be useful **synthetic fake-data scenario themes** later, but they are
not conclusions from the trove.

## Recommended R26 Boundary

Keep H-derived artifacts here:

```text
tests/fixtures/h_series_profiles/
```

Do not put them here yet:

```text
tests/fixtures/bernie_scenarios/
```

The Bernie scenario corpus should remain either manually authored product memory
or executable fake-data replay. H-series profiles are aggregate evidence about
movement shape, not natural-language receptionist turns.

## Future Synthetic Scenario Families

Once authored from explicit fake data, not from inferred trove semantics, these
families would be valuable:

- **Refresh stability:** a visible diary refresh preserves backend appointment
  state and does not resurrect stale Bernie advice.
- **No unconfirmed write:** movement-profile-inspired tests assert that count or
  visual movement never becomes a write without backend evidence and staff
  confirmation.
- **Roster vs slot distinction:** synthetic fake rosters can test that Bernie
  distinguishes unavailable practitioner days from empty slot searches.
- **Large change caution:** synthetic large fake updates can test conservative
  copy, audit preservation, and no automatic semantic classification.

## Acceptance Criteria

- H-derived fixtures reference only committed H-series docs.
- H-derived fixtures include explicit privacy flags blocking raw trove access,
  semantic labels, provider calls, and raw identifiers.
- H-derived fixtures have a validator independent of the Bernie replay loader.
- Any future executable Bernie scenario must be authored from fake data with
  exact expected fields, not from aggregate H-series event classes.
- The H15 semantic labelling gate remains closed unless Yuri explicitly reviews
  and approves it.

## Open Questions

- Should H-series profiles later include exact synthetic field deltas, or remain
  high-level profile metadata?
- Do we want a second profile for deliberately unusual days, or is H21 enough
  until deterministic diary/Bernie work consumes this first bridge?
- What minimum fake-data scenario would best exercise stable-grid refresh
  behaviour without implying raw historical semantics?
