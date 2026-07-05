# Sprint R23 DeepSeek Adversarial Frame Review

DeepSeek Flash independently reviewed the R22/R23 fake-provider frame seam for
safe-looking malformed outputs that could slip past phrase/key detectors before
live Gemini wiring.

## Review Focus

- Proposal frames that look polite but omit explicit staff confirmation or carry
  confirmation-envelope/write-grant fields.
- Clarification frames that default ambiguous patients, expose raw IDs, or select
  a reason code while still claiming to clarify.
- Refusal frames that use refusal copy but omit a blocking reason, or smuggle a
  confirmation type/envelope.
- Read-request frames that claim live availability or free slots from manifest
  context instead of requiring a backend check.
- Type confusion around boolean fields such as `writes_authorized`,
  `requires_staff_confirmation`, `blocked`, and `requires_backend_check`.

## Integrated Outcome

- `validate_response_frame_shape()` now validates declared `frame_kind` values for
  `proposal`, `clarify`, `refusal`, and `read_request`.
- `evaluate_manifest_response()` now reports `malformed_frame` violations and
  exposes `malformed_frame_detected` on the eval result.
- R23 tests cover missing required keys, forbidden confirmation/write fields,
  ambiguous-patient defaulting, selected reason-code leakage, malformed refusal
  frames, read-request availability claims, and unknown frame kinds.

## Remaining Risk

The frame validator is intentionally fake-provider/test-only. It should remain a
gate for live-provider readiness, not a runtime write-authority mechanism. Future
provider dry-runs should add examples from real model output and expand the
detectors only from observed misses.
