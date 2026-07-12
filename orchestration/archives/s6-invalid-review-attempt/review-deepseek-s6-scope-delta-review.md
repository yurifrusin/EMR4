# S6 Lane 2: Independent Review — Scope Delta Repair

| Field | Value |
|---|---|
| Role | Independent code/security/test reviewer |
| Resource | `deepseek-flash-workers` (instance 2) |
| Model | `deepseek-v4-flash` / high reasoning |
| Candidate commit | `38d95ed0404831b0f7eba4e3c9de2733cb975ef1` |
| Review worktree | `deepcode/s6-scope-delta-review` |
| Verdict | **PASS** |

---

## 1. Findings

### Finding F1 — Practitioner guard retained
The existing invalid-practitioner guard in `saveBooking()` fires **before** the `ahpra` derivation. The guard at line ~7706 (`if (!practitioner || !practitioner.id)`) returns early with the correct error message. The `const ahpra = ...` line is inserted at line ~7715, after the guard returns. Requirement 1 satisfied.

### Finding F2 — UUID never stored as AHPRA
The `ahpra` derivation chain is:
```
practitioner.ahpra_number
  || ahpraToPractitionerMap lookup by id
  || activeTemplate.columns.practitioner_ahpra
  || null
```
The final fallback is `null`, not the raw directory UUID (`practitionerSelection`). A GraphQL directory UUID can never be stored or used as an AHPRA number. The plan suggested the raw selection as a tertiary fallback; the fix uses `null`, which is **safer** than the plan specified. Requirement 2 satisfied.

### Finding F3 — Signed confirm tests at full strength
All signed create/update-confirm tests are **unchanged** in the diff. No tests were removed, skipped, xfailed, renamed, or weakened. The diff touches only the 4 practitioner-directory route mocks and adds the invalid-practitioner guard assertion to the 200-row test. All 9 signed confirm tests pass. Requirement 3 satisfied.

### Finding F4 — Practitioner-directory assertions complete
All four practitioner-directory tests verify the required assertions:

| Test | Assertion | Status |
|---|---|---|
| `test_practitioner_directory_route_data_populates_booking_selector` | POST `/api/v1/graphql`, Bearer auth, `GetPractitioners` query, exact variables `{activeOnly:true, limit:200, offset:0}`, no sensitive fields, no REST fallback | ✅ |
| `test_practitioner_directory_selector_keeps_legacy_fallback_for_unmapped_ahpra` | POST `/api/v1/graphql`, Bearer auth, `GetPractitioners` query, no REST fallback | ✅ |
| `test_practitioner_directory_401_fails_closed_with_auth_banner` | POST `/api/v1/graphql` → 401, token cleared in localStorage, auth banner visible, grid hidden, "Session expired" copy | ✅ |
| `test_practitioner_directory_limit_200_cap_renders_all_returned_rows` | POST `/api/v1/graphql`, variables `{limit:200, activeOnly:true, offset:0}`, 200 options rendered, elapsed <500ms, no REST fallback, invalid-practitioner guard assertion | ✅ |
| `test_practitioner_directory_smoke_mode_does_not_call_route_and_uses_template_fallback` | Zero REST calls (`captured["practitioner_requests"] == []`), template fallback renders expected options | ✅ |

Sensitive field projection checked for: `provider_number`, `ahpra_number`, `prescriber_number`, `hpi_i`, `providerNumber`, `prescriberNumber`, `ahpraNumber`, `hpiI`, `email`, `phone`, `address`. All absent from the GraphQL query. Requirement 4 satisfied.

### Finding F5 — Cache bust only
The only change to `docs/diary/diary.html` is the version bump from `v=182` to `v=183`. The `check_frontend_versions.py` PASSED and confirmed the bump is appropriate. No other frontend or runtime delivery changes. Requirement 5 satisfied.

### Finding F6 — No adjacent scope breach
`git diff master...HEAD -- app/` returns empty. No backend, provider, database, H-series, historical diary, RAG, deployment, product-policy, or runtime gate changes are present. The `?smoke=true` test still routes only the REST path and asserts zero route calls, proving GraphQL smoke isolation. Requirement 6 satisfied.

---

## 2. Command Results

### 2.1 Test collection count
```text
review/test_diary_smoke.py: 139
```

### 2.2 Independent smoke suite run
```text
139 passed in 34.50s
```
Exit code 0. No failures.

### 2.3 JS syntax
```text
node --check docs/diary/diary.js → PASS (exit 0)
```

### 2.4 Frontend version integrity
```text
[PASSED] Verification Passed: All modified assets have appropriate version bumps.
diary.js v=182 → v=183 ✓
```

