# Sol Review and Acceptance — Ariadne Sydney Vertex Gemini 2.5 Flash Post-Failure Diagnostic

Date: 2026-07-24
Decision:
`ariadne_vertex_sydney_gemini_25_postfailure_diagnostic_pass`

I accept the provider-blocked diagnosis as a bounded repository-local result.

The diagnostic reconstructs the exact historical provider-request hash and
identifies one concrete contract defect at
`generationConfig.responseSchema.properties.total_tiles.enum[0]`. The exact
request used a JSON integer enum member, while the official Vertex REST
contract, structured-output guidance and installed official v1 protobuf
require enum members to be strings. The complete reconstructed request fails
the official local protobuf parse; changing only that member to a string in a
deep-copied local counterfactual makes the full parse pass.

I accept this as a deterministic defect sufficient to invalidate the retained
request and as the leading explanation for the HTTP 400. I do not accept a
stronger claim that the server named this field historically or that the same
single-field correction would guarantee provider acceptance. The raw provider
message was deliberately discarded, and the counterfactual was not sent.

The historical occupied result and consumed ledger remain immutable. No
request constructor was changed, no ledger was opened, no credential or cloud
state was accessed, no prompt was transmitted, and no provider call, retry or
fallback occurred. Product, database, clinical, patient, command, production,
deployment and release surfaces remained closed under the API Spine boundary.

This review accepts the diagnosis only. Any constructor repair or further
occupied call requires a fresh Yuri decision.
