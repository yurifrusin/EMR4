# Independent Audit — Reception One Bureau Model Text Iterative Retry

## Disposition

`reception_one_bureau_model_text_iterative_retry_pass`

This review reconstructs the sequence from the three external audits, their
distinct ledgers, durable hash chains and the independent post-run residue
check. It does not inspect raw prompts, raw provider responses, credentials or
model reasoning.

## Findings

- Retry 001 consumed one call and failed before the proofreader with the bounded
  reason `schema_invalid`. It released nothing and cleaned up.
- Retry 002 consumed one call, received HTTP 200 from
  `australia-southeast1-aiplatform.googleapis.com` in 1471 ms and failed only
  at four allowlisted prior-step source paths. It released nothing and cleaned
  up.
- Retry 003 consumed one call, received HTTP 200 from the same hostname in
  1435 ms and supplied 1286 prompt, 148 candidate and 1434 total tokens.
- The unchanged deterministic proofreader admitted the five-operator plan with
  no proofreader or wire safe repair and no violation.
- Atomic release contained only the twelve admitted proposal fields. It
  described one authored-synthetic squeeze-in assessment, required human
  selection and confirmation, and recorded `write_performed=false`.
- All three ledgers are consumed. There was no call after the first admitted
  result, no provider or regional fallback and no remaining task container,
  network, image, broker process, token or temporary context.
- Provider, model, project, service account, keyless ADC authentication,
  location and hostname remained identical across the sequence. API-key
  authentication was not used.

The deterministic cost guard uses the official Gemini 2.5 Flash rates of USD
0.15 per million input tokens and USD 0.60 per million no-thinking output
tokens. Even treating every call as the full 65,536-token request ceiling plus
the 1,024-token output ceiling produces a conservative USD 0.0313344 upper
bound, below the USD 1 application ceiling. This is a guard estimate, not a
cloud invoice.

## Evidence boundary

The evidence proves the configured and observed Sydney locational endpoint
path, keyless Bernie impersonation, isolated one-use model composition,
deterministic typed admission and in-memory proposal release for one
authored-synthetic case.

It does not prove Australian physical or sovereign processing, product-data or
clinical-data safety, general model quality, production fitness, user value,
database/API runtime integration, appointment mutation, deployment or release.

The machine-readable analysis is
`orchestration/continuity/reception-one-bureau-model-text-lane/occupied-iterative-retry-independent-audit-analysis.json`.
