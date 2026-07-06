# Sprint R29 Adversarial Review: Native Bernie/Diary Action Grammar Foundation

**Reviewer:** Codex/DeepSeek Flash adversarial lane
**Target:** Proposed native Bernie/Diary action grammar foundation
**Review date:** 2026-07-06
**Mode:** source-safe committed-doc review only; no production code edits, no raw trove, no ignored JSON

---

## 0. Current-State Summary (Pre-Grammar Baseline)

The existing codebase already has a substantial action-grammar substrate across multiple concerns:

| Concern | Current home | What it owns |
|---|---|---|
| **Envelope contracts** | app/services/diary/envelopes.py | DiaryActionIntent, DiaryActionProposal, DiaryActionConfirmation, DiaryActionSuggestion with writes_authorized Literal baked into type |
| **Capability registry** | app/services/diary/capabilities.py | 13 registered capabilities with tiers (read_only, propose, confirm, meta), allowed authors, staff-confirmation requirements |
| **Confirmation action descriptors** | app/services/diary/confirm_actions.py | 5 signed confirm endpoints with evidence purposes and block builders |
| **Session state machine** | app/services/bernie/session.py | 12 states, client event transitions, server advance targets, outcome event mappings |
| **Outcome classification** | app/services/diary/outcomes.py | 11 discriminated outcome kinds, outcome-state map, pure classifier |
| **Confirm affordance gate** | app/services/diary/confirm_gate.py | evaluate_confirm_affordance - fail-closed gate fusing policy, staleness, and proposal presence |
| **Capability manifest** | app/services/diary/capability_manifest.py | Read-only Bernie schema-awareness layer with authority boundaries |
| **Appointments router** | app/routers/appointments.py | ~280 KB of proposal, confirm, slot-search, supervision, and session endpoints |

**Key invariant:** every write-capable path currently passes through signed confirmation evidence, freshness/staleness gating, session binding, and either explicit staff confirmation or a revalidation chain. There is no auto-confirm path, no bernie-only write path, and no path where writes_authorized=True is reachable without the full gate sequence.

---

## 1. Overbroad Grammar: Capability Tier Confusion

### Risk 1.1: Grammar redefines tiers that already exist

BernieCapabilityTier (read_only, propose, confirm, meta) already enforces a semantic hierarchy. A new grammar foundation must not introduce a competing tier system (query, mutate, execute, command, admin) that maps differently:

| Existing tier | What it means | Renamed risk |
|---|---|---|
| read_only | Observes and interprets; never mutates | query could imply safe to call on any DB table |
| propose | Prepares typed non-mutating proposal; staff must confirm | prepare or stage might lose requires_staff_confirmation=True |
| confirm | Executes previously proposed mutation after evidence/freshness gating | execute or commit might skip freshness revalidation |
| meta | Session/flow control, no diary effect | control or manage might extend to appointment management |

**Recommendation:** The grammar must declare BernieCapabilityTier as its sole tier vocabulary. Any new action must slot into read_only, propose, confirm, or meta - no new tier, no renaming, no implied auto-upgrade.

### Risk 1.2: Grammar implies actions that do not exist

A grammar may enumerate actions like create_appointment, cancel_appointment, reschedule_appointment, check_in_patient, change_status. If the grammar lists cancel_appointment as propose-tier without mapping to the existing propose_cancel capability and the signed-confirm delete action descriptor, the grammar fabricates write-authority paths.

**Recommendation:** Every grammar production with tier confirm or propose must have a one-to-one mapping to a registered capability in BERNIE_CAPABILITY_REGISTRY whose implemented_as is not None. Grammar actions with implemented_as=None must be declared as planned-not-implemented and must not appear in any prompt or assembly context as available actions.

### Risk 1.3: suggest_next_actions is read_only but near-write

suggest_next_actions is registered as read_only with allowed_authors including system. If the grammar produces a suggested action that looks like a proposal (pre-filled proposal_id or writes_authorized field), this blurs the line between suggestion (read-only) and proposal (requires staff confirmation).

