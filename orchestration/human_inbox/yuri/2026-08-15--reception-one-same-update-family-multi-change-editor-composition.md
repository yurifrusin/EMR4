# Yuri closeout — Reception One combined appointment-change editor

Date: 2026-08-15

Timestamp: 2026-08-15T04:08:00+10:00 (Australia/Brisbane)

Result: `raisa_reception_one_same_update_family_multi_change_editor_composition_pass`

Accepted reviewed source: `daed421954d65c159871585559f45caa32d95aee`

## Lay summary

Reception One now lets a receptionist prepare one appointment change that may
alter the doctor, start time and length together. The three controls are views
of one provisional draft: moving among them preserves the draft, while closing
it, selecting a different appointment, moving into the separate status action
or being interrupted throws the unfinished draft away.

Pressing Review does not save anything. It sends one complete proposal through
the existing safe appointment-update path and always stops at the familiar
confirmation dialog. Only the visible `Confirm & Save` button authorises the
change. Cancel, Escape, a clash, stale information or a network failure cannot
partly promote the draft. Reception One then rereads authoritative appointment
truth before showing the outcome.

This is the visible milestone that joins the simple four-key semantic console
to the previously proved all-or-nothing update kernel. Raisa can help shape the
proposal, but she receives neither a generic tool belt nor autonomous booking
authority.

## Technical summary

One local typed update draft now spans practitioner, local start and duration.
All three field-specific Review controls converge on one
`executeSelectedUpdateAction`, one `metaGridUpdateAppointmentDetails` bridge
and exactly one existing `handleMoveResize` proposal/confirm flow. The bridge
validates the combined interval and freshly reloads the active practitioner
directory before proposal. `forceConfirmation` makes even a safe proposal stop
at the existing dialog. Status remains a separate command family, and terminal
state comes only from fresh exact appointment/projection reconciliation.

No backend route, API/OpenAPI/GraphQL contract, database schema, migration,
event family or product-data access changed.

## Evidence

- 70 focused Reception One UI tests passed.
- 173 widened Reception One, parity, lower-level composition and API tests
  passed.
- 391 API Spine, latch, orchestrator and correction-register checks passed;
  after the final workflow incident, the complete 242-test register suite also
  passed.
- The canonical fast profile passed 196 tests, Ruff, compilation of 209
  maintained Python sources, Diary JavaScript syntax and Git whitespace.
- The final continuity/register/index/latch/Compass/baton packet passed all 356
  tests across nine modules.
- Fresh Gemini 3.6 Flash/high independently returned `pass` at unchanged clean
  source `daed421954d65c159871585559f45caa32d95aee` after the exact 173-test
  packet and static checks.

Evidence is authored-synthetic and route-intercepted; it is not a live-backend,
patient, provider or production claim.

## Issues exposed and resolved

AER-0312 through AER-0319 record eight contained workflow defects: DeepSeek's
fenced response, a guessed local module name, an invalid schema vocabulary
value, JavaScript files sent to Ruff, a detached verifier worktree and invalid
Continuity evidence-category links, one missed register aggregate fixture, and
an invalid latch enum with stale global baton fixtures. The mandatory controls
stopped each before it could contaminate acceptance. The final named, clean
verifier branch and corrected continuity/register state passed unchanged.

DeepSeek's test seed had negative net leverage after Sol recovery; Gemini's
independent veto had positive leverage. No useful native subagent package
remained in the tightly coupled implementation.

## Authority and revocation

This editor does not confer authority on Raisa or an external assistant. A
future delegated grant may be revoked to block future actions immediately.
Revocation does not silently undo an appointment already committed; that needs
a separately authorised cancellation and its own audit trail.

## Next

Run one provider-free read-only post-editor Compass orientation. It will take
stock of the now-composed Reception One command surface, Context Fabric/event
cues, the patient-channel foundation and the still-closed Yuri decisions, then
freeze the narrowest useful next tranche. It opens no new command, model,
channel, real-data or runtime authority itself.

Yuri attention required: no.
