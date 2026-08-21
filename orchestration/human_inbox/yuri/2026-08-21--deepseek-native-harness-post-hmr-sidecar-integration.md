# Native Harness sidecar and broker-zero integration

Date: 2026-08-21

Yuri attention required: `no`

## Lay summary

The control mechanism now has two independent gauges rather than trusting one
ambiguous failure message. The future runner can record which of seven fixed
steps it had reached, but the orchestrator calls that failure “before the
request” only when a separate broker gauge also reads exactly zero. The model
cannot invent either reading or substitute descriptive prose.

This is a substantial step toward useful DeepSeek workers: it makes the next
failure localisable and prevents the system from overclaiming where a request
failed. It is still a provider-free construction test, not yet evidence that
DeepSeek completed Raisa work.

## Technical summary

- Accepted candidate:
  `3a16f5a00e50259caf993decc67719173348dc0a`.
- Future runner: exact accepted attempt-005 source plus one closed sidecar
  integration; accepted runner and consumed attempts remain immutable.
- Controller rule: exact sidecar + five broker counters at zero permits
  `post_hmr_pre_request_failure`; any non-zero counter is unresolved; bad or
  absent sidecar preserves the generic terminal; bad broker evidence rejects.
- Verification: 24 focused tests and 125 inherited tests pass, plus generator
  drift check, Ruff and compilation. Prohibited process/request counts are
  zero.
- Five corrected workflow observations will enter the next register revision,
  including the newly observed danger of manually expanding a short Git hash
  in prose instead of copying a machine snapshot, and a rejected clockwork
  forward reference to its own not-yet-generated register output and the
  initially omitted pre-existing human revision intake note.

## Deliberately closed

No Node/Harness/broker/worker/model/provider execution, occupied attempt,
retry, raw stream, product/configuration/API/database change, ordinary-practice
enablement, patient or clinical data, production, deployment, release, Pages
or protected-ref movement is authorised or claimed.

## Next

The engine continues with a provider-free materialisation and controller-
terminal fixture rehearsal. That will assemble the exact runner, helper and
controller gears in a disposable future-attempt tree before any occupied
native Harness attempt is considered.
