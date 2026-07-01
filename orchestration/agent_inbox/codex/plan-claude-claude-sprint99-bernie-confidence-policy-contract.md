# plan-claude-claude-sprint99-bernie-confidence-policy-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint99-bernie-confidence-policy-contract` |
| Status | pending_plan_review |
| Created | 2026-07-01 16:59 +1000 |
| Source HEAD | `0ffeb20` |

## Plan Summary

Add a per-axis Bernie confidence + decision-policy contract to the read-only booking-instruction interpreter. Replace reliance on a single opaque scalar confidence with named confidence axes (intent, temporal, practitioner, patient_identity, slot_validity, and a reserved speech_transcription axis) each carrying a categorical band: assume | proceed_with_check | ask | block. The overall decision is the most conservative band across axes (a lattice min), never a product of raw scalars. Bands map onto the existing result/autonomy_tier/blocks fields and NEVER auto-confirm a mutation: appointment creation still requires explicit staff confirmation at confirm-bernie. Codify deterministic rules for omitted date, misspelled practitioner names (small closed set -> typo-tolerant, surfaced as an assumption), and fuzzy patient matches (large PHI set -> exact-only, always staff-verified). Plan-only packet; no production code changes now.

## My Understanding

Bernie's interpret endpoint POST /api/v1/appointments/proposals/bernie/interpret-booking-instruction is read-only: it parses staff free text into a SlotSearchCommandIn candidate and returns BernieBookingInstructionInterpretOut. It writes no appointments and no appointment audit rows (live provider path writes only bounded Access AI audit metadata). Today the output exposes one scalar confidence:float plus result ("blocked"|"clarification_required"|"interpreted") and autonomy_tier ("execute_with_report"|"blocked"). The scalar is set ad hoc (0.9 for fake, provider-supplied and clamped for live) and is NOT what actually gates behaviour - gating comes from normalization.safe, missing_fields, and blocks. Deterministic resolution happens in _resolve_bernie_interpretation_context (app/routers/appointments.py): practitioner name resolved by exact token match over the small active-practitioner set; patient by exact token match over the whole practice patient table; duration defaulted to 15; autonomous-booking language flagged as a warning only. Identity strength is separately modelled in _build_bernie_identity_evidence (unlinked/low/medium/high/ambiguous) for the supervised-booking surface, and that surface already keeps verification_status=requires_staff_verification. The gap this sprint closes: there is no explicit, typed, per-axis confidence/decision contract, and the raw scalar risks being misread as a gating signal. The design must make the decision bands authoritative and the scalar display-only, so no combination of scores can silently authorise a booking.

## Intended Surface / Boundary

Backend/API only. Affected: the typed response contract of the Bernie booking-instruction interpreter and its deterministic decision logic. Concretely: app/schemas/appointments.py (new confidence/decision models + additive fields on BernieBookingInstructionInterpretOut), app/services/bernie_booking_interpreter.py (populate axes in disabled/fake/live paths), app/routers/appointments.py (_resolve_bernie_interpretation_context computes bands, adds practitioner typo tolerance, aggregates the decision policy, gates debug disclosure), and the Bernie interpreter test suite. No visual surface changes: the diary grid, booking slot cards, waiting-room panels, staff-review cards, and stacking/lifecycle colours are NOT touched. The BernieStaffReviewPayload rendered in the supervised-booking panel is not restructured here; if it consumes the new axes it does so additively without changing existing card/slot/status layout. Explicitly: no HTML/CSS/JS under docs/ or EMR4 Sidebar/ is edited.

## Out Of Scope

No production code before "complete sprint task". No diary UI / taskpane / command-centre changes. No live phone/voice/Caller ID, Medicare, OPV, or PVM integration (the speech_transcription axis is reserved as a typed placeholder only - no transcription logic). No new autonomous mutation path; the staff confirmation gate at /proposals/create/confirm-bernie is preserved unchanged. No broad GraphQL/API-spine redesign and no refactor of appointment CRUD, slot search, or the normalizer beyond what is needed to attach axes. No weakening of existing blocks (missing_practitioner_id, missing date, invalid command) into soft warnings. No fuzzy matching over the patient database.

## Files I Expect To Edit

