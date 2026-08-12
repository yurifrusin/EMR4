# Threat-model delta: compatibility-consumer and kernel-convergence admission review

Date: 2026-08-12

## New decision surface

This tranche creates only a static source-bound consumer and behavior map. It
adds no runtime principal, data flow, route, kernel, observer or persistence.

## Threats held closed

| Threat | Control |
|---|---|
| Inferring route retirement from zero native calls | External consumers remain `unknown_without_operational_observation`; routes stay mounted. |
| Treating tests as deployed consumers or deleting their coverage | Executable conformance callers are a distinct inventory class and remain preservation evidence. |
| Treating direct fixture writes as command authority | Four fixture/bootstrap writers are named as non-route obligations with no production authority. |
| Grandfathering raw requests into the kernel | Current raw profiles retain the exact three missing control groups and remain ineligible. |
| Conflating freshness with confirmation | A backend precondition and separate confirmation evidence remain independent. |
| Preserving duplicate-write behavior as a safety contract | Absence of command idempotency is recorded as a gap requiring a reviewed transition. |
| Breaking clients by changing status first | The selected first slice is confirm-first and unmounted; raw `PATCH` remains unchanged. |
| Moving directly to create | Create remains last and blocked on a database-owned schedule-domain fence. |
| Operational-data leakage through consumer discovery | The census reads only committed repository text and emits path/count facts, never requests, bodies, database values or telemetry. |
| Weakening current controls to satisfy stale tests | Past-date temporal denial and proposal idempotency admission remain unchanged; the next test-only repair must update clocks/headers, not expectations or application code. |

## Residual risks

Unknown external consumers cannot be resolved without separately authorised,
privacy-minimized operational observation. The existing raw status semantics
also permit an unusual terminal-state re-transition after warning/confirmation
on the preferred path; whether to retain or tighten that policy remains a
separate product/API decision. Neither risk is altered here.

## Authority boundary

No patient, clinical, product or operational data; database/source/watcher/
event; provider; credential; network; executable Bureau capability; command;
deployment; production; release; Pages or protected-ref authority is opened.
