# Ariadne Sydney Vertex Gemini 2.5 Flash — Post-Failure Diagnostic Closeout

Date: 2026-07-24
Owner: GPT Sol
Result:
`ariadne_vertex_sydney_gemini_25_postfailure_diagnostic_pass`

## Outcome

The provider-blocked diagnosis establishes one deterministic defect in the
exact retained occupied request:

`generationConfig.responseSchema.properties.total_tiles.enum[0]`

The request encoded that enum member as JSON integer `5`. The current official
Vertex `Schema` contract defines `enum[]` as repeated strings and the current
structured-output guidance states that only string enum values are supported.
The installed official Vertex v1 protobuf likewise exposes the field as a
repeated string.

The local constructor reproduced the immutable provider-request hash exactly:

`sha256:6710af194aba6a2731008475e5509fa27ba12c8b58e995e1952faa036ecba61c`

Parsing that complete reconstructed request through the installed official
Vertex `GenerateContentRequest` protobuf failed. A deep-copied, in-memory
counterfactual that changed only the enum representation from integer `5` to
string `"5"` parsed completely. The counterfactual was not transmitted and
the repository request constructor was not changed.

This is a proved request-contract defect and is sufficient to make the exact
retained request invalid. It is therefore the leading deterministic
explanation for the bounded HTTP 400 `INVALID_ARGUMENT`.

## Historical and causal limits

The occupied rehearsal and its consumed ledger remain unchanged as
`ariadne_vertex_sydney_gemini_25_occupied_rehearsal_revision_required`.

The bounded provider-error policy deliberately discarded the raw provider
message. Consequently, this diagnosis cannot prove which field the historical
server response named, and it cannot prove that correcting this field would
eliminate every later provider or model validation. The local counterfactual
proves contract parsing only; it does not prove provider acceptance,
inference, model output or a successful future call.

The method, fully qualified publisher-model path, retained top-level body
shape, JSON response-schema pairing and Gemini 2.5 Flash thinking budget zero
were checked against current official contracts and are not the identified
defect. No provider tool or cached-content field was present.

## Authority and operations

The diagnosis performed:

- zero credential discovery, access-token refresh or API-key operations;
- zero cloud-control or authenticated metadata reads;
- zero provider or model calls;
- zero prompt transmissions;
- zero occupied-ledger openings;
- zero request-constructor changes;
- zero retries or fallbacks; and
- zero product, database, clinical, patient, command, production, deployment
  or release operations.

The API Spine remains closed. No command, clinical truth, diary truth,
database write or product-facing release path was opened.

## What the evidence proves

It proves that the exact retained request hash can be reconstructed locally,
that its numeric enum member violates the official Vertex schema type
contract, that the complete official local protobuf parser rejects it, and
that the one-field string counterfactual parses locally.

It does not prove the server's exact historical diagnostic wording, provider
acceptance of a corrected request, successful inference, model quality,
Australian physical processing or sovereign processing. The closed rehearsal
still proves only the configured and observed Sydney locational request path
and the previously recorded local control posture.

## Continuing gate

This diagnostic authority is consumed. It does not revive the earlier
conditional retry or convert the unused numerical call ceiling into authority.
Any request-constructor repair, regression intended for a future wire request,
new occupied ledger, further Vertex call, broader error disclosure or changed
provider/model/project/identity/region/credential boundary requires a fresh
Yuri decision.

No commit, push, pull request, protected-ref movement, deployment or release
was performed.
