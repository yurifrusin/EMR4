# T3R1 Synthetic Shadow Refresh — Sol Acceptance

Date: 2026-07-18

Decision: `accepted_provider_free_shadow_refresh`

## Accepted scope

Sol accepts the source-bound projection of all 192 admitted synthetic Silver
v2 dialogues into the default-disabled T3 runner, the optional withdrawal
scoring dimension, the non-executing proposal vocabulary, and the exact offline
plumbing report.

The implementation does not copy or promote v2, alter its admission, change the
deterministic product parser/replay/scorer, access protected evidence, or open a
provider, runtime, API, database, UI, confirmation, deployment, release, or
write surface.

## Acceptance evidence

- projection hash:
  `sha256:c39cc71a988a425886d96ccb75ccf07a3937f5e1363899b08366319f4dd7b4bd`;
- report hash:
  `sha256:1c08d7bce492cdc94be5fa032498356cd1cb1283e2d5d387df86d1565f2de5a4`;
- cases: 192/192;
- offline samples: 384/384 perfect and safe;
- scored dimensions: 2,304/2,304;
- variance: zero;
- focused T3 plus v2 preservation gate: 127/127;
- final combined gate with handover/closeout guards: 139/139;
- provider calls: false; and
- model-quality claim: false.

The expected-decision echo is accepted only as an offline wiring oracle. It is
not accepted as evidence that any model understands the corpus.

## Review and boundaries

This was a tightly coupled Sol-owned tranche. The user-authorized first stage
was explicitly offline, so no external implementation or review prompt was
sent. Ariadne pre-plan receipt status was `passed`; worker slots remained empty.

The T3 live gate remains `blocked`, interpretation readiness remains
`runtime_or_provider_wiring_ready=false`, and the provider report remains
`live_provider_enabled=false` and `provider_calls_performed=false`.

Pause before the proposed synthetic-only live comparison. Its provider/model
selection, cost, privacy/retention, kill-switch, and execution evidence require
a new explicit Yuri approval payload.
