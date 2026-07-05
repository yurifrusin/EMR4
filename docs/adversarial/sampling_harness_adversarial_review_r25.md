# Sprint R25 Adversarial Review

**Reviewer:** DeepSeek Flash adversarial lane, integrated by Ariadne  
**Target:** `provider_sampling_harness.py` consumption path against the R24
`manifest_eval.py` gate  
**Mode:** no live calls, no database access, no runtime provider wiring

## Risk Classes Reviewed

### Accidental Live Calls

- Harness import must not import Gemini, Vertex, Google Cloud clients, routes,
  models, SQLAlchemy, Alembic, or diary mutation services.
- Default-disabled behaviour must be testable by direct import and method calls.
- The harness must not be registered in any production provider registry.

### Write Authority

- `writes_authorized=True` must fail in every frame shape, including nested
  structures and fake confirmation envelopes.
- Provider-style synonyms must not bypass the gate. R25 found and fixed one
  concrete gap: `allow_write=True` previously passed; it now fails while
  `allow_write=False` remains safe.
- Passing fixture output must never be described as provider trust or write
  readiness.

### PHI Logging

- Fixtures should avoid PHI-indicative keys, even with synthetic values, unless
  the fixture exists specifically to prove PHI detection.
- Assertion messages and pytest artifacts must not persist real patient details.
- Future live-provider telemetry needs a separate privacy/redaction design.

### Provider Metadata Spoofing

- Static samples must not be confused with live model responses.
- Future metadata should use explicit provenance labels such as
  `source="static_sample"` or `run_mode="sampling"`.
- Golden fixtures must not use real project IDs, service account names, or
  production-like model metadata as proof of runtime origin.

### Sample-Evaluation Bypass

- Every enabled sample must go through `evaluate_manifest_response()`.
- Frameless safe-looking dicts are a known boundary: they can pass generic
  safety checks while skipping frame-shape validation.
- Lists and unknown frame kinds must remain rejected or violation-bearing.

## Integrated Outcome

- Added static Gemini-style, Vertex-style, and adversarial sample sets.
- Added default-disabled/no-write harness tests.
- Added adversarial boundary tests for live-call imports, write authority, PHI
  keys, metadata spoofing, frameless bypass, malformed frames, and fake-provider
  state.
- Hardened `manifest_eval.py` so `allow_write=True` is treated as a
  write-authority claim.

## Remaining Risks

- R25 is still a static scaffold, not live-provider readiness.
- A future live shadow pilot needs explicit opt-in, privacy controls, telemetry
  provenance, cost/latency gates, and a kill switch.
- Frame-shape enforcement for frameless responses remains a useful future
  hardening target.
