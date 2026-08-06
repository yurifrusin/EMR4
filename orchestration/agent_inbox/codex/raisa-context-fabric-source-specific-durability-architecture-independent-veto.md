# Independent veto — source-specific durability architecture

Date: 2026-08-06

Decision: `revision_required`

Reviewed source HEAD:
`92cf76b17bbab276df701ee1e0af0da77e1768a9`

Review worktree:
`C:\Users\sarashera\EMR4-worktrees\r15`

## Findings

- P0: none.
- P1: the supposedly exact closed schema allowed safety-critical list
  substitution. Projection/audit allowlists, producer transaction members,
  checkpoint keys and atomic commit members were constrained only as bounded
  unique string arrays. A resealed contract could therefore add `patient_id`,
  replace the practice-bound checkpoint key or remove an atomic member while
  still validating. Existing tests checked canonical subsets and scalar
  widening but did not mutate those lists.
- P2: none.

This contradicted the frozen recursively closed payload-free contract and exact
adversarial-mutation acceptance. Every safety-critical list must be a schema
constant or equivalently closed ordered tuple, with direct substitution,
append, removal and reordering tests.

## Verification and postconditions

- focused durability architecture: 30 passed;
- default-off observation boundary: 13 passed;
- observation-to-signal plan: 4 passed;
- API Spine: 36 passed;
- total: 83 passed;
- before/after HEAD remained
  `92cf76b17bbab276df701ee1e0af0da77e1768a9`;
- branch remained `codex/review-source-specific-durability-92cf76b1`;
- review worktree remained clean;
- local/origin `master` and `handoff/current` remained
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`; and
- no edit, provider, browser, database, source, runtime, deployment, push,
  fetch or ref mutation occurred.

DECISION: revision_required
