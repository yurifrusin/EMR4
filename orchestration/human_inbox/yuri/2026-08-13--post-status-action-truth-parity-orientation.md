# Post-status-action truth-parity orientation

Date: 2026-08-13

Timestamp: 2026-08-13T23:21:48+10:00 (Australia/Brisbane)

Attention required: no

## Lay summary

Your reading is correct: this is the point at which Reception One becomes an
equal **reflection of truth** for a complete action, even though it is not yet
an equal collection of features.

The conventional grid and meta-grid can look and speak very differently. Both
now send the receptionist's intention to the same truth-owning kernel, and both
must accept the kernel's answer about whether anything was allowed, confirmed
and committed. They then redraw themselves from current Diary truth. Neither
screen gets to decide what happened.

That gives us the architectural basis for future modalities—conversation,
email, SMS, thin web, voice or a delegated assistant—without forcing any of
them to imitate a grid. They may express meaning differently, but the kernel
defines the meaning.

## Technical summary

Accepted source is `4b6a060c6b1aab42e1062c41d48d109f683abe00`.
Exact source inspection shows both clients converge on
`setAppointmentStatus`, the status proposal/confirm family and fresh Diary
reconciliation. The meta-grid bridge contains no network/confirm implementation
and GraphQL remains read-only.

The next tranche will turn this principle into a small conformance proof: two
renderer traces over the existing status family must agree on every kernel-
relevant state while being free to differ in layout, wording, focus and local
history. It will add no API, runtime object, database, new command, event,
provider or product data.

Other command families, representative staff sessions, the first patient
channel, another event family and operational watcher work remain at their
recorded gates.
