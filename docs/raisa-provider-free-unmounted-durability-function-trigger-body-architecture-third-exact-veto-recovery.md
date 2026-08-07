# Durability function-and-trigger-body third exact-veto recovery

Date: 2026-08-07

Status: corrected replacement candidate built; deterministic and independent
acceptance pending

Rejected candidate source HEAD:
`5a3c5b5118f80153d545bf30ae9db99acb187cd7`

Independent veto:
`orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-r6-independent-veto.md`

Rejected candidate contract:
`sha256:78db131b6da9482e7092a3530d747030010cf027c582f54f49b959827f4bff8a`

Immutable parent contract:
`sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8`

## Recovery classification

The fifth candidate remains rejected even though its exact deterministic packet
passed 192/192. Fresh exact-HEAD review found two P1 semantic gaps and one P2
structural-schema gap. Sol's already frozen recovery lease is invoked again.
The rejected candidate is evidence only and cannot be accepted or used to
weaken the surviving requirements of the earlier recoveries.

This recovery changes neither the accepted migration/transaction parent nor
the API Spine, provider, data, runtime, command, deployment or claim boundary.
It closes only the three exact surfaces below.

## R6A — branch-local coordinator reads and source-independent replay

`apply_durability_transition_v1` may load common binding, barrier, generation,
checkpoint, retained admission and receipt evidence before it chooses a route.
It must not load source or branch-dependent frame, watermark, obligation or
anchor evidence unconditionally.

- A retained CONFLICT route loads only the evidence required by the already
  frozen rebase branch.
- `RECEIPT_REPLAYED` locks, reloads, rederives and compares its exact receipt,
  PRIMARY, zero-CONFLICT, generation and checkpoint evidence without reading
  the source outbox or unrelated dependent relations.
- `TERMINAL_REPLAYED` uses only its terminal generation, checkpoint, lifecycle
  and result-integrity evidence. It reads neither source nor another branch's
  dependent rows.
- Only the active no-receipt/no-conflict route may load the exact source row and
  the dependent anchor, frame, watermark and obligation evidence required for
  apply or rebase.
- Path-sensitive effects, not merely top-level body summaries, are normative.
  Hostile hoisting or unconditional selection of the source or branch-dependent
  relations must fail after candidate digests are resealed.

## R6B — independently derived complete recovery anchors

`append_recovery_anchor_v1` is not a copier for generation/checkpoint fields.
For every requested revision greater than zero it must independently load and
prove the exact committed lifecycle packet before inserting or replaying an
anchor. Revision zero remains registration-owned: registration creates and
compares the complete baseline anchor, while this entry point rejects a
revision-zero request with `F_ANCHOR`.

All non-zero paths must prove one exact lifecycle row at the requested current
checkpoint revision, coordinate equality, generation/checkpoint consistency,
the seven controlling generation digests, and lifecycle/checkpoint integrity.
Missing, duplicate, wrong-kind or mismatched evidence fails `F_ANCHOR`.

For a `DECISION` lifecycle row:

- load the exact durability-audit row at that revision;
- prove `source_position` is present and positive and both key-interval fields
  are absent;
- independently prove `prior_audit_digest` names the latest earlier audit head,
  with no intervening audit revision, or the revision-zero registration
  baseline anchor when no earlier audit exists;
- for a rebase decision, prove zero classified receipt rows, independently
  recompute `checkpoint_rebase_digest_v1` from the exact locator, lifecycle
  source position and revision, and compare lifecycle, audit and checkpoint
  integrity/state evidence;
- for any receipt-bearing decision, prove exactly one classified receipt and
  exactly one matching retained PRIMARY with zero CONFLICT entries, rederive
  `classified_receipt_digest_v1`, independently recompute
  `checkpoint_apply_digest_v1`, and compare receipt, audit, lifecycle and
  checkpoint fields and digests, including contiguous position and observation
  digest.

For a `KEY_ROTATION` lifecycle row:

- prove zero durability-audit and classified-receipt rows at that revision;
- prove lifecycle `source_position` is absent, both key-interval fields are
  present with end strictly greater than start, and the producer body writes exactly that parent-bound
  NULL branch shape;
