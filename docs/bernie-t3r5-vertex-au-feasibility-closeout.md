# Bernie T3R5 Australian Vertex Feasibility Closeout

Date: 2026-07-18

Decision: `blocked_before_provider_call`

## Outcome

The user-authorized no-call Australian-region Gemini/Vertex feasibility and
entitlement design is complete. No current long-lived Gemini successor is
eligible for the proposed Sydney evaluation:

- `gemini-3.5-flash` and `gemini-3.1-flash-lite` are GA but do not list
  `australia-southeast1` availability; and
- `gemini-2.5-flash` lists Sydney but its documented 2026-10-16 retirement is
  only 90 days after assessment, below the 180-day stability floor.

The legacy model makes an Australian route technically possible, but the short
runway makes it a poor foundation for Bernie. The recommended trigger is a
fresh no-call assessment when a current Gemini successor becomes GA in Sydney.

## Local entitlement posture

Read-only checks found a configured `bernie-emr4-dev` project and keyless
impersonated-service-account ADC. They also found billing and the Vertex AI API
disabled, with no explicit project, Sydney-location, or Vertex-transport
environment pins. Sensitive control evidence remains unverified: least-
privilege prediction IAM, Data Access auditing, disabled request-response
logging, Australian organization policies, global-endpoint denial, retention,
disabled grounding/tools, cost approval, budget alerts, and an application
hard limit/kill switch.

No cloud setting was changed. No model call, access-token generation for a
model request, prompt, response, or content transmission occurred. Durable
evidence contains no account or service-account identifier.

## Fail-closed contract

The pure reducer accepts reviewed documentary/local evidence and requires all
model, entitlement, privacy, audit, regional-isolation, and cost controls. It
imports no cloud SDK, network client, subprocess, product runtime, route, or
database surface. The committed result is deterministic and blocked.

Even a hypothetical fully verified long-lived Sydney successor produces only
`ready_for_separately_approved_synthetic_evaluation` with
`authorizes_provider_call: false`. A new explicit user decision would still be
required for its exact model, retention posture, budget, and bounded prompt.

## Verification

- focused and preservation tests: 71 passed;
- committed-report check: passed;
- evidence file SHA-256:
  `37ab88b2c9c660cbf7793a199d86d32c048a6c3f87eb5d3cf494e37c92fc8add`;
- report file SHA-256:
  `628b631bfdcf117ab5c8df2fda9cc88ac452775daa971697b1ae99792e49d37d`;
- internal report hash:
  `sha256:c19a713ca4819319bcb380284cf4e6df74e4ef2c59c239f8138da17c805d57f2`;
- provider model calls: zero;
- cloud mutations: zero; and
- API Spine classification: developer-only Access AI/provider feasibility.

Protected holdouts v1-v10, historical diary material, external corpora,
patient/practice data, T3.5, product runtime, GraphQL/REST, database/audit
writes, appointment/confirmation authority, deployment, release, and write
authority remain closed.
