# Native Harness root-service-forwarding process-free correction report

Date: 2026-08-22

Timestamp: 2026-08-22T08:57:54.796863+10:00 (Australia/Brisbane)

Result: **root_service_forwarding_correction_admitted**

The prospective runner passes its already admitted root preset service into an
explicit guard parameter. The prospective guard no longer reads
`agentCtx.agentPresets`; it passes only the service object into the typed
bridge. The bridge alone validates the service, reads and validates its mount
handle and invokes that handle with the service as receiver. All of those
operations occur inside the bridge's sanitizing `try` boundary.

Failed source coordinates: `none`.

The caller-authored contract contains no Git object identity. Its plan and
candidate sources were resolved by the repository resolver as full commits at
evidence time.

This is a prospective source correction only. JavaScript was not materialized
or executed, and no Node, native Harness, worker, model or provider process,
request, retry or resume occurred. A separately frozen isolated Node fixture is
required before any native process can be considered.
