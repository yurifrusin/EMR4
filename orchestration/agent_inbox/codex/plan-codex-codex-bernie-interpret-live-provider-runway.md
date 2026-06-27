# plan-codex-codex-bernie-interpret-live-provider-runway

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-interpret-live-provider-runway` |
| Branch | `codex/bernie-interpret-live-provider-runway` |
| Source Task | `codex-bernie-interpret-live-provider-runway` |
| Status | integrated |
| Created | 2026-06-27 12:22 +1000 |
| Source HEAD | `42e8bf8` |

## Plan Summary

Sprint 64 backend live-provider runway plan

## My Understanding

After approval, add a real Gemini/Vertex-backed Bernie booking-instruction interpreter path behind explicit configuration while preserving the current disabled default and deterministic fake provider. The endpoint must remain read-only: it interprets staff text into the existing structured command/normalization envelope only, never searches slots, creates proposals, confirms bookings, writes appointments, writes audit rows, logs raw PHI-heavy instructions, or performs live LLM calls in ordinary tests.

## Intended Surface / Boundary

Backend-only provider seam for POST /api/v1/appointments/proposals/bernie/interpret-booking-instruction, centered on app/services/bernie_booking_interpreter.py and app/config.py. The affected product surface is the non-mutating interpretation envelope returned by the backend. Nearby visual/runtime surfaces that must not change: diary grid booking slots/cards, waiting-room panels/statuses, Bernie review sidebar, taskpane, Command Centre, frontend launch affordances, proposal/confirm routes, slot-search execution, appointment writes, and audit logging.

## Out Of Scope

Frontend/UI changes; staff-visible enablement; autonomous booking; slot-search/proposal/confirm execution changes; appointment/audit mutations; service-account creation; committing secrets/key files; broad AI-provider refactors; migrations; PHI-heavy logging; live cloud calls in ordinary tests; enabling Gemini/Vertex by default; unrelated test hygiene.

## Files I Expect To Edit

Expected after approval: app/services/bernie_booking_interpreter.py for a provider interface plus Gemini/Vertex interpreter implementation and safe parsing/validation flow; app/config.py for explicit provider/model/enablement-style settings with disabled defaults; app/schemas/appointments.py only if provider_metadata Literal values need a narrow backward-compatible expansion; tests/test_bernie_interpret_booking_instruction.py for disabled/fake/mocked-live coverage and no-mutation/no-live-call proofs; possibly a minimal env-example/docs note only if Ariadne requires discoverable config names. Plan-gate files only now: orchestration/agent_inbox/codex/codex-bernie-interpret-live-provider-runway.md and the generated plan packet.

## Implementation Steps

1. Reconfirm the current Sprint 63 disabled/fake endpoint contract, route source no-write assertions, and schema literals. 2. Add explicit config names for live provider selection/model without changing defaults, likely keeping bernie_booking_interpreter_provider=disabled and adding Gemini/Vertex model/config fields that are inert unless provider is exactly enabled. 3. Expand provider metadata schema narrowly to include a live Gemini/Vertex provider mode while preserving existing disabled/fake responses. 4. Implement a Gemini/Vertex interpreter class behind the existing get_booking_instruction_interpreter seam, with dependency injection or a factory hook so tests can mock the model call without cloud access. 5. Design the prompt/output contract to request strict JSON for SlotSearchCommandIn-like fields plus confidence/missing/safety notes, with explicit instructions that the model must not book, search, confirm, or emit raw PHI-heavy logs. 6. Parse and validate model output through SlotSearchCommandIn and normalize_slot_search_command, converting malformed, unsafe, missing, or autonomous language cases into clarification/block responses rather than exceptions or writes. 7. Add focused tests for default disabled unchanged, fake unchanged, mocked live safe interpretation, mocked live malformed/unsafe output block, provider metadata, no raw instruction echo, no appointment/audit writes, no route calls to slot search/proposal/confirm/write helpers, and proof ordinary tests do not call live Gemini/Vertex. 8. Run py_compile on touched backend files, focused Bernie interpreter pytest, source/no-write checks, and git diff hygiene.

## Visual / Behavioural Acceptance Checks

Default config still returns provider_disabled with provider=disabled/mode=disabled/live_provider=false. Fake provider remains deterministic and backward compatible. Live provider path is reachable only by explicit config and is tested with mocked provider dependencies, not real cloud calls. All outputs use the same read-only interpretation envelope and validated normalization path. Unsafe/autonomous booking language remains blocked. No appointment, proposal, slot-search execution, confirm-Bernie, DB write, audit write, frontend, diary grid, booking slot/card, waiting-room panel, taskpane, or Command Centre behaviour changes. No secrets are committed and no raw instruction/PHI-heavy text is logged or returned beyond the existing structured summary/fields.

## Risks / Ambiguities

Main ambiguity is the repo's existing Gemini/Vertex client pattern: if there is a shared AI helper, I will reuse it only if it does not broaden the seam; otherwise I will keep the provider local and injectable. Another risk is Pydantic Literal compatibility for provider_metadata, so any schema expansion must be additive and preserve old JSON exactly. Model output reliability is a risk; implementation should fail closed on invalid JSON, missing required context, low confidence, or autonomous booking language. Live cloud credentials and exact model names are intentionally out of scope; tests must mock provider calls and should fail if a real SDK call is attempted.

## Codex Plan Review

- Review result: Accepted; backend-only/default-off provider runway plan was scoped and safe.
- Required changes before implementation: None.
- Approved to proceed: yes
