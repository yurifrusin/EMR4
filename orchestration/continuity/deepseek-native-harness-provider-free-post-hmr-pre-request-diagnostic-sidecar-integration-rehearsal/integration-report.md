# Native Harness post-HMR sidecar integration report

Date: 2026-08-21

Result: **pass**

- Claim: `provider_free_future_runner_sidecar_and_broker_zero_join_representable`
- Complete future runner: `98cf8db1803c7dbfde867044504a820518e448278faf220c8ec3c5dbb8818805`
- Generated helper: `bd2995a62c7d8bbf37b29c0cd5b5a88c3570341255d1644d9cb98cbef0bd490e`
- Closed join: exact sidecar plus broker-zero -> `post_hmr_pre_request_failure`
- Non-zero broker -> `post_hmr_request_boundary_unresolved`
- Invalid/absent sidecar -> `native_harness_terminal_failure`
- Node/Harness/broker/worker/model/provider/network/database/Docker counts: zero

This is provider-free representability evidence. It does not prove native
loading, a real sidecar, a real broker reading, DeepSeek behavior or Harness
readiness.
