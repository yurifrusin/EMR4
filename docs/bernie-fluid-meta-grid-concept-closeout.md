# Bernie Fluid Meta-Grid — In-House Concept Tranche Closeout

Date: 2026-07-20

Owner: Yuri / GPT Sol Extra High

Result: `meta_grid_concept_pass`

Claim scope: `provider_neutral_authored_synthetic_concept_design`

## Outcome

The tranche establishes a coherent interaction language for the Diary's
just-in-time visual form. The fixed grid is now one reversible projection in a
typed family rather than the required starting point for every task.

The accepted concept is **one stable shell with a fluid canvas**:

- a request rail creates or refines intent;
- a persistent scope ribbon says whose information, when, where, freshness and
  omissions are visible;
- an explicit state header distinguishes answer, clarification, selection,
  proposal, notice, block and committed receipt;
- the canvas selects the smallest useful family for the task; and
- a projection trail supports back, explicit recent-view restoration and
  ordinary-overview fallback.

The first grammar covers focused practitioner lanes, patient timelines,
availability and selection, aligned comparison, committed-change context,
proposal review, clarification and ordinary overview. It is tablet-first
without being tablet-only.

## Authority and API Spine result

The projection contract is presentation state over a fresh authorised read;
it is not Diary truth or a new API authority.

- GraphQL and existing read models remain read-only context sources.
- A selected appointment or slot is staff input only.
- Proposal review is visibly `proposal_not_committed`.
- The lab exposes no operational confirmation control and performs no
  appointment write.
- The existing REST/OpenAPI proposal and confirmation family remains the sole
  future mutation path, with backend revalidation, idempotency, audit and
  receipt.
- A committed event is a signal to obtain a fresh scoped read; no displayed
  Diary fact is trusted from an event payload and no event grants command
  authority.

No FastAPI route, GraphQL schema, command, database schema, production Diary,
event runtime or deployment artifact changed.

## Accepted evidence

The isolated static lab uses only authored synthetic fixtures and local assets.
It contains no fetch, API, WebSocket, event source, provider, persistence,
telemetry, cookie, service worker or transcript path.

| Scenario | Accepted behavior |
|---|---|
| MG-01 | Dr Shera's Friday-afternoon lane is scoped, chronological and free of unrelated columns. |
| MG-02 | Margaret Thompson's upcoming appointments use a chronological patient timeline with reversible refinement. |
| MG-03 | Available slots are chronological, touch-sized and selectable without a write. |
| MG-04 | Slot plus patient becomes a visible proposal; confirmation remains disabled and nothing is committed. |
| MG-05 | Dr Shera and Dr Patel are compared on one date, time, location and duration basis. |
| MG-06 | Ambiguous identity produces clarification before any Diary projection. |
| MG-07 | One relevant committed fixture produces one concise notice backed by a fresh synthetic read. |
| MG-08 | Replay, older revision and unrelated roster fixtures produce no second or broadened visual effect. |
| MG-09 | A new root request clears trail, selection, proposal and attention state; older roots require explicit restoration. |
| MG-10 | The ordinary overview remains the initial and direct fallback projection. |

Browser evidence passed at desktop 1280×720, tablet portrait 768×1024 and
tablet landscape 1024×768. All tested layouts had zero horizontal page
overflow and no enabled control below 44 pixels. Landscape comparison lanes
were equal width. Browser console warnings and errors were zero. Transient
screenshots were inspected locally and not retained.

Smartphones inherit this projection grammar but are not claimed by the tablet
pass. The lab has a narrow breakpoint; one-column projection, sequential
comparison, one-handed reach, software-keyboard occlusion, interruption/resume
and small-screen privacy still require their own browser and functional
evidence in the next tranche.

Native semantic buttons, chronological DOM order, visible focus, live-region
scope/state announcements and reduced-motion styling provide the conceptual
keyboard/accessibility contract. The in-app browser automation's locator
`press` operation did not synthesize native Enter/Space button activation, so
the full selection flow was exercised by pointer and the limitation is
preserved in the browser evidence. A product implementation tranche must add a
real-browser keyboard smoke test before making a stronger accessibility claim.

## Corrections found during acceptance

Three bounded corrections improved the concept without widening behavior:

1. recent-view history controls increased from 36 to at least 44 pixels;
2. selected projection `time_from` and `time_to` now derive from typed instants
   in the projection timezone rather than display-text parsing; and
3. slot labels now use DOM nodes and `textContent`, not HTML-string insertion.

The evidence heading was also made programmatically focusable so `Why this
view?` moves keyboard focus to the explanation it reveals.

## Verification

- fresh new-tranche and post-compaction five-source Ariadne receipts: pass;
- projection schema validation over every demonstrated family: pass;
- focused concept population: 18 passed;
- combined meta-grid/API Spine/Stage 3A/handover/Ariadne population: 78 passed;
- JavaScript syntax checks: pass;
- Ruff on the concept artifact test: pass;
- local browser desktop/tablet interaction and console checks: pass;
- local server and browser cleanup: pass; and
- `git diff --check`: pass.

The two Python warnings are existing dependency deprecation notices and do not
come from the concept artifacts.

## What is now settled

The following are no longer open conceptual questions:

- the grid is a fallback projection, not the Diary's compulsory shape;
- fluid content must sit inside a stable orientation shell;
- projection state is typed, scoped, fresh-read-backed and reversible;
- new root intents cannot inherit selection, proposal or attention hangover;
- touch, typing and conversation are interfaces to the same projection and
  proposal semantics;
- selection never commits;
- event awareness reconciles through current state and stays quiet by default;
  and
- tablet ergonomics are a primary constraint, not a later responsive patch.
- smartphone UX is a responsive variant of the same grammar, but tablet
  evidence does not substitute for a bounded phone population.

## Exact next decision boundary

Return the baton to Yuri. The recommended next step is a **bounded functional
meta-grid implementation tranche** over the existing Diary read and proposal
boundaries, beginning with focused practitioner view, patient timeline,
availability/selection, proposal review and ordinary fallback. It should add
the typed non-authoritative projection frame to the real client, retain the
current REST/OpenAPI confirmation path, and require fresh browser keyboard,
tablet, API-boundary and regression evidence.

That implementation is not opened by this closeout. Before it begins, Yuri
must approve its exact client surface, first projection families, read-model
inputs, whether the existing proposal handoff is in or out, and its acceptance
population, including the narrow-phone states named in the canonical design. A
committed-event runtime should remain a separate later tranche;
until then, change-context behavior uses fixtures only. Stage 3B should follow
functional implementation and correction, not this low-fidelity concept alone.

High-fidelity styling, any external design model or subscription, runtime API
wiring beyond the approved implementation contract, event infrastructure,
voice, representative participants, PII, production, deployment and release
remain closed.
