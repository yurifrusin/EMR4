# Sprint 158 — Confirm-Client Surface Checkpoint (Antigravity Lane Replacement Review)

| Item | Value |
|---|---|
| **Review type** | Frontend/product-readiness checkpoint assessment |
| **Sprint** | 158 |
| **Lane** | Antigravity replacement (Codex) |
| **Target** | `C:\Users\sarashera\emr4` |
| **Status** | Review artifact (no runtime changes) |
| **Reviewed sprints** | 153 (create-proposal header), 154 (gap preflight), 155 (create-confirm/Bernie confirm header), 156 (status/delete confirm header), 157 (update-confirm header) |

---

## 1. Current Surface: 7 Wired, 4 Deferred

### 1.1 Wired — all ordinary Diary confirm callers now emit `Idempotency-Key`

| # | Confirm family | Frontend caller | Key source | Sprint |
|---|---|---|---|---|
| 1 | Create-proposal | `saveBooking()` create branch | `generateClientIdempotencyKey()` on `saveBtn.dataset.idempotencyKey` | 153 |
| 2 | Staff create-confirm | `saveBooking()` create confirm branch | `ensureElementConfirmIdempotencyKey(saveBtn)` | 155 |
| 3 | Bernie create-confirm (review adapter) | `renderBernieReview()` confirm click | `bernieSession.getServerRouteIdempotencyKey("create-confirm-bernie", ...)` | 155 |
| 4 | Status-confirm | `applySignedStatusProposal()` | `status_proposal_freshness_id` → `confirmIdempotencyKeyFromFreshness` | 156 |
| 5 | Delete-confirm | `applySignedDeleteProposal()` | `delete_proposal_freshness_id` → `confirmIdempotencyKeyFromFreshness` | 156 |
| 6 | Update-confirm (modal edit) | `saveBooking()` update confirm branch | `update_proposal_freshness_id` → `updateConfirmIdempotencyKey` | 157 |
| 7 | Update-confirm (drag/resize) | `handleMoveResize()` confirm branch | `update_proposal_freshness_id` → `updateConfirmIdempotencyKey` | 157 |

### 1.2 Deferred — tracked in gap preflight, not wired

| # | Surface | Reason | Sprint 158 posture |
|---|---|---|---|
| 8 | `confirmBernieToolIntentChange` | Bernie session-scoped update-confirm; needs Bernie-specific key scoping | Header-free (correct) — one remaining confirm-client gap |
| 9 | Proposal-only backend header binding (4 routes) | Backend doesn't bind `Header(None, ...)` yet — no client header would help | No change |
| 10 | `minLength: 8` runtime enforcement | OpenAPI documents it; backend doesn't enforce | No change — all client keys satisfy 8+ chars |
| 11 | Raw compatibility `PUT/PATCH/DELETE` routes | Policy-deferred — not canonical confirm surfaces | No change |

---

## 2. Test Evidence: What the Checkpoint Proves

### 2.1 Static header inventory (`tests/test_api_spine_frontend_header_inventory.py`)

| Test | What it proves | Status |
|---|---|---|
| `test_frontend_create_proposal_and_create_confirm_emit_headers` | S153/S155: create-proposal and create-confirm emit headers | ✅ Passing |
| `test_frontend_create_confirm_bernie_review_caller_emits_stable_header` | S155: Bernie review adapter emits session-scoped header | ✅ Passing |
| `test_frontend_status_and_delete_confirm_callers_emit_stable_headers` | S156: status/delete confirm use freshness ID + `confirmIdempotencyKeyFromFreshness` | ✅ Passing |
| `test_frontend_update_confirm_callers_emit_stable_headers` | S157: both modal edit and drag/resize emit headers | ✅ Passing |
| `test_frontend_update_confirm_falls_back_to_proposal_scoped_key` | S157: fallback when freshness ID absent | ✅ Passing |
| `test_frontend_remaining_confirm_callers_are_explicitly_tracked` | Proves `confirmBernieToolIntentChange` is the sole remaining gap | ✅ Passing |
| `test_frontend_proposal_only_callers_are_explicitly_tracked_as_deferred` | 4 proposal-only routes tracked as deferred | ✅ Passing |
| `test_frontend_header_preflight_keeps_closed_gates_closed` | All closed boundaries preserved in preflight doc | ✅ Passing |

