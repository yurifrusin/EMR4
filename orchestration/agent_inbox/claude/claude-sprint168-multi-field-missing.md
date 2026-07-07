---
id: claude-sprint168-multi-field-missing
title: Sprint 168 – Multi-field missing clarifying copy + UUID pre-resolution gate
agent: claude
status: submitted
type: review
sprint: 168
date: 2026-07-07
---

# Sprint 168 Review Packet

## Scope

Two-line change in `app/routers/appointments.py`, one new fixture, and a README
addendum. No migrations, no schema changes, no route additions.

---

## Changes reviewed

### 1. UUID gate for practitioner pre-resolution (`app/routers/appointments.py` line 3728)

**Before**

```python
if not command_values.get("practitioner_id"):
```

**After**

```python
if not _valid_uuid_text(command_values.get("practitioner_id")):
```

#### What this fixes

The old guard is falsy only for `None` and `""`. A live-provider-style payload that puts a
display name such as `"Dr Shera"` into `practitioner_id` evaluates as truthy — so the old
code skipped `_resolve_practitioner_from_instruction` entirely, then the downstream
non-UUID clear at line 3765 (`if ... and not _valid_uuid_text(...)`) nulled the name with
nothing to substitute. The result: a payload that named the practitioner ended up with
`practitioner_id = None`.

The new guard calls `_valid_uuid_text`, which returns `False` for both `None`/`""` and any
non-UUID string, `True` only for a well-formed UUID. This correctly triggers
`_resolve_practitioner_from_instruction` for the name-in-field case so the resolver has
the chance to find the real UUID from the instruction tokens.

#### Downstream logic is already consistent

Lines 3765–3766 remain unchanged: any non-UUID value is cleared before the pre-resolved
value is considered. So the new gate adds pre-resolution opportunity; it cannot produce a
non-UUID landing in `practitioner_id`.

#### Edge case: name present, instruction doesn't mention the practitioner

`_resolve_practitioner_from_instruction` uses instruction tokens, not the `practitioner_id`
field. If the instruction carries no practitioner name, the resolver returns `None` and the
field is cleared — correct fail-safe behaviour, same as before for null inputs.

#### Verdict: correct, tightly scoped, no regression risk.

---

### 2. Clarifying copy priority (`app/routers/appointments.py` lines 4123–4126)

**Before**

```python
clarifying: Optional[str] = temporal_clarifying
if not clarifying:
    clarifying = _bernie_clarifying_question(missing_fields)
```

**After**

```python
clarifying: Optional[str] = _bernie_clarifying_question(missing_fields)
if not clarifying:
    clarifying = temporal_clarifying
```

#### What this fixes

When both `practitioner_id` and `date_from` are missing, `_bernie_clarifying_question`
produces the coherent multi-field phrase:

> "I need the doctor or nurse, and the day before I search."

Under the old order, `temporal_clarifying` (e.g. "Which day would you like me to check?")
would win even when the practitioner was also absent — asking only about the date while the
more fundamental gap (no practitioner at all) went unmentioned.

`_bernie_clarifying_question` returns `None` when `missing_fields` is empty, so the
fallback to `temporal_clarifying` still fires for all date-ambiguity cases where both
required fields are already resolved.

#### Missing-fields list is stable by construction

`missing_fields` is built at lines 4088–4092, appending `practitioner_id` then `date_from`
in that fixed order. `_bernie_clarifying_question` handles 1 or 2 entries directly; with 2
it uses the `"I need X, and Y before I search."` conjunction that the fixture asserts.
Currently only those two fields can appear (the function can only grow if future fields are
added to the append block), so the multi-item path is fully covered.

#### One accepted tradeoff: simultaneous temporal + missing-practitioner

If a same-day past-window block fires at the same time as a missing practitioner (both
`temporal_clarifying` and `missing_fields` are non-empty), the new ordering surfaces the
missing-fields copy and suppresses the temporal copy. The temporal block is still present
in `normalization.blocks` for callers that inspect it, but the top-level
`clarifying_question` string won't mention the time issue. This is a product tradeoff, not
a logic error:

