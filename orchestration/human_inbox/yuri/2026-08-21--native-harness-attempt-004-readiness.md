# DeepSeek Native Harness Attempt 004 — Readiness Result

Date: 2026-08-21
Timestamp: 2026-08-21T11:59:13.0977106+10:00

## Lay summary

Attempt 004 is ready for one carefully bounded run. Nothing was sent to
DeepSeek during this check. The earlier three attempts are locked as consumed,
the new attempt has its own identity, and the exact Harness preset, task,
broker limits, diagnostic record and cleanup sequence all agree.

The key clockwork improvement is active: the reading used to make this decision
cannot be reused. The actual run must take a fresh reading after closeout, so
the work order and lease are derived from the current mechanism rather than
remembered or copied manually.

## Technical summary

- candidate: `0ef8ab1317e21152c9ee7c331801183250361745`;
- decision: `ready_for_one_separately_checkpointed_occupied_attempt_004`;
- focused tests: `32/32` passed;
- exact Harness: `@deepseek-ai/dsh` `0.1.0-rc.7`;
- preset/tools: `emr4-bounded-worker`; `edit`, `glob`, `read`;
- attempt root and twelve future outputs: absent;
- readiness clock: generation `gen-ffb51b…`, lease 103, read-only/non-reusable;
- Harness/model/provider/network actions in readiness: zero;
- future authority: one process/session/turn, at most one provider request and
  one tool call, zero retry/resume/fallback/second worker.

The first rehydration receipt correctly rejected a caller-authored Git object
and the corrected receipt passed with zero manual IDs. A new timestamp guard
also converts the Brisbane Date/Timestamp rule into a test rather than a memory
obligation.

No EMR4 product behavior, data, ordinary-practice admission, deployment, Pages
or protected ref changed.