### 2.2 Smoke tests (`review/test_diary_smoke.py`)

| Test | What it proves | Status |
|---|---|---|
| `test_create_proposal_idempotency_header` | Create-proposal key stable across retry; confirm key distinct; key refreshes on input change | ✅ Passing |
| `test_status_control_uses_signed_status_confirm_without_raw_patch` | Status confirm with idempotency key | ✅ Passing |
| `test_status_control_failed_signed_confirm_does_not_raw_patch` | Status confirm failure doesn't fall through to raw PATCH | ✅ Passing |
| `test_cancel_flow_uses_signed_delete_confirm_without_raw_delete` | Delete confirm with idempotency key | ✅ Passing |
| `test_cancel_flow_failed_signed_confirm_does_not_raw_delete` | Delete confirm failure doesn't fall through to raw DELETE | ✅ Passing |
| `test_human_drag_resize_uses_signed_update_confirm_route` | Drag/resize update-confirm with `idempotency_key: "update-confirm-human-fresh-1"` | ✅ Passing |
| `test_edit_modal_uses_signed_update_confirm_before_status_patch` | Modal edit update-confirm with `idempotency_key: "update-confirm-edit-fresh-1"` | ✅ Passing |
| `test_edit_modal_does_not_patch_status_when_signed_update_confirm_fails` | Confirm failure blocks status PATCH | ✅ Passing |
| `test_bernie_tool_intent_extension_proposal_renders_and_confirms` | Bernie tool-intent confirm works; **no idempotency-key assertion** (correctly deferred) | ✅ Passing |

### 2.3 Cross-family backend integration (`tests/test_api_spine_confirmation_family_idempotency_integration.py`)

Proves all 5 confirm routes share the fail-closed replay/conflict/stale map against a real DB session. 30 cross-family cases passing as of Sprint 146.

---

## 3. Frontend/Product-Readiness Assessment

### 3.1 Is the checkpoint close to a meaningful Bernie/Diary user review?

**Yes for ordinary staff Diary surfaces. No for a full Bernie/Diary integrated review.**

| Scenario | Ready? | Evidence |
|---|---|---|
| Staff: create new appointment | ✅ Full coverage | Create-proposal header + create-confirm header; stable retry; distinct keys |
| Staff: edit appointment (modal) | ✅ Full coverage | Update-confirm header from freshness ID; correct separation from raw PUT fallback |
| Staff: drag/resize appointment | ✅ Full coverage | Same update-confirm pattern; smoke test proves key stability |
| Staff: change status (Arrived, DNA, etc.) | ✅ Full coverage | Status-confirm header from freshness ID; no raw PATCH fallback |
| Staff: cancel/delete appointment | ✅ Full coverage | Delete-confirm header from freshness ID; no raw DELETE fallback |
| Bernie: create new appointment (review confirm) | ✅ Full coverage | Bernie session-scoped key; adapter header emission tested |
| **Bernie: tool-intent change (extend, resize)** | ❌ Blocking gap | `confirmBernieToolIntentChange` lacks header — will 400 if backend enforces |
| Bernie: mixed workflow (create, then extend) | ❌ Partial | First create confirm works; tool-intent confirm broken |

### 3.2 What additional frontend/smoke evidence is still needed?

#### Low-severity gaps (additive, non-blocking)

| Gap | Source | Recommendation |
|---|---|---|
| No negative header assertion for `confirmBernieToolIntentChange` in smoke tests | Sprint 157 review §5.1 | Add belt-and-suspenders `assert captured_update_headers.get("idempotency-key") is None` to `test_bernie_tool_intent_extension_proposal_renders_and_confirms` |
| No status/delete confirm fallback test for freshness ID absent | Sprint 156 review recommended pattern | Add `test_frontend_status_delete_confirm_fallback_to_random_key` for parity with the update-confirm fallback test |
| No isolated unit test for 128-char freshness truncation | Sprint 157 review §5.2 | Add truncation boundary test for `confirmIdempotencyKeyFromFreshness` |

