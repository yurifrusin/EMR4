# Bernie UI Derived-State Safe-Copy Matrix

Date: 2026-07-10

Status: Sprint 291 docs/tests-only checkpoint. This matrix records the copy
contract already projected by the display-only `BernieUiViewModel`; it does not
change Diary JavaScript, backend routes, confirm payloads, or appointment write
behaviour.

| State | Permitted copy posture | Required recovery / safety posture |
|---|---|---|
| Instruction waiting | Waiting for the next session event | No confirm or success copy |
| Clarification or ambiguous identity | Resolve the blocking detail | No confirm or success copy |
| Candidate times available | Candidate times are available for staff review | Staff selects a candidate; no booking claim |
| Proposal ready | No appointment has been made yet | Staff review or choose another time; confirm may be available only when the existing evidence gate is ready |
| Confirm pressed | No appointment has been made yet | Await signed confirmation submission; no success copy |
| Awaiting backend | No appointment has been made yet | Await the backend result; route-intercepted evidence only |
| Backend-confirmed session | Appointment booked after backend confirmation | Confirm hidden; success is permitted only in this state |
| Stale or rejected proposal | Refresh or retry before booking | Refresh, retry, or edit; no success copy |
| No suitable time found | No suitable time in that searched window | Offer next options; no booking claim |

The canonical machine-readable matrix is
`docs/bernie-ui-derived-state-safe-copy-matrix.json`. Its rows are tied to the
existing `tests/fixtures/bernie_ui_view_model/cases.json` fixtures and validated
against their copy mode, confirmation state, and confirm/success flags.

The matrix maintains five non-negotiable rules:

- success copy is reserved for `confirmation_state=confirmed`;
- pre-confirm copy does not say booked, confirmed, or that an appointment has
  been made;
- copy is display-only, never write authority;
- route-intercepted evidence is not live backend or provider evidence; and
- ordinary staff copy excludes raw identifiers, snake_case codes, and generic
  not-found wording.

Ariadne S3 classified this planned changed-path set as Green and `allowed`.
The human outcome matches: the sprint is docs/tests-only. This is an advisory
calibration record, not an enforcement action.

The next proposed step is Sprint 292, a draft-only D5 next-step approval
payload. D5 runtime remains closed.
