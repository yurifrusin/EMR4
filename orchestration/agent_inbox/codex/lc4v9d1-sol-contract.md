# LC4V9D1 Sol Contract

Date: 2026-07-16
Status: `frozen_before_diagnostic_content`

## Purpose

Create an ordinary, inspectable synthetic development diagnostic for the
aggregate LC4V9 hypothesis that non-create language may lose patient identity
or diverge during policy projection. This is not certification, does not reuse
or approximate protected V9 cases, and cannot authorize a new holdout.

## Frozen population

- 30 new synthetic Gold probes: six per action for `move`, `resize`, `cancel`,
  `status_change`, and `explain_schedule`.
- Exactly six fresh language structures per action: direct named patient,
  `appointment for` patient, possessive patient, patient-first word order,
  polite/speech-like request, and two-turn additive context.
- Every probe uses a fresh synthetic full patient name, one mapped synthetic
  practitioner, explicit reference date, and action-sufficient fields.
- At least one safe negated instruction and one unsafe bypass/refusal pair per
  mutation action may be added only inside the fixed 30, with matched Gold.
- Gold must independently state extraction identity/semantics, intended action,
  policy outcome, and the exact 14-field canonical projection.

## Diagnostic layers

Each probe is evaluated twice through the ordinary, non-intercepted path:

1. `extract_semantics(utterances, reference_date)`;
2. `resolve_policy(...)` from extraction plus explicit synthetic diary state;
3. exact JSON-safe 14-field projection; and
4. independent safety/outcome derivation.

Classify each probe as exactly one of:

- `pass`;
- `extraction_gap` — intended action or patient identity/semantics first
  diverges in extraction;
- `policy_gap` — extraction Gold passes but policy outcome/projection diverges;
  or
- `authoring_invalid` — the inspectable Gold contradicts its utterance or
  cross-field policy contract.

The report records aggregate counts, explicit probe IDs by class, two-repeat
variance, fixture/report hashes, and no protected evidence. D1 is diagnostic
only: it must not change parser or policy code.

## Candidate files and authority

DeepSeek V4 Flash/high through Claude Code `--bare` may create only:

- `app/services/bernie/lc4v9d1_development_evidence.py`;
- `tests/fixtures/bernie_lc4v9d1_development/probes.json`;
- `tests/test_bernie_lc4v9d1_development.py`; and
- `orchestration/agent_inbox/claude/lc4v9d1-worker-closeout.md`.

The candidate must not edit product parser/policy code, handover, contracts, or
historical evidence. It commits only on its disposable branch. Sol owns Gold
adjudication, acceptance, recovery, baseline classification, protected
integration, closeout, master/handoff, and push.

## Forbidden surfaces

All holdouts v1-v9, including their fixtures, evaluator/authoring/support code,
manifests, seals, markers, tests, and per-case evidence, are forbidden. The
V9 aggregate report itself is unnecessary and must not be opened by the
worker. Historical diary data, T3, providers, live calls, APIs, database, UI,
deployment, and write authority remain closed. No broad filename search or
repository-wide grep is permitted.

## Acceptance

- fixture shape and Gold cross-fields fail closed;
- observation code never reads Gold before producing extraction/policy output;
- exactly 60 observations, stable repeat pairs, and one class per probe;
- safety is derived from runtime behavior, not copied from Gold;
- tests cover fail-open schema, oracle leakage, projection drift, and variance;
- focused tests pass serially; and
- Sol independently audits all 30 utterance/Gold pairs before accepting any
  classification.

Conceptual taxonomy, provenance, Gold, or evidence failures move immediately
to Sol recovery without a Flash correction loop. A mechanical defect may
receive at most one bounded revision under the standing protocol.
