# LC4R6 Sol Recovery Amendment — Temporal Source-Evidence Audit

Date: 2026-07-14

Owner: GPT Sol, protected Conductor, acceptance/recovery owner, and integrator.

## Candidate history

DeepSeek V4 Flash/high through Claude Code `--bare` produced the first bounded
five-file candidate at `645d35f3`. Sol rejected that candidate before
integration because it duplicated the private development-audit conflict
ordering, did not actually reorder inputs in its order-invariance test, left
one drift test without a `run_check` assertion, and ambiguously labelled
pre-LC4R5 values as the LC4R5 baseline.

The unchanged worker lane revised those defects at `ce9c5fe3`; its evidence
commit is `90f5336a`. The revision uses the public `audit_candidates` path,
exercises real shuffled and reversed inputs, makes drift tests call the
fail-closed checker, and distinguishes `pre_lc4r5_baseline` from the current
`lc4r5_baseline`. The worker reported 29/29 focused tests and `--check`
passing. Sol independently reproduced those results.

## Sol-owned recovery amendment

The revised tests claimed to compare the complete aggregate taxonomy across
input orders but asserted only selection and bucket fields. Under the
documented low-risk recovery lease, Sol amended only
`tests/test_bernie_lc4r6_temporal_evidence_report.py` at `d37d229f` so both
shuffled and reversed cases compare the complete returned taxonomy, including
selection, buckets, insufficient subtypes, and conflict-pair counts. Sol also
removed two unused imports. No runtime, report, fixture, corpus, audit, scorer,
or provider surface changed.

After the amendment, Sol reproduced 29/29 focused tests, the authoritative
LC4R6 report check, and clean diff hygiene. A proportional serial preservation
gate across LC1, T1, all three T2 matrix layers, composed evaluation/audit,
action grammar/harness, Ariadne preflight, T3.1-T3.4 shadow scaffolding, and
LC4 repair reports passed except for the documented historical LC4R2
development-gap committed-report equality node. That node was rerun with only
`test_report_hash_deterministic` deselected; all remaining 32 audit tests
passed. The frozen historical report was preserved rather than regenerated.

## Accepted boundary

The development-only taxonomy remains exactly:

- selection: 159, hash `f56b4a20aad6161c`;
- insufficient surface evidence: 84, hash `c341652065504d17`;
- surface/contract conflict: 75, hash `fd04b9c86a54fea4`; and
- parser gap: 0, hash `e3b0c44298fc1c14`.

No parser remediation is authorized. Protected holdout v1 remains sealed.
T3.1-T3.4 remain intact and blocked by default. T3.5 providers, live calls,
routes/APIs, database, UI, deployment, historical diary, and write authority
remain deferred.

