# LC4V6D1 Sol Acceptance

Date: 2026-07-16

Decision: `development_diagnostic_pass_no_runtime_remediation`

## Result

The fresh inspectable D1 matrix passes exactly:

- 24/24 extraction contracts;
- 24/24 Option A policy contracts;
- 24/24 composed layer-specific contracts;
- 24/24 safe;
- zero two-repeat variance; and
- zero authoring-invalid, parser-gap, policy-gap, or runner contract-gap cases.

The whole-fixture canonical hash is
`sha256:cee606a54a6b508e4d7b8f1a9ce1e6e4a0a905373deadce71c995901b1645ebc`.
The report file hash is
`sha256:b454ef44c99783f821d7bdf5699762fa968b093b28d8b0d60cd21a949b380403`.

All 12 fresh unknown-practitioner move probes deliberately and correctly differ
between layers. Context-free extraction preserves the explicitly named doctor
as an exact mention, retains the move/time contract, and does not claim a
linguistic ambiguity. Option A policy performs practitioner-directory lookup,
finds no ID, and fails closed with clarification only, no mutation tool, no
deltas, no completion claim, and no simulated write. A scorer that incorrectly
requires extraction and policy clarification to be identical would fail all
12 otherwise complete probes.

The six known-practitioner move controls, three resize normalization controls,
and three status plain/paraphrase/negation controls all pass. Normalized
earliest/latest bounds and lexical/multi-turn durations are lossless.

## Provenance and review

Sol authored and froze the 24 probes before baseline execution. Gemini 3.5
Flash independently reviewed the contracts at source `b8bafbdd` without
executing the parser and returned `DECISION: pass` with no authoring changes.

DeepSeek V4 Flash/high through Claude Code `--bare` supplied candidate
`67f232a1`. Sol rejected its self-pass because duration/normalized values were
not scored, practitioner mapping tests passed vacuously, safety was fail-open
for non-clarifying cases, and the hash omitted the fixture envelope. The
conceptual candidate moved directly to Sol recovery without a correction loop;
the original artifact and commit remain preserved.

Sol's recovered source at `bef040eb` adds exact envelope validation, whole-
fixture hashing, normalized bounds/duration evidence, non-vacuous name mapping,
field-level mismatches, and policy-exact safety without changing parser or
policy runtime code. Gemini independently reproduced 40/40 focused, 146/146
semantic-extraction, and 34/34 temporal-policy tests and returned
`DECISION: pass` on that exact head. Its review also observed the documented
pre-existing runtime-isolation node; it is not a D1 regression.

Sol's final serial D1, semantic extraction, temporal policy, Option A policy,
V6 aggregate-only validation, Ariadne, autonomous-continuation, and handover
preservation gate passed `287/287`.

Gemini's phrase that D1 “resolves” the sealed V6 certification failure is not
adopted. D1 proves only that the new public-category probes are correct and
that conflated clarification scoring fails them. The numerical alignment with
V6's public aggregate is a strong explanation hypothesis, not access to or
proof about sealed V6 cases. V6 remains failed and permanently sealed.

## Acceptance and next boundary

No parser or policy remediation is authorized or needed from D1. The supported
development issue is future certification-contract granularity: extraction and
policy clarification must be scored separately before composition.

The next decision is Yuri's. Sol recommends a genuinely fresh V7 with a new
content-blind, layer-specific evaluator and thresholds frozen before content.
Alternative reuse/rescoring of V6 would require a separately reviewed explicit
policy and is not recommended. Neither path may begin implicitly.

T3.1-T3.4 remain intact and blocked by default. T3.5/providers, local-model
product use, historical material, routes, APIs, UI, database, deployment,
release, and all live/write authority remain deferred.