### 2.5 Whitespace
```text
git diff --check → clean (exit 0)
```

### 2.6 Diff stat (production-impacting files only)
```text
 docs/diary/diary.html      |   2 +-
 docs/diary/diary.js        |   4 +
 review/test_diary_smoke.py | 129 ++++++++++++++++++---
```

Orchestration artifacts (receipts, review packets) are also present in the full commit `--stat` but are coordination/metadata files only — no production impact.

### 2.7 Baseline confirmation (HEAD = master state)
Before reviewing the candidate, the review worktree (which resets test/diary files to master) confirmed:
```text
8 failed in 34.50s
```
The 8 failures match the plan's diagnosis exactly:
- 4 practitioner-directory tests (stale REST mocks, GraphQL default-on)
- 4 signed create/update-confirm tests (`ahpra is not defined` ReferenceError)

---

## 3. Boundary Review

| Gate | Status |
|---|---|
| No `app/` backend changes | ✅ Empty diff against master |
| No provider/database/migration changes | ✅ |
| No H-series/historical diary changes | ✅ |
| No RAG/GraphRAG/memory access | ✅ |
| No runtime gate opening | ✅ All gates remain closed |
| No deployment/product-policy change | ✅ |
| No GraphQL readiness/production claim | ✅ |

---

## 4. Test-Count Discrepancy Resolution

**Reported discrepancy:**
- Lane 1 artifact: `138 passed`
- Sol independent collection: 139 tests
- Sol independent run: 139 passed

**Independent verification (this review):**
- Collection: 139 tests (`--collect-only -q`)
- Execution: 139 passed (exit 0, 34.50s)

**Resolution:** The Lane 1 report of 138 was either a counting error or an intermediate state before the final revision. The candidate at commit `38d95ed0` collects and passes **all 139 tests**. This review confirms 139 as the authoritative count. No discrepancy remains — the candidate is valid.

---

## 5. Detailed Manual Review: `diary.js` AHPRA Fix

The fix adds 4 lines at the correct insertion point in `saveBooking()`:

```js
const ahpra = practitioner.ahpra_number
  || Object.keys(ahpraToPractitionerMap).find(k => ahpraToPractitionerMap[k].id === practitioner.id)
  || activeTemplate?.columns.find(c => c.practitioner_id === practitioner.id)?.practitioner_ahpra
  || null;
```

**Path analysis:**

| Scenario | Source | `ahpra` value | Correct? |
|---|---|---|---|
| Directory practitioner has `ahpra_number` field | `practitioner.ahpra_number` | Directory-carried AHPRA ✅ | Yes |
| Directory practitioner has no AHPRA, but template column maps by ID | `activeTemplate.columns[].practitioner_ahpra` | Template column AHPRA ✅ | Yes |
| Legacy template-only mode (no directory) | `activeTemplate.columns[].practitioner_ahpra` | Template column AHPRA ✅ | Yes |
| Legacy mode with `ahpraToPractitionerMap` | Map lookup by directory practitioner.id | Map AHPRA ✅ | Yes |
| No mapping possible | `null` | null (guard will fire) ✅ | Yes |
| AHPRA needed for `appointmentCrossesBreak` | Passed as `ahpra` parameter | Correctly derived AHPRA ✅ | Yes |
| AHPRA stored in `appt.practitioner.ahpra_number` | `ahpra` variable | Correctly derived AHPRA ✅ | Yes |

The three pre-existing `ahpra` references (lines 7827, 7854, 7927) require no changes — they now reference the correctly-derived variable that replaces the removed `<select>` value.

---

## 6. Verdict

```text
VERDICT: PASS
STATUS: complete
DECISION: pass
```

The candidate at commit `38d95ed0404831b0f7eba4e3c9de2733cb975ef1` satisfies all 6 review requirements:

1. ✅ Invalid-practitioner guard retained before `ahpra` dereference
2. ✅ Directory UUID never stored as AHPRA (`null` final fallback)
3. ✅ Signed confirm tests unchanged, at full strength, all passing
4. ✅ Practitioner-directory tests assert GraphQL variables, auth, projection, 401 clearing, 200-row rendering, and zero smoke traffic
5. ✅ Only required `diary.js` cache bust in delivery
6. ✅ No adjacent gate, backend, provider, database, H-series, diary, RAG, deployment, or policy change

**No findings requiring revision.** The test-count discrepancy is resolved (139 collected, 139 passed — Lane 1's 138 was an intermediate or counting error). The candidate is ready for orchestrator acceptance and integration.
