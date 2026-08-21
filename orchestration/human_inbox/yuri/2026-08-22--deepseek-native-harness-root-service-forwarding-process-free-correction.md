# DeepSeek native Harness root-service-forwarding process-free correction

Date: 2026-08-22

Timestamp: 2026-08-22T09:01:43.2459891+10:00 (Australia/Brisbane)

## Lay summary

We have now designed the exact wiring correction for the Harness without
risking another run. The outer runner hands the preset service directly to the
guard, and the guard hands the service into one controlled bridge. Only that
bridge is allowed to inspect and call the service's mount function, so a bad or
missing connection becomes a small typed terminal instead of escaping as a
vague Harness failure.

The Git bookkeeping improvement also worked: the contract contains no commit
field for the model to remember or type. The controller asked Git's resolver
for the plan and implementation objects and recorded the resulting full IDs.

## Technical summary

At exact implementation source
`2c25ce7d65199e82c4d4fe93bbd1d0efc80474fe`, all 23 static source predicates
passed. The derived guard has zero `agentCtx.agentPresets` reads. The derived
bridge validates the root service and mount handle inside its `try`, invokes
`mount.call(presetService, agentCtx, presetId)` and retains the accepted safe
terminal mapping. The focused 11 tests and exact broader 169-test collection
passed with one platform-specific skip.

Eight bounded workflow incidents were caught and corrected. They add honest
local build cost, but no external worker, native Harness or provider attempt
was wasted. The accepted v2 object-ID mechanism recomputes unchanged after its
evidence commit, so later repository progress no longer changes which
implementation object it reports.

## Next and attention

Next is one separately frozen isolated Node fixture for the exact derived
bridge and sanitizer, using authored-synthetic stubs in a disposable root. It
will not start the native Harness, DeepSeek worker, model or provider. Yuri's
attention is not required.
