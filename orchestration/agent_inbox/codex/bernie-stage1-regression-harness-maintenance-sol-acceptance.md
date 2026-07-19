# Bernie Stage 1 Regression-Harness Maintenance — Sol Acceptance

Date: 2026-07-19

Reasoning level: `Sol Extra High`

Decision: `maintenance_pass_ready_for_fresh_tranche_d`

Stage 1 decision: **no `stage1_pass` is issued by this maintenance tranche**

## Rehydration and freeze

This fresh context completed the mandatory five-source rehydration from the
live handover, all 35 Current Baton acceptance artifacts, the frozen Stage 1
plan and Sol review, the strategic transition review, the protected-evidence
and user-decision boundaries, and the appointment-first sources required by the
EMR4 API Steward.

All five Git refs were verified at
`2d3fa717d612add9d1f871daf9e899751c5d210c`. The passed receipts are:

- rehydration:
  `orchestration/agent_inbox/codex/bernie-stage1-regression-harness-maintenance-rehydration-receipt.json`,
  SHA-256
  `b023d7495ce3eda365ad9e4009d6523e48d8c1bcaa44351b658edab870e0aac5`;
- pre-plan:
  `orchestration/agent_inbox/codex/bernie-stage1-regression-harness-maintenance-preplan-receipt.json`,
  SHA-256
  `ec6ab49f7cb392ce8eb1f1034dec5da6c4b354d12a2fafb8da5deed97b8cf556`;
  and
- verifier acceptance:
  `orchestration/agent_inbox/codex/bernie-stage1-regression-harness-maintenance-preacceptance-receipt.json`,
  SHA-256
  `d25e1e1ab93070fd6ccaded35b08eded18794d23d5b141ebae9242d13943a25e`.

Each receipt names the five required sources:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

Before edits, the exact nine-node population reproduced as `9 failed`, and the
three owned test files matched their committed blobs. The frozen maintenance
contract is `docs/bernie-stage1-regression-harness-maintenance-plan.md`,
SHA-256
`df3710e7d357e6d4c5635b40375cfb284d6c251855936c11eeb7936d0bae49a0`.

## Accepted maintenance

Only these three historical test files changed:

| File | Final SHA-256 |
|---|---|
| `tests/test_bernie_sprint98_release_gates.py` | `6612416e52c47a631777a57d4b423498456cdba86b1e81fb6598c363513f72ac` |
| `tests/test_bernie_wrapper_confirmation_review_harness.py` | `470ebe9936696cbf043100eb2c32c0d010d05e166a621170474741a1adadc24a` |
| `tests/test_bernie_confirmed_flow_review_harness.py` | `edfe0daca89ca2f80e0be33b08832c28cb378a2a54cdb15f45ac45b9fe247405` |

The changes preserve rather than weaken the current contracts:

- historical 2026-06-22 wrapper/confirmed-flow cases pin the clinic clock to
  the authored fixture date, so freshness remains fail-closed for genuinely
  past dates while the historical Monday roster and conflict fixture stay
  deterministic;
- every `confirm-bernie` request now sends an explicit nonblank
  `Idempotency-Key`;
- staff-review payload confirmation asserts verified signed evidence, while
  direct historical selection clients assert the explicit
  `legacy_unsigned_confirmation_compat` audit tag; and
- competing synthetic appointments are committed before the HTTP command so a
  route-level rollback cannot erase already-authoritative test setup.

No application, API schema, migration, Diary/UI, provider/runtime, policy,
replay, scorer, protected-evidence, historical-diary, or Stage 2 file changed in
this maintenance tranche.

## Verification

All repository pytest runs were serial.

- frozen nine-node population after maintenance: `9 passed`;
- all three owned harness files: `16 passed`;
- core Sprint 98, signed evidence, idempotency, and freshness population:
  `63 passed`;
- supervised-booking, interpretation, receipt/accessibility, wrapper, and
  confirmed-flow population: clean rerun `63 passed`;
- API Spine artifacts, accessible confirmation, and booking classifier:
  `81 passed`;
- exact protected-safe Diary allowlist: 115 named test functions expanded to
  `139 passed`, labelled `route_intercepted_browser`; and
- fourteen immutable R2 receipts, correction artifacts, backend replay, and
  screenshot SHA-256 bindings reproduced exactly.

The first 63-case supervised-flow run returned `62 passed, 1 failed` when
`test_keyboard_activation_submits_confirm_space` timed out waiting five seconds
for the mocked receipt after native Space activation. No source was changed for
that node. It then passed in isolation, in the clean 63-case rerun, and again in
the independent 81-case API/accessibility/classifier batch. The failed attempt
is retained as a transient timing observation rather than discarded or treated
as a product override.

Additional checks passed:

- exact Python compilation of the Stage 1 product, harness, freshness, and
  maintained test files;
- `node --check docs/diary/diary.js`;
- Bandit at high-severity threshold over the changed product/harness Python
  surfaces;
- tracked-diff whitespace validation;
- interpretation readiness remains
  `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, and `runtime_gate_decision=blocked`; and
- provider-boundary readiness remains `default_provider=disabled`,
  `live_provider_enabled=false`, `provider_calls_performed=false`, with no
  route, database, memory/RAG, or historical-diary access.

## Preserved database evidence

Read-only inspection of the preserved disposable database
`gp_pms_stage1_2d3fa717_20260719_r2` still returns exactly:

- one appointment;
- one appointment audit linked to that appointment; and
- one completed `confirmed_write` idempotency result targeting that
  appointment.

The existing idempotency row's optional direct `audit_log_id` remains null.
That unchanged structural correlation gap is not required by the frozen Stage 1
claim, which separately requires a matching appointment audit and a completed
idempotency result. Complete command/audit correlation remains part of the
separately unauthorized Stage 2 foundation and is disclosed here so it is not
mistaken for evidence added by this harness repair.

## API Spine and authority decision

The maintained evidence preserves the mixed API spine: proposal/search/select
remain non-mutating, `confirm-bernie` remains the sole Stage 1 REST mutation,
staff confirmation and backend revalidation remain mandatory, and GraphQL,
the fake provider, the Diary client, and the harness receive no write
authority.

The nine historical G10 failures are resolved without narrowing the frozen
regression set or overriding a failed gate. The candidate is ready for a new,
fresh-context Tranche D acceptance. This maintenance context does not issue
`stage1_pass`, commit, push, move protected refs, begin Stage 2, deploy, release,
call a provider, mutate cloud state, or open any protected or non-synthetic
surface.

## Closeout and handoff

The required compact non-PHI closeout notification was delivered successfully
with Pushover request ID `2077d145-cf9f-4fdb-bdfc-d7e2113999c4`. It states that
the nine failures are repaired, the explicit regressions and 139 Diary cases
are green, no Stage 1 pass was issued, and the next work is fresh Tranche D
acceptance.

The live baton and frozen Stage 1 plan now name
`maintenance_pass_ready_for_fresh_tranche_d`. The next tranche must use a fresh
context, repeat the full five-source rehydration, and independently apply the
frozen Stage 1 gates. This context deliberately leaves integration, commit,
push, protected-ref movement, and any `stage1_pass` decision to that acceptance
tranche.
