# LC4V5R1E1 Sol Contract

Date: 2026-07-16

Decision before implementation: `development_exit_reassessment_frozen`

This is a small Sol-owned deterministic evidence binder. No external worker is
dispatched: the underlying R1 source has just received an exact-head Gemini
veto, and E1 changes no parser, policy, replay, fixture, or product behavior.

## Exact inputs

- LC4V5 aggregate report file hash:
  `sha256:40dfa844b5e94ce5ec88aae39d942ab9edfeb7835ce613da4d68c5ed99f0fb1c`.
- LC4V5 report hash embedded in accepted aggregate evidence:
  `17c123559a8c708fa0d122a2de1dbadc465e1d4e93a19814c5968f00f0b9c88b`.
- LC4V5 Sol acceptance file hash:
  `sha256:ecd575cfe73f4cbba9eee6c0733a30ac5aefe3ec78183371a0664c8aed8bdbcd`.
- LC4V5R1 development report file hash:
  `sha256:3ab20d99c93fb14c528e229752072a969b5190b6fb3fd7cde8755aa40468689c`.
- LC4V5R1 frozen probe hash:
  `sha256:e44885916b9790ac858715c7d3d7c43b10231edc5bdfcceeba8486fc077ec55f`.
- LC4V5R1 acceptance at `82cef912` with decision
  `development_three_family_remediation_accepted`.

## Required result

Read only the two committed aggregate/development reports and their named Sol
acceptances. Validate exact file hashes, schemas, populations, aggregate family
localization, zero variance, sealed-fail v5 decision, R1 `4/18` to `18/18`
completion, `14/18` to `18/18` safety, exact probe hash, and closed provider and
certification boundaries.

Return `development_exit_valid_holdout_decision_required` only if every gate
passes. Missing, malformed, drifted, or contradictory input returns
`reassessment_invalid`. Do not execute the parser, regenerate either report,
discover fixtures, or inspect any protected surface.

The accepted exit means only that the supported ordinary-development blockers
derived from the v5 aggregate are closed. It is not product certification. The
next step is a Yuri decision between a genuinely fresh certification holdout v6
(recommended) and an explicit reviewed reuse policy.

## Closed boundaries

Holdouts v1-v5 remain sealed and unavailable. T3.1-T3.4 remain intact and
blocked by default. T3.5/providers, local-model development use, historical
diary material, runtime/default changes, routes, APIs, UI, database,
deployment, release, and all live/write authority remain deferred. E1 may add
only its binder, tests, report, acceptance/closeout, receipts, and handover
updates.