**Attack vector:** A grammar production that generates a DiaryActionSuggestion with writes_authorized:False by type contract, but whose payload contains pre-computed slot coordinates or patient-matching data that would bypass the slot-search/confirmation gate if fed directly into a write endpoint.

---

## 2. Hidden Write Authority

### Risk 2.1: writes_authorized is a type literal, not a runtime check

The envelope contracts enforce writes_authorized: Literal[False] on DiaryActionIntent, DiaryActionProposal, and DiaryActionSuggestion at Pydantic validation time. These are type-level contracts, not runtime guards.

A grammar foundation that produces compact action tokens must not introduce a new envelope type or serialization path where writes_authorized is a plain bool field (allowing True) rather than a Literal[False] or Literal[True] die. Pydantic discriminated union with Literal narrows the possible values to exactly one per type - any grammar that produces generic DiaryAction (no discriminated type) recreates the write-authority bypass vector.

**Concrete check:** Inspect all new grammar action types for a writes_authorized field. It must be Literal[False] on any type that could be created by Bernie or an automated agent, and Literal[True] only on DiaryActionConfirmation - which must be created solely by the signed confirm route after the full evidence/freshness/confirmation gate.

### Risk 2.2: The grammar next action is not a write grant

A grammar that allows Bernie to produce next recommended action tokens (find_slots -> propose_booking -> confirm_booking) must not let Bernie generate a confirm_booking token without the preceding propose_booking having been staff-confirmed. If the grammar allows client-side state to advance Bernie suggested confirm_booking without the server-owned session transition rule (proposal_preview -> confirm_submitted -> confirmation -> confirmed), the grammar is authoring a write path without the session authority.

**Recommendation:** Grammar productions that map to propose or confirm tier capabilities must include an invariant reference to the session state machine transition table (CLIENT_EVENT_TRANSITIONS, SERVER_ADVANCE_TARGETS). The grammar documentation must state the session state that must be current for the action to be valid.

---

## 3. Route Compatibility Risks

### Risk 3.1: Grammar actions must not imply new endpoint paths

DiaryConfirmAction enum and DIARY_CONFIRM_ACTIONS define the five signed confirmation endpoints. If the grammar introduces a new action name like bernie_reschedule or staff_extend that maps to an endpoint path not in DIARY_CONFIRM_ACTIONS, the grammar fabricates an endpoint that does not exist - or could be added later without updating the evidence/freshness gate.

**Recommendation:** The grammar must derive its confirm-action vocabulary from DiaryConfirmAction enum values. Any confirm-action production must reference its DiaryConfirmActionDescriptor entry including endpoint, evidence_purpose, and blocked_summary. Grammar documentation of a new confirm action must be a proposal to add to DIARY_CONFIRM_ACTIONS, not an independent parallel catalog.

### Risk 3.2: Slot search is read_only; grammar must not upgrade it

find_slots is registered as read_only tier with requires_staff_confirmation=False. The grammar must not accidentally classify slot search as a propose-tier action - doing so would imply that a slot search result requires staff confirmation before display, breaking the existing flow where slot candidates are shown immediately. Conversely, slot search output must not be treated as a proposal - SlotSearchProposalOut carries candidates, not a staged write.

### Risk 3.3: explain_schedule is unimplemented

explain_schedule has implemented_as=None. A grammar foundation that lists it as a usable action without marking it planned/imminent invites the implementation lane to write a first implementation that may not match the future DiaryScheduleExplanation contract.

---

## 4. Terminology Drift

### Risk 4.1: Existing term inventory

The following terms already have precise meanings in committed code. A grammar foundation must not reuse them with different semantics:

| Term | Current meaning | Must not become |
|---|---|---|
| intent | DiaryActionIntent - parsed desire, no proposal, no write | A name for a confirmed action |
| proposal | DiaryActionProposal - staff-reviewable, non-mutating, requires_staff_confirmation=True | Any auto-approved action |
| confirmation | DiaryActionConfirmation - writes_authorized=True, requires signed evidence, session binding | A soft approval without evidence |
| suggestion | DiaryActionSuggestion - read-only, writes_authorized=False, rejects confirm-grade evidence in payload | A camouflaged proposal |
| slot | A time window on a practitioner schedule; search result, not a booking | A reserved/pre-committed time |
| candidate | An unconfirmed slot search result with zero write authority | A pre-staged booking |
| handoff | Terminal session state; no further booking steps possible | A pause/resume mechanism |
| outcome | Discriminated booking outcome kind with family, session mapping, confirmation flags | Any generic result |
| affordance | Confirm-affordance gate - backend-owned single decision on confirm-grade UI | Any UI permission |

