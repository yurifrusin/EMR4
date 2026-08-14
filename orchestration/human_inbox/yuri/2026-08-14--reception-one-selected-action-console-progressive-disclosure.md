# Reception One selected-action-console progressive disclosure

Date: 2026-08-14

Timestamp: 2026-08-14T18:40:01+10:00 (Australia/Brisbane)

Status: accepted; programme continuing

## Lay summary

Reception One's four appointment actions now live in one compact console. A
selected appointment shows its current status, time, duration and practitioner,
then four simple action choices. The receptionist opens only the editor she
needs; closing it or moving to another choice makes no Diary change and throws
away any abandoned draft.

Once review or confirmation begins, the console is locked to that action and
appointment until fresh Diary truth returns. This prevents a half-finished
action being concealed or accidentally attached to another appointment.

Several requested changes are still intentionally handled as separate,
explicit confirmations. Nothing silently chains commands together, and the UI
does not pretend that a multi-field transaction exists before the backend has
proved one.

## Technical summary

- Presentation: one truth summary, four native buttons and zero-or-one shared
  editor.
- Safety: idle drafts clear on collapse, switch, interruption and fresh event
  replacement; busy reselection and action switching are blocked.
- Authority: all four existing renderers, bridges, request shapes and
  proposal/confirm paths are preserved.
- Accessibility: normal button tab order, `aria-expanded`/`aria-controls`, one
  active polite region, 44-pixel targets and responsive wrapping.
- Evidence: 23 new and 49 existing browser checks, one truth-parity case, 167
  exact broader tests, 196 canonical tests, five evidence checks and one fresh
  unchanged-candidate Gemini veto.
- Evidence label: exact UI command behavior is `route_intercepted_browser`, not
  a live backend or database claim.

## Parallel work and issues

The two native read-only audits materially improved the safety design. Gemini
provided the independent acceptance veto. DeepSeek's test-only contribution
needed Sol recovery after its bounded correction, so that lane had negative net
economy even though the recovered final tests are useful. No failed candidate
was admitted and no product defect remains open.

## Deliberately closed

No backend, API, database, event, watcher, compound command, patient/product
data, provider, credential, deployment, production, release, Pages or
protected-ref authority opened. All unrelated untracked files, including
`docs/branding/`, remain preserved.

## Place in Raisa and next work

This is an important minimum-app/maximum-intelligence step: Reception One can
grow in capability without growing into a wall of forms, while the kernel—not
the projection—continues to own committed meaning.

The next read-only tranche examines requests containing several changes. It
will map the existing update contract and freeze the proper atomicity and
confirmation boundary before any compound UI or command is considered. Until
that proof exists, automatic sequencing remains forbidden.

Yuri attention required: no.
