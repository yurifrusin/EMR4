# Native Harness composition-unclassified source reconciliation report

Date: 2026-08-22

Timestamp: 2026-08-22T08:22:07.529443+10:00 (Australia/Brisbane)

Result: **root_preset_service_not_forwarded_before_bridge**

The exact generated runner admits the root `agentPresets` service but does not
forward that handle into the composition guard. The exact installed agent loop
supplies setup with a private context derived from a dependency surface that
does not declare `agentPresets`. The generated guard dereferences
`agentCtx.agentPresets.mount.bind(...)` before the preset-mount bridge enters
its sanitizing boundary. An uncoded escape therefore reaches the broader guard,
whose closed fallback is the observed
`EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED` coordinate.

Failed source coordinates: `none`.

The narrowest prospective correction is to forward the already admitted root
preset service explicitly into the guard and validate the mount handle inside
the bridge. No correction or retry occurred here. No raw exception or private
context value was recovered, and the new bridge runtime path remains unproved.

Node, native Harness, worker, model and provider processes started by this
reconciliation: **0**.
