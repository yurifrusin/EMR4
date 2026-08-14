# Reception One selected-appointment practitioner reassignment closeout

Date: 2026-08-14

Timestamp: 2026-08-14T13:38:04+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `f085fc98ead21a3e7929ee9adbda81abfc7542c9`

Result: `raisa_reception_one_selected_appointment_practitioner_reassignment_composition_pass`

## Lay summary

Reception One can now move one selected current appointment to a different
active practitioner without becoming another booking system. Staff choose a
current practitioner, review the proposed change in the ordinary Diary dialog,
and see the result only after current Diary truth has been read again.

Date, start time, duration, patient and every unrelated appointment detail stay
fixed. If the practitioner disappears, becomes inactive, is duplicated in the
directory, or current truth changes before confirmation, the change stops
without presenting the requested practitioner as fact.

## Technical result

- The selected-action panel offers only distinct rows marked active by the
  existing authenticated practice-scoped directory and excludes the current
  practitioner.
- Immediately before delegation, the bridge reads the exact appointment and
  directory again, requires one exact active match, freezes that admitted
  identity, supplies literal zero start and duration deltas, and delegates once
  to existing `handleMoveResize`.
- The shared composer rejects a mismatch between the frozen admission and
  caller-supplied column. Reception One owns no route, fetch, signing,
  idempotency, confirmation or raw PUT code.
- The existing update proposal now blocks a changed target that is not
  currently active. Confirmation re-runs the same proposal, closing the
  deactivation race. An unchanged inactive historical practitioner remains
  valid for time or duration changes.
- Twelve paired conventional-grid/Reception One traces agree on eight fresh
  truth fields across safe, cancelled, blocked, stale, failed and committed
  outcomes, with exact route counts and zero raw or unexpected mutations.

GraphQL remains read-only. No new route, request/response schema, OpenAPI
surface, database object, event family or command authority was added.

## Issues exposed and repaired

The native read-only review found that duplicate directory identities were
being shown first-wins and that a direct caller column needed to be bound to
the bridge's fresh admission. Both now fail closed before proposal. Sol then
identified the deeper source-truth race: client directory freshness alone
could not prevent a practitioner being deactivated before command execution.
The existing proposal/confirm family now owns that active-target invariant.

The DeepSeek browser artifact was structurally useful but included three bad
fixture assumptions: card display names included no title, confirmation always
changed practitioner even for a time-only regression, and a 201-row response
misrepresented the real first-200 contract. Sol recovered these without
weakening the product contract; the final 649-line file passes 20 cases.

## Parallelism efficacy: planned versus actual

- **DeepSeek V4 Flash/high:** planned for one isolated test-only file capped at
  650 lines; returned 646 lines and was integrated at 649 after Sol recovery.
  It supplied a broad paired matrix, but its non-authoritative adapter estimate
  was USD 17.55. Its defect-finding value was real, while its economy was
  negative; this allocation should not be repeated unchanged.
- **Native subagent:** planned for an exact read-only seam map; completed with
  no edits and directly caused the duplicate-ID and frozen-admission repairs,
  while clarifying malformed-ID and read-model boundaries. Positive leverage.
- **Gemini 3.6 Flash/high:** reserved until deterministic passage; then returned
  `pass` over exactly 80 tests at unchanged clean candidate
  `f085fc98ead21a3e7929ee9adbda81abfc7542c9`. Its prose transcribed stale and
  transport route counts incorrectly; Sol acceptance uses the actual passing
  test matrix: stale `[1,1]`, failed `[1,0]`.
- **Sol:** retained product/UI meaning, command-truth recovery, worker-test
  recovery, stateful browser execution, integration, acceptance, Continuity
  and Git authority.

This demonstrates the permanent anti-serial-drift control: DeepSeek, Gemini
and native lanes each received an explicit disposition and bounded package at
every continuation gate; dispatch occurred only where expected leverage
exceeded coordination cost, and closeout records actual efficacy and economy.

## Verification

- 11 dedicated browser functions / 20 collected practitioner cases pass.
- All 42 appointment-update proposal/confirmation tests pass.
- The consolidated practitioner/duration/time/status/truth/API packet passes
  126/126.
- Gemini independently passes the exact 80-test packet, Ruff, both JavaScript
  syntax checks and Git whitespace at the unchanged clean candidate.
- The canonical fast profile passes 196/196, plus Ruff, compilation of 209
  maintained Python sources, Diary JavaScript syntax and Git whitespace.
- Rendered Playwright inspection passes at desktop and phone, with automated
  tablet coverage, no horizontal overflow, exact practitioner transition,
  confirmation dialog and Escape focus return. The in-app Browser connected
  but could not bind newly created tabs to its active session, so the explicitly
  permitted local Playwright fallback supplied rendered evidence.
- Typed evidence is schema-valid and source-bound.

## Place in the Raisa direction

Reception One now composes status, same-day start, duration and practitioner
reassignment over the same kernel-owned appointment truth. The conventional
grid and meta-grid can express different interaction grammars while one backend
proposal/confirm path owns authority, safety and committed meaning.

The four proven selected-action panels also reveal the next UX risk: adding a
separate full-width panel for every remaining field would undermine the
minimum-app/maximum-intelligence direction. The next safe descendant is a
provider-free read-only selected-action-console consolidation orientation. It
will choose the narrowest progressive-disclosure or intent-led composition
without opening another field or command.

## Claim boundary

This proves repository-local authored-synthetic client composition, local
database-backed command tests, route-intercepted browser behavior, rendered
inspection and independent source review. It does not prove live product data,
deployed or production behavior, real-user operation or patient-data safety.
Cross-day movement, full edit, further fields, real product data, provider
calls, deployment, release, Pages and protected-ref movement remain closed.

Yuri attention required: no.
