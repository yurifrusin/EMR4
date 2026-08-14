# Reception One selected-action-console consolidation architecture

Date: 2026-08-14

Timestamp: 2026-08-14T14:18:57+10:00 (Australia/Brisbane)

Status: `selected_for_next_implementation`

Source inspected: `2b65cc8b639b6922c8f176a1d65ddc206fa6ba52`

Decision: `deterministic_action_palette_with_single_panel_progressive_disclosure`

## Decision

Reception One should present one compact `Appointment actions` console for a
selected current appointment. Its collapsed state shows a patient-minimized
fresh-truth summary and four native buttons:

- Change status
- Change time
- Change duration
- Change practitioner

The console starts with no editor open. Activating a button performs no
proposal or command; it only sets a presentation enum and opens exactly one
existing field-specific editor beneath the palette. The button reports its
state with `aria-expanded` and references the shared editor region with
`aria-controls`. Native buttons preserve ordinary Tab and Shift+Tab behavior;
the implementation adds no custom tablist, toolbar or roving-tabindex model.

This is progressive disclosure with intent-compatible activation. A future
deterministically admitted conversation intent may open the same field editor,
but neither the next implementation nor this architecture lets language issue,
confirm or combine a command.

## Truth and authority layers

| Layer | Owns | Must not own |
|---|---|---|
| Console summary | Fresh selected projection values for status, time, duration and practitioner | Requested values, command admission or committed claims |
| Action palette | One presentation-only `activeSelectedAction` enum | Proposal, payload, route, confirmation or generic update dispatch |
| Field editor | Existing field-specific provisional input and feedback | Another field's draft or a compound edit |
| Existing bridge | Exact current read, field-specific admission and delegation | A second command path |
| Backend command family | Authority, warnings, blocks, confirmation, idempotency, audit and atomic write | Client presentation state |
| Fresh reconciliation | The displayed terminal truth | Optimistic requested values |

Status remains mapped to `metaGridSetAppointmentStatus` and the existing
status proposal/confirm family. Time, duration and practitioner retain their
current bridges and delegate through `handleMoveResize` to the existing update
proposal/confirm family. The palette is not a combined transaction or generic
appointment-update API.

## State contract

`activeSelectedAction` is presentation-only and is exactly one of `null`,
`status`, `time`, `duration` or `practitioner`.

1. Selecting an appointment resets it to `null`, exposes the four buttons and
   focuses the first action button without activating it.
2. Activating an idle action opens only that editor and moves focus to its
   current field control.
3. Activating the already-open action collapses it and returns focus to its
   palette button.
4. Switching while idle discards the outgoing unsubmitted draft, announces
   that no Diary change occurred, resets that field state from current truth
   and opens the requested editor.
5. Switching or collapsing is disabled while any field action is busy, while
   the confirmation dialog owns focus, or while freshness is stale or
   reconciliation is required.
6. The active editor stays mounted during confirmation so existing Escape,
   cancellation and deterministic focus return remain valid.
7. After any terminal outcome, exact fresh reconciliation remains mandatory.
   The same action stays active so its one polite live result and field focus
   remain available.
8. If the appointment leaves the projection, the editor is replaced by its
   existing action-specific terminal outcome; no requested value is shown as
   current truth.
9. Blur or visibility interruption retains the existing refresh-only
   reconciliation gate and clears any unsubmitted draft before another action
   may open.

The four existing action-state objects and field-specific execute functions
remain independent. The implementation must not replace them with one generic
command object.

## Layout and accessibility

- The palette wraps without horizontal scrolling and supplies at least
  44-by-44 CSS-pixel targets at desktop, tablet and phone widths.
- The truth summary precedes the palette in reading order and contains only
  the selected appointment's current status, start/end, duration and
  practitioner display.
- The shared editor region has one stable labelled heading. Only the active
  field's existing control, review button and polite atomic feedback region
  are present.
- No modal or drawer is added. The existing proposal/confirmation dialog
  remains the only focus-contained command review layer.
- Workspace Escape keeps its current meaning: it returns to the ordinary
  Diary except while the existing confirmation dialog owns Escape.
- On phones the palette may use two columns or one column, followed by one
  full-width editor. It must never stack four full editors.

## Rejected alternatives

- **Four always-visible panels:** discoverable but grows linearly, creates four
  apparent draft surfaces and already consumes four full rows.
- **Single dropdown:** compact but makes frequent actions less discoverable
  and adds an extra selection step.
- **Free-text-only intent:** strategically compatible but currently adds
  ambiguity and interpretation at a safety-sensitive boundary.
- **Multiple-open accordion:** permits concealed or competing provisional
  drafts.
- **Modal or drawer per field:** competes with the existing confirmation
  dialog and complicates focus, interruption and small-screen layering.
- **Generic multi-field editor or dispatcher:** would blur the distinct status
  and update authorities and invite compound commands.

## Next implementation tranche

The next safe tranche is
`raisa_reception_one_selected_action_console_progressive_disclosure_composition`.
It is limited to `docs/diary/meta-grid.js`, `docs/diary/meta-grid.css`, the
necessary Diary asset cache reference and affected provider-free tests.

It may add the presentation enum, truth summary, palette and one shared editor
region; reuse the four existing renderers within that region; and adjust tests
to open the required action before using its existing control. It may not
change a bridge, executor, request payload, route count, confirmation flow,
backend, API Spine, database or command authority.

Acceptance must prove zero routes on open/collapse/switch, one-or-zero editor,
discarded inactive drafts, four-way busy exclusion, dialog focus/Escape,
interruption teardown, fresh rebind/removal, unchanged paired command traces,
one live region, native keyboard semantics, 44-pixel targets and no overflow
at desktop, tablet and phone widths.

## Claim boundary

This is repository-local, provider-free, read-only architecture evidence. It
does not prove implemented UI behavior, usability, real-user operation,
product data, live backend/database behavior, provider behavior, deployment or
production readiness.
