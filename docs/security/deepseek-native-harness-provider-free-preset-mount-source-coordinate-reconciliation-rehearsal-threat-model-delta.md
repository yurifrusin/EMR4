# Threat-model delta: preset-mount source-coordinate reconciliation

Date: 2026-08-22

Timestamp: 2026-08-22T04:31:24.1598131+10:00 (Australia/Brisbane)

Status: **frozen before implementation**

## Scope delta

The accepted safe terminal identifies preset mounting but deliberately omits
the raw exception. This tranche reads only the exact pinned package source and
projects a finite internal candidate set. It adds no runtime or provider
authority.

## Controls

| Threat | Fail-closed control |
|---|---|
| Source inspection silently becomes execution | Deterministic Python reads only pinned files; native-process count is schema-fixed at zero. |
| A plausible cause is presented as observed fact | Separate source-reachable candidates from observed terminal fields; `exact_internal_coordinate_observed` remains false. |
| Ambient package update changes the inference | Verify exact version and SHA-256 for every inspected file before projection. |
| Discarded raw error is reconstructed or exposed | Accept no logs, streams, exception text, stack, cause, path, prompt, response or credential. |
| Candidate vocabulary expands through prose | Schema-enumerate the six accepted source coordinates and reject extra fields or values. |
| Static result authorises a retry or repair | `repair_selected`, `second_native_process_authorized`, worker and occupied-model authority remain false. |

## Residual risk

Static source may leave more than one reachable internal coordinate. That is an
honest result and may justify a separately frozen safe probe. It is not evidence
for choosing a repair or rerunning the native process.

## Security acceptance

Accept only exact source identities, the closed finite candidate set, explicit
non-observation and zero runtime/provider/product authority. Preserve every
data, production, Pages and protected-ref boundary.
