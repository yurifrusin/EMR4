# Antigravity T1 - Stateful Duplicate Booking Browser Acceptance

Role: bounded browser and accessibility implementation worker
Platform/model: Antigravity / Gemini 3.5 Flash (Medium)
Parent roadmap: `docs/bernie-consultant-triage-implementation-roadmap.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-antigravity-t1-stateful-duplicate-playwright.md`

## Mission

Add a focused Playwright acceptance test for the receptionist-visible sequence:
the first request is reviewed and authoritatively confirmed, then the same
booking is requested again and Bernie presents the existing-booking outcome
instead of another confirmable candidate.

This lane is deliberately distinct from the backend replay worker. It may use
stateful route interception in the existing static diary smoke harness and must
label that evidence honestly as browser/UI contract evidence, not live-backend
evidence. Create a candidate commit on the disposable worker branch only. Do
not push, integrate protected master, or move `handoff/current`.

## Owned Surface

- one new focused test under `review/`, or a tightly scoped addition to
  `review/test_diary_smoke.py` if that is clearly the established local pattern
- optional focused browser-test helper or fixture under `review/`
- the expected completion artifact above

Do not edit `app/`, `tests/bernie_scenarios/`, scenario YAML, backend tests,
`docs/diary/diary.js`, HTML/CSS runtime assets, `AGENTS.md`, phase programmes,
providers, migrations, or orchestration policy.

## Acceptance Contract

1. Reuse the existing static diary Playwright setup and selectors where
   practical. Do not create a second UI test framework.
2. Model stateful intercepted responses: first request offers/reviews a booking;
   confirmation returns authoritative success; repeated identical request
   returns the structured existing-booking result.
3. Assert that after first confirmation the authoritative receipt/status is
   exposed to assistive technology through the existing status/live region.
4. Assert that the repeated request exposes the existing booking outcome and
   does not expose a second candidate confirmation action.
5. Assert useful accessible next actions for changing time or day where the
   current UI contract supplies them. Use role/name selectors and keyboard
   activation; record a precise gap instead of changing runtime UI if the
   current surface lacks an expected control.
6. Count intercepted confirmation requests and prove the duplicate path makes
   no additional confirmation request.
7. Check focus remains coherent after the outcome transition and that no
   actionable control is hidden only in visual copy.
8. Keep all data authored/synthetic. Make no external network/provider calls.

Do not weaken assertions to accommodate the current UI. If a required behavior
is absent, add a focused expected-failure or completion-artifact finding with
the exact observed gap; do not modify production assets in this worker lane.

## Verification

Run the narrow new browser test plus the existing relevant smoke/accessibility
slice. Use the shared EMR4 virtual environment and existing browser setup.
At minimum run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest <new-or-focused-review-test> -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_accessible_confirmation.py -q
git diff --check
```

Write the expected artifact with candidate commit SHA, files changed, exact
evidence tier, browser/viewport used, assertions exercised, verification
results, observed product gaps, boundary confirmation, and the exact final
marker `STATUS: complete`.
