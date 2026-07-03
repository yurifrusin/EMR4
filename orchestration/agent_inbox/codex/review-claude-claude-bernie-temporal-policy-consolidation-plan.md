# review-claude-claude-bernie-temporal-policy-consolidation-plan

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-bernie-temporal-policy-consolidation-plan` |
| Status | integrated |

## Review Request

claude-bernie-temporal-policy-consolidation-plan ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Plan-only sprint - no production code edited. Coordination artifacts only: `orchestration/agent_inbox/codex/plan-claude-claude-bernie-temporal-policy-consolidation-plan.md` (Fable 5 implementation plan for Sprint 106B) and this packet's status/notes. The plan names the exact later-implementation file boundary: `app/services/bernie/temporal.py` (canonical pure temporal policy: NL time/date helpers move in, new `resolve_week_relative_date` and `evaluate_same_day_window`/`SameDayWindowDecision`), `app/services/bernie_booking_interpreter.py` (helpers become aliases importing from temporal; import direction inverts), `app/routers/appointments.py` (delete duplicated `BERNIE_WEEK_RELATIVE_RE`/week-relative body and both inline same-day clamp/exhaustion blocks in favour of shared policy calls, response assembly and all copy stay byte-identical, `_clinic_local_now` stays router-level for the test monkeypatch seam), `app/services/bernie/__init__.py` (exports), `tests/test_bernie_domain_package.py` (invert identity assertions), new `tests/test_bernie_temporal_policy.py`.
- Verification run: Plan phase - read `app/services/bernie/temporal.py`, `app/services/bernie/__init__.py`, `app/services/bernie_booking_interpreter.py` (temporal helpers, lines 38-135), both duplicated same-day blocks in `app/routers/appointments.py` (interpret path ~1932-2019; supervised wrapper ~3557-3706 incl. `_bernie_clinic_day_exhausted`), `app/services/bernie_slot_normalizer.py` relative-token handling, and the temporal test seams (16+ `appointments_router._clinic_local_now` monkeypatches; `test_bernie_domain_package.py` identity tests). No tests run and none required for a plan-only packet; the plan lists the focused suites and full `pytest tests -q` for the implementation phase.
- Remaining risks: (1) Known local test DB lifecycle fragility on full-suite runs (create/drop teardown flakiness per the integrated claude-test-db-teardown-hardening work) - implementation phase should run focused Bernie/slot suites first, run the full suite serially, and rerun a DB-lifecycle failure once to separate infra flake from regression. (2) Exact-string coupling: tests assert basis/summary/clarifying copy, so any wording drift during extraction is a defect. (3) Import-direction inversion between temporal.py and the legacy interpreter must not create a cycle. (4) The interpret-path and wrapper clamps re-normalize from different sources; the plan preserves both shapes deliberately rather than unifying them. Implementation remains blocked until Ariadne/Yuri explicitly say `complete sprint task`.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-bernie-temporal-policy-consolidation-plan.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Accepted. This is the right next slice after the bounded Bernie package foundation because it attacks duplicated time/date policy without changing UI or persisted-session architecture.
- Follow-up required: Dispatch implementation only after explicit release. Watch import-cycle risk when inverting temporal helper ownership, exact-string/copy drift, and the known local test DB lifecycle fragility during broad test runs.

## Integration Notes

- Integration result: Implemented directly by Ariadne after Yuri approved proceeding.
- Claude/Fable role: consulting plan author; no further Claude implementation run was used because the 5-hour limit was close.
- Verification: py_compile/import smoke passed; focused Bernie/slot suite passed with `206 passed`; `git diff --check` passed with only existing CRLF normalization warnings.
