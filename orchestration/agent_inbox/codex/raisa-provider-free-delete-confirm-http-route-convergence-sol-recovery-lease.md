# Sol recovery lease — provider-free delete-confirm HTTP route convergence

Date: 2026-08-17

Timestamp: 2026-08-17T05:43:34.1924091+10:00 (Australia/Brisbane)

Status: active

Frozen plan source: `f78524b41c909c74acc93b2818be8fc871ed8fd3`

Initial worker result commit: `abdbcd5f28d39d21084bbc86b22f7201217226b0`

Initial worker receipt commit: `45311f8c238d935716574abae96d9715a070782d`

## Reason for recovery

Sol rejected the worker's self-reported completed candidate before admission.
The delete-confirm OpenAPI success response still referenced the generic
appointment envelope, and the nested Pydantic receipt admitted unknown fields
and a non-null waiting-area value. These are mechanical schema omissions, so
the frozen plan permitted one bounded same-lane correction.

That sole correction transport ended with exit code 1 and produced no terminal
correction receipt or commit. Exact readback found HEAD unchanged at
`45311f8c238d935716574abae96d9715a070782d` and uncommitted partial edits only
in `app/schemas/appointments.py` and
`docs/api-spine/openapi/appointment-commands.yaml`. Those edits remain
untrusted in the preserved worker worktree. No further DeepSeek correction is
permitted under the Flash correction-loop rule.

## Source adoption boundary

Sol may cherry-pick the two preserved initial worker commits only as an
untrusted candidate. The worker's closeout remains under the worker's identity
and is not rewritten or accepted. The failed partial correction is evidence,
not transferable implementation provenance. Sol will independently compare it
with the frozen contract and either reimplement or explicitly adopt each
mechanical idea under Sol identity.

## Sol-owned amendments

The recovered candidate must add and verify all of the following without
editing the accepted adapter, composition or physical seam:

1. replace the generic delete-confirm OpenAPI success reference with one
   dedicated minimal result-envelope component;
2. make the nested Pydantic delete receipt `extra="forbid"` and require
   `waiting_area_id` to be exactly null;
3. restrict reason and warning semantics to the dedicated delete-confirm
   constants, including deterministic uniqueness and ordering;
4. mirror those bounds in OpenAPI, including the one known
   `waiting_area_cleared` warning code;
5. add deterministic regression guards that fail on the original two
   omissions and on widened reason/warning semantics; and
6. regenerate the provider-free evidence/report from the repaired reviewer.
7. make private receipt presence an explicit committed/replay invariant and
   fail closed if success lacks it or a non-success unexpectedly carries it.

The canonical/alias route, accepted-adapter call, server dependency ingress,
proposal-version binding, private/public byte separation and raw DELETE
isolation must remain otherwise unchanged.

## Verification and claim boundary

Sol must run the exact provider-free focused and static API Spine profile,
reviewer no-write mode, Ruff, maintained-source compilation and whitespace
checks. No test may load the repository database fixture or execute SQL. Since
this is authenticated runtime/security-boundary code recovered from a failed
worker attempt, one fresh exact-candidate Gemini 3.7 Flash/high veto is required
before Sol acceptance.

Passing proves only provider-free HTTP route composition and canonical public
transport over the already accepted lower seams. Database execution, raw
DELETE convergence, capability provisioning, product/patient/clinical data,
provider or credential work, UI, deployment, production, release, Pages and
protected refs remain closed. `docs/branding/` and every unrelated untracked
file remain preserved; staging is explicit-path only.
