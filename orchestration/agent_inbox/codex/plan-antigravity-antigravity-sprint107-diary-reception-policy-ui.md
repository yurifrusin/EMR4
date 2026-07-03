# plan-antigravity-antigravity-sprint107-diary-reception-policy-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint107-diary-reception-policy-ui` |
| Status | pending_plan_review |
| Created | 2026-07-03 14:03 +1000 |
| Source HEAD | `7eacce9` |

## Plan Summary

Plan Diary UI lane to consume reception_policy and reception_context

## My Understanding

The goal is to consume the backend reception_policy in the Diary Bernie review panel to prevent rendering incorrect or contradictory messages. We want to distinguish true slot-search failures ('No matching times found') from roster unavailability ('Roster/schedule unavailable') or other states. We must also ensure that advisory warnings like existing_future_follow_up do not block candidate slot display, and that stale/older response fallbacks remain safe and stable.

## Intended Surface / Boundary

We are modifying the Diary Bernie review panel, specifically how it renders status, headlines, and actions in docs/diary/diary.js. This affects the review panel content section and elements like statusBadge and headline. Adjacent components like the diary grid, booking modal, and instruction input must remain unaffected.

## Out Of Scope

Backend API/schema changes, database migrations, broad state-machine rewrite, persisted sessions, limited Bernie auto-mode, patient-specific copy branches, and changing booking/confirmation behavior.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.css, review/test_diary_smoke.py

## Implementation Steps

1. Update bernieReviewTransition in docs/diary/diary.js to parse payload.reception_policy. 2. Set canShowNoSlots based on policy.search_ran_no_candidates === true, fallback to legacy rules if policy is absent. 3. Set canShowCandidates to policy.can_offer_candidates === true && candidateSlots.length > 0, fallback to legacy rules if policy is absent. 4. Map state to roster_unavailable when policy.availability === 'roster_unavailable'. 5. Update bernieStatusCopyForPayload and bernieHeadlineCopyForPayload to return 'Roster/schedule unavailable' when state is 'roster_unavailable'. 6. Update bernieReviewActionCopy to return 'I could not find a bookable session for that request...' when state is 'roster_unavailable'. 7. In candidate slots rendering block, handle empty slots for roster_unavailable state by showing 'There is no bookable session configured for that request.' 8. In docs/diary/diary.css, add style class .bernie-status-badge.roster_unavailable styled as a neutral grey badge. 9. Write Playwright smoke tests in review/test_diary_smoke.py to assert correct rendering of: search_ran_no_candidates (showing 'No matching times found'), roster_unavailable (showing 'Roster/schedule unavailable' and the session search message), advisory warnings (proving candidates list is still rendered and not blocked by the warning), stale/older fallback payloads (proving backward-compatibility and stale-turn protection)

## Visual / Behavioural Acceptance Checks

- Running pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q passes without errors. - node --check docs/diary/diary.js runs cleanly. - The UI correctly displays 'Roster/schedule unavailable' status and headline, and does not show 'No matching times found' unless reception_policy.search_ran_no_candidates is true. - Candidates list renders successfully when advisory warning existing_future_follow_up is present in the response.

## Risks / Ambiguities

Ensuring legacy payloads (which lack reception_policy) fall back gracefully without JavaScript runtime exceptions. This is mitigated by defensive checks (e.g. const policy = payload.reception_policy) and using existing logic when policy is falsy.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
