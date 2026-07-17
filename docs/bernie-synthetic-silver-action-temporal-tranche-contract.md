# Bernie Synthetic Silver Action/Temporal Tranche Contract

Date: 2026-07-17

Status: `accepted_partial_pass`

Authority: Yuri's bounded ordinary-development diagnostic/remediation authorization

## Objective

Reproduce and classify a deterministic 24-candidate slice of the accepted
synthetic Silver robustness failures, then repair only language-extraction or
normalization causes independently supported by that slice. Do not broaden
policy, replay, product, runtime, provider, API, database, UI, confirmation,
deployment, release, or write authority.

## Frozen selection

The selection manifest is
`tests/fixtures/bernie_synthetic_noise/action_temporal_tranche.json`. It binds:

- merged selection source `fafe6ad57bde62a6ee08172d88ec43fd71728f64`;
- accepted baseline report hash
  `sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5`;
- accepted candidate hash
  `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`;
- 12 primary action-extraction failures;
- 10 primary temporal/normalization failures; and
- both replay-only failures as controls.

The action slice covers all six actions, medium and high noise, and one-shot,
clarification, correction, ellipsis/repetition, and session-restart surfaces.
The temporal slice covers `not_before` ("3pm or later"), `not_after` ("by
5pm"), and corrected `approximate` ("at 4pm—sorry, around 3pm") language.

## Ordered method

1. Run all 24 candidates twice through the existing interpretation, replay,
   and composed scorer before modifying extraction code.
2. Preserve the pre-repair report and classify every selected failure as:
   `supported_extraction_gap`, `supported_normalization_gap`,
   `language_authoring_gap`, `replay_gap`, or `upstream_cascade`.
3. Implement only the smallest parser changes supported by multiple clear
   receptionist-to-assistant surfaces or an exact frozen semantic contract.
4. Add direct unit tests for each accepted language rule.
5. Re-run the frozen 24, the full 192-candidate Silver baseline, and the
   relevant ordinary-development preservation suite serially.
6. Obtain a fresh exact-head independent veto if a material parser change
   survives preservation checks.

## Acceptance

The tranche may close as `remediation_pass`, `partial_pass`, or
`diagnostic_only`.

- Safety must remain perfect and repeat variance must remain zero.
- Replay controls may be classified but are not automatically repairable.
- No selected candidate may be made to pass by feeding expected fields into
  interpretation or by weakening the scorer.
- Improvements outside the selected slice are evidence only; they do not
  promote Silver to Gold or alter V10 certification.
- Any newly exposed clarification-policy or product-behaviour choice returns
  to Yuri before implementation.

## Protected boundary

Protected V1-V10 artifacts remain inaccessible. Only ordinary development,
the admitted synthetic Silver corpus, its accepted aggregate baseline, and
new tranche artifacts may be used. The earlier metadata-only filename incident
grants no access authority.

## Accepted evidence

The immutable pre-repair report hash is
`sha256:1bf572c3906fe108cd81332953ae3333d033b6afc2f34827b2cdd0f1154e3822`.
The final exact report hash is
`sha256:6a4c89992e7a791164bda581b04ae2216a3c7e2661b4a9f29963b220d90b9db2`.
Fresh Gemini independently reproduced the final tranche, the full 192-record
Silver result, the focused tests, and the exact ordinary-development impact
and returned `DECISION: pass` on candidate code head `13214dab`.
