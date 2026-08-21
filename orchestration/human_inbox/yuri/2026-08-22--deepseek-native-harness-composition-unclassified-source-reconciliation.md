# DeepSeek native Harness unclassified-composition source reconciliation

Date: 2026-08-22

Timestamp: 2026-08-22T08:26:47.0343827+10:00 (Australia/Brisbane)

## Lay summary

We have found the precise wiring gap behind the Harness's last vague
"unclassified" failure. The outer controller already had the correct preset
service in hand, but it did not pass that handle into the private DeepSeek
agent setup. The guard then looked for the service in a narrower private
context and failed before our new typed bridge could take control.

This is useful progress because the failure is now a specific connection error,
not another opaque Harness episode. The next tranche will correct that
connection entirely offline before we consider another native attempt.

## Technical summary

The hash-bound controller compared the accepted generated runner/guard/bridge/
sanitizer and the installed rc.7 agent-loop/scope/preset-service sources. All
thirteen source coordinates passed at exact implementation source
`ab2018091ee40fa8833f957daf41085a83f6b41d`. The closed result is
`root_preset_service_not_forwarded_before_bridge`.

The runner resolves root `presets`, but calls
`assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS)`. The installed
agent loop supplies `prepared.agent.ctx` from its narrower dependency surface.
The guard evaluates `agentCtx.agentPresets.mount.bind(...)` during argument
construction, outside the bridge's sanitizing body, and the broad sanitizer
therefore returns `EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED`.

No Node/native-Harness/worker/model/provider process, request, retry, product
change or protected-ref movement occurred. The exact runtime exception remains
deliberately unknown and the new bridge runtime remains unproved.

## Next and attention

Next is the process-free root-service-forwarding correction rehearsal. It will
pass the already admitted root service explicitly and place validation inside
the typed bridge, still without a native process. Yuri's attention is not
required.
