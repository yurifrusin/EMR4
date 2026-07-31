# Reception One Bureau Typed Plan Protocol — Sol acceptance

Date: 2026-07-29

Disposition: `accepted`

Accepted result:
`reception_one_bureau_typed_plan_protocol_provider_free_pass`

## Review

The implementation satisfies the authorised provider-free,
authored-synthetic Typed Plan Protocol tranche.

The accepted language contains fourteen closed operators with only `pure`,
`authorised_read` and `proposal_only` effects. It can represent the existing
create, move, resize, cancel and status proposal families and a novel
squeeze-in assessment without adding a new primitive, command or write.

The deterministic proofreader checks the exact input, plan and review schemas;
request, practice and correlation scope; context freshness; grounded values;
operator signatures; typed topological dataflow; semantic action; effect
ceiling; and authority. The in-memory executor independently rechecks the
admitted plan hash and context revision before returning a typed proposal
candidate or assessment. No result can confirm or mutate an appointment.

Six positive authored-synthetic cases pass. Six adversarial cases fail closed.
The bounded typed dialogue rejects a missing required duration, admits one
corrected second attempt and permits no further revision. A simulated watcher
revision makes a stale plan reject without connecting a new event runtime.

The implementation reuses the accepted deterministic semantic extractor and
the existing API Spine proposal operation identifiers. No API route, database,
event family, provider, credential, network path, product-data path or UI
delivery was added.

The focused protocol suite, inherited semantic and runtime-gate population,
API Spine artifacts, Ariadne cognitive-work-cell/continuity/Compass tests,
JSON/schema checks, Ruff, compilation and repository-only verifier pass.

The test-only repair to
`tests/test_bernie_interpretation_runtime_isolation.py` removes an over-broad
filename assertion. The app's intentional fail-closed read of the inert
runtime-gate JSON remains in place and its provider-gate tests pass.

Acceptance is limited to a repository-local provider-free protocol and
authored-synthetic evidence. A model-connected cell, product context reads,
runtime proposal delivery, any confirmation or write, real or historical
Diary data, voice, production, deployment and release require separately
scoped authority.
