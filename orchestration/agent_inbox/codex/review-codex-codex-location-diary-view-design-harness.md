# review-codex-codex-location-diary-view-design-harness

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/location-diary-view-design-harness` |
| Source Task | `codex-location-diary-view-design-harness` |
| Status | queued |

## Review Request

Location/diary view design harness ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/location_diary_view_review.md` added;
  `orchestration/sprint_closeout.md` updated with a Sprint 16 harness pointer;
  `implementation_plan.md` updated with the Sprint 16 location review harness
  guardrail; `orchestration/agent_inbox/codex/plan-codex-codex-location-diary-view-design-harness.md`
  captured the approved plan; source task packet updated with completion notes.
- Verification run: `git diff --check` passed.
- Remaining risks: API spot-check snippets are review aids only because final
  route and payload names depend on the submitted backend/UI branches. The
  harness deliberately avoids production code and does not prove runtime
  location scoping by itself.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-location-diary-view-design-harness.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
