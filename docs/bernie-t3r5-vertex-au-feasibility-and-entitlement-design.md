# Bernie T3R5 Australian Vertex feasibility and entitlement design

Date: 2026-07-18

Owner: GPT Sol

Decision: `blocked_before_provider_call`

## Outcome

An Australian-region Vertex evaluation is technically possible today only by
using the older GA `gemini-2.5-flash` model in Sydney. That model has a
documented retirement date of 2026-10-16, only 90 days after this assessment.
The current general-purpose `gemini-3.5-flash` and economical
`gemini-3.1-flash-lite` successors do not list an Australian location.

T3R5 therefore does **not** recommend enabling Vertex AI, billing the project,
granting prediction access, or making a model call. The appropriate trigger for
reassessment is a current Gemini successor becoming GA in
`australia-southeast1` with at least 180 days of documented runway.

## What was and was not inspected

The assessment used official public Google Cloud documentation and local,
read-only control-plane/configuration observations. It found a configured
development project and keyless impersonated-service-account ADC posture. It
also found Vertex AI disabled, billing disabled, and no explicit project,
Sydney-location, or Vertex-transport environment pins.

No model prompt or response occurred. No access token was generated for a
model call. No cloud resource, API, billing configuration, IAM binding,
organization policy, logging setting, budget, application runtime, database,
route, deployment, or release was changed. No patient, practice, historical,
external-corpus, or protected-holdout material was accessed or transmitted.

The committed evidence deliberately records booleans and the development
project name only; it does not persist account or service-account identifiers.

## Documentary finding

| Candidate | Sydney availability | Lifecycle | Runway from 2026-07-18 | T3R5 result |
|---|---:|---|---:|---|
| `gemini-3.5-flash` | No | GA | at least 305 days | Blocked: no Australian endpoint |
| `gemini-3.1-flash-lite` | No | GA | at least 293 days | Blocked: no Australian endpoint |
| `gemini-2.5-flash` | Yes | GA | 90 days | Blocked: below 180-day floor |

Google states that global endpoints do not provide regional isolation or data
residency compliance. A global alias therefore cannot substitute for Sydney.
For a future eligible model, EMR4 must use the locational
`australia-southeast1-aiplatform.googleapis.com` endpoint and must separately
verify policy enforcement that denies global endpoint use.

## Future entitlement contract

A later, separately authorized synthetic evaluation may become *ready for
approval* only when every item below is verified:

1. A GA successor lists `australia-southeast1`, supports regional isolation,
   and has at least 180 days until documented retirement.
2. The selected project is `bernie-emr4-dev`; billing and Vertex AI are enabled
   under separately approved cost authority.
3. Authentication remains keyless, using impersonated service-account ADC.
4. The environment explicitly pins the project, Sydney location, and Vertex
   transport. Global, US, EU, and non-Australian fallbacks are prohibited.
5. A least-privilege custom role grants prediction only (including
   `aiplatform.endpoints.predict`) and no endpoint administration.
6. Data Access audit logging is enabled and verified. Audit evidence records
   metadata only, never raw synthetic prompts or responses.
7. Vertex request-response logging is confirmed disabled. Grounding, tools,
   explicit caching, and raw prompt/response persistence remain disabled.
8. The applicable abuse-monitoring/retention posture and any required zero-data-
   retention exception are verified before content transmission.
9. Yuri explicitly accepts pricing. A billing budget alert is configured, and
   an application-owned hard sample/token/cost ceiling plus kill switch exists;
   a Google billing budget alone is not a hard cap.
10. The evidence reducer returns
    `ready_for_separately_approved_synthetic_evaluation`. Even that decision
    does not itself authorize a provider call.

The stable API Spine classification remains developer-only Access AI/provider
feasibility. Any future method would bind to capability
`admin.booking.interpret` and method `evaluate_fixture`; no GraphQL or REST
surface, product runtime wiring, database/audit write, appointment or
confirmation authority, deployment, or release is opened here.

## Fail-closed implementation

- `docs/bernie-t3r5-vertex-au-feasibility.json` is the reviewed evidence packet.
- `app/services/ai/evals/bernie_vertex_au_readiness.py` is a pure deterministic
  reducer with no cloud SDK, network, subprocess, FastAPI, database, or product
  runtime import.
- `scripts/bernie_t3r5_vertex_readiness_check.py --check` verifies that the
  committed report exactly matches the evidence.
- `docs/bernie-t3r5-vertex-au-readiness-report.json` is the durable result.

## Official sources checked

- [Gemini 3.5 Flash model card](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-flash)
- [Gemini 3.1 Flash-Lite model card](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-lite)
- [Gemini 2.5 Flash model card](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/2-5-flash)
- [Gemini model lifecycle](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions)
- [Regional endpoint compliance](https://docs.cloud.google.com/docs/security/compliance/about-regional-endpoints)
- [Restrict endpoint usage](https://docs.cloud.google.com/docs/security/compliance/restrict-endpoint-usage)
- [Resource locations](https://docs.cloud.google.com/organization-policy/restrict-locations)
- [Zero data retention](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/zero-data-retention)
- [Request-response logging](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/request-response-logging)
- [Vertex AI audit logging](https://docs.cloud.google.com/gemini-enterprise-agent-platform/machine-learning/general/audit-logging)
- [Vertex AI access control](https://docs.cloud.google.com/gemini-enterprise-agent-platform/machine-learning/general/access-control)
- [Programmatic budget notifications](https://docs.cloud.google.com/billing/docs/how-to/budgets-programmatic-notifications)
- [Dynamic shared quota](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/resources/throughput-quota)
