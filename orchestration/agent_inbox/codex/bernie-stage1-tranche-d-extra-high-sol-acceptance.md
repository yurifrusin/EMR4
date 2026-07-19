# Bernie Stage 1 Tranche D — Extra High Final Acceptance

Date: 2026-07-19

Reasoning level: `Sol Extra High`

Decision: `stage1_pass`

Claim scope: `local_synthetic_provider_free_supervised_booking_vertical`

## Final decision

Every frozen Stage 1 gate passes on the exact bounded candidate. In a local,
synthetic development environment, the real Diary can take the frozen booking
instruction through the real FastAPI backend and isolated PostgreSQL database;
proposal remains non-mutating; an authenticated receptionist explicitly
confirms; and the backend revalidates and creates exactly one appointment, one
matching appointment audit, one completed idempotency result, and a complete
typed receipt. Ambiguity, no-slot, replay, duplicate, and stale/conflict paths
remain fail-closed without an additional Bernie write.

This acceptance is not production readiness, clinical validation, provider
selection, deployment, release, PII authority, migration authority, durable
session authority, or Stage 2 authority.

## Fresh-context binding

This named tranche repeated the mandatory five-source rehydration from:

1. `live_handover_current_baton`;
2. `current_authority_allocation`;
3. `active_plan_and_acceptance`;
4. `protected_evidence_boundaries`; and
5. `git_refs_and_worktree`.

It read `AGENTS.md`, all 37 Current Baton acceptance artifacts, the frozen
Stage 1 plan and review, the strategic transition review, and the appointment-
first API Spine sources required by the EMR4 API Steward. The receipts are:

- rehydration:
  `orchestration/agent_inbox/codex/bernie-stage1-tranche-d-extra-high-reacceptance-receipt.json`,
  SHA-256
  `eb4b89782c4e94dc9a9ac4038f6e7f5e6ea49362e2c308040075bb61d01203e3`;
- verifier acceptance:
  `orchestration/agent_inbox/codex/bernie-stage1-tranche-d-extra-high-preacceptance-receipt.json`,
  SHA-256
  `d25e1e1ab93070fd6ccaded35b08eded18794d23d5b141ebae9242d13943a25e`.

Both receipts pass and explicitly name all five sources. Before acceptance,
`HEAD`, local `master`, local `handoff/current`, `origin/master`, and
`origin/handoff/current` were all
`2d3fa717d612add9d1f871daf9e899751c5d210c`.

No protected holdout, historical diary material, blocked external corpus,
provider prompt, cloud surface, PII, production, deployment, release,
migration, or Stage 2 surface was opened.

## Exact candidate and evidence

The accepted R2 execution record is
`docs/bernie-stage1-r2-execution-evidence.json`, SHA-256
`cd5b230d61d93cd41e76dfae3a54e3c96d32bab4f98969e40dfcbc4a7bf11ec9`.
Its happy path is correctly labelled
`live_local_browser_backend_postgres`; direct HTTP replay is
`live_local_backend_postgres`; and the Diary breadth suite is
`route_intercepted_browser`.

The bounded product correction remains exactly two comparison changes in
`app/routers/appointments.py`, SHA-256
`533b44747c7b2c928c284a1fc3063ee9d2ff7f170cd877651369166da80100c0`:
a reference date is stale only when it predates clinic-local today. Its focused
test file is `tests/test_bernie_reference_date_freshness.py`, SHA-256
`487ab16dfad6219371ce1e77cdb236d06a3ed65a93d1cf78efd9d89a38cf3fca`.
The rule preserves fail-closed handling for genuinely past dates while
permitting an explicitly pinned current or future Diary/session date. It adds
no policy, authority, migration, route, or mutation family.

The accepted historical regression-harness maintenance is bound by
`orchestration/agent_inbox/codex/bernie-stage1-regression-harness-maintenance-sol-acceptance.md`,
SHA-256
`08866c1b6a47555abf498ea2f51e75a5a4dc8448011351d76b8404946e2d8f79`.
Its three final file hashes reproduce exactly:

| File | SHA-256 |
|---|---|
| `tests/test_bernie_sprint98_release_gates.py` | `6612416e52c47a631777a57d4b423498456cdba86b1e81fb6598c363513f72ac` |
| `tests/test_bernie_wrapper_confirmation_review_harness.py` | `470ebe9936696cbf043100eb2c32c0d010d05e166a621170474741a1adadc24a` |
| `tests/test_bernie_confirmed_flow_review_harness.py` | `edfe0daca89ca2f80e0be33b08832c28cb378a2a54cdb15f45ac45b9fe247405` |

All fourteen immutable R2 receipt, correction, backend-replay, and screenshot
SHA-256 bindings reproduce exactly. The protected-safe Diary file remains
SHA-256
`011f237a97f0ad3939cc02fc470943d9440b6a540d23c37f7f1840d1582b1bd9`,
contains no protected-path reference, and exposes exactly 115 named test
functions.

## Gate decision

