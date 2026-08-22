# Native Harness useful-worker attempt — paired closeout

Date: 2026-08-22

Timestamp: 2026-08-22T13:30:09.9126535+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

The first genuinely useful DeepSeek job through its native Harness did not
produce the runbook file we wanted. It did get substantially further than the
earlier Harness failures: the Harness started correctly, contacted DeepSeek
once, and DeepSeek selected the permitted edit action. The edit did not change
the file, however, and the controlled turn ended rather than being allowed to
make another request.

The safety machinery behaved properly. There was no retry, no fallback, no
candidate to smuggle through, no process left running and no raw model or
credential material retained. This is therefore a useful negative result, but
not yet the useful worker capability we were seeking.

The next step is a provider-free diagnosis of the narrow tool-result/conclusion
joint. That should tell us why the edit was not accepted and make the next
occupied attempt more informative without spending another DeepSeek request.

## Technical summary

- Result: `native_harness_useful_worker_failed_closed_no_candidate`.
- Native process: 1; exit: 1; expected HMR events: 2/2.
- Broker: one request started/completed, zero provider failures, one later
  request rejected at the fixed ceiling.
- Runner: one request, `edit` tool call/result 1/1, conclusion false,
  `turn_kind: error`.
- Candidate: zero changed paths, not admitted, not retained, not adopted.
- Retry/resume/fallback/auxiliary model: 0/0/0/0/0.
- Cleanup: Harness absent, broker absent, disposable root absent, raw sensitive
  artifacts absent.
- Deterministic post-terminal validation: passed.

Issues exposed and resolved before launch included machine binding of the
validation runner's hashed Git ledger, an evidence-only checkpoint descendant,
tranche-owned exact cleanup and persisted checkpoint readback. The remaining
issue is the unclassified tool-result/post-execute outcome.

Still deliberately closed: ordinary-practice activation, feature/allowlist/
route changes, generic `Arrived`, grammar/client/waiting-area changes, product
or patient data, live runtime, production, deployment, release, Pages and
protected refs.

Next tranche:
`deepseek-native-harness-provider-free-tool-result-conclusion-coordinate-diagnostic-recovery`.
