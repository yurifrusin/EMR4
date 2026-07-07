# Sprint 158 Review — Confirm-Client Surface Checkpoint

| Item | Value |
|---|---|
| **Review type** | Compact confirm-client surface checkpoint |
| **Sprint** | 158 |
| **Target** | Full confirm-header inventory after Sprints 153–157 |
| **Runtime behaviour changed** | No (review artifact only) |
| **Previous reviews** | 153 (create-proposal header), 155 (create-confirm header), 156 (status/delete confirm header), 157 (update-confirm header) |
| **Previous review artifacts** | `review-deepseek-sprint157-update-confirm-client-header.md`, `plan-claude-claude-sprint157-update-confirm-client-header.md`, `plan-antigravity-antigravity-sprint157-update-confirm-client-header.md` |

---

## 1. Ordinary Diary Confirm Surface: 6/6 Wired

Sprints 153–157 wired HTTP `Idempotency-Key` emission for all six ordinary Diary confirm callers. Every frontend path that posts to a backend signed-confirm route now sends a stable header:

| Caller | Backend route | Sprint wired | Derivation |
|---|---|---|---|
| `saveBooking` create-proposal branch | `POST /proposals/create` | 153 | `generateClientIdempotencyKey()`, stored on `btn-booking-save.dataset.idempotencyKey` |
| `saveBooking` create-confirm branch | `POST /proposals/create/confirm` | 155 | Separate `btn-booking-save.dataset.confirmIdempotencyKey` |
| Bernie review confirm adapter | `POST /proposals/create/confirm-bernie` | 155 | `bernieSession.getServerRouteIdempotencyKey("create-confirm-bernie", …)` |
| `applySignedStatusProposal` | `POST /proposals/status-confirm` | 156 | `status-confirm-` + `status_proposal_freshness_id`; fallback to generated |
| `applySignedDeleteProposal` | `POST /proposals/delete-confirm` | 156 | `delete-confirm-` + `delete_proposal_freshness_id`; fallback to generated |
| `saveBooking` update-confirm branch | `POST /proposals/update/confirm` | 157 | `update-confirm-` + `update_proposal_freshness_id`; fallback to generated |
| `handleMoveResize` update-confirm branch | `POST /proposals/update/confirm` | 157 | `update-confirm-` + `update_proposal_freshness_id`; fallback to generated |

**Verdict:** The ordinary Diary confirm-client surface is complete. All preflight-identified gaps for the six-table cell from Sprint 154 are closed. Raw `PUT`/`PATCH`/`DELETE` compatibility fallbacks are correctly header-free.

---

## 2. Critical Finding: `confirmBernieToolIntentChange` Is a Bug, Not a Deferral

The preflight doc lists `confirmBernieToolIntentChange()` as the remaining confirm-client gap and describes the work as "deferred". **This classification is dangerously misleading.**

### Why

`confirmBernieToolIntentChange()` (diary.js:~1734) posts to the same backend route as the ordinary update-confirm callers:

```js
const response = await apiFetch(normalizeApiPath(envelope.confirm_endpoint), {
  method: "POST",
  body: JSON.stringify(confirmPayload)
});
```

The `confirm_endpoint` value carried in the Bernie tool-intent proposal envelope is `"/api/v1/appointments/proposals/update/confirm"` (confirmed in `review/test_diary_smoke.py:~6701`).

That backend route (`confirm_update_proposal_route` at `app/routers/appointments.py:1458`) already binds `Header(None, alias="Idempotency-Key")` and calls `_normalize_idempotency_key()`, which **raises `HTTPException(400, code="idempotency_key_required")` when the header is absent or blank** (line 1242-1243).

### Impact

The Bernie tool-intent update-confirm path **cannot complete successfully** against a real backend. Every time a receptionist clicks "Confirm" on a Bernie tool-intent proposal, the request is rejected with 400. The smoke test (`test_bernie_tool_intent_extension_proposal_renders_and_confirms`) does not catch this because the Playwright `route.fulfill()` intercepts the request before it reaches the backend — the test captures only `request.post_data_json` (body) and never inspects headers.

### Severity: Needs Fix

This is not a "should we do this later" architectural question. It is a functional gap: the button that staff click produces a confirmed-looking success response in smoke mode and a 400 error in production.

### Comparison

| Path | Header wired? | Backend route enforces? | Production functional? |
|---|---|---|---|
| `saveBooking` edit-modal update-confirm | ✅ Yes (Sprint 157) | ✅ Yes | ✅ Yes |
| `handleMoveResize` update-confirm | ✅ Yes (Sprint 157) | ✅ Yes | ✅ Yes |
| `confirmBernieToolIntentChange` | ❌ No (listed as deferred) | ✅ Yes | ❌ **Broken** |

---

## 3. Candidate Next-Slice Ranking

Given the critical finding in §2, the three candidate slices now have different urgency weights.

### Candidate A: Wire `confirmBernieToolIntentChange` Header Emission — **Recommended Next**