- Asking for the practitioner first is the more fundamental gap — no slot search can
  proceed without it regardless of date.
- The full response structure still signals `clarification_required` and carries the
  normalization block.

No test covers this edge path today. If the product intent is to surface both messages, a
follow-up could either add a second surface copy field or check both conditions and prefer
a compound message. Flag for Ariadne/Yuri if needed; not a blocker for this sprint.

#### Verdict: correct. Single edge case accepted; document for follow-up if desired.

---

### 3. New fixture `tests/fixtures/bernie_scenarios/interpret_multi_field_missing_no_context.yaml`

```
id: interpret_multi_field_missing_no_context
category: booking_interpret_contract
reference_date: 2026-07-08
```

- **Action** is `interpret` with `instruction: "Book Margaret Thompson"` and empty
  `context_frames: []`. Valid per `KNOWN_ACTIONS`.
- **Expected result** `clarification_required` / `safe: false` — correct; both
  `practitioner_id` and `date_from` are absent.
- **`command_candidate.patient_id: "{patient_id}"`** — patient is identified from the
  instruction; correct because Margaret Thompson is in the test fixtures.
- **`command_candidate.practitioner_id: null` / `command_candidate.date_from: null`** —
  matches the expected post-resolution state.
- **`missing_fields.0: practitioner_id` / `missing_fields.1: date_from`** — matches the
  construction order at lines 4089–4092 (practitioner first, date second). Stable by
  construction.
- **`clarifying_question: "I need the doctor or nurse, and the day before I search."`** —
  matches `_bernie_clarifying_question(["practitioner_id", "date_from"])` exactly (two
  labels → `"I need the doctor or nurse, and the day before I search."`).
- **`normalization.safe: false`** — correct; no resolved date → normalizer cannot mark safe.
- **`forbidden_outcomes`** — `provider_called`, `appointment_written`, `audit_written` —
  correct for a clarification_required result.
- **`expected.appointment_written: false` / `audit_written: false`** — consistent with
  forbidden outcomes.

The YAML is well-formed and passes the loader's schema checks (`id` alphanumeric,
`reference_date` YYYY-MM-DD, turns non-empty, `action` in `KNOWN_ACTIONS`, `forbidden_outcomes`
in `KNOWN_FORBIDDEN_OUTCOMES`).

#### Verdict: fixture is correct and directly exercises the clarifying copy change.

---

### 4. README addendum (`tests/fixtures/bernie_scenarios/README.md`)

Adds one bullet to the existing list of covered slices:

> "multi-field-missing prompts: patient-only booking requests without context ask
> for missing practitioner/date details instead of guessing."

Accurate description of the new fixture and the behaviour change. No structural
changes to the README.

---

## Missing coverage

One gap worth noting for a follow-up sprint (not blocking):

**No fixture exercises the UUID gate change directly.** The multi-field missing fixture
reaches pre-resolution through the `None` path (the fake provider emits no practitioner_id
at all for this instruction), so it does not prove the "name in practitioner_id" branch
that the UUID gate change was written to handle. A complementary fixture that provides
e.g. `practitioner_id: "Dr Shera"` in the command candidate and confirms it resolves or
clears to the expected UUID/null would make the fix self-documenting in the test corpus.

---

## Summary

| Change | Verdict |
|---|---|
| UUID gate: `_valid_uuid_text` instead of bare truthiness | Correct — fixes silent drop of name-valued practitioner_id in live-provider payloads |
| Clarifying copy order: missing_fields before temporal | Correct — produces coherent multi-field questions; accepted tradeoff on combined temporal+missing edge |
| New fixture `interpret_multi_field_missing_no_context.yaml` | Correct — assertions match implementation exactly |
| README addendum | Accurate |

Sprint engine: **continuing**. No blocking findings. One optional follow-up:
add a fixture that directly exercises the name-in-practitioner_id pre-resolution
path to close the coverage gap on the UUID gate change.
