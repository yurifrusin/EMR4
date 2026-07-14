# LC4R6 Temporal Source-Evidence Audit — Sprint Contract

Date: 2026-07-14

Active Conductor, sprint planner, architecture/acceptance owner, recovery
owner, and protected integrator: GPT Sol. Planning mode is
`sol_direct_routine`. DeepSeek V4 Flash/high through Claude Code `--bare` owns
one bounded report/test lane. Gemini 3.5 Flash through Antigravity owns the
independent veto review. DeepSeek Pro is not a Conductor or worker.

Settings fingerprint:
`sha256:8001d1ecaa70140748ac50277d0beeb33db37ab03e80a635a5da66c90aa69db8`

## Direction-dialogue disposition

Skipped. Sol's development-only profiling produced a complete deterministic
taxonomy with no parser-remediation subset. External models do not plan,
allocate, accept, or integrate this sprint.

## Protected evidence boundary

Use only the ordinary Silver/pending LC4 development partition. Do not open,
enumerate, import, load, regenerate, evaluate, hash-check, infer from, or tune
against protected holdout v1 or any fixture, support module, seal, receipt, or
report belonging to it. Do not inspect historical diary material or transmit
patient/practice data. No provider inference, T3.5 adapter, route/API,
database, UI, deployment, memory, RAG/GraphRAG, confirmation, or write
authority is permitted.

Generated fixtures, scenario labels, and source spans are evidence inputs for
the audit only. They must never feed values into interpretation. A source span
proves where authored text came from; its field name does not override the
ordinary meaning of `at`, `around`, missing bounds, or missing point times.

## Frozen selection

Starting from exact LC4R5 behavior, select only development scenarios which:

1. are currently classified `aligned_failure` by the ordinary development
   audit;
2. fail the composed temporal-relation semantic field; and
3. are evaluated from their authored dialogue turns without reading protected
   evidence.

The frozen selection is exactly 159 scenarios, hash `f56b4a20aad6161c`.

## Taxonomy

Derive the surface relation by applying the existing oracle-free temporal
extractor independently to every dialogue turn and retaining the last
non-`unspecified` relation and bounds.

Classify each selected scenario into exactly one bucket:

- `insufficient_surface_evidence`: the contract expects a non-unspecified
  relation, but the dialogue has no extractable point/bound/interval relation;
- `surface_contract_conflict`: dialogue has an explicit surface relation that
  differs from the contract relation; or
- `parser_gap`: explicit surface evidence supports the contract relation but
  the final interpreter observation differs.

Frozen results:

| Bucket | Count | Selection hash |
|---|---:|---|
| insufficient surface evidence | 84 | `c341652065504d17` |
| surface/contract conflict | 75 | `fd04b9c86a54fea4` |
| parser gap | 0 | `e3b0c44298fc1c14` |

The 84 insufficient cases divide into expected relation counts:

- exact 18;
- not-before 18;
- not-after 18;
- interval 18; and
- approximate 12.

The 75 conflicts divide into expected/observed relation pairs:

- approximate/exact 10;
- exact/approximate 2;
- interval/approximate 3;
- interval/exact 14;
- not-after/approximate 2;
- not-after/exact 16;
- not-before/approximate 3;
- not-before/exact 14;
- unspecified/approximate 2; and
- unspecified/exact 9.

## Required implementation

Add an audit-only deterministic LC4R6 report helper with `--check`, a committed
JSON report, a concise implementation note, and focused tests. The report must:

- reproduce the 159/84/75/0 counts and all four hashes;
- reproduce every frozen subtype count;
- record the LC4R5 semantic baseline unchanged;
- prove safety `1152/1152` and zero variance over 2,304 samples;
- be invariant to input ordering;
- fail closed for a new taxonomy bucket, selection drift, corpus drift, or
  report drift; and
- emit aggregate authored-synthetic evidence only, not full scenario payloads.

Do not change `semantic_extraction.py`, `development_gap_audit.py`, composed
scoring/replay, scenario schema, source-span validation, fixtures, generators,
or any earlier report. LC4R6 is diagnostic because the parser-gap set is
empty. Do not manufacture a remediation subset.

## Owned files

The worker may add:

- `scripts/bernie_lc4r6_temporal_evidence_report.py`;
- `tests/test_bernie_lc4r6_temporal_evidence_report.py`;
- `docs/bernie-lc4r6-temporal-evidence-report.json`;
- `docs/bernie-lc4r6-temporal-evidence-audit.md`; and
- `orchestration/agent_inbox/codex/lc4r6-dw1-completion.md`.

No other file may change.

## Acceptance

Acceptance requires exact frozen taxonomy reproduction; unchanged semantic
counts `880/814/628/101/300/782`; safety `1152/1152`; zero variance; report
`--check`; focused and proportional LC1-LC4 plus T1/T2/T3.1-T3.4 checks; clean
diff; and Gemini `DECISION: pass` on the exact recovered head.

Protected holdout v1 remains sealed. T3.5, providers, live calls, APIs,
database, UI, deployment, and write authority remain deferred.

Sprint engine state: continuing.
