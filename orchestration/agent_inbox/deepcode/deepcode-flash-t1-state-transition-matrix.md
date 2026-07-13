# DeepSeek Flash T1 - Stateful Booking Transition Matrix

Role: bounded backend test implementation worker
Resource: `deepseek-flash-workers` (one disposable instance)
Model: `deepseek-v4-flash` / high
Parent roadmap: `docs/bernie-consultant-triage-implementation-roadmap.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-deepseek-t1-state-transition-matrix.md`

## Mission

Extend the T1 scenario laboratory so a scenario can apply an explicitly
allowlisted external appointment-state event between Bernie turns. Use that
capability to add deterministic golden scenarios covering the difference
between an exact duplicate, an overlapping but different booking, a distinct
same-day booking, a terminal-status historical booking, and stale/concurrent
state that appears after a proposal has been prepared.

This is a tests-and-documentation worker lane. Create a candidate commit on the
disposable worker branch only. Do not push, integrate protected master, or move
`handoff/current`.

## Owned Surface

- `tests/bernie_scenarios/loader.py`
- `tests/bernie_scenarios/replay.py`
- `tests/bernie_scenarios/test_t1_stateful_contract.py`
- new focused files under `tests/fixtures/bernie_scenarios/`
- `tests/bernie_scenarios/README.md`
- `docs/bernie-t1-stateful-scenario-laboratory.md`
- the expected completion artifact above

Do not edit `app/`, `docs/diary/`, `review/`, `AGENTS.md`, orchestration policy,
phase programmes, provider code, migrations, schemas, or unrelated fixtures.

## Required Contract

1. Add one canonical scenario action for a fixture-owned external state event.
   Prefer a narrow name such as `external_appointment` and an explicit operation
   such as `create` or `set_status`; do not accept arbitrary model/table writes.
2. Allow only the existing synthetic patient/practitioner fixtures, validated
   dates/times, positive bounded duration, known appointment statuses, and local
   aliases. Reject unknown fields and unsupported operations at load time.
3. Treat setup/event mutations as scenario-environment changes, not as Bernie or
   system product writes. Per-turn `appointment_delta` and `audit_delta` must
   continue to describe authoritative product effects. Evidence must separately
   identify fixture event counts without exposing entity IDs or request bodies.
4. Preserve deterministic clinic-local time and existing fake-provider guard.
5. Add executable golden coverage for:
   - an overlapping appointment that is not the same requested booking;
   - a different same-day appointment that does not become an exact duplicate;
   - a terminal cancelled/no-show appointment that does not masquerade as the
     currently existing requested booking;
   - an appointment inserted after preparation but before confirmation, proving
     confirmation revalidates or fails closed without a second booking/audit
     write.
6. Assert exact structured outcomes and row deltas. Do not settle for copy-only
   assertions where a result kind or authority field exists.

If current runtime behavior cannot satisfy one matrix case, preserve it as an
honest `xfail` with a precise reason and do not modify production code to make
the worker lane pass.

## Verification

Run from the disposable worktree using the shared EMR4 virtual environment:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\ tests\test_bernie_scenario_integrity.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_evidence_snapshot.py -q
git diff --check
```

Write the expected artifact with candidate commit SHA, changed files, scenario
matrix and observed outcomes, verification results, residual risks, boundary
confirmation, and the exact final marker `STATUS: complete`.
