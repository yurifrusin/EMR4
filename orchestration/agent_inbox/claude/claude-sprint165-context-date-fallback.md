# Sprint 165 — Context-Date Fallback Fixture Review

| Field | Value |
|---|---|
| Reviewer | Claude (Sonnet 4.6) |
| Review date | 2026-07-07 |
| Scope | `tests/fixtures/bernie_scenarios/interpret_context_date_missing_no_context.yaml` + `tests/fixtures/bernie_scenarios/README.md` (uncommitted changes) |
| Review type | Read-only fixture correctness and boundary assessment |

---

## Verdict

**PASS — fixture is correct and the boundary gates are honest.**

The new fixture accurately covers the omitted-date / no-context fallback case that completes the Sprint 164 context-date precedence matrix. All asserted field paths are consistent with live route and service code. No provider, write, memory, H15, or trove gates are opened.

---

## Correctness Assessment

### Fixture intent

The fixture proves: when a booking instruction supplies patient, practitioner, time, and duration but omits the date, and no `selected_proposal`, `selected_diary_appointment`, or `visible_diary_page` context frame is present, the route returns `clarification_required` and asks "Which day would you like me to check?" rather than guessing a date.

This directly covers the gap identified after Sprint 164: the three precedence fixtures proved what happens when context is available (proposal > selected diary > visible diary page), but none proved the fully-absent case.

### Field-by-field trace

| Asserted field | Asserted value | Code path | Verdict |
|---|---|---|---|
| `result` | `clarification_required` | `temporal_band = "ask"` when `date_transition.action == "ask"` (route line ~3967); `overall_band == "ask"` → `final_result = "clarification_required"` (route line ~4082) | CORRECT |
| `safe` | `false` | `overall_band == "ask"` → `final_safe = False` (route line ~4084) | CORRECT |
| `provider_metadata.provider` | `fake` | Replay engine patches `settings.bernie_booking_interpreter_provider = "fake"` (replay.py line 260) | CORRECT |
| `provider_metadata.live_provider` | `false` | Fake provider sets `live_provider = false`; all existing interpret fixtures assert this consistently | CORRECT |
| `command_candidate.patient_id` | `{patient_id}` | Instruction names "Margaret Thompson"; `patient` fixture is in `initial_state.fixtures`; template var resolves at replay time | CORRECT |
| `command_candidate.practitioner_id` | `{practitioner_id}` | Instruction names "Dr Shera"; `practitioner` fixture present; same resolution path as Sprint 164 precedence fixtures | CORRECT |
| `command_candidate.date_from` | `null` | No date in instruction; `date_transition.action == "ask"` (not `"assume"`) so the transition is NOT applied; `command_values["date_from"]` stays None | CORRECT |
| `missing_fields.0` | `date_from` | Route lines ~4072–4075: `practitioner_id` is set so not appended; `date_from is None` → `missing_fields = ["date_from"]`; index 0 is correct | CORRECT |
| `clarifying_question` | `"Which day would you like me to check?"` | `resolve_booking_date_transition` returns `DateResolutionTransition(…, clarifying_question="Which day would you like me to check?")` for the `date.ask_missing_context` transition (transition table line 110); route picks this up at line ~3971 (`temporal_clarifying = date_transition.clarifying_question or "Which day…"`) and sets `clarifying = temporal_clarifying` | CORRECT |
| `normalization.safe` | `false` | Normalizer emits `missing_date_from` block when `date_from is None` (normalizer line ~214); block presence → `safe=False` | CORRECT |
| `blocks.0.code` | `missing_date_from` | Top-level `blocks = list(normalization.blocks)` (route line 4130); normalizer adds `missing_date_from` block for absent `date_from`; confirmed by `test_bernie_slot_normalizer.py:test_missing_date_from_blocks` | CORRECT |

### Clarifying-question derivation path — key chain

The specific question string flows through three distinct components cleanly:

