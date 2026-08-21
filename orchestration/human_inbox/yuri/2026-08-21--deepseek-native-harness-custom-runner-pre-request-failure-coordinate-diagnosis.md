# Native Harness typed failure-coordinate diagnosis

Date: 2026-08-21

Yuri attention required: `no`

## Lay summary

We have replaced the design's vague “custom runner failed” reading with a
finite seven-position dial. The model cannot write its own description into
that dial: the runner advances it mechanically as execution moves, and the
sidecar accepts only the fixed positions and fixed sanitized error kinds.

This is a useful example of the emerging control architecture: the LLM can sit
at a reasoning control seat, but deterministic machinery owns the readings,
the admissible levers and the authority checks. Human intent and judgment stay
above that mechanism, with human confirmation retained for lasting real-world
effects where required.

The live handover compaction is now part of the clockwork's own projection. It
must remain below 80 KB / 500 lines, while 222 historical acceptance rows stay
available in a hash-bound index rather than burdening every rehydration.

## Technical summary

- Accepted diagnostic source: `167f8330216b84f2981469299575f4fa7ad1f7e8`.
- Reviewed closeout source: `97c4367cc21c7bf9dad1cbeab6be0da314fec3be`.
- Closed output: 7 stages, 3 causes, 7 error kinds, exact keys, full Git OID,
  4,096-byte canonical limit and all raw-retention flags false.
- Bound sources: accepted runner plus cached rc.7 `dsh-agent`,
  `dsh-agent-loop`, `dsh-agent-presets` and `dsh-session` members.
- Verification: 19 focused tests, 106 predecessor regressions, 548 final
  governance tests, lint, compile and generated schemas pass; prohibited
  process/request counts remain zero.
- Eleven workflow observations are corrected or contained in register revision
  596, with none open.

## Deliberately closed

No occupied attempt, Harness/broker/worker/model/provider process, DeepSeek
request, product/configuration change, ordinary-practice enablement, patient or
clinical data, production, deployment, release, Pages or protected-ref movement
is authorised or claimed.

## Next

The engine continues with the provider-free post-HMR sidecar integration
rehearsal. It will integrate the code-owned dial into a new future-only runner
and prove controller ingestion plus broker-zero joining before any occupied
attempt is considered.
