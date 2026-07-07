# Sprint 167 Review — Practitioner Override in Context Threading

**Status:** accepted  
**Reviewer:** Claude (Sonnet 4.6)  
**Date:** 2026-07-07  
**Scope:** `app/routers/appointments.py` · `tests/bernie_scenarios/replay.py` · `tests/bernie_scenarios/test_scenario_replay.py` · `tests/fixtures/bernie_scenarios/interpret_context_practitioner_override.yaml` · README updates

---

## Verdict: ACCEPTED — no blockers

The implementation is correct. New-reply-wins semantics are cleanly enforced, the fallback chain for the no-name case is preserved, gate compliance holds, and the scenario fixture matches the expected logic. Three low-risk notes follow; none require changes before integration.

---

## What the change does

`_resolve_bernie_interpretation_context` previously ran the clarification merge loop (carry forward prior `requested_appointment` frame fields) before resolving the practitioner name from the instruction. This meant: if the prior frame had `practitioner_id = <Shera>` and the new instruction said "Actually with Dr Patel please", the merge would fill `command_values["practitioner_id"]` with Shera's UUID before instruction name resolution ran, and the resolution block would see a UUID already present and skip to the "Practitioner UUID provided directly" branch — silently ignoring Patel.

The fix introduces a **pre-resolution pass** before the merge loop:

```
if not command_values.get("practitioner_id"):
    pre_resolve _resolve_practitioner_from_instruction(...)
    → store as pre_resolved_practitioner_id
```

Then in the merge loop:

```
if _f == "practitioner_id" and pre_resolved_practitioner_id:
    continue   ← skip merging the stale prior practitioner
```

And in the resolution block, the pre-resolved ID takes priority over the frame-UUID fallback:

```
if pre_resolved_practitioner_id:   ← now checked first
    use it
elif frame_practitioner_id UUID:
    use it
else:
    diary context inference
```

---

## Correctness analysis

### New-reply-wins

Instruction names Patel, prior context has Shera:

1. Pre-resolution: "Patel" → exact surname match → `pre_resolved_practitioner_id = Patel.id`
2. Merge loop: `practitioner_id` skip condition is True → Shera's UUID is **not** merged
3. Resolution block: `not command_values.get("practitioner_id")` → True; `pre_resolved_practitioner_id` → True → Patel used ✓

### No-name case (threading unaffected)

Instruction has no practitioner, prior context has Shera:

1. Pre-resolution: no match → `pre_resolved_practitioner_id = None`
2. Merge loop: skip condition `pre_resolved_practitioner_id` is falsy → prior Shera UUID **is** merged ✓
3. Resolution block: `command_values["practitioner_id"]` now set → `else` branch → "Practitioner UUID provided directly" axis, unchanged from prior behaviour ✓

### Frame-UUID fallback (no-instruction, no-payload-practitioner)

When neither instruction nor the `requested_appointment` payload has a practitioner, the `_context_frame_value` path (top-level frame field, not payload) remains the second fallback and is reached correctly via the inner `else` branch. ✓

### Ambiguous practitioner name

When `_resolve_practitioner_from_instruction` returns `None` because multiple practitioners match (ambiguous): `pre_resolved_practitioner_id = None` → merge loop does **not** skip → prior context practitioner is carried forward as intended. Ambiguity warning stored in `pre_resolved_practitioner_warnings` but not surfaced in this path (same behaviour as the old code, which would have resolved ambiguity silently in the same position). ✓

### Warnings and assumptions

- `pre_resolved_practitioner_warnings` flows to `resolver_warnings` in the two paths that need it: the pre-resolved-hit path and the no-frame-UUID fallback path.
- `all_assumptions.extend(pre_resolved_practitioner_assumptions)` mirrors the old code's `all_assumptions.extend(pr_assumptions)`.
- For an exact-match practitioner, `_resolve_practitioner_from_instruction` returns `pr_assumptions = []` (line 3466-3475), so no extra assumption is prepended before `clarification_merge`. The fixture assertion `assumptions.0.field: clarification_merge` is correct. ✓

### `clarification_merge` assumption completeness

