# review-claude-claude-sprint152-create-proposal-minlength-readiness

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint152-create-proposal-minlength-readiness` |
| Status | integrated |

## Review Request

claude-sprint152-create-proposal-minlength-readiness ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint152-create-proposal-minlength-readiness.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated. Ariadne accepted Claude's defer-with-guard recommendation.
- Follow-up required: Sprint 153 should close the real proposal-header readiness gap before strict length enforcement.
