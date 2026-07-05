# review-antigravity-antigravity-sprint-r17-expired-session-ux-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-r17-expired-session-ux-review` |
| Status | integrated |

## Review Request

Sprint R17 expired-session UX review packet.

## Worker Completion Notes

- Files changed: `docs/receptionist_review_r17.md`.
- Verification run: inspected token validation, backend `401` mapping, and background refresh behaviour in `docs/diary/diary.js`; drafted copy, selector, risk, and acceptance guidance.
- Remaining risks: visual blink on fast auth handshakes, stale grid visibility after background `401`, repeated backend polling after auth loss, and generic offline/network errors being distinct from verified auth failure.

## Codex Integration Notes

- Integrated the central recommendations into the Diary surface with a visible `[data-testid="diary-auth-banner"]`, grid hiding, token clearing, generic-error suppression after `401`, and refresh timer stop on auth loss.
- Preserved a concise receptionist review artifact in `docs/receptionist_review_r17.md`.
- Deferred richer copy variants/offline-network handling as future work.
