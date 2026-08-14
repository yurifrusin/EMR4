# Reception One selected-appointment duration composition closeout

Date: 2026-08-14

Timestamp: 2026-08-14T11:55:58+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `f397a3706f3b870b8436eb3993bd90c6c0c742a8`

Result: `raisa_reception_one_selected_appointment_duration_composition_pass`

## Lay summary

Reception One can now change how long one selected current appointment lasts
without becoming a second booking system. Staff choose from bounded duration
options, review the proposed change in the ordinary Diary confirmation dialog,
and see the result only after current Diary truth has been read again.

The appointment's date, start time, practitioner, patient and every unrelated
field remain outside this control. Warnings and blocks still belong to the
existing backend-owned appointment update path. A failed, cancelled, stale or
interrupted change never leaves the requested duration displayed as fact.

## Technical result

- `docs/diary/diary.js` adds a narrow duration bridge. It reads the exact
  current appointment, admits only integer targets from 15 through 480 minutes
  whose delta is divisible by 15, keeps the derived end on the same date,
  supplies literal zero for the start delta, retains the same practitioner and
  delegates once to existing `handleMoveResize`.
- `docs/diary/meta-grid.js` adds a bounded selector and separate duration-only
  submission beside the existing status and time actions. Valid non-grid
  current durations remain usable: a 20-minute appointment can reach 35
  minutes because the delta, rather than the absolute target, is quantized.
- Status, time and duration submissions are mutually exclusive. Interruption
  or failed reconciliation leaves the projection stale and blocks another
  operational action until fresh truth returns.
- The existing update proposal endpoint and proposal-supplied allowlisted
  confirmation endpoint remain the sole command path. Reception One contains
  no route, fetch, signature, confirmation, idempotency or raw PUT
  implementation.
- The duration-specific dialog retains visible staff confirmation, focus
  containment, Escape cancellation and deterministic return focus.

GraphQL remains read-only. FastAPI, OpenAPI, database, event and watcher
surfaces are unchanged.

## Issues exposed and repaired

The recovered paired browser matrix exposed a real ordering race: the ordinary
Diary callback could announce a terminal committed result before the duration
bridge completed its mandatory exact fresh read and projection update. The
bridge now withholds terminal callback phases until fresh reconciliation
succeeds.

Rendered phone inspection then exposed one mojibake range separator in the new
time label. The source now uses the correct Unicode en dash. Desktop, tablet
and phone layouts remain horizontally contained.

## Parallelism efficacy: planned versus actual

The mandatory three-lane assessment worked as intended after task-window
restoration:

- **DeepSeek V4 Flash/high:** planned for one isolated browser-test artifact;
  completed exactly that file. Sol rejected its free-form-input assumptions,
  recovered the useful paired matrix to the frozen selector contract, and the
  resulting execution exposed the terminal-callback race. The lane delivered
  positive defect-finding leverage, though the adapter reported unusually
  large token use and a non-authoritative estimated cost of about USD 8.56.
  Future packets should keep the same separation while further constraining
  output size and stopping once the closed matrix is complete.
- **Native subagent:** planned for a read-only seam map; completed without
  edits. It identified exact-read, reconciliation, midnight-boundary and
  brittle-static-test risks before acceptance, all of which informed the final
  implementation.
- **Gemini 3.6 Flash/high:** reserved until deterministic passage; then ran one
  fresh exact-candidate veto. It passed 68/68 tests and returned `pass` while
  leaving candidate HEAD and worktree unchanged and clean.
- **Sol:** retained product integration, worker recovery, the stateful browser
  session, deterministic admission, acceptance, Continuity and Git authority.

This is the durable workflow answer to solo-serial drift: every continuation
receipt must carry separate DeepSeek, Gemini and native-agent dispositions,
owned packages or serial constraints, and reassessment triggers. Missing
assessment now returns `revision_required`; dispatch remains leverage-gated
rather than ceremonial.

## Verification

- 10 dedicated browser functions / 12 collected cases pass, including 12
  paired conventional-grid/Reception One traces over safe, cancelled, blocked,
  stale, failed and committed outcomes.
- The consolidated duration/time/status/truth-parity and affected Diary packet
  passes 118/118.
- Gemini independently passes the exact 68-test packet plus Ruff, JavaScript
  syntax and Git whitespace at unchanged candidate
  `f397a3706f3b870b8436eb3993bd90c6c0c742a8`.
- The canonical fast profile passes 196/196, including Ruff, maintained-source
  compilation, Diary JavaScript syntax and Git whitespace.
- In-app rendered inspection passes at 1280x900, 768x1024 and 390x844 with
  zero document-width overflow, a visible bounded selector, duration-specific
  dialog and Escape focus return.
- Typed evidence is schema-valid and source-bound.

## Place in the Raisa direction

Reception One now reflects the same appointment truth and converges on the
same command path for status, start time and duration. The meta-grid remains a
projection over the kernel rather than an alternative store or scheduler.
Each new modality is proving that visual composition can vary while authority,
confirmation and fresh truth remain projection-neutral.

## Next tranche

The narrowest remaining `handleMoveResize` field is practitioner-only
reassignment for the same date, start and duration. The next planned tranche
should offer only an existing active-practitioner target, delegate once through
the same update proposal/confirm interaction, preserve every other field and
prove the same paired outcomes, fresh reconciliation and zero-second-command
boundary.

Yuri's attention is not presently required.

## Claim boundary

This proves repository-local authored-synthetic client composition,
route-intercepted browser behavior, rendered inspection and independent source
review. It does not prove live backend/database, deployed, production,
real-user or patient-data operation. Cross-day moves, full edit, real product
data, event/watcher runtime, provider/product calls, deployment, release,
Pages and protected-ref movement remain closed.
