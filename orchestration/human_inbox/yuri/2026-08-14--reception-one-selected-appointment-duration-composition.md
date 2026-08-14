# Reception One selected-appointment duration composition

Date: 2026-08-14

Timestamp: 2026-08-14T11:55:58+10:00 (Australia/Brisbane)

Status: accepted at candidate `f397a3706f3b870b8436eb3993bd90c6c0c742a8`

## Lay summary

Reception One can now change the length of one selected appointment without
becoming a separate booking system. Staff select a bounded duration, pass
through the ordinary Diary review, and see committed duration/end only after
the Diary has read current truth again. Date, start time, practitioner,
patient and all unrelated details remain fixed.

The work exposed and repaired two useful issues: completion could briefly be
announced before fresh truth was repainted, and one small-screen time-range
label had an encoding defect. Both are closed. Desktop, tablet and phone views
remain contained and keyboard Escape returns focus to the duration selector.

## Technical summary

- The new bridge supplies `deltaStart = 0`, computes only a bounded duration
  delta and calls existing `handleMoveResize` once with the same practitioner.
- The only command route remains the existing update proposal/confirm family;
  Reception One adds no fetch, raw PUT or second write path.
- Twelve paired route-intercepted traces agree between the conventional grid
  and Reception One across six success/failure outcomes and eight truth fields.
- The consolidated packet passes 118/118, the canonical fast profile 196/196,
  and Gemini's clean independent veto 68/68.
- DeepSeek's recovered test matrix and the native read-only subagent both
  produced genuine defect-finding value. DeepSeek's unusually large token use
  also shows why the permanent control weighs efficacy and packet economy, not
  worker occupancy alone.

## Deliberately closed

No live backend/database proof, patient or product data, cross-day move, full
edit, watcher/event runtime, provider/product call, new command family,
deployment, production, release, Pages or protected-ref movement is opened.
`docs/branding/` and every unrelated untracked file remain preserved.

## Place in the overall project

Status, start time and duration can now be composed in Reception One while the
same kernel and command path retain meaning. This is concrete evidence for the
projection-neutral architecture: the meta-grid and conventional grid can look
different while they remain answerable to one source of truth.

## Next planned tranche

Proceed to the narrowest remaining resize/move field: practitioner-only
reassignment at the same date, start and duration, through the same existing
proposal/confirm interaction and with the same fresh-truth and no-second-path
proofs.

Yuri attention required: no.
