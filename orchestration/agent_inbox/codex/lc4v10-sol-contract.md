# LC4V10 Sol Contract

Date: 2026-07-17

Decision: `genuinely_fresh_content_blind_framework_authorized`

## Authority

Yuri's 2026-07-17 standing authorization permits genuinely fresh LC4V10 and
successive fresh versions until certification passes, evidence shows progress
has stalled, or an unexpected material decision fork appears.

GPT Sol owns planning, thresholds, framework recovery, protected corpus
authorship, sealing, one-shot execution, acceptance, integration, and push.
DeepSeek V4 Flash/high through Claude Code `--bare` may implement one bounded
content-blind framework/test candidate. Gemini 3.5 Flash through a fresh
Antigravity project must independently veto the accepted framework before any
actual V10 content exists. DeepSeek Pro is forbidden.

## Clean-room boundary

Holdouts v1-v9 are sealed. No participant may open, enumerate, list, search,
import, run, regenerate, hash-check, infer labels from, or inspect any earlier
holdout fixture, framework, evaluator, authoring/support module, manifest,
seal, marker, threshold, report, receipt, test, filename, or per-case evidence.
V10 must not copy, import, adapt, or compare any earlier holdout implementation
or content.

Before the independent pre-content veto, the repository may contain only this
contract, the frozen acceptance rule, an empty generic V10 framework, opaque
in-memory tests, worker/review packets, and provenance receipts. No actual V10
utterance, patient, practitioner, diary state, expected value, scenario ID,
fixture, authoring module, manifest, seal, marker, report, or protected path may
exist. After Gemini passes, all external sessions close and Sol alone authors
and handles protected V10 content.

## Fixed comparable shape

The framework must fail closed unless the eventual protected corpus contains:

- exactly 24 unique groups;
- exactly 4 groups for each implemented action: `create`, `move`, `resize`,
  `cancel`, `status_change`, and `explain_schedule`;
- exactly 12 scenarios per group and 288 unique scenarios total;
- exactly 2 scenarios per group for each generic language form: `plain`,
  `paraphrase`, `speech_like`, `word_order`, `correction`, and `interval`;
- exactly 3 multi-turn scenarios per group, producing 72 multi-turn and 216
  one-turn scenarios;
- exactly 288 distinct coverage-cell identities; and
- exactly two repeat evaluations per scenario, producing 576 samples.

Group/action, language form, turn count, coverage-cell identity, scenario
identity, and repeat identity are evidence gates, not descriptive metadata.

## Scenario and layer contract

Each future scenario contains only receptionist utterances, explicit synthetic
diary state, and an independently authored Gold contract. Before product
execution, authoring validation must reject unknown or missing fields and every
cross-field contradiction without reading product output.

The evaluator must call the ordinary non-intercepted semantic extraction path,
explicit Option A policy resolver, exact canonical policy projection,
interpretation-tool projection, and replay path. Expected values may never be
passed to extraction, policy, projection, tool, replay, or safety functions.
There may be no scenario/group/language-form branch in product observation.

The exact canonical policy projection has these 14 JSON-safe fields:

1. `requires_clarification`;
2. `clarification_choices`;
3. `resolved_patient`;
4. `resolved_practitioner`;
5. `resolved_practitioner_id`;
6. `selected_tools`;
7. `authority`;
8. `diary_relation`;
9. `conflicting_fields`;
10. `downstream_outcome`;
11. `appointment_delta_count`;
12. `audit_delta_count`;
13. `simulated_write`; and
14. `entity_semantics_unchanged`.

Gold policy semantics and the exact projection must agree on clarification,
authority, mutation allowance, safety, selected tools, deltas, simulated
writes, identity resolution, and downstream outcome. A mutation-like outcome
without its required tool/delta/write evidence, or hidden mutation in a
non-mutation/refusal/clarification outcome, is authoring-invalid.

Score these dimensions independently:

1. intended action;
2. action semantics;
3. temporal relation and bounds;
4. normalized values;
5. entity semantics;
6. lossless source spans;
7. extraction clarification;
8. policy behavior;
9. exact policy projection;
10. policy clarification;
11. clarification composition;
12. interpretation tool;
13. replay; and
14. safety.

`complete` is the conjunction of all fourteen. Extraction clarification and
policy clarification may intentionally differ when explicit diary context
resolves or introduces uncertainty.

## Evidence versus product decision

The framework must import
`app.services.bernie.certification_decision_taxonomy.classify_certification`.
It may not reimplement, override, or reinterpret its precedence:

- evidence-procedure failure -> `certification_invalid`;
- valid evidence plus any product-gate failure -> `certification_fail`;
- valid evidence plus no product-gate failure -> `certification_pass`.

Safety misses, semantic misses, policy failures, and integration failures are
product results. They never invalidate otherwise complete evidence.

## Immutable binding and one-shot state

The framework must fail closed unless fixture, framework/evaluator, manifest,
seal, and threshold schemas are exact; all byte hashes and Git blobs match;
the named corpus-source commit is an ancestor of the execution head; and the
exact protected blobs at that source commit match the execution inputs.

The seal binds the manifest, thresholds, and unique attempt ID in state
`unconsumed`. Exclusive marker creation must succeed before any protected
fixture read or product execution. After marker creation every exit path,
including validation failure or exception, leaves the attempt consumed. No
run, failure, or exception may restore or reuse it.

The aggregate report must never contain or permit recovery of utterances,
expected contracts, patient/practitioner names, diary state, scenario IDs,
case-level results, source spans, or per-case hashes. It may contain only fixed
aggregate counts, generic group labels, language-form labels, gate names,
evidence/product counters, decision, and complete-report hash.

## Content-blind worker surface

The bounded worker may create or edit only:

- `app/services/bernie/lc4v10_content_blind_framework.py`;
- `tests/test_bernie_lc4v10_content_blind_framework.py`; and
- `orchestration/agent_inbox/claude/lc4v10-deepseek-framework-candidate.md`.

Tests use opaque in-memory placeholders and temporary files/repositories. They
must contain no plausible receptionist corpus or real expected values. The
worker may not create a fixture, authoring module, manifest, seal, marker,
threshold file, report, evaluator sidecar, or actual scenario text; edit
product parser/policy/runtime code; access earlier holdouts; or commit/push
protected refs.

## Framework acceptance before content

Sol must reject fail-open shape/schema, cross-field, oracle-separation,
projection, source-binding, seal, marker, aggregate-only, exception-consumption,
or decision-taxonomy behavior. Conceptual defects move directly to Sol's
recovery lease without a Flash correction loop. A single mechanical omission
may receive at most one bounded revision.

The accepted framework must pass focused tests and ordinary isolation checks.
A genuinely fresh Gemini project must return `DECISION: pass` on the exact
accepted head before actual V10 content or protected artifacts are created.

## Closed surfaces

T3.1-T3.4 remain intact and blocked. T3.5/providers, historical data,
runtime/product wiring, routes, APIs, UI, database, deployment, release, and
every live/write-authority surface remain deferred.
