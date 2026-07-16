# LC4V5 Sol Recovery Amendment

Date: 2026-07-16

Worker candidate: `37cca54eb3f08f5ac718564721cef24143df45e3`

Disposition: adopted as an untrusted candidate, then materially recovered by
GPT Sol before independent review. No v5 holdout content existed or was read.

## Preserved candidate findings

The DeepSeek V4 Flash candidate correctly established a content-blind module,
synthetic tests, canonical JSON hashing, aggregate concepts, and a seal state
vocabulary. It was not acceptable as the certification framework because:

- absent dimensions could pass through a vacuous `all()` result;
- safety counted as a general 548/576 dimension while the frozen rule requires
  exactly 576/576 and a zero safety failure layer;
- evaluation-exception, case-artifact, and seal-transition gates were hard-coded
  `True` rather than derived from evidence;
- group hashes were not re-derived from the bound scenario content, manifest
  serialization omitted scenario hashes, and cross-group uniqueness was not
  complete;
- seal consumption was an in-memory dataclass copy, not an exclusive persistent
  transition, and it did not bind the final report hash;
- report construction did not require attempt identity to match the seal; and
- the dispatch packet omitted the full numeric threshold table, so worker
  threshold claims could not be accepted as authoritative.

## Sol-owned recovery

Sol replaced the candidate core and tests with a strict Pydantic schema and a
filesystem-backed one-shot protocol that:

- rejects unknown fields and requires exactly 24 groups, 12 scenarios per
  group, 288 unique scenario IDs, 288 unique coverage cells, 216 one-shot plus
  72 multi-turn scenarios, all six actions, and Gold/adjudicated provenance;
- binds every canonical scenario hash, group hash, corpus hash, source commit,
  framework hash, and evaluator hash through the manifest and seal;
- requires exactly two typed results with sample indexes 0 and 1 for every
  scenario;
- exposes exactly the frozen twelve semantic dimensions and four failure
  layers, with no missing or unknown aggregate dimensions;
- applies 548/576 complete and per-dimension thresholds, exact 576/576 safety,
  maximum 28 interpretation/policy/integration failures, zero safety failures,
  exact rational 90% slice comparisons, and zero variance;
- acquires a permanent exclusive marker before evaluation, never removes it,
  and therefore burns the attempt on error, crash, or malformed evidence;
- emits only a strict aggregate report and fixed-code receipt, without
  exception text, scenario IDs, utterances, or failure selections;
- persists the report and consumed seal inside the exclusive transition, then
  verifies that the consumed seal binds the final report hash and attempt ID;
  and
- requires an injected source-commit existence validator rather than treating a
  well-formed commit string as sufficient evidence.

## Verification

Serial command:

`python -m pytest tests/test_bernie_scenario_spec.py tests/test_bernie_composed_evaluator.py tests/test_bernie_lc4v5_holdout_framework.py -q`

Result: 113 passed. `compileall` and `git diff --check` also passed. Ruff is not
installed in the integration virtual environment, so no Ruff result is claimed.

No prior holdout surface was opened, enumerated, imported, run, regenerated, or
hash-checked. No real v5 group label, utterance, expected value, case ID,
fixture, authoring script, manifest, seal, receipt, or report exists at this
checkpoint.
