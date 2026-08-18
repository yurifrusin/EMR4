# Provider-free shadow clockwork / broker gear rehearsal report

## Result

`revision_required_efficacy_threshold_exceeded`

The provider-free four-event tick was derived and validated but was not published as an accepted private generation because its measured rerun count exceeded the frozen threshold. Ariadne transferred one sequence lease to the broker simulation; the broker returned one terminal result; Ariadne acknowledged its exact digest and recovered the lease. There were no provider calls and no live adoption.

## Efficacy reading

- Conventional failure-induced reruns: 14
- Candidate failure-induced reruns: 9
- Reduction: 35.714%
- Frozen gauges covered: 14/14
- Caller-supplied derived fields: 0
- New mutable-current fixtures: 0
- Partial publications: 0
- Uncaught escapes: 0
- Coverage loss: false
- Raw shared line growth: 1552
- Median clean-run overhead: 103.153 ms (diagnostic only)

Every one of the fourteen comparator failures was injected as an immutable malformed prospective reading and rejected in its owning phase before publication. These rejections preserve coverage and do not count as execution reruns.

## Causal binding

- Source commit: `159301c3ef84c3f274971df9ef0776312b99f7af`
- Acknowledged tip: `d407d9e881b3d10c2dd745466b3d1e6ae9e5c6a8b994069df98332b55edfe415`
- Authoritative generation digest: `7634d82d419901b8d071354bbde9454ac9813fb48fbe79d9af8ad163f4befb11`
- Provider calls: 0
- Published files: 0

Timing is excluded from the authoritative generation digest and from acceptance.

## Boundary

The accepted architecture and current controls remain unchanged. No occupied DeepSeek Harness, HMR retry, provider, product/practice surface, data, runtime, deployment, release, Pages, protected evidence or protected-ref movement was exercised or authorised.
