# Bernie LC4V4D3 Policy Decision Surface

Date: 2026-07-15

Status: user decision required before implementation.

## What D2 left

The exact current policy-gap population contains 20 ordinary development cases
under selection hash
`sha256:d3c6618cb586f5dc43824ec7a6e9e33957fee587a45c19f89e5a4bb425006e2a`.
They are deterministic and contain no remaining utterance-parser gap.

| Surface | Cases | Current disagreement |
|---|---:|---|
| Clarification alternatives | 5 | Explicit surface alternatives are not returned as choices |
| Corrected-patient resolution | 2 | Final corrected patient is not searched before slot/proposal work |
| Practitioner replay mapping | 3 | Two use the wrong final practitioner; one creates with no practitioner |
| Diary-state conflicts | 5 | Correct utterance entities are expected to become `mismatched` after diary comparison |
| Unsafe confirmation bypass | 5 | Conceptual read/action tools are selected before refusal |

## The material choice

Fourteen cases have a narrow fail-closed correction: reproduce explicit
alternatives losslessly, re-resolve corrected identities, map the final named
practitioner, and refuse a confirmation-bypass demand before selecting diary or
action tools.

The remaining six expose a real contract choice:

- `lc4v4d1_entity_practitioner_omitted_08` expects a booking to proceed without
  a selected practitioner and records `practitioner_id: null` in a created
  appointment delta.
- The five `*_mismatched_*` cases expect the composed result to change an
  utterance entity from `exact` to `mismatched` because an existing diary row
  differs. That mixes two distinct facts: what the user said and how it relates
  to current diary state.

## Options

### A. Strict separated semantics — recommended

- Echo only the alternatives explicitly surfaced by the user.
- Search/resolve the final corrected identity before availability or proposal.
- Ask whether “any available practitioner” is acceptable when practitioner is
  omitted; do not create a practitioner-less appointment.
- Keep utterance entity semantics exact. Represent duplicate/collision/
  disagreement in a separate diary-state relation and require the appropriate
  clarification or proposal policy.
- On an explicit `Bypass confirmation` demand, refuse immediately and select no
  diary/action tool before refusal.

This preserves clean architecture and fail-closed scheduling. It requires a
versioned correction/recontract for the six incompatible D1 expectations
instead of forcing them green.

### B. Compatibility-first old-oracle behavior

- Treat omitted practitioner as an implicit any-practitioner request and allow
  the abstract created delta to retain no practitioner.
- Rewrite utterance entity semantics to `mismatched` after diary comparison.
- Apply the other fourteen narrow policy fixes.

This can make the old 20-case oracle green with less fixture change, but it
conflates language interpretation with state joins and permits an appointment
contract that lacks a practitioner. Sol does not recommend it.

### C. Hybrid

- Treat omitted practitioner as an explicit any-practitioner search, but bind a
  concrete practitioner before any proposal/created delta.
- Keep the separate diary-state relation from Option A.

This supports receptionist shorthand while preserving a valid appointment. It
still requires a versioned D1 contract correction and a clear UI/clarification
rule for when “any practitioner” may be inferred rather than asked.

## Sol recommendation

Approve Option A. It is the most deterministic and safest foundation for a GP
receptionist assistant: omissions fail closed, corrections are re-resolved,
surface meaning remains lossless, diary conflicts stay explicit, and unsafe
authority demands stop before tool selection.

If approved, the implementation tranche will target the fourteen narrow fixes,
add a separate state-join relation for the five diary conflicts, and version the
six incompatible development expectations. It will not modify the utterance
parser further, open product write authority, or touch any protected holdout.

## Boundaries

The pre-plan protected-support search incident is recorded separately and is
not evidence for this decision. This packet is derived only from the already
frozen ordinary D1/D2 development population. Holdouts v1-v4 remain sealed;
future certification still requires Yuri's approval of a new holdout version or
explicit reuse policy. T3.1-T3.4 remain blocked, and T3.5/live/write surfaces
remain deferred.
