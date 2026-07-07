# review-claude-claude-sprint153-diary-create-proposal-header-readiness

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint153-diary-create-proposal-header-readiness` |
| Status | integrated |

## Review Request

claude-sprint153-diary-create-proposal-header-readiness plan ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Plan-gate only. No production code or tests edited. Wrote the
  implementation/review plan packet
  `orchestration/agent_inbox/codex/plan-claude-claude-sprint153-diary-create-proposal-header-readiness.md`
  and moved this task packet to `pending_plan_review`. No `app/`, OpenAPI,
  migration, diary UI, or test edits.

- Verification run: Read-only/static review only (plan gate). Reviewed AGENTS.md,
  protocol_alerts.md, the Sprint 152 task/decision packet + its completion notes,
  `app/routers/appointments.py` (`propose_create_appointment` +
  `_normalize_create_proposal_idempotency_key`, lines 1030-1051, and
  `propose_update_appointment` at 1503 which takes no Idempotency-Key), the live
  diary caller `docs/diary/diary.js:7389-7395` (create/update proposal POST via
  `apiFetch` with NO Idempotency-Key header), `apiFetch` (diary.js:2417, forwards
  `opts.headers`), and `bernieSession.generateEventId()` (diary.js:174,
  `crypto.randomUUID()` / `evt-...` fallback, both >=8 chars). No pytest run per
  the plan-gate rule.

- Recommendation: PROCEED with a client-only fix. Add an 8+ char Idempotency-Key
  header to the CREATE branch of the diary booking-modal save flow (generated via
  a standalone `crypto.randomUUID` helper, not a hard dependency on bernieSession),
  bump the diary cache-bust, and add a structural check. This closes the Sprint 152
  client-readiness gap (live non-smoke create currently 400s with
  `idempotency_key_required`) while leaving runtime enforcement at non-blank-only,
  OpenAPI unchanged, and no ledger/write/replay authority change. A UUID key also
  satisfies the deferred minLength 8, making a future runtime-enforcement sprint a
  clean follow-on. Suggested tests for Ariadne/implementation: `node --check
  docs/diary/diary.js`; `pytest tests/test_api_spine_create_proposal_header_alignment.py
  tests/test_api_spine_create_proposal_idempotency_route_contract.py -q`;
  `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q`.

- Remaining risks: (1) Prefer a standalone key generator; bernieSession may be
  uninitialised in the plain booking path. (2) Scope the header to the create
  branch so the shared caller does not alter update-proposal (which ignores the
  header). (3) Smoke mode bypasses the endpoint, so header coverage needs a
  structural/static check, not the smoke path. (4) The OpenAPI-vs-runtime
  minLength split is intentionally preserved this sprint. (5) No tests were run
  during the plan gate; Ariadne should run the three commands above before/after
  implementation.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint153-diary-create-proposal-header-readiness.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated. Ariadne accepted the client-only create-proposal header readiness plan.
- Follow-up required: Later sprints should address confirm-route and sibling proposal-route header gaps without expanding Sprint 153.
