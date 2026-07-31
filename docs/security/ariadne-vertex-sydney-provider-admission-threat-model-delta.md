# Threat-Model Delta — Ariadne Sydney Vertex Provider Admission

Date: 2026-07-24
Scope: Tranche 1 documentary admission only
Result: blocked before credential, cloud or provider access

## Boundary

This delta covers the decision that precedes any launcher, broker, ADC,
container or provider activity. The assets are the frozen provider/model/
project/identity/region contract, authored-synthetic classification, call and
cost ceilings, historical evidence integrity, and the accuracy of residency
claims.

## Threats and controls

| Threat | Failure mode | Control |
|---|---|---|
| Endpoint-existence laundering | Treating the Sydney Vertex service hostname as proof that a named model is served there | Require the exact per-model location matrix and model card; endpoint existence is recorded separately and never satisfies model admission |
| Region-name confusion | Confusing `asia-southeast1` (Singapore) with `australia-southeast1` (Sydney) | Exact string binding and negative tests; aliases, prefixes and “Asia Pacific” summaries cannot substitute |
| Missing-table-cell misread | Losing supported/unsupported icons during text extraction | Independently inspect the official HTML table cell order and record the Australia cell explicitly as unsupported |
| Stale documentary evidence | Relying on the 2026-07-18 T3R5 report after provider documentation changes | Bind current official URLs and their displayed update dates in a fresh observation; historical T3R5 remains context only |
| Model or provider substitution | Falling back to another Gemini, region, Developer API, OpenAI, Terra or DeepSeek | Explicit fail-closed rejected-route set and exact model-family rule; unsupported Sydney status stops for Yuri |
| Global or cross-region fallback | SDK or service retries through `global`, `us`, `eu` or another region | Global and automatic fallback are policy rejections; no request constructor or client is opened after the documentary failure |
| Premature credential exposure | Inspecting ADC or refreshing a token even though the model-location gate already failed | Tranche order is enforced; Tranche 3 remains unopened and evidence records zero credential, token and cloud-control actions |
| API-key leakage | Reading key presence or values while proving the no-key boundary | No environment inspection occurs; the admission validator has no environment or cloud imports and records only that no API-key path is authorised |
| Residency overclaim | Describing a locational endpoint as independently observed physical or sovereign processing | Claims are limited to provider-contractual country-jurisdiction processing when a model is supported and a request is observed; physical and sovereign claims are prohibited |
| Training/retention conflation | Treating the training restriction as zero retention | Training restriction, abuse-monitoring retention and request-response logging are separate policy fields; no zero-retention claim is admitted |
| Container-geography conflation | Claiming local isolation determines the provider's remote processing location | Policy states that a container constrains local capabilities only |
| Historical-evidence rewrite | Updating consumed Terra/Gemini nodes to fit the new route | New descendant only; attempts 001-004 and their ledgers remain immutable |
| Authority carry-forward | Treating unused call ceiling as deferred authority after a failed predecessor gate | The failed sequence closes with zero calls consumed and zero calls remaining under this closed sequence |

## Residual risk

Provider documentation can change after this observation. A future Yuri
decision may authorise a fresh documentary recheck, but this result cannot be
silently promoted. Even future documentary Sydney support would not prove
project entitlement, ADC usability, audit posture, provider acceptance,
inference location or output safety; those later gates would still be required.

No credential, cloud-control, network, container or provider evidence is
present in this tranche.
