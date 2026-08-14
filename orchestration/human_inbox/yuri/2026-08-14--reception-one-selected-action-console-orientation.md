# Reception One selected-action-console orientation

Date: 2026-08-14

Timestamp: 2026-08-14T14:29:56+10:00 (Australia/Brisbane)

Status: accepted; programme continuing

## Lay summary

Reception One's four proven appointment actions will no longer grow as four
large forms stacked beneath every selected appointment. The accepted direction
is one compact action console: four clear choices remain visible, but only the
chosen editor opens.

This keeps the interface learnable for reception staff, much lighter on phones
and tablets, and compatible with the longer-term conversational direction. A
future request such as “change the time” may open the time editor, but it will
not secretly perform the change. The ordinary review and fresh-Diary-truth
rules remain decisive.

## Technical summary

- Selected pattern: deterministic native-button palette with single-panel
  progressive disclosure.
- Initial state: no editor open; maximum visible editors: one.
- Switching: idle only, discards the outgoing unsubmitted draft and calls no
  route.
- Busy/interrupted state: switching disabled; current reconciliation gate
  retained.
- Authority: status and update proposal/confirm families remain distinct; no
  generic dispatcher or compound edit.
- Accessibility: ordinary button tab order, `aria-expanded`/`aria-controls`,
  one polite live region, existing dialog Escape/focus ownership and 44-pixel
  responsive targets.
- Evidence: 6 dedicated tests, 196 canonical tests and one fresh Gemini veto
  with 77/77 exact tests at unchanged clean candidate.

## Parallel work

Two native read-only agents supplied positive-leverage surface and option
analyses. Gemini supplied the fresh independent veto. DeepSeek was explicitly
declined because this tranche had no stable mechanical package and its use
would have repeated the preceding tranche's negative economy; it will be
reassessed for a tightly capped browser-test artifact in the implementation.

## Deliberately closed

No product UI was changed in this orientation. No backend, route, schema,
database, event, watcher, patient/product data, provider, deployment, release,
Pages or protected-ref authority opened.

## Place in Raisa and next work

The architecture protects the minimum-app/maximum-intelligence direction: one
calm projection can offer growing capability without becoming conventional
form middleware. The next tranche implements only this presentation shell over
the four already-proven actions and reruns their full truth and command
evidence.

Yuri attention required: no.
