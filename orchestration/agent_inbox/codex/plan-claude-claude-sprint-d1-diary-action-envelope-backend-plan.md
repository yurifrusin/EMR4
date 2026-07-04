# plan-claude-claude-sprint-d1-diary-action-envelope-backend-plan

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-d1-diary-action-envelope-backend-plan` |
| Status | integrated |
| Created | 2026-07-04 11:41 +1000 |
| Source HEAD | `c6e3304` |

## Plan Summary

Bounded first extraction: a typed diary-domain confirm-action descriptor table that becomes the single source of truth for each confirm route's endpoint path, signed-evidence purpose, and blocked-issue factory, replacing 5 hardcoded endpoint literals and 4 near-identical per-action block factories in appointments.py without changing any G1-G6 behaviour or response shape.

## My Understanding

G1-G6 built five confirm routes (staff-create, bernie-create, update, status, delete) each independently carrying a hardcoded confirm endpoint literal (appointments.py:1073,1424,1960,4095,5046), a per-action signed-evidence purpose constant paired with a per-action signed-payload builder, an identical-shaped block factory pair (_confirm_<action>_block + _block_<action>_confirmation), and the same verify pipeline. A pure diary contract layer already exists (app/services/diary/envelopes.py, capabilities.py) but is NOT wired to the routes; capabilities.py implemented_as strings already drift from the router literals. D1 gives create/update/status/delete confirm one typed diary-domain source of truth for endpoint+purpose+block construction so human and Bernie callers share it. Sprawl reduction, not a pipeline rewrite.

## Intended Surface / Boundary

Backend service + router internals only. New app/services/diary/confirm_actions.py (DiaryConfirmAction enum + frozen descriptor table: endpoint path, evidence purpose, shared blocked-issue/response factory). appointments.py: swap 5 endpoint literals and 4 block-factory pairs to descriptor references, keeping verify-route bodies byte-identical in flow and return shape. Optional: capabilities.py implemented_as points at registry paths. MUST NOT change: diary grid docs/diary, booking slots, appointment cards/stacking, waiting room, status controls, taskpane, Command Centre (no frontend touched), the HMAC signed-evidence algorithm in bernie_turn_evidence.py, the raw compatibility endpoints PUT/PATCH/DELETE, and every response JSON body.

## Out Of Scope

No persisted PHI/session table, no GraphRAG, no auto-mode, no broad root-to-branch API review, no raw endpoint removal, no frontend redesign. Deferred within D1: unifying the five verify-pipeline bodies into one shared function (behavioural risk, natural D2 follow-up), and migrating DiaryActionProposal/Confirmation envelopes to be the actual request/response models.

## Files I Expect To Edit

app/services/diary/confirm_actions.py (new); app/routers/appointments.py (swap literals+block factories to descriptor refs, flow unchanged); app/services/diary/__init__.py (export symbols); app/services/diary/capabilities.py (optional implemented_as alignment); tests/ new focused regression test pinning endpoint paths, evidence purposes, blocked-issue shape, and full-coverage of confirm actions.

## Implementation Steps

1) Add confirm_actions.py: DiaryConfirmAction enum (staff_create,bernie_create,update,status,delete) + frozen descriptor dataclass + DIARY_CONFIRM_ACTIONS table binding each to its EXISTING endpoint string and EXISTING SIGNED_*_CONFIRMATION_EVIDENCE_PURPOSE imported from bernie_turn_evidence, plus shared blocked_issue/blocked_response helpers. 2) Swap the 5 confirm_endpoint literals to descriptor.endpoint. 3) Delegate per-action block factories to the shared factory, keeping thin wrappers so call sites and outputs are unchanged. 4) Point signed-payload verification at descriptor.evidence_purpose (same value). 5) Optional capabilities.py alignment. 6) Export from __init__.py. 7) Add regression test; run verification.

## Visual / Behavioural Acceptance Checks

Backend-internal refactor, no visual surface. Behavioural equivalence: every confirm route returns the same confirm_endpoint string (test pins pre-D1 literals); signed-evidence uses same purpose per action and still fails closed on tamper/stale/wrong-purpose with same block code; blocked confirmations still return safe=False requires_confirmation=True with identical code/message/severity. Verification: py_compile appointments.py + confirm_actions.py; pytest tests -q (appointment proposal/confirm/status/delete/audit); pytest review/test_diary_smoke.py -q; git diff --check.

## Risks / Ambiguities

Silent contract drift is the key hazard - new test must pin exact pre-D1 endpoint literals and purposes. Diff-size vs sprawl tension: keep thin per-action wrappers delegating to shared factory so call sites stay unchanged and diff is reviewable. Generic block-response factory must take the output class + fixed kwargs because Confirm*ProposalOut models differ slightly (e.g. appointment field). New cross-file invariant: capabilities.py implemented_as must agree with router paths - test guards it, step 5 skippable if risky. Ambiguity for Codex: should D1 also fold the five verify pipelines into one shared function? I recommend NO for D1 (behavioural risk) and flagging it as the D2 follow-up once the descriptor table is proven.

## Codex Plan Review

- Review result: Accepted with the planned D1 constraint that verify pipelines remain route-local.
- Required changes before implementation: Keep `app/services/diary/confirm_actions.py` pure; do not import route schemas into the diary domain module.
- Approved to proceed: yes; implemented by Ariadne in the integration worktree.
