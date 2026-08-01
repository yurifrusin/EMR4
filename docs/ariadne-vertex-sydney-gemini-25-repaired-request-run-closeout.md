# Ariadne Sydney Vertex Gemini 2.5 Flash iterative repaired-run closeout

## Result

Terminal result:
`ariadne_vertex_sydney_gemini_25_occupied_rehearsal_pass`.

One bounded authored-synthetic request reached `gemini-2.5-flash` through the
Sydney Vertex locational endpoint and returned a typed response. The
deterministic proofreader admitted and atomically released exactly four
grounded fields. The successful ledger is consumed, no call followed success,
no fallback occurred, and task-scoped cleanup is complete.

## Diagnosis and repairs

1. The historical INTEGER enum member encoded as JSON number `5` was proved
   invalid and first repaired to string `"5"`. That full request parsed the
   official local Vertex protobuf but the first repaired occupied call still
   returned bounded HTTP 400 before a candidate.
2. Official structured-output guidance says only string enums are supported.
   The second request therefore removed the enum from the INTEGER field and
   used exact numeric `minimum: 5` and `maximum: 5`. The deterministic
   proofreader continued to require integer `5`, so the release contract was
   not weakened.
3. The first provider-free run for that repair failed before broker contact
   because the relay process was running before its listener was ready. Its
   zero-call ledger was consumed and residue cleared.
4. A connection-refused-only pre-connect retry repaired the readiness race.
   It cannot replay once a connection is established. Focused regression tests
   and the next distinct provider-free lifecycle passed.

## Successful occupied attempt

- Attempt: `gemini-25-repair-002`
- Ledger: `gemini-25-repair-ledger-002` — consumed, one call
- Provider/model: Google Vertex AI / `gemini-2.5-flash`
- Project: `bernie-emr4-dev`
- Identity:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`
- Authentication: `keyless_impersonated_service_account_adc`
- Region: `australia-southeast1`
- Host: `australia-southeast1-aiplatform.googleapis.com`
- HTTP status: 200
- Latency: 1108 ms
- Token usage: 176 prompt, 50 candidate, 226 total
- Successful-call usage estimate under the frozen application prices:
  USD 0.0000564; actual provider billing was not supplied
- Fallback, API-key authentication and provider tools: none

The request hash was
`sha256:784a68a5d4f45d62d2dbe8ab3b0388585d5938abdb8185ead99952eb41375357`
and the provider-schema hash was
`sha256:21a2208ab1dc4b73f6134bd378eb532a6b5c974e822985e23c5aa7ecc5d37621`.
The eight-event audit chain terminates at
`sha256:763b600bdfdb69af25347f1b0e2b66acb1c7f796a7fc438fd5a353c8538db8ec`.

## Proofreader and release

The exact schema, field paths, types, authored-synthetic grounding, command
absence, model/project/region binding, freshness and supersession checks
passed. No safe repair was needed. The atomic authored-synthetic release was:

```json
{
  "summary": "Project Lark has 5 tiles: 3 blue and 2 green.",
  "total_tiles": 5,
  "risk_level": "none",
  "evidence_ids": ["fact_alpha", "fact_beta"]
}
```

No draft, raw prompt, raw provider response, credential, token, API-key
information, hidden reasoning or chain-of-thought was retained.

## Controls and cleanup

The same-session Tranche 3 evidence verifies the exact impersonated ADC,
project, target service account, cloud-platform scope, prediction-only custom
role and `aiplatform.endpoints.predict` permission, Vertex AI API/billing
entitlement, Vertex Data Access audit logging, disabled/absent request-response
logging, explicit project cache disablement, zero user-managed
service-account keys, current Sydney model catalogue and exact regional
endpoint. It made no inference call and changed no external state.

Every opened repair-run ledger is consumed: three provider-free ledgers and two
occupied ledgers. Across the wider immutable lineage, three occupied calls were
made: the original primary, repaired attempt 001, and successful repaired
attempt 002. No blind identical retry or fallback occurred.

Independent post-run checks found zero task containers, networks, images,
broker processes, temporary tokens, contexts or roots. No daemon-wide prune
was used. Three unrelated pre-existing repository-local development servers
were preserved unchanged.

## What the evidence proves

It proves one small authored-synthetic typed request was accepted and answered
through the configured Sydney Vertex locational endpoint using the verified
keyless Bernie impersonated-ADC boundary. It proves deterministic four-field
release, single-use accounting, no post-success call, no fallback, and complete
task-scoped cleanup.

## What it does not prove

It does not prove Australian physical or sovereign processing, provider
internals, exact provider billing, general model reliability, production
suitability, or safety for product-derived, patient, health, clinical or
historical data. The configured locational endpoint, observed request path and
Google's published contract are the maximum residency evidence. The container
constrains local capabilities and credential exposure; it does not determine
the remote provider's processing geography.

## Final disposition

The external audit and separate repository-only audit analysis pass. The
descendant closes on success at Continuity graph revision 49 and Compass map
revision 36. No product, database, clinical, patient, command, production,
deployment, release, protected-ref, commit, push or external-worker authority
was used or created.
