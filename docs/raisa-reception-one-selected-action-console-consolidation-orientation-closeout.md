# Reception One selected-action-console consolidation orientation closeout

Date: 2026-08-14

Timestamp: 2026-08-14T14:29:56+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `2d602cfd822235977676bfe9ee8d8dc0a14714fe`

Result: `raisa_reception_one_selected_action_console_consolidation_orientation_pass`

## Lay summary

Reception One now has a clear direction for keeping appointment actions small
and calm as its abilities grow. Rather than showing four complete editing
panels at once, it will show four plain choices—status, time, duration and
practitioner—and open only the one the receptionist chooses.

This preserves discoverability without turning the bottom of the projection
into an ever-growing form. Choosing a field does nothing to the Diary. Staff
still enter a provisional value, review it through the familiar confirmation
flow and see committed meaning only after current Diary truth is read again.

## Technical result

The selected architecture is
`deterministic_action_palette_with_single_panel_progressive_disclosure`:

- one patient-minimized current-truth summary;
- four native action buttons with ordinary tab order, `aria-expanded` and
  `aria-controls`;
- no editor open initially and at most one existing field editor visible;
- idle-only switching that discards an outgoing unsubmitted draft;
- no switching while any action is busy, stale, interrupted or in
  confirmation;
- one active polite live region and field-specific focus return; and
- exact fresh reconciliation before terminal truth is displayed.

The palette is presentation state only. Status retains
`metaGridSetAppointmentStatus` and the status proposal/confirm family. Time,
duration and practitioner retain their current bridges through
`handleMoveResize` and the update proposal/confirm family. The design forbids a
generic command dispatcher, compound edit or combined transaction.

## Alternatives rejected

- Four always-visible panels remain clear but grow linearly and create four
  apparent provisional surfaces.
- A dropdown is compact but hides frequent actions.
- Free-text-only intent adds ambiguity at a command-sensitive boundary.
- Multiple-open accordions permit concealed drafts.
- Modal or drawer editors compete with the existing confirmation dialog.
- A generic multi-field editor would blur distinct command authorities.

The architecture stays intent-compatible: a future deterministically admitted
request may open an editor, but it may never propose, confirm or combine a
command.

## Parallelism efficacy: planned versus actual

- **DeepSeek V4 Flash/high:** explicitly assessed and declined. The tranche
  contained product-meaning and accessibility judgment, not a stable
  mechanical artifact, and the preceding test package had negative economy.
  Reassess a tightly capped browser-test package in the implementation
  descendant.
- **Native subagents:** two read-only packages completed concurrently. The
  surface audit identified exact state, focus, interruption, responsive and
  command-authority seams. The option analysis independently recommended the
  same four-button/single-editor hybrid and clarified rejected alternatives.
  Positive leverage with no edits.
- **Gemini 3.6 Flash/high:** one fresh exact-candidate veto returned `pass`.
  All seven manifest commands passed, including exactly 77 tests; HEAD and the
  worktree remained unchanged and clean.
- **Sol:** retained architecture selection, reconciliation, deterministic
  admission, acceptance, Continuity and Git authority.

This is the intended permanent allocation behavior: every lane was evaluated,
only the useful packages ran, and non-use survived in fail-closed receipts
rather than depending on conversational memory.

## Verification

- Six dedicated typed architecture tests pass.
- The exact Gemini packet passes 77/77 across the orientation, active-latch
  and orchestrator-preflight modules.
- Gemini's seven-command manifest, Ruff and Git whitespace all pass at
  unchanged clean candidate
  `2d602cfd822235977676bfe9ee8d8dc0a14714fe`.
- The canonical fast profile passes 196/196 plus Ruff, compilation of 209
  maintained Python sources, Diary JavaScript syntax and Git whitespace.
- The candidate changes no Diary HTML, CSS, JavaScript, backend or API Spine
  product source.

## Next tranche

The next safe descendant is
`raisa_reception_one_selected_action_console_progressive_disclosure_composition`.
It may change only the Reception One presentation layer and affected
provider-free tests: add the presentation enum, compact truth summary, native
button palette and one shared editor region while reusing every existing
field-specific renderer, executor, bridge, route and confirmation flow.

It must prove one-or-zero editor, zero routes on palette activity, discarded
abandoned drafts, four-way busy exclusion, interruption teardown, exact fresh
reconciliation, unchanged paired command traces, native keyboard and
screen-reader semantics, 44-pixel targets and no desktop/tablet/phone overflow.

## Claim boundary

This proves repository-local provider-free read-only architecture and
independent source review. It does not prove implemented UI, representative
usability, live product data, backend/database behavior, deployed or
production operation. Product/patient data, provider use, new commands/routes,
deployment, release, Pages and protected-ref movement remain closed.

Yuri attention required: no.
