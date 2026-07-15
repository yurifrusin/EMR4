# LC4V4D5 Sol Acceptance

Date: 2026-07-16

Decision: `option_a_adoption_audit_valid_with_4_blockers`

GPT Sol retained taxonomy, recovery, acceptance, and integration authority.
DeepSeek V4 Flash/high through Claude Code `--bare` supplied one mechanical
candidate. Gemini 3.5 Flash/medium independently reviewed the exact recovered
head. DeepSeek Pro was not used.

## Exact evidence

- Contract head: `1ac0c71b929cff610f78d2ed8a803b057627d31e`.
- Worker candidate: `034df477f2f00945a1b5ed7af05d4190e9ef2e5c`,
  adopted as untrusted at `54017c72`.
- Sol recovered source: `80bfdfd49bad95589d35e7865d5a97493376f1bf`.
- Exact report head reviewed by Gemini:
  `4fba7408486819e7036af618ed93d1745da2aaba`.
- Gemini review commit `c3b23e48`, integrated at `85518715`.
- All-60 population hash:
  `sha256:ed65fe7821b0239066c532320bff05cc31a0699674987de8587efd74e05bbd44`.
- Five-difference selection hash:
  `sha256:b06da04e89b195b6de271b7ca4b8c22453426917b1d8c76389e4d41bf727aec7`.
- Complete D5 report hash:
  `sha256:e2c461ee3b1821c94574b33693efa88d21b99ecf9a95b1ac723b24a933c50564`.

## Accepted result

All 60 ordinary probes were run twice under legacy and twice under explicit
Option A, retaining 240 complete typed observations. Classification is exactly:

- 35 `legacy_equivalent`, including all three quarantined authoring-invalid
  probes;
- 20 `accepted_d4_versioned_change`;
- 1 `expected_versioned_relation` for the exact-duplicate diary relation;
- 3 `adoption_blocker_missing_mutation_deltas`; and
- 1 `adoption_blocker_target_field_conflict_and_missing_mutation_deltas`.

The four blockers are the safe move, resize, cancel, and status-change probes.
Option A drops their supported simulated appointment/audit deltas; resize also
mistakes its requested target duration for conflicting diary identity evidence
and clarifies. This is policy/replay adoption evidence, not parser evidence.

All 27 fail-closed gates pass. Legacy and Option A variance are zero, all 240
observations are complete, and no forbidden outcome/tool was observed.

## Worker recovery and verification

The Flash candidate reproduced the counts but classified named cases without
proving exact difference shapes, retained only fingerprints, omitted a legacy
variance/complete-count gate, and filtered unfamiliar forbidden observations.
Sol recovered those conceptual evidence defects without a correction loop.

D5+D4 focused preservation passed 65/65 serial tests and `git diff --check`
passed. Gemini reproduced the hashes, taxonomy, complete observations, exact
difference shapes, 27 gates, and diagnostic-only boundary, returning
`DECISION: pass` on `4fba7408`.

D5 authorizes no remediation itself. Holdouts v1-v4 remain sealed;
T3.1-T3.4 remain blocked; T3.5/providers/product/write surfaces remain
deferred. The next ordinary step is a separately frozen D5R1 remediation of
only these four supported Option A adoption blockers.
