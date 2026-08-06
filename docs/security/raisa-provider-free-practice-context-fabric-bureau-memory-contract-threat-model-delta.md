# Threat-model delta: provider-free Context Fabric and Bureau Memory Bank contract

Date: 2026-08-06

Status: bounded design/implementation delta

## Assets and trust boundaries

Protected assets are tenant and role scope, principal identity, source and field
policy, temporal limits, frame contents, provenance, expiry and command
separation. The candidate is untrusted. Authority binding and policy are
trusted backend inputs. Authored-synthetic item fixtures are untrusted until
schema and policy admission. The proofreader is deterministic and separate
from the requester.

## Threats and controls

| Threat | Control |
|---|---|
| Candidate claims a principal, practice, role or retention | Those fields are absent from the closed candidate schema; backend binding is independently digested. |
| Scope widening or cross-tenant inference | Stable set intersection, half-open time clipping, minimum bounds and generic `NOT_AVAILABLE`. |
| Raw audit becomes model memory | Memory items expose a closed minimal projection only; prompts, responses, payloads, actor ids, database keys and command material are schema-forbidden. |
| Historical item masquerades as current truth | Source is fixed to `recent_collective_work`; authority is fixed to `read_context_only`; proofreader rejects current-truth or command claims. |
| Stale, expired or superseded frame release | Caller-supplied deterministic clock, source/grant/binding expiry minima and supersession checks. |
| Digest substitution between Bureau and proofreader | Exact need, grant, selector, weave and frame-set digest recomputation. |
| Cardinality/count side channel | Backend cap, deterministic truncation and uniform external denial shape without hidden counts. |
| GraphQL becomes a command or audit-search API | One candidate-only read field; no mutation, subscription, standalone memory query, resolver or authority input. |
| Hidden I/O or runtime wiring | Pure standard-library module plus static import/call checks and zero-side-effect evidence. |

## Residual risks deliberately deferred

Real identity resolution, data classification, RLS, production retention,
bitemporal persistence, audit-projection generation, product integration,
provider prompt minimisation and clinical source governance need separately
authorised descendants. This contract contains no patient or product data and
cannot validate those controls.

## Forbidden openings

No provider call, external retrieval, raw audit access, product import,
database, persistence, filesystem write, subprocess, network, command, runtime
route, deployment, production, release, Pages, protected evidence or
protected-ref movement. Preserve and exclude `docs/branding/`.
