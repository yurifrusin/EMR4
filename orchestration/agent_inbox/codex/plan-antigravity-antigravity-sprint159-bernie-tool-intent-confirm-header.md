# Sprint 159 — Bernie Tool-Intent Confirm Header Review (Antigravity Replacement)

> **Reviewer:** Codex (Antigravity replacement lane)
> **Target:** `C:\Users\sarashera\emr4`
> **Basis:** `bc31b102` (Dispatch Sprint 159 worker packets) + working tree
> **Focus:** Frontend/smoke-test side of `confirmBernieToolIntentChange` HTTP `Idempotency-Key` emission

---

## 1. Summary

Sprint 159 wires HTTP `Idempotency-Key` for the remaining user-clickable confirm-client gap: `confirmBernieToolIntentChange()`. The working tree implementation is **correct and complete**. All enforced backend confirm routes now have matching client header emission. No UI redesign, provider enablement, backend ledger changes, or broader architectural changes were needed.

---

## 2. Frontend Call Site (diary.js:1716-1753)

### `confirmBernieToolIntentChange`

| Item | Evidence | Status |
|---|---|---|
| Header function used | `updateConfirmIdempotencyKey(envelope, confirmPayload)` at line 1744 | ✅ |
| Header emitted in fetch | `headers: confirmHeaders` via `idempotencyHeadersFor(...)` at lines 1743-1746 | ✅ |
| Key strategy | Same freshness-derived strategy as other update-confirm callers: `update-confirm-<update_proposal_freshness_id>` | ✅ |
| Fallback | `ensureProposalConfirmIdempotencyKey` fallback when freshness is absent (through `confirmIdempotencyKeyFromFreshness`) | ✅ |
| Route used | `POST` to dynamic `envelope.confirm_endpoint` (signed update-confirm route `/api/v1/appointments/proposals/update/confirm`) | ✅ |
| Pre-existing guard | Still throws for missing `confirm_endpoint`/`confirm_payload` (lines 1738-1739) | ✅ |
| Pre-existing smoke shortcut | `isSmokeMode()` still short-circuits (lines 1730-1735) | ✅ |

The diff is minimal — 4 lines added in `confirmBernieToolIntentChange`:

```diff
+  const confirmHeaders = idempotencyHeadersFor(
+    updateConfirmIdempotencyKey(envelope, confirmPayload)
+  );
   const response = await apiFetch(normalizeApiPath(envelope.confirm_endpoint), {
     method: "POST",
+    headers: confirmHeaders,
     body: JSON.stringify(confirmPayload)
   });
```

---

## 3. Smoke Test Assertions (review/test_diary_smoke.py)

### `test_bernie_tool_intent_extension_proposal_renders_and_confirms`

The route-intercepted handler was updated to capture both body and header:

```python
captured_update.append({
    "body": request.post_data_json,
    "idempotency_key": request.headers.get("idempotency-key"),
})
```

New/drifted assertions:

| Assertion | Status |
|---|---|
| `captured_update[0]["idempotency_key"] == "update-confirm-fresh-tool-1"` | ✅ |
| `captured_update[0]["body"]["confirmed"] is True` | ✅ (was `captured_update[0]["confirmed"]`) |
| `captured_update[0]["body"]["update_proposal"]["command"]["appointment_id"] == "appt-tool-1"` | ✅ (was shallow path) |
| `captured_update[0]["body"]["update_proposal"]["command"]["duration_minutes"] == 30` | ✅ (was shallow path) |

The test now proves the visible tool-intent confirm button emits the expected idempotency header in route-intercepted coverage. Existing assertions for request context frames and tool-intent payload are unchanged.

---

## 4. Header Inventory Tests (tests/test_api_spine_frontend_header_inventory.py)

### `test_frontend_update_confirm_callers_emit_stable_headers`

| New assertion | Status |
|---|---|
| `confirmBernieToolIntentChange` parsed and checked for `updateConfirmIdempotencyKey(envelope, confirmPayload)` | ✅ |
| `confirmBernieToolIntentChange` checked for `headers: confirmHeaders` | ✅ |

### `test_frontend_confirm_callers_are_wired_or_explicitly_tracked`

Renamed from `test_frontend_remaining_confirm_callers_are_explicitly_tracked_as_missing_headers`. Previously asserted no header; now asserts:

| New assertion | Status |
|---|---|
| `_contains_idempotency_header(tool_intent)` is true | ✅ |

All 8 header inventory tests pass.

---

## 5. Supporting Documentation

| File | Change | Status |
|---|---|---|
| `orchestration/api_spine_appointment_idempotency_bernie_tool_intent_confirm_client_header.md` | New: Sprint 159 scope doc describing header strategy | ✅ |
| `orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md` | Table updated: Bernie tool-intent update confirm → "Wired in Sprint 159"; follow-up narrowed to proposal-only binding + `minLength: 8` | ✅ |
| `orchestration/api_spine_confirm_client_surface_checkpoint.md` | Bernie tool-intent row → `Covered`; Sprint 159 scoped; Sprint 160 → Bernie/Diary review readiness packet | ✅ |
| `orchestration/api_spine_appointment_idempotency_update_confirm_client_header.md` | Deferred work section updated to show Sprint 159 closes the gap | ✅ |
| `docs/diary/diary.html` | Version bump `v=178` → `v=179` | ✅ |

---

## 6. Constraint Verification

| Constraint | Status | Evidence |
|---|---|---|
| No UI redesign | ✅ | Only 4 JS lines added inside fetch options; no DOM, CSS, or HTML changes |
| No provider enablement | ✅ | No provider calls added; `isSmokeMode()` unchanged |
| No backend ledger changes | ✅ | No backend routes, handlers, or models touched |
| No proposal-only header binding | ✅ | Only the confirm-endpoint `POST` is touched |
| No strict `minLength: 8` enforcement | ✅ | Not touched |
| No memory/RAG/GraphRAG | ✅ | Not touched |
| No H15/H-series runtime imports | ✅ | Not touched |
| No raw compatibility writes | ✅ | Raw PUT fallback unchanged |

---

## 7. Verdict

Sprint 159's working tree changes are **correct and complete**. The last enforced confirm-client header gap is closed:

- `confirmBernieToolIntentChange()` now emits `Idempotency-Key: update-confirm-<freshness>` using the same helper as the two ordinary update-confirm callers.
- Route-intercepted smoke coverage proves the header appears on the visible tool-intent confirm click.
- Static source inventory tests confirm the function declaration contains the header wiring.
- All 8 header inventory tests pass.

All six enforced backend confirm routes (`create/confirm`, `create/confirm-bernie`, `update/confirm`, `status-confirm`, `delete-confirm`) now have matching client header emission. The remaining idempotency work (proposal-only binding, `minLength: 8`, raw compatibility) is correctly tracked as separate backend/API spine slices.

**Recommendation:** Commit the working tree changes and proceed to Sprint 160 (Bernie/Diary review-readiness packet and Yuri review readiness).
