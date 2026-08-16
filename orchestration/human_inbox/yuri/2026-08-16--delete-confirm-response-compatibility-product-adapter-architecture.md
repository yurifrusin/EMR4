# Delete-confirm response compatibility and product-adapter architecture

Date: 2026-08-16

Timestamp: 2026-08-16T18:12:23.8651539+10:00 (Australia/Brisbane)

## Lay summary

The cancellation path now has a settled design for returning a stable answer
without keeping or reconstructing a larger snapshot of the appointment. Raisa
will keep only a small six-field cancellation receipt as command truth. Both
the first answer and any safe retry are generated from that same receipt, so a
later change elsewhere in the diary cannot silently alter the answer.

The design also keeps authority on the server: the client cannot declare its
own role, permission, session or generation. Raisa must check the proposal
before opening the command and check current authority and appointment truth
again while the record is locked. The old raw DELETE path remains separate and
does not acquire the safer proposal-confirm powers by accident.

One useful workflow defect was found and repaired. Our ordinary pytest setup
automatically touches a local synthetic test database, even in a tranche whose
boundary said no database. A new provider-free test runner now prevents that
fixture from loading in such tranches. No product database or patient data was
involved.

## Technical summary

The accepted candidate is
`9f0c166be2276d4e236dbdb4ed5657074ffbd0aa`. It freezes a two-layer response
contract: exact ordered six-field private bytes remain persisted truth, while
`raisa.delete_confirm_public_envelope.v1` is a sorted-key compact UTF-8 pure
projection containing `appointment.delete_confirmation_receipt.v1`. Replay
performs no current appointment read.

Admission derives server-owned identity and authority, validates the opaque
proposal-generation binding and signed evidence before the command session,
then rebuilds delete state from the locked target before the accepted physical
seam stages cancellation, attributable audit and private receipt atomically.
Seven internal outcome classes have one closed, non-disclosing HTTP posture.

The proof passes 14 input bindings, four semantic digests, 136 contract hostile
mutations, 20 evidence mutations, 191 canonical-static tests, 424 focused
tests, Ruff, deterministic validation, whitespace and 214-source compilation.
The host does not have exact Python 3.11, so that stricter runtime result is not
claimed. Gemini 3.7 Flash/high returned one clean pass with six zero-exit
commands and an unchanged review worktree.

## Deliberately closed

No product source, route or schema changed; no route or database ran; no
capability, product/patient/clinical data, provider, credential, network, UI,
deployment, release, Pages or protected ref opened. `docs/branding/` and all
unrelated untracked files remain preserved.

## Place in Raisa and next work

This closes the architectural bridge between cancellation command truth and
what Reception One will eventually receive. The next narrow tranche is the
provider-free unmounted implementation of that adapter composition. It remains
off-route and no-database: it can implement the pure projection, server-owned
ingress, locked re-admission composition and closed outcome mapping, but not
mount or call a route. Your attention is not required; standing authority
applies.
