# Ariadne agent-error and correction register — revision 554

Date: 2026-08-19
Timestamp: 2026-08-19T09:32:45.0527773+10:00 (Australia/Brisbane)

## Revision scope

Revision 554 preserves AER-0642. The first AER-0641 draft used `direct_process_evidence` for `causal_claim_level`, but the register schema intentionally permits only `observation_only`. Canonical validation rejected the draft before the pattern report was published.

AER-0641 now uses the closed schema value. The register contains 642 incidents, all corrected or contained and none open. Aggregate construction cost is thirteen reruns.

Repair-only break-even remains two future closeouts at the measured nine-rerun avoidance rate. Cumulative break-even remains three closeouts.

## Prevention

Incident construction resolves every enum from the committed schema before publication. Descriptive evidence strength remains prose and cannot widen the closed vocabulary.
