# Native Harness corrected-runner boot proof

Date: 2026-08-22

Timestamp: 2026-08-22T21:03:29.4171606+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

The new DeepSeek Harness has now passed the last provider-free boot test that
was actually needed. Its ordinary stock headless launcher reached our corrected
controlled runner once, produced exactly the reading predicted by the preceding
diagnosis, and shut down cleanly. It did not contact DeepSeek or any other
provider, and there was no retry.

This means we are no longer justified in doing more generic Harness boot work.
The next test must let DeepSeek attempt one small, wholly synthetic development
job and judge whether the result is useful, traceable and cheap to correct.
That is the point at which the Harness starts serving Raisa development rather
than proving its own machinery.

The surrounding bureaucracy still exposed twelve small technical corrections,
but the clockwork caught all of them without wasting another Harness process or
provider call. I have retained those costs rather than hiding them, so we can
judge whether the workflow is genuinely becoming more efficient.

## Technical summary

- exact rc.7 stock-headless processes: 1;
- HMR mutations: 1;
- distinct preset roots / root reads / hooks: 2 / 4 / 5;
- accepted coordinate: `EFFECTIVE_TOOL_COMPOSITION_PASSED`;
- runner stop: controlled `failed/factory` before request;
- stock exit: 0 after 5,874 ms;
- target, agent publication, session, turn, broker, worker, model, provider,
  network, database and Docker counts: all zero;
- retry/resume/fallback: all zero; and
- process/root cleanup and canonical source/package-seed immutability: passed.

The exact passing evidence source is
`f0f8e59ebd70da5167edf907c9ece26049cdcf1c`.

## Deliberately closed

No product or real data, ordinary-practice change, product source mutation,
production runtime, deployment, release, Pages or protected-ref movement is
opened by this proof.

## Next tranche

Freeze and, only after deterministic preexecution admission, run one distinct
authored-synthetic corrected-guard-graph DeepSeek development recovery attempt.
It will have one exact work order, explicit owned paths, at most one prepaid
provider request, no Claude Code fallback, typed candidate/failure outputs and
measured useful-output, traceability and correction cost. Your attention is not
required under the standing authority.
