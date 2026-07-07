# claude-sprint152-create-proposal-minlength-readiness

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | a3783d74 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint152-create-proposal-minlength-readiness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint152-create-proposal-minlength-readiness --commit-message "Sprint 152 create-proposal minLength readiness review" --message "claude-sprint152-create-proposal-minlength-readiness ready for Codex review"` |

## Mission

Review whether EMR4 should enforce OpenAPI Idempotency-Key minLength: 8 at runtime for POST /api/v1/appointments/proposals/create now, or keep compatibility mode and preflight the next proposal-only surface.

## Scope

### In Scope

Read AGENTS.md, orchestration/protocol_alerts.md, orchestration/phase_programmes.md, orchestration/sprint_closeout.md, orchestration/api_spine_programme.md, the Sprint 147-151 create-proposal docs/tests, app/routers/appointments.py create-proposal handling, and current clients/tests that call create-proposal. Produce a bounded review/plan packet only; identify required tests/docs if runtime minLength should remain deferred or be enforced.

### Out of Scope

Do not edit production code during planning. Do not wire minLength enforcement, do not alter OpenAPI header shape, do not touch confirmation idempotency ledger semantics, raw compatibility routes, providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, or historical diary trove material.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Run only read-only/static checks needed for the plan if useful; otherwise list exact tests Ariadne should run. Any later implementation must pass focused API spine create-proposal/idempotency tests and leakage lint.

## Merge Criteria

Ariadne can decide Sprint 152 scope from the packet: enforce minLength now with explicit client evidence and regression plan, or record deferred compatibility with guard tests and next proposal-only preflight recommendation.

## Completion Notes

- Files changed: plan/review packet only; no production code, tests, OpenAPI, diary UI, taskpane, or migrations.
- Verification run: read-only/static review by Claude; Ariadne ran the focused Sprint 152 API-spine pytest suite after integration.
- Integration result: accepted. Ariadne followed the defer-with-guard recommendation and added static guard tests plus a Sprint 152 decision artifact.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Plan-gate only. No production code or tests edited. Wrote the
  implementation/review plan packet
  `orchestration/agent_inbox/codex/plan-claude-claude-sprint152-create-proposal-minlength-readiness.md`
  and moved this task packet to `pending_plan_review`. No `app/`, OpenAPI,
  migration, diary UI, or test edits.

- Verification run: Read-only/static review only (plan gate). Reviewed AGENTS.md,
  protocol_alerts.md, api_spine_programme.md, the Sprint 149/150/151 create-proposal
  decision/guard docs, `app/routers/appointments.py` (propose_create_appointment +
  _normalize_create_proposal_idempotency_key, lines 1030-1051), the OpenAPI
  IdempotencyKey parameter (`docs/api-spine/openapi/appointment-commands.yaml:405`,
  minLength 8/maxLength 128, required), the guard/contract tests
  (`tests/test_api_spine_create_proposal_header_alignment.py`,
  `tests/test_api_spine_create_proposal_idempotency_route_contract.py` incl.
  `test_short_nonblank_key_is_accepted_until_minlength_client_readiness_decision`),
  and the real callers. Key evidence: the diary booking modal
  (`docs/diary/diary.js:7392`) POSTs `/appointments/proposals/create` via `apiFetch`
  with NO Idempotency-Key header, and `apiFetch` (`docs/diary/diary.js:2417`) injects
  only Content-Type/ngrok-skip/Authorization; backend test default key `proposal-key`
  (12 chars) already satisfies minLength 8. No pytest was run per the plan-gate rule.

- Recommendation: DEFER runtime OpenAPI minLength 8 enforcement this sprint; keep
  non-blank-only compatibility and keep the existing guard tests locking the split
  posture. Reasons: (A) client-readiness for even the non-blank bar is not met (the
  diary client sends no header); (B) create-proposal is deterministic re-evaluation
  with no ledger/replay, so short keys cause no correctness harm and minLength adds
  negligible safety while adding client-break risk; (C) a raw FastAPI min_length would
  emit 422, inconsistent with the typed 400 idempotency_key_required. Next proposal-only
  preflight should be update/status header discipline, not raw-compat writes. Natural
  trigger to later enforce minLength: once the diary client sends an 8+ char key
  (e.g. reuse generateEventId), which satisfies minLength automatically.

- Remaining risks: (1) Live non-smoke diary booking may already 400 on create-proposal
  because it sends no header at all — a pre-existing client gap for the client-compat
  lane (Antigravity) to confirm; (2) the OpenAPI-vs-runtime split may confuse SDK
  generators, mitigated by the x-emr4-proposal-header-posture annotation + guard test;
  (3) recommendation assumes the route stays deterministic (no proposal marker/ledger);
  (4) no tests were run during the plan gate — Ariadne should run the three test files
  above before acting on either verdict.
