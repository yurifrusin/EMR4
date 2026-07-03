# plan-claude-claude-bernie-temporal-policy-consolidation-plan

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-bernie-temporal-policy-consolidation-plan` |
| Status | accepted |
| Created | 2026-07-03 12:17 +1000 |
| Source HEAD | `a5b83e3` |

## Plan Summary

Consolidate Bernie temporal/date/time/clinic-day policy into pure, typed functions in app/services/bernie/temporal.py with zero public JSON/API behaviour change; routers keep response assembly and the monkeypatchable clinic clock seam.

## My Understanding

Sprint 106B is plan-only. Bernie temporal policy is currently split three ways: (a) week-relative phrase resolution duplicated between app/services/bernie_booking_interpreter.py (WEEK_RELATIVE_RE + _extract_natural_date_constraint) and app/routers/appointments.py (BERNIE_WEEK_RELATIVE_RE + _resolve_bernie_instruction_relative_date) with identical regex and identical +7-day resolution; (b) same-day clamp / clinic-day-exhaustion policy implemented twice inside appointments.py - the interpret path temporal axis (approx lines 1932-2019: fully-past bounded window -> ask band + clarifying copy; partly-past window -> clamp earliest_time to clinic-now and re-normalize; open-ended past earliest -> clamp and re-normalize) and the supervised wrapper (approx lines 3557-3706: pre-search fully-past bounded window -> clinic_day_exhausted; open-ended clamp-to-now with re-normalize; post-search open-ended zero-candidate -> clinic_day_exhausted); (c) the pure NL time/date helpers whose implementation still lives in the legacy interpreter module while app/services/bernie/temporal.py only re-exports them. The consolidation makes temporal.py the single canonical home for this policy as pure functions (no DB, no network, no wall clock), while both router paths and the interpreter delegate to it and keep their existing branch-specific response assembly and copy byte-identical.

## Intended Surface / Boundary

Backend only: app/services/bernie/temporal.py grows into the canonical temporal policy module; app/routers/appointments.py and app/services/bernie_booking_interpreter.py get mechanical delegation swaps. No public schema/JSON contract change, no endpoint added or removed, no Alembic migration. Visually adjacent surfaces that must NOT change: diary grid, booking slots/cards/panels, waiting room, taskpane, command centre, appointment status colours - none of these are touched; all response copy (summaries, warning/block codes, clarifying questions, basis strings) stays byte-identical so the Bernie staff-review UI renders identically.

## Out Of Scope

No production code edits during this plan phase. In the later implementation: no persisted Bernie session table, no Alembic migration, no diary UI changes, no broad appointments.py rewrite beyond the temporal call sites, no LLM provider changes, no autonomous booking, no root-to-branch API review, no test deletion, no change to bernie_slot_normalizer.py relative-token semantics, no change to the business-hours bare-hour-is-pm assumption.

## Files I Expect To Edit

app/services/bernie/temporal.py (canonical implementations + new typed policy API); app/services/bernie_booking_interpreter.py (helpers move out; legacy private names become aliases importing from temporal - import direction inverts); app/routers/appointments.py (delete BERNIE_WEEK_RELATIVE_RE and the _resolve_bernie_instruction_relative_date body, replace both inline same-day blocks with calls to the shared policy while keeping response assembly); app/services/bernie/__init__.py (export new names); tests/test_bernie_domain_package.py (flip identity assertions to legacy-is-temporal); new tests/test_bernie_temporal_policy.py (pure unit tests). No other files.

## Implementation Steps

1) Move _parse_time_fragment, _extract_natural_time_constraints, _extract_natural_date_constraint and their regexes (including WEEK_RELATIVE_RE) verbatim into temporal.py as the canonical implementations; the legacy interpreter module re-imports them under the old private names so external monkeypatch/import paths keep working; update the two identity tests in test_bernie_domain_package.py to assert the inverted direction. 2) Add resolve_week_relative_date(instruction, reference_date) -> str-or-None in temporal.py; _resolve_bernie_instruction_relative_date in appointments.py becomes a thin delegate and BERNIE_WEEK_RELATIVE_RE is deleted; the _extract_natural_date_constraint week branch delegates to the same function. 3) Add a typed pure same-day policy: frozen dataclass SameDayWindowDecision(kind in {ok, not_same_day, window_fully_past, clamp_earliest}, clamp_hhmm) returned by evaluate_same_day_window(resolved_date, earliest_time, latest_time, clinic_now) - clinic_now is passed in, never read from the wall clock. 4) Interpret path maps decisions to its existing outputs verbatim: window_fully_past -> temporal_band ask + existing clarifying copy; clamp_earliest -> set command_values earliest_time to clamp_hhmm, re-normalize via normalize_slot_search_command, keep exact basis strings. 5) Supervised wrapper maps the same decisions to its existing outputs verbatim: pre-search window_fully_past -> _bernie_clinic_day_exhausted with the same summary; clamp_earliest -> re-normalize from body.command.model_dump() exactly as today; the post-search zero-candidate open-ended exhaustion branch keeps its current condition (it depends on search results, so it stays in the router but reads the same-day/open-ended predicate from the shared decision). 6) _clinic_local_now stays in appointments.py because 16+ existing tests monkeypatch appointments_router._clinic_local_now; temporal.py stays wall-clock-free. 7) Export new names via temporal.__all__ and app/services/bernie/__init__.py. 8) Add pure unit tests for resolve_week_relative_date and evaluate_same_day_window covering fully-past, partly-past, open-ended-past, exact-boundary (latest == now, earliest == now), and non-same-day cases; run focused suites then full pytest.

## Visual / Behavioural Acceptance Checks

All existing JSON outputs unchanged: week-relative instruction still produces the date_resolved_from_instruction_relative_week warning + BernieAssumption with identical text; same-day fully-past window still returns interpret-path ask band with the same clarifying question and wrapper clinic_day_exhausted with the same summary/block code; partial-past and open-ended clamps still rewrite earliest_time to clinic-now HH:MM with the same basis strings and re-normalized constraint; normalizer today/tomorrow handling untouched; no response_model/schema diffs. Focused tests green: tests/test_bernie_domain_package.py, tests/test_bernie_interpret_booking_instruction.py, tests/test_bernie_supervised_booking_wrapper.py, tests/test_bernie_confidence_policy.py, tests/test_bernie_no_slot_suggestions.py, tests/test_bernie_slot_normalizer.py, tests/test_slot_search_normalize_endpoint.py, tests/test_bernie_turn_contract.py, plus new tests/test_bernie_temporal_policy.py. Then full pytest tests -q green and python -m compileall app.

## Risks / Ambiguities

1) Local test DB lifecycle fragility (known): full-suite runs against local Postgres have create/drop teardown flakiness (see integrated claude-test-db-teardown-hardening). Mitigation: run focused Bernie/slot files first, run the full suite serially, rerun a DB-lifecycle failure once to separate infra flake from regression, and report persistent failures rather than masking them. 2) Exact-string coupling: many tests assert basis/summary/clarifying copy; all copy must move verbatim or stay in the routers - treat any wording diff as a defect. 3) Monkeypatch seams: tests patch appointments_router._clinic_local_now and router-level bindings; keep those module-level names bound in appointments.py. 4) Import-cycle inversion: temporal.py currently imports FROM the legacy interpreter; step 1 inverts this - ensure the legacy module imports from temporal only and that app.services.bernie.__init__ does not create a cycle through the interpreter facade (verify with a plain import smoke test). 5) The two clamp paths re-normalize from different sources (interpret path mutates its command_values dict; wrapper rebuilds from body.command.model_dump()) - the plan intentionally preserves both shapes rather than unifying them, since unifying could change outputs when the interpreter added fields. 6) The post-search exhaustion check cannot be fully pure (depends on candidate count); scope discipline: only the same-day/open-ended predicate is shared, the branch stays in the router.

## Codex Plan Review

- Review result: Accepted by Ariadne as a narrow Sprint 106B implementation plan. The plan preserves public JSON/API/copy behaviour, keeps `_clinic_local_now` in the router for existing monkeypatch seams, and limits implementation to temporal policy extraction plus focused tests.
- Required changes before implementation: Implementation should wait for explicit Yuri/Ariadne `complete sprint task` approval, ideally after the Claude 5-hour window resets. Keep implementation at medium reasoning and stop if exact-string behaviour drifts or router changes widen beyond the listed call sites.
- Approved to proceed: yes, after explicit implementation release
