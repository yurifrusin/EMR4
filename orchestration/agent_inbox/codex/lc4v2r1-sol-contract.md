# LC4V2R1 Sol Development Evidence Contract

## Decision and scope

Yuri authorized the recommended aggregate-guided development-only semantic
repair and corpus-engineering tranche on 2026-07-15. LC4V2R1 freezes a fresh
Sol-authored entity/normalization development matrix, audits the existing
deterministic extraction boundary, and remediates only independently
surface-supported gaps.

The committed LC4V2 aggregate report is a prioritization signal only. Protected
holdouts v1 and v2 remain sealed. No worker or orchestrator may open, enumerate,
list, search, import, run, regenerate, evaluate, hash-check, infer from, or tune
against either protected corpus, authoring surface, manifest, seal, receipt, or
per-case support module.

## Semantic boundary

The matrix covers the canonical entity slots `patient`, `practitioner`,
`location`, `appointment_type`, and `duration`. Text-only extraction may emit:

- `exact` when the utterance supplies one explicit value;
- `omitted` when it supplies no value or reference;
- `ambiguous` when it supplies a non-unique reference;
- `corrected` when a later correction replaces an earlier explicit value; and
- `negated` when an explicit value is rejected without an accepted replacement.

`mismatched` is deliberately excluded from parser remediation because mismatch
requires authoritative diary/entity context that is unavailable to the pure
text extraction boundary.

Lexical duration normalization is limited to unambiguous `quarter of an hour`,
`half an hour`, and `one hour` forms. A negated duration must not become an
accepted normalized duration. Existing canonical numeric-minute and temporal
behavior must remain unchanged.

Explicitly negated required patient, practitioner, or duration evidence must
fail closed into clarification, must not claim completion, and must not select
a mutating tool. Location and appointment type remain optional product facts;
their negation is classified but does not independently impose a new
clarification policy in this tranche.

## Frozen development evidence

Sol alone authors
`tests/fixtures/bernie_lc4v2r1_development/entity_normalization_cases.json`.
Every record is synthetic Gold/adjudicated development evidence with explicit
utterances, normalized-value expectations, full entity semantics, and
clarification/authority/tool-safety expectations. External workers may consume
the fixture but may not change it, derive replacement expectations from parser
output, or certify it.

The frozen fixture contains exactly 21 unique cases. Its byte-level SHA-256 is
`0f957518d1481ce831a55ca8d12388f245ae89ae516e96ef1d5037080d925afd`.

The parser baseline at source commit `7abf3aa9` is frozen in
`docs/bernie-lc4v2r1-baseline.json`: 17/21 normalized-value passes, 5/21 entity-
semantic passes, 17/21 clarification/authority/tool-safety passes, 21/21 no-
completion-claim passes, and 4/21 complete passes. The 17-case failure
selection hash is `ddfbc280bb822993`.

The audit must report baseline and post-remediation results for every dimension,
case-level development findings, deterministic selection hashes, and zero
variance across two repeats. It must fail closed on fixture/schema/hash drift,
unknown entity relations, duplicate IDs, expected-field injection, and any
protected/provider/runtime/write reference.

## Worker allocation

DeepSeek V4 Flash/high through Claude Code `--bare` receives one bounded lane
for the development-only audit harness, focused tests, and extraction repair.
GPT Sol retains architecture, expected evidence, acceptance, recovery, and
integration. Gemini 3.5 Flash through a fresh Antigravity project provides an
independent exact-head review after Sol acceptance. No external worker may
change protected refs or push.

## Authorized files

- `app/services/bernie/semantic_extraction.py`;
- `scripts/bernie_lc4v2r1_entity_normalization.py`;
- `tests/test_bernie_lc4v2r1_entity_normalization.py`;
- `docs/bernie-lc4v2r1-entity-normalization-report.json`;
- `docs/bernie-lc4v2r1-entity-normalization.md`; and
- the worker completion artifact.

The Sol-authored fixture and this contract are read-only to the worker.

## Acceptance

- the frozen fixture validates and its hash/count match this contract;
- every expected relation is directly supported by the authored surface;
- baseline findings are recorded before repair;
- all authorized parser gaps pass after repair without changing expected data;
- location/type extraction is conservative and cannot capture patient or
  practitioner names as values;
- negated required entities fail closed without mutation tools or completion
  claims;
- existing temporal relations remain unchanged and the ordinary LC4R10
  development baseline does not regress;
- two repeats have zero variance;
- DeepSeek does not self-certify the corpus and Gemini returns an independent
  exact-head `DECISION: pass`;
- T3.1-T3.4 remain intact and blocked by default; and
- T3.5, providers, routes, database, UI, deployment, release, historical diary,
  memory, confirmation, and write authority remain closed.
