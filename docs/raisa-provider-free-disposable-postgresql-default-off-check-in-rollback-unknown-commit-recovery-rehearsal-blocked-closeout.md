# Check-in rollback and unknown-response rehearsal blocked closeout

Date: 2026-08-19

Timestamp: 2026-08-19T18:08:13.2461050+10:00 (Australia/Brisbane)

Status: **blocked — not accepted**

## Result

The explicit rollback half of the fixed authored-synthetic disposable
PostgreSQL rehearsal passed in all three authorised executions: each staged
the receipt/effect/audit packet, rolled back and observed exact zero state.

The lost-complete-response half did not reach its authoritative readback
classifier. Each execution observed the exact post-commit
`Timeout/PgSleep` state and terminated only that exact backend, but the local
caller transport never returned one closed worker outcome. No complete
success was released, no command was automatically reissued and no fourth
execution is authorised.

This tranche therefore does not close the readiness review's
`atomic_effect_rollback_and_unknown_commit_recovery` operational-evidence
gap. It is negative transport evidence, not a product or database acceptance.

## Immutable attempts

| Attempt | Terminal coordinate | SHA-256 | Cleanup |
|---|---|---|---|
| 001 | `ambiguous_response/worker_join_timeout` | `e357e3a2dec7f0d0740a2ea6f518cb695dc2a5cbf88b9c321dbcd61d6e7bd1c1` | role absent before teardown; relay stopped; container/network absent |
| 002 | `ambiguous_response/worker_outcome_missing` | `bea605006bf36996d439876a4976ec5b733ddc4bb841d5942aae1057c5f514ed` | role absent before teardown; relay stopped; container/network absent |
| 003 | `ambiguous_response/worker_outcome_missing` | `15cebad64c7bfbddb83878e75cf8f3a0d137a7834075e063c92aead8b603e219` | role absent before teardown; relay stopped; container/network absent |

No matching labelled container or network remained after the final attempt.
The generic latest-failure projection equals attempt 003.

Attempt 002 initially exposed that the generic failure writer had overwritten
attempt 001. The original closed bytes were restored and verified against the
full originally observed SHA-256, and the writer now allocates an immutable
numbered path before updating the convenience projection. Because the tranche
is not accepted, this corrected evidence conflict and the temporary direct
latch-checkpoint edits remain explicitly disclosed here for registration if a
future recovery is admitted; neither was erased or converted into acceptance.

## Clockwork terminal correction

Read-only inspection found that the live clockwork supported only successful
closeout plus an in-progress successor. It could not represent exhausted
bounded recovery without falsely advancing Continuity/Compass or requiring a
manual canonical latch edit.

Candidate `2e814b2c3f8b687adb499d6f61a64d316dc016df` adds one closed
`blocked_transition` intent and reducer. The pointer-last publication passed
once at generation
`gen-6f758043be53b4ce1d14e9e9fab01649c0aa2d91fb90ac649f9db314c216b811`,
lease sequence 5, with zero caller-authored derived fields, zero bespoke
updater executions, ten clockwork-owned surfaces and zero dual-owned surfaces.

The active latch is now `blocked`, requires Yuri's attention, permits terminal
handback and has no next executable stage. Continuity remains 334 and Compass
316. Continuity, Compass JSON/Markdown, Current Baton, error register and
pattern report are byte-identical to candidate source; only the latch and
clockwork metadata/pointer changed. The earlier temporary hand-edited latch
checkpoints were restored to the exact full-Git source before publication, so
no manual canonical drift remains.

## Verification

- 117 focused clockwork, latch, orchestrator, rehearsal, plan and Current
  Baton tests passed with one expected live-evidence skip.
- The new blocked path proved one pre-pointer injected failure restores all
  canonical surfaces, metadata and pointer; successful publication is
  idempotent; rollback restores canonical/metadata bytes with a monotonic
  lease.
- Ruff, compilation, JSON parsing and `git diff --check` passed.
- The first final blocked-state suite exposed two Current Baton assertions that
  treated every selected clockwork transaction as an accepted graph node. The
  compatibility test now branches on `event_kind`: clean closeouts retain the
  old accepted-node binding, while blocked transitions bind the terminal latch
  and require the accepted graph/Baton to remain unchanged.
- The earlier full static and material surrounding suites passed with only the
  plan-recorded historical mutable-current exclusions; the unrelated
  `AGENTS.md` 504-versus-less-than-500 archive-line baseline remains unchanged.
- No Gemini call occurred because deterministic database acceptance failed
  before external-veto eligibility.

## Closed boundaries

No feature flag, authored-synthetic allowlist, product/config/API/OpenAPI/
GraphQL/client/schema, ordinary-practice posture, generic-status `Arrived`,
action grammar, waiting-area behavior, product/patient/appointment/clinical or
protected data, occupied DeepSeek HMR, production runtime, deployment,
release, Pages or protected ref changed. Local/origin `master` and
`handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. `docs/branding/` and all unrelated
untracked files remain preserved.

## User-attention fork

Yuri must choose between materially different outcomes:

1. authorise a newly frozen transport redesign that removes this host relay
   from the evidence path before any new disposable execution; or
2. defer the rollback/unknown-response operational-evidence gap and leave
   ordinary check-in admission not ready.

The current plan grants neither a fourth execution nor an inferred successor.
