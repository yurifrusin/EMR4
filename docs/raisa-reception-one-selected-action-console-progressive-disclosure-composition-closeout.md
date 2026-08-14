# Reception One selected-action-console progressive-disclosure composition closeout

Date: 2026-08-14

Timestamp: 2026-08-14T18:40:01+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `1d9e58fd2624f87b8b3def538297054999e7bef3`

Result: `raisa_reception_one_selected_action_console_progressive_disclosure_composition_pass`

## Lay summary

Reception One now presents the four proven appointment actions as one calm,
compact console. Selecting an appointment shows its current status, time,
duration and practitioner, followed by four clear choices. No editor is open
until the receptionist chooses one, and only that editor appears.

Opening, closing or changing the visible editor does not contact the server or
change the Diary. An abandoned draft is discarded rather than hidden. Once a
proposal or confirmation is under way, the console cannot switch appointments
or actions underneath it. Committed meaning is still shown only after fresh
Diary truth is reconciled.

Requests containing several changes remain deliberately non-executable as a
combined operation. The console neither silently runs several commands nor
claims atomic multi-field behavior. Each current field action retains its own
explicit review and confirmation path.

## Technical result

The accepted implementation adds:

- one presentation-only `activeSelectedAction` enum;
- a patient-minimized current-truth summary;
- four native 44-pixel action buttons with ordinary keyboard semantics;
- one stable shared editor region containing zero or one existing renderer;
- idle draft reset on collapse, switching, interruption and fresh external
  projection replacement;
- busy and confirmation exclusion for palette transitions and appointment
  reselection; and
- action-specific terminal removal outcomes without presenting requested
  values as current truth.

The four existing renderers, executors and bridges are retained. Status still
uses the status proposal/confirm family; time, duration and practitioner still
use their field-specific bridges to the update proposal/confirm family. The
implementation adds no generic dispatcher, combined payload or second write
path. `docs/diary/diary.js`, the backend, OpenAPI, GraphQL and database remain
unchanged.

## Evidence and verification

- The new route-intercepted browser contract passes 23/23 checks.
- The four existing selected-action browser suites pass 49/49 checks.
- The unchanged paired-projection status truth case passes 1/1 after only its
  palette-opening helper was adapted.
- The exact broader eleven-module packet passes 167/167.
- The canonical fast profile passes 196 tests, Ruff, compilation of 209
  maintained Python sources, Diary JavaScript syntax and Git whitespace.
- The typed tranche evidence passes five schema and boundary checks.
- One fresh Gemini 3.6 Flash/high veto passes the exact 167-test packet at
  unchanged clean candidate
  `1d9e58fd2624f87b8b3def538297054999e7bef3`.
- In-app Browser inspection confirmed the local authored-synthetic shell and
  responsive visual composition. Exact command behavior remains correctly
  labelled `route_intercepted_browser`, not live backend evidence.

The unchanged baseline-to-candidate Git blobs are:

- `docs/diary/diary.js`:
  `789c5e43078bdc08c7e060938dda606b4b98d199`;
- `app/routers/appointments.py`:
  `ccae18334f82fc29822c1e32f0d99585cf850657`; and
- `docs/api-spine/openapi/appointment-commands.yaml`:
  `42e24524e069fe12a15911cee98f9df22f0d51fb`.

## Parallelism efficacy: planned versus actual

- **Native subagents:** both read-only audits completed with positive leverage.
  They identified the busy-reselection and fresh-event draft hazards and made
  the implementation and acceptance stronger.
- **DeepSeek V4 Flash/high:** produced the bounded test-only candidate, but its
  initial and one permitted corrected structures needed Sol recovery before
  admission. The final tests are useful and pass, but the lane had negative
  net leverage; no additional same-lane correction ran.
- **Gemini 3.6 Flash/high:** supplied the required independent veto with
  positive acceptance value and no candidate mutation.
- **Sol:** retained product implementation, test recovery, browser evidence,
  acceptance, continuity and Git authority.

The DeepSeek defects were ordinary candidate-test defects within the bounded
recovery rule. No failed result was admitted and no agent-error-register event
was required.

## Next tranche

The next safe descendant is a provider-free, read-only
`raisa_reception_one_multi_change_request_atomicity_orientation`. It will map
the exact existing update proposal/confirm contract and freeze how a request
containing more than one appointment change should be represented and
confirmed. It must preserve the present rule that no client may auto-sequence
single-field commands or imply compound atomicity. It may recommend a later
atomic kernel-owned command contract, but it grants no product implementation,
route, schema or write authority itself.

## Claim boundary

This proves a repository-local presentation composition with authored-synthetic
and route-intercepted browser evidence. It does not prove representative
usability, live backend/database behavior, product or patient data, a compound
update transaction, conversational command execution, deployment or production
readiness. Provider use, events/watchers, new commands/routes, release, Pages
and protected-ref movement remain closed.

Yuri attention required: no.