| Dimension | Assessment |
|---|---|
| **Backend change required** | No — the route already enforces the header. Only frontend JS changes needed. |
| **Frontend change scope** | Small. Add `headers: confirmHeaders` to the `apiFetch` call in `confirmBernieToolIntentChange()`, with a key derivation strategy. |
| **Key derivation** | Three options, listed below. The freshness-derived pattern (`update-confirm-` + `update_proposal_freshness_id`) is the most natural because the proposal envelope already carries `update_proposal_freshness_id`. |
| **Test impact** | Expand `test_bernie_tool_intent_extension_proposal_renders_and_confirms` to capture and assert the idempotency-key header. The smoke test already intercepts the confirm endpoint and can trivially capture `request.headers.get("idempotency-key")`. |
| **Risk** | Low. Matches the proven Sprint 156/157 pattern. Cannot accidentally affect raw compatibility paths or proposal-only routes because those are separate endpoints/code paths. |
| **Why not defer further** | Every sprint that defers this fix keeps the Bernie tool-intent confirm button broken in production. The Sprint 158 checkpoint is the natural place to correct the classification. |

#### Key derivation options for Candidate A

| Strategy | Pros | Cons |
|---|---|---|
| **A1 — Freshness-derived** (`update-confirm-` + `update_proposal_freshness_id` with generated fallback) | Matches Sprint 156/157 pattern; proposal envelope already carries the freshness field; stable for retries | Depends on envelope carrying a valid freshness ID (it does in the smoke fixture) |
| **A2 — Server-session/key derived** (`bernieSession.getServerRouteIdempotencyKey("update-confirm-bernie", endpoint)`) | Matches Sprint 155 create-confirm-Bernie pattern; session-scoped instead of proposal-scoped | Different key strategy from the same backend route; could produce conflicting keys if the same proposal is confirmed via tool-intent and ordinary edit |
| **A3 — Generated-per-proposal** (`ensureProposalConfirmIdempotencyKey(proposal, "update-confirm-bernie")`) | Isolation from session lifecycle | The envelope's `proposal` object may not be the same structure as ordinary update proposals — matches `ensureProposalConfirmIdempotencyKey` requires | 

**Recommendation:** Use **A1 (freshness-derived)**. It keeps one consistent key strategy for `/proposals/update/confirm` regardless of which frontend caller posts to it. The proposal envelope already includes `update_proposal_freshness_id` (`test_diary_smoke.py:~6726` / `~6735`). The fallback path (`ensureProposalConfirmIdempotencyKey`) may need adjustment if the Bernie tool-intent `proposal` structure differs from ordinary update proposals.

### Candidate B: Proposal-Only Backend Header Binding

| Dimension | Assessment |
|---|---|
| **Backend change required** | Yes — 4 FastAPI handlers need `Header(None, alias="Idempotency-Key")` binding. |
| **Frontend change required** | Yes — proposal callers for update/status/waiting-area/delete need header emission. |
| **Risk** | Medium. Backend route changes plus frontend emission changes. Could also require ledger integration changes to avoid accidentally granting confirmation replay authority to proposal-only headers. |
| **Why not first** | Larger scope, backend changes, and less urgent than fixing a broken confirm button. No evidence that proposal-only routes cause production failures. |

### Candidate C: Strict OpenAPI `minLength: 8` Enforcement

| Dimension | Assessment |
|---|---|
| **Backend change required** | Yes — add `min_length=8` to `Header(...)` parameter or validate in `_normalize_idempotency_key`. |
| **Frontend change required** | No (unless existing keys are shorter than 8 chars — need to audit). |
| **Risk** | Medium — could break existing keys shorter than 8 characters. The current `generateClientIdempotencyKey()` produces UUIDs (36 chars + prefix), but the generated fallback in `ensureProposalConfirmIdempotencyKey` uses `${kind}-${Math.random()}` which could be shorter than 8. |
| **Why not first** | Production surface: no evidence that short keys cause backend confusion. The `_normalize_idempotency_key` function already rejects empty/blank keys, so the most common idempotency bug (missing header) is already caught. |

---

## 4. Preflight Doc Update Required

The header gap preflight (`orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md`) currently describes `confirmBernieToolIntentChange` as "remaining deferred gap" and does not flag the functional breakage. After this checkpoint resolves, update:

- **Enforced Backend Confirm Routes And Diary Headers** table — add a row for Bernie tool-intent update-confirm with the correct driver status (broken/deferred-now-deemed-bug).
- **Follow-Up Recommendation** — replace the generic recommendation with the chosen Candidate A/B/C decision and the bug rationale.

---

## 5. Remaining Deferred Surfaces (Unchanged)

The following gates remain closed regardless of which candidate is chosen:

- Raw `POST /appointments`, `PUT /appointments/{id}`, `PATCH /appointments/{id}/status`, `DELETE /appointments/{id}` — header-free, unchanged.
- Slot-search reservation or replay semantics.
- Bernie interpreter/session command idempotency expansion beyond header emission.
- Provider calls.
- GraphQL mutations.
- H15/H-series runtime imports.
- Memory/RAG/GraphRAG runtime wiring.
- Broad historical diary trove mining.

---

## Summary

| Dimension | Verdict |
|---|---|
| Ordinary Diary confirm surface (6/6 callers) | ✅ Complete and correct |
| `confirmBernieToolIntentChange` classification | ⚠️ **Is a bug, not a deferral** — currently broken in production |
| Next recommended slice | **Candidate A: Wire tool-intent confirm header** (freshness-derived, matches Sprint 156/157 pattern) |
| Next after A | Candidate B: Proposal-only backend header binding |
| Proposal-only candidate ranking | Second priority |
| `minLength: 8` enforcement ranking | Third priority — no evidence of need, risks breaking generated fallback keys |

The compact checkpoint confirms that the "deferred Bernie tool-intent" gap is actually a production bug that should be fixed in the next slice, not pushed further down the roadmap.  The fix is small, frontend-only, and follows the proven freshness-derived pattern.
