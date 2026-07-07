---
id: claude-sprint169-temporal-drift-followup
title: Sprint 169 – Temporal-drift follow-up fixture
agent: claude
status: submitted
type: review
sprint: 169
date: 2026-07-07
---

# Sprint 169 Review Packet

## Scope

One new YAML fixture and a README addendum. No implementation changes, no
migrations, no schema changes, no route additions.

---

## Changes reviewed

### 1. New fixture `tests/fixtures/bernie_scenarios/interpret_context_temporal_drift_followup.yaml`

```
id: interpret_context_temporal_drift_followup
category: booking_interpret_contract
reference_date: 2026-07-08
```

#### Purpose

This fixture proves two properties at once that no prior fixture exercises in
combination:

1. **Auto-threading + reference-date drift** — omitting `context_frames` on a
   follow-up turn threads the prior requested-appointment frame while the
   `reference_date` has advanced (2026-07-08 → 2026-07-09). The key contract is
   that relative-date resolution in the follow-up uses the *current* turn's
   reference date, not the threaded frame's reference date.

2. **New-reply-wins on the date axis** — "Actually make it tomorrow" overrides
   the threaded `date_from` from turn 1 (2026-07-14) while all other threaded
   fields (patient, practitioner, time, duration) are preserved via
   `clarification_merge`.

The existing `interpret_turn_reference_date_drift.yaml` proves reference-date
resolution in isolation (no threading, explicit `context_frames: []` on both
turns). The existing `interpret_context_frames_auto_thread_vs_empty.yaml` proves
auto-threading with a time-change follow-up (no reference-date drift between
turns). Sprint 169 closes the combination gap.

---

#### Turn 1 analysis

```yaml
instruction: "Book Margaret Thompson with Dr Shera next Tuesday at 09:00 for 20 minutes"
reference_date: "2026-07-08"
context_frames: []
```

**Date arithmetic**: 2026-07-08 is a Wednesday (2026-01-01 is Thursday; +188 days
mod 7 = Wednesday). "Next Tuesday" from Wednesday 2026-07-08 resolves to
2026-07-14 (6 days ahead). The fixture asserts `command_candidate.date_from:
"2026-07-14"`. ✓

`_extract_natural_date_constraint` calls `resolve_weekday_date` for "next Tuesday"
and returns the ISO string "2026-07-14" directly (not a relative token), so
`command_candidate.date_from` holds the resolved string. ✓

**Remaining turn-1 assertions** — `result: interpreted`, `safe: true`,
`provider_metadata.provider: fake`, `live_provider: false`, `patient_id`,
`practitioner_id`, `earliest_time: "09:00"`, `duration_minutes: "20"`,
`request_reference_date: "2026-07-08"` — all consistent with a complete
full-request instruction processed by `FakeBookingInstructionInterpreter`. ✓

---

#### Turn 2 analysis

```yaml
instruction: "Actually make it tomorrow"
reference_date: "2026-07-09"
# context_frames omitted → auto-threads from turn 1
```

**Auto-threading path**: the replay engine's `_execute_interpret` detects the
absence of `context_frames` in the input and populates it with
`_requested_appointment_frames(self.last_interpret_response)` — the
`requested_appointment`-typed frames from turn 1's `reception_context`. These
carry `patient_id`, `practitioner_id`, `date_from`, `earliest_time`, and
`duration_minutes` from the prior command candidate. ✓

**New-reply-wins on `date_from`**: the instruction "Actually make it tomorrow"
supplies `date_from = "tomorrow"` via `_extract_natural_date_constraint`. The
clarification-merge loop (lines 3744–3761 of `appointments.py`) only copies a
field from the prior frame when `command_values.get(_f)` is falsy. Since
`date_from` is now "tomorrow" (truthy), it is *not* overwritten from the prior
frame. The prior `date_from: "2026-07-14"` is discarded. ✓

**`command_candidate.date_from: tomorrow`** — `_extract_natural_date_constraint`
matches DATE_RE (`\b(?:today|tomorrow|...)\b`) and returns
`date_match.group(0).lower()` = `"tomorrow"`. This raw token lands in
`SlotSearchCommandIn.date_from`. The fixture asserts the raw token, not the
resolved date. Correct for the fake-provider path. ✓

**`normalization.constraint.date_from: "2026-07-10"`** — `normalize_slot_search_command`
receives `date_from = "tomorrow"` and `reference_date = 2026-07-09`, resolving
to `2026-07-09 + 1 = 2026-07-10`. ✓

