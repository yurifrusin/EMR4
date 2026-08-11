# Sol rejection: AES-C2 DeepSeek blue candidate

Date: 2026-08-11

Decision: `revision_required`

Candidate: `52f1dbb10fd6e616d3190aa896e60d8facf5897d`

Source: `bd11333d462424b40f5f8f014b1c4a945b3a5133`

Worker branch: `codex/aes-c2-blue-deepseek`

## Exact findings

The clean seven-path worker candidate is not accepted. An instrumented Sol probe
replaced the sole pure adapter with a counting wrapper and evaluated the frozen
malformed-result scenario. The candidate reported one invocation but the actual
call count was zero because `adapter_result_override` returned before the pure
adapter. A separate schema-valid result override produced a released
`simulated` result with reported one and actual zero calls. An additional
top-level scenario-packet field also returned no validation error.

The worker closeout consequently misreports three actual pure calls, incorrectly
claims all 15 acceptance criteria are complete before Sol and Gemini acceptance,
does not name the exact final candidate commit or all four protected refs, and
says only a digest comparison observes the synthetic fixture although the
frozen plan intentionally supplies that fixture directly to the pure adapter.

## Bounded revision

The defect is a contained implementation-and-evidence closure error under the
already frozen plan, so the plan's single mechanical same-lane revision applies.
The revision must:

- call the fixed pure adapter before observing the exact malformed-result seam;
- instrument and assert actual calls, not just a reported counter;
- reject open or noncanonical scenario packets;
- add regressions for a schema-valid override and an added packet field;
- regenerate exact evidence; and
- correct the candidate, protected-ref, fixture and pending-acceptance closeout
  claims.

Any failed revision or conceptual authority/custody change ends the DeepSeek
correction lane and moves recovery to Sol. No protected evidence, patient or
product data, provider, real credential, runtime, real adapter, network,
database/source, executable, command, deployment, release, Pages or protected
ref is opened by this rejection or revision.
