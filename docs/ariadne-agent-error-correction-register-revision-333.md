# Ariadne agent error and correction register — revision 333

Date: 2026-08-17

Timestamp: 2026-08-17T12:02:01.2827456+10:00 (Australia/Brisbane)

Status: control implemented pending independent acceptance

## Revision

Revision 333 retains 381 bounded known incidents. No incident is erased or
reclassified as a reviewer decision.

- AER-0380 preserves both Gemini 3.7 Antigravity exit-1/empty-stderr failures.
- Provider-free replay proves their exact eight-command manifest passes in
  150.578 seconds, while the retry interval correlates with the launcher's
  fixed 30-minute print deadline.
- The launcher now uses one bounded 45-minute full-veto deadline and writes an
  atomic digest-only failure receipt with elapsed time, exit code and exact
  worktree postcondition after every nonzero transport exit.
- The correction remains `control_implemented_pending_acceptance` until one
  newly authorised fresh exact-checkpoint veto passes or returns durable
  fail-closed evidence.

## Boundary

The diagnosis makes no provider- or model-causal claim and does not treat a
transport failure as rejection or acceptance. It opens no alternate model,
product/patient/clinical/protected data, credential or IAM change, database,
deployment, release, Pages or protected ref.
