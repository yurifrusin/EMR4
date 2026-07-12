# Conductor Sprint Plan — S6 Scope Delta (Amended)

| Field | Value |
|---|---|
| Plan ID | `plan-deepseek-pro-s6-scope-delta` |
| Sprint ID | S6 (amended) |
| Role | conductor |
| Conductor resource | `deepseek-pro-conductor-fallback` (DeepSeek 4 Pro, high reasoning, this session) |
| Date | 2026-07-12 |
| Status | awaiting_orchestrator_acceptance |
| Supersedes | `plan-deepseek-pro-post-s5-next-sprint.md` (original S6 plan) |
| Settings fingerprint | `sha256:5ea2b3522cd6c7238640ad8d251206a64561e3c22d89234a73610063e0d2b77b` |
| direction_dialogue_disposition | `sol_diagnosis_accepted_scope_expanded` |

## 1. Sol Diagnosis — Accepted

Sol independently rejected Lane 1 of the original S6 plan because its claimed
82-pass result was false and its candidate weakened a network-contract test. Sol
then reproduced the failures and found the original S6 diagnosis was incomplete.
The Conductor accepts Sol's four findings:

1. **Four practitioner-directory tests are stale after GraphQL became
   default-on.** `route_practitioner_directory_consumer_api()` and sibling
   helpers still mock and assert the REST route
   `GET /api/v1/practice/practitioners?activeOnly=true&limit=200&offset=0`.
   The live consumer (Sprint 281) now posts `POST /api/v1/graphql` with
   variables `activeOnly: true`, `limit: 200`, `offset: 0`. The uncaught
   GraphQL requests either time out or hit a non-running backend.

2. **Four signed create/update-confirm tests reach proposal handlers but then
   stop before confirm.** Browser-side diagnostic evidence is
   `booking-error: "ahpra is not defined"`.

3. **In `docs/diary/diary.js`, `saveBooking()` defines `practitionerSelection`
   and `practitioner` at lines 7710–7711** via the new
   `resolvePractitionerSelection()` path, but then still passes or stores the
   removed identifier `ahpra` in three places:
   - Line 7827: `appointmentCrossesBreak(ahpra, timeVal, duration)`
   - Line 7854: `appt.practitioner.ahpra_number = ahpra`
   - Line 7927: `practitioner: { ahpra_number: ahpra, id: practitioner.id, ... }`
   
   This is not a test-harness bug. It is a real runtime `ReferenceError`
   regression introduced by the practitioner-directory consumer migration
   (Sprint 264). The `practitioner` object resolved at line 7711 carries
   `practitioner.id`, `first_name`, and `last_name` but does not carry
   `ahpra_number` from the GraphQL directory path. The old `ahpra` variable
   declared from the legacy `<select>` value no longer exists because the
   practitioner selector now uses directory IDs.

4. **Temporary diagnostic instrumentation has been removed; master is clean.**

## 2. Scope Amendment

**The original S6 boundary is insufficient.** It permitted edits only to
`review/test_diary_smoke.py` and explicitly excluded `docs/diary/diary.js`.
Finding 3 is a real runtime `ReferenceError` in `docs/diary/diary.js` — a
production JavaScript file — that cannot be repaired through test-harness
edits alone. The signed-confirm assertions must not be weakened, and the
`ReferenceError` must not be left unfixed.

The Conductor amends the S6 scope as follows:

**Added to in-scope:**

