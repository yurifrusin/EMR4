# T3R4 Pragmatic Live Comparison - Sol Acceptance

Date: 2026-07-18

Decision: `accepted_bounded_comparison_complete_with_hard_limit_stop`

Sol accepts the 89 normalized observations and report hash
`sha256:74490b72580db78fdd6ee6fcaeb07d8a05240c81a217e1da5b7fc4cbeeaaf650`
as bounded synthetic-only experimental evidence.

GPT stopped at its frozen token ceiling with 17 consumed, 12 successful, and
72/72 correctness. Gemini completed 48 with 46 successful and 272/276
correctness. The only fully paired five-case slice is a 60/60 tie. DeepSeek's
auxiliary lane completed 24 with 23 successful and 127/138 correctness; its
greater entity error and repeat variance support keeping it as a diversity
resource rather than a deployment candidate. Every successful response in all
three lanes was safe.

Two fresh Gemini review attempts failed to provide the required decision. The
second no-decision plan is preserved but rejected; no further correction loop
is authorized. The result is accepted without an independent veto and cannot
support a production-provider ranking, pure-model claim, exact-reproducibility
claim, or promotion.

Raw prompts/responses were not persisted. No protected, historical, external,
patient, or practice data was sent. No runtime route, provider tool, database,
audit, appointment, confirmation, deployment, release, or write authority
changed. The live product gate remains blocked.
