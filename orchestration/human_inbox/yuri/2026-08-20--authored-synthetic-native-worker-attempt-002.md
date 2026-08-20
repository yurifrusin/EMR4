# Authored-synthetic native Harness worker attempt 002

Date: 2026-08-20

Timestamp: 2026-08-20T22:55:57.2746082+10:00 (Australia/Brisbane)

## Lay summary

The new clockwork and broker controls worked as intended around the attempt,
but the native Harness itself did not reach DeepSeek. It started once, stopped
before its internal HMR/runner stage, made no provider request and was not
retried. Nothing was edited and cleanup was complete.

This is a mixed but useful conclusion. We can now say exactly that a launch was
consumed, where in the lifecycle it stopped, that DeepSeek was never called,
and that no hidden retry or leftover process occurred. We still cannot say why
the Harness stopped: the controller retained only the startup error's byte
count and digest before deleting the raw stream, so the final label is too
generic. The Harness is therefore better controlled and traceable, but not yet
reliable or diagnosable enough for normal EMR4 worker duties.

## Technical summary

- Candidate isolation: 11 deterministic commands plus fresh Gemini 3.7
  Flash/high semantic veto passed at exact candidate
  `7f14d9eb2490aa0864feb8d70f1dcd9a2422747b`.
- Checkpoint publication: task source
  `bf4af9db23827bbed8adc724eaf4ad58a1347dfe`, clockwork lease sequence 81,
  canonical drift 0 and dual ownership 0.
- Occupied terminal: one process, exit 1, 11,214 ms, zero HMR events, zero
  runner requests, zero provider calls, zero tools, zero changes and zero
  retries/fallbacks/auxiliary calls.
- Failure: `native_harness_terminal_failure`; 7,314 stderr bytes retained only
  by SHA-256, so the exact pre-HMR cause is unproved.
- Cleanup: Harness absent, broker absent, exact attempt root absent, raw session
  and logs absent; attempt-001 lifecycle digests unchanged.
- Post-terminal validation: 9/9 deterministic commands passed.
- Clockwork closeout: Continuity 353 / Compass 335, lease sequence 82,
  canonical drift 0, dual ownership 0 and one publication. Three dry-run
  vocabulary/order mistakes were rejected without mutation, registered and
  corrected; revision 576 has 715 contained incidents and none open.

## Deliberately closed

No new worker attempt, retry, provider request, product/database/data access,
ordinary-practice enablement, route/client/status change, production,
deployment, release, Pages or protected-ref movement is open.

## Place in the Raisa direction and next work

The Harness remains a potential economical worker surface, but only behind the
clockwork/broker boundary. The next tranche will be provider-disabled and will
turn pre-HMR startup failures into a closed sanitized terminal vocabulary
before raw streams are deleted. It will not launch another worker. Yuri's
attention is not required for that repair; a later occupied retry would require
a distinct decision.
