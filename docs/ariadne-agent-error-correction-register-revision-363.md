# Ariadne agent error and correction register — revision 363

Date: 2026-08-18

Timestamp: 2026-08-18T07:34:51+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 363 adds AER-0414. The first terminal latch transition repeated the
known AER-0390 pattern: status changed to `complete`, but
`resume_after_compaction` remained true and `next_executable_stage` remained
non-null. Both pure latch validators failed closed before commit or push.

The correction constructs the terminal branch from the validator contract:
resume false, next stage null, no user attention and terminal permission true.
The already-recorded successor remains in the Current Baton, not in a completed
operation's executable-stage field. The fresh complete packet then exposed the
new explicit recurrence assertion still present in the residual recurrence
list; the correction applies AER-0410's paired exclusion rule and reruns the
complete packet.

## Population

- incidents: 414;
- corrected or explicitly contained: 414;
- open: 0;
- latest id: `AER-0414`.

No product, data, provider, deployment or protected-ref authority changed.
