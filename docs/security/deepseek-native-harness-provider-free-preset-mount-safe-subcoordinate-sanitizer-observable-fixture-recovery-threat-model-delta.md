# Threat-model delta: preset-mount sanitizer observable-fixture recovery

Date: 2026-08-22

Timestamp: 2026-08-22T05:15:00.4286611+10:00 (Australia/Brisbane)

Status: **frozen recovery before implementation**

## Scope delta

Attempt 001 consumed one local Node process but its internal self-check emitted
no safe vector. This recovery authorises one distinct replacement process whose
only observable is the already schema-closed result vector.

## Controls

| Threat | Fail-closed control |
|---|---|
| A mismatch remains opaque | Fixture always emits only fifteen three-field safe terminals; Python owns comparison and a mismatch index. |
| Making failure observable leaks fixture inputs | The observable vocabulary contains only the seven closed codes, array position and null detail. |
| Attempt 001 is silently retried | Bind its exact candidate, exit 2, zero streams and consumed state before attempt 002. |
| Recovery turns into repeated probing | Exactly one attempt-002 process; mismatch stops with no third-process authority. |
| Fixture becomes a Harness launcher | Repository binding still denies DSH, dynamic imports, child-process, environment, filesystem and network APIs. |
| Safe vector is mistaken for repair evidence | Runner integration, exact native cause, repair and retry authority remain false. |

## Security acceptance

Accept only immutable attempt-001 evidence, one closed observable attempt-002
vector and unchanged no-Harness/no-provider/no-product boundaries.
