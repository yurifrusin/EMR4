# Native agent-factory diagnostic report timestamp recovery

Date: 2026-08-22

Timestamp: 2026-08-22T03:42:19.3682524+10:00 (Australia/Brisbane)

Status: **contained without execution retry**

The generated diagnostic report used the controller's frozen illustrative
timestamp `2026-08-22T04:15:00+10:00`, which was still in the future when the
single native attempt completed. The report's exact bytes remain immutable,
but that one metadata value is rejected by
`generated-report-metadata-rejection.json`.

The typed evidence's `launch.started_at_utc` remains the exact machine-recorded
process time. The terminal, stage, counters, package bindings and cleanup
claims in the report remain consistent with the evidence and are not rejected.

Future generated narrative timestamps must be derived from a machine clock at
artifact creation or omitted in favour of an already typed evidence timestamp;
they must never be guessed as a static future value.
