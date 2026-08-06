# Threat-model delta: Context Fabric intent-shaped temporal retrieval rehearsal

Date: 2026-08-06

Status: bounded provider-free design delta

## Trust boundaries and assets

The intent candidate and every upstream data-shaped object are untrusted until
their seals and accepted proofreader results pass. Backend authority binding,
closed intent templates, deterministic selection and same-packet proofreading
are separate controls. No provider, live source, database, watcher, API or
command service exists in this tranche.

Protected assets are practice/principal/session isolation, atomic Bureau
capabilities, purpose limitation, private-session containment, current-truth
freshness, bitemporal integrity, minimal disclosure, provenance and the strict
read/command separation.

## Threats and controls

| Threat | Control |
|---|---|
| Brand or screen is treated as authority | Workspace names are absent from the authority decision; only exact backend Bureau/purpose/capability grants admit a component. |
| Candidate injects tenant, role, location, retention or authority | Closed candidate rejects these fields; binding is separately sealed and backend-owned. |
| Intent text becomes an unbounded query | Closed intent codes and field profiles only; no free text, SQL, vector query, prompt or arbitrary selector. |
| Vocabulary case mismatch widens scope | Explicit per-component canonical mapping; no implicit case folding or guessed alias. |
| Current coherence is weakened by selecting convenient sources | Accepted four-source Current weave is one atomic component; only fields narrow. |
| Cross-Bureau request leaks private session narrative | Private-session component is non-shareable; bilateral Bureau/purpose grant is required for every shareable recent-work component. |
| A historical snapshot is asserted as current truth | Distinct component and constant `current_truth_authority: false`; Current use also requires a non-invalidated parent set. |
| Missing history is interpreted as no event | `NO_COVERAGE`/gap remains explicit and prevents an absence claim. |
| Ambiguous opaque matches are silently resolved | Equal matches produce bounded canonical `ALTERNATIVES` and a discriminator request; no identity assertion. |
| Stale state is released during an interaction | Expiry, supersession, session generation and temporal lifecycle state are rechecked immediately before proofreader release. |
| Resealed output hides over-disclosure or provenance substitution | Proofreader independently reconstructs plan, projection, digest tree and limits from the same packet. |
| Context is promoted to command authority | Every object is read-only/no-command; no command API/import exists and a later command must re-authorise against fresh backend truth. |
| Rejection leaks cross-tenant/Bureau counts | Uniform `NOT_AVAILABLE` with no rejected counts or source details. |
| Clinical, prescribing, referral or billing authority leaks through interweaving | Context composition grants no professional or command capability; each future Bureau retains an independent capability and command gate. |

## Residual risks deliberately deferred

Natural-language intent classification, provider prompt construction, real
identity and patient-data privacy, production RLS/ABAC, live source retrieval,
watcher/outbox guarantees, retention/deletion, clinical evidence licensing,
cross-Bureau clinical handoffs, runtime load and every command path require
separately authorised descendants.

## Forbidden openings

No patient, clinical, product-derived, financial or protected data; no raw
audit; no provider or external retrieval; no live database/session/feed/listener
or source reader; no persistence or retention choice; no GraphQL/REST route,
resolver, mutation or subscription; no command/write; no product runtime; no
deployment, production, release, Pages, protected evidence or protected-ref
movement. Preserve and exclude `docs/branding/` and unrelated untracked
artifacts.