- app/schemas/appointments.py: add BernieConfidenceBand (Literal assume|proceed_with_check|ask|block), BernieConfidenceAxis (axis, band, basis, staff_detail, optional debug_score), BernieAssumption (field, assumed_value, basis, reversible_copy), BernieStaffCheck (code, staff_prompt), BernieDecisionPolicy (overall_band, rationale, requires_staff_confirmation:bool=True). Add additive fields to BernieBookingInstructionInterpretOut: confidence_axes, decision, assumptions, staff_checks, and optional debug. Keep the existing scalar confidence as display-only/advisory (documented as non-gating).
- app/services/bernie_booking_interpreter.py: helpers to build axes for disabled (all block), fake, and live paths; set the reserved speech_transcription axis to a fixed non-gating placeholder; do NOT let the live provider's raw scalar set any band.
- app/routers/appointments.py: in _resolve_bernie_interpretation_context compute per-axis bands from deterministic evidence; add practitioner near-match (typo tolerant) resolution distinct from patient exact-only; aggregate overall_band as lattice-min; map bands to result/autonomy_tier/blocks; first-person clarifying copy; gate debug field behind the disclosure flag.
- app/config.py: add bernie_interpreter_debug_disclosure: bool = False (ordinary staff never see raw scores/internal codes).
- tests/test_bernie_interpret_booking_instruction.py: extend for axes/bands/assumptions and non-gating scalar.
- tests/test_bernie_confidence_policy.py (new): axis lattice, omitted-date, practitioner-typo, patient-ambiguity/duplicate, no-write, debug-gating.
- tests/test_bernie_sprint98_release_gates.py: assert the ordinary Margaret Thompson / Dr Shera prompt yields expected bands without leaking raw scores/internal codes to ordinary staff.

## Implementation Steps

1) Define the band lattice: assume > proceed_with_check > ask > block (assume most permissive, block most restrictive). The overall decision = the most restrictive band present across axes. Bands are categorical; any raw scalar is advisory only and is never multiplied or thresholded into a gating decision.
2) Add typed models to app/schemas/appointments.py (see Files). BernieDecisionPolicy.requires_staff_confirmation defaults True and is never set False by this endpoint. Add additive fields to BernieBookingInstructionInterpretOut; keep existing fields/order stable so current clients and tests keep passing.
3) Axis definitions and deterministic band rules:
   - intent: block if instruction empty/parse fails; proceed_with_check if autonomous_booking_language present (warning only, still searchable); else assume. Autonomous language never blocks.
   - temporal: assume if an explicit date (today/tomorrow/ISO) is present; proceed_with_check if a time constraint is present but the date is omitted (assume today, recorded as an explicit reversible assumption); ask if no date and no temporal cue at all (do NOT silently assume today); block only on contradictory/invalid dates from the normalizer.
   - practitioner: assume on exact unique name/UUID match; proceed_with_check on a unique typo-tolerant near-match (surfaced as assumption "I think you mean Dr X"); ask on multiple matches or unresolved-but-required; the normalizer's missing_practitioner_id remains a hard block feeding band=block.
   - patient_identity: exact matching only. proceed_with_check on unique exact match (still requires_staff_verification, never assume); ask on multiple exact matches / duplicate name+DOB (request DOB + identifier); unlinked/provisional maps to proceed_with_check with is_provisional and a staff check; identity NEVER reaches band=assume.
   - slot_validity: mirror normalization.safe/blocks - block when normalization blocks, else assume/proceed_with_check.
   - speech_transcription: reserved; fixed non-gating placeholder band this sprint (no transcription input yet).
