# Threat-model delta: preset-mount sanitizer runner bridge

Date: 2026-08-22

Timestamp: 2026-08-22T06:03:42.6115665+10:00 (Australia/Brisbane)

Status: **frozen before implementation**

## Scope delta

The pure preset-mount sanitizer is admitted, but it is not connected to a
runner. This tranche introduces only a deterministic provider-free source
bridge at the exact preset-mount catch. It introduces no native Harness process.

## Controls

| Threat | Fail-closed control |
|---|---|
| Bridge catches too broadly | Bind one catch to the exact `await presets.mount(...)` call and test its source coordinates. |
| Raw `PresetMountError` detail escapes | Emit only the sanitizer's frozen stage/code/null-detail record; forbid message, stack, cause, paths and streams. |
| New grammar conflicts with the existing fallback | Make preset-mount and broader composition terminals disjoint and precedence-test both. |
| Sanitizer bytes drift during connection | Bind the accepted SHA-256 before runner derivation and in all evidence. |
| Static success is mistaken for native readiness | Native process, worker/model/provider and retry counters remain zero; a later native run needs a new frozen tranche. |
| Provider or product authority leaks through the runner | No provider configuration, request path, target, product source or data surface is admitted. |

## Security acceptance

Accept only the exact one-catch, one-import, one-call closed projection with null
detail, deterministic fixture proof and all native/provider/product gates false.
