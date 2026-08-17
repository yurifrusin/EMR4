# Provider-free read-only post-cancellation programme orientation closeout

Date: 2026-08-18

Timestamp: 2026-08-18T04:57:36+10:00 (Australia/Brisbane)

Status: accepted

Accepted reviewed source: `74da22d5372299eb2d2e38bb2266b76c89a97035`

Result:
`raisa_provider_free_read_only_post_cancellation_programme_orientation_pass`

## Outcome

The completed first-party cancellation chain leaves arrival/check-in as the
narrowest dependency-satisfied command-family question. The repository
currently carries three scopes that must be reconciled before another visible
control or runtime opening:

- both first-party Diary projections can express check-in through generic
  status `Arrived`;
- a distinct A5.1 proposal/confirm family can atomically include waiting-area
  assignment but remains default-off and authored-synthetic-practice-only; and
- the static action grammar, route contract and promotion checklist still
  describe check-in as planned or lacking a signed confirm endpoint.

This is an authority and lifecycle inconsistency, not proof of a corrupt write
path. The selected successor is therefore one provider-free read-only
arrival/check-in command-family convergence review. It will compare exact
contracts and choose whether A5.1 becomes canonical, generic status gains an
explicit check-in binding, or the families retain strict non-overlap. This
orientation selects none of those product meanings.

## Negative evidence

The unchanged endpoint-coverage baseline reports six failures because the
static route contract spells `{appointment_id}` while FastAPI exposes
`{appointment_id:uuid}`, which also causes a false literal
`/status/confirm` shadow diagnosis. That packet is preserved as required input
to the successor review. It is not a candidate regression and grants no source
repair authority in this tranche.

## Verification

- 11 new orientation and plan checks passed;
- 107 API Spine, action-grammar, route-contract and promotion checks passed;
- the canonical fast profile passed 200 tests, Ruff, 217 maintained-source
  compilations, Diary JavaScript syntax and Git whitespace;
- the candidate register and canonical validator passed; and
- one fresh Gemini 3.7 Flash/high exact-candidate veto passed all seven
  manifest commands and left the clean review worktree unchanged.

Subsequent AER-0399 through AER-0401 preserve three orchestration-only
pre-dispatch/register correction incidents. They changed neither the reviewed
candidate nor its architecture finding.

## Claim boundary

This is repository-static, authored-synthetic orientation evidence. No product,
backend, API/OpenAPI/GraphQL, schema, service, migration, database, route,
feature flag, product/patient/clinical data, provider, credential/IAM,
deployment, release, Pages or protected ref changed. `docs/branding/` and all
unrelated untracked files remain preserved.
