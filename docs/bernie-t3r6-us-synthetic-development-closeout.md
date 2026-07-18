# Bernie T3R6 US Synthetic-Development Policy Closeout

Date: 2026-07-18

Policy decision: `accepted_us_synthetic_development_after_au_2_5_retirement`

Current readiness: `us_synthetic_development_path_scheduled_not_call_ready`

## Outcome

Yuri's development/production residency distinction is now durable and
machine-checked. From 2026-10-16, synthetic-only Bernie development may use a
location-controlled Vertex `us` multi-region path. Production or any PII use
remains Australian-only and cannot be reviewed before 2027 at the earliest.

Gemini 3.5 Flash is currently a suitable *model candidate* for that future US
development lane: it is GA, lists model availability and ML processing in
`us`, supports data-residency controls, and has 215 days of documented runway
on the transition date. This corrects T3R5's wait-for-Sydney recommendation
without altering its historical evidence.

## Preserved gates

The lane is synthetic development only. It excludes patient/practice data,
PII, protected holdouts, historical diary material, external corpora, raw
prompt/response persistence, grounding, tools, explicit caching, product
runtime inputs, routes, database/audit writes, appointments, confirmations,
deployment, release, and write authority.

No automatic regional fallback is allowed. Development must pin `us`;
production must later pass a fresh Australian model, privacy, security,
entitlement, and release review. Development configuration cannot be promoted
to production.

T3R6 authorizes no model call or cloud mutation. Even a fully verified future
report returns only `ready_for_separate_us_synthetic_provider_call_approval`
with `authorizes_provider_call: false`. Exact model, retention, bounded
synthetic prompt/corpus, and budget approval remain Yuri decisions.

## Verification

- focused and preservation suite: 89 passed;
- committed-report check: passed;
- policy evidence SHA-256:
  `fe818a2ba86235923740c4e60cf2a6b57ad7c8deb843ba1dcf2334b285906a2b`;
- report file SHA-256:
  `26de56de961fe189e417954c5247572facaab559a51e44be5ca46f415aef7f5d`;
- internal report hash:
  `sha256:7f3aac1d92a4200221c0b41bc70f496de4639cad93ff413cd79ef04d6a61f996`;
- provider model calls: zero; and
- cloud mutations: zero.

API Spine classification remains developer-only synthetic Access AI/provider
feasibility. T3.5 and the product live-provider gate remain closed.
