# Reception One combined-scope product proof closeout

**Final result:** `reception_one_combined_scope_pass`  
**Decision owner:** Yuri  
**Conductor, recovery and acceptance owner:** GPT Sol  
**Final reviewed candidate:** `e675e7d21a8eb7b0fbc514773bb875c97269e5ac`  
**Date:** 2026-07-21

## 1. Outcome

The bounded Reception One client now proves the ordinary combined request as
one visible proposal-only interaction:

> Show me all the available slots with Dr Shera for a half-hour appointment
> with Margaret Thompson after 2 today.

The client resolves Margaret Thompson and Alex Shera, interprets half-hour as
30 minutes and unqualified `after 2` as 2:00 pm in the daytime Diary, and shows
all five dimensions in one current scope before returning real backend
availability. After staff selects a candidate, the visible action is `Prepare
proposal for Margaret Thompson`; it prepares the existing supervised-booking
proposal without requiring the receptionist to type the patient again.

The meta-grid still cannot confirm or write. Acceptance stops at the visible
`proposal_not_committed` review, and automation never activates the existing
booking-review handoff.

## 2. Contextual refinement and state safety

The same root interaction passed:

- `tomorrow instead`, retaining patient, practitioner, duration and time;
- `make it 45 minutes`, retaining patient, practitioner, date and time; and
- `after 3`, retaining patient, practitioner, date and duration.

New root requests do not inherit an identity merely because it exists in the
in-memory patient map; a projection carries patient context only through its
explicit `scope.patient_ids` and freshly resolved item context.

Selection, proposal, privacy and interruption behaviour remains reversible:

- selection does not reserve or book;
- a non-selection projection clears the current selected item;
- Back may deliberately restore an earlier selection only when returning to
  that earlier selection projection;
- privacy masks patient-bearing scope, proposal/action and history surfaces and
  gives the live region a patient-free message; and
- interruption clears selected-slot and proposal state, then requires fresh
  patient resolution and fresh backend availability before proposal work may
  resume.

## 3. Sol recovery after the first veto

The first fresh Gemini review passed candidate
`3742d11df811efe3e1f0a480ffbbd090def7ff44`. Sol did not accept it immediately.
A post-veto state trace found that refining after selecting a slot rendered a
fresh availability answer but left `state.selectedItem` in memory. A later
typed proposal instruction could therefore have used the refined-away slot.

Sol recorded the finding in
`orchestration/agent_inbox/codex/reception-one-combined-scope-proof-post-veto-sol-amendment.md`,
cleared selected state on every incoming projection other than selection or
proposal review, added a real select-then-refine browser assertion, regenerated
the evidence and required a second fresh veto. The first review remains
preserved provenance but is superseded for acceptance.

Gemini 3.5 Flash/high then reviewed amended candidate
`e675e7d21a8eb7b0fbc514773bb875c97269e5ac` from a new clean Antigravity
worktree and returned `pass` with no material state, privacy, evidence or
authority finding. Its worker receipt and full report text are preserved in
`orchestration/agent_inbox/antigravity/reception-one-combined-scope-proof-gemini-veto-2.md`.
Sol narrows its final recommendation: this passes only the bounded combined-
scope product proof; it does not advance or reopen Stage 3A, Stage 3B, provider,
write, deployment or release authority.

## 4. Real local browser/backend/PostgreSQL evidence

The final task-scoped Playwright run used a real Chromium browser, the ordinary
visible Diary UI, loopback FastAPI and PostgreSQL, with no `page.route(...)`,
API interception or page-internal command invocation. Its strict label is
`live_local_browser_backend_postgres`.

IPv6 loopback `::1:3000` and `::1:8001` isolated this run from Yuri's existing
IPv4 `127.0.0.1` review servers. The committed Diary adds only the corresponding
narrow loopback bootstrap/backend mapping; non-loopback behavior is unchanged.

The final evidence at
`orchestration/prototypes/bernie-reception-one-combined-scope-proof/browser-acceptance-evidence.json`
records:

- desktop landscape 1440×900;
- tablet landscape 1024×768;
- tablet portrait 768×1024;
- smartphone portrait 390×844;
- smartphone landscape 844×390;
- six hashed screenshots with complete painted raster extents;
- exact combined-scope, contextual refinement, touch, keyboard, privacy,
  interruption, Back and ordinary full-Diary fallback results;
- zero horizontal page or host overflow at every viewport;
- no enabled control below 44×44 CSS pixels;
- zero browser console warnings/errors or page errors;
- only loopback requests, no forbidden request and no failed API response; and
- observed patient search, practitioner/Diary reads, slot-search proposals and
  supervised-booking proposals, with no confirm, session, event or appointment
  mutation call.

The machine JSON is sanitized: it records no patient name, date of birth,
patient identifier, token, password or credential. Screenshots contain only
the newly authored synthetic identities.

## 5. Zero-write and cleanup evidence

The exact disposable authored-synthetic database was
`gp_pms_reception_one_combined_scope_9c41b7e2_20260721`. The interpreter
provider was `disabled`, deterministic fallback was false, and cloud
credentials were blank.

Before/after counts and SHA-256 readback were identical. The final state was:

- appointments: 6 unchanged;
- appointment audit rows: 0;
- appointment command idempotency rows: 0;
- Bernie booking sessions: 0; and
- Bernie session events: 0.

After evidence capture, cleanup verified the exact synthetic ownership markers
and dropped only that database. The drop is irreversible but affected only the
authorised disposable synthetic database. Evidence is at
`orchestration/prototypes/bernie-reception-one-combined-scope-proof/database-cleanup-evidence.json`.

Yuri's active IPv4 review processes remained present and untouched throughout.

## 6. Final verification

After the post-veto amendment:

- combined-scope plus inherited functional/live-local focused tests: 30/30;
- focused product, Stage 1 proposal, API Spine, continuity and meta-grid
  population: 95/95;
- Diary regression population: 211/211;
- fresh Gemini amended-candidate veto: `pass`;
- Node syntax checks for `meta-grid.js`, `diary.js` and
  `office-bootstrap.js`: pass;
- Ruff on the new harness, runner and focused test: pass; and
- Ariadne continuity graph structural validation: pass.

Warnings were limited to the documented Starlette/httpx2 deprecation,
google-genai Python deprecation, and short synthetic test JWT key warnings.
No warning represents a new failure or authority opening.

## 7. Ariadne continuity result

The accepted node is `reception-one-combined-scope-proof`. Its inherited
`combined-patient-practitioner-time-duration-intent` contract is now
`satisfied` by the focused test plus the real local evidence. The historical
functional and live-local nodes retain their original narrower acceptance
claims and gap records; this descendant supplies the missing proof rather than
rewriting history.

The Continuity Engine remains advisory and did not accept work, create agents,
move refs or grant authority.

## 8. Boundaries preserved and next decision

No API, GraphQL, OpenAPI/Pydantic, database model/migration, appointment create,
confirm, cancel or delete, event runtime, product provider, PII, protected
holdout, historical Diary, Stage 3B, production, deployment, release, voice,
autonomous action, rename, artwork or trademark surface changed.

Reception One and meta-grid remain the provisional user-facing and architectural
terms respectively. Final visual/interaction design remains intentionally
unsettled. The baton returns to Yuri for focused review. Any high-fidelity
design synthesis, representative staff study, confirmation-path expansion or
further functional tranche requires its own explicit decision.
