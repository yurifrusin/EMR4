# Reception One combined-scope product proof plan

**Status:** frozen for bounded implementation  
**Decision owner:** Yuri  
**Conductor and acceptance owner:** GPT Sol  
**Date:** 2026-07-21  
**Source head:** `1d0442845974a46e12f5963ed9afb14beb4fd381`  
**Task branch:** `codex/reception-one-combined-scope-proof`

## 1. Decision and purpose

Yuri authorises one bounded Reception One client proof over the already accepted
functional meta-grid and Stage 1 proposal foundations. The proof must make this
ordinary request work as one visible scope:

> Show me all the available slots with Dr Shera for a half-hour appointment
> with Margaret Thompson after 2 today.

The point is plumbing, not final visual design. The projection must resolve and
show the patient, practitioner, duration, date and time window together; obtain
current backend availability; keep the resolved patient and practitioner in
scope when staff selects a slot; and prepare the existing non-committing
proposal without making the user repeat the patient name.

Reception One remains the provisional user-facing product name and meta-grid
remains the architectural term. This tranche grants no rename, artwork,
trademark, high-fidelity styling or final UX authority.

## 2. Frozen visible interaction

The target flow is:

1. A receptionist opens the existing meta-grid workspace and submits the exact
   combined request above through the visible request field.
2. The client resolves exactly one authorised practitioner and exactly one
   authorised patient before showing availability. Ambiguity stops in a
   clarification projection; neither identity is guessed or inherited from an
   earlier root request.
3. The availability projection visibly states Margaret Thompson, Alex
   Shera, the Diary reference date, a 2:00 pm start boundary and 30-minute
   duration. Candidate slots come from the existing non-mutating slot-search
   proposal route.
4. Staff selects one visible candidate by touch, mouse or keyboard. Selection
   neither reserves nor books anything.
5. Because the patient was resolved in the root request, the visible action is
   `Prepare proposal for Margaret Thompson`. Activating it calls the existing
   supervised-booking proposal route and shows the existing proposal review.
6. The proof stops at proposal review. `Continue to booking review` may be
   shown as the already accepted handoff, but acceptance automation must not
   activate it. No confirmation control exists in the meta-grid.

The same root scope must support these contextual refinements without losing
the other four dimensions:

- `tomorrow instead` changes only the date;
- `make it 45 minutes` changes only duration;
- `after 3` changes only the lower time boundary and deterministically means
  3:00 pm inside the ordinary daytime Diary window.

An unqualified time from one through six is interpreted as afternoon within
the ordinary 8:00 am–5:00 pm Diary day. Explicit `am` or `pm` always wins.
New root requests clear patient, selection and proposal scope before resolving
their own identities.

## 3. State, privacy and interruption rules

- Patient context is in-memory only. It is carried by the typed projection
  scope and its visible items; it is not written to browser storage.
- Patient-sensitive scope copy, proposal copy, actions and root-history labels
  participate in the existing privacy mask.
- Privacy mode must not announce the patient name in the live region.
- A window blur or visibility interruption marks the projection stale, hides
  patient details, removes selected-slot and proposal state, and disables
  proposal work.
- `Refresh current view` performs a fresh patient resolution plus the exact
  scoped availability read. It may restore the patient to scope only after the
  fresh unambiguous read; it never reconstructs a stale slot or proposal.
- Back and ordinary-overview fallback remain available and reversible.

## 4. Existing read and proposal boundary only

Permitted existing routes are:

- `GET /api/v1/appointments`;
- `GET /api/v1/patients/search`;
- the existing practitioner directory read;
- `POST /api/v1/appointments/proposals/slot-search` as a command-shaped,
  non-mutating read; and
- `POST /api/v1/appointments/proposals/bernie/supervised-booking` as a
  non-committing proposal.

No API, Pydantic, GraphQL, OpenAPI or database artifact changes are authorised.
GraphQL remains read-only. No appointment create, confirm, cancel or delete
route may be called. The client must continue to declare
`appointment_write_authority: false`.

The API Spine proposal order remains proposal, deterministic backend checks,
typed envelope, staff review, and only then a separately owned explicit
confirmation command. This tranche ends before that confirmation command.

## 5. Implementation allocation

