# S6 Lane 2: Independent Static Veto Review — DeepSeek Flash

**Role:** independent code/security/reviewer  
**Review worktree:** `C:\Users\sarashera\EMR4-worktrees\deepcode-s6-scope-delta-review`  
**Observed HEAD:** `0690f77dffb2d36178d3773e841f5716711d0606`  
**Candidate commit in ancestry:** `8b91eccc`  
**Sol verification HEAD:** `b0536c31` (ancestor of current HEAD; subsequent commits are docs-only)  
**Review date:** 2026-07-13  
**Review artifact:** `orchestration/agent_inbox/codex/review-deepseek-s6-scope-delta-review-v3.md`

---

## Findings

### Finding 1 — Runtime `ahpra` ReferenceError (Fixed)

**Root cause:** `saveBooking()` in `docs/diary/diary.js` resolved a practitioner via the new `resolvePractitionerSelection()` directory path but then referenced the removed `ahpra` variable in three locations (break check, smoke fixture assignment, payload construction). This was a real `ReferenceError` regression introduced by the practitioner-directory consumer migration.

**Fix (commit `8b91eccc`):** Introduced a derived `ahpra` local after the practitioner null-guard:

```js
const ahpra = practitioner.ahpra_number
    || Object.keys(ahpraToPractitionerMap).find(k => ahpraToPractitionerMap[k].id === practitioner.id)
    || activeTemplate?.columns.find(c => c.practitioner_id === practitioner.id)?.practitioner_ahpra
    || null;
```

**Assessment — PASS.** Three critical properties verified via static source review:

1. **Null guard precedes dereference:** `if (!practitioner || !practitioner.id) { ... return; }` at lines 7712–7716 executes BEFORE `practitioner.ahpra_number` is read at line 7717. No TypeError on invalid selection.

2. **No directory UUID can become AHPRA:** The fallback chain ends with `|| null`, NOT `|| practitionerSelection`. The revision-1 defect (which passed a UUID through `practitionerSelection`) is corrected. The chain uses three safe sources: direct `practitioner.ahpra_number` from directory data, reverse-mapping via `ahpraToPractitionerMap` (legacy path), and template column `practitioner_ahpra`. All are known AHPRA-bearing sources.

3. **Existing `ahpra` usages (break check, smoke assignments, payload) now resolve correctly** without any further code changes required.

### Finding 2 — Stale Practitioner-Directory Route Mocks (Fixed)

**Root cause:** Four tests asserted `GET /api/v1/practice/practitioners` with REST query parameters. The live consumer now uses `POST /api/v1/graphql`. The uncaught GraphQL requests either timed out or hit a non-running backend.

**Fix (commit `8b91eccc`):** `route_practitioner_directory_consumer_api()` was extended with a `POST /api/v1/graphql` interceptor. The four affected tests now assert:

| Test | Key Assertions |
|---|---|
| `test_practitioner_directory_route_data_populates_booking_selector` | GraphQL POST, auth header, `GetPractitioners` in query, exact variables `{activeOnly:true, limit:200, offset:0}`, sensitive-field projection blocked (both REST and GraphQL names), zero REST fallback, no PUT/PATCH/DELETE |
| `test_practitioner_directory_selector_keeps_legacy_fallback_for_unmapped_ahpra` | GraphQL POST, auth, `GetPractitioners`, no REST fallback, unmapped AHPRA falls back to template `practitioner_ahpra` |
| `test_practitioner_directory_401_fails_closed_with_auth_banner` | GraphQL 401 (HTTP, not 200-error-body), token cleared, auth banner displayed, no REST fallback |
| `test_practitioner_directory_limit_200_cap_renders_all_returned_rows` | GraphQL variables verified, 200 options rendered, elapsed < 500ms, invalid-practitioner guard fires `"Practitioner ID not found"` |

**Assessment — PASS.** The GraphQL interceptor correctly inspects POST body to distinguish practitioner queries. The REST handler is preserved as a fallback for legacy paths. The 401 test uses HTTP 401 status (not 200-with-error-body), correctly exercising `apiFetch()` token clearing. The smoke-isolation test (`?smoke=true`) is unchanged and still asserts zero practitioner-directory requests.

### Finding 3 — Invalid-Practitioner Guard Assertion (Added)

**Fix:** `test_practitioner_directory_limit_200_cap_renders_all_returned_rows` now includes a focused assertion that calls `saveBooking()` with an unresolvable practitioner UUID after establishing provisional patient context. Assertion checks for `"Practitioner ID not found"` in `#booking-error`.

