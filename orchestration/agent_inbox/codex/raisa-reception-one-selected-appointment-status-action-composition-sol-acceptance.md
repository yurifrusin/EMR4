# Sol acceptance — Reception One selected-appointment status action

Date: 2026-08-13

Timestamp: 2026-08-13T22:46:00+10:00 (Australia/Brisbane)

Decision: accept

Accepted source: `b6c6a983c4936c1f0bd5e9daf03924bbcd4ddd33`

Result: `raisa_reception_one_selected_appointment_status_action_composition_pass`

## Acceptance reasoning

The candidate satisfies the frozen narrow boundary. One selected current,
non-placeholder Reception One appointment can invoke one status from the
existing vocabulary through a local bridge to the existing
`setAppointmentStatus` interaction. The bridge contains no `fetch`,
`apiFetch`, proposal, confirm or raw-write implementation. The accepted REST
proposal/confirm family remains the sole command path and GraphQL remains
read-only.

The UI remains modeless except for the existing terminal confirmation. It
reports busy, cancellation, blocking, stale/failure and committed outcomes;
prevents a second invocation during an active attempt; and performs a fresh
projection rebuild before presenting terminal truth. Responsive and keyboard
evidence covers desktop, tablet and phone. The single visual defect discovered
during inspection was repaired inside the frozen verification loop.

The evidence schema binds the result to exact source
`b6c6a983c4936c1f0bd5e9daf03924bbcd4ddd33`; the dedicated 8-case rendered
suite, full 144-case native Diary suite, 171-test focused packet and canonical
193-test fast profile all pass.

## Authority finding

No provider, real patient/product record, database/source access, backend
change, new route, new command family, deployment, release, Pages or protected
ref was used or authorised. `docs/branding/` and unrelated untracked files
remain outside the candidate.

The next safe step is a fresh read-only programme orientation. It has no
authority to choose an option that still carries an explicit Yuri-owned gate.
