# Reception One practitioner reassignment

Date: 2026-08-14

Timestamp: 2026-08-14T13:38:04+10:00 (Australia/Brisbane)

Status: accepted at candidate `f085fc98ead21a3e7929ee9adbda81abfc7542c9`

## Lay summary

Reception One can now move a selected appointment to another active
practitioner without becoming a separate scheduler. Staff choose a current
active practitioner, pass through the ordinary Diary confirmation, and see the
new practitioner only after the Diary reads current truth again. Date, time,
duration, patient and every unrelated detail remain fixed.

The work caught three important boundaries: duplicate directory identities
must not become choices, a caller cannot substitute a practitioner after fresh
admission, and a practitioner who becomes inactive before confirmation must be
blocked by the backend itself. All three now fail closed.

## Technical summary

- Reception One supplies zero start/duration deltas and delegates once to the
  existing `handleMoveResize` proposal/confirm path.
- The existing backend proposal rechecks a changed target's active status, and
  confirmation re-runs it; no new route, schema or command family was added.
- Twelve paired traces agree between the conventional grid and Reception One
  across six success/failure outcomes and eight current-truth fields.
- Practitioner browser tests pass 20/20; update-proposal tests 42/42;
  consolidated checks 126/126; canonical fast 196/196; Gemini veto 80/80.
- Desktop, tablet and phone remain horizontally contained, and Escape returns
  focus to the practitioner selector.

## Parallel-work lesson

The permanent planning control worked. The native reviewer found high-value
boundary defects. DeepSeek produced useful test breadth but at a poor
non-authoritative estimated economy (about USD 17.55), so that packet should
not be repeated unchanged. Gemini supplied the independent clean-candidate
veto. Sol retained integration, correction and acceptance authority.

## Deliberately closed

No real product/patient data, live product database operation, provider call,
new command, deployment, production, release, Pages or protected-ref movement
is opened. `docs/branding/` and all unrelated untracked files remain preserved.

## Next planned direction

Before adding another full-width field control, perform a provider-free
read-only orientation for a compact selected-action console. The goal is to
preserve the four proven truth/command paths while choosing a progressive-
disclosure or intent-led interaction that fits the minimum-app/maximum-
intelligence direction.

Yuri attention required: no.
