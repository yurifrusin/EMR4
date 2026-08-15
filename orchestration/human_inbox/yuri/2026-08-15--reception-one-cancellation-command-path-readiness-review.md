# Reception One cancellation command-path readiness review

Date: 2026-08-15

Timestamp: 2026-08-15T11:33:02+10:00 (Australia/Brisbane)

Status: accepted; development continuing

## Lay summary

The cancellation path already has the right basic shape: Raisa prepares the
action, a staff member confirms it separately, the backend checks signed
evidence, prevents duplicate execution, records the decision and returns fresh
appointment truth.

Before cancellation becomes another Reception One action, one small foundation
piece is still needed. The final cancellation transaction must lock the
appointment and recheck that the staff member still has authority at the moment
of writing. We also should not reproduce the ordinary Diary's older fallback,
which turns cancellation into a status change and can lose the free-text reason.

This is not evidence that anyone can presently exploit the route. It is an
assurance gap we can now close deliberately before presenting the destructive
action through a second interface.

## Technical summary

At reviewed source `bb36e19c774eb1bc4ace8cafc6ae2b5c35bc8735`:

- dedicated proposal/confirm, raw compatibility delete, native status fallback
  and Reception One reach are fully inventoried;
- explicit confirmation, signed evidence, freshness, reason-code/text
  preservation, idempotency, audit and readback already pass on the dedicated
  family;
- no row lock or explicit in-transaction current-authority recheck exists in
  delete confirm;
- current differently-keyed coverage is serial, not overlapping concurrency;
- the status fallback omits `cancellation_reason`; and
- OpenAPI proposal/confirm path and payload shapes are not exact runtime shapes.

Seven focused checks, 188 cancellation/API tests and the 196-test canonical
profile passed. Gemini independently cleared ten challenges and reran all 188
tests at an unchanged clean candidate.

The required non-PHI closeout notification succeeded with request
`001a6d8a-b5fc-42fa-8a1d-385d6b0296e2`.

## Place in Raisa

This turns cancellation from a vaguely available route into a precisely mapped
next product capability. It preserves the principle established by Reception
One's status and rescheduling work: the visible projection never owns truth;
one backend transaction owns current authority, current Diary state,
confirmation, idempotency, audit and the committed result.

## Next

Development is continuing into the provider-free unmounted delete-confirm
conditional-command kernel architecture and admission rehearsal. It will not
change mounted routes, database/runtime behavior or the UI. Yuri attention is
not required.

Formal closeout: `docs/raisa-reception-one-cancellation-command-path-readiness-review-closeout.md`.
