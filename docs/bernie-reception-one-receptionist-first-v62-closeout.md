# Reception One Receptionist-first v6.2 Closeout

Status: complete; occupied cohort failed closed at 21/24 exact outcomes
Recorded: 2026-07-30

## Result

The complete twenty-four-case authored-synthetic v6 regression ran through the
exact bounded Sydney Vertex lane. Twenty-one terminal results matched their
frozen deterministic oracle. Three did not, so the tranche result is
`reception_one_receptionist_first_v62_full_cohort_fail_closed`.

The failure is safe: no unverified draft from the three mismatches was
released. All thirty opened single-use ledgers are consumed, no call followed
the terminal cohort result, and task-scoped residue is clear.

## What improved

The minimal desk context removed the model/proofreader context asymmetry
without exposing the wider Diary. The model and proofreader shared one hashed,
source-labelled selected appointment, recent-dialogue and Diary-focus packet.

The full cohort, including all nine v6.0 passes, produced exact safe outcomes
for twenty-one cases. In particular, direct and corrected creates; the other
move variants; every resize and cancellation; explicit complete/arrived
statuses; both squeeze-in variants; and all four clarification patterns except
the deliberately ungrounded no-show synonym closed safely.

## Three terminal mismatches

1. `b-create-alias` ended twice at the provider response boundary with
   `MAX_TOKENS` and no parseable JSON candidate. The proofreader was not
   reached and nothing was released.
2. `b-move-shift` selected the correct move goal and used the readable selected
   appointment, but its first form omitted a required source and its corrected
   form connected incompatible source types. The proofreader vetoed both.
3. `b-status-noshow-gap` demonstrated useful colloquial understanding by
   interpreting “no-show” as a status change. The frozen typed contract,
   however, had no grounded `no-show`/`dna` status binding. The proofreader
   correctly rejected the invented external binding.

These are respectively an output-ceiling defect, low-level form-wiring defect,
and a typed-vocabulary/product-semantics gap. They should not be collapsed into
one generic model failure.

## Calls and controls

- 24 primary calls and 6 terminal second calls; 30 total against a ceiling of
  48;
- 28 completed provider responses and 2 bounded pre-candidate rejections;
- 110,027 prompt, 13,778 visible candidate, 20,275 thinking and 144,080 total
  tokens reported by Vertex;
- exact `gemini-2.5-flash`, `bernie-emr4-dev`, Bernie impersonated service
  account, `australia-southeast1` and regional hostname throughout;
- no API key, service-account key, global endpoint, fallback, provider tool,
  grounding, retrieval, cache creation, product/database access, write or
  delivery; and
- raw prompts, raw provider responses, credentials, API-key information and
  hidden chain-of-thought were not retained.

## Cleanup

All thirty ledgers are consumed. Independent post-run checks found zero owned
containers, networks, images or broker/cell processes. No daemon-wide prune was
performed.

## Recommended descendant

A separately versioned repair should:

- raise the output-token ceiling enough to preserve the 1024-token thinking
  budget plus the closed form;
- state explicitly that mention bindings must pass through their typed
  resolver before their resolved outputs can feed selected-appointment or
  proposal operators; and
- preserve clarification for unstamped colloquial statuses unless Yuri
  separately decides that `no-show` should be a deterministic alias for `dna`.

The existing output schema, deterministic proofreader, model/provider/project/
identity/region, authored-synthetic data, isolation, no-fallback and cost
boundaries can remain unchanged.

## Claim limit

This evidence proves twenty-one exact safe outcomes over the reused
authored-synthetic cohort through the configured and observed Sydney
locational request path. It does not prove independent generalisation,
production fitness, Australian physical or sovereign processing, or safety for
real, product-derived, patient, health, clinical, protected or historical
data.
