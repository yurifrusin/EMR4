---
title: Sprint 166 — Context-Threading Fixture Review
agent: claude
task: claude-sprint166-context-threading
status: submitted
date: 2026-07-07
---

# Review: interpret_context_frames_auto_thread_vs_empty.yaml + README.md

## Verdict

**ACCEPT with minor notes.** The fixture correctly proves both sides of the contract. Boundary is clean. No blocking issues.

---

## What the fixture proves

Three turns over a single scenario (`interpret_context_frames_auto_thread_vs_empty`):

| Turn | context_frames in input | Instruction | Expected result |
|---|---|---|---|
| 1 | `[]` (explicit empty) | Full booking request — patient, practitioner, "next Tuesday", 09:00, 20 min | `interpreted` / `safe: true` — all fields resolved |
| 2 | *omitted* | "Actually make it 09:30" | `interpreted` / `safe: true` — time updated, all other fields threaded from turn 1 |
| 3 | `[]` (explicit empty) | "Actually make it 10:00" | `clarification_required` / `safe: false` — only time parsed, patient/practitioner/date require re-clarification |

---

## Harness threading mechanics — confirmed correct

`replay.py:_execute_interpret` (lines 152–172) implements the threading rule precisely:

```python
if "context_frames" in inp:
    context_frames = inp.get("context_frames") or []
else:
    context_frames = _requested_appointment_frames(self.last_interpret_response)
```

- **Explicit `context_frames: []`** in the fixture YAML → key present → `inp.get(...) or []` → empty list → no threading. Correct for turns 1 and 3.
- **Omitted `context_frames`** in the fixture YAML → key absent from parsed `inp` dict → falls through to `_requested_appointment_frames(self.last_interpret_response)` → extracts `reception_context.frames` entries where `frame_type == "requested_appointment"` from turn 1's response → those frames are forwarded as context for turn 2.

The fixture input for turn 2 has no `context_frames` key at all:

```yaml
  - action: interpret
    input:
      instruction: "Actually make it 09:30"
```

This is the right shape. The harness key-presence check (`"context_frames" in inp`) will correctly see it as absent and auto-thread.

---

## Assertion analysis

### Turn 1 assertions — sound
All booking fields asserted after an explicit fresh start with a complete request. `result: interpreted`, `safe: true`, all five fields (`patient_id`, `practitioner_id`, `date_from: 2026-07-14`, `earliest_time: 09:00`, `duration_minutes: 20`) resolved. `provider_metadata.provider: fake` and `live_provider: false` confirmed.

"Next Tuesday" relative to `reference_date: 2026-07-08` resolves to 2026-07-14 — correct (Tuesday 14 July 2026).

### Turn 2 assertions — sound, one minor note
Auto-threaded context carries patient, practitioner, date, and duration forward; only the time changes to 09:30. `assumptions.0.field: clarification_merge` confirms the merge pathway was taken. This mirrors the existing `interpret_clarification_practitioner_merge.yaml` pattern, so it's a known-good assertion shape.

**Minor note:** `duration_minutes` is **not** re-asserted in turn 2's `expect.fields`. It appears only in turn 1. The fixture relies on the harness not checking what it doesn't assert, which is fine — but a `preserved_fields` entry for `command_candidate.duration_minutes` would make drift detectable automatically without verbose per-turn re-assertion. Not a defect; just less future-proof.

### Turn 3 assertions — sound, one order note
Explicit `context_frames: []` clears the thread. "Actually make it 10:00" with no patient/practitioner/date context produces `clarification_required`, `safe: false`, `patient_id: null`, `practitioner_id: null`, `date_from: null`, `earliest_time: 10:00`. This correctly proves the "explicit empty clears" branch.

`missing_fields.0: practitioner_id` and `missing_fields.1: date_from` asserts a specific ordering of the missing-fields list. This ordering will be correct as long as the route emits fields in the current order. If the route ever reorders its missing-fields list, this assertion would fail spuriously. Consider using two separate unordered existence checks if ordering is not semantically meaningful; for now it is acceptable because the ordering reflects route priority (practitioner before date).

`safe: false` on `clarification_required` is correct by the existing route contract. No comment is required in the fixture to explain this, as it is already established by earlier fixtures.

---

## No `preserved_fields` declaration

The new fixture does not declare `preserved_fields`. The existing `interpret_clarification_practitioner_merge.yaml` uses `preserved_fields: ["command_candidate.patient_id"]` to catch mid-scenario patient-id disappearance. This fixture covers the same ground via explicit per-turn assertions in `expect.fields`, which is sufficient. However, adding `preserved_fields: ["command_candidate.patient_id"]` to this fixture (or at minimum noting its absence) would provide the same automatic regression guard that the practitioner-merge fixture has. Not blocking.

---

## Boundary assessment

| Gate | Status |
|---|---|
| Provider called | Blocked — `forbidden_outcomes: [provider_called]` + monkeypatch guard in harness |
| Appointment written | Blocked — `forbidden_outcomes: [appointment_written]` + harness count check |
| Audit written | Blocked — `forbidden_outcomes: [audit_written]` + harness count check |
| Live provider | `provider_metadata.live_provider: false` asserted in all three turns |
| Fake provider asserted | `provider_metadata.provider: fake` asserted in all three turns |
| H15 / H-series material | Not referenced anywhere in fixture or README delta |
| Historical trove | Not referenced |
| Memory / RAG / GraphRAG | Not referenced |
| Database writes | `expected.appointment_written: false`, `expected.audit_written: false` |
| Route-level / no-write | Correctly described in README as fake-provider, route-level contract tests |

Boundary is fully clean.

---

## README delta assessment

The README addition accurately describes the new fixture slice:

> context-threading prompts: omitted `context_frames` auto-threads prior requested appointment context, while explicit `context_frames: []` clears the thread and asks again.

This correctly mirrors the fixture's three-turn structure. The inline schema description at the bottom of the README — "For `interpret` turns, omitted `context_frames` auto-threads the `requested_appointment` frame from the previous `interpret` turn. Use `context_frames: []` to force a fresh turn." — is accurate, matches the harness implementation, and belongs in the README as normative protocol documentation for fixture authors.

The README does not introduce any new permissions, provider access, or scope relaxations. It is documentation only.

---

## Summary of findings

| Finding | Severity | Blocking? |
|---|---|---|
| No `preserved_fields` for duration across turns 1→2 | Low | No |
| `missing_fields` order assertion is order-sensitive | Low | No |
| `safe: false` convention on `clarification_required` is implicit, not commented | Trivial | No |

All findings are non-blocking. The fixture is correct, the boundary is honest, and the README description accurately reflects the fixture's intent and the harness's threading mechanics.

---

## Recommendation

Accept as-is. Optionally add `preserved_fields: ["command_candidate.duration_minutes"]` in a follow-up if duration drift becomes a risk. No changes required before commit.
