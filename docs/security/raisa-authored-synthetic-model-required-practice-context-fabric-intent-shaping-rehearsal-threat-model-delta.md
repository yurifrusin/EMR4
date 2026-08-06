# Threat-model delta: model-required Context Fabric intent shaping

Date: 2026-08-06

Status: frozen authored-synthetic occupied-envelope delta

## Trust boundaries and assets

The provider model, its bytes and every candidate field are untrusted. The host
broker, closed schemas, deterministic intent proofreader, trusted candidate
wrapper, backend authority binding, accepted parent retrieval engine and parent
same-packet proofreader are distinct controls. The occupied cell receives no
product source, database, watcher, credential or command capability.

Protected assets are provider/data-scope integrity, exact model/region/identity
binding, patient and product-data exclusion, intent and temporal grounding,
atomic Bureau authority, minimal disclosure, same-packet provenance, cost/call
ceilings, raw-response non-retention and strict read/command separation.

## Threats and controls

| Threat | Control |
|---|---|
| A synthetic utterance or model output injects identity, tenancy, source or command authority | Provider request and body are closed; all authority fields are exact false; trusted code supplies every candidate authority coordinate. |
| The model becomes a hidden retriever or practice memory | It receives only one synthetic utterance, ontology and coordinate codes; no ContextFrame, source catalog, audit, product identifier, database or retrieval tool crosses the boundary. |
| Brand name grants Bureau authority | Brand is absent from the decision; backend binding independently fixes requesting/contributing Bureau and purpose. |
| Model invents a new intent, coordinate, cue, URL, SQL, tool or free-text instruction | Enum-only closed JSON schema; exactly one non-thought text part; extra fields and unrecognised values block. |
| Plausible but wrong classification selects excessive context | Deterministic authored-case grounding rejects the body; the accepted parent template and binding independently minimise or reject every component. |
| Model selects the parent components or disclosure limits directly | Trusted wrapper derives them from code-owned intent templates and backend maxima; provider body has no such fields. |
| Provider output is resealed after tamper | Request, response, body, candidate, parent packet and both proofreader digests are bound into one release envelope and recomputed. |
| Correction prompt leaks or anchors on the failed candidate | The prior body is discarded; correction carries only the same synthetic input, ontology and safe failure code. |
| Retries or fallback bypass cost/call limits | Immutable single-use attempt ledgers, one parent ledger, maximum two calls/USD 0.50, no fallback and no call after admission. |
| Hidden thinking or raw provider data becomes retained practice memory | Only bounded usage counts and hashes survive; raw prompt/provider text/thought/header/token/credential retention is forbidden. |
| Provider invocation is mistaken for product/API authority | Isolated development Access AI evidence only; no mounted route/import; zero product, database, command or write capability. |
| A context result is promoted into a command | Parent and final envelopes are read-only/no-command; every future command must re-authorise fresh backend truth through its own boundary. |
| Cross-Bureau clinical, prescribing, referral or billing authority leaks through intent shaping | Only the closed Rayleen authored-synthetic case is occupied; every future Bureau and professional command remains independently closed. |

## Residual risks deliberately deferred

Real staff-language variance, adversarial user/provider content, patient and
product-data privacy, production RLS/ABAC, live source retrieval, database
watching, retention/deletion, runtime latency/availability, broader cross-Bureau
intent routing and all clinical or administrative command paths require later
separately frozen descendants.

## Forbidden openings

No patient, clinical, product-derived, financial, protected or historical-PHI
data; no raw audit; no live source/database/session/feed/watcher; no persistence
or retention choice; no external evidence/RAG; no product GraphQL/REST route,
resolver, mutation or subscription; no command/write; no cloud/IAM mutation;
no deployment, production, release, Pages, protected evidence or protected-ref
movement. Preserve and exclude `docs/branding/` and unrelated untracked
artifacts.
