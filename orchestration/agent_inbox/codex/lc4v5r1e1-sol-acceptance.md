# LC4V5R1E1 Sol Acceptance

Date: 2026-07-16

Decision: `development_exit_valid_holdout_decision_required`

E1 is a Sol-owned deterministic binder with no behavior change and no external
worker. The underlying R1 source had already received an exact-head Gemini veto,
so another provider round trip had no material leverage.

## Evidence

- Contract and preplan receipt commit: `393033b7`.
- Binder source: `af8dc8dfb2750b291c2f750dc9c4598b3dc4f228`.
- Frozen report/test commit: `cc93957d`.
- E1 report hash:
  `sha256:488e3478eab1c9451f5d78c33c16a2d06be1fc89117f8da8fc6a24fdc2f001ed`.
- Bound v5 aggregate file hash:
  `sha256:40dfa844b5e94ce5ec88aae39d942ab9edfeb7835ce613da4d68c5ed99f0fb1c`.
- Bound R1 development report file hash:
  `sha256:3ab20d99c93fb14c528e229752072a969b5190b6fb3fd7cde8755aa40468689c`.

All 13 gates pass. The binder validates the exact v5 aggregate population and
valid sealed certification-fail decision, its three-family localization, all
21 unaffected families, the exact R1 probe population/hash, `4/18` to `18/18`
completion, `14/18` to `18/18` safety, zero variance, and both Sol acceptance
decisions. Tampered, malformed, missing, or contradictory input returns
`reassessment_invalid`.

The combined R1+E1 suite passed 35/35. The final serial semantic, temporal,
clarification, safety, D2-D4, D5R1, R1, and E1 handover gate passed 450/450.
The binder imports neither the parser nor fixture authoring code and does not
regenerate any prior report.

## Decision boundary

The supported ordinary-development blockers derived from the v5 aggregate are
closed. This is not product certification. Holdouts v1-v5 remain sealed and
cannot be rerun or reused implicitly.

Yuri must now choose either:

1. authorize a genuinely fresh certification holdout v6 (Sol's
   recommendation); or
2. approve a separately reviewed explicit reuse policy.

No certification evaluation, holdout authorship, or reuse may start before
that decision. T3.1-T3.4 remain intact and blocked by default. T3.5/providers,
local-model development use, historical diary material, runtime/default
changes, routes, APIs, UI, database, deployment, release, and all live/write
authority remain deferred.
