# Arrival/check-in command-family convergence review — lay and technical summary

Date: 2026-08-18

Timestamp: 2026-08-18T07:20:15+10:00 (Australia/Brisbane)

Status: accepted

Yuri attention required: no

## Lay summary

Raisa now has a clear answer to what “check this patient in” should mean.
Check-in will be its own authoritative command, not merely another way of
setting an appointment label to `Arrived`. That distinction lets Raisa prove
who checked the patient in, that the appointment was in a check-in-ready state,
that any waiting area was compatible, that confirmation was used only once,
and that the audit, event and receipt all describe the same committed act.

The existing general status mechanism remains useful for other appointment
changes. When the product is eventually switched, both first-party Diary views
must move to dedicated check-in together, while ordinary `Arrived` is removed
from general status at that same boundary. That avoids a gap and avoids two
competing “correct” ways to perform the same check-in.

Nothing was turned on for real use. The specialist A5.1 path is still switched
off and restricted to its existing synthetic-development boundary. No patient
data, live database, provider, route, UI or deployment was opened.

## Technical summary

The accepted matrix compares general status, waiting-area-only proposals and
A5.1 check-in across request, role, admission, signed evidence, freshness,
state transition, waiting-area policy, transaction, audit, event, replay,
receipt, readback, consumers and static action contracts.

Dedicated check-in is selected because it adds exact `Booked|Confirmed ->
Arrived` policy, Receptionist authority, durable one-use confirmation evidence,
same-practice/same-location waiting-area checks and a dedicated committed event.
The reusable deterministic kernel is explicitly separated from the
Rayleen-named feature flag and authored-synthetic practice allowlist.

Eleven new checks, 118 focused static/API checks, the register/compact-baton
packet, the 200-test canonical fast profile and one seven-command Gemini 3.7
Flash/high veto passed. The known typed-path endpoint-coverage false positive
remains recorded, not silently repaired.

The closeout also caught stale Compass/baton fixtures, a handover size-limit
breach and one invalid first terminal-latch draft. AER-0413/AER-0414 record the
narrow harness-only repairs; AER-0415 corrects one stale evidence count found
on successor rehydration, and AER-0416 corrects the schema/test defects caught
while validating that repair. Product code and the accepted check-in decision
did not change.

The next tranche is the provider-free unmounted canonical check-in product-
adapter extraction rehearsal. It will extract the reusable kernel and test it
without changing any mounted route, enabling any practice, changing general
status, registering a UI action or wiring either client. DeepSeek will be
reassessed for that bounded separable implementation package; Gemini remains
the independent veto lane. No user-attention fork is present.
