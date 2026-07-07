# Fable Sprint 161 - Bernie/Diary Sequencing Review

| Item | Value |
|---|---|
| Reviewer | Claude Fable 5, via Claude CLI |
| Date | 2026-07-07 |
| Brief | `orchestration/agent_inbox/claude/claude-fable-sprint161-bernie-diary-sequencing-review.md` |
| Gate posture cited | `runtime_or_provider_wiring_ready=false`, `raw_trove_access_ready=false`, `runtime_gate_decision=blocked` |

## Verdict

Small authored prompt-thread automation should start now, with one framing
correction: this is contract-level automation over the deterministic fake
provider and route layer, not an AI-training or live-provider quality harness.

The useful target is regression armor for the interpretation contract:
clarification merge, change requests, selected-slot pivot, confirm-required
boundary, and no-write posture. That stable yardstick is what will later make a
provider-boundary or live-provider review measurable instead of anecdotal.

## Direct Answer To Yuri

Fable's direct answer: yes, the current Diary/Bernie system has strong enough
bones and sinews for automatic prompt testing and troubleshooting to produce
diagnostic signal now. The deliberately weak muscle is the modest fake
interpreter, and that is not a reason to wait; it is the reason to focus the
automation on route/contract behavior rather than claiming linguistic or
provider-quality evidence.

Fable's breakdown:

- Bones: route contracts and proposal/confirm spine are strong enough. The
  interpret endpoint is a real contract surface with typed outcomes, session
  state, outcome/state consistency assertions, and no-write posture, while the
  signed proposal/confirm pattern remains the write authority.
- Sinews: clarification merge, context frames, and session threading are present
  and tested, but the corpus is thin.
- Muscles: natural-language strength is intentionally modest under the fake
  provider. That means automation now should measure contract stability, not
  language intelligence.

The exact missing structural capability is small and concrete: add an
`interpret` action to the existing `tests/bernie_scenarios` replay harness, with
context-frame threading between turns.

The threshold for contract-level automation is already crossed. The threshold
for provider-quality prompt automation remains later and requires explicit
provider-boundary review plus a dry-run/provider lane. No amount of deterministic
harness work substitutes for that gate.

## Ranked Next Sprints

1. **Interpret-capable prompt-thread harness.** Extend the existing
   `tests/bernie_scenarios` replay engine with an `interpret` action and add
   10-15 hand-authored natural-phrasing multi-turn threads.
2. **Residual review-friction triage, timeboxed.** Treat Yuri's already fixed
   launcher and migration blockers as closed. If no further friction appears,
   fold this into the harness sprint closeout rather than spending a full sprint.
3. **Narrow live-backend evidence, not live-provider evidence.** Run the same
   corpus against a non-intercepted local backend with the fake provider so
   route-level and live-backend labels can diverge on the same corpus. Do not
   open the provider gate.
4. **H-series coverage taxonomy only, optional and cheap.** Add coarse
   `coverage_category` labels from neutral profile category names only. Do not
   use prompt text, parameters, appointment semantics, or provider context from
   H-series material.
5. **Resume API-spine prototype work.** This can run later or in parallel where
   non-invasive; it should not preempt the prompt-thread harness.

## Smallest Useful Prompt-Thread Automation Scope

- Add `interpret` as a scenario action in `tests/bernie_scenarios/loader.py` and
  `tests/bernie_scenarios/replay.py`.
- Post to
  `/api/v1/appointments/proposals/bernie/interpret-booking-instruction` with
  `bernie_booking_interpreter_provider="fake"`.
- Extract the `requested_appointment` frame using the pattern from
  `tests/test_bernie_clarification_merge.py`, then thread it as
  `context_frames` into the next `interpret` turn.
- Add 10-15 natural-phrasing YAML threads covering initial request to
  clarification reply, change of date, change of time window, change of
  practitioner, change of duration, selected-slot pivot, confirm-required
  boundary, and stale/past-date blocks where existing fixtures can be extended.
- Assert expected per-turn result, merged versus new-reply-wins fields,
  preserved fields, forbidden provider calls, no appointment writes, no audit
  writes, and no raw UUIDs or `snake_case` in staff-facing copy fields.
- Label evidence as `fake-provider, route-level`. It is not live evidence and
  not provider-quality measurement.

## Explicit No-Go Boundaries

- No raw historical diary trove files outside ignored local processing.
- No committed raw, extracted, or PHI-bearing diary text.
- No broad 58k-file processing.
- No H15/H-series runtime imports into Bernie, Access AI, providers, memory,
  RAG, GraphRAG, routes, or UI.
- No historical diary material in prompts, provider calls, memory, or executable
  Bernie scenarios.
- H-series profiles may supply coverage category names only, never prompt
  strings, appointment semantics, or patient/practitioner/resource parameters.
- No provider prompt wiring, dry-run wiring, or live-provider enablement without
  explicit provider-boundary gate review first.
- No model-to-database writes, GraphQL mutations, or bypass of signed
  proposal/confirm commands.
- No weakening of staff confirmation, idempotency, audit, freshness, or
  route-authority boundaries.

## Risks

1. Overclaiming: a passing corpus can be mistaken for "Bernie understands
   language." Mitigate with mandatory evidence labels in README and closeout.
2. Corpus drift into `key:value` shorthand. Require natural phrasing in new
   fixtures.
3. Scope creep into provider testing. Keep readiness/provider gates cited and
   unchanged.
4. Duplicating `tests/test_bernie_clarification_merge.py`. Keep that pytest file
   as semantic spec; use scenario fixtures for thread breadth.

## Acceptance Criteria For The Next Sprint

- `interpret` action lands with schema validation and README documentation.
- At least 10 natural-phrasing prompt threads pass.
- All forbidden-outcome and no-write assertions hold.
- `pytest tests/bernie_scenarios/ -q` is green.
- Readiness gate values remain unchanged and are cited.
- Closeout labels all evidence as `fake-provider, route-level`.

Yuri's next hands-on review should focus on what automation cannot judge:
copy tone, staged-versus-confirmed visual clarity, pivot ergonomics in the real
Diary panel, workflow feel, and clinical plausibility of candidate slots.

## Files To Touch First

1. `tests/bernie_scenarios/replay.py`
2. `tests/bernie_scenarios/loader.py`
3. `tests/fixtures/bernie_scenarios/`
4. `tests/bernie_scenarios/README.md`

Fable also noted a hygiene item for a later API-spine sprint: the API steward
skill references `references/review-checklist.md`, which is absent from this
checkout and should be restored or re-pointed later.

