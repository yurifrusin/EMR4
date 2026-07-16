# LC4V9 Sol Contract

Date: 2026-07-16

Decision: `genuinely_fresh_content_blind_framework_authorized`

Yuri authorized genuinely fresh LC4V9 after LC4V8D1 reached its documented
ordinary-development clean exit. GPT Sol owns planning, schema and threshold
authorship, framework recovery, protected corpus authorship, sealing, one-shot
execution, acceptance, integration, and push. DeepSeek V4 Flash/high through
Claude Code `--bare` may implement one bounded content-blind framework/test
candidate. Gemini 3.5 Flash through a fresh Antigravity project must veto the
accepted framework before any actual V9 content exists. DeepSeek Pro is
forbidden.

## Clean-room protected boundary

Holdouts v1-v8 are sealed. No participant may open, enumerate, list, search,
import, run, regenerate, hash-check, infer labels from, or inspect any protected
fixture, support/authoring module, manifest, seal, receipt, test, filename, or
per-case evidence. V9 must not copy or reuse any prior protected implementation
or content. Its framework is authored only from this contract, the generic
ordinary certification taxonomy, LC4V8D1's accepted aggregate conclusion, and
ordinary product interfaces.

Before real content exists, external workers may see only the empty framework,
opaque in-memory test objects, fixed shape, schemas, thresholds, generic policy
projection contract, and evidence rules. After Gemini's pre-content pass, all
external sessions close. Sol alone authors, validates, commits, manifests,
seals, executes, and accepts the actual V9 corpus.

## Fixed comparable shape

The framework must require exactly:

- 24 unique groups;
- 12 scenarios per group and 288 unique scenarios total;
- 4 groups for each of `create`, `move`, `resize`, `cancel`,
  `status_change`, and `explain_schedule`;
- 2 scenarios per group for each of `plain`, `paraphrase`, `speech_like`,
  `word_order`, `correction`, and `interval`, producing 48 scenarios per form;
- exactly 3 multi-turn scenarios per group and 72 total; and
- two repeat evaluations per scenario, producing 576 samples.

Every scenario must have a unique coverage-cell identity. Group/action,
language-form, turn-count, and coverage-cell counts are evidence gates, never
soft reporting metadata.

## Layer and scoring contract

Each scenario contains only receptionist utterances, explicit synthetic diary
state, and a Gold expected contract. The evaluator must call the ordinary
non-intercepted `extract_semantics`, explicit Option A `resolve_policy`,
interpretation-tool projection, and replay path without passing expected values
downstream. It scores these dimensions separately:

1. intended action;
2. action semantics;
3. temporal relation and bounds;
4. normalized values;
5. entity semantics;
6. lossless source spans;
7. extraction clarification;
8. policy behaviour;
9. policy projection;
10. policy clarification;
11. clarification composition;
12. interpretation tool;
13. replay; and
14. safety.

`complete` is the conjunction of all fourteen. Extraction and policy
clarification may intentionally differ. Policy behaviour judges the resolver's
semantic outcome; policy projection judges the exact canonical representation.
Neither may be silently substituted for the other.

## Canonical policy projection

The Gold policy projection and actual policy projection must contain exactly
these fourteen fields, with no omissions or unknown fields:

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

Null values remain explicit and tuples project to JSON arrays. The semantic
policy outcome is separately constrained to `propose_mutation`,
`proceed_read`, `clarify`, `refuse`, or `no_action`, together with explicit
`mutation_allowed` and `safe` booleans.

Before any product execution, Gold authoring validation must fail closed on
cross-field contradictions. A mutation outcome requires the appropriate tools,
nonzero simulated mutation evidence, and authority consistent with a proposal;
clarify, refuse, read, and no-action outcomes may contain no hidden mutation.
Resolved identity fields, clarification state, temporal relation/bounds, diary
relation, tool selection, deltas, simulated write, and unchanged-entity claims
must agree. These are evidence-validity checks on Gold, not product scores.

## Generic decision taxonomy

The framework must import
`app.services.bernie.certification_decision_taxonomy.classify_certification`.
It may not reimplement or override the precedence:

- evidence-procedure failure -> `certification_invalid`;
- valid evidence plus any product-gate failure -> `certification_fail`;
- valid evidence plus no product-gate failure -> `certification_pass`.

Nonzero product policy or integration failures must never make the evidence
invalid. This rule does not reinterpret any earlier holdout.

## Immutable binding and one-shot state

The framework must fail closed unless:

- fixture, manifest, seal, threshold, and report schemas reject unknown fields
  and validate exact required fields;
- fixture, framework, evaluator, and threshold bytes match their SHA-256
  manifest bindings;
- the loaded evaluator's exact source path and bytes are the manifest-bound
  evaluator, established through `inspect.getsourcefile` or an equally strict
  source identity check;
- the manifest names a committed corpus-source Git commit that is an ancestor
  of the execution head and whose exact fixture/framework/evaluator/threshold
  blobs match;
- the seal binds the manifest and unique attempt ID;
- the attempt begins `unconsumed`; and
- exclusive durable marker creation succeeds before evaluation.

After marker creation, every exit path consumes the attempt. No exception,
invalid evidence, or product failure may restore, delete, clean up, or reuse
it. Aggregate output must contain no utterance, expected contract, case ID,
per-case result, or recoverable oracle content. Actual protected files may not
exist before the pre-content Gemini veto.

## Content-blind worker surface

The bounded worker may create/edit only:

- `app/services/bernie/lc4v9_content_blind_framework.py`;
- `tests/test_bernie_lc4v9_content_blind_framework.py`; and
- `orchestration/agent_inbox/claude/lc4v9-deepseek-framework-candidate.md`.

Tests generate opaque in-memory placeholder objects and temporary manifests,
seals, Git bindings, markers, and reports. They must contain no actual V9
receptionist corpus. The worker may not create a fixture, evaluator, authoring
module, manifest, seal, thresholds, report, actual case text, or protected
artifact; edit product parsers or policy; access protected history; or
commit/push protected refs.

## Framework acceptance before content

Sol must reject fail-open schema, Gold cross-field validation, source binding,
evaluator identity, seal, marker durability, aggregate-only reporting,
decision-taxonomy, or exception-consumption behaviour. A conceptual defect
moves directly to Sol recovery without a Flash correction loop. The accepted
framework must pass focused and ordinary isolation tests, then Gemini must
return `DECISION: pass` on its exact head before any actual corpus file,
evaluator, authoring surface, threshold file, manifest, or seal is created.

## Closed surfaces

T3.1-T3.4 remain intact and blocked. T3.5/provider calls, historical data,
runtime/product wiring, routes, APIs, UI, database, deployment, release, and
all live/write authority remain deferred.

