# Threat-model delta: Ariadne handover and verifier workflow optimization

Date: 2026-08-03

Parent: `docs/ariadne-antigravity-gemini-36-high-verifier-allocation.md`

## Boundary change

No product or data boundary opens. The repository-local orchestration control
plane gains a compact hash-bound acceptance index, native five-source receipt
evidence and deterministic-before-model dispatch enforcement.

| Threat | Control | Failure outcome |
|---|---|---|
| Handover compaction silently drops historical acceptance provenance | Preserve each moved table row exactly and bind the ledger path, labels, row/byte/line counts and SHA-256 in a tested manifest | Compaction test fails; no acceptance or commit |
| A stale or partial context claims successful rehydration | Require the exact five source names plus non-empty evidence for every configured continuation event | Receipt is `revision_required`; dispatch/integration/commit/push is denied |
| Manual post-processing makes the receipt differ from what the harness validated | Emit rehydration fields and evidence in the pure receipt builder from explicit runtime state or typed primary-session prefixes | Missing/ambiguous evidence fails closed; no manual patch is part of the accepted workflow |
| Model review consumes cost or supplies false confidence before basic gates pass | Require exact candidate, authority packet, settings fingerprint, focused tests, static checks and clean worktree before risk-triggered dispatch | No external verifier call |
| Verifier becomes an implementer or self-accepts | Gemini resource lacks implementation capability, uses a fresh read-only worktree and returns exactly one terminal decision | Candidate mutation or invalid envelope is rejected |
| Parallel tests corrupt shared PostgreSQL state | All pytest processes loading repository `conftest.py` remain serial; only independent no-shared-state checks may run in parallel | Execution plan is invalid before dispatch |
| Material architecture or authority choice receives routine reasoning | Sol profile escalates material architecture, security, authority, provider, production and release decisions to Extra High | Pause and replan at the material decision boundary |
| Concurrent user branding assets leak into the tranche | Explicit-path staging, no `git clean`, and cached-path inspection before every commit | Stop on any `docs/branding/` collision |

## Residual gates

The receipt still proves declared repository evidence, not the truth of an
external system. The acceptance ledger is an artifact index only and cannot
override live authority or protected boundaries. Model review remains advisory
to Sol acceptance. Product access, real identity, provider calls, deployment,
protected integration, production and release remain separately closed.
