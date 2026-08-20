# DeepSeek native Harness pre-HMR startup recovery

Date: 2026-08-20

Timestamp: 2026-08-20T23:49:08.9636913+10:00 (Australia/Brisbane)

## Lay summary

The Harness controller can now take a safe reading of a startup failure before
deleting its raw output. Instead of leaving us only with “the process failed”,
it records whether process creation failed or a started process failed before
HMR, plus one of eleven tightly bounded cause classes. Unknown and mixed cases
stay explicitly unknown or ambiguous. No raw error text or secret is retained.

This is a real traceability improvement, not yet a reliability result. It gives
the next occupied rehearsal a much better chance of telling us what failed if
the Harness stops early, but it says nothing new about DeepSeek because no
DeepSeek request occurred in this tranche.

## Technical summary

At reviewed candidate `12c289e28490fcef50f95d50a299e186b4b78847`,
the reusable terminal component and controller binding pass 12 semantic
scenarios, 12 hostile mutations, 49 provider-disabled tests, five ordering
checks, Ruff and compilation. Seventeen attempt-001/002 artifacts remain
byte-identical. The controller writes and validates the sanitized sidecar
before exact-root cleanup and publishes only its digest.

During development I selected one legacy controller test too broadly; it
briefly started the local provider-free broker only to its ready event, then
terminated it without a provider request. Exact readback found zero matching
processes. This and eight smaller rejected technical drafts are preserved and
contained as AER-0716 through AER-0724.

## Deliberately closed

No new occupied worker, Harness/broker/provider execution, attempt-002
reclassification, raw output retention, product/database/data change,
ordinary-practice enablement, deployment, release, Pages or protected-ref
movement is accepted here.

## Next decision

The provider-disabled recovery is complete. A new occupied authored-synthetic
native-worker attempt would now be materially better instrumented, but the
accepted boundary requires your distinct decision before it is launched.
Your attention is therefore genuinely required for that next step.
