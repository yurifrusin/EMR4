# T3R3 Three-Lane Transport Preflight — Sol Acceptance

Date: 2026-07-18

Decision: `accepted_no_call_preflight_live_blocked`

## Accepted scope

Sol accepts the DeepSeek three-lane amendment, revised hard ceilings, static
transport profiles, closed normalization schema, pre-dispatch kill switch,
policy-source retention review, and exact no-call report.

This acceptance does not approve any model prompt, live adapter execution,
provider account/data-control posture, API billing, agentic-subscription
methodology, provider tool, runtime route, raw-response retention, promotion,
database/audit/appointment write, confirmation, deployment, or release.

## Evidence

- frozen selection:
  `sha256:7871dff782747c9aadf42aaed840b21981a37410c52862329a9e99380d31ea0e`;
- preflight report:
  `sha256:3f111b990e253c1471673222096cda063f60328b6b24c6f8f2981c43a7468c07`;
- lanes: three; maximum samples: 144; per-lane token ceiling when available:
  250,000; total token ceiling: 750,000;
- adapter-contract-ready lanes: one, DeepSeek only;
- execution-ready lanes: zero;
- focused verification: 35/35; preservation gate: 39/39;
- provider calls and prompts: zero; and
- API-spine boundary: static evaluation preflight only, with no command/read
  graph, runtime, provider-tool, audit, or write surface.

## Required decision

Yuri must choose strict API comparability versus a deliberately labelled
agentic-subscription systems comparison. A strict three-model comparison needs
new GPT and Gemini API access/billing. The subscription option retains
unresolved host-tool and Antigravity audit/persistence limitations and cannot be
reported as a pure-model comparison. DeepSeek's documented mainland-China
storage/retention/cache posture requires separate explicit acceptance.

The T3 live gate remains `blocked`; no execution sprint is authorized by this
acceptance.
