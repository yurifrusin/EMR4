# LC4V7D1 Sol Baseline Recovery

Date: 2026-07-16

Decision: `deepseek_candidate_rejected_sol_recovery_baseline_valid`

DeepSeek V4 Flash/high produced candidate commit
`f28bac48204eea65cae3a5cd3b49d8e92e466d69` through Claude Code `--bare`.
Its bounded implementation was useful and stayed within the three owned files,
but its `CANDIDATE: ready` self-decision is rejected. No correction loop was
opened because the primary defect concerns evidence integrity rather than a
missing mechanical assertion.

## Preserved candidate failure

The candidate constructed `report_hash` while `selection.non_pass_count` was
still zero and `selection.selection_hash` was still empty, then mutated those
fields. The advertised report hash therefore did not bind the complete final
report. Its policy comparison also omitted deterministic delta counts and the
simulated-write marker, allowing a composed pass to ignore those policy
outputs. The closeout named the parent source head as its exact commit, and one
test was an empty placeholder.

These defects invalidate the candidate's evidence hash and self-acceptance,
but they do not invalidate the fresh fixture or the observed repeat results.

## Sol amendments under the recovery lease

Sol adopted the candidate as untrusted source and:

1. moved non-pass selection construction before report hashing so the final
   hash binds the complete report except its self-referential hash field;
2. compared appointment-delta count, audit-delta count, and simulated-write
   state using the fixture's derived no-mutation/create contract;
3. strengthened fixture validation for all expected field types, enum values,
   time canonicals, non-negative in-range turn indices, and duplicate forms;
4. made the runner accept an injected fixture solely so invalid-fixture paths
   can be tested without product execution; and
5. replaced the placeholder with direct hash-binding and invalid-fixture
   assertions.

## Recovered frozen baseline

The recovered runner validates the exact 24-case fixture and produces zero
variance across 48 observations:

- fixture hash:
  `sha256:03544ffab7d3a720faf6cba3cac7f33c5e45e7a42dfec231223334fdd335b2ea`;
- complete report hash:
  `sha256:c093616ff2916097e546cda2e4c9681eaaf1ef27b49fc0d86a5651cc7ef7a97d`;
- frozen valid-gap selection hash:
  `sha256:643339dfb9008f8df1b81b5e8e8effbf5d6d4561bafa67376d721fb0c185cd77`;
- aggregate: normalization 18/24, extraction 6/24, policy 12/24,
  composed 0/24, safety 12/24, variance zero; and
- classifications: 6 normalization gaps, 12 parser gaps, 6 policy gaps,
  zero authoring invalid, zero contract-layer gap, and zero pass.

Gemini's pre-baseline review found no authored defects. Sol independently
adjudicates all 24 non-passes as valid gaps matching the four frozen questions.
The exact case-level selection is permanently recorded in
`docs/bernie-lc4v7d1-development-baseline.json`. Product remediation is now
authorized only for that selection.

Protected holdouts v1-v7 remained unopened. T3.1-T3.4 and all T3.5/provider,
historical-data, product/runtime, API/UI/database, deployment, and write gates
remain unchanged.
