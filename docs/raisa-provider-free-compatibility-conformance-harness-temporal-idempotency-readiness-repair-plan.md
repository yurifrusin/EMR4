# Provider-free compatibility conformance-harness temporal/idempotency readiness repair plan

Date: 2026-08-12

Source HEAD: `712e9842297e5aee21c3b4acb061d439639bae04`

Status: `frozen_for_test_only_execution`

## Purpose

Restore the accepted 311-test ordinary compatibility collection to a current,
repeatable baseline without changing any application behavior or expected route
semantics. The accepted admission review identified exactly 45 stale-harness
failures: 33 temporal-fixture failures and 12 missing proposal-idempotency
headers.

## Exact owned test files

Only these eight existing test files may change:

1. `tests/test_booking_create_edit.py`
2. `tests/test_booking_patient_flow.py`
3. `tests/test_break_overlap_contract.py`
4. `tests/test_location_scoped_diary.py`
5. `tests/test_noshow_dna_status_contract.py`
6. `tests/test_nurse_practitioner.py`
7. `tests/test_reason_code_backend.py`
8. `tests/test_slots.py`

Plan, threat, receipt, deterministic acceptance, continuity and closeout
artifacts may be added separately. No application file is owned.

## Frozen repair classes

### Clinic-local temporal fixtures

- Same-day suites keep `date.today()` where waiting-room semantics depend on
  the actual test date and freeze only `appointments._clinic_local_now` at
  08:00 in the practice timezone. Their exercised 09:00-or-later inputs remain
  same-day and future at the validation boundary.
- Weekday-specific schedule suites derive the next occurrence of the required
  weekday, at least one day in the future, rather than retaining June 2026
  dates. Assertions derive their date prefix from that same fixture constant.
- The UTC-input conversion case derives its UTC instant from the same frozen
  test date rather than retaining the elapsed July 2026 literal.
- Temporal-denial expectations and application clocks are not changed.

### Proposal idempotency fixtures

- Each status/delete proposal expected to reach its route contract receives a
  deterministic, non-empty `Idempotency-Key` derived from its test appointment
  and action.
- Confirm-command idempotency helpers remain unchanged.
- Invalid-body proposal cases that deliberately prove validation precedence
  retain their existing requests and expected `422` results.

## Acceptance

The repair passes only if:

1. the fresh five-source Ariadne preplanning receipt passes;
2. the exact pre-repair 311-test collection reproduces 266 pass / 45 fail with
   the accepted 33 temporal and 12 header classification;
3. only the eight named test files change outside tranche evidence;
4. no assertion, expected status, application source or safety control changes;
5. the same exact 311-test collection passes 311/311;
6. the admission-review census and API Spine dependency tests still pass;
7. the canonical fast repository profile and `git diff --check` pass; and
8. protected refs, `docs/branding/` and every unrelated untracked file remain
   unchanged.

## Forbidden surfaces

- no application, router, schema, service, model, migration or database change;
- no expected-status or semantic-assertion weakening;
- no removal or bypass of temporal or idempotency admission;
- no route/kernel/adapter/shadow/observer/sink/runtime implementation;
- no operational database/source/watcher/event or product/patient data;
- no provider, network, credential, IAM, command/write or deployment; and
- no production, release, Pages, protected-ref movement or broad staging.

## Next safe descendant

After 311/311 and closeout, continue to the provider-free unmounted status
transaction-kernel protocol rehearsal. That descendant remains authored-
synthetic and unmounted and may not import or execute an application route,
database, provider, watcher, event or command.
