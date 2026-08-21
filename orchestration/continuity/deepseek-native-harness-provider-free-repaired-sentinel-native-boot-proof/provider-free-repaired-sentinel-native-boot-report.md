# Provider-free repaired-sentinel native boot report

Date: 2026-08-21

Result: **failed_closed**

- Attempt: `repaired-sentinel-native-boot-attempt-001`
- Candidate: `b99d961e225f355a17e74ec15d6e82fb61d83532`
- Native processes / retries: `1` / `0`
- HMR events: ``
- Controller terminated after readiness: `false`
- Network / model / provider requests: `0` / `0` / `0`
- Process absent: `true`
- Disposable root absent: `true`
- Raw streams retained: `false`

This proves only the repaired initial sentinel loads and stock-headless HMR
reaches readiness in one provider-free rc.7 process. It is not a worker,
model/provider, product-runtime or reliability result.
