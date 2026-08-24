# Historical-derived check-in adapter-test utility gap review

Date: 2026-08-24

Timestamp: 2026-08-24T15:12:00.0000000+10:00 (Australia/Brisbane)

Decision: `accepted_read_only_utility_gap_review`

## Conclusion

The trove-derived candidate supplied traceable provenance to one adapter test, but added zero incremental adapter branches and discovered zero new check-in business rules. Its canonical digest determined one-way synthetic identities, idempotency material and evidence material. Its nineteen-minute span shifted the injected synthetic clock. No event count, minute count, event-kind count or slot count independently changed the appointment state, authority, waiting-area, evidence, idempotency, transaction or readback branch.

The occupied path was the already-covered `Booked`, no-waiting-area success. The accepted product suite already covers `Booked` and `Confirmed`, none/assign/preserve waiting areas, exact replay, fail-closed authority/evidence/freshness/idempotency paths and precommit/unknown-outcome failures.

## Structural influence reading

| Structural measurement | Value | Utility |
|---|---:|---|
| `event_count` | 6 | `digest_only_provenance` |
| `distinct_relative_minutes` | 4 | `digest_only_provenance` |
| `relative_minute_span` | 19 | `synthetic_time_parameter_only` |
| `distinct_event_kinds` | 2 | `digest_only_provenance` |
| `synthetic_subject_slots` | 1 | `digest_only_provenance` |
| `resource_slots` | 1 | `digest_only_provenance` |

## Honest gap

The missing utility is time-ordered composition: an initial synthetic context, an intervening state/authority/area/idempotency or transaction change, and the resulting adapter stop, replay, success or outcome-unknown reading. Repeating more isolated atomic branches would mostly duplicate existing coverage.

The successor is therefore limited to three authored-synthetic axis families and may use a minimal pairwise set. The contract does not claim those axes occurred in the historical trove and authorises no further historical access or execution by itself.

## Deterministic boundary

Rejected 69 hostile contract mutations with zero escape. Only ten exact tracked inputs were admitted. No `local_data`, fixture control, archive, provider, model, network, product runtime, database, route invocation or ordinary-practice surface was opened.