Sol retains implementation and runtime testing. The change is a small but
stateful client grammar alteration coupled to one disposable database and one
serial real-browser run; a worker packet and shared-runtime coordination would
not save a meaningful implementation cycle. No native subagent is assigned.

A fresh Gemini Flash review through Antigravity is required after the candidate
and evidence packet are complete. It is an independent veto over identity
retention, refinement semantics, privacy/interruption recovery, closed-route
observations and claim width; it receives no integration or acceptance
authority.

## 6. Deterministic and browser acceptance

Focused repository guards must prove:

- the exact combined request and all three refinements are encoded;
- patient identity is resolved before availability and is not silently reused
  by a new root;
- selection can prepare a proposal directly from the resolved combined scope;
- interruption requires fresh patient resolution and fresh availability;
- no fetch, persistence, event, provider, voice or confirmation surface is
  added to `meta-grid.js`;
- the Diary bridge still names only the accepted read and proposal routes; and
- the canonical Ariadne contract is linked to focused test evidence.

The task-scoped Playwright runner is equivalent to interactive control because
it drives Chromium through the ordinary visible UI, uses no `page.route(...)`
or API interception, makes real calls to the local FastAPI backend and
PostgreSQL, and records sanitized network observations, screenshots and
database readback. It runs on IPv6 loopback `localhost:3000` and
`localhost:8001` so Yuri's existing `127.0.0.1` review servers and browser tabs
remain untouched.

The exact disposable authored-synthetic database is
`gp_pms_reception_one_combined_scope_9c41b7e2_20260721`. The interpreter
provider is `disabled`, fallback is false, cloud credentials are blank, and
the database must not pre-exist. Cleanup may drop only this exact database
after its ownership marker is verified.

The evidence label is `live_local_browser_backend_postgres`. Acceptance must
cover:

- desktop landscape 1440×900;
- tablet landscape 1024×768;
- tablet portrait 768×1024;
- smartphone portrait 390×844;
- smartphone landscape 844×390;
- exact combined request, 2:00 pm and 30-minute interpretation;
- `tomorrow instead`, `make it 45 minutes`, and `after 3` while patient and
  practitioner remain in scope;
- touch/click and native-keyboard selection and proposal preparation;
- Enter request submission, Space slot selection, Tab navigation and Escape
  explanation dismissal;
- privacy masking and interruption followed by a fresh scoped recovery;
- back and ordinary full-Diary fallback;
- correct page identity, nonblank rendered content, no error overlay, no
  console warnings/errors, zero horizontal overflow and no enabled control
  below 44×44 CSS pixels at every viewport;
- only loopback network traffic and only the allowlisted read/proposal routes;
- before/after appointment, audit, idempotency, Bernie session and Bernie event
  counts and hashes are identical; and
- no proposal handoff, confirmation control, event runtime or receipt is
  activated.

Screenshots may visibly contain only the newly authored synthetic identities.
Machine-readable evidence must remain sanitized and must not record a patient
name, date of birth, patient identifier, token, password or credential.

Repository pytest processes that load `tests/conftest.py` and the disposable
browser/backend/PostgreSQL run remain serial. Historical evidence artifacts are
not regenerated.

## 7. Continuity and closeout gates

The Ariadne node `reception-one-combined-scope-proof` is a descendant of the
accepted functional client and inherits
`combined-patient-practitioner-time-duration-intent`. During implementation its
contract evidence remains `gap`. It may change to `satisfied` only when the
focused test and live-local evidence both pass and are linked in the node.
The engine remains advisory and cannot grant authority or accept the tranche.

Final `reception_one_combined_scope_pass` requires all of the following:

1. focused, combined and API Spine regressions pass;
2. the real-browser evidence and zero-write readback pass;
3. the exact disposable database is marker-verified and dropped;
4. the fresh Gemini veto passes with no unresolved material finding;
5. Sol records closeout and acceptance with accurately bounded claims;
6. check-gated PR integration succeeds; and
7. local and origin `master` and `handoff/current` realign cleanly.

## 8. Boundaries that remain closed

This plan opens no provider, event-runtime, persistence, appointment write or
confirmation authority. PII, real patient/practice data, protected holdouts,
historical diary material, representative participants, Stage 3B, voice,
push-to-talk, ambient listening, autonomous confirmation, external design
models, high-fidelity styling, production, deployment and release remain
closed. Dependabot alert 5 remains untouched.
