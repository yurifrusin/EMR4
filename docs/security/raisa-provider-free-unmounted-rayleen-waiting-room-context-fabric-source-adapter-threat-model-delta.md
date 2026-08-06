# Threat-model delta: unmounted Rayleen waiting-room Context Fabric source adapter

Date: 2026-08-06

Status: frozen provider-free authored-synthetic delta

Parent threat surfaces are Rayleen A4 and the accepted Practice Context Fabric
Current operational weave. This delta opens no product route or live source.

| Threat | Control | Fail-closed result |
|---|---|---|
| A caller passes an unauthorised frame directly to the Fabric | Require the exact sealed backend binding and admitted scope grant before payload inspection | `source_scope_not_admitted` |
| A model or client selects practice, location, role, purpose or aliases | Accept only backend-authored sealed binding/grant and alias manifest; candidate authority is absent | `adapter_authority_invalid` |
| Raw patient/source identifiers leak into cross-Bureau context | Complete one-to-one request-scoped aliases; omit patient token/source ids; canonical output leak scan | `raw_identifier_leak` |
| Added A4 fields bypass minimization | Recursive source schema closure and exact excluded-field list | `source_schema_invalid` |
| A source signal is fabricated, orphaned or stale | Recompute elapsed, threshold, exceptions and ranks; bind nested labels to frame coordinates | `source_signal_not_grounded` |
| Missing arrival time becomes a guessed wait | Preserve a closed exception and omit elapsed/threshold | `derived_value_unavailable` without partial invention |
| Context lifetime is extended | Output expiry is the minimum of source, binding, grant and manifest; expired/stale inputs reject | `source_not_current` |
| Cross-practice, cross-location or unrelated aliases are mixed | Exact source UUID and Fabric-ref set equality, binding/grant/session digest checks | `alias_scope_mismatch` |
| Duplicate facts or aliases create ambiguous identity | Enforce unique source and opaque references and bounded cardinality | `duplicate_reference` |
| A partial adapter result is used after failure | Atomic result construction; no envelope returned on exception | no release |
| A caller adds an unknown outer or nested field and recomputes the non-cryptographic seals | Recursively closed result/envelope/payload/entry/trace schema plus full revalidation in the sole deep-copy handoff extractor | `adapter_result_schema_invalid` |
| A caller changes duplicated provenance digests/ids together and recomputes every affected seal | Handoff recomputes the entire expected result from authoritative frame/binding/grant/manifest inputs and requires canonical equality; envelope id/revision also bind the frame-digest suffix | `adapter_result_provenance_mismatch` |
| A narrow grant relies on the parent projector to discard ungranted waiting fields | Adapter entry construction intersects optional waiting fields with the effective grant before sealing; parent projection remains a second minimisation layer | focused narrow-grant exact-shape test |
| The adapter becomes a watcher, database client or command tunnel | Pure module, static fixture, no app-service import, network, database, subprocess, route or command dependency | deterministic/API Spine regression failure |
| A sealed source envelope is treated as present authority or action proof | All-false authority ceiling; future commands must re-authorize and re-read | proofreader blocks command-shaped use |

## Residual closed boundaries

This proof cannot establish safety for real patient/product data, production
identity aliasing, operational secrets, live events/watchers, retention,
historical state, provider prompts, clinical cross-Bureau handoff or commands.
Those remain separate authority and threat-model descendants.
