# Clockwork compact-card live-use review

Date: 2026-08-23

Timestamp: 2026-08-23T20:13:31.0779586+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

The clockwork's shorter control card has survived ordinary use. Three real
workflow events passed without a retry, a missing decision or a fallback to the
long manual form. The measured pairs averaged about 7.0 KB against 16.2 KB
previously, a 56.8 percent reduction.

The exercise also found and fixed one surrounding-test weakness. A test had
confused an old latch record with the live moving latch. The clockwork itself
was correct; the test now takes its current reading from the same mechanism.

## Technical summary

- accepted projection source remains
  `7c296e942530b80c49a08ed144e4b934587b1064` at lease 217;
- exact test-repair source is
  `0a24f0ed1eb941e5a5e3619bd0961ad6291441b4`;
- three compact events: first-invocation pass, zero preflight rejections, zero
  expanded state files and zero missing non-default decisions;
- one postpublication moving-latch test failure, contained and repaired;
- one fail-closed launcher-interpreter mismatch before any publication attempt,
  corrected by binding the repository virtual environment;
- 42 focused and 162 combined tests, Ruff, diff check and live-state check pass;
  and
- DeepSeek, Gemini and native subagents were not used because this was one
  serial deterministic latch observation.

## What remains closed

No native-Harness qualification, Claude fallback, provider call, worker
dispatch, product or patient/clinical data, runtime, deployment, release,
Pages, protected evidence or protected-ref movement is opened.

## Place in Raisa and next tranche

This is the practical shift from models rewriting bureaucratic state to models
choosing typed control positions while deterministic machinery takes the
reading. The next tranche maps duplicated postpublication validation so we can
identify a safe future simplification without removing any test yet.