**`request_reference_date: "2026-07-09"`** — the route stamps the turn's
`body.reference_date`, not the scenario-level `reference_date`. ✓

**`assumptions.0.field: clarification_merge`** — the merge loop fires because
`patient_id`, `practitioner_id`, `earliest_time`, and `duration_minutes` are all
absent from "Actually make it tomorrow" and are copied from the prior frame. The
`clarification_merge` assumption is appended first inside
`_resolve_bernie_interpretation_context` (before practitioner, date-transition,
and duration assumptions). `assumptions[0]` reliably holds it. ✓

**`preserved_fields`** — the scenario declares:
- `command_candidate.patient_id`
- `command_candidate.practitioner_id`
- `command_candidate.earliest_time`
- `command_candidate.duration_minutes`

`date_from` is intentionally absent from this list (it changes). The harness
snapshots turn 1 values and fails if they disappear or change on turn 2. ✓

---

#### Schema and loader compliance

| Check | Result |
|---|---|
| `id` matches `[a-zA-Z0-9][a-zA-Z0-9_-]*` | ✓ |
| `category` non-empty string | ✓ |
| `reference_date` matches YYYY-MM-DD | ✓ |
| `turns` non-empty list | ✓ |
| All `action` values in `KNOWN_ACTIONS` | ✓ (`interpret`, `interpret`) |
| All `forbidden_outcomes` in `KNOWN_FORBIDDEN_OUTCOMES` | ✓ (`provider_called`, `appointment_written`, `audit_written`) |
| `initial_state.fixtures` — standard set | ✓ (practice, practitioner, gp_user, patient, schedule) |
| `expected.appointment_written: false` / `audit_written: false` | ✓ |

The loader will parse this file without error and `discover_scenarios` will
include it in the replay corpus.

---

#### Minor fragility notes (not blocking)

**1. `assumptions.0.field` ordering dependence.**
The assertion `assumptions.0.field: clarification_merge` relies on
`clarification_merge` being the first element appended to `all_assumptions` in
`_resolve_bernie_interpretation_context`. This is currently stable, but if a
future change adds an earlier assumption (e.g. a speech-transcript placeholder
assumption prepended in the provider layer), the index would become 1. Consistent
with how earlier fixtures in the corpus use the same pattern; watch if
assumption-ordering changes are made in the route.

**2. Turn 1 does not assert `normalization.constraint.date_from`.**
Only `command_candidate.date_from: "2026-07-14"` is checked. If the normalizer
were to mishandle "next Tuesday" → ISO date resolution, the only signal would be
turn 2's `normalization.constraint.date_from: "2026-07-10"` assertion (which
would still pass because turn 2 uses "tomorrow", not "next Tuesday"). Low risk
in practice — the resolver is covered by `interpret_turn_reference_date_drift.yaml`
— but worth noting for completeness.

**3. `command_candidate.date_from: tomorrow` asserts the raw token.**
This is correct for the fake-provider path: `_extract_natural_date_constraint`
returns the literal match. A live provider might normalise the date inside the
command candidate itself. Not an issue for this fixture (fake-provider boundary
is enforced by `provider_metadata.live_provider: false` and the monkeypatch
guard), but reviewers integrating a live-provider tranche should remember that
`command_candidate.date_from` and `normalization.constraint.date_from` can
diverge.

---

### 2. README addendum (`tests/fixtures/bernie_scenarios/README.md`)

Adds one bullet to the "current executable `interpret_*` corpus" list:

> "temporal-drift follow-ups: relative-date corrections resolve against the
>  current turn reference date while preserving threaded appointment details."

Accurate description of what the new fixture exercises. No structural changes.

---

## Missing coverage (optional follow-up, not blocking)

**Multi-turn temporal drift with no prior date in context.** The current fixture
threads a prior `date_from` that is explicitly overridden. An adjacent case worth
a future fixture: a follow-up turn where the prior frame has no `date_from` (e.g.
the prior turn returned `clarification_required` for a missing date) and the
follow-up supplies "tomorrow" with a drifted reference date — proving that the
drifted reference date is used for resolution even when there is nothing to
override from context. Not blocking; the current fixture proves the override path,
which is the more complex surface.

---

## Summary

| Change | Verdict |
|---|---|
| New fixture `interpret_context_temporal_drift_followup.yaml` | Correct — assertions match implementation, date arithmetic verified, auto-threading and new-reply-wins both exercised |
| README addendum | Accurate |

Sprint engine: **continuing**. No blocking findings. Three minor fragility notes
recorded above; none require changes before integration. One optional follow-up
fixture described.
