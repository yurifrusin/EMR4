# Sprint 157 — Update-Confirm Client Header Review (Antigravity Replacement)

> **Reviewer:** Codex (Antigravity replacement lane)
> **Target:** `C:\Users\sarashera\emr4`
> **Basis:** `8adf9d40` (Dispatch Sprint 157 worker packets)
> **Focus:** Frontend/smoke-test side of ordinary signed update-confirm HTTP `Idempotency-Key` headers

---

## 1. Summary

Sprint 157 wires HTTP `Idempotency-Key` headers for the two ordinary signed update-confirm callers in the Diary frontend. The implementation is **correct and complete for the stated scope**. Raw PUT fallback and `confirmBernieToolIntentChange` remain correctly header-free and deferred.

---

## 2. Frontend Call Sites (diary.js)

### 2.1 Edit modal update-confirm (`saveBooking`)

| Item | Evidence | Status |
|---|---|---|
| Header function defined | `updateConfirmIdempotencyKey(proposal, confirmPayload)` at line 7072 | ✅ |
| Key derivation | Freshness-first via `confirmIdempotencyKeyFromFreshness("update-confirm", ..., proposal)` with `ensureProposalConfirmIdempotencyKey` fallback | ✅ |
| Header emitted in fetch | `headers: confirmHeaders` via `idempotencyHeadersFor(...)` at line 7579-7581 | ✅ |
| Route used | `POST` to `confirm_endpoint` (signed update-confirm route) | ✅ |

### 2.2 Drag/resize update-confirm (`handleMoveResize`)

| Item | Evidence | Status |
|---|---|---|
| Header function used | `updateConfirmIdempotencyKey(proposal, confirmPayload)` at line 8123 | ✅ |
| Header emitted in fetch | `headers: confirmHeaders` via `idempotencyHeadersFor(...)` at line 8123-8126 | ✅ |
| Route used | `POST` to `confirm_endpoint` (signed update-confirm route) | ✅ |

### 2.3 Raw PUT fallback

Both call sites have an `else` branch at lines 7587-7589 (edit modal) and 8130-8132 (drag/resize):
```js
updateRes = await apiFetch(`/appointments/${id}`, { method: "PUT", body: ... });
```
No `headers` field. No `Idempotency-Key`. **Correctly deferred** — compatibility path with no header enforcement.

### 2.4 `confirmBernieToolIntentChange`

```js
const response = await apiFetch(normalizeApiPath(envelope.confirm_endpoint), {
  method: "POST",
  body: JSON.stringify(confirmPayload)
});
```
No `headers` field. **Correctly deferred** — tracked in the preflight doc as remaining confirm-client gap.

---

## 3. Smoke Test Assertions (review/test_diary_smoke.py)

### 3.1 `test_human_drag_resize_uses_signed_update_confirm_route` (line 6826)

| Assertion | Line | Status |
|---|---|---|
| `captured_confirms[0]["idempotency_key"] == "update-confirm-human-fresh-1"` | 6973 | ✅ |
| `captured_raw_puts == []` | 6972 | ✅ |
| Body `confirmed` is `True` | 6971 | ✅ |
| Body carries proposal command | 6975-6976 | ✅ |

### 3.2 `test_edit_modal_uses_signed_update_confirm_before_status_patch` (line 6979)

| Assertion | Line | Status |
|---|---|---|
| `captured_confirms[0]["idempotency_key"] == "update-confirm-edit-fresh-1"` | 7141 | ✅ |
| `captured_raw_puts == []` | 7140 | ✅ |
| `captured_status_patches` non-empty (status PATCH follows confirm) | 7139 | ✅ |
| Body `confirmed` is `True` | 7142 | ✅ |
| Body carries proposal command | 7143-7144 | ✅ |

### 3.3 `test_edit_modal_does_not_patch_status_when_signed_update_confirm_fails` (line 7148)

| Assertion | Line | Status |
|---|---|---|
| `captured_confirms` non-empty (confirm was attempted) | 7278 | ✅ |
| `captured_status_patches == []` (status not patched on confirm failure) | 7277 | ✅ |

