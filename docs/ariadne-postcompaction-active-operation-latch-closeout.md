# Ariadne post-compaction active-operation latch closeout

Date: 2026-08-13

Timestamp: 2026-08-13T09:31:31+10:00 (Australia/Brisbane)

Source: `ac62a6f65612acb624f14b53ba86b1a9dbf72dab`

Result: `ariadne_postcompaction_active_operation_latch_pass`

## Outcome

The post-compaction continuation failure now has a durable repository control.
Every configured Ariadne continuation receipt must carry one exact validated
active-operation latch. The receipt exposes the operation, status, source,
completed checkpoint, next executable stage, resumption requirement and whether
terminal handback is permitted.

For an `in_progress` operation, the contract requires a next stage and automatic
resumption after compaction, prohibits simultaneous user-attention claims, and
sets `terminal_handback_permitted=false`. An attempted terminal response returns
`revision_required` with `unfinished_authorized_operation`.

The interruption policy now states mechanically that prompt recency alone is
not controlling authority. Side questions and status requests are
`answer_then_resume`; additions are `merge_then_resume`; explicit pause or
redirect requires a latch update before replacement or terminal handback.

## Timestamp convention

Yuri's requested timestamp convention is now machine-readable policy. Every
new tranche plan, threat-model delta, report, formal closeout, Sol acceptance
and Yuri lay/technical summary must place an Australia/Brisbane ISO 8601
timestamp beside its date near the top. Formal closeouts remain primarily under
`docs/*-closeout.md`, paired with Sol acceptance in
`orchestration/agent_inbox/codex/`, machine evidence in
`orchestration/continuity/`, and Yuri's paired summary in
`orchestration/human_inbox/yuri/`.

## Verification

- 39 hostile latch mutations fail closed;
- all ten configured continuation events fail without a latch and pass with a
  valid one;
- side-question, status, addition, pause and redirect decisions are exercised;
- 81 focused latch, receipt, lifecycle and handover tests pass after the only
  mechanical correction;
- the first canonical run found only that `AGENTS.md` had grown to 502 lines
  against its `<500` compactness invariant; the same policy was compressed to
  495 lines and the failed gate passed; and
- the final canonical fast profile passes Ruff, maintained-source compilation
  over 208 files, 193 tests, Diary JavaScript syntax and Git whitespace.

No external worker or model review was selected because this was a small,
serial, fully deterministic workflow-control change.

## Claim boundary and residual risk

This proves repository validation and receipt visibility. It cannot directly
intercept the host application's final-channel operation, so a model could
still ignore the policy. The improvement removes the ambiguity that caused the
incident and makes the wrong terminal decision mechanically inconsistent with
the required continuation receipt.

No product, route, database, provider, credential, IAM, browser, network,
patient/product data, command, deployment, production, release, Pages,
protected-evidence or protected-ref authority opened. `docs/branding/` and all
unrelated untracked files remain preserved.

## Resumption

The durable latch now returns directly to the frozen provider-free read-only
status-confirm route-mounting readiness re-review. Its plan and threat delta
remain separate untracked tranche artifacts until that review's own source
commit. Exact-file inspection and ten-dimension reclassification are next; no
route or database is mounted or executed.
