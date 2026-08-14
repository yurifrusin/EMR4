# Reception One multi-change request atomicity orientation closeout

Date: 2026-08-14

Timestamp: 2026-08-14T21:47:54+10:00 (Australia/Brisbane)

Status: accepted

Accepted reviewed source: `fbb7ffb46e041bbfc193ff3a76b2f970c06dee58`

Result: `raisa_reception_one_multi_change_request_atomicity_orientation_pass`

## Lay summary

Reception One's four large controls are now anchored as a small semantic
keyboard for authorised reception staff. Raisa may understand and propose those
meanings, but neither Raisa nor Siri, email, SMS, WhatsApp, voice or another
chatbot may press the controls, confirm a change or inherit a user's authority.

Several compatible changes—time, duration and practitioner—belong to one
existing appointment-update family. The safe future shape is one combined
proposal, one review and one explicit human confirmation, not a hidden series of
separate writes. Status remains a different command family. A request such as
“move it to 10:00 and mark it arrived” can be shown as a non-executable review
plan, but there is no current all-or-nothing command and no rollback promise.

The human confirmer need not always be a receptionist in the wider Raisa
architecture. A properly identified and authorised patient may eventually
confirm their own new appointment from candidate bookings. Email, Siri or
another service would remain a revocable transport/client acting under a
narrow patient grant; the patient is the principal and the backend still owns
fresh availability, command execution and the receipt. That patient-channel
runtime remains a separately closed programme gate.

## Technical result

The accepted architecture selects
`typed_inert_candidate_then_one_family_owned_command`:

- `AppointmentActionCandidate` has an exact target, allowlisted provisional
  values and zero DOM, route, confirmation or write authority;
- time, duration and practitioner compose only inside the existing update
  proposal/confirm family;
- status remains inside its distinct signed status proposal/confirm family;
- cross-family candidates are non-executable and disclose the absence of
  atomicity;
- contradiction, ambiguity, unsupported fields, missing authority, stale truth
  and interruption clarify or block;
- events remain refresh hints, while current source truth and authority are
  rechecked by the command kernel; and
- a future complex button is only a typed presentation macro unless a separately
  proven kernel command owns every field and transactional effect.

The exact source map distinguishes direct evidence from structural support. A
combined date/time/duration proposal and confirmation are directly proven, as
is changed-practitioner revalidation denial. Successful changed practitioner,
time and duration in one confirmation, its exact same-key replay and injected
rollback remain deliberately unproved and form the next rehearsal.

No product, Diary UI, backend, API, OpenAPI, GraphQL, database, migration,
event, watcher or runtime source changed.

## Evidence and verification

- Exact core appointment/API/orientation packet: 144 passed.
- Exact latch/preflight/autonomous-continuation packet: 79 passed.
- Exact agent-error register packet: 234 passed.
- Total independent review packet: 457 passed across eight modules.
- Ruff lint and format check passed; JSON, source-hash and Git whitespace
  checks passed.
- Fresh Gemini 3.6 Flash/high returned one schema-constrained `pass` at
  unchanged clean source `fbb7ffb46e041bbfc193ff3a76b2f970c06dee58`.
- Evidence label: `repository_static_authored_synthetic`.

Gemini's narrative said five commands although the frozen packet contains nine
command lines, and described two files as formatted although Ruff ran only
`format --check`. AER-0308 preserves the discrepancy. The receipt's detailed
144/79/234 results, separate Ruff checks, exact Git checks and harness-owned
unchanged-clean postcondition reconcile it without another model call or a
broader claim.

## Parallelism efficacy: planned versus actual

- **DeepSeek V4 Flash/high:** declined as planned because no stable mechanical
  implementation package existed; actual leverage remained neutral/negative.
- **Native subagents:** both attempted read-only analysis, but AER-0306 and
  AER-0307 record command-scope breaches. Both outputs were interrupted,
  quarantined and wholly inadmissible. Actual leverage was negative.
- **Gemini 3.6 Flash/high:** completed one fresh exact-candidate veto. Its
  independent architecture challenge had positive value; AER-0308 contains the
  bounded receipt wording defect.
- **Sol:** independently reproduced every source fact from exact ordinary files
  and retained architecture, containment, acceptance, continuity and Git
  authority.

No protected content or rejected worker finding enters the accepted result.

## Next tranche

Proceed under standing authority with
`raisa_reception_one_same_update_family_multi_change_kernel_rehearsal`. Use
provider-free authored-synthetic data to exercise the existing update
proposal/confirm path with changed time, duration and practitioner in one
command, plus stale/current-truth, conflict, idempotency, audit and rollback
checks. Prefer tests over product changes and add no UI.

## Claim boundary

This proves repository-local architecture and exact current-source semantics.
It does not prove a compound editor, conversational execution, external patient
or assistant identity, live channel delegation/revocation, patient data, voice
safety, a cross-family transaction, deployment or production readiness.
Provider use, credentials/IAM, watcher/database runtime, release, Pages and
protected-ref movement remain closed.

Yuri attention required: no.
