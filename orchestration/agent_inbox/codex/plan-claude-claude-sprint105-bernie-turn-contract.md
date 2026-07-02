# plan-claude-claude-sprint105-bernie-turn-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint105-bernie-turn-contract` |
| Status | pending_plan_review |
| Created | 2026-07-02 23:40 +1000 |
| Source HEAD | `0e9438b` |

## Plan Summary

Add a backend-owned typed turn contract and confirmation-evidence layer for Bernie: explicit session/turn ids, a typed event vocabulary, candidate/proposal freshness ids-or-hashes, immutable reference_date across turns, and a staleness gate that blocks confirmation writes on mismatched or stale evidence, all additive over Sprint 104 and non-mutating before confirm.

## My Understanding

Today Bernie's multi-step flow (interpret -> supervised search/selection -> create-proposal -> confirm) carries session/turn continuity only as UI-tolerated metadata (context_frames: list[dict]) with no backend-owned turn ids, event vocabulary, or evidence freshness. request_reference_date is already echoed immutably on interpret/supervised outputs (schemas L665,L710) and reference_date is intake-captured, but nothing stops a client confirming a stale candidate/proposal from an earlier turn or a proposal built against a different reference_date. Sprint 104 patient recognition (BerniePatientBookingContext, exact-match only) and context_freshness already exist and must stay separate from patient-details verification. The interpreter is a read-only provider boundary (no DB writes) and the privileged/agent path must never write. This sprint closes the evidence gap: make turns and freshness first-class typed backend fields and add a pre-write staleness check.

## Intended Surface / Boundary

Backend/API only, additive over Sprint 104. Typed turn contract in app/schemas/appointments.py (session_id, turn_id, turn_index, event kind vocabulary, candidate/proposal freshness id-or-hash fields on the existing Bernie In/Out envelopes). A narrow evidence/freshness helper (new app/services/bernie_turn_evidence.py if justified, else extend bernie_slot_normalizer usage) computing deterministic freshness ids/hashes and staleness verdicts. Wiring in app/routers/appointments.py Bernie endpoints (interpret, supervised booking, create-proposal confirmation) to stamp turn/event ids, echo immutable reference_date per turn, and block confirmation when evidence is stale/mismatched. Interpreter (bernie_booking_interpreter.py) only threads reference_date/turn context through; no live-provider dependency added.

## Out Of Scope

No production code before approval. No limited Bernie auto-mode, voice/headset/Caller ID, Medicare/HI/PVM/OPV verification, GraphQL/context-graph migration, statechart runtime dependency, or broad root-to-branch API redesign. Do not weaken staff confirmation, do not add any agent-only/privileged write path, do not change diary grid / booking-slot / waiting-room UI surfaces, do not alter Sprint 104 patient-recognition-vs-details separation or the deterministic slot search, and do not break existing Diary calls (all new fields additive/optional).

## Files I Expect To Edit

app/schemas/appointments.py (typed turn + event vocabulary + freshness id/hash fields on Bernie In/Out models); app/routers/appointments.py (stamp turn/event ids, echo immutable reference_date, staleness gate before confirm); app/services/bernie_turn_evidence.py NEW narrow helper if justified (deterministic freshness id/hash + stale verdict) else extend existing normalizer usage; app/services/bernie_booking_interpreter.py (thread reference_date/turn through, no live dep); tests/test_bernie_turn_contract.py NEW focused backend tests.

## Implementation Steps

1) Define typed turn primitives in schemas: BernieTurnRef(session_id, turn_id, turn_index, reference_date) and a BernieTurnEventKind Literal vocabulary (staff_instruction, bernie_clarification, no_slot_suggestion_selection, candidate_selection, proposal_preview, confirmation). 2) Add optional additive freshness fields: candidate_freshness_id/hash and proposal_freshness_id/hash on SlotSelectionProposalOut / BernieSupervisedBooking In+Out / BernieCreateProposalConfirmationIn, derived deterministically from normalized command + reference_date + candidate identity. 3) Add a deterministic evidence helper computing freshness ids/hashes and a compute_staleness verdict (fresh vs stale vs mismatched-reference-date). 4) Wire interpret/supervised endpoints to mint/echo session_id+turn_id+turn_index and immutable request_reference_date; reject malformed/absent turn ids on turns that require prior context. 5) Wire create-proposal confirmation to recompute expected freshness and BLOCK (typed block issue, no mutation) when submitted freshness id/hash mismatches or reference_date differs across turns. 6) Keep no-slot BernieSlotSuggestion selection as a typed event that carries its originating turn_id. 7) Add tests. 8) Backcompat: all new fields Optional/defaulted so current Diary Sprint-104 calls omitting them still succeed; only confirmation with explicit stale/mismatched evidence is blocked.

## Visual / Behavioural Acceptance Checks

Backend/API only; no visual surface changes to diary grid, booking slots, cards, panels, or waiting room. Behavioural: (a) a well-formed turn payload with matching freshness is accepted; (b) a confirmation carrying a stale or reference-date-mismatched candidate/proposal is blocked with a typed block issue and NO DB mutation; (c) malformed/missing turn ids on context-dependent turns are rejected; (d) typed no-slot suggestion selection is handled and carries its turn_id; (e) reference_date is identical across all turns of a session; (f) existing Sprint 104 live flow (interpret->search->select->confirm happy path) still succeeds when new fields are omitted.

## Risks / Ambiguities

1) Hash/id design: must be deterministic and PHI-safe (hash normalized command + reference_date + candidate identity, never raw patient text) and stable across process restarts; risk of accidental instability if datetime.now() leaks into the hash — exclude wall-clock from the freshness id, keep generated_at only as a display/staleness-basis signal. 2) Backcompat: if any new field is non-optional it breaks Sprint 104 Diary calls — all additive fields must default. 3) Scope creep toward a statechart runtime — explicitly avoided; turn_index is a plain integer, not a state machine dependency. 4) Staleness gate must fail closed on confirm but must not block legitimate same-session re-confirmation; verdict must distinguish stale (older turn) from mismatch (different reference_date) so error messaging is correct. 5) Dissent: consider whether freshness belongs as an opaque server-signed token vs a client-recomputable hash; recommend server-recomputed comparison (client sends echoed id, server recomputes expected and compares) to avoid trusting client-supplied hashes.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
