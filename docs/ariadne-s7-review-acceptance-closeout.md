# Ariadne S7 Review Acceptance Closeout

Date: 2026-07-13
Status: complete; publication pending closeout commit

S7 repaired the cross-boundary contract gaps exposed by S6 and added one thin,
executable acceptance decision for independent worker reviews. The gate does
not replace Sol's integration authority. It prevents Sol from accepting a
review unless the durable artifact, PTY receipt, Git state, and deterministic
test evidence all describe the same candidate.

## Integrated Contract

- The Deep Code resource settings and tests now include the approved
  `deepseek-pro-conductor-fallback` while preserving both security quirks:
  permission prompts are not authority, and no worker has integration
  authority.
- `orchestration_harness/review_acceptance.py` validates the expected worktree,
  branch, candidate ancestry, canonical decision/completion markers, receipt
  shape, artifact identity/kind, process cleanup, review mode, and
  authoritative pytest collection count.
- `scripts/ariadne_review_acceptance.py` exposes the decision as a
  standard-library CLI with `accepted`, `rejected`, and input/internal-error
  exit states. It reads evidence files and does not execute worker-supplied
  commands.
- Scratch output cannot substitute for the declared artifact or receipt.
- Multi-file pytest collection is aggregated by unique file path. Conflicting
  duplicate counts, summary/per-file disagreement, missing counts, and zero
  counts fail closed.

## Agent Evidence

- Claude Fable and Opus were subscription-limited at the S7 boundary, so
  DeepSeek 4 Pro/high served as Conductor through Deep Code.
- Sol used one permitted direction rejoinder to require an executable gate
  instead of a test-only audit. DeepSeek Pro accepted the amendment and retained
  final sprint/allocation authority.
- DeepSeek Flash Lane 1 implemented the candidate and completed three
  substantive revisions. Each revision returned to the same worker rather than
  being silently repaired by Sol.
- DeepSeek Flash Lane 2 independently reviewed the final candidate in a clean,
  candidate-containing worktree and returned `DECISION: pass`.
- The first real gate run rejected the initial candidate because its collection
  parser could not aggregate multiple files. The worker fixed that defect and a
  fresh independent review accepted the amended candidate.

## Verification

- Focused candidate suite: 88 passed.
- Adjacent Deep Code PTY/mailbox suite: 22 passed.
- Broad Ariadne closeout suite: 121 passed.
- Direct acceptance CLI help: passed.
- Python compilation and whitespace checks: passed before closeout edits.
- The persisted real acceptance decision is
  `orchestration/harness_evidence/s7-review-v2-acceptance.json`.

No S7 work opens application runtime, provider, database, deployment,
production, external-client, H15/H-series, historical diary, memory/RAG,
GraphRAG, schema, or product-policy gates. Cost and wall-clock task caps remain
inactive; real provider availability still drives the configured Conductor
fallback chain.

Sprint engine state: continuing automatically to the next Conductor planning
boundary. No user decision is required.
