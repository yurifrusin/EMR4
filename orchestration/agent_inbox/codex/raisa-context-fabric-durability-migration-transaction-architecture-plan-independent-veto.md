# Durability migration/transaction architecture plan independent veto

Date: 2026-08-06

Candidate: `bea7d7193503c9176acea24395d3b7727f617454`

Decision: `revision_required`

## Rehydration and authority

The fresh native reviewer rehydrated from all five required sources:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. The `emr4-api-steward` boundary was applied read-only.
The candidate and review worktree began at the exact clean HEAD above; local and
origin `master` and `handoff/current` remained exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

## Blocking findings

1. **P1 — the proofread observation handoff is not authenticated.** The plan
   gives the coordinator a caller-supplied proofread decision packet at lines
   237-239 and makes the observer/proofreader solely responsible for its HMAC
   observation/key proof at lines 244-248. The coordinator checks only source-
   row membership. No immutable admitted packet, authenticated observer binding
   or independently verifiable handoff joins those two facts. A compromised or
   confused coordinator caller can therefore pair a real source coordinate with
   invented proofreader effects. The parent keeps the observer and coordinator
   as distinct principals and gives the observer no direct persistence authority
   (`docs/raisa-provider-free-unmounted-source-specific-durability-architecture-plan.md`,
   lines 82-113), so the missing receive/admission boundary cannot be assumed.

2. **P1 — exact redelivery incorrectly depends on retained source.** The
   coordinator algorithm selects the source row before deriving redelivery
   (lines 244-249), while the same plan permits source rows to be retained and
   purged independently of receipts/checkpoints (lines 304-320). A valid exact
   redelivery after safe source purge would be classified as a missing retained
   row and forced to rebase at lines 260-264, contradicting the accepted exact-
   redelivery contract.

3. **P1 — the recovery anchor is not representable.** The one-row generation
   registry is described as holding immutable recovery-anchor coordinates
   (lines 109-113), while the checkpoint advances independently (lines 114-117).
   The accepted restart contract requires an independently trusted anchor equal
   to the current candidate state and last contiguous coordinate. A fixed
   baseline row cannot anchor every later checkpoint, while mutating that row
   would not be immutable or independently lifecycle-owned. The catalogue needs
   append-only lifecycle-owned recovery anchors and an exact checkpoint/anchor
   handshake.

4. **P1 — lifecycle atomicity is stated but not staged.** The catalogue requires
   one gap-free `DECISION`/`KEY_ROTATION` lifecycle journal at lines 134-137,
   but the authoritative coordinator staging list at lines 250-252 omits the
   lifecycle member. A receipt/audit/checkpoint commit can therefore be read as
   valid under the prose while leaving a lifecycle gap.

5. **P1 — key schedule and rotation scope is ambiguous.** The key-interval
   relation at lines 143-147 does not say whether it is stream-global or keyed
   by the full observer-generation coordinate, while lifecycle revisions are
   generation-scoped and routine rotation at lines 294-300 says only that it
   consumes "the generation." A shared schedule would require one atomic update
   across every non-consumed generation; a generation-local schedule would not.
   The plan freezes neither interpretation and therefore cannot produce one
   exact schema or lock protocol.

## API Steward result

No API-plane defect was found. The candidate remains internal asynchronous
durability architecture: GraphQL is read-only and unchanged; REST/OpenAPI is
the unchanged command plane; the existing staff committed-event route is not
observer/checkpoint authority; and there is no new route, mutation,
subscription, acknowledgement, retention endpoint or event-triggered fresh
read.

## Check and process record

The conductor independently passed 67 focused plan, parent state-machine-plan
and source-specific-architecture checks, Ruff and `git diff --check`. The
reviewer's first requested `uv run --frozen` command unexpectedly bootstrapped
an ignored `.venv` in the otherwise clean review worktree and then failed before
collection because `authlib` was absent. This was a read-only-process breach,
not product evidence. The conductor resolved the exact target
`C:\Users\sarashera\EMR4-worktrees\r23\.venv`, previewed an exact ignored-path
cleanup that named only `.venv/`, removed only that owned directory, and
re-established clean HEAD. No user-owned untracked artifact was touched. The
reviewer then used only non-writing inspection and a system-Python/no-conftest
fallback for static checks.

The reviewer was interrupted after its material findings and check record were
delivered because final prose generation did not terminate promptly. That
termination does not weaken the reproduced architectural contradictions above;
the candidate remains rejected and requires a fresh exact-head veto after
repair.

## Exact postflight

- review worktree: `C:\Users\sarashera\EMR4-worktrees\r23`
- branch: `codex/review-durability-migration-transaction-plan-bea7d719`
- HEAD: `bea7d7193503c9176acea24395d3b7727f617454`
- tracked and untracked status after owned cleanup: clean
- local/origin `master` and `handoff/current`:
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`
- provider/model/database/source/runtime calls: zero
- protected-ref movement: zero

`DECISION: revision_required`
