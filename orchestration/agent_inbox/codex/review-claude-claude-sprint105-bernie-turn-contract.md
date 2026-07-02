# review-claude-claude-sprint105-bernie-turn-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint105-bernie-turn-contract` |
| Status | queued |

## Review Request

claude-sprint105-bernie-turn-contract implementation complete

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - app/schemas/appointments.py: Added BernieTurnRef model, BernieTurnEventKind Literal vocabulary, BernieTurnEventKind field; added optional turn_ref to BernieSupervisedBookingIn/Out, SlotSelectionProposalOut, BernieBookingInstructionInterpretIn/Out, BernieCreateProposalConfirmationIn; added candidate_freshness_id to SlotCandidate; added proposal_freshness_id to SlotSelectionProposalOut; added candidate_freshness_id/proposal_freshness_id/turn_ref to BernieCreateProposalConfirmationIn; added BernieNoSlotSuggestionSelectionIn/Out schemas; all new fields Optional/defaulted for backward compat.
  - app/services/bernie_turn_evidence.py (NEW): Deterministic PHI-safe freshness id helpers (compute_candidate_freshness_id, compute_proposal_freshness_id), staleness gate (check_staleness → StalenessVerdict), session/turn id minters. No wall-clock in hash inputs.
  - app/routers/appointments.py: Added imports for new schemas/evidence module; added _mint_next_turn_ref helper; wired turn minting into interpret-booking-instruction response; wired candidate freshness id stamping into supervised-booking search proposal (all candidates); wired proposal_freshness_id stamping into SlotSelectionProposalOut built inside supervised-booking; wired turn_ref onto candidate_selection_required and confirmation_ready BernieSupervisedBookingOut responses; added staleness gate in confirm_bernie_create_proposal that blocks on stale/cross-session candidate_freshness_id or proposal_freshness_id with no DB mutation; added new POST /proposals/bernie/no-slot-suggestion-selection endpoint.
  - tests/test_bernie_turn_contract.py (NEW): 34 tests covering BernieTurnRef validation, all event kinds, freshness id determinism/PHI-safety/stability, staleness gate verdicts (fresh/stale/mismatch), mint helpers, schema backward-compat (Sprint 104 payloads omitting new fields), no-slot suggestion selection typed event, staleness gate blocks with no DB mutation, cross-session freshness id blocking, Sprint 104 backward compat, supervised booking turn minting, candidate freshness id stamping, reference_date immutability.

- Verification run:
  - 34/34 new tests pass (test_bernie_turn_contract.py)
  - Pre-existing bernie tests unchanged: test_bernie_supervised_booking_wrapper.py (32 pass), test_bernie_no_slot_suggestions.py, test_bernie_sprint104_state_memory.py all pass
  - Pre-existing failures confirmed pre-existing (not introduced): test_bernie_confirm_create_proposal.py::test_bernie_confirm_success_writes_exactly_one_appointment_and_bounded_audit (failing before my changes); test_slot_search_proposal.py and other slot failures (pre-existing)
  - Python syntax check: python -c "import app.routers.appointments; import app.schemas.appointments; import app.services.bernie_turn_evidence" all OK

- Remaining risks:
  1. The staleness gate recomputes expected freshness ids using turn_ref.reference_date. For cross-session detection to work, the client must echo back the correct turn_ref. If a client supplies no turn_ref/freshness_ids, the gate is bypassed (backward-compat tolerated as documented). The underlying revalidation of create command entities and conflict check still fires regardless.
  2. proposal_freshness_id is stamped on SlotSelectionProposalOut only when created inside supervised-booking. The standalone /proposals/slot-search/selection endpoint does not stamp it (out of scope). If a client goes through that route and echoes no freshness ids, the gate is benign (backward-compat tolerates absent ids).
  3. The pre-existing test failure in test_bernie_confirm_create_proposal.py (test_bernie_confirm_success_writes_exactly_one_appointment_and_bounded_audit) was not caused by this sprint — confirmed by reproducing on the baseline commit. Codex should investigate separately.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint105-bernie-turn-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
