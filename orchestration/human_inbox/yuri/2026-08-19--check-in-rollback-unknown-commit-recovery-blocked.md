# Check-in rollback and unknown-response rehearsal — blocked

Date: 2026-08-19

Timestamp: 2026-08-19T18:08:13.2461050+10:00 (Australia/Brisbane)

Yuri attention required: **yes**

## Lay summary

The safe rollback portion worked every time, but the test harness could not
reliably hand the final caller result back after the simulated lost response.
It failed safely three times: no success was announced, the command was not
retried, and every temporary database role, relay, container and network was
removed.

This means ordinary check-in has not been enabled and the unknown-response
safety gap remains open. I stopped at the plan's hard limit rather than spend a
fourth database run on the same transport shape.

The clockwork itself handled this honestly after one small missing gear was
added: it can now record a blocked operation without pretending it succeeded,
advancing the programme maps or requiring a hand-edited latch. That part is a
useful workflow improvement.

## Technical summary

- Attempt 001: `worker_join_timeout`, SHA-256 `e357e3a2dec7f0d0740a2ea6f518cb695dc2a5cbf88b9c321dbcd61d6e7bd1c1`.
- Attempt 002: `worker_outcome_missing`, SHA-256 `bea605006bf36996d439876a4976ec5b733ddc4bb841d5942aae1057c5f514ed`.
- Attempt 003 after explicit relay EOF propagation: still
  `worker_outcome_missing`, SHA-256 `15cebad64c7bfbddb83878e75cf8f3a0d137a7834075e063c92aead8b603e219`.
- Every attempt passed rollback-zero and exact cleanup; none reached the
  authoritative readback classifier.
- Candidate `2e814b2c3f8b687adb499d6f61a64d316dc016df` added a closed clockwork
  `blocked_transition` path. Generation
  `gen-6f758043be53b4ce1d14e9e9fab01649c0aa2d91fb90ac649f9db314c216b811`
  published once at lease 5 with no Continuity/Compass advance and no manual
  canonical drift.
- 117 focused tests passed with one expected live-evidence skip; Ruff,
  compilation, JSON and whitespace gates passed. Gemini was correctly not
  called after deterministic failure.

## Deliberately closed

No ordinary-practice activation, feature/allowlist change, product/API/client
change, generic-status `Arrived`, waiting-area movement, data, provider,
production, deployment, release, Pages or protected-ref movement occurred.
`docs/branding/` and unrelated untracked files are preserved.

The non-PHI paused Pushover notification succeeded with request
`674f08c4-6aa9-44c7-9357-9749eb5ff93c`.

## Decision needed

Please choose one of these two outcomes:

1. authorise a new, separately frozen transport design that removes the host
   relay from the evidence path before another disposable execution; or
2. defer this operational-evidence gap and leave ordinary check-in admission
   not ready.

No fourth run is authorised under the present plan.