1. `bernie_transition_table.py` line 110: `clarifying_question="Which day would you like me to check?"` is the terminal return for `date.ask_missing_context`.
2. Route line ~3971: `temporal_clarifying = date_transition.clarifying_question or "Which day…"` — the explicit value from step 1 is used; the fallback string is unreachable here.
3. Route line ~4107: `clarifying = temporal_clarifying` — route uses `temporal_clarifying` directly; it is non-None so the lower-priority `_bernie_clarifying_question(missing_fields)` call at line ~4109 is not reached.

The fixture does **not** clash with the service-level `_clarifying_question()` in `bernie_booking_interpreter.py` (which would return `"Please provide date_from before Bernie searches for slots."`) because the route overrides that field via `model_copy(update={"clarifying_question": clarifying})`.

---

## Boundary Assessment

| Gate | Status | Evidence |
|---|---|---|
| `provider_called` | NOT triggered | Replay monkeypatches `_get_default_provider` to raise; listed in `forbidden_outcomes` |
| `appointment_written` | NOT triggered | `result = clarification_required`; no confirm/mutating turn; `expected.appointment_written: false`; listed in `forbidden_outcomes` |
| `audit_written` | NOT triggered | Same; `expected.audit_written: false`; listed in `forbidden_outcomes` |
| Live provider | NOT used | `provider_metadata.live_provider: false` asserted; `BERNIE_BOOKING_INTERPRETER_PROVIDER=fake` patched by harness |
| H15/H-series profiles | NOT referenced | No H-series fixture data, no profile fields, no ignored local-data paths in YAML |
| Historical diary trove | NOT referenced | No trove paths, no raw diary content, no inventory JSON references |
| Memory / RAG / GraphRAG | NOT referenced | Fixture has no session, no memory frame types, no RAG annotations |
| Write gates | NOT opened | `clarification_required` carries no write authority; no `confirm` turn; no `appointment_written` or `audit_written` expectation |

---

## README Assessment

The README diff adds a fourth bullet to the corpus coverage list:

> *context-fallback prompts: omitted dates with no selected proposal, selected diary appointment, or visible diary page context ask for the missing date instead of guessing.*

This accurately describes the new fixture. The description is honest: it says the route *asks* for the missing date rather than *guessing*, which matches `result: clarification_required` + `clarifying_question` with `date_from: null` on the command candidate.

The README also correctly places this bullet as logically sequential after the three context-precedence bullets, which mirrors the transition table priority order in `bernie_transition_table.py`.

---

## Minor Observations (no blockers)

1. **Category string.** The fixture uses `category: booking_interpret_contract`. This is not in the README's schema reference example list (`booking_clarification`, `future_booking_advisory`, etc.), but the loader accepts any non-empty string. Consistent with all other `interpret_*` fixtures in the Sprint 164 batch, which also use `booking_interpret_contract`. No action required.

2. **`safe` path ambiguity.** The fixture asserts both `safe: false` (top-level response field) and `"normalization.safe": false` (sub-object field). Both are correct and independently verifiable. This double coverage is useful: the top-level `safe` is the gating signal; `normalization.safe` is the upstream cause. Retaining both is good practice.

3. **No `preserved_fields`.** The fixture is a single-turn scenario so `preserved_fields` would be vacuous. Absence is correct.

4. **`assumptions` not asserted.** The Sprint 164 precedence fixtures assert `assumptions.0.field: date_from` and `assumptions.0.assumed_value: <date>` to prove a reversible assumption was recorded. This fallback fixture does NOT assert `assumptions` because no assumption is made — the route reaches `overall_band = "ask"` and does not append to `all_assumptions`. The absence is correct and intentional. Asserting a non-existent assumption would be wrong.

---

## Summary

The fixture is structurally valid, loads cleanly under the corpus loader, and all asserted field paths trace correctly through the live production code. The boundary gates are complete and honest. The README update accurately extends the corpus coverage description. No changes required.

**Sprint 165 recommendation:** Accept both files as-is and close out Sprint 164 context-date work as fully covered.