Turn 2 instruction "Actually with Dr Patel please" — fake provider returns no UUIDs. The prior frame's payload has: patient_id, practitioner_id, date_from, earliest_time, duration_minutes. After skipping practitioner_id, the merged fields are: date_from, duration_minutes, earliest_time, patient_id (sorted). The assumption is emitted with those four fields. The fixture assertions for all four fields in `command_candidate` are correct. ✓

---

## Gate compliance

| Gate | Status |
|---|---|
| No live AI provider calls | ✓ monkeypatch guard in replay.py unchanged; `_resolve_practitioner_from_instruction` is DB-only |
| No new routes or schema changes | ✓ |
| No trove/RAG/memory/H15 access | ✓ |
| Readiness check `runtime_or_provider_wiring_ready=false` | ✓ unaffected |
| Provider boundary readiness: live provider disabled | ✓ unaffected |
| `git diff --check` clean | ✓ confirmed |

---

## Regression risk assessment

**`interpret_context_practitioner_change.yaml`** — turn 1 returns `clarification_required` (missing practitioner); the prior frame's payload does **not** contain `practitioner_id` (it was unresolved). In turn 2 "With Dr Shera please", `_clarification_prior_frame_values` returns no `practitioner_id` key, so the skip condition is never evaluated. Pre-resolution finds Shera; merge carries patient/date/time/duration. No regression. ✓

**`interpret_clarification_practitioner_merge.yaml`** — identical analysis. Prior frame lacks practitioner_id in payload; skip condition never fires; Shera resolved from instruction. ✓

**All other scenarios** — the `other_practitioner` fixture (Priya Patel, AHPRA `MED0007654321`) is now created for every parametrized scenario. Existing scenarios use "Shera" as the only named practitioner. "Patel" does not appear in any existing instruction text. No ambiguity is introduced. ✓

---

## Low-risk notes (no action required before integration)

**L1 — Missing `preserved_fields` in new fixture.**  
`interpret_context_practitioner_override.yaml` does not include `preserved_fields` for `command_candidate.patient_id` or `command_candidate.date_from`, unlike `interpret_clarification_practitioner_merge.yaml`. The field assertions in `expect.fields` provide equivalent single-turn coverage, but `preserved_fields` would protect against a future regression that drops the threaded patient or date mid-scenario. Low priority — the existing `expect.fields` assertions are sufficient for the current contract.

**L2 — Ambiguous-practitioner + prior-context path is untested.**  
The correct behaviour (ambiguous instruction name → prior context practitioner carries forward) is logically sound given the code but has no covering fixture. If this path is ever exercised in a real turn (instruction says "Patel" when two Patels exist), the prior practitioner silently wins and no warning is surfaced about the ambiguity. A future fixture with two practitioners whose names are close to the instruction text would close this gap. Not urgent given the current practitioner set.

**L3 — `_resolve_practitioner_from_instruction` is now unconditionally called when no practitioner UUID is in `command_values`.**  
In production this is one extra DB query (practitioners for the practice, O(10) rows) per interpret call. The query is deterministic and indexed by `practice_id` + `is_active`. Negligible for a small set, but worth noting if the interpret endpoint is ever on a hot path.

---

## Harness changes

**`replay.py`** — `other_practitioner_id` added to `ReplayContext.__init__` and `_resolve`. The None guard `if ctx.other_practitioner_id is not None:` prevents a literal `{other_practitioner_id}` string from passing a value comparison if a scenario mistakenly uses the template without the fixture — it would fail clearly rather than silently match. ✓

**`test_scenario_replay.py`** — `other_practitioner` fixture (Priya Patel) added at the test function level and always passed to `run_scenario`. `run_scenario` already accepted `other_practitioner=None` in the Sprint 166 changes, so the signature is compatible. ✓

---

## Verification replicated

All items from the sprint brief confirmed consistent with the above analysis:

- `pytest tests/bernie_scenarios/ -q` → `.x....................` (20 pass, 1 xfail)
- `pytest tests/test_bernie_scenario_integrity.py -q` → `........s`
- `bernie_interpretation_readiness_check.py` → blocked/false posture unchanged
- `bernie_provider_boundary_readiness_report.py` → live provider disabled, no provider/db/memory/trove access
- `git diff --check` → clean

Integration may proceed.