### 3.4 `test_bernie_tool_intent_extension_proposal_renders_and_confirms` (line 6655)

| Assertion | Line | Status |
|---|---|---|
| Body `confirmed` is `True` | 6821 | ✅ |
| Body carries proposal command | 6822-6823 | ✅ |
| **Idempotency-Key not asserted** — correct per deferral | — | ✅ (deferred) |

---

## 4. Header Inventory Tests (tests/test_api_spine_frontend_header_inventory.py)

### 4.1 `test_frontend_update_confirm_callers_emit_stable_headers` (line 83)

| Assertion | Status |
|---|---|
| `function updateConfirmIdempotencyKey(...)` exists in source | ✅ |
| Save booking update-confirm block contains `updateConfirmIdempotencyKey` and `headers: confirmHeaders` | ✅ |
| Move/resize update-confirm block contains `updateConfirmIdempotencyKey` and `headers: confirmHeaders` | ✅ |

### 4.2 `test_frontend_update_confirm_falls_back_to_proposal_scoped_key` (line 106)

| Assertion | Status |
|---|---|
| Uses `"update-confirm"` prefix | ✅ |
| Checks `confirmPayload?.update_proposal_freshness_id` first | ✅ |
| Checks `proposal?.update_proposal_freshness_id` second | ✅ |
| Falls back to `ensureProposalConfirmIdempotencyKey(proposal, kind)` | ✅ |

### 4.3 `test_frontend_remaining_confirm_callers_are_explicitly_tracked_as_missing_headers` (line 118)

| Assertion | Status |
|---|---|
| `confirmBernieToolIntentChange` has no Idempotency-Key | ✅ |
| Preflight doc lists `confirmBernieToolIntentChange` as missing | ✅ |
| Preflight doc lists all other confirm route names | ✅ |

### 4.4 `test_frontend_header_preflight_keeps_closed_gates_closed` (line 148)

| Assertion | Status |
|---|---|
| `raw compatibility` in preflight | ✅ |
| `slot-search reservation or replay semantics` in preflight | ✅ |
| `Bernie interpreter/session command idempotency expansion` in preflight | ✅ |
| `OpenAPI minLength: 8 runtime enforcement` in preflight | ✅ |
| `provider calls`, `GraphQL mutations`, `H15/H-series`, `memory/RAG`, `historical diary` in preflight | ✅ |
| `confirmBernieToolIntentChange, proposal-only header binding` in preflight | ✅ |

---

## 5. Missing Gaps (Non-blocking)

### 5.1 Bernie tool-intent confirm smoke: no negative header assertion

`test_bernie_tool_intent_extension_proposal_renders_and_confirms` captures the update confirm request body but does not capture or assert the absence of `idempotency-key`. The static inventory test covers this, but a smoke-level negative assertion (e.g., `assert captured_update_headers.get("idempotency-key") is None`) would make the deferral more explicit at the smoke layer.

**Severity:** Low — the static test already enforces this. Worth adding during Sprint 157 closeout for belt-and-suspenders coverage.

### 5.2 No offline unit test for freshness fallback boundary

The `confirmIdempotencyKeyFromFreshness` helper's boundary logic (freshness too long -> generated fallback) is only tested via the static helper assertion in the inventory test. There's no isolated unit test for the 128-char truncation boundary.

**Severity:** Low — the function is small and the smoke tests exercise the happy path end-to-end. Not blocking.

### 5.3 Cache-bust version skew

`diary.html` serves `diary.js?v=178` which is well past the Sprint 157 increment. This is organic and not a bug, but worth noting that the version counter has drifted from the sprint numbering.

**Severity:** Information only.

---

## 6. Verdict

Sprint 157's narrow scope is correctly implemented and tested. The two ordinary update-confirm callers (edit modal and drag/resize) correctly emit freshness-derived `Idempotency-Key` headers. Raw PUT fallback and `confirmBernieToolIntentChange` remain header-free and are correctly tracked as deferred. No implementation changes needed.

**Recommendation:** Close Sprint 157 as implemented. The next safe slice (compact confirm-client surface checkpoint) can proceed once this review is acknowledged.