### Risk 4.2: Plain-English collision

Terms like create, book, schedule, confirm, done, arrange, place, make are domain-generic. A grammar production named book_appointment reads like a write command even if the grammar assigns it read_only or propose tier.

**Recommendation:** Every grammar production user-facing verb must match its tier: propose_* for propose-tier, find_* or suggest_* for read_only, confirm_* for confirm-tier. Never create_* or book_* as a read_only action name.

---

## 5. Missing Confirmation/Evidence Invariants

### Risk 5.1: Grammar must reference the confirm gate

evaluate_confirm_affordance is the single backend-owned gate for whether confirm-grade UI may be shown. A grammar foundation that defines a can-confirm predicate without referencing this gate creates a parallel confirm-authority path.

**Invariant:** Every proposed action with tier=confirm must declare that evaluate_confirm_affordance(policy, staleness=..., has_staged_proposal=...) must return confirm_grade_allowed=True before the action can be suggested or rendered.

### Risk 5.2: Freshness/staleness must gate all propose-to-confirm transitions

The evidence module provides check_staleness, compute_candidate_freshness_id, compute_proposal_freshness_id, and signed evidence mint/verify. The grammar must make freshness an explicit precondition on any propose-to-confirm transition.

**Concrete invariant:** Every grammar rule that transitions from a propose-tier action to a confirm-tier action must include freshness_required=True and reference the exact SIGNED_*_EVIDENCE_PURPOSE constant for the action.

### Risk 5.3: Outcome classification must remain pure

classify_booking_outcome is a pure function (no DB, no clock, no LLM) that takes already-computed evidence and returns a deterministic label. The grammar must not introduce an LLM-generated outcome classification.

**Recommendation:** The grammar foundation may classify outcomes only by referencing the existing outcome kinds in BernieBookingOutcomeKind. Any new outcome kind must be added to classify_booking_outcome precedence-ordered chain, not defined inline in grammar text.

---

## 6. H-Series/Full-Trove Boundary

### Risk 6.1: Grammar vocabulary must not depend on H-series profiles

Per R28 Fable and docs/receptionist_review_r27.md, H-series profiles exist as non-semantic aggregate evidence only. A grammar foundation that derives its action vocabulary, transition frequencies, or status reason codes from H-series profile data crosses the H15 gate without approval.

**Recommendation:** The grammar vocabulary must be grounded entirely in committed source code (app/, tests/), existing review artifacts (docs/), and the known Diary domain model - never in local_data/historical-diary-trove/, ignored JSON, H-series profile fixture fields, or trove-derived counts.

### Risk 6.2: No trove-derived action frequencies in grammar

A native grammar must not use neutral event class distributions (e.g. 85% of transitions are small_content_delta) to justify grammar production priorities, action ordering, or default confidence thresholds. That would use non-semantic aggregate evidence to make action-grammar design decisions, which is a form of semantic inference across the H15 gate.

---

## 7. Concrete Attack Vectors (for Ariadne Merge Gate)

### Vector A: Grammar action that skips confirm affordance gate

A new grammar action suggest_confirmation that bypasses evaluate_confirm_affordance and presents confirm UI based on a grammar-embedded rule (if any candidates exist, show confirm). This is a parallel confirm-authority decision.

### Vector B: propose_edit without session state check

The grammar lists propose_edit as available from any session state. The client sends candidate_selected from the wrong state, the session validator rejects with 409, but the grammar has already presented the action as legally available from that state - creating a mismatch between UI affordance and backend availability.

### Vector C: Grammar produces DiaryAction without writes_authorized Literal