#### Medium-severity gaps (worth review before next implementation slice)

| Gap | Assessment | Recommendation |
|---|---|---|
| `confirmBernieToolIntentChange` header gap | Only remaining confirm-client surface; Bernie pilot users exercising tool-intent will get 400 if backend enforces | Wire as next sprint after this checkpoint: use `bernieSession.getServerRouteIdempotencyKey("update-confirm-bernie", ...)` — same pattern as the create-confirm adapter, no new key derivation needed |
| No integrated "user story" smoke test for chained workflow (proposal → confirm → verify diary state) | All confirm surfaces tested individually; no test that a create, then an update, then a status change all succeed with correct idempotency separation | Not blocking — individual smoke+static coverage is sufficient |
| Preflight doc still mentions update-confirm in "missing" row | Sprint 157 review flagged this; if not yet updated, it creates stale documentation | Update `orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md` to move update-confirm from "Missing frontend header" to "Wired (Sprint 157)" |

---

## 4. Verdict: Next Safe Slice Recommendation

### Recommended order of work

1. **Zero-cost belt-and-suspenders** (Sprint 158 closeout):
   - Add negative header assertion to `test_bernie_tool_intent_extension_proposal_renders_and_confirms`
   - Add status/delete confirm fallback test for parity
   - Update gap preflight doc to reflect wired update-confirm surface

2. **Wire `confirmBernieToolIntentChange` header** (next implementation sprint):
   - Use `bernieSession.getServerRouteIdempotencyKey("update-confirm-bernie", envelope.confirm_endpoint)` — follows existing Bernie create-confirm adapter pattern
   - No new key derivation needed; no proposal freshness dependency
   - Update static header inventory to move this from "missing" to "wired"
   - Add or extend smoke test with idempotency-key assertion on the tool-intent confirm path
   - **Boundary constraint:** Do not open proposal-only header binding, `minLength: 8`, raw compatibility routes, providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, or historical diary trove

3. **Proposal-only backend header binding** (third sprint, after Bernie tool-intent confirm):
   - Backend: add `Header(None, alias="Idempotency-Key")` to `propose_update_appointment`, `propose_status_update`, `propose_waiting_area_update`, `propose_delete_appointment`
   - Frontend: wire client header from existing `ensureProposalConfirmIdempotencyKey(proposal, "propose-{kind}")` pattern
   - Requires coordination: backend binding before client emission to avoid rejecting existing header-free callers

4. **`minLength: 8` runtime enforcement** (fourth sprint, after proposal-only binding):
   - Backend: validate minimum length in `_normalize_idempotency_key()`
   - No frontend change needed — all keys already satisfy 8+ chars

### What remains closed

| Boundary | Sprint 158 posture |
|---|---|
| Live provider calls | Not wired |
| Memory/RAG/GraphRAG runtime wiring | Not wired |
| H15/H-series runtime imports | Not imported |
| Broad historical diary trove mining | Not performed |
| GraphQL mutations | Not wired |
| Raw compatibility route headers | Not changed |
| Proposal-only backend header binding | Deferred (step 3 above) |
| `minLength: 8` runtime enforcement | Deferred (step 4 above) |

---

## 5. Summary

| Dimension | Verdict |
|---|---|
| Staff Diary confirm surfaces (create, update, status, delete) | ✅ Fully wired — ready for user review |
| Bernie create-confirm (review adapter) | ✅ Fully wired |
| Bernie tool-intent update-confirm | ❌ Single remaining gap — wire next |
| Static inventory forward drift detection | ✅ Comprehensive — 8 tests prove structure |
| Smoke-level retry/key-stability coverage | ✅ Strong for all wired surfaces |
| Negative header assertion for remaining gap | ⚠️ Add as belt-and-suspenders |
| Preflight doc stale for update-confirm | ⚠️ Update to reflect wired surface |

The checkpoint proves the ordinary Diary confirm-client surface is **production-ready for a staff user review**. The `confirmBernieToolIntentChange` gap is the one thing blocking a full Bernie/Diary integrated review. Wiring it requires one sprint using the existing `bernieSession.getServerRouteIdempotencyKey()` pattern — no new architecture needed.
