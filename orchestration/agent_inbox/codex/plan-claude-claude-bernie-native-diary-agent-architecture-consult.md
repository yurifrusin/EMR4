# plan-claude-claude-bernie-native-diary-agent-architecture-consult

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-bernie-native-diary-agent-architecture-consult` |
| Status | pending_plan_review |
| Created | 2026-07-03 15:09 +1000 |
| Source HEAD | `b4211da` |

## Plan Summary

Fable 5 consult: make Bernie native by unifying the diary domain's action grammar - one capability catalog, one evidence-gated confirm path, one deterministic authority - with Bernie as intent compiler and narrator, not a bolted-on chatbot lane. Four-sprint path; GraphRAG advisory-only and deferred. Plan-only.

## My Understanding

Sprints 104-107 built the right primitives (typed frames, reception policy, session contract, capability registry) but the grammar is split three ways: human UI proposals confirm via open raw PUT/POST, Bernie has its own evidence-gated confirm-bernie lane, and the capability registry lives in Bernie's package though its actions are diary-domain actions. Freshness ids are unsigned hashes with a None-is-fresh compat backdoor.

## Intended Surface / Boundary

Consulting plan only. Future implementation surface: new app/services/diary/ domain package, app/services/bernie/ package, appointments.py Bernie/proposal sections, docs/diary/diary.js Bernie panel and confirm flows, tests. Must-not-change surfaces: diary grid geometry, booking modal layout, Waiting Room cards, taskpane, Word surfaces.

## Out Of Scope

No production code, migrations, UI changes, route/schema changes, autonomous booking, voice lanes, GraphRAG store, or XState in this phase. Stop after plan-packet submit.

## Files I Expect To Edit

orchestration/agent_inbox/codex/plan-claude-claude-bernie-native-diary-agent-architecture-consult.md and the source task packet status/notes only.

## Implementation Steps

Full plan body in the packet: domain boundaries; native action grammar; event/state model; deterministic authority; Bernie reasoning/language; guardrails; UI rendering; session-persistence entry point; signed stateless evidence; GraphRAG boundaries; migration path; sprints N1-N4 with N1 (catalog rehome + typed action envelopes, no behaviour change) recommended first.

## Visual / Behavioural Acceptance Checks

Packet contains every section the task packet Verification list requires; no production files touched; explicit pause-before-execution note; submitted via protocol submit command.

## Risks / Ambiguities

Rehoming churn; unified confirm is a breaking flow needing versioned backend-first rollout; persisted session still blocked on PHI retention decision; GraphRAG scope creep; diary.js monolith size.

---

# Full Consulting Plan — Bernie as a Native Agentic Layer of the Diary Domain (Claude Fable 5)

> **Pause before execution.** This is a plan-only consulting packet. Nothing below
> is authorization to implement. Implementation may begin only after Yuri reviews
> this plan with Ariadne and a specific sprint packet receives its own plan gate
> and an explicit `complete sprint task` release.

## 1. Evidence Base

Read for this consult (read-only; no production tests run, none needed):
`AGENTS.md`, protocol alerts, `orchestration/parallel_workstreams.md` (Sprints
96–107), `orchestration/sprint_closeout.md` (Sprint 107 + Sprint 108 candidate),
`orchestration/bernie_interaction_model.md`, the accepted Sprint 106 consult
plan (`plan-claude-claude-bernie-reception-domain-copilot-architecture-consult.md`),
the full `app/services/bernie/` package (`capabilities.py`, `session.py`,
`policy.py`, `frames.py`, facades), `app/services/bernie_turn_evidence.py`,
the `app/routers/appointments.py` endpoint surface (all 24 routes mapped;
proposal/confirm flows at lines ~832–4460), and the `docs/diary/diary.js` call
sites for proposal endpoints, `BernieSession`, and the drag/resize
proposal-then-raw-PUT flow (~6575–6630).

## 2. Where I Agree, and Where I Push Back

This consult was asked to knock heads. Four positions, stated plainly:

**2.1 Agree with Yuri's instinct — but the diagnosis is sharper than "chatbot
bolted on".** The native grammar Yuri wants already *half-exists*: every human
diary mutation (booking modal, drag/move/resize, cancel, status, waiting-area)
already flows through typed proposal endpoints. The actual defect is that the
domain has **three confirmation grammars for one set of actions**:

1. *Human UI lane:* `POST /proposals/update/{id}` → confirm dialog → **open raw
   `PUT /appointments/{id}`**. The write endpoint never sees the proposal; a
   client can skip the proposal entirely; no evidence is echoed.
2. *Bernie lane:* interpret → supervised-booking → `POST
   /proposals/create/confirm-bernie` with candidate/proposal freshness ids and
   a fail-closed staleness gate.
3. *Raw API lane:* `POST /appointments`, `PUT/PATCH/DELETE /{id}` remain open
   direct mutations.

Bernie is not a chatbot bolted onto the diary; Bernie is currently the **only
client speaking the diary's best grammar**. The fix is not more Bernie
machinery — it is promoting the Bernie-grade grammar (typed proposal +
evidence-gated confirm + domain event) to be *the* diary write grammar, with
the human UI and Bernie as two authors of the same actions. Bernie becomes
native by symmetry, not by special-casing.

**2.2 Disagree with the current package homes (including my own Sprint 106A
placement).** `BERNIE_CAPABILITY_REGISTRY` lives in
`app.services.bernie.capabilities`, but `propose_booking`, `propose_edit`,
`propose_cancel`, `find_slots`, and `explain_schedule` are **diary-domain
actions** — the human UI performs the same actions with no Bernie involved.
Same for canonical temporal policy (`app.services.bernie.temporal`): "is 15:00
past clinic close on this date" is a diary fact, not a Bernie fact. Keeping
these under Bernie's namespace is exactly the "bolted-on" shape Yuri is
reacting to, expressed as module paths. They should be rehomed to a diary
domain package with import-compat facades; Bernie's package keeps only what is
genuinely Bernie: interpretation, session statechart, reception policy over
frames, and narration.

**2.3 Push back on one reading of "native agentic layer": no autonomous tool
loop.** Ariadne's constraint is right and should be strengthened into a
mechanism: Bernie is a **compiler and a narrator**. The LLM compiles natural
language into a typed action intent (which capability, which typed arguments,
which confidence flags) and narrates typed outcomes in the receptionist voice.
Capability *sequencing* is deterministic orchestration validated by the
transition table; the LLM may *propose* the next transition, never execute
one. A mutating capability is reachable only through the staff-confirmed,
evidence-gated confirm path regardless of who authored the intent. "Agentic"
means the diary domain natively speaks actions any agent can author — not that
an agent free-runs over tools.

**2.4 Push back on GraphRAG timing, agree on its boundary.** Ariadne's rule
(GraphRAG must never decide whether a slot is free) is correct and this plan
gives it an enforcement mechanism (§12). But EMR4 should not build a graph
store yet at all: the relational schema plus typed frames *is* the practice
knowledge graph for everything Bernie currently needs. The right first step is
a typed practice-facts layer, not a vector/graph deployment (§12.3).

**2.5 A real gap found during review (fold into the grammar work):**
`bernie_turn_evidence.py` freshness ids are truncated unsigned SHA-256 content
hashes ("not cryptographic; not used for auth"), and `check_staleness` treats
a missing echoed id as **fresh** (Sprint 104 back-compat). Today that is
defensible — same-origin staff UI, RBAC on every route. The moment the confirm
path becomes the *only* write path (§14 N3), evidence must be HMAC-signed with
the server secret and the None-is-fresh path must close for grammar-routed
confirms. Evidence should carry trust; the session store (§10) carries memory.

## 3. Proposed Domain Boundaries

Three bounded homes plus the router as a thin adapter:

- **`app/services/diary/` (new) — the diary domain.** Owns what is true and
  what can be done: the **action catalog** (rehomed capability registry,
  §4), **deterministic authority** (slot search, conflict checks, roster/
  `DiaryRoster` reads, canonical temporal policy rehomed from
  `bernie/temporal.py`), **schedule explanation** (`explain_schedule`),
  **typed action envelopes** (§4.2), and the **domain event vocabulary**
  (§5.1). No LLM imports, no copy strings, no HTTP.
- **`app/services/bernie/` (existing) — the reception agent.** Owns
  interpretation (NL → typed action intent), the booking-session statechart
  (`session.py`, unchanged design), reception context frames + policy
  (`frames.py`, `policy.py` — these stay here for now: they describe a
  *reception turn*, not the diary; revisit only if the diary UI starts
  building frame sets itself), narration/voice responsibilities (§7), and the
  pilot gate. Bernie *imports from* the diary domain; the diary domain never
  imports Bernie.
- **`docs/diary/` — presentation.** Renders typed state; owns no availability
  or policy logic (§9).
- **`app/routers/appointments.py` — adapter.** Auth, RBAC, request/response
  models, delegation. The 4,465-line router keeps thinning as logic moves to
  the two packages (continuing Sprint 106A's direction).

Multi-agent placement: **Rayleen** (auto-arrival daemon) is a headless caller
of diary-domain read actions plus a future `execute_with_report` tier — no
Bernie import. **Scribe/Consultant** live on the Word/clinical surface and
never touch the diary catalog; they share only the Access AI capability/audit
pattern. **Davida** spans domains and consumes the diary catalog as one of
several per-domain catalogs — the catalog-per-domain pattern *is* the
multi-agent architecture, which is why the catalog cannot live inside one
agent's package.

## 4. Native Diary Capability/Action Grammar

### 4.1 One catalog, two authors

Rehome `BERNIE_CAPABILITY_REGISTRY` → `app/services/diary/actions.py` as the
**diary action catalog**. Split entries by true owner:

| Action | Tier | Author today | Notes |
|---|---|---|---|
| `find_slots` | read_only | UI + Bernie | existing slot-search proposals |
| `explain_schedule` | read_only | UI + Bernie | Sprint 108 candidate; first grammar-first capability |
| `get_patient_booking_context` | read_only | Bernie | UI may consume later |
| `suggest_next_actions` | read_only | Bernie | typed chips |
| `propose_booking` | propose | UI (`/proposals/create`) + Bernie (supervised wrapper) | one action, two authors |
| `propose_edit` (move/extend/resize) | propose | UI drag + modal | Bernie gains authorship in N3+ via the same action |
| `propose_cancel` / `propose_status` / `propose_waiting_area` | propose | UI | same |
| `confirm_action` | confirm | Bernie only today | generalizes `confirm-bernie`; becomes the domain's single write gate (N3) |
| `check_in_patient` | execute_with_report (future) | Rayleen/UI | low-risk reversible tier from the interaction-model doc |
| `handoff_to_receptionist` | meta | Bernie | terminal |

Bernie-only capabilities (`interpret_instruction`, `resolve_patient`,
`resolve_practitioner`) stay in a small Bernie-side registry that *references*
diary actions — the agent knows how to author intents; the diary knows what
actions exist.

### 4.2 Typed action envelopes

Three envelope contracts in the diary package, versioned like the frame set
(`diary.action.v1`):

- `DiaryActionIntent` — action name, typed arguments, author
  (`staff_ui | bernie | rayleen | ...`), authenticated actor, context
  evidence refs (turn_ref, frame refs).
- `DiaryActionProposal` — the deterministic result: command payload,
  warnings/blocks (typed reason codes), `proposal_freshness_id`,
  `requires_confirmation`, expiry.
- `DiaryActionConfirmation` — proposal id + echoed evidence + confirmed
  warnings; validated fail-closed by the staleness/signature gate.

Existing proposal endpoints keep their response models; envelopes are the
internal lingua franca first, wire contract later (N3). This is how "booking,
extending, moving, explaining unavailability, offering alternatives" become
domain DNA: each is a catalog row plus an envelope flow, identical no matter
which surface or agent authored it.

## 5. Event/State Model

Three layers, strictly ordered by authority:

### 5.1 Diary domain events (ground truth)

Typed event vocabulary in `app/services/diary/events.py`:
`AppointmentCreated/Updated/Moved/Extended/Cancelled/StatusChanged/
WaitingAreaChanged`, `ProposalPrepared/Confirmed/Expired`, `RosterChanged`,
`ScheduleTemplateChanged`. Initially these are **views over
`AppointmentAuditLog` rows plus emit points in the confirm path** — no new
table until N4 decides the event-log persistence question together with the
session table. Domain events are what make staleness *derivable* instead of
asserted: a candidate snapshot is stale iff a domain event affecting its
(practitioner, date) coordinates postdates it.

### 5.2 Bernie session statechart (conversation memory)

`session.py` as shipped is the right design: semantic states, client events
validated by `CLIENT_EVENT_TRANSITIONS`, server advances bounded by
`SERVER_ADVANCE_TARGETS`, the statically-checkable invariant that `confirmed`
is reachable only via `confirmation` from `proposal_preview`. No change to the
state set. What changes over N3–N4: session evidence fields reference unified
proposal ids, and `diary_navigated`/staleness marking keys off domain events
(§5.1) rather than UI guesswork.

### 5.3 UI presentation state

Panel open/closed, composer mode, disclosure expanded, auto-preview toggle —
frontend-only, per the session.py docstring. Everything semantic renders from
`reception_policy` + session state (§9).

## 6. Deterministic Scheduling/Roster Authority

Unchanged in principle, consolidated in location: slot search, conflict
checking (`_overlaps`), roster/`DiaryRoster` resolution, break handling, and
temporal policy (same-day windows, week-relative resolution, clamping) are the
**only** sources of availability truth, and all live in the diary domain
package. Enforcement points that already exist and must be preserved verbatim:

- `evaluate_reception_context` classifies availability **only** from
  `roster_schedule` and `slot_search` frames; "no matching times" requires a
  proven `searched_no_candidates` frame (the Sprint 107 invariant).
- The LLM never authors `roster_schedule`, `slot_search`, or
  `guardrail_outcome` frames — frame `source` literals already constrain this
  in the type system; add an explicit test that rejects model-sourced
  availability frames (§16).
- `find_slots` and `explain_schedule` are read_only catalog entries with no
  LLM in the loop.

## 7. Bernie Reasoning and Language Responsibilities

Bernie's LLM does exactly three jobs:

1. **Compile** staff language into a `DiaryActionIntent` (which action, typed
   arguments, explicit-vs-inferred flags, confidence axes). Missing fields →
   clarification state, never invention. Omitted-date resolution stays in the
   deterministic transition table (`resolve_booking_date_transition`), not the
   prompt.
2. **Clarify** — choose the *question*, not the answer: when policy says
   `must_ask_clarification`, Bernie phrases the question over the typed
   ambiguity (patient candidates, ambiguous day, missing duration).
3. **Narrate** typed outcomes in the receptionist voice — friendly, familiar,
   professional, terse. Baseline copy is the deterministic catalog keyed by
   `(session_state, reason_code)` (Sprint 108 candidate). A later optional
   LLM *paraphrase lane* may rephrase catalog copy for conversational warmth
   under a hard constraint: every date, time, name, and count token in the
   narration must appear in the typed frame set/policy payload (template-fill
   verification, §16). If verification fails, fall back to catalog copy. The
   deterministic catalog ships first; the paraphrase lane is a separate,
   later, optional sprint.

Bernie never: computes availability, self-assigns trust bands, selects a
mutating capability without staff confirmation, or emits copy contradicting a
policy predicate.

## 8. Transition-Table/Guardrail Responsibilities

- **Session transition table** (`session.py`): which client events are legal
  in which states; invalid → typed 409-shaped rejection. Guards conversation
  shape.
- **Reception policy** (`policy.py`): copy-free predicates over typed frames
  (`can_offer_candidates`, `must_block_confirmation`,
  `advisory_warnings_only`, availability classification). Guards what may be
  *offered*.
- **Evidence gate** (`check_staleness`, upgraded per §11): guards what may be
  *written* — fresh, signed, reference-date-matched proposal evidence, fail
  closed. Stale evidence after diary navigation, roster change, or competing
  booking is caught here even if every upstream layer misbehaves.
- **Irreversibility tiering**: cancel/delete and any future irreversible
  action are always `propose` tier with explicit confirmation; no
  `execute_with_report` shortcut ever applies to them. Encoded as catalog
  data, testable.
- **RBAC/audit**: unchanged at the route layer; actions carry audit codes in
  the catalog so every confirm writes an attributable audit row (staff user +
  session id, per the interaction-model doc).

Layered defence, in order: transition table (conversation) → policy (offer) →
evidence gate (write) → RBAC/audit (accountability). UI render states are
deliberately *not* a guardrail layer (§9).

## 9. UI Rendering Responsibilities

Continue the Sprint 107 direction to its end state:

- The diary renders **typed state, never inferred state**: `reception_policy`
  predicates and reason codes drive Bernie panel states; session state drives
  flow position; domain data drives the grid. No message sniffing, no
  availability inference in JS.
- One copy catalog keyed by `(state, reason_code)` replaces
  `BERNIE_STATUS_COPY`/`BERNIE_HEADLINE_COPY`/block-code sniffing (Sprint 108
  candidate). Technical evidence stays behind Details disclosure.
- The confirm affordances for human mutations (drag/move/extend dialogs)
  progressively adopt evidence echo (N3): the dialog submits the proposal's
  freshness evidence instead of re-posting an unverified raw payload.
- Long-run (post-N4): the Bernie panel becomes render-from-server-session
  state and the legacy `syncToLegacy`/`syncFromLegacy` globals are deleted.
- Must-not-change surfaces throughout: diary grid geometry/lanes, booking
  modal layout, Waiting Room cards/panels, status controls, taskpane, Word
  surfaces.

## 10. Where Persisted Server-Side Session State Enters

At **N4, after the grammar unifies — not before.** Reasoning: a session row's
most valuable fields are references to proposals, candidates, and domain
events. Persisting sessions before the unified action/proposal ids exist means
migrating the table's foreign shape twice. Prerequisites that remain Yuri/
Ariadne decisions before N4 lands (unchanged from the Sprint 106 consult, now
with a deadline attached to a specific sprint):

- PHI/retention classification of session rows (they hold patient ids +
  instruction text);
- TTL/cleanup policy and what "abandoned session" means operationally;
- concurrency rule (recommend: one active booking session per staff user per
  surface; a new `staff_instruction` in a terminal/stale session forks a new
  session id).

The session table and the domain event log (§5.1) should land in the same
migration decision — they are the same audit substrate, and both are hard
requirements for any future limited auto-mode.

## 11. Where Signed Stateless Evidence Remains Useful

Permanently — the session store never replaces it. Division of labour:
**evidence carries trust; the session carries memory.**

- Candidate/proposal freshness ids remain stateless and verifiable per
  request: the confirm gate must hold even if the session row is missing,
  expired, or the store is degraded (fail closed on evidence, not on session
  presence).
- Upgrade at N3: HMAC-sign the evidence (server secret, practice-scoped,
  short expiry window) and close the None-is-fresh back-compat path for
  grammar-routed confirms. Content-hash determinism is kept *inside* the
  signed payload so identical slots still produce comparable ids.
- Signed evidence is also the future substrate for confirms that arrive from
  outside the live UI session: SMS "reply YES" confirmations, kiosk flows,
  patient portal holds — all places a server session cookie/row cannot reach.
- Replay/audit: a signed proposal token in the audit row lets any later
  reviewer verify what exactly was confirmed without trusting the DB row's
  mutable neighbours.

## 12. GraphRAG — How It Should and Should Not Be Used

### 12.1 Never (hard boundary, mechanically enforced)

GraphRAG/knowledge-graph/vector retrieval must never decide availability,
slot validity, conflicts, roster state, or temporal policy. Enforcement is
already latent in the frame type system — make it explicit: **retrieval- or
graph-sourced facts may only enter a Bernie turn as `advisory_warning` (or a
future `knowledge` frame type) with source attribution; `evaluate_reception_
context` derives availability classification exclusively from `roster_
schedule`/`slot_search` frames.** A graph fact can therefore colour narration
("Mrs Thompson usually sees Dr Shera") but can never flip
`can_offer_candidates` or produce a no-slot state. Add the adversarial test
(§16) so this survives future refactors.

### 12.2 Where it genuinely helps (later)

- **Practice knowledge for narration/explanation**: fee policies, "Dr Shera
  doesn't do procedures on Fridays", new-patient rules — as advisory frames
  feeding Bernie's clarifications and Davida's onboarding answers.
- **Workflow explanations**: "why do we double-book flu clinics" — Davida
  territory.
- **Patient relationship context**: family/carer links for reception
  conversations ("book Billy and his mum back-to-back") — advisory only;
  identity linking still goes through recognition + staff selection.
- **Cross-agent shared substrate**: one knowledge layer serving Bernie
  (reception), Rayleen (arrival heuristics as advisories), Consultant
  (clinical retrieval has its own separate safety review), and Davida
  (practice management) — consistent with the existing pgvector/rag models
  and the Access AI capability pattern.

### 12.3 Where to start (dissent on timing)

Not with a graph store. Start with a **typed practice-facts table**
(practice-scoped, structured advisories keyed by reason codes, CRUD by
practice admin) surfaced as advisory frames. It is auditable, deterministic,
and covers most of what a graph would return for a single practice. Adopt
GraphRAG only when a real unstructured multi-hop corpus exists (practice
manual, policies, correspondence) and at least two agents need it. Davida's
onboarding skill is the natural first consumer; that is the right time, and
it is not now.

## 13. Migration Path From the Sprint 104–107 Shape

Everything shipped stays load-bearing; nothing is thrown away:

- Sprint 104's patient context and clarification turns → unchanged inputs to
  the compile/clarify stages.
- Sprint 105's turn refs + freshness ids + staleness gate → upgraded (signed)
  and generalized into the domain confirm gate (N3).
- Sprint 106A's bounded package + facades → the extraction pattern reused for
  the diary package; Bernie facades keep import paths stable.
- Sprint 106B's canonical temporal policy → rehomed to the diary domain with
  a facade left behind (the module is already single-source; only its address
  changes).
- Sprint 106C's typed frames + 107's reception-policy UI → unchanged
  contract; the UI keeps consuming `reception_policy`; new reason codes from
  `explain_schedule` extend rather than replace it.
- The queued Sprint 108 candidate (schedule explanation + copy catalog) is
  absorbed as N2, implemented grammar-first.

## 14. First Sprints (each separately plan-gated)

| Sprint | Content | Risk | Behaviour change |
|---|---|---|---|
| **N1 — Diary action catalog + envelopes** | Create `app/services/diary/`; rehome capability registry as the action catalog with human-UI actions added (`propose_edit`, `propose_cancel`, `propose_status`, `propose_waiting_area`); rehome temporal policy with facade; add `DiaryActionIntent/Proposal/Confirmation` envelope models (internal only); catalog-completeness contract test over the router | Low | None (pure moves + additive contracts; suite green unchanged) |
| **N2 — `explain_schedule` + copy catalog** (absorbs Sprint 108) | Typed schedule explanation (no roster row / day off / breaks / fully booked / outside hours) as a catalog action in the diary package; reason codes flow through frames → policy → diary copy catalog keyed `(state, reason_code)`; both Bernie narration and the diary's roster-unavailable states consume it | Medium-low | Copy/diagnostics improve; no write-path change |
| **N3 — Unified evidence-gated confirm** | Generalize `confirm-bernie` into the diary's confirm for grammar-routed mutations; human move/extend/cancel dialogs echo proposal evidence; HMAC-sign evidence + close None-is-fresh for the new path; legacy raw endpoints kept through a deprecation window; backend-first deploy ordering | High | Human confirm flow semantics; the "grammar becomes DNA" sprint |
| **N4 — Persisted session + domain event log** | The deferred Sprint C, now keyed to unified proposal/action ids; session table + event emission in one migration decision; UI starts rendering server session state; requires the §10 Yuri decisions first | High | Session semantics move server-side |

**First implementation sprint recommendation: N1.** It is a
no-behaviour-change slice in the proven Sprint 106A extraction pattern, it
corrects the package-home mistake while it is still cheap (one importing
consumer), and every later sprint builds on its contracts. If Yuri prefers a
visible win first, N2 can run before N1 without harm — at the cost of landing
`explain_schedule` under Bernie's namespace and paying a second (small) move
later. Deferred beyond this plan: voice lanes, wake word, limited auto-mode,
LLM paraphrase lane, patient-details verification statechart, GraphRAG store,
API-spine review, XState.

## 15. Risks

- **N3 is a breaking flow change** for the diary UI's write paths. Mitigate:
  versioned rollout, backend accepts both paths during the window, Pages
  deploys after backend, deterministic smoke coverage of both paths during
  the window.
- **Rehoming churn** (N1): many import sites move. Mitigate: facades, pure
  moves with no logic edits in the same commit, unchanged-suite rule.
- **Grammar over-engineering**: the envelope layer could drift into a
  framework. Boundary: catalog is data + Pydantic contracts; no plugin
  system, no dynamic dispatch registry beyond a dict lookup, no new runtime
  dependency.
- **Persisted-session prerequisites** (PHI retention, TTL, concurrency) are
  Yuri decisions that block N4; flagging them now prevents N4 stalling
  mid-sprint.
- **GraphRAG scope creep**: the advisory-only rule needs its adversarial test
  landed *before* any retrieval integration exists, so the boundary is
  enforced from day one.
- **diary.js at 8.1k lines**: render-from-state migration (N4 tail) is risky
  in a monolith; carve the Bernie panel into a clearly-bounded section (or
  separate file) as part of N4 planning, not as a side effect.
- **Evidence signing key management**: HMAC secret rotation and
  practice-scoping need a config story (existing `SECRET_KEY` posture is the
  starting point); expiry windows must tolerate legitimate slow reception
  workflows (minutes, not seconds).

## 16. Acceptance Checks

- **Catalog completeness** (N1): a test enumerates every mutating
  `appointments.py` route and asserts a catalog action exists with tier and
  confirmation requirement; fails on any future uncataloged mutation.
- **Availability provenance** (N1, guards §12): property-style test feeding
  `evaluate_reception_context` adversarial frame sets — no
  advisory/model-sourced frame combination may yield
  `search_ran_no_candidates`, `roster_unavailable`, or flip
  `can_offer_candidates`; model-sourced `roster_schedule`/`slot_search`
  frames are rejected at the type layer.
- **Temporal single-source** (N1): both former clamp sites import the one
  rehomed module; table-driven tests cover after-hours same-day, partly-past
  clamping, and week-relative immutability.
- **Schedule explanation** (N2): each explanation reason code maps to
  distinct catalog copy; the Sprint 107 smoke invariants extend — no-slot
  copy only under proven `searched_no_candidates`, roster-unavailable copy
  under `roster_unavailable`, and the new "day off / breaks / fully booked"
  variants render distinctly.
- **Confirm integrity** (N3): no grammar-routed event sequence reaches a
  write without fresh, signature-valid, reference-date-matched evidence;
  tampered or expired evidence → typed 409; missing evidence on the new path
  → typed 409 (None-is-fresh closed); session-transition property from the
  Sprint 106 plan (`confirmed` only via `proposal_preview` with fresh
  evidence) becomes executable.
- **Narration constraint** (paraphrase lane, if/when built): every
  date/time/name/count token in narrated copy must appear in the typed
  frame/policy payload; failure falls back to catalog copy — verified in
  tests before the lane ships.
- **No-behaviour-change sprints** (N1): full backend suite green unchanged;
  `git diff`-reviewable pure moves; JSON responses byte-identical.
- **UI harness**: `review/test_diary_smoke.py` remains the deterministic
  gate; each sprint adds structural assertions rather than screenshot checks,
  per the cost-conscious review rule.

## 17. Dissent Recorded

- The capability registry and temporal-policy rehome reverses part of my own
  Sprint 106A/B placement; I consider the original placement a mistake made
  visible by Yuri's "native grammar" framing, and moving now (one consumer)
  is far cheaper than after Rayleen/Davida start importing.
- I recommend N1 before the queued Sprint 108 content; Ariadne may reasonably
  invert (visible progress first) — both orders are safe, the inversion just
  pays one extra small move.
- I decline to recommend any GraphRAG build now, despite it being in the
  consult brief's option space; the typed practice-facts table is the honest
  first step and the graph earns its place only with a real multi-hop corpus
  and a second consuming agent.
- The LLM paraphrase lane (§7) is deliberately optional and last; if Yuri
  wants Bernie's voice to feel warmer sooner, invest in the copy catalog's
  wording first — it is auditable and free.

## 18. Pause Before Execution

This packet is consulting output only. No production code, migrations, UI, or
schema changes were made. Next action belongs to Ariadne and Yuri: review,
amend, and — only if approved — dispatch individual sprint packets, each with
its own plan gate and explicit `complete sprint task` release.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