**Assessment — PASS.** The test correctly sets `provisionalName` before calling `saveBooking()`, bypassing the patient validation guard and exercising the practitioner null-guard path. No test was weakened, skipped, or xfailed.

### Finding 4 — Unused Query Fragment (Removed)

**Revision-1 fix:** The unused `PRACTITIONER_DIRECTORY_GRAPHQL_QUERY_FRAGMENT` local was removed. Not present in current source — confirmed via `rg` search.

**Assessment — PASS.**

### Finding 5 — Sensitive-Field Projection Assertion (Strengthened)

**Revision-1 fix:** Sensitive-field assertion now checks both REST snake_case names (`provider_number`, `ahpra_number`, `prescriber_number`, `hpi_i`) and GraphQL camelCase names (`providerNumber`, `prescriberNumber`, `ahpraNumber`, `hpiI`), plus `email`, `phone`, `address`.

**Assessment — PASS.** All 13 sensitive names are asserted absent from the GraphQL query. The `displayName` count assertion (`== 1`) is preserved.

---

## Evidence Assessment

### Sol's independent verification (document: `review-sol-s6-candidate-verification.md`)

Sol ran the full deterministic test suite in the same corrected worktree:

| Check | Result |
|---|---|
| `git rev-parse HEAD` | `b0536c31e64ab5904a6a5ec99282714caa331356` |
| `git merge-base --is-ancestor 8b91eccc HEAD` | exit 0 (candidate in ancestry) |
| `pytest review/test_diary_smoke.py --collect-only -q` | `139` |
| `pytest review/test_diary_smoke.py -q --tb=short` | 139 passed, 100%, exit 0 |
| `node --check docs/diary/diary.js` | exit 0 |
| `scripts/check_frontend_versions.py` | PASSED; diary.js local/HEAD v183, deployed v182 |
| `git diff --check` | clean |
| Test-definition/skip/xfail diff scan | No removed/renamed tests, no added skip/xfail |

### Current worktree confirmation (HEAD moved 2 doc-only commits past Sol)

Commits `b0536c31 → 0690f77d` only add `review-sol-s6-candidate-verification.md` and `deepcode-s6-scope-delta-review-v3.md`. No implementation files changed.

---

## Boundary Assessment

### Permitted file changes (commit `8b91eccc` diff `2842bb3b...8b91eccc`)

| File | Change |
|---|---|
| `docs/diary/diary.js` | +4 lines: derived `ahpra` local after practitioner null-guard |
| `docs/diary/diary.html` | `diary.js?v=182` → `diary.js?v=183` (cache bust) |
| `review/test_diary_smoke.py` | +113/-16: GraphQL intercept in route helper, 4 practitioner tests updated, invalid-practitioner guard assertion added |

### Non-permitted files — NOT changed

- `app/` — no backend routes, schemas, services, models, or middleware
- No provider, database, migration, or deployment file
- No H15/H-series, historical diary, local_data, or RAG file
- No GraphQL server, readiness, telemetry, or production-claim file
- No product-policy or terminal-status decision file
- No cross-boundary contract audit surface (deferred to S7)

### Runtime gate posture

All runtime gates remain closed:
- No provider wiring, live-provider dry-run, or LLM prompt change
- No database write routes or mutation authority created
- No memory/RAG/GraphRAG access
- No H15/H-series runtime imports or historical diary material access
- No Pages deployment or production endpoint touched

---

## Veto Criteria Re-Evaluation

| Criterion | Status | Evidence |
|---|---|---|
| Practitioner dereferenced before validation | ✅ PASS | Null guard at line 7712 precedes line 7717 |
| Directory UUID becomes AHPRA | ✅ PASS | Fallback chain ends with `|| null` |
| Signed-confirm assertions weakened | ✅ PASS | No signed-confirm test modified in diff |
| GraphQL/auth/variable/projection/401/200-row/smoke-isolation | ✅ PASS | All checks accurate (see Finding 2) |
| Cache bust/boundary correct | ✅ PASS | `v182→v183`, only 3 impl files changed |
| Evidence establishes 139 collected + passing | ✅ PASS | Sol's independent verification confirms |
| No skip/xfail/test count change | ✅ PASS | Confirmed via grep and Sol's scan |

---

## Verdict

```text
VERDICT: PASS
STATUS: complete
DECISION: pass
```
