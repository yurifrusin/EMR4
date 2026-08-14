# Reception One multi-change request atomicity orientation

Date: 2026-08-14

Timestamp: 2026-08-14T21:47:54+10:00 (Australia/Brisbane)

Result: `raisa_reception_one_multi_change_request_atomicity_orientation_pass`

Accepted reviewed source: `fbb7ffb46e041bbfc193ff3a76b2f970c06dee58`

## Lay summary

The four large Reception One buttons are now formally understood as a small,
safe vocabulary for a receptionist—not as controls that Raisa can press.
Raisa, Siri, email, SMS or another chatbot may eventually say which action a
request appears to mean, but only as a provisional typed candidate.

Time, duration and practitioner changes can safely belong to one existing
appointment-update proposal and one human confirmation. Status belongs to a
different command family, so a status-plus-time request cannot yet be called
atomic or run as a hidden sequence.

Your clarification about patients fits the previously accepted patient
foundation: the human confirmer of a new booking may eventually be the patient,
including through a narrow, revocable delegation to Siri or another service.
The channel carries the patient's request; it does not become the patient or
inherit unrestricted command authority. That live identity/delegation layer is
not implemented here.

## Technical summary

The accepted contract selects typed inert `AppointmentActionCandidate` input,
deterministic single-target/allowlist/current-authority admission, one
same-update-family proposal/confirmation, distinct status-family handling and
non-executable cross-family review. Events remain refresh hints; the kernel
rechecks current source truth, authority and command evidence.

The source proves combined date/time/duration success and practitioner-state
revalidation denial. It does not yet prove successful practitioner/time/
duration confirmation together, exact replay or injected rollback. Those are
the next test target.

The exact independent packet passed 457 tests. Gemini returned `pass` at an
unchanged clean candidate. AER-0308 corrects a bounded command-count/Ruff wording
error in its prose; AER-0306 and AER-0307 keep both native analyses rejected and
unused. No protected content enters the result.

## Deliberately closed

No UI, API, database, watcher, provider, patient channel, identity/delegation
runtime, patient/product data, deployment, production, release, Pages or
protected ref was opened.

## Place in Raisa

This is the vocabulary-and-authority bridge between the compact Reception One
console and future conversational or channel-neutral interaction. It lets Raisa
understand richer requests without giving the model a generic tool belt.

## Next tranche

Proceed with the provider-free same-update-family multi-change kernel rehearsal:
one authored-synthetic time/duration/practitioner update through the existing
proposal/confirm path, with stale truth, conflict, idempotency, audit and
rollback checks and no new UI.

Yuri attention required: no.
