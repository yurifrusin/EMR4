# Antigravity T2.2 - Stale Proposal Accessibility

Role: bounded browser/accessibility implementation worker
Platform/model: Antigravity / Gemini 3.5 Flash (Medium)
Parent: `docs/bernie-t2-deterministic-behaviour-matrix.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-antigravity-t2-stale-proposal-accessibility.md`

## Mission

Add focused route-intercepted Playwright UI-contract evidence for canonical
stale, failed, and confirmation-pending proposal states. Reuse the current diary
harness and `bernie.ui_view_model.v1`; do not bypass that view model with legacy
fallback payloads.

## Required Acceptance

- each state renders distinguishable receptionist-facing copy and a
  machine-readable state marker;
- the completed transition has coherent focus/live-region behavior;
- stale and failed states expose only appropriate retry/edit recovery actions
  reachable and activatable by keyboard;
- pending state does not permit another confirmation attempt;
- none exposes an enabled confirm button, success receipt, authoritative
  completion copy, or confirm request;
- tests use authored synthetic route responses and state E3
  route-intercepted evidence honestly; and
- existing T2.1 outcome tests remain green.

If behavior is missing, preserve a precise failing/xfail case or report the gap.
Do not modify product HTML, JavaScript, or CSS in this worker lane.

## Ownership

- one focused test under `review/`
- expected artifact above

Do not edit `app/`, `docs/diary/`, backend tests, scenario fixtures, AGENTS,
roadmap documents, orchestration policy, providers, schemas, or migrations.
Create one candidate commit only. Do not push, integrate master, or move
`handoff/current`.

## Verification

```powershell
pytest <new-focused-test> review\test_diary_outcome_accessibility.py -q
node --check docs\diary\diary.js
git diff --check
```

Write the expected artifact with evidence tier, state/assertion matrix, browser,
test results, product gaps, candidate commit resolution, boundaries, and
`STATUS: complete`.
