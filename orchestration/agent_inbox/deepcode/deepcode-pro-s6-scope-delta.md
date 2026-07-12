# DeepSeek 4 Pro Conductor: S6 Scope Delta

Role: Conductor fallback
Resource: `deepseek-pro-conductor-fallback`
Model: `deepseek-v4-pro`
Reasoning: high
Trigger: Claude subscription remains at a real session limit; Fable and Opus
share that unavailable account window.
Completion plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s6-scope-delta.md`

Act as Ariadne Conductor under `operating_model.yaml`, `role_preferences.yaml`,
`continuous_sprint_engine.yaml`, and `cost_controls.yaml`. You have sprint
planning and worker-allocation authority only. You cannot integrate, commit,
push, or modify master.

Read the current S6 plan, the rejected Lane 1 artifact, and the files named
below. Sol independently rejected Lane 1 because its claimed 82-pass result was
false and its candidate weakened a network-contract test. Sol then reproduced
the failures and found that the original S6 test-only diagnosis is incomplete:

1. Four practitioner-directory tests are stale after GraphQL became default-on.
   `route_practitioner_directory_consumer_api()` still mocks and asserts the REST
   route. The live consumer now posts `/api/v1/graphql` with variables
   `activeOnly: true`, `limit: 200`, and `offset: 0`.
2. Four signed create/update-confirm tests do reach their proposal handlers, but
   then stop before confirm. Browser-side diagnostic evidence is
   `booking-error: "ahpra is not defined"`.
3. In `docs/diary/diary.js`, `saveBooking()` now defines
   `practitionerSelection` and `practitioner` at lines approximately 7710-7711,
   but later still passes or stores the removed identifier `ahpra` in three
   places: `appointmentCrossesBreak(ahpra, ...)`,
   `appt.practitioner.ahpra_number = ahpra`, and the new-appointment
   `practitioner.ahpra_number` field. This runtime regression was introduced by
   the practitioner-directory consumer migration.
4. The temporary diagnostic instrumentation has been removed; master is clean.

The current S6 boundary permits edits only to `review/test_diary_smoke.py` and
explicitly excludes `docs/diary/diary.js`. Determine the smallest correct next
step. You may amend S6 or close/resequence it, but do not leave a known runtime
ReferenceError unfixed and do not weaken the signed-confirm assertions. Preserve
independent review, regular Sol commit/push checkpoints, and the already planned
S7 Ariadne cross-boundary contract audit. Do not add monetary or wall-clock
caps. Keep every unrelated runtime gate closed.

The completion artifact must state:

- direction/scope disposition and rationale;
- exact revised worker allocation and ownership;
- concrete worker packet paths for any revised/new lanes;
- acceptance evidence, including a zero-failure full diary smoke suite;
- whether an independent LLM verifier is risk-triggered (deterministic checks
  remain mandatory);
- all closed gates and the Claude-to-DeepSeek fallback reason; and
- the next sprint transition after acceptance.

End the final plan with:

```text
STATUS: complete
```
