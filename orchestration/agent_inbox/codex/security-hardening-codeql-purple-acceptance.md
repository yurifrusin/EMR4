# Secure SDLC hardening — CodeQL recovery purple acceptance

Date: 2026-07-17

Candidate: `a248f659545975ada9662e08f89962c87952e77f`

DECISION: pass

## Decision

The CodeQL-driven recovery candidate is accepted for representative CI. It
replaces the superseded exact code candidate `4efe9ff3363c3f563a03a1f5bd0978998ca55d07`.
The earlier final red and purple passes remain provenance for that older head
only and were not carried forward as acceptance evidence.

GitHub Advanced Security identified two high-severity
`js/user-controlled-bypass` results in changed Diary lines and one unused
variable. Sol did not dismiss the alerts or weaken the check. The repair
separates local mock loading from authenticated loading: URL state can invoke
only `loadSmokeDiary`, which is constrained to the local harness and supplies
a literal mock-data mode; `loadAuthenticatedDiary` independently requires the
token before live rendering. Startup now chooses the smoke loader first for
local QA and otherwise starts refresh only through the authenticated loader.
The unused variable is removed.

## Independent and Sol evidence

A fresh Gemini project, prohibited from reading the earlier review outcomes,
returned `DECISION: pass` on the exact candidate. It reproduced 45 focused
tests, all 139 Diary Playwright cases, Node syntax, and the scoped whitespace
gate. Its reachability analysis found no URL-to-live-loader path without a
token and no regression in local smoke, authenticated refresh, practitioner
directory, confirmation allowlisting, secure randomness, or selector safety.

Sol independently reproduced the directly failing browser case, all 139 Diary
Playwright cases, the 45 focused security/Ariadne/API/auth cases, Node syntax,
and current-code whitespace checks. The Ariadne plan gate passes with dual
review and purple review required.

## Remaining integration gate

The pull request must now reproduce the Python and JavaScript CodeQL jobs,
Python Security, Node Security, Diary smoke, and the GitHub Advanced Security
aggregate alert gate. Any surviving critical/high result blocks integration
and master protection. No alert dismissal is authorized by this acceptance.

No protected holdout, T3/provider, historical-data, runtime/product, database,
deployment, release, or new write-authority surface was opened.