4) Small-set vs large-set asymmetry (explicit): practitioner set is small, closed, low-PHI, staff-known -> typo-tolerant near-match (e.g. surname Levenshtein<=2 or unambiguous prefix), unique near-match => proceed_with_check assumption, ambiguous => ask. Patient table is large, open, identity-critical, PHI -> exact token match ONLY, never fuzzy; ambiguity resolved by asking for DOB/identifier; unique match still staff-verified. Document this asymmetry in code comments and tests.
5) Aggregate decision in _resolve_bernie_interpretation_context: overall_band = lattice-min over axes; map to existing fields - block=>result "blocked"/autonomy_tier "blocked"/populate blocks; ask=>result "clarification_required"/autonomy_tier "blocked"; assume|proceed_with_check with required fields present=>result "interpreted"/autonomy_tier "execute_with_report". Keep requires_staff_confirmation True regardless.
6) First-person Bernie clarification copy: rewrite clarifying_question and per-assumption copy in Bernie's voice ("I need to know which day you would like." / "I think you mean Dr Shera - can you confirm?" / "I found more than one patient with that name - can you give me a date of birth?"). No raw field names or codes in ordinary copy.
7) Details/debug disclosure: raw debug_score and internal codes live only in the optional debug field, emitted only when bernie_interpreter_debug_disclosure is enabled (or an existing debug gate). Ordinary reception responses expose bands + plain copy only, consistent with Sprint 98 gate rules (no raw UUIDs / snake_case / internal codes to ordinary staff).
8) Preserve non-mutation: no db.add/commit/appointment/audit writes in the interpreter service or route (the structural no-write test already asserts this; extend it to the new helpers).
9) Tests: extend existing suites and add tests/test_bernie_confidence_policy.py covering the ordinary release-gate prompt, omitted-date (ask vs assume-today), practitioner typo near-match, patient duplicate/ambiguity, non-gating scalar, debug gating on/off, and appointment/audit no-write assertions.
10) Migration rationale: NO Alembic migration - all changes are response-shape and service/route logic; no models, tables, columns, or enums persisted to the DB (bands/axes are computed per request, not stored). config.py adds one settings flag with a safe default. Document "no migration required" in the completion notes.

## Visual / Behavioural Acceptance Checks

Behavioural (backend/API; no UI changes expected or verified visually):
- Ordinary release-gate prompt "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45" returns result="interpreted", overall_band in {assume, proceed_with_check}, temporal band=assume (date present), practitioner band resolving to Dr Shera, patient_identity band=proceed_with_check with requires_staff_verification, and no appointment/audit write.
- Omitted-date prompt with a time but no day => temporal band=proceed_with_check with an explicit "assumed today" assumption; omitted-date with no temporal cue at all => temporal band=ask, result="clarification_required", first-person clarifying copy, no silent today assumption.
- Misspelled practitioner (e.g. "Dr Sherra"/"Shara") with a unique near-match => practitioner band=proceed_with_check plus an assumption naming the resolved practitioner; multiple near-matches => band=ask.
- Patient ambiguity: two patients with the same name (or same name+DOB) => patient_identity band=ask requesting DOB/identifier; no fuzzy/approx patient match is ever produced; unique exact patient match => proceed_with_check but never assume and always requires_staff_verification.
- Decision aggregation: any block axis => result "blocked"; any ask axis (no block) => "clarification_required"; otherwise "interpreted". Verified that no combination of scalar scores alone flips the decision - bands are authoritative (test varies scalar independently of bands).
- requires_staff_confirmation stays True on every interpreted response; the confirm-bernie mutation gate is unchanged.
- Debug disclosure off (default): response contains no raw debug_score, UUIDs, or internal snake_case codes in staff-facing fields; on: debug field present.
- Structural no-write test passes: interpreter service/route contain no db.add/db.commit/appointment/audit writes.
- Full suite green: pytest tests/test_bernie_interpret_booking_instruction.py tests/test_bernie_sprint98_release_gates.py tests/test_bernie_confidence_policy.py -q, plus python -m compileall on edited modules.

## Risks / Ambiguities

- Backward compatibility: existing tests assert exact scalar confidence values (0.9, 0.82) and provider_metadata. Keeping confidence as a display-only field preserves them; if any assertion must change it will be the minimal set and documented. Risk that a client currently gates on the scalar - mitigated by documenting it as advisory and making bands authoritative.
- Practitioner typo tolerance could over-match in a large multi-practitioner practice; mitigated by requiring a UNIQUE near-match for proceed_with_check and falling to ask otherwise, and by keeping the closed active-practitioner set small. Threshold choice (Levenshtein<=2 vs prefix) is an open tuning question - default conservative, documented.
- Never introduce fuzzy patient matching; the asymmetry must be enforced in code and tests, or a false-positive PHI match could reach staff. This is the highest-risk line and is covered by an explicit test.
- Band lattice must be the single source of the decision; a subtle bug re-deriving decisions from the scalar would reintroduce the unsafe path - covered by an aggregation test that varies scalar independently of bands.
- Reserved speech_transcription axis must not accidentally gate anything while unused.
- Scope creep into BernieStaffReviewPayload/UI: kept additive and out of scope; if the supervised-booking surface needs the axes, that is a follow-up.
- Open question for Codex: should the new axes also surface on the supervised-booking staff_review payload now, or in a later sprint? Plan assumes later to keep this packet narrow.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
