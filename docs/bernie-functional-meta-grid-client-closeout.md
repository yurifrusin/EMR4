# Bernie Functional Meta-Grid Client Closeout

Date: 2026-07-20

Owner: GPT Sol

Result: `functional_meta_grid_client_pass`

Evidence posture: local, authored-synthetic, provider-disabled and
non-authoritative

## 1. Decision and result

Yuri authorised the bounded functional client tranche recommended by the
accepted provider-neutral meta-grid concept closeout. The native Diary now has
a working intent-projected client over existing read and proposal-only
boundaries. It supports plain-language root requests and reversible
refinements, desktop, tablet and smartphone layouts, keyboard operation,
privacy masking, interruption reconciliation and a safe return to the ordinary
Diary.

The result is `functional_meta_grid_client_pass` for the frozen tranche in
`docs/bernie-functional-meta-grid-client-plan.md`.

This is not a production, representative-usability, live-provider, event
runtime, PII, deployment, release or appointment-write result.

## 2. Implemented client surface

The implementation is confined to the existing native Diary surface:

- `docs/diary/diary.html` hosts the semantic shell and controls;
- `docs/diary/meta-grid.js` owns the typed projection state, bounded
  plain-language routing, rendering, history, privacy and reconciliation;
- `docs/diary/meta-grid.css` owns the functional responsive and accessibility
  contract; and
- a small controlled bridge in `docs/diary/diary.js` reuses the existing
  appointment read, patient search, practitioner directory, non-mutating slot
  search and supervised-booking proposal surfaces.

The client implements these accepted projection families:

1. ordinary overview;
2. focused practitioner schedule;
3. patient timeline;
4. availability;
5. aligned practitioner comparison;
6. selection;
7. proposal review; and
8. clarification.

Every projection carries `appointment_write_authority: false`. A new root
clears transient selection and proposal state. Back restores the exact parent
projection. The ordinary Diary remains the reversible fallback.

## 3. Plain-language refinement

The bounded deterministic grammar supports:

- named practitioner roots, patient upcoming-appointment roots,
  availability and exactly-two-practitioner comparison;
- today, tomorrow, weekday and ISO-date selection;
- after, before, morning, afternoon and whole-day time changes;
- patient-horizon refinement; and
- ordinary overview and back.

Refinements preserve the root intent and name the changed structured scope
dimensions. A full root request that happens to contain a time phrase is not
misclassified as a refinement. Ambiguous practitioner or patient identity
produces clarification before sensitive projection.

## 4. Authority and API Spine review

### Spine Surface

`command_only`

The tranche introduces no GraphQL schema, read-model type, resolver, REST
route, OpenAPI/Pydantic command, database table or migration. It consumes
existing client-visible reads and two existing proposal-only routes:

- `GET /appointments`;
- `GET /patients/search`;
- the existing practitioner directory read/fallback;
- `POST /appointments/proposals/slot-search`; and
- `POST /appointments/proposals/bernie/supervised-booking`.

The meta-grid script has no arbitrary `fetch`, confirmation endpoint,
WebSocket, EventSource, service worker, browser persistence, voice or provider
primitive. In operational local mode it may explicitly hand an already
prepared proposal to the existing Bernie booking review. The meta-grid cannot
confirm. The existing review and backend command path retain identity,
availability, conflict, freshness, idempotency, audit, write and receipt
authority.

### Backward Compatibility

`compatible`

No public contract changed. Existing Diary and confirmation paths remain
available and unchanged. Smoke mode cannot hand off, call confirmation or
produce a receipt.

## 5. Responsive, privacy and keyboard result

The canonical browser evidence is
`orchestration/prototypes/bernie-functional-meta-grid/browser-acceptance-evidence.json`.
It records the real native Diary smoke route without API interception.

| Viewport | Result |
|---|---|
| desktop 1440×900 | focused root, time refinement, patient timeline and ordinary fallback passed |
| tablet landscape 1024×768 | rail plus canvas, availability, touch selection, proposal review and two-lane aligned comparison passed |
| tablet portrait 768×1024 | stacked shell, refinement, exact back restoration and proposal review passed |
| phone portrait 390×844 | timeline, availability, Space selection, proposal review, clarification, privacy, interruption/reconciliation and fallback passed |
| phone landscape 844×390 | single-column shell, one visible comparison lane and visible next/previous navigation passed |

All five viewports recorded zero page and meta-grid horizontal overflow, zero
enabled controls below 44 CSS pixels and no relevant console warning/error.
The phone composer remained sticky, focused and visible, with a
`visualViewport`-driven software-keyboard inset.

Keyboard evidence passed for Enter request submission, Space selection and
Escape explanation dismissal with focus restoration. The computed native tab
sequence follows visual and DOM order through the stable shell, current
projection and fallback controls.

The ordinary privacy control masks sensitive content immediately. The real
blur/visibility handler and an acceptance-only, doubly gated smoke control use
the same interruption function. Interruption masks, marks the projection
stale, clears selection/proposal state and exposes only a fresh-read recovery
action. The acceptance control is hidden unless both `smoke=true` and
`meta_grid_acceptance=true` are present.

## 6. Deterministic and regression evidence

The final serial population passed **101 tests**:

- functional meta-grid artifact, boundary, accessibility and evidence guards;
- API Spine artifacts and existing confirmation-client checkpoint;
- accepted meta-grid concept guards;
- Stage 3A artifact guards;
- existing accessible confirmation guards;
- live handover/archive guards; and
- Ariadne orchestrator preflight guards.

Node syntax checks passed for the two Diary JavaScript files. Focused Ruff and
`git diff --check` passed. Exact blocked-primitive and closed API/database diff
scans were clean.

The final browser screenshots and their SHA-256 hashes are committed with the
canonical browser evidence. They contain authored-synthetic names only.

## 7. Correction record

Rendered validation found and Sol corrected these bounded mechanical defects:

1. full-name patient resolution initially delegated a two-token smoke query to
   a one-field matcher;
2. a new availability root containing “after 2 pm” was initially mistaken for
   a refinement of the current projection;
3. colliding smoke practitioner identifiers initially hid the comparison
   practitioner;
4. the browser automation surface did not synthesize native button activation,
   so explicit standards-compatible Enter/Space handlers were added;
5. Escape initially worked only while the request field held focus;
6. cancelled rows were initially present in the focused projection despite its
   stated omission;
7. the tablet-landscape breakpoint initially stacked rather than retaining
   rail plus canvas; and
8. phone-landscape comparison initially hid its next/previous controls.

Every correction stayed inside the frozen client contract and was followed by
focused and combined reruns.

## 8. Closed boundaries and next decision

The tranche did not open or change:

- protected holdouts v1-v10 or historical Diary material;
- providers, external prompts, design-model subscriptions or costs;
- PII or real practice/patient data;
- API, GraphQL, OpenAPI/Pydantic or database authority;
- confirmation, appointment write, autonomous action or receipt authority;
- event producers, consumers, outbox, attention runtime or subscriptions;
- Stage 3B, representative participants, voice or ambient listening; or
- production, deployment or release.

The baton returns to Yuri. A sensible next fresh decision is whether to
authorise a bounded provider-free live-local synthetic integration/evaluation
tranche over the already existing read and proposal-only endpoints, followed
by Yuri's focused review of the working client. It should not add an API,
confirmation/write authority, event runtime, provider, PII, Stage 3B,
deployment or release surface.
