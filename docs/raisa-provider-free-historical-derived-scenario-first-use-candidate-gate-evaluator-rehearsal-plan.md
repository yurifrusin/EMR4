# Raisa provider-free historical-derived scenario first-use candidate gate evaluator rehearsal — plan

Date: 2026-08-24

Timestamp: 2026-08-24T09:52:28.8027597+10:00 (Australia/Brisbane)

Operation: `raisa-provider-free-historical-derived-scenario-first-use-candidate-gate-evaluator-rehearsal`

Reasoning level: Extra High

## Objective

Implement the already accepted closed first-use contract as one pure,
provider-free, typed in-memory evaluator before any reusable
historical-derived scenario can be written.

This tranche proves the evaluator only on wholly authored-synthetic candidates.
It does not evaluate, admit or materialise a historical-derived candidate and
does not access the private archive or any ignored measurement output.

## Authority and source

The active latch and Yuri's delegated first-use gate timing authorize this
provider-free evaluator rehearsal. It builds on the accepted measurement at
machine-resolved closeout source
`7f9a526e57a4c10502f01b0e7c1cc5ec6910f00c` and the existing
`raisa.historical_derived_scenario_first_use_gate.v1` contract.

The implementation may add only:

- `orchestration_harness/historical_diary_first_use_candidate_gate.py`;
- `scripts/raisa_provider_free_historical_derived_scenario_first_use_candidate_gate_evaluator_rehearsal.py`;
- the focused test file;
- this plan, its threat-model delta and bounded closeout evidence.

No archive, ignored attempt output, product source, database, route, client,
runtime configuration or protected evidence may be read or changed.

## Typed input form

Pydantic models use strict validation and `extra="forbid"`. The candidate and
declaration contain no unconstrained prose field. Every string other than a
Git object ID and SHA-256 digest is a `Literal`; every integer is bounded.

The trusted policy binds exactly:

- accepted source commit:
  `7f9a526e57a4c10502f01b0e7c1cc5ec6910f00c`;
- purpose: `provider_free_reception_check_in_context_scenario_development`;
- identity policy: `source_independent_synthetic_identity_only`;
- date policy: `relative_day_offset_only`;
- authority ceiling: `local_provider_free_development_test_only`;
- candidate digest algorithm: `sha256`;
- initial admissible artifact class: `minimised_structural_scenario`.

The candidate payload contains only relative day zero and one to twelve typed
structural events. Each event contains a closed event kind, a relative minute,
a synthetic subject slot and a resource slot. Event kinds are exactly:

- `scheduled_slot_present`;
- `scheduled_slot_added`;
- `scheduled_slot_removed`;
- `scheduled_slot_moved`;
- `scheduled_slot_replaced`; and
- `scheduled_slot_format_changed`.

There are no name, contact, note, diagnosis, source text, filename, path,
absolute date, timestamp, HMAC token, key or mapping fields. Unknown fields and
unknown enum values fail schema validation before evaluation.

## Canonical binding and utility

The evaluator computes SHA-256 over UTF-8 canonical JSON with sorted keys and
compact separators. The declaration's digest must match exactly.

The declaration carries a typed structural-utility reading, but the evaluator
recomputes it and rejects any mismatch. Initial minimised utility requires:

- three to twelve events;
- at least three distinct relative minutes;
- a positive span from 10 through 120 minutes;
- at least two distinct event kinds;
- at most four synthetic subject slots; and
- at most two resource slots.

These thresholds admit only a small temporal topology. They do not claim that
the topology is anonymous, representative or suitable for product use.

## Closed decisions

Evaluator output is restricted to:

- `blocked`;
- `revision_required`; or
- `admitted_for_exact_declared_artifact_only`.

`whole_day_or_near_lossless_replay` is always `blocked`.
`bounded_multi_event_scenario` is initially `revision_required`.
Only `minimised_structural_scenario` can reach the exact-artifact decision, and
only when source, digest, declaration, zero forbidden-field reading and utility
all pass.

An admitted result binds the exact source, digest, class, purpose and authority
ceiling and states `non_transitive=true`. The evaluator opens no write. A later
materialiser requires a separate accepted plan and the exact admission receipt.

## Authored-synthetic rehearsal matrix

The deterministic script and focused tests must prove:

1. one exact minimal positive candidate reaches the exact-artifact decision;
2. wrong accepted source is blocked;
3. mismatched digest is blocked;
4. a nonzero forbidden-field reading is blocked;
5. a declaration/utility mismatch is blocked;
6. insufficient minimised utility requires revision;
7. bounded multi-event class requires revision;
8. whole-day or near-lossless replay is blocked; and
9. abbreviated Git IDs, unknown enums, unknown keys, free-form event values and
   out-of-range integers are schema-rejected before evaluation.

The committed reading is labelled
`authored_synthetic_gate_behavior_only`. A synthetic positive result is not a
historical first-use admission because the existing gate explicitly does not
apply to wholly authored-synthetic tests.

## Verification and acceptance

Acceptance requires:

- the focused matrix and all historical-Diary provider-free tests pass;
- Ruff, compileall, JSON/schema and source-boundary checks pass;
- no archive or ignored attempt path is opened by implementation or tests;
- no provider/network/model, product, database, client or filesystem writer
  exists in the evaluator;
- the accepted source is a full 40-character object ID resolved from Git; and
- the first-use gate remains `closed_pending_candidate_specific_evaluation`.

The evaluator is accepted only if its positive result is exact, non-transitive
and write-free and every hostile case fails closed.

## Parallelism efficacy

- DeepSeek: declined, negative leverage. The native Harness remains paused and
  Claude Code is not a silent fallback; the small authority-critical evaluator
  is not a separable worker package.
- Gemini: not applicable, neutral leverage. This is a provider-free typed
  mechanism with deterministic acceptance and no independent model veto need.
- Native subagents: declined, negative leverage. Schema, digest, decision and
  tests form one tightly coupled seam whose briefing/reconciliation cost would
  exceed parallel benefit.
- GPT Sol: serial owner for plan, implementation, verification, acceptance,
  Git and closeout.

Reassess only if deterministic verification exposes a genuinely separable
mechanical repair or before any future external verifier dispatch.

## Closed surfaces

No historical archive or ignored attempt access; no reusable artifact write;
no provider/model/network; no product, patient, appointment, clinical or
protected data; no database, route, API, client or runtime; no ordinary-
practice enablement; no production, deployment, release or Pages; no protected
ref movement. Preserve `docs/branding/` and every unrelated untracked file.
Stage explicit paths only.
