# Reception One Receptionist-first v6.3 Closeout

Status: complete; occupied cohort did not pass at 22/24 exact outcomes
Recorded: 2026-07-30

## Result

The complete twenty-four-request authored-synthetic regression ran through the
exact bounded Sydney Vertex lane. Twenty-two terminal results matched their
frozen deterministic oracle. Two did not, so the tranche result remains
`reception_one_receptionist_first_v63_full_cohort_fail_closed`.

The result name must not obscure an important distinction: one mismatch was a
normal fail-closed no-release terminal, but `b-create-correct` exposed a
deterministic proofreader coverage defect and produced a non-exact
proposal-only study release. That release reached no user, product or database
and performed no write, but it is not acceptable evidence of exact form
filling.

All twenty-nine opened ledgers are consumed, no call followed the terminal
cohort result and task-scoped residue is clear.

## What improved

- The former `MAX_TOKENS` case passed on its primary with the 3072-token
  ceiling.
- The unstamped “no-show” request safely produced the frozen clarification
  outcome without inventing a `dna` alias.
- Twenty-two of twenty-four requests matched exactly, compared with
  twenty-one of twenty-four in v6.2.
- Every resize, cancellation, explicit status, squeeze-in and clarification
  pattern passed, as did most create and move patterns.

## Two mismatches

1. `b-create-correct` selected the correct create goal and passed the current
   proofreader, but its form omitted the explicitly corrected 3:00 PM time
   constraint from the slot search. The released authored-synthetic proposal
   contained both the 2:30 and 3:00 candidate slots instead of only 3:00. No
   write or delivery occurred. This is a deterministic proofreader coverage
   defect: recognized exact constraints must be checked against the typed
   source graph and released candidate set.
2. `b-move-shift` produced a correctly typed move program on its terminal
   turn, but the independently bounded natural receptionist response did not
   describe the same goal. The proofreader correctly vetoed it and released
   nothing. The model needs a clearer same-goal rule across its spoken and
   form channels, including correction turns.

## Calls and controls

- 24 primary calls and 5 terminal second calls; 29 total against a ceiling of
  48;
- all 29 provider responses completed with HTTP 200;
- 113,676 prompt, 15,235 visible candidate, 19,095 thinking and 148,006 total
  tokens reported by Vertex;
- exact `gemini-2.5-flash`, `bernie-emr4-dev`, Bernie impersonated service
  account, `australia-southeast1` and regional hostname throughout;
- no API key, service-account key, global endpoint, fallback, provider tool,
  grounding, retrieval, cache creation, product/database access, write or
  delivery; and
- raw prompts, raw provider responses, credentials, API-key information and
  hidden chain-of-thought were not retained.

## Cleanup

All twenty-nine ledgers are consumed. Independent post-run checks found zero
owned containers, networks, images or broker/cell processes. No daemon-wide
prune was performed.

## Recommended descendant

A separately versioned v6.4 descendant should:

- add a deterministic proofreader invariant that every recognized exact
  request constraint is present in the typed source graph and reflected in
  the admitted candidate set;
- add focused regression tests for corrected exact-time broadening before any
  occupied call;
- state that the natural receptionist response and decision note must describe
  the same goal as the typed form, including after a correction ticket; and
- rerun the complete twenty-four-request cohort without opening the
  no-show-to-`dna` alias.

The provider, model, project, identity, Sydney endpoint, authored-synthetic,
isolation, no-fallback, no-write and USD 1 boundaries can remain unchanged.

## Claim limit

This evidence proves twenty-two exact safe outcomes and exposes two actionable
defects over a reused authored-synthetic cohort through the configured and
observed Sydney locational request path. It does not prove independent
generalisation, production fitness, Australian physical or sovereign
processing, or safety for real, product-derived, patient, health, clinical,
protected or historical data.
