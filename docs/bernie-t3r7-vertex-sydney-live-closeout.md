# Bernie T3R7 Vertex Sydney Live Pilot Closeout

Date: 2026-07-18

Decision: `pilot_stopped_on_consumed_failure`

## Outcome

Yuri authorized an exact, synthetic-only Vertex pilot using
`gemini-2.5-flash` at the `australia-southeast1` Sydney regional endpoint.
The frozen population was 24 existing Silver v2 cases with two observations
per case and at most 48 calls. The implementation enforced a ten-second
minimum start interval (six calls per minute), one attempt per observation,
no automatic retries, mechanically disabled tools, and a USD 1 application
hard stop.

The run consumed 11 calls. Calls 1-10 succeeded. Call 11 returned provider
text but no JSON object that satisfied the normalized Bernie response schema.
It was recorded as `parse_error` with safe code
`normalized_response_parse_or_schema_failure`. The runner stopped immediately,
did not retry the consumed case, and did not send calls 12-48. Thirty-seven
authorized calls therefore remain unused, not deferred or implicitly
authorized.

## Eleventh-call limitation

The affected Silver case was
`t3r1_sol_v2_bernie_noise_seed_v2_041_01`: a medium-noise, ellipsis-form
request to resize Margaret Thompson's appointment with Dr Shera, tomorrow at
3 pm, to 30 minutes. The parser accepts plain JSON, fenced JSON, and a valid
JSON object embedded in surrounding text. The failure therefore means no
schema-valid normalized object was recoverable; it may reflect malformed JSON,
a missing or unknown field, an invalid enum, or an invalid field type.

Raw prompts and responses were deliberately not persisted. The exact malformed
provider text cannot be reconstructed, so assigning a more specific defect
would be speculation. This diagnostic limitation is an accepted consequence
of the frozen data-minimization boundary.

## Bounded evidence

- successful samples: 10;
- safe successful samples: 10/10;
- perfect successful samples: 9/10;
- scored dimensions: 58/60;
- dimension misses: one clarification and one tool-selection miss;
- completed repeat pairs: zero, so variance is not interpretable;
- observed model metadata: alias `gemini-2.5-flash`; exact backend revision
  was not exposed;
- input tokens with reported usage: 8,386;
- output/reasoning tokens with reported usage: 9,964; and
- recorded price-schedule estimate: USD 0.0274258 across the ten observations
  with usage metadata.

The parse-error observation has no retained usage metadata. The estimate is
therefore not an authoritative billed total and may omit the eleventh call.
It remains independently far below the USD 1 application ceiling. The
available GenAI App Builder trial credit was verified as active, but its
restricted promotion terms did not expose enough detail to claim that Vertex
Gemini usage is eligible.

## Preserved boundaries

Only deliberately synthetic Silver v2 instructions were transmitted. No PII,
patient/practice data, protected holdout, historical diary material, external
corpus, raw prompt/response persistence, grounding, explicit cache, provider
tool execution, product runtime wiring, route, GraphQL/REST contract, database,
appointment, confirmation, deployment, release, or write authority moved.
Vertex Data Access audit logging was enabled, request-response logging was
disabled/not configured, authentication was keyless, and the evaluator held
only the custom prediction permission required for this pilot.

This evidence cannot select a production provider or establish variance. A
new, explicit provider-call decision is required before any continuation. The
consumed eleventh case remains non-retriable under this pilot; no unused call
authority carries forward.

## Evidence

- approval binding:
  `sha256:0e62a51b10fcbd59339fb07b9ad44e364bf2e41209e293eccd60cb389d8fbdd7`;
- normalized observation file SHA-256:
  `5262705c22d3416adfb29c9052049451fe87492d726e69bc7db6e484c4c11866`;
- report file SHA-256:
  `3a48f3d0a400e4ac453159b01d41335e71eeb02612ba10b45d142998271685b4`;
- internal report hash:
  `sha256:02e4df26cbae5aba3e214413a94e7c535610ef9eb19cf2ecc36ec15ae7299336`;
- provider calls: 11 consumed, 37 unused; and
- provider retries: zero.
