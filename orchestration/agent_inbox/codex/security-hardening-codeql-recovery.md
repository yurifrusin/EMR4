# Secure SDLC hardening — CodeQL recovery amendment

Date: 2026-07-17

Superseded reviewed candidate: `4efe9ff3363c3f563a03a1f5bd0978998ca55d07`

Recovered exact candidate: `a248f659545975ada9662e08f89962c87952e77f`

## Trigger and disposition

The representative pull request made the proposed required checks observable.
Python Security, Node Security, JavaScript CodeQL, and the Diary browser suite
passed, but GitHub Advanced Security correctly failed the aggregate CodeQL
check because changed Diary lines produced two high-severity
`js/user-controlled-bypass` alerts and one unused-variable note.

The alerts were not dismissed and enforcement was not weakened. Sol separated
the local mock loader from the authenticated Diary loader so URL state can
select only a mock-only function and cannot participate in an authentication
condition. The authenticated function now checks the token before entering the
shared renderer. The unused local variable was removed. Local `file:` and
localhost smoke remain supported, while live refresh remains token-gated.

## Verification before redispatch

- the directly failing full Diary case passed;
- all 139 Diary Playwright smoke cases passed;
- 45 focused security, Ariadne, confirmation, API-spine, and auth tests passed;
- Node syntax and current-code whitespace checks passed.

The earlier exact-head red and purple passes remain preserved as evidence for
the superseded candidate but do not certify this recovered head. A new fresh
Gemini exact-candidate veto and a new Sol purple synthesis are required before
integration.
