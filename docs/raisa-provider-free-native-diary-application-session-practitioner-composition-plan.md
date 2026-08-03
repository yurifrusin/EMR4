# Raisa provider-free native-Diary application-session practitioner composition plan

Date: 2026-08-03

Status: authorised architecture-only tranche (Diary lane step 1)

Parent: `bernie_davida_parallel_seam_pass`

## Outcome sought

Freeze the first bounded Diary lane descendant: an architecture-only,
provider-free, non-executing composition contract that binds the already
accepted application-session practitioner-directory read to the native Diary
surface without changing any runtime. The contract must preserve the current
native Diary bearer-authenticated GraphQL read and its REST fallback
byte-for-byte whenever the composition is off (the default). It is not a new
directory API and is not a general GraphQL migration. It shares only the lower
application-session/product-read authorization bridge with Office consumers.

## Authority

This tranche inherits Yuri's standing authority for bounded logical
descendants of the accepted Bernie/Davida parallel seam, recorded in
`orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.json`
for the `diary_native_consumer` lane. It may author the six owned plan/design/
threat/contract/schema/test artifacts and publish them to the task branch.

It may not edit `AGENTS.md`, `docs/branding/`, application/runtime code,
Diary HTML/JS/CSS, shared auth, models, migrations, routes, `app/main.py`,
API Spine artifacts, manifests, workflows, harness settings, protected
evidence or other agents' files. It may not mount any factory, open a
provider call, run a probabilistic interpretation, pass through an agent
proofreader, reuse the Office one-use terminal reload/logout lifecycle, add a
GraphQL mutation, command tunnel, new REST surface or event actuator, write
product state, deploy, rebuild Pages, move a protected ref or make any runtime
or usability claim.

## Frozen contract

1. The composition binds exactly `Surface.NATIVE_DIARY` and the accepted
   application-session policy identifiers from the shared bridge:
   `practice-practitioner-directory-read.v1`,
   action `practice.practitioner-directory.read`, resource
   `practitioner_directory`. No new policy, action or resource is introduced.
2. The composition binds the existing read to
   `Query.practice.practitioners(activeOnly: true, limit: 200, offset: 0)` and
   only the display-safe shape
   `{id, displayName, roleLabel, active, defaultLocation {id, name}}`.
3. The composition is unmounted and default-off. When off, the current
   native Diary bearer-auth GraphQL read and its existing REST fallback remain
   byte-for-byte unmodified and behaviourally unchanged.
4. Only an authenticated, practice-scoped fresh read is permitted. Session
   artifacts, authority envelopes and raw identifiers are not UI data.
5. The Office terminal session consumption/logout/reload lifecycle stays out of
   the native Diary contract. The native Diary is a long-lived browser surface;
   it is not an Office one-use terminal.
6. Providers, probabilistic interpretation, proofreader gates, writes, real
   identity, Microsoft federation, deployment, production and release remain
   closed.
7. The contract defines fail-closed mismatch, stale/superseded response and
   privacy behaviour, deterministic acceptance cases, residual risks and a safe
   implementation handoff. It makes no runtime or usability claim.
8. The contract conforms to the API Spine: GraphQL remains a scoped read-only
   graph; no mutation, command tunnel, new REST surface or event actuator is
   introduced.

## Deterministic acceptance cases

- The machine-readable composition contract validates against its schema.
- Tests prove the exact `Surface.NATIVE_DIARY` and policy/action/resource
  binding against the shared application-auth runtime constants.
- Tests prove the exact read query, variables and display-safe projection.
- Tests prove the off-path preservation claims against the current
  `docs/diary/diary.js` practitioner read, auth and fallback functions.
- Tests prove forbidden dependency surfaces (Bernie, Davida, probabilistic
  work cell, agent proofreader, Office one-use terminal lifecycle) are absent.
- Tests prove fail-closed mismatch, stale/superseded and privacy behaviour are
  declared, and that no runtime or usability claim is made.
- Tests prove the API Spine stays scoped read-only (no mutation, command
  tunnel, new REST surface or event actuator).
- `git diff --check` passes and `docs/branding/` remains absent from the index.

## Residual risks

- Native-Diary UI wiring, the unmounted provider-free composition runtime and
  the live local browser acceptance remain later lane steps with separate
  authority; this tranche claims none of them.
- Session revocation and stale-session reconciliation in a long-lived browser
  surface are design obligations for a later step, not proven here.
- General application-session GraphQL mounting is not opened; only the exact
  practitioner-directory composition is described.
- Real identity, production and release suitability are not established.

## Implementation handoff

The next bounded lane step is the provider-free unmounted composition contract
plus direct HTTP/PostgreSQL evidence, with no native Diary asset edit and no
`app.main` mounting. Every write, provider, real identity, deployment and
default-on switch remains closed. This tranche produces no runtime or
usability result.
