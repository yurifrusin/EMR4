# Sprint R17 Receptionist Review - Expired-Session Diary UX

Antigravity/Gemini reviewed the Diary authentication-expiry surface for Sprint
R17. The goal is to avoid a blank or ambiguous Diary when the Office taskpane
has not supplied a token, the local token has expired, or the backend rejects a
request with `401 Unauthorized`.

## Recommended Staff Experience

- Show a visible, staff-facing banner in the Diary body, not only the small
  header status text.
- Use calm, actionable copy: `Session expired`, `Please sign in again before
  using the diary.`, and `Close and reopen the taskpane to refresh your EMR4
  session.`
- Hide the grid while the banner is visible so stale appointment availability
  is not accidentally read as current.
- Clear the expired or rejected token from `localStorage`.
- Stop background refresh polling while unauthenticated so the frontend does
  not repeatedly hit backend routes with known-invalid credentials.
- Keep smoke mode unaffected so deterministic UI review can still run without
  auth.

## Risks Captured

- A background `401` could otherwise leave stale appointments visible.
- A lost token could otherwise leave only tiny header text while the grid area
  looks empty or still loading.
- Repeated polling after auth expiry can create noisy backend logs and wasted
  requests.
- Generic network failures should remain distinct from verified auth failures;
  Sprint R17 only handles missing/expired token and explicit `401`.

## Acceptance Checks

- Loading `diary.html` without smoke mode and without a token shows
  `[data-testid="diary-auth-banner"]` and hides `#diary-grid-container`.
- Loading with an expired local JWT shows the same banner and clears
  `emr4_token`.
- A backend `401` on any API request shows the same banner, clears `emr4_token`,
  suppresses generic diary errors, and hides the grid.
- Re-auth via `DialogParentMessageReceived` with a valid token hides the banner
  and resumes normal diary loading/refresh behaviour.