| Gate | Result | Accepted evidence |
|---|---|---|
| G1 Boundary | pass | Loopback, synthetic-only, fake-provider, cloud-free, protected-free execution; all blocked surfaces remain closed |
| G2 Authentication and tenancy | pass | Authenticated synthetic receptionist, same-practice pilot eligibility, roster and practice scope proven |
| G3 Proposal has no write | pass | S1 reached a usable proposal with 0 appointment, 0 audit, and 0 idempotency rows before confirmation |
| G4 Human authority | pass | Visible distinct confirmation action; no silent or autonomous confirmation path |
| G5 Backend authority | pass | Backend revalidation produced exactly one appointment, one matching linked audit, and one completed confirmed-write idempotency result targeting that appointment |
| G6 Receipt and readback | pass | Complete `appointment.confirmation_receipt.v1` and authoritative Diary reload/readback |
| G7 Failure safety | pass | Replay, exact duplicate, ambiguity, no-slot, and stale/conflict cases create no extra Bernie write |
| G8 Evidence integrity | pass | Evidence labels are exact; R2 browser happy path is non-intercepted; no credentials, tokens, or raw headers are committed |
| G9 API Spine | pass | Proposal/search/session paths remain non-mutating; `confirm-bernie` is the sole Stage 1 REST mutation; GraphQL/provider/client have no write authority |
| G10 Regression | pass | Complete explicit regression, Diary, syntax, security, readiness, boundary, artifact, and whitespace gates pass |

The preserved database `gp_pms_stage1_2d3fa717_20260719_r2` contains exactly
one appointment, one appointment-linked audit, and one completed
`confirmed_write` idempotency result targeting the same appointment. The
idempotency row's optional direct `audit_log_id` remains null. This is the
previously disclosed complete-correlation gap reserved for a separately
authorized Stage 2 foundation; it does not replace or weaken the frozen Stage
1 requirement for a matching audit and completed idempotency result.

## Fresh verification

All pytest processes ran serially:

- core Sprint 98, signed evidence, idempotency, and freshness: `63 passed`;
- supervised booking, interpretation, receipt/accessibility, wrapper, and
  confirmed flow: `63 passed`;
- API Spine artifacts, accessibility, and classifier: `81 passed`;
- exact protected-safe Diary allowlist: 115 named nodes expanded to
  `139 passed`, labelled `route_intercepted_browser`.

No test failed or was deselected. The transient Space-key timeout retained by
the maintenance acceptance did not recur.

Additional checks passed:

- Python compilation of the Stage 1 product, harness, freshness, and maintained
  historical tests;
- `node --check docs/diary/diary.js`;
- Bandit with the high-severity threshold over the changed product/harness
  Python surfaces;
- `git diff --check`;
- interpretation readiness remains
  `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, and `runtime_gate_decision=blocked`;
- provider boundary remains `default_provider=disabled`,
  `live_provider_enabled=false`, `provider_calls_performed=false`, with no
  route, database, memory/RAG, or historical-diary access.

Fresh visual review confirms the S1 proposal, S2 receipt/readback, S3 exact
duplicate, S4 ambiguity, and S5 no-slot states. The S6 screenshot shows the
staged proposal before conflicting confirmation, as already disclosed; the
terminal typed conflict and zero-write result are established by the sanitized
R2 request/outcome record and database counts rather than that image alone.

## API Spine and authority disposition

The accepted product path preserves the mixed API spine. Bernie may interpret,
clarify, retrieve bounded context, and prepare proposals. The authenticated
staff member confirms. FastAPI/PostgreSQL owns identity, availability,
conflicts, freshness, idempotency, the appointment write, audit, and receipt.
The fake provider, Diary client, GraphQL read graph, test harness, and any model
have no write authority.

No independent external review was added in this final tranche. The product
change is the already bounded two-expression freshness correction; the later
maintenance is tests-only; and Sol Extra High directly reproduced the exact
browser, backend, database, API Spine, security, and regression gates. Worker
and subagent dispatch would not add a separable implementation artifact or
independent authority to this serial acceptance.

During protected integration, PR 36's Python Security job exposed a mechanical
annotation mismatch in the new local harness: four fixed-loopback `urlopen`
calls carried Ruff's `# noqa: S310` form, which Bandit does not consume. The
reviewed Bandit baseline remains unchanged at exactly its two historical B324
Git-identity findings. Only those four annotations changed to the scoped
`# nosec B310` form; all URLs remain hard-coded to loopback. The complete
Bandit gate then passed with exactly two reviewed findings, the two security-
tooling contract tests passed, Python compilation passed, and
`git diff --check` passed. This correction changes no Stage 1 behavior,
acceptance meaning, database state, provider boundary, or protected evidence.

Stage 1 is complete with `stage1_pass`. Stage 2 does not begin automatically.
Its durable session, migration, concurrency, structural security, retention,
recovery, and complete command/audit-correlation scope requires a new Yuri
decision.

The integration, pre-commit, and pre-push receipts all pass with the same five-
source binding:

- integration: SHA-256
  `d1575dc4757295bb3203bab1aff3d906cbccc1fe5ea5ed161f5560d9798fac59`;
- pre-commit: SHA-256
  `567b7ce0e4648e6392feeaec230d60dc0c873e2fa6f9f4663df02ad4e0b95bd5`;
- pre-push: SHA-256
  `5cc3bc885b25ba1a47eae7d6b41f5908e35447099bbe126cefa9281cb59270b8`.

Git integration uses `codex/stage1-final-acceptance` and the normal check-gated
protected-branch workflow. Final PR, commit, ref-alignment, and notification
evidence will be added by the closeout carrier after successful integration.
