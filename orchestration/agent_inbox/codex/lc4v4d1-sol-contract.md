# LC4V4D1 Sol Contract — Independent Development Diagnostic Matrix

Date: 2026-07-15

Authority: Yuri said to continue after accepting the LC4V4 closeout and its
recommended development-only diagnostic path.

Conductor, taxonomy, architecture, acceptance, recovery, and integration
authority: GPT Sol. Bounded implementation/test worker: DeepSeek V4 Flash/high
through Claude Code `--bare`. Independent veto reviewer: Gemini 3.5 Flash
through a fresh Antigravity worktree. DeepSeek Pro is not authorized.

## Objective

Build an inspectable, ordinary-development diagnostic matrix that separates:

1. unsupported or internally contradictory authored semantics;
2. deterministic interpretation/parser disagreement with an independent
   surface-supported oracle;
3. policy/replay contract disagreement after interpretation succeeds;
4. scorer/comparison disagreement after interpretation and replay succeed;
5. deliberately planned or unavailable behavior; and
6. complete supported passes.

LC4V4D1 is diagnostic only. It may identify a frozen parser-gap subset, but it
must not modify the parser, policy, replay, scorer, routes, providers, runtime,
or product behavior in this sprint.

## Protected boundary

Protected holdouts v1-v4 remain sealed. No worker or Sol diagnostic action may
open, enumerate, list, search, import, run, regenerate, evaluate, hash-check,
infer from, or tune against any protected fixture, support module, authoring
program, quality receipt, manifest, seal, consumed seal, test, filename
population, or case-level surface. LC4V4D1 may use only the accepted aggregate
v4 report, Sol acceptance, and closeout as historical inputs. The aggregate
weak axes may select diagnostic categories, but no v4 case, wording, label,
combination, or expected value may be reconstructed.

## Fresh probe matrix

Exactly 60 independently authored, inspectable Gold/adjudicated development
probes are required, each run twice:

- 30 isolated entity probes: patient, practitioner, location, appointment
  type, and duration, each crossed with exact, omitted, ambiguous, corrected,
  negated, and authoritative-diary-supported mismatched semantics. Only the
  target entity field may vary; other fields remain explicit and exact.
- 12 dialogue probes: matched single-turn and multi-turn forms covering
  clarification, correction, reversal, ellipsis, anaphora, and session
  restart. Every carried or replaced fact must have explicit turn-level source
  evidence.
- 12 matched policy/safety probes: one safe/explicitly-negated or
  safe/unsafe pair for each of create, move, resize, cancel, status change, and
  explain schedule. The pair must differ only in the authority-bearing safety
  clause.
- 6 diary-state probes: empty, exact duplicate, overlap, no slots, break, and
  terminal, with an otherwise identical surface and explicit synthetic diary
  evidence.

Every probe must have unique development namespace identity, exact lossless
source spans, a canonical semantic oracle authored before observation, an
independent policy expectation, explicit forbidden outcomes/tools, and a
surface-evidence rationale. Mismatched semantics are valid only where the
synthetic diary state explicitly proves the mismatch. No field may be labelled
ambiguous, omitted, corrected, negated, or mismatched merely to populate a
category.

## Diagnostic pipeline

The implementation must:

- validate fixture schema, exact population/family counts, IDs, source spans,
  matched-pair invariants, single-field isolation, and two-repeat policy;
- compute and freeze a deterministic fixture hash before observation;
- validate surface support without importing or consulting the production
  interpretation observation;
- execute the ordinary deterministic interpretation, replay, and composed
  scorer paths only after the oracle and surface validation pass;
- retain complete inspectable case-level results because this is ordinary
  development evidence, not a protected holdout;
- classify each probe into exactly one of:
  `authoring_invalid`, `parser_gap`, `policy_contract_gap`, `scorer_gap`,
  `planned_unavailable`, or `supported_pass`;
- name exact failed semantic fields and layers without collapsing a later
  failure into an earlier one;
- report two-repeat variance per probe and fail the diagnostic if any variant
  observation occurs;
- emit aggregate category/family/field totals plus a frozen candidate parser-
  gap selection hash; and
- refuse to emit a remediation-authorized decision.

Classification precedence is fixed:

1. invalid surface/oracle → `authoring_invalid`;
2. valid surface plus interpretation mismatch → `parser_gap`;
3. interpretation match plus replay/policy mismatch → `policy_contract_gap`;
4. interpretation and replay match plus scorer mismatch → `scorer_gap`;
5. explicitly planned-unavailable contract → `planned_unavailable`;
6. otherwise → `supported_pass`.

## Acceptance

Evidence is invalid unless all 60 fixtures pass authoring/surface validation,
all 120 executions are deterministic, every classification is reproducible,
the report hash and fixture hash are stable, and protected boundaries remain
intact.

Any candidate `parser_gap` is diagnostic only. It becomes eligible for a later
remediation contract only if all of the following hold:

- the source surface and exact span directly support the expected field;
- the oracle does not depend on hidden diary state except the explicit
  mismatched family;
- both repeats produce the same observed mismatch;
- no policy, replay, scorer, authoring, or planned-unavailable explanation
  applies; and
- Gemini independently confirms the classification on the exact recovered
  head.

Sol may reject or recover a worker candidate under the Ariadne recovery lease.
Conceptual classification defects receive no Flash correction loop. Final
acceptance must state whether the result is `diagnostic_valid` or
`diagnostic_invalid`, list the frozen classification counts and candidate hash,
and explicitly preserve that remediation remains unauthorized in D1.

## Owned paths

- `app/services/bernie/lc4v4_development_diagnostic.py`
- `tests/fixtures/bernie_lc4v4d1_development/`
- `tests/test_bernie_lc4v4d1_development_diagnostic.py`
- `docs/bernie-lc4v4d1-development-diagnostic.json`
- `docs/bernie-lc4v4d1-development-diagnostic.md`
- one durable worker receipt under `orchestration/agent_inbox/claude/`

The worker may not edit `AGENTS.md`, this contract, acceptance criteria,
protected evidence, historical reports, runtime parser/policy/replay/scorer
code, or any provider/product surface.

No T3.1-T3.5, provider, historical diary, route/API, database, UI, deployment,
runtime write, confirmation, release, or new-certification gate is opened.
