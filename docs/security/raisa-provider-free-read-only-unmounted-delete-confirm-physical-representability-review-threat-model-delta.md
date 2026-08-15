# Threat-model delta — delete-confirm physical representability review

Date: 2026-08-15

Timestamp: 2026-08-15T13:34:23+10:00 (Australia/Brisbane)

Status: `frozen_read_only_review_boundary`

## Security objective

Prevent a read-only repository review from overstating current cancellation
authority, weakening destructive-command ordering or crossing protected
evidence, runtime, database or implementation boundaries.

## Added threats and controls

| Threat | Fail-closed control |
|---|---|
| Directory metadata exposes protected authoring paths | AER-0325 discards the first output; every later command names literal allowlisted paths and source expansion requires plan revision before opening. |
| Existing login/session rows are mistaken for a transaction-stable practice authority fence | The authority domain requires exact lockable current actor, practice, role and capability evidence; historical admission and route prechecks are insufficient. |
| Appointment timestamps are treated as state versions | Only a positive monotonic committed-state identity is admissible. |
| Existing raw delete/status fallback is treated as the dedicated kernel | Ingress families remain distinct; compatibility behavior cannot satisfy delete-confirm evidence or authority. |
| Replay discloses target or receipt before current authority | The ordered-atomic domain requires target non-disclosure and fresh authority before replay/conflict classification. |
| Public API compatibility is widened with private idempotency/session fields | Private correlation and public minimized response are assessed separately. |
| Nullable free-text cancellation reason is collapsed into absence or a structured code | Structured and free-text reason obligations are traced independently through appointment, audit and receipt. |
| Readback is treated as proof that commit occurred | Receipt completion is transaction evidence; readback is a later fresh-authorised reconciliation only. |
| A positive representability verdict silently selects migration or SQL design | The schema rejects design choices and fixes overall status to `implementation_not_admitted`. |
| Worker inventory becomes self-acceptance | DeepSeek may report line-bounded observations only; Sol owns verdicts and Gemini may independently veto material positive claims. |

## Residual risk and closed claims

The review cannot establish real PostgreSQL lock strength, transaction
isolation, migration/backfill safety, RLS behavior, concurrency, mounted-route
behavior, UI safety or production suitability. Those claims remain closed even
if every domain is representable with additive change.

No protected evidence, patient/product/clinical data, provider, database,
runtime, command, credential, network, deployment, release, Pages or protected
ref is authorized.
