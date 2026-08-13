# CF-D2 event and cue behavior/transaction rehearsal — paired closeout

Date: 2026-08-13

Timestamp: 2026-08-13T20:54:23+10:00 (Australia/Brisbane)

Status: accepted; development continuing

## Lay summary

The small database mechanism behind CF-D2 now does the limited job we actually
want from it. It can remember that a change cue was classified, combine
adjacent compatible cues, advance only across an unbroken sequence, record a
delivery attempt and record the result of one fresh-read reconciliation. If a
step fails halfway through, PostgreSQL rolls the whole step back. Old owners,
conflicting duplicates, gaps and invalid results are refused without changing
the record.

This does **not** make the event stream the truth. The Diary/source remains the
truth; the cue merely tells Reception One that it may be useful to read that
truth again. Booking and other consequential commands still recheck the live
database and current authority before writing.

The first launcher command found a small import-path mistake before any
container or database was touched. That was repaired, and the fresh real
database rehearsal passed. We also removed three obsolete test assumptions
that treated an earlier pause as if it had to last forever.

## Technical summary

At exact source `f4bd8ca5ec0654f8be7b1d2d74b1aca444038ee9`, one cached PostgreSQL
16 container ran with no network, no host port and tmpfs-only storage. Six fixed
serial groups proved `admit_terminal`, `coalesce_pending`,
`advance_contiguous_checkpoint`, `record_dispatch_attempt` and
`record_reconciliation`. Evidence records three forced rollback equivalences,
eleven denial non-effects, five required uncontended relation-lock subsets and
verified exact-ID cleanup. All 64 hostile contract mutations, 215 combined
lineage/API/latch/Compass tests and the 193-test canonical fast profile pass.

The claim deliberately excludes concurrency, restart/crash/unknown commit,
watcher/source access, runtime wiring, operational retention, real delivery,
real authorisation/fresh reads, patient/product data, providers, product
commands, deployment, production and release.

## Place in Raisa and next work

This completes CF-D2's narrow serial database foundation: reliable ribbons for
payload-free refresh obligations, while source truth and conditional commands
remain the correctness kernel. The next tranche is a read-only post-CF-D2
Compass/baton orientation to identify the next already-planned Reception One
product direction. It grants no implementation authority by itself.

Yuri's attention is not required; standing uninterrupted-development authority
continues.
