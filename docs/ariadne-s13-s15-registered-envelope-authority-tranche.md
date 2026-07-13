# Ariadne S13-S15 Registered Envelope Authority Hardening

Status: S13 approved for staging execution; S14-S15 closed pending Sol
authorization of the exact S13 protected-master manifest.

## Direction

Known Bernie capability names already declare an authority tier and permitted
authors, but internal Diary envelopes do not enforce that declaration. This
tranche adds deterministic, non-route enforcement for registered names only.
Unknown free-string names remain compatible with existing generic envelopes.

## Sprints

| Sprint | Scope | Dependency | Allocation |
| --- | --- | --- | --- |
| S13 | Enforce registered action author and envelope-tier compatibility in the pure Diary contract layer. | Sol authorization of this tranche. | One DeepSeek 4 Flash/high worker through detached Deep Code PTY. |
| S14 | Cross-contract alias/tier adversarial hardening. | Accepted S13 staging result and new Sol authorization. | Gemini 3.5 Flash via Antigravity. |
| S15 | Deterministic final acceptance and process measurement. | Accepted S13-S14 staging results and new Sol authorization. | Terra; no extra worker unless evidence conflicts. |

## API Steward Classification

S13 is an internal capability/authority-contract hardening, not a GraphQL
read-model change, REST/OpenAPI command change, async contract, provider
boundary, or client surface. It preserves the API Spine: GraphQL remains
read-only; appointment writes remain typed REST proposal/confirmation commands
with existing idempotency, confirmation, freshness, revalidation, and audit
boundaries. The change adds no command, endpoint, schema/database change,
runtime provider call, or write authority.

## Closed Gates

Terminal-to-active policy remains user-owned. Provider/live-provider,
schema/database, deployment/release, external patient client, H15/H-series,
historical trove, memory/RAG/GraphRAG, GraphQL mutation, UI delivery, new
confirmation action, route wiring, and new write authority remain closed.

## Metrics Baseline

S13 starts at zero for Sol interventions, Terra corrections, worker retries,
stalls, marker corrections, lifecycle defects, consultations, invalid
integrations, manifest variances, and duplicated-context events. One DeepSeek
Flash worker launch is planned; DeepSeek Pro, Claude, Gemini, and a verifier
are omitted because S13 has one bounded pure-domain implementation surface and
no ambiguity, scope change, or independent-risk trigger.

Durations are advisory and come only from durable receipt/commit timestamps.
The closeout records coordination-artifact versus product/test line counts,
focused/API-Spine test results, and final correction work. The prior S10-S12
comparison baseline is three Sol escalations, one S10 retry, two S11
recoveries, four S12 attempts/corrections, zero invalid integrations, and zero
duplicated-context events.
