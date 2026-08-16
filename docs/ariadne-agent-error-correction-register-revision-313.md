# Ariadne agent error and correction register — revision 313

Date: 2026-08-16

Timestamp: 2026-08-16T20:43:39.3173841+10:00 (Australia/Brisbane)

## Result

Revision 313 preserves 362 bounded known incidents. AER-0360 and AER-0362 are
corrected; no incident is open or contained.

AER-0362 records a continuation-evidence harness gap found before verifier
dispatch. The pre-commit receipt correctly computed the changed harness
settings fingerprint, but the copied active-operation latch retained the prior
fingerprint and the receipt still returned `passed`. No worker or verifier was
dispatched on that inconsistent evidence.

The orchestrator preflight now computes the settings fingerprint once and
requires exact equality with
`active_operation.checkpoint.settings_fingerprint`. A mismatch returns
`revision_required` and forbids dispatch for every configured continuation
event. The workflow hard controls, exact fixture and current latch are updated
to the newly computed fingerprint, and focused hostile/pass coverage protects
the invariant.

AER-0360's recovery is now closed at exact candidate
`43e993a98ffec3f9ffe2740b0b38816bcb2d6adb`. The 517-test provider-free
profile and one clean seven-command Gemini 3.7 Flash/high veto pass; every
recovery amendment remains limited to the two lease-owned paths.

## Boundary

This is a locally observed harness failure, not a model, provider or product
quality claim. It opened no route, database, capability, product
data, provider, network, deployment, Pages or protected ref.
