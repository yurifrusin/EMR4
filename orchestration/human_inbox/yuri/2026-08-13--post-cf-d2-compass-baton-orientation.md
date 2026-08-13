# Post-CF-D2 programme orientation

Date: 2026-08-13

Timestamp: 2026-08-13T21:25:00+10:00 (Australia/Brisbane)

Attention required: no

## Lay summary

The durability foundation has now done enough for us to return to visible
Reception One work. We do not need to build or operate a watcher first because
current database truth and command-time checks—not cue delivery—remain the
safety mechanism.

The next piece will let a receptionist change the status of one selected
appointment from inside Reception One. Today Reception One can show and select
the appointment, while the ordinary Diary already has the secure status-change
flow. We will join those two existing pieces so staff do not have to leave the
focused projection merely to mark an arrival, consultation or other existing
status.

This is a composition, not a new power. The same backend will still check the
current user and current Diary, show warnings or confirmation when required,
record the audit and receipt, and reload the result.

## Technical summary

The accepted source is `edba8f57380a48fd98decc332608349f2d9012e6`.
Repository evidence shows that `meta-grid.js` renders appointment status and
selection but `EMR4DiaryMetaGridBridge` has no status action. The ordinary
Diary's accepted `setAppointmentStatus` path already converges on canonical
status proposal/confirm with no raw fallback.

The selected tranche is limited to one current selected appointment, the
existing status vocabulary, one bridge into that existing interaction,
modeless busy/cancel/blocked/stale/success feedback, fresh reload and
responsive keyboard/focus/interruption evidence. It adds no backend/API/schema/
database change, new command, event runtime or provider.

The focused orientation/UI/foundation/latch/baton/Compass packet passes 91
tests and the canonical 193-test fast profile passes. Two mechanical
test/latch wording defects were corrected without changing the direction or
any product file.

## Deliberately still closed

Representative staff sessions still need your cohort and reopening. The first
external patient channel still has identity, provider, recovery and hosting
choices. Another event family still needs an explicit value/family decision.
Operational CF-D2 watcher, restart/unknown-commit, product/patient data,
providers, new commands, deployment, production, release, Pages and protected
refs remain closed.

## Next

Proceed immediately to the provider-free Reception One selected-appointment
status-action composition. Your attention is not required.
