# LC4R2 Sol Recovery Amendment

Date: 2026-07-14

Recovery owner and protected acceptance owner: GPT Sol.

## RECOVERY DECISION: amendment_permitted

DeepSeek V4 Flash's final LC4R2 evidence artifact remains
`DECISION: revision_required` and is preserved unchanged. Sol adopted the branch
as an untrusted candidate under the documented recovery lease and owns the
single amendment below.

## Amendment

`tests/test_bernie_development_gap_audit.py` embedded the disposable worker
worktree path in its deterministic report-hash test. That path would make the
test validate the wrong checkout after integration. Sol replaced it with a
repository root derived from `__file__`; the shared pinned virtual-environment
Python path remains explicit by design.

No implementation, replay policy, candidate classifier, corpus fixture,
provider, route, API, database, UI, T3 gate, protected evidence, or write
authority changed in this amendment.

## Safety-first acceptance evidence to verify

The LC4R1 base passed 212/1,152 appointment-delta comparisons; the LC4R2
candidate passes 209/1,152. Sol independently compared the exact pass sets. The
only lost records are:

- `lc4_dw1_dev_mt_001_03`;
- `lc4_dw1_dev_mt_002_03`; and
- `lc4_dw1_dev_mt_013_03`.

All three are authored Silver/pending reversal trajectories with an empty
`initial_diary_state.seeded_appointments`, a final “never mind / not needed”
turn, and an expected created delta. LC4R1 counted them only because its replay
heuristic inferred an earlier write from date/time text. LC4R2 removes that
unproved simulated write. The numerical decrease is therefore a fail-closed
safety correction, not permission to suppress the remaining aligned or
unsupported gaps.

Sol may accept LC4R2 as a safety-first diagnostic closeout only if:

- the deterministic focused/composed/scale and exact LC1 regression gates pass;
- safety remains 1,152/1,152 with measured zero repeat variance;
- every LC4R1 semantic-field count is preserved;
- oracle-mutation and six-action authored replay tests pass;
- the development report remains deterministic and honestly exposes aligned,
  conflict, and unsupported failures;
- Gemini 3.5 Flash independently returns `DECISION: pass`; and
- protected holdout, T3.5, provider/live, route/DB/UI, and write-authority
  boundaries remain closed.

This amendment does not change or certify protected holdout evidence. T3.1-T3.4
remain preserved; T3.5 and all provider/live/write authority remain deferred.
