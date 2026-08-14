# Yuri closeout — Reception One combined update kernel rehearsal

Date: 2026-08-15

Timestamp: 2026-08-15T00:46:56+10:00 (Australia/Brisbane)

Result: `raisa_reception_one_same_update_family_multi_change_kernel_rehearsal_pass`

Accepted reviewed source: `3dd5f3b39ed98a2d562685d1d1567a359930c693`

## Lay summary

Reception One's truth kernel can now safely handle one request that changes the
doctor, time and appointment length together. It prepares one provisional
proposal and, after explicit human confirmation, either commits all three
changes together or none of them.

The kernel checks the live appointment and target diary again at confirmation.
An intervening appointment change, a new clash or an inactive practitioner
blocks the whole proposal. Repeating the same confirmed request does not write
twice. Even a deliberately injected late transaction failure leaves no partial
appointment, audit or request-ledger result and permits one clean retry.

This establishes the safe backend floor for a visible combined Reception One
editor. It does not add that editor yet.

## Technical summary

All frozen `M1-M7` scenarios pass through the unchanged existing appointment
update proposal/confirm kernel. One combined practitioner/time/duration command
produces one appointment update, one correlated audit and one completed
idempotency result. Stale truth, target conflict and inactive-practitioner
cases retain no candidate effect. Exact fresh-session replay is mutation-free;
different-body reuse conflicts. Failure at idempotency completion after
update/audit flush proves full rollback, clean same-key retry and exact replay.

Verification comprised 109 core/API tests, 69 continuity tests and 234 register
tests: 412 total. Fresh Gemini 3.6 Flash/high independently passed the exact
candidate and left the worktree unchanged and clean. Ruff, JSON, 32-path scope
and Git whitespace checks pass. The final continuity-inclusive closeout packet
passed 438 tests across eleven modules. No product source changed.

## Issues exposed and resolved

- DeepSeek returned the correct bounded one-file candidate but violated its
  exact JSON-only response format; AER-0309 contains that defect and Sol relied
  only on Git plus independently reproduced tests.
- Sol briefly wrote an invented full hash from a short Git display; AER-0310
  records the correction before any receipt used it.
- Sol invoked the Antigravity help command by the wrong Python form; AER-0311
  records the local pre-model failure and correct module-form recovery.
- A first aggregate test run exceeded a 120-second shell deadline. It was
  discarded, and the complete serial-locked rerun passed with a suitable
  deadline.

## Deliberately closed

No compound UI yet; no new backend route, schema, command family or migration;
no status-plus-update transaction; no conversational execution; no external
patient, email, SMS, WhatsApp, voice or delegated-assistant runtime; no patient
or product data; no provider/ADC, credentials/IAM or network; and no
deployment, production, release, Pages or protected-ref movement.

## Place in Raisa

The semantic keyboard now rests on a proved multi-field transactional kernel.
Raisa or a future adapter may shape a typed provisional request, but current
truth, authority, confirmation, the write and its receipt remain backend-owned.
This is the bridge from individual safe buttons to useful compound actions
without giving the intelligence layer a generic tool belt.

## Next

Build the narrow provider-free Reception One combined editor for practitioner,
time and duration. It will create one draft, call the existing proposal route,
show one review and require one explicit confirmation; status remains separate.
No conversational or external-channel activation is included.

Yuri attention required: no.
