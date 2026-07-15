# LC4V4D5 Sol Recovery Amendment

Date: 2026-07-16

Worker candidate: `034df477f2f00945a1b5ed7af05d4190e9ef2e5c`.
Adopted as untrusted candidate at `54017c72`.

DeepSeek V4 Flash/high supplied useful diagnostic scaffolding and reproduced
the frozen `35/20/1/3/1` counts, but its `candidate_complete` evidence is
rejected. The defects are conceptual, so Sol opened no correction loop.

The candidate classified each of the five named cases by ID without proving its
exact difference shape; a known case could acquire extra regressions and still
pass. It retained only fingerprints rather than the contract-required complete
legacy and Option A observations, did not gate legacy repeat variance or exact
120/120 observation counts, omitted several replay fields from difference
detection, and filtered unknown forbidden observations away unless they matched
a small hard-coded vocabulary.

Sol retained the mechanical audit and recovered it by freezing and checking the
complete exact five-case difference map, retaining both complete observations
for both policy versions in every case record, adding exact legacy and Option A
observation-count gates, gating legacy as well as Option A variance, comparing
clarification and forbidden replay fields, and treating every recorded
forbidden outcome/tool as evidence rather than filtering unfamiliar values.
Focused tests now exercise complete observations, exact difference shapes, and
an unknown forbidden-tool value.

D5 remains diagnostic only and authorizes no policy, parser, fixture, default,
product, provider, or write change.
