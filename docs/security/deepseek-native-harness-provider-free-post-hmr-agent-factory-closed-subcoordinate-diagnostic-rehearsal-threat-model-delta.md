# Threat-model delta: native agent-factory closed-subcoordinate diagnostic

Date: 2026-08-22

Timestamp: 2026-08-22T02:48:06.6590250+10:00 (Australia/Brisbane)

Status: **frozen before implementation or execution**

## Scope delta

The predecessor proved clean containment but exited after HMR mutation without
a typed runner sidecar. This diagnostic adds finite stage attribution around
dynamic package imports, service admission and at most one real factory call.
It grants no published agent/session, turn, request, target or product power.

## Controls

| Threat | Fail-closed control |
|---|---|
| A static package import prevents `apply()` and erases attribution | The HMR wrapper statically imports only Node built-ins and dynamically imports every package/guard inside its guarded transaction. |
| Raw errors become a new data leak | Only exact known-error classification or `unclassified_error` plus a closed stage is retained; message, stack, code, cause, stream and path are forbidden. |
| Fallback zeros are mistaken for factory observations | With no sidecar, the controller may claim only `runner_link_or_apply_absence`; factory counters are nullable/unknown. |
| A diagnostic becomes an implicit retry | It has a distinct operation and attempt id, changed typed objective and immutable consumed predecessor; it cannot accept the predecessor result. |
| The factory publishes before diagnosis | The same synchronous commit veto, registry listeners and postrollback reads remain mandatory; any handle, event or residue rejects. |
| Provider configuration produces traffic | No message or turn exists; independent broker/network gauges remain zero and any request rejects. |
| Multiple terminals obscure causality | Exclusive sidecar creation, one terminal schema and one native process; a second write or output rejects. |
| Failure cleanup erases evidence or leaves resources | Bounded sidecar is read before exact process termination/root deletion; publication waits for process/root absence. |

## Residual risk

The result may still be `runner_link_or_apply_absence`, which would narrow the
failure to the HMR linkage boundary but not identify an in-runner stage. It will
not establish coding quality, DeepSeek transport, model behavior, target edits
or product fitness.

## Security acceptance

Accept only a closed typed terminal joined to exact readiness/HMR evidence,
all-zero downstream gauges, immutable bundle/seed and complete cleanup. Preserve
the consumed predecessor and every product, data, production, Pages and
protected-ref closure.
