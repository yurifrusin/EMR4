# Provider-free source-repaired sentinel native-boot report

Date: 2026-08-21

Result: **failed_closed**

- Attempt: `source-repaired-sentinel-native-boot-attempt-001`
- Candidate: `84a9327d98812a9891af0ef5724045f7599eb3a5`
- Native processes / retries: `1` / `0`
- HMR events: `sentinel_activated`
- Failure coordinate: `native_process_exited_before_readiness`
- Network / model / provider requests: `0` / `0` / `0`
- Process absent: `true`
- Disposable root absent: `true`
- Raw streams retained: `false`

The repaired sentinel loaded, but stock-headless HMR did not reach readiness.
This result is scoped to one provider-free rc.7 process. It is not a runner,
worker, model/provider, product-runtime or reliability result.
