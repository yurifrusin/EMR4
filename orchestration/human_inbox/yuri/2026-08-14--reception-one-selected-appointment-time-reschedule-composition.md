# Reception One selected-appointment time reschedule

Date: 2026-08-14

Timestamp: 2026-08-14T09:50:00+10:00 (Australia/Brisbane)

Attention required: no

## Lay summary

Reception One can now move one selected appointment to another time on the same
day without taking on a separate scheduling power. The receptionist chooses a
15-minute-aligned time and reviews the proposal through the same guarded
interaction already used by the conventional Diary. The date, practitioner and
length of the appointment cannot be changed from this control.

The requested time is never presented as fact merely because it was selected.
If the request is cancelled, blocked, stale, fails or is interrupted, Reception
One reloads current truth and does not retain an optimistic change. If it
succeeds, the displayed time comes from the fresh appointment read after the
backend commit.

Parallel work was useful here. DeepSeek produced the independent browser-test
matrix; after integration it uncovered a real reconciliation race in which a
selected card could briefly retain its old time. That was repaired. Gemini then
reviewed the exact repaired candidate independently and passed it without
changing the candidate.

I have also made that consideration durable for future tranches. Every new,
restored or compacted task window must now carry an explicit assessment of
DeepSeek, Gemini and native subagents. A receipt fails if any lane is silently
ignored or if solo execution has neither useful parallel work nor a stated
serial constraint. This keeps worker use deliberate without forcing wasteful
parallelism.

## Technical summary

Accepted source is `d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a`.
The Reception One bridge validates an exact current appointment and `HH:MM`,
fixes `deltaDuration` at zero, retains the same practitioner and delegates once
to the existing `handleMoveResize` update proposal/confirm path. It implements
no API request or fallback write. GraphQL remains read-only; FastAPI, OpenAPI,
database, event and watcher surfaces did not change.

The evidence includes 12 paired conventional-grid/Reception One traces over
six outcomes, 11 dedicated browser cases, 144 native Diary cases, 85 API/latch
checks, the 193-test reviewed-candidate fast profile, the final 196-test
closeout profile and a fresh Gemini veto whose exact six-module packet passed
51/51. A packet estimate of 35 was corrected against
mechanical collection and preserved as AER-0305. No provider, patient/product
data, database/source runtime, deployment, release, Pages or protected ref was
touched.

## Next

I will continue within the same selected update/rescheduling direction with
the narrowest remaining field: duration only. It will reuse the identical
backend update proposal/confirm path while freezing date, start time,
practitioner and every unrelated field. This extends the truth-kernel pattern
without opening another command surface.
