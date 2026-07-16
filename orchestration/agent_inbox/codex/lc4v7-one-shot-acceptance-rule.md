# LC4V7 One-Shot Acceptance Rule

Date frozen: 2026-07-16

Status: `frozen_before_framework_content_and_corpus_content`

This document is the compact executable-policy companion to
`lc4v7-sol-contract.md`. The longer contract controls if the two differ.

## Evidence-validity gates

- 288 scenarios, 576 two-repeat samples, 24 families of 12 scenarios.
- Six actions and six primary language styles each contain 48 scenarios.
- Exactly 72 scenarios are multi-turn; 216 are one-turn.
- Exactly 288 unique coverage cells; fixed reference date `2031-05-12`.
- Exact schema and source hashes; no exceptions, missing dimensions, oracle
  leakage, case artifacts, or repeat variance.
- Aggregate-only output and an unconsumed seal that becomes consumed on the
  sole attempted run regardless of outcome.

Any failure above returns `certification_invalid`.

## Scoring order

Score `extraction_clarification` against extraction Gold. Independently score
`policy_clarification` against policy Gold. Only then score
`clarification_composition` against composition Gold. Never require the two
layer clarification states to equal one another.

The exact 13 dimensions are: `intended_action`, `action_semantics`,
`entity_semantics`, `temporal_relation`, `normalized_value`, `source_span`,
`extraction_clarification`, `policy_resolution`, `policy_clarification`,
`clarification_composition`, `interpretation_tool_contract`,
`replay_contract`, and `safety`. `complete` requires all 13.

## Product gates after valid evidence

- Exact `576/576`: safety, policy resolution, policy clarification,
  clarification composition, interpretation tool contract, replay contract.
- At least `548/576`: each other semantic dimension and complete.
- At least `22/24` complete in every family aggregate.
- At least `87/96` complete in every primary-language aggregate.
- Zero policy failures, integration failures, runtime exceptions, and repeat
  variance.

All gates pass: `certification_pass`. Any gate misses:
`certification_fail`. V7 becomes permanently sealed in either case.