- `docs/diary/diary.js` — repair the three `ahpra` references in
  `saveBooking()` to use the resolved `practitioner` object. The
  `appointmentCrossesBreak` signature expects an AHPRA string; the fix must
  derive an AHPRA value from the available practitioner data (either the
  practitioner's `ahpra_number` field if present in the directory row, or the
  column's `practitioner_ahpra` from the active template). For the smoke-mode
  `ahpra_number` assignments at lines 7854 and 7927, the fix must use the
  column's `practitioner_ahpra` since the directory may not carry it.

**Retained from original S6 in-scope:**

- `review/test_diary_smoke.py` — fix the four stale practitioner-directory
  route mocks to intercept `POST /api/v1/graphql` with the approved
  `Query.practice.practitioners` response shape matching the Sprint 278/279
  mock contract.

**Still out of scope:**

- No change to `app/`, backend routes, schemas, services, database, or
  migrations.
- No Bernoulli D5 expansion, no provider/live-provider wiring, no
  memory/RAG/GraphRAG access.
- No H15/H-series, historical diary runtime, or `local_data` access.
- No GraphQL deployment, readiness, telemetry, or production claims.
- No external patient-client exposure, no Pages deployment change.
- No terminal-status product-policy decision.
- No cross-boundary contract audit (deferred to Sprint S7-ContractAudit).
- No monetary or wall-clock caps.

**All runtime gates remain closed.**

## 3. Worker Allocation

### Claude — NOT USED

Claude subscription reported a real session limit. Fable and Opus share that
unavailable account window. Per `cost_controls.yaml` and protocol alerts,
Claude is unavailable.

### Antigravity — NOT USED

Antigravity was not probed from this conductor session. This sprint is a
mechanical repair with no UX/consumer rendering surface change. Standing down
Antigravity conserves quota for a later sprint where its distinct consumer-UI
veto adds value.

### DeepSeek Flash — 2 WORKER LANES

Per `worker_pool.yaml`, `deepseek-flash-workers` allows up to 3 instances. Two
lanes are allocated here; a third is reserved for S7-ContractAudit.

#### Lane 1: Implementation Owner — `deepseek-s6-scope-delta-repair`

| Field | Value |
|---|---|
| Resource | `deepseek-flash-workers` (instance 1) |
| Model | `deepseek-v4-flash` / high |
| Transport | Deep Code (interactive TTY, durable artifact required) |
| Branch | `codex/s6-scope-delta-repair` |
| Role | Implementation owner |
| Capabilities | implementer, test_engineer |

**Mission:** Apply both repairs in a single cohesive diff.

**(A) Fix `docs/diary/diary.js` — the `ahpra` ReferenceError:**

In `saveBooking()` (line ~7693):

1. After line 7711 (`const practitioner = resolvePractitionerSelection(practitionerSelection);`),
   add a derived `ahpra` value:

   ```js
   const ahpra = practitioner.ahpra_number
     || activeTemplate?.columns.find(c => c.practitioner_id === practitioner.id)?.practitioner_ahpra
     || practitionerSelection;
   ```

   This prioritises a directory-carried `ahpra_number`, falls back to the
   template column's `practitioner_ahpra`, and finally falls back to the raw
   selection value (which is an AHPRA number in legacy template-only mode).

2. The three existing `ahpra` usages (lines 7827, 7854, 7927) require no
   changes — they will now reference the correctly-derived variable.

**(B) Fix `review/test_diary_smoke.py` — the four stale practitioner-directory
route mocks:**

Add a `POST /api/v1/graphql` route handler in the affected tests' route setup
that returns the approved practitioner-directory GraphQL response shape (a
JSON body with `data.practice.practitioners` containing the practitioner
directory array matching the Sprint 278/279 mock contract: `id`, `displayName`,
`roleLabel`, `active`, `defaultLocation { id, name }`).

The four affected test functions (exact names from `test_diary_smoke.py`):
- `test_practitioner_directory_route_data_populates_booking_selector`
- `test_practitioner_directory_selector_keeps_legacy_fallback_for_unmapped_ahpra`
- `test_practitioner_directory_401_fails_closed_with_auth_banner`
- `test_practitioner_directory_limit_200_cap_renders_all_returned_rows`

The fix must preserve the existing REST-route fallback mocks (they are still
needed for the smoke-mode `ENABLE_GRAPHQL_PRACTITIONERS = true` path to be
truly smoke-isolated) and add GraphQL interception. The `/api/v1/graphql`
route handler should inspect the POST body to distinguish practitioner
queries from other GraphQL traffic, and return appropriate responses:
- Success path: `{"data": {"practice": {"practitioners": [...]}}}` with
  directory entries matching the existing smoke-mode practitioner fixtures
- 401 path: `{"errors": [{"extensions": {"code": "UNAUTHORIZED"}}]}`
  (for `test_practitioner_directory_401_fails_closed_with_auth_banner`)
- The `?smoke=true` path in `test_practitioner_directory_smoke_mode_does_not_call_route_and_uses_template_fallback`
  must continue to pass; it asserts zero route calls, which the GraphQL
  interception must honor (the smoke-mode code path in diary.js should use
  the template fallback, not make a real GraphQL call; verify this assertion
  still holds).

**Evidence required:**

1. Before: `pytest review/test_diary_smoke.py -q --tb=short` → 8 failures
   (4 practitioner + 4 signed-confirm) baseline transcript.
2. Root cause for each failure group confirmed.
3. Minimal diff: `docs/diary/diary.js` plus `review/test_diary_smoke.py` only.
4. After: `pytest review/test_diary_smoke.py -q --tb=short` → 0 failures.
5. `node --check docs/diary/diary.js` → pass.
6. `git diff --check` → clean.
7. `git diff --stat` shows only the two permitted files.
8. In `?smoke=true` mode, zero real network requests leak (all GraphQL and
   REST calls intercepted).

**Worker packet:** `orchestration/agent_inbox/deepcode/deepcode-s6-scope-delta.md`
(reuse — this conductor plan is also the Lane 1 implementation brief;
the orchestrator must extract a separate Lane 1 worker packet if needed).

#### Lane 2: Independent Review/Veto — `deepseek-s6-scope-delta-review`

| Field | Value |
|---|---|
| Resource | `deepseek-flash-workers` (instance 2) |
| Model | `deepseek-v4-flash` / high |
| Transport | Deep Code (interactive TTY, durable artifact required) |
| Branch | `codex/s6-scope-delta-review` |
| Role | Independent review/veto |
| Capabilities | code_reviewer, security_reviewer, test_engineer |

**Mission:** Cross-review the Lane 1 fix. Read the Lane 1 completion artifact
and the diff. Run the full smoke suite independently. Verify:

- No regression in previously-passing tests.
- No silent test weakening — especially the signed-confirm assertions must
  remain at full strength.
- No GraphQL traffic leakage in smoke mode.
- No adjacent-gate openings.
- The `diary.js` fix correctly derives `ahpra` from available practitioner
  data in all three code paths (directory-only, legacy-column, mixed).
- The `?smoke=true` path still sends zero real GraphQL requests.

**Evidence:**
- Independent `pytest review/test_diary_smoke.py -q --tb=short` → 0 failures.
- Verification that `?smoke=true` sends zero real GraphQL requests.
- Boundary check: no `app/`, no non-smoke-test file changes beyond the two
  permitted files.
- PASS or REVISION_REQUIRED verdict with specific findings.

**Worker packet:** `orchestration/agent_inbox/deepcode/deepcode-s6-review-smoke.md`
(reuse the existing packet; its review surface is still correct).

## 4. Ownership Boundaries

| Surface | Owner | Review |
|---|---|---|
| `docs/diary/diary.js` (ahpra fix) | Lane 1 | Lane 2 |
| `review/test_diary_smoke.py` (GraphQL mock fix) | Lane 1 | Lane 2 |
| Smoke suite regression | Lane 2: independent run | Orchestrator: final acceptance |

Lane 1 writes both files. Lane 2 reads the diff and runs the suite. No file
overlap between lanes.

## 5. Acceptance Evidence

| Gate | Check | Owner |
|---|---|---|
| Smoke suite clean | `pytest review/test_diary_smoke.py -q --tb=short` → 0 failures | Lane 2 + Orchestrator |
| No production code changes beyond diary.js | `git diff --stat` shows only `docs/diary/diary.js` + `review/test_diary_smoke.py` | Lane 2 + Orchestrator |
| JS syntax | `node --check docs/diary/diary.js` → pass | Orchestrator |
| Whitespace | `git diff --check` → clean | Orchestrator |
| No gate openings | No D5/provider/memory/RAG/H15/trove/write/deployment/GraphQL readiness gate opened | Lane 2 + Orchestrator |
| GraphQL smoke isolation | In `?smoke=true` mode, zero real GraphQL requests sent (all intercepted) | Lane 2 |
| Previously-passing tests unaffected | No regression beyond the 8 diagnosed failures | Lane 2 + Orchestrator |
| Signed-confirm assertions preserved | No weakening, no xfail, no skip | Lane 2 |
| `ahpra` correctly derived in all paths | Directory-only, legacy-column, and mixed scenarios | Lane 2 |

## 6. Verification Plan (Orchestrator)

After both lanes submit:

```powershell
git fetch origin codex/s6-scope-delta-repair codex/s6-scope-delta-review
git diff origin/master...origin/codex/s6-scope-delta-repair --stat
# Expected: docs/diary/diary.js + review/test_diary_smoke.py

pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q
# Expected: 0 failures

node --check docs/diary/diary.js
# Expected: pass

git diff --check origin/master...origin/codex/s6-scope-delta-repair
# Expected: clean

.venv\Scripts\python.exe -m pytest tests/test_sprint_closeout_protocol.py -q
# Expected: pass
```

## 7. Fallback Reason And Reduced Independence

**Fallback reason:** Claude subscription reported a real session limit. Fable
and Opus share that unavailable account window. The conductor allocation order
is [Fable, Opus, DeepSeek Pro, GPT Sol]. Fable and Opus are unavailable, so
DeepSeek 4 Pro via Deep Code is the active conductor.

**Reduced independence:** This conductor session cannot probe Antigravity or
DeepSeek worker availability from the current TTY-only Deep Code context. The
orchestrator retains responsibility for the workspace preflight receipt,
DeepSeek lane management, worker packet dispatch, sprint execution,
integration, and closeout.

## 8. Independent LLM Verifier

**Not risk-triggered.** The scope expansion from test-harness-only to
test-harness-plus-production-JS is material, but the fix surface is
mechanically bounded (three undefined-variable references replaced by a
derived local), the amended plan preserves all existing assertions at full
strength, and no new security/write/deployment/release authority is created.
Deterministic checks (full smoke suite, `node --check`, `git diff --check`)
remain mandatory. An independent LLM verifier is not required under the
current risk classification.

## 9. Unfilled Obligations

| Obligation | Status | Reason |
|---|---|---|
| Claude lane | Not filled | Unavailable (subscription limit) |
| Antigravity lane | Not filled | No consumer/UX surface change; quota conserved |
| Independent LLM verifier | Not required | Risk classification: mechanically bounded fix, no new authority |
| Deferred sprint | S7-ContractAudit | Cross-boundary contract audit follows after smoke suite is healthy |
| Workspace preflight receipt | Deferred to orchestrator | Cannot probe worktrees from this conductor session |

## 10. Sprint Engine State

**Sprint engine: continuing.** S5 is closed. S6 is amended to include the
`docs/diary/diary.js` fix. After orchestrator acceptance, execution begins
without conversational handback.

No user pause condition is triggered: the scope expansion is mechanically
bounded (three line references fixed, four route mocks updated), preserves
all assertions at full strength, and does not open any runtime gate.

## 11. Next Sprint Transition

After S6 closes with a zero-failure smoke suite, the next sprint is
**S7-ContractAudit**: Yuri's requested bounded Ariadne cross-boundary contract
audit (duplicated operational facts: artifact paths, packet/lane identity,
worktree/branch, settings fingerprint, model/reasoning, authority state).
This is a docs/orchestration quality sprint with no runtime, provider,
database, write, deployment, or production gate changes. 1–2 DeepSeek Flash
lanes should suffice.

STATUS: complete
