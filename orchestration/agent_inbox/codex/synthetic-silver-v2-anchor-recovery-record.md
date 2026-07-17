# Synthetic Silver V2 Anchor Worker Rejection and Sol Recovery Record

Date: 2026-07-17

## Worker disposition

DeepSeek V4 Flash/high returned `candidate_ready` through Claude Code `--bare`
and reported 45/45 focused tests. Its output was left uncommitted despite the
packet's explicit commit requirement. Sol preserved the exact untrusted output
as worker-branch commit `47eb5f2551e345c4e925410559edb450077df4c1` and adopted
that source on the integration branch as untrusted recovery input at
`49dfb7d7`.

The worker's attestation remains unchanged in
`orchestration/agent_inbox/claude/synthetic-silver-v2-anchor-worker.md`. It is
not accepted as implementation evidence.

## Conceptual rejection

Sol rejected the candidate without a same-lane correction loop because its
green tests did not enforce the frozen taxonomy:

- clarification cell variant 1 frequently retained exact patient semantics;
- clarification cell variant 2 frequently retained exact practitioner
  semantics;
- schedule-clarification anchors sometimes had no ambiguous entity at all;
- correction anchors required only tools and an outcome, not a named replaced
  value, replacement cue, or final corrected value;
- ellipsis, anaphora, repetition, and restart contracts did not freeze their
  promised local-recovery evidence;
- source bindings were checked for presence but not against the ordinary
  development source hash or action;
- the validator did not reconstruct and compare the complete expected semantic
  and dialogue-form contracts; and
- appointment and audit delta dictionaries were newly invented rather than
  preserving coherent action-specific shapes from a bound development source.

These are category-meaning and provenance defects. Under the Ariadne recovery
lease and Flash complexity rule they move directly to Sol recovery.

## Sol amendments

Sol owns every amendment after `49dfb7d7`:

1. select only action-matching, exact-entity, successful, internally coherent
   ordinary-development scenarios as provenance bases, independently of their
   old dialogue form;
2. preserve the exact source outcome/tool/delta shapes for successful mutation
   anchors and use the surfaced read-only `find_slots` tool for schedule reads;
3. freeze patient ambiguity for non-schedule clarification variant 1,
   practitioner ambiguity for variant 2, and practitioner ambiguity for both
   schedule-read clarification variants;
4. freeze explicit practitioner replacement metadata and corrected semantics
   for every correction anchor;
5. freeze form-specific surface requirements for reversal, ellipsis, anaphora,
   repetition, and restart;
6. derive required evidence keys from the v2 meaning rather than old source
   spans;
7. validate exact ordinary-development source ID/hash/action bindings;
8. reconstruct and compare each complete semantic and dialogue-form contract
   in the fail-closed validator;
9. remove the redundant nested seed-hash field and require exact fixture
   regeneration; and
10. repair the CLI's repository-root import bootstrap so its documented direct
    invocation works from a clean shell.

## Recovery evidence

The recovered candidate must receive deterministic regeneration, mutation
rejection tests, source-binding verification, active preservation, and a fresh
independent exact-source review before acceptance. Exact hashes and final test
counts are recorded in the later v2 anchor acceptance/closeout, not in the
rejected worker attestation.

WORKER_DECISION: rejected_conceptual
RECOVERY_OWNER: GPT Sol
SAME_LANE_CORRECTION: false
PROTECTED_ACCESS: false