If the grammar foundation defines a generic DiaryAction base class (not the existing discriminated union of intent/proposal/confirmation/suggestion), a serialization bug could produce a DiaryAction with writes_authorized=True for a read_only action.

### Vector D: Grammar action that implies patient/practitioner assignment without resolve_* capabilities

A grammar production like book_tony_with_dr_smith_in_the_afternoon that skips resolve_patient and resolve_practitioner capabilities and presents a combined book production. This collapses the recognition/write boundary.

### Vector E: Grammar suggests same-day propose_booking without temporal guard

evaluate_same_day_window returns clamp_earliest or window_fully_past, but the grammar presents a propose_booking suggestion anyway. The grammar must explicitly reference SameDayWindowDecision.kind as a precondition.

---

## 8. Positive Design Requirements

| Requirement | Must include | Must not include |
|---|---|---|
| Tier vocabulary | Exact reuse of BernieCapabilityTier | New or renamed tiers |
| Action-to-capability map | 1:1 mapping to BERNIE_CAPABILITY_REGISTRY entries | Orphan actions without registry entry |
| Write-authority field | writes_authorized: Literal[False] on read-only/propose; Literal[True] only on confirm type | writes_authorized: bool |
| Session state binding | Every confirm-tier action references its session transition rule | Actions allowed from any state |
| Confirm gate precondition | Every confirm action declares evaluate_confirm_affordance(...) == allowed | Grammar-internal confirm predicate |
| Freshness invariant | Every propose-to-confirm transition requires freshness check and signed evidence | Auto-confirm without freshness revalidation |
| Outcome classification | Pure deterministic via classify_booking_outcome | LLM-generated or grammar-inline outcome labels |
| Implemented actions only | implemented_as != None for usable productions | Planned-but-unimplemented in prompt context |
| H15 boundary | Zero H-series/trove/neutral-event references | Trove-derived frequencies or transition priors |
| Terminology | Exact reuse of envelopes.py types | Generic or plain-English names without tier prefix |

---

## 9. Adversarial Questions

1. Where does the grammar get its action vocabulary from - a new file, an extension to the capability registry, or a generated manifest? How is this source bounded so it cannot grow unseen?
2. If a grammar action maps to a registered capability with implemented_as=None, should the grammar auto-generate a stub, or must implementation be a separate plan-approved sprint?
3. propose_status allows rayleen as an author. Are Rayleen-authored proposals subject to the same signed-confirmation evidence chain as Bernie-authored ones? The grammar must represent Rayleen authority identically to Bernie - no shortcut.
4. Should the grammar foundation include a golden test that serializes the full grammar, runs it past evaluate_confirm_affordance with known stale/fresh evidence, and asserts the only allowed confirm actions are those where the gate passes?
5. The existing DiaryActionSuggestion validator reject_confirm_grade_evidence recursively scans the payload for forbidden evidence keys. If the grammar introduces a new suggestion-like action type, does it inherit this validator?

---

## 10. Verdict

**Conditional pass for plan-only review.** The grammar foundation should proceed to implementation planning, subject to these pre-merge gates:

1. No writes_authorized field without a Literal die - all grammar action types must be discriminated unions or have writes_authorized baked into the type.
2. Every confirm-tier grammar action must document its evaluate_confirm_affordance gateway and session state transition rule.
3. Zero H-series, trove, or neutral event class references in grammar vocabulary or design rationale.
4. A golden test that proves the grammar cannot generate a confirm-tier action suggestion when the confirm affordance gate returns confirm_grade_allowed=False.

The H15 semantic labelling gate remains closed. The R28 Fable ordering (grammar -> replay consumer -> H22 gate -> full-trove mining) is preserved. The existing determinism of classify_booking_outcome, evaluate_confirm_affordance, evaluate_same_day_window, and the session state machine must remain the sole sources of backend booking authority - the grammar is advisory translation, not new authority.

---

*This review is source-safe: no raw trove filenames, PHI, patient/staff identifiers, exact timestamps, document text, or semantic appointment labels are disclosed. All findings are derived from committed source code and review artifacts only.*
