# Secure SDLC hardening — CodeQL bootstrap recovery

Date: 2026-07-17

Superseded candidate: `a248f659545975ada9662e08f89962c87952e77f`

Recovered candidate: `73eba9c144ac1a41be5b2e150b9d2c1c7c77675c`

GitHub's second representative scan showed that loader separation was correct
but that two top-level URL-dependent bootstrap conditions still matched
`js/user-controlled-bypass`. Sol retained the blocking alerts and removed the
conditions instead of suppressing them. Bootstrap now invokes the Diary
dispatcher, refresh scheduler, and review initializer unconditionally. The
dispatcher alone selects the mock-only local path or the independently
token-gated authenticated path; unauthenticated live loading still returns
before the shared renderer.

Before representative repush, 45 focused tests, all 139 Diary Playwright
cases, Node syntax, and current-code whitespace checks passed. The exact
candidate remains pending until the GitHub alert gate passes, followed by a
fresh exact-head Gemini veto and replacement purple acceptance.
