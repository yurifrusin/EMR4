# LC4V4D5E1 Sol Contract

Date: 2026-07-16

Decision before implementation: `development_exit_reassessment_frozen`

This is a small Sol-owned deterministic evidence binder. No external worker is
dispatched: the underlying D5R1 source has just received an independent Gemini
veto, and D5E1 changes no parser, policy, replay, fixture, or product behavior.

## Exact inputs

- D4 report hash:
  `sha256:dd1ecc077a59bf05e777eda1f3a5450c0a1b97a4c8a3fd21dc0363d473abd653`.
- D5 diagnostic report hash:
  `sha256:e2c461ee3b1821c94574b33693efa88d21b99ecf9a95b1ac723b24a933c50564`.
- D5R1 remediation report hash:
  `sha256:0cb444d1aeba82a80f5a16170b30b8ea203842dec4af81b768a688e5aae9bcdf`.
- D5R1 acceptance: `exact_four_remediation_accepted` at `feb66c35`.

## Required result

Read only the three committed development reports and their named acceptance
artifacts. Validate schema, embedded/canonical hashes, exact populations,
observation counts, taxonomy, all gates, zero variance, zero forbidden
observations, immutable legacy/D4 evidence, and empty D5R1 blocker selection.
Verify the runtime default remains legacy and Option A remains explicit.

Return `development_exit_valid_holdout_decision_required` only if every gate
passes. Any missing, malformed, drifted, or contradictory input returns
`reassessment_invalid`. Do not execute the parser, regenerate D4/D5/D5R1,
discover fixtures, or inspect any protected surface.

The accepted exit means only that the current ordinary development sequence
has no supported remediation blocker. It is not product certification. The
next step is a Yuri decision between a genuinely fresh certification holdout
(recommended) and an explicit reviewed reuse policy.

## Closed boundaries

Holdouts v1-v4 remain sealed and unavailable. T3.1-T3.4 remain blocked;
T3.5/providers, historical diary material, runtime/default changes, routes,
APIs, UI, database, deployment, release, and all live/write authority remain
deferred. D5E1 may add only its binder, tests, report, acceptance/closeout, and
handover updates.
