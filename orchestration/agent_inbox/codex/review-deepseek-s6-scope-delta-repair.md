# DeepSeek S6 Scope Delta Repair — Lane 1 Completion Artifact

| Field | Value |
|---|---|
| Plan ID | `plan-deepseek-pro-s6-scope-delta` |
| Worker lane | Lane 1 — implementation owner |
| Resource | `deepseek-flash-workers` (instance 1) |
| Model | `deepseek-v4-flash` / high |
| Transport | Deep Code (interactive TTY) |
| Worktree | `EMR4-worktrees\deepcode-s6-scope-delta-repair` |
| Packet | `orchestration/agent_inbox/deepcode/deepcode-s6-scope-delta-repair.md` |
| Completion artifact | `orchestration/agent_inbox/codex/review-deepseek-s6-scope-delta-repair.md` |

---

## Changed Files

| File | Change type |
|---|---|
| `docs/diary/diary.js` | Repair A — 3 lines added |
| `docs/diary/diary.html` | Cache-bust `?v=` bump: 182 → 183 |
| `review/test_diary_smoke.py` | Repair B — GraphQL route interception + 4 test updates |

**Excluded:** No other files changed. No `app/`, no backend, no migrations, no routes, no providers, no H15/H-series, no RAG/GraphRAG, no memory, no `local_data`, no Pages deployment.

---

## Repair A — Runtime ReferenceError

### Root Cause

In `saveBooking()` (line ~7710), the `practitioner` object is resolved via the new `resolvePractitionerSelection()` which returns `{id, first_name, last_name}` from the directory. The legacy `ahpra` local variable was removed during the GraphQL migration (Sprint 264) but three downstream usages still reference it:

1. Line 7827: `appointmentCrossesBreak(ahpra, timeVal, duration)` — break-check call
2. Line 7854: `appt.practitioner.ahpra_number = ahpra` — smoke-mode edit assignment
3. Line 7927: `practitioner: { ahpra_number: ahpra, ... }` — smoke-mode create assignment

All three produce `ReferenceError: ahpra is not defined` before any signed-confirm flow completes.

### Fix

After `resolvePractitionerSelection()`, derive `ahpra` with a three-level fallback:

```js
const ahpra = practitioner.ahpra_number
  || activeTemplate?.columns.find(c => c.practitioner_id === practitioner.id)?.practitioner_ahpra
  || practitionerSelection;
```

1. **Directory-carried `ahpra_number`** — if the practitioner directory row carries it (future schema expansion)
2. **Template column `practitioner_ahpra`** — the column mapped to this practitioner's `id`
3. **Raw selection value** — legacy fallback (the old AHPRA string from the `<select>`)

The three downstream references (lines 7827, 7854, 7927) require no further changes since `ahpra` is now defined in scope.

---

## Repair B — Default-On GraphQL Test Contract

### Root Cause

The diary's `ENABLE_GRAPHQL_PRACTITIONERS = true` (line 17) makes `loadPractitionerDirectory()` call `POST /api/v1/graphql` as the default path. Four tests in `test_diary_smoke.py` still mocked and asserted the old REST path `GET /api/v1/practice/practitioners`. The unhandled GraphQL requests either timed out or hit the non-existent local server endpoint, causing failures in these four tests:

1. `test_practitioner_directory_route_data_populates_booking_selector`
2. `test_practitioner_directory_selector_keeps_legacy_fallback_for_unmapped_ahpra`
3. `test_practitioner_directory_401_fails_closed_with_auth_banner`
4. `test_practitioner_directory_limit_200_cap_renders_all_returned_rows`

### Fix

**`route_practitioner_directory_consumer_api()`** rewritten to intercept `POST /api/v1/graphql` as the primary path:

- Parses the POST body to extract the GraphQL query and variables
- Identifies practitioner-directory queries by checking for `"GetPractitioners"` in the query
- Returns the correct GraphQL response shape: `{"data": {"practice": {"practitioners": [...]}}}`
- Transforms REST-style `practitioner_rows` into the GraphQL response shape (only `id`, `displayName`, `roleLabel`, `active`, `defaultLocation`)
- For 401 tests, returns HTTP 401 with `{"errors": [{"extensions": {"code": "UNAUTHORIZED"}}]}`
- Keeps the REST `/api/v1/practice/practitioners` handler as a fallback surface (still exercised by legacy paths)
- Captures GraphQL requests in a new `captured["graphql_requests"]` list alongside the existing `captured["practitioner_requests"]`

**Four test functions updated** to assert GraphQL request details:
- Check `captured["graphql_requests"]` instead of `captured["practitioner_requests"]`
- Assert POST method and `/api/v1/graphql` URL
- Assert `authorization` header starts with `Bearer`
- Assert query contains `GetPractitioners`
- Assert variables are `{activeOnly: true, limit: 200, offset: 0}`
- Assert query does NOT request sensitive fields (`provider_number`, `ahpra_number`, `prescriber_number`, `hpi_i`, `email`, `phone`, `address`)
- Assert no REST fallback was used (`len(captured["practitioner_requests"]) == 0`)
- Allow POST (non-mutating GraphQL) but reject PUT/PATCH/DELETE

**Smoke-mode test** (`test_practitioner_directory_smoke_mode_does_not_call_route_and_uses_template_fallback`) — unchanged. Smoke mode sets `practitionerDirectory = []` directly (diary.js line 4155) without calling `loadPractitionerDirectory()`, so neither GraphQL nor REST paths are hit.

---

## Verification Results

### Pre-fix baseline: 8 failures (4 practitioner-directory + 4 signed-confirm blocked by `ahpra` ReferenceError)

### Post-fix: 0 failures, all 139 tests pass

| Check | Result |
|---|---|
| `pytest review/test_diary_smoke.py -q --tb=short` | 139 passed, 0 failed, 0 skipped, 0 xfailed |
| `node --check docs/diary/diary.js` | pass |
| `python scripts/check_frontend_versions.py` | pass (diary.js 182→183 verified) |
| `git diff --check` | clean (no whitespace errors) |
| `git diff --stat` | 3 files changed (plus completion artifact) |

### Boundary Statement

- No `app/`, backend routes, schemas, services, database, or migrations touched
- No Bernoulli D5 expansion, no provider/live-provider wiring, no memory/RAG/GraphRAG access
- No H15/H-series, historical diary runtime, or `local_data` access
- No GraphQL deployment, readiness, telemetry, or production claims
- No external patient-client exposure, no Pages deployment change
- No terminal-status product-policy decision
- No cross-boundary contract audit (deferred to S7)
- All runtime gates remain closed
- All signed-confirm assertions preserved at full strength
- No test names changed, no skips/xfails added or removed
- No adjacent surfaces altered

### Artifact Attestation

All repairs were applied in a disposable worktree (`deepcode-s6-scope-delta-repair`). No commits, pushes, merges, or master modifications were performed. The diff is limited to the three permitted implementation files plus this completion artifact.

STATUS: complete
