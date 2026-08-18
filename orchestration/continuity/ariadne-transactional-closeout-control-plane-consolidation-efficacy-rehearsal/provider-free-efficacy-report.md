# Provider-free transactional closeout-control-plane efficacy report

Date: 2026-08-19

Timestamp: 2026-08-19T00:50:18.5366163+10:00 (Australia/Brisbane)

Decision: `passed`

Evidence label: `provider_free_repository_local_shadow`

## Result

The candidate passed the frozen efficacy thresholds without excluding its
shared-engine cost. Three accepted historical projections retained exact node,
journey, source, authority and evidence hashes. All seven observed bookkeeping
defect classes failed before publication; none escaped. The injected exception
after each of eight staging writes left no published generation and no change
to the live graph, Compass or latch.

The manifest contains no Git object field. The engine observed HEAD as the full
`f21072405a4d5877ec03e2cd1aefc7fa74d379e9`, verified it with the existing
strict resolver and copied it into every prospective projection and WorkOrder.

## Measured weight

| Measure | Legacy representative surface | Clockwork candidate |
|---|---:|---:|
| Maintained executable/schema/test files | 6 | 5 |
| Physical maintained lines | 1,002 | 975 |
| Manually supplied binding/leaf fields | 72 top-level updater constants | 54 manifest leaves |
| Projection publication calls | 12 | 1 |
| Controlled procedural retries | 7 | 0 |
| Defect escapes | 7 observed correction opportunities | 0 |
| Hand-copied Git object IDs | required by bespoke updater constants | 0 manifest fields |
| Prevalidation canonical writes | present in two representative updaters | 0 |

The candidate is not intrinsically faster. Across 20 alternating shadow
iterations, one clean latest-legacy apply had a 321.402 ms median, while the
candidate's complete prepare-and-shadow-publication had a 985.012 ms median.
The clockwork pays roughly three times the clean-run cost for full Git, graph,
Compass, latch, journal, digest and generation validation.

The 20-run timing observation is retained here but is not rerun by clean-checkout
admission because the legacy updater depends on historical local-only evidence.

When the seven observed procedural correction cycles are included, the derived
median cycle is 2,571.216 ms for the legacy reference and 985.012 ms for the
candidate, a 61.7% reduction. This estimate is explanatory only: scheduler and
filesystem timing are explicitly non-authoritative. The acceptance rests on
zero escapes, zero partial publication, 100% retry reduction in the controlled
defect suite, preserved coverage and the one-surface / 27-line reduction. The
line reduction is modest and is not treated as sufficient efficiency evidence
on its own.

## DeepSeek gear result

The broker's WorkOrder mode is opt-in and provider-free. With no WorkOrder, all
existing broker tests retain their current event shapes and behavior. With a
valid WorkOrder, ready, request, response and terminal events continue the
transaction journal's sequence and digest chain while binding the same source
commit, operation, transaction and authority digest. The broker also requires
the independently supplied canonical WorkOrder digest; a malformed or drifted
WorkOrder stops before listen/upstream I/O. No occupied Harness, DeepSeek or Gemini call
occurred.

## Claim boundary

This is shadow evidence, not live-control replacement. The shadow report uses
deterministic structural Compass validation; historical evidence-file presence
remains an explicit canonical-adoption gate because the accepted map names
preserved local evidence absent from a clean checkout. It proves a smaller and
more reliable candidate reading mechanism plus shared broker causal time. It
does not prove crash-atomic migration of the independently addressed live
files, occupied native-Harness startup, model performance, product throughput
or production suitability.

No product/configuration/route/database change, ordinary-practice enablement,
generic-status `Arrived`, grammar/client/waiting-area movement, product/patient/
clinical data, provider call, credential/network change, production runtime,
deployment, release, Pages or protected-ref movement occurred.
