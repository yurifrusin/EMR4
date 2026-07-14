# LC4 protected-master integration manifest

Date: 2026-07-14
Integrator: GPT Sol
Staging branch: `codex/lc4-staging`
Protected targets: `master`, `handoff/current`, `origin/master`,
`origin/handoff/current`

## Authorized result

Integrate the complete LC4 Scale and Protected Holdout tranche from the staging
head after final documentation and deterministic verification. The starting
protected baton was `d085a234a883eb8da7e03ec25be3748ae3d0387b`.

The authorized history includes:

- the LC4 tranche contract;
- three accepted DW1 development-corpus commits;
- DW2 implementation, bounded correction, evidence artifacts, and Sol
  capability/schema amendment;
- two Antigravity review packets plus the transparent independent veto record;
- the Sol-only holdout harness;
- the immutable `lc4-holdout-v1` fixture, consumed seal receipt, and
  aggregate-only report; and
- LC4 closeout, plan/T3 status, and handover updates.

## Boundaries confirmed

- no provider SDK/adapter, live prompt, external call, or T3.5 implementation;
- no route, GraphQL/OpenAPI, database, migration, UI, runtime, deployment, or
  write/confirmation-authority change;
- no historical-diary/H-series/H15, memory, RAG, or GraphRAG access;
- no external dataset or sensitive data;
- development remains Silver/pending and cannot reduce Gold gaps;
- holdout v1 is Sol-authored Gold/adjudicated, aggregate-only, and consumed
  once; and
- T3.1-T3.4 and both blocked gates remain intact.

## Verification authority

The final serial gate collected 682 tests and completed with 681 passes and one
expected xfail across T1, T2, LC1-LC4, and T3.1-T3.4. The LC4-focused gate
completed 183 passes. These commands also pass:

```text
python scripts/bernie_lc4_development_report.py --check
python scripts/bernie_lc4_scaled_evaluation.py --check
python scripts/bernie_lc4_holdout.py --check
python scripts/bernie_shadow_live_gate_check.py
git diff --check
```

The holdout check validates committed hashes and aggregate structure without
re-evaluating labels. The shadow gate remains blocked.

## Integration procedure

1. Commit this manifest and all final documentation on `codex/lc4-staging`.
2. Obtain a fresh passed Ariadne receipt for integration/commit/push.
3. Verify the protected master worktree is clean and still at the starting
   baton.
4. Fast-forward `master` to the accepted staging head.
5. Force-update local `handoff/current` to that same head only after the
   fast-forward succeeds.
6. Push `master:master` and `master:handoff/current` atomically where supported.
7. Fetch and read back all local and remote refs; all four must match.

No worker, reviewer, receipt, or manifest has integration authority. GPT Sol
retains the protected operation.
