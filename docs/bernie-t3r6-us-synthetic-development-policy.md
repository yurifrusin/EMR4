# Bernie T3R6 US synthetic-development residency policy

Date: 2026-07-18

Decision: `accepted_us_synthetic_development_after_au_2_5_retirement`

## User decision and corrected direction

Yuri determined that Australian data residency is not necessary for the
current synthetic development phase because EMR4 is not expected to use PII in
production before 2027 at the earliest. Synthetic Bernie development may
therefore continue through a location-controlled US Vertex path from
2026-10-16, the documented retirement date of the Australian Gemini 2.5 Flash
path.

This supersedes T3R5's recommendation to wait for a current Gemini successor in
Sydney, but it does not invalidate T3R5's documentary or local entitlement
evidence. T3R5 remains the record of why a long-lived Sydney path was not
available on 2026-07-18.

## Two trust zones

| Surface | Allowed location | Allowed data | Earliest boundary |
|---|---|---|---|
| Development evaluation | Vertex `us` multi-region | Deliberately synthetic development evidence only | 2026-10-16 |
| Production or any PII | `australia-southeast1` after fresh review | Only data explicitly approved under later privacy/security gates | 2027 review at earliest |

The US development lane excludes patient and practice data, historical diary
material, protected holdouts, external corpora, raw prompt/response
persistence, grounding, provider tools, product runtime inputs, and any
database, appointment, confirmation, deployment, release, or write authority.

There is no automatic location fallback. Development configuration must pin
`us`; production configuration must independently pin an approved Australian
location. A deployment cannot inherit or promote the development provider
configuration.

## Documentary basis

Google's current Gemini 3.5 Flash model card lists model availability and ML
processing in the `us` multi-region, data-residency security controls, GA
status, and retirement on 2027-05-19 or later. On the T3R6 transition date it
has 215 days of documented runway, above the 180-day floor.

The policy deliberately uses the `us` multi-region, not the global endpoint.
Global processing is not an acceptable substitute for a location-controlled
US path.

## What this policy authorizes

T3R6 authorizes the *policy direction* and future no-call readiness work. It
does not authorize a Vertex model call, API or billing enablement, IAM changes,
cost acceptance, prompt transmission, T3.5 adapter, runtime route, or cloud
mutation.

After 2026-10-16, the deterministic gate may reach
`ready_for_separate_us_synthetic_provider_call_approval` only if all of the
following have been independently verified:

1. a current GA model is location-controlled in `us` with at least 180 days of
   documented runway;
2. Vertex AI and billing/cost acceptance are explicitly approved;
3. keyless, prediction-only IAM and an explicit US location pin are verified;
4. global and non-US fallback is denied;
5. Data Access audit logging is enabled and request-response logging is
   disabled;
6. retention and abuse-monitoring posture is accepted;
7. grounding, tools, and explicit caching are disabled; and
8. an application hard sample/token/cost ceiling and kill switch are verified.

Even that result has `authorizes_provider_call: false`. Yuri must still approve
the exact model, retention posture, bounded synthetic prompt/corpus, and budget
before any call.

## API Spine boundary

Classification remains developer-only synthetic Access AI/provider
feasibility. The stable capability is `admin.booking.interpret` and the method
is `evaluate_fixture`. Frontends do not call Vertex; no GraphQL/REST route,
runtime provider adapter, audit/database write, product entitlement,
appointment/confirmation authority, deployment, or release is opened.

## Official sources

- [Gemini 3.5 Flash model card](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-flash)
- [Gemini 2.5 Flash model card](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/2-5-flash)
- [Regional and multi-regional endpoint compliance](https://docs.cloud.google.com/docs/security/compliance/about-regional-endpoints)