- load the exact key interval named by the lifecycle row and the immediately
  preceding immutable anchor;
- independently recompute `key_rotation_digest_v1` from the exact locator, key
  interval, key identifier, availability attestation, previous anchor digest
  and requested revision;
- compare that digest with lifecycle, generation key-schedule and checkpoint
  integrity evidence; prove checkpoint position and observation digest remain
  equal to the immediately preceding anchor rather than comparing them with the
  necessarily NULL lifecycle source position;
- independently prove the checkpoint audit head is the latest earlier audit
  head, or the registration baseline anchor when no audit exists, so an
  intervening rotation cannot rewrite or roll back the audit chain.

For every non-zero lifecycle kind, prove checkpoint `updated_at` equals the
committed lifecycle timestamp. This closes the final checkpoint field without
making time a caller input.

Only after the applicable branch has derived one trusted committed integrity
digest may the body derive `recovery_anchor_digest_v1` from the complete
verified state. Exact replay compares every stored anchor field, not only its
digest. It never repairs partial state or advances a checkpoint.

Focused acceptance must reject omitted lifecycle, audit, receipt, PRIMARY,
conflict, key, previous-anchor, baseline-anchor or latest-audit evidence; copied
rather than rederived controlling digests; a non-NULL rotation source position;
wrong branch/cardinality; revision-zero append; checkpoint timestamp mismatch;
audit rollback across a rotation; and replay field substitution after resealing.

## R6C — structurally duplicate-free set key pairs

The exact structural-schema branches for both `SET_CONTAINS_KEY.key_pairs` and
`SET_COVERS_KEYS.key_pairs` must carry `uniqueItems: true` in addition to their
existing non-empty tuple shape. A duplicate otherwise-valid pair must fail
Draft 2020-12 structural validation even if semantic validation is not run.

## R6D — single-anchor path-local lock order

The first integrated R6 worktree state was rejected before commit because its
coordinator acquired and then reacquired the current anchor around an existing
admission lock. Every primary or conflict path now locks exactly one current
anchor at ordinal four, then its admission row at ordinal five, and passes the
held anchor symbol into descendant rebase branches. Admission-missing rebase
paths take exactly one branch-local anchor lock. Receipt replay and
already-terminal replay remain anchor-free and source-independent.

The path-sensitive validator now rejects duplicate, non-contiguous or
out-of-order lock ordinals before generation. Focused tests additionally assert
the exact primary/conflict ordinals and hostile branch-local read hoisting.

The corrected generated candidate is
`sha256:c8d27c85def134056598be7ef12cda3ae7b509b3d06b16a536459baea51bc24b`.
That digest is candidate evidence only until the full packet and a fresh
exact-HEAD independent veto pass.

## Lane allocation

- **Anchor challenger:** read-only analysis of R6B branch completeness and
  digest provenance; no repository edits.
- **Entry-program lane:** R6A/R6B implementation and focused hostile tests in
  the shared entry-program surface.
- **Schema lane:** R6C schema implementation and focused resealed structural
  test.
- **Sol:** reconcile the challenger, integrate shared vocabulary, rebuild the
  generated contract/schema, verify effects and hashes, run the complete packet
  and commission a new candidate-independent exact-HEAD veto.

Repository pytest remains serial. Worker lanes may not run Git, pytest,
generation or external tools unless their later packet expressly says so.

## Acceptance and unchanged boundary

The replacement must pass every preceding plan/recovery test plus focused
R6A-R6D hostile proofs, the AER packet, scoped API Spine checks, Ruff, builder
`--check`, `git diff --check`, explicit-path worktree guards and a fresh clean
exact-HEAD independent veto. Candidate
`5a3c5b5118f80153d545bf30ae9db99acb187cd7` cannot become accepted source.

This remains pure, provider-free, unmounted and repository-local. It renders or
executes no SQL/DDL; creates no migration, database object or operational state;
opens no source/feed/watcher/listener, product/patient read, provider, command,
runtime, deployment, production, release, Pages or protected-ref authority.
