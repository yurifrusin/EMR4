# Antigravity T2.1 - Outcome Accessibility Matrix

Role: bounded browser/accessibility implementation worker
Platform/model: Antigravity / Gemini 3.5 Flash (Medium)
Parent: `docs/bernie-t2-deterministic-behaviour-matrix.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-antigravity-t2-outcome-accessibility-matrix.md`

## Mission

Add focused route-intercepted Playwright UI-contract evidence for the currently
weaker non-authoritative outcomes: `no_slots`, `roster_unavailable`, and one
clarification state. Reuse the established diary harness and existing selectors.
Do not duplicate existing smoke assertions unless the new test adds keyboard,
focus, live-region, accessible-name, or authority-absence evidence.

## Required Acceptance

- each state has a distinguishable receptionist-facing heading/copy and
  machine-readable state marker;
- status or changed outcome is exposed through an appropriate live/status
  region where the current contract provides one;
- keyboard users can reach and activate the next useful action where one exists;
- focus remains coherent after the state transition;
- no state exposes a confirm button, confirm request, success receipt, or copy
  claiming availability/action completion; and
- the route-intercepted evidence tier is stated honestly and uses only authored
  synthetic data.

If the current UI lacks one of these behaviors, preserve a precise expected
failure or report the gap. Do not modify production HTML/JavaScript/CSS in this
worker lane.

## Ownership

- one new focused test under `review/`, with a small helper there only if needed
- expected artifact above

Do not edit `app/`, `docs/diary/`, backend tests, scenario fixtures, AGENTS,
phase programmes, orchestration policy, providers, schemas, or migrations.

Create one candidate commit only. Do not push, integrate master, or move
`handoff/current`.

## Verification

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest <new-focused-test> review\test_diary_smoke.py -k "no_slot or roster_unavailable" -q
git diff --check
```

Write the expected artifact with the evidence tier, states/assertions, browser,
test results, product gaps, candidate commit as resolved by Git/receipt, boundary
confirmation, and `STATUS: complete`.
