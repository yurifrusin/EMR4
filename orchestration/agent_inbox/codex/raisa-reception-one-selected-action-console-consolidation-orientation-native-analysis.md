# Native read-only analysis — Reception One selected-action console

Date: 2026-08-14

Timestamp: 2026-08-14T14:18:57+10:00 (Australia/Brisbane)

Source: `2b65cc8b639b6922c8f176a1d65ddc206fa6ba52`

Disposition: two native subagent packages completed read-only with no edits.

## Current-surface seam map

- `docs/diary/meta-grid.js` lines 85-118 hold one selected appointment and four
  independent action latches. They must not become one generic command state.
- Lines 2276-2336 own interruption and refresh-only reconciliation. Lines
  2884-2917 centrally apply exact fresh appointment truth.
- Lines 3294-3580 build four labelled editors, each with its own field,
  review button and polite atomic feedback. Lines 3626-3633 append all four
  sequentially.
- `docs/diary/meta-grid.css` lines 2942-2955 make every action consume 100 per
  cent width; lines 3070-3101 stack each panel again below 700 pixels.
- Existing terminal paths return focus to the action-specific control. The
  active editor therefore must remain mounted while the existing confirmation
  dialog is open.
- Status uses the status proposal/confirm family; time, duration and
  practitioner use their existing bridges and update proposal/confirm family.
  Presentation consolidation must not imply a combined transaction.

## Option analysis

Both packages recommend a deterministic four-button palette plus one inline
progressively disclosed editor. It keeps all actions visible without keeping
all editors visible. Native buttons avoid custom keyboard semantics, one live
region reduces announcement noise, and a single full-width editor contains
phone growth.

Four permanent panels, a dropdown, free-text-only intent, multiple-open
accordions and modal/drawer editors were rejected for density,
discoverability, ambiguity, concealed-draft or focus-layer reasons.

## Required implementation safeguards

- Start closed and focus the first action button without activating it.
- Action choice causes zero route calls.
- Switch only while idle and discard an abandoned draft.
- Disable switching while any action is busy, stale or interrupted.
- Preserve the active field through terminal confirmation and fresh
  reconciliation for feedback and focus return.
- Render the existing action-specific terminal outcome if the appointment
  leaves the projection.
- Keep the current four state objects, bridges, executors, route counts and
  command families unchanged.

Neither subagent received architecture acceptance, integration, Git,
protected-ref, provider, product-data or write authority.
