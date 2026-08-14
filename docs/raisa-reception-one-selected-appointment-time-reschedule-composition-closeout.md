# Reception One selected-appointment time-reschedule composition closeout

Date: 2026-08-14

Timestamp: 2026-08-14T09:50:00+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a`

Result: `raisa_reception_one_selected_appointment_time_reschedule_composition_pass`

## Outcome

Reception One can now propose a new start time for one selected current
appointment without becoming a second scheduler or command implementation. The
control permits only a 15-minute-aligned time on the same date, for the same
practitioner and with unchanged duration. It delegates once to the native
Diary's existing update proposal/confirm interaction.

The backend-owned proposal continues to show warnings and blocks, explicit
staff confirmation remains mandatory where required, and the command rechecks
current truth before commit. Reception One does not display the requested time
as committed truth. Every terminal outcome performs a fresh read; a successful
result is projected from the fresh appointment returned by that read.

## Implementation and command boundary

- `docs/diary/diary.js` adds a narrow local bridge that validates the selected
  current appointment and requested `HH:MM`, fixes duration delta at zero,
  resolves the same practitioner and delegates to `handleMoveResize`.
- The existing `POST /api/v1/appointments/proposals/update/{id}` and the
  proposal-supplied allowlisted confirmation endpoint remain the sole update
  command path. There is no raw `PUT`, new route or bridge-local network code.
- `docs/diary/meta-grid.js` and `meta-grid.css` add the modeless selected-time
  panel, one-action latch, fresh reconciliation, deterministic focus return and
  responsive desktop/tablet/phone treatment.
- Date, practitioner, duration, patient linkage, type, location, status,
  waiting area, reason, notes and booking channel remain outside the new
  control surface.

GraphQL stays read-only. FastAPI, OpenAPI, database, event and watcher surfaces
are unchanged.

## Worker contributions and recovery

The planned and actual mix agree: DeepSeek completed the separable browser-test
package, Gemini completed the required independent veto after deterministic
passage, and native subagents were deliberately not used because their likely
surface overlapped the two assigned lanes. Product integration, worker
recovery, acceptance, Continuity and Git remained serial under Sol.

DeepSeek V4 Flash/high delivered exactly one isolated browser-test artifact and
made no acceptance claim. When integrated, its provisional selectors and a few
pre-implementation assumptions required bounded Sol recovery. The recovered
matrix exposed a real product race: after a successful scoped refresh, the
selected Reception One card could briefly retain the old coordinate. The
final implementation now applies the exact fresh appointment read before it
announces committed truth.

Gemini 3.6 Flash/high independently reviewed exact candidate
`d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a` in a fresh clean read-only
worktree and returned one `pass`. Its worktree HEAD and status remained
unchanged. The review packet had incorrectly estimated 35 collected tests;
Gemini ran all six listed modules and reported 51, which Sol reproduced with
`--collect-only`. Acceptance uses the exact observed 51. The discrepancy is
preserved as AER-0305 rather than silently normalized.

Yuri also identified a workflow-continuity weakness: worker use could revert to
an implicit solo-serial default after a new task window. The new Ariadne
parallelism-efficacy control now makes three-lane consideration part of every
continuation receipt and makes missing or unreasoned allocation fail closed.
It requires explicit consideration, not automatic dispatch, so tightly coupled
or uneconomical work may still remain serial with a durable explanation.

## Verification

- 9 dedicated browser-test functions / 11 collected cases pass, including 12
  paired route-intercepted traces over safe, cancelled, blocked, stale, failed
  and committed outcomes in the conventional grid and Reception One.
- The paired outcomes agree on appointment id, date, start, end, practitioner,
  duration, patient linkage and status, with exact proposal/confirm counts and
  zero raw or unexpected mutation routes.
- The 23-test focused UI/truth packet, 144-test native Diary suite and 85-test
  API/latch packet pass.
- Gemini independently ran 51/51 packet tests plus Ruff, JavaScript syntax and
  whitespace checks.
- At the reviewed product candidate, the canonical fast profile passed its
  193/193 tests. After the closeout and parallelism-control tests were added,
  the final profile passes 196/196 plus Ruff, maintained-source compilation,
  Diary JavaScript syntax and Git whitespace.
- In-app rendered inspection passes at 1280x900, 768x1024 and 390x844 with
  correct dialog Escape/focus behavior and no horizontal overflow.
- Typed evidence is schema-valid and source-bound.

## Next tranche

The next narrow dependency-satisfied descendant inside Yuri's selected
appointment update/rescheduling family is a selected-appointment duration-only
composition. It should preserve date, start time, practitioner and every other
field; reuse the same existing `handleMoveResize` update proposal/confirm path;
and prove the same fresh-truth, fail-closed and no-second-command invariants.
It opens no new backend authority.

Yuri's attention is not presently required.

## Claim boundary

This proves repository-local authored-synthetic client composition,
route-intercepted browser behavior and independent source review. It does not
prove live backend/database, deployed, production, real-user or patient-data
operation. Protected evidence, historical Diary/PHI, product/patient/clinical
data, cross-day or cross-practitioner rescheduling, database/source/watcher
runtime, providers/ADC, credentials/IAM/network, new command or event families,
deployment, production, release, Pages and protected-ref movement remain
closed.
