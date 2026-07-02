# plan-claude-claude-bernie-reception-domain-copilot-architecture-consult

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-bernie-reception-domain-copilot-architecture-consult` |
| Status | pending_plan_review |
| Created | 2026-07-03 09:17 +1000 |
| Source HEAD | `80d51e7` |

## Plan Summary

Fable 5 architecture consult: extract Bernie into a bounded reception-domain package with a server-owned booking-session statechart, typed context frames, a formal capability/tool registry, one temporal-policy module, a copy catalog, and behaviour-named test consolidation - delivered as five no-behaviour-change-first sprints. Plan-only; no implementation in this phase.

## My Understanding

Bernie works but its domain logic has accreted inside app/routers/appointments.py (~1500 lines of inline resolution/policy), the statechart exists in docs but not in code (two half-machines: stateless backend turn refs + a warn-only frontend enum with legacy-global dual state), context frames are untyped trust-carrying dicts, same-day clamping is implemented twice, and tests are sprint-named history rather than a behavioural spec.

## Intended Surface / Boundary

Consulting plan only. Future implementation surface: new app/services/bernie/ package, appointments.py Bernie sections, docs/diary/diary.js Bernie panel state handling, tests/test_bernie_*.py. Adjacent surfaces that must NOT change in any proposed sprint: diary grid rendering/geometry, booking modal, Waiting Room cards, taskpane, Word surfaces.

## Out Of Scope

No production code edits, migrations, UI changes, route/schema changes, autonomous booking, voice lanes, auto-mode, XState dependency, GraphQL spine, or provider changes in this phase. Stop after plan-packet submit.

## Files I Expect To Edit

This phase: orchestration/agent_inbox/codex/plan-claude-bernie-reception-domain-copilot-architecture-consult.md and the source task packet status/completion notes only.

## Implementation Steps

See the full consulting plan body below: diagnosis of nine failure modes; capability/tool map; event/statechart boundary assignment; backend contract changes; UI voice/copy strategy; roster/schedule diagnostics tool; test strategy; five-sprint migration breakdown (A extraction, B typed frames, C server session, D capability registry + diagnostics + copy catalog, E test consolidation).

## Visual / Behavioural Acceptance Checks

Plan packet contains all sections required by the task packet Verification list; no production files touched; packet submitted via the protocol submit command; explicit pause-before-execution note present.

## Risks / Ambiguities

Server-side session state adds persistence/cleanup burden (dissent recorded); extraction refactor risk mitigated by no-behaviour-change rule with existing suite as characterization tests; envelope slimming is breaking for diary.js and must be versioned; test consolidation must migrate assertions before deleting sprint files.

---

# Full Consulting Plan — Bernie as a Reception-Domain Copilot (Claude Fable 5)

> **Pause before execution.** This is a plan-only consulting packet. Nothing below
> is authorization to implement. Implementation may begin only after Yuri reviews
> this plan with Ariadne and issues an explicit `complete sprint task` for a
> specific, separately dispatched sprint packet.

## 1. Evidence Base

Read for this consult (read-only, no production tests run): `AGENTS.md`,
`orchestration/protocol_alerts.md`, `orchestration/sprint_closeout.md` (Sprints
103–105 + Sprint 106 candidate), `orchestration/event_driven_statechart_architecture.md`,
`orchestration/bernie_interaction_model.md`,
`app/services/bernie_booking_interpreter.py`, `app/services/bernie_patient_context.py`,
`app/services/bernie_slot_normalizer.py`, `app/routers/appointments.py` (Bernie
sections in full: interpret route, `_resolve_bernie_interpretation_context`,
supervised-booking wrapper, confirm/no-slot endpoints), `app/schemas/appointments.py`
(Bernie/SlotSearch models), `docs/diary/diary.js` (`BernieSession` + panel logic),
`tests/test_bernie_transition_table.py`, test-suite inventory (20 Bernie test
files, ~6900 lines), and recent commits `a1865e6` / `1389579`.

## 2. Diagnosis — What Is Right, What Is Failing

### 2.1 What the current implementation gets right (keep these)

- **The LLM-as-translator discipline is real.** The interpreter only produces a
  `SlotSearchCommandIn`; slot search, conflict, and roster logic are fully
  deterministic. The live provider fails closed with deterministic fallback.
- **The pure normalizer** (`bernie_slot_normalizer.py`) is exactly the right
  shape: pure, typed, idempotent, well-tested.
- **Confidence axes + lattice-min decision policy** correctly avoid one scalar
  confidence gate, matching the architecture doc invariant.
- **Turn refs, candidate/proposal freshness ids, and the stale-confirmation
  gate** (Sprint 105) are the correct primitives for session integrity.
- **Compact `patient_booking_context`** (recognized-patient-only, capped, no
  notes text) is the right middle path between "one appointment" and "diary dump".
- **The date transition table** (`resolve_booking_date_transition`) is the first
  correct deterministic transition-table implementation and should become the
  template for the rest.

### 2.2 Failure modes (ranked by architectural cost)

1. **Domain logic lives in the router.** `appointments.py` is 4,249 lines;
   `_resolve_bernie_interpretation_context` (~480 lines) plus the supervised
   wrapper, identity resolvers, Levenshtein matching, temporal policy, duration
   defaults, and axis construction are inline route code. Every Bernie sprint
   bolts more logic into the same file. There is no bounded module named for the
   thing the architecture doc says exists ("the Bernie booking session").
2. **Two half-state-machines, neither authoritative.** The backend mints
   `turn_ref`s but holds no session state — each request rebuilds the world from
   client-echoed `context_frames` and `turns`. The frontend `BernieSession` class
   has a state enum and a transition map, but invalid transitions only
   `console.warn` and proceed, and state is mirrored into ~9 legacy globals via
   `syncToLegacy()`/`syncFromLegacy()` — a standing drift hazard. The documented
   statechart (recognition → context_enrichment → slot_search →
   candidate_selection → proposal_preview → confirmation) is emergent from
   scattered conditionals, not implemented anywhere as a machine.
3. **Context frames are an untyped trust boundary.** `context_frames:
   list[dict]` is scanned by string keys. `_context_frame_value` takes the first
   value for a key from *any* frame type, and a `patient_id` found this way is
   assigned band=**assume** ("resolved from trusted diary context"). The client
   asserts its own trust level. This is the single most safety-relevant gap:
   recognition confidence should be a server-side judgment over typed, validated
   frames, not a dict key the UI happens to send.
4. **Duplicated temporal policy.** Same-day clamp/exhaustion logic exists twice
   with slightly different shapes: interpret path (appointments.py ~1980–2023)
   and supervised wrapper (~3610–3710). Week-relative regexes exist twice
   (interpreter service and router). The "bare hour 1–11 → pm" business-hours
   assumption is applied silently inside `_parse_time_fragment` without emitting
   a `BernieAssumption`. Divergence between these copies is exactly the class of
   bug (the "tomorrow becomes tomorrow again" incident) this programme exists to
   prevent.
5. **A god-envelope response.** `BernieBookingInstructionInterpretOut` now
   carries command, normalization, axes, decision, assumptions, staff checks,
   patient candidates, booking context, freshness, debug, and turn_ref. Every
   sprint adds fields; diary.js must understand all of them. There is no
   versioning or client-capability story.
6. **Dual NL interpretation paths.** The deterministic (fake/fallback)
   interpreter's regex extraction and the live Gemini prompt must be maintained
   in lockstep by hand. The router then re-resolves practitioner/patient/date on
   top of whichever ran, so the LLM's marginal contribution today is small while
   its maintenance surface is doubled.
7. **UI copy is scattered ad hoc.** `BERNIE_STATUS_COPY`, `BERNIE_HEADLINE_COPY`,
   block-code sniffing (`provider_unavailable`), and per-function copy branches
   are spread through diary.js. There is no single (state, reason-code) → copy
   catalog, which makes the "calm, helpful, terse" voice requirement unauditable.
8. **Sprint-named test archaeology.** ~20 `test_bernie_*` files are named for
   sprints (97/98/99/100/104/105), encoding contract history rather than
   behaviour. New work must satisfy assertions whose intent is only recoverable
   from closeout docs; refactors pay a tax proportional to history, not risk.
9. **Minor but real:** `_lattice_min` returns the lattice *max* order (name
   inverts meaning); `_practitioner_display` is an N+1 query per context entry;
   `build_patient_booking_context` loads all patient appointments unbounded;
   `_run_access_ai_invocation` hard-fails in async contexts (fragile coupling to
   sync route execution); diary.js at 8,059 lines mixes grid, modal, Bernie
   panel, and dev fixtures in one file.

## 3. Receptionist-Domain Capability / Tool Map (proposed)

Formalize what exists (and what's next) as a typed capability registry — one
vocabulary shared by the diary panel today and voice lanes/Davida later. Each
tool: typed input/output, autonomy tier, audit codes, and required session state.

| Tool | Tier | Exists today as | Notes |
|---|---|---|---|
| `interpret_instruction` | read-only | `/proposals/bernie/interpret-booking-instruction` | LLM translate + deterministic resolve |
| `resolve_patient` | read-only | `_resolve_patient_from_instruction` (inline) | extract to domain module |
| `resolve_practitioner` | read-only | `_resolve_practitioner_from_instruction` (inline) | extract to domain module |
| `get_patient_booking_context` | read-only | `bernie_patient_context.py` | already correct shape |
| `find_slots` | read-only | `/proposals/slot-search*` + supervised wrapper | deterministic only, never LLM |
| `explain_schedule` | read-only | partial (commit `1389579` diagnostics) | promote to typed "why no slots" tool: no roster row / day off / breaks / fully booked |
| `suggest_next_actions` | read-only | `_build_no_slot_suggestions` + selection endpoint | Sprint 106 candidate finishes typing the chips |
| `propose_booking` | propose | supervised-booking wrapper | staff confirmation required |
| `propose_edit` / `propose_cancel` / `propose_status` | propose | existing proposal endpoints | fold into registry vocabulary |
| `confirm_booking` | confirm | `/proposals/create/confirm-bernie` | evidence + freshness gate (keep) |
| `handoff_to_receptionist` | meta | implicit (clarification states) | make explicit terminal state |

Registry is data + typed contracts, not a framework: a module-level table the
router and future runtimes read, mirroring `AiCapability` on the Access AI side.

## 4. Event / Statechart Boundaries (proposed assignment)

**Backend owns semantic state; frontend owns presentation state.** This is the
core boundary decision of this consult.

- **Backend `BernieBookingSession`** (new, persisted keyed by `session_id`;
  small table or server cache with TTL — decision point for Ariadne):
  states `instruction_entry, recognition, clarification, context_enrichment,
  slot_search, candidate_selection, proposal_preview, confirmation, confirmed,
  no_slot, clinic_day_exhausted, handed_off`; memory = immutable
  `request_reference_date`, recognised patient/practitioner ids + bands,
  candidate snapshot + freshness ids, staged proposal id, turn log. Clients send
  **typed events** (`StaffInstruction`, `ClarificationReply`,
  `CandidateSelected`, `SuggestionSelected`, `DiaryNavigated`, `RefreshRequested`,
  `ConfirmSubmitted`, `NewSession`); the server validates the transition and
  returns the new state + render payload. Invalid transitions are 409s with
  typed reasons, not console warnings. This makes the Sprint 105 freshness gates
  *enforced* rather than honor-system, and is the audit substrate limited
  auto-mode would require anyway.
- **Frontend `BernieSession`** collapses to a render-from-server-state view
  model plus purely presentational state (panel open/closed, composer mode,
  disclosure expanded, auto-preview toggle). Delete the legacy globals and the
  `syncToLegacy`/`syncFromLegacy` bridge.
- **Cross-chart links stay event-shaped:** `BookingConfirmed` → appointment
  lifecycle `AppointmentCreated` (already true via confirm endpoint); diary
  navigation emits `DiaryNavigated` into the session rather than the UI deciding
  what is stale.
- **Not proposed:** XState or any statechart runtime. A dict-based transition
  table + persisted session row is enough at this scale, consistent with the
  programme's "extract patterns first, decide on runtime later" order.

## 5. Backend Contract Changes (proposed, all future-sprint work)

1. **Extract `app/services/bernie/` package** — `interpreter.py` (existing
   service moves), `resolvers.py` (patient/practitioner), `temporal.py` (ONE
   same-day clamp/exhaustion/week-relative implementation), `policy.py` (axes +
   lattice + decision), `session.py` (statechart + memory), `context.py`
   (patient context, existing), `transitions.py` (existing table),
   `capabilities.py` (registry §3). Router endpoints become thin adapters.
   JSON responses byte-identical in the extraction sprint.
2. **Typed context frames:** replace `list[dict]` with a Pydantic discriminated
   union (`VisibleDiaryPageFrame | SelectedDiaryAppointmentFrame |
   SelectedProposalFrame | DiaryDayBookingFrame`), with per-frame-type trust
   rules (e.g. patient_id from `SelectedDiaryAppointmentFrame` → assume;
   loose ids elsewhere → never assume). Accept legacy dicts for one deprecation
   window with a warning issue code.
3. **Session/event endpoint:** `POST /appointments/bernie/session/{session_id}/events`
   (or per-event routes) returning `BernieSessionStateOut`; existing endpoints
   keep working during migration and internally route through the session.
4. **Envelope versioning:** freeze `BernieBookingInstructionInterpretOut` as v1;
   new session responses use a leaner state+render payload; deprecate rather
   than mutate.
5. **Surface silent assumptions:** business-hours pm inference and duration
   default must emit `BernieAssumption` entries; rename `_lattice_min` →
   `most_restrictive_band`; bound `build_patient_booking_context` query and fix
   the practitioner N+1 (joinedload).

## 6. UI Response Voice / Copy Strategy

- One **copy catalog module** in diary.js (later its own file) keyed by
  `(session_state, reason_code)`, first-person Bernie voice, terse, calm; all
  current `BERNIE_*_COPY` maps and block-code sniffing fold into it.
- Technical evidence (axes, freshness ids, provider metadata) stays behind the
  Details/dev disclosure — consistent with the protocol rule that safety lives
  in contracts/audit, not alarming copy.
- No-slot and exhausted states use `explain_schedule` output for *specific*
  copy ("Dr Shera isn't rostered on Friday" vs generic "no free times"), with
  typed suggestion chips (Sprint 106 candidate) as next-turn events.
- Surfaces that must not change while doing this: diary grid geometry, booking
  modal, Waiting Room cards/panels, status controls, taskpane.

## 7. Test Strategy

- **Characterization first:** the existing 20-file suite is the safety net for
  the extraction sprint — it must pass unchanged there.
- **Then consolidate by behaviour, migrating assertions before deleting files:**
  `test_bernie_interpretation.py`, `test_bernie_identity_resolution.py`,
  `test_bernie_temporal_policy.py` (table-driven, both former clamp sites),
  `test_bernie_session_transitions.py` (exhaustive event×state matrix),
  `test_bernie_confirmation_evidence.py`, `test_bernie_copy_catalog` checks in
  the review harness. Sprint-named files retire only after their assertions are
  provably represented.
- **Keep** `review/test_diary_smoke.py` as the deterministic UI harness; add
  structural checks for render-from-server-state and stale-event clearing.
- **Add** a session-transition property: no event sequence may reach `confirmed`
  without passing `proposal_preview` with fresh evidence (executable version of
  the Sprint 104 invariant harness idea).

## 8. Migration / Sprint Breakdown (each separately plan-gated)

| Sprint | Content | Risk | Behaviour change |
|---|---|---|---|
| A | Extract `app/services/bernie/` package; router thins; unify temporal policy into one module | Low | None (byte-identical JSON; suite green unchanged) |
| B | Typed context frames + per-frame trust rules; legacy-dict deprecation window | Medium | Trust tightening only |
| C | Server-side session + typed events; UI renders server state; delete legacy globals | Highest | Session semantics move server-side |
| D | Capability registry; `explain_schedule` typed tool; copy catalog; typed suggestion chips (absorbs the Sprint 106 candidate) | Medium | Copy/diagnostics improve |
| E | Test consolidation + transition-matrix/property coverage | Low | None |

Ordering note: A must precede C (you cannot host a session statechart inside a
4,249-line router). D's suggestion-chip typing can be pulled earlier as the
already-recommended Sprint 106 if Ariadne prefers a small next step before A.
Deferred beyond this plan: voice lanes, wake word, limited auto-mode, patient
details verification statechart, GraphQL/API spine, XState.

## 9. Risks / Dissent

- **Server session state is the contentious call.** It adds a table/cache,
  TTL/cleanup, and concurrency considerations that the current stateless design
  avoids. Dissent worth preserving: a stateless alternative (HMAC-signed
  evidence tokens over the existing freshness ids) gets ~70% of the integrity
  benefit with no persistence. I still recommend the persisted session because
  audit, transcript retention, multi-turn clarification, and any future
  auto-mode all independently require a durable session record — but Ariadne
  should make this call explicitly.
- **Extraction churn risk:** Sprint A touches many lines with zero intended
  behaviour change; the mitigation is the unchanged-suite rule plus
  `git diff`-reviewable pure moves (no logic edits in the same commit).
- **Envelope compatibility:** diary.js is the only client today, which makes
  now the cheapest possible time to version the contract — but Pages deploy
  ordering (backend first, frontend second) must be respected in Sprint C.
- **Test consolidation loss risk:** sprint-named tests encode live-incident
  regressions (e.g. "tomorrow becomes tomorrow again"); migration must be
  assertion-by-assertion, not file-by-file deletion.
- **Levenshtein patient matching** scans the register per request; fine at dev
  scale, needs a bound/index before multi-thousand-patient practices.
- **Ambiguity flagged:** whether Bernie session rows are PHI-bearing (they hold
  patient ids + instruction text) and therefore need the same retention policy
  the interaction-model doc defers on transcripts — needs a Yuri decision before
  Sprint C.

## 10. Pause Before Execution

This packet is consulting output only. No production code, migrations, UI, or
schema changes were made. The next action belongs to Ariadne and Yuri: review,
amend, and — only if approved — dispatch individual sprint packets, each with
its own plan gate and explicit `complete sprint task` release.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
