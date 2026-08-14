# Reception One selected-action-console progressive-disclosure composition threat-model delta

Date: 2026-08-14

Timestamp: 2026-08-14T17:06:54+10:00 (Australia/Brisbane)

Status: `frozen`

Parent authority: accepted selected-action-console orientation at exact source
`2d602cfd822235977676bfe9ee8d8dc0a14714fe` and closeout commit
`67f203097507d5f8c976f716ff37f720f4ea6b73`

## Changed surface

The native Diary presentation may add one action enum, a current-truth summary,
four native buttons and one shared editor region. Existing field-specific
renderers move into that region without changing their command behavior.

## Threats and required controls

| Threat | Required control |
|---|---|
| Palette activation becomes a command | Button handlers may set presentation state only; open, collapse and switch must produce zero API routes. |
| Consolidation introduces a generic dispatcher | Keep four action states, renderers, executors and bridge methods; map each button explicitly and construct no generic command object. |
| A multi-field request becomes several silent commits | Represent no executable multi-field change set and add no automatic sequential execution. Separate independently confirmed actions remain the only current behavior. |
| The UI implies unproved atomic compound update | Present only one field editor and one field-specific review at a time; make no compound transaction claim. |
| A hidden provisional draft later executes | Permit only one editor and reset the outgoing idle action state before switching or collapsing. |
| Switching during proposal or confirmation unmounts the focus owner | Disable every palette transition while any action is busy or the existing confirmation dialog is present; keep the active renderer mounted. |
| Selecting another appointment erases an in-flight latch | Ignore appointment-card selection while any field action is busy or the confirmation dialog owns focus. |
| Stale or interrupted presentation reopens command affordance | Disable the palette when interrupted, stale or in reconciliation and retain the existing exact refresh-only gate. |
| A committed-event refresh resurrects an idle draft against changed truth | Reset idle action drafts when fresh external projection replacement changes the selected appointment. |
| Requested values contaminate the truth summary | Build the summary solely from the selected fresh projection, never action-state requested fields. |
| Several live regions announce competing outcomes | Render only the active field's existing polite atomic live region. |
| Custom keyboard semantics become inaccessible | Use native buttons, normal tab order, `aria-expanded` and `aria-controls`; add no roving focus. |
| Appointment removal strands focus or displays provisional truth | Render the active action's existing committed-removal outcome and return focus safely to the canvas when its field no longer exists. |
| Responsive consolidation still overflows | Require wrapping 44-pixel palette targets and one full-width editor at desktop, tablet and phone widths. |
| Cache skew serves incompatible JavaScript and CSS | Advance both exact Diary asset query references with the product-source change. |
| Presentation change broadens API authority | Run API Spine invariants and source/route guards; no backend, OpenAPI, GraphQL, request or route edit is admitted. |

## Residual boundary

This tranche does not establish a compound-update transaction, conversational
command execution, representative usability, live backend/database behavior,
product-data operation, deployment or production readiness. A future atomic
multi-field proposal requires a separately frozen backend admission,
confirmation, idempotency, conflict and rollback proof.
