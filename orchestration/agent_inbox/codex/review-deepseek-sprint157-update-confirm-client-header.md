# Sprint 157 Review — Update-Confirm Client Header Emission

| Item | Value |
|---|---|
| **Review type** | Narrow plan review |
| **Sprint** | 157 |
| **Target** | docs/diary/diary.js — Idempotency-Key header emission for signed update-confirm calls |
| **Runtime behaviour changed** | No (review artifact only) |
| **Reviewer sprints** | 124 (idempotency gap), 139 (update-confirm preflight), 140 (route tests), 141 (wiring), 154 (header gap preflight), 155 (create-confirm client header), 156 (status/delete confirm client header), 157 (this review) |

---

## 1. Current Code State: Already Emitting

The docs/diary/diary.js source already emits Idempotency-Key headers for
both ordinary signed update-confirm callers. No new client code is required.

| Caller | Location | Source | Header present? |
|---|---|---|---|
| Modal edit (saveBooking update branch) | diary.js:~7578 | updateConfirmIdempotencyKey(proposal, confirmPayload) → idempotencyHeadersFor(...) | ✅ Yes |
| Drag/resize (handleMoveResize) | diary.js:~8122 | updateConfirmIdempotencyKey(proposal, confirmPayload) → idempotencyHeadersFor(...) | ✅ Yes |
| Raw PUT fallback (modal edit) | saveBooking else branch | piFetch(PUT) without headers | ✅ No (correct) |
| Raw PUT fallback (drag/resize) | handleMoveResize else branch | piFetch(PUT) without headers | ✅ No (correct) |
| confirmBernieToolIntentChange | diary.js:~1739 | piFetch(POST) without headers | ✅ No (deferred per gap doc) |

---

## 2. Question 1: Key Derivation from update_proposal_freshness_id — Yes, Adopt

The existing updateConfirmIdempotencyKey(proposal, confirmPayload) already
uses the Sprint 156‑endorsed pattern:

`
confirmIdempotencyKeyFromFreshness(
  "update-confirm",
  confirmPayload?.update_proposal_freshness_id || proposal?.update_proposal_freshness_id,
  proposal
)
`

This derives the key from the server-generated update_proposal_freshness_id
when present (within 128-char prefix+key limit), with a
[ensureProposalConfirmIdempotencyKey](https://github.com/emr4/emr4/blob/main/docs/diary/diary.js#L7047-L7052)
fallback that generates ${kind}-.

**Verdict:** The current derivation exactly matches the status/delete confirm
pattern validated in Sprint 156. No change needed.

### Fallback recommendation

The fallback to ensureProposalConfirmIdempotencyKey (random uuid or
"evt-" + Math.random()) is acceptable for defensive completeness, but the
confirmEndpoint && confirmPayload guard means the fallback path should only
fire if the proposal object lacks a update_proposal_freshness_id — an edge
case that does not arise from current backend responses. The Sprint 156 review
recommended adding a frontend-inventory test for the fallback; that gap still
applies here. See Section 5.

---

## 3. Question 2: Both Callers Covered Without Leaking to Raw Paths — Yes

### Covered confirm callers

| Caller | Path cooked | Header scope |
|---|---|---|
| Modal edit update-confirm | POST {confirmEndpoint} via if (confirmEndpoint && confirmPayload) | updateConfirmIdempotencyKey(proposal, confirmPayload) |
| Drag/resize update-confirm | POST {confirmEndpoint} via if (confirmEndpoint && confirmPayload) | updateConfirmIdempotencyKey(proposal, confirmPayload) |

### Not covered (correctly)

| Path | Reason |
|---|---|
| Raw PUT fallback in saveBooking | No confirmEndpoint → else branch uses bare PUT without header. Correct — compatibility write, not canonical confirm. |
| Raw PUT fallback in handleMoveResize | Same else branch, same reasoning. Correct. |
| confirmBernieToolIntentChange | Uses Bernie session event routing, not proposal-scoped idempotency. Deferred per gap doc. |

### Notable: Proposal call lacks header

Both saveBooking (editingAppointmentId branch) and handleMoveResize do
NOT send Idempotency-Key on the proposal call itself
(POST /appointments/proposals/update/{id}). This is correct because:

- Proposal-only backend header binding is explicitly deferred per the gap preflight.
- The proposal route does not bind Header(None, alias="Idempotency-Key").
- A client header here would hit an unbound FastAPI parameter and be silently dropped.

When proposal-only backend binding is later addressed, both saveBooking and
handleMoveResize must be updated to emit headers on the proposal call. Flag
this as a deferred dependency in the preflight doc.

---

## 4. Question 3: Blocking Tests and Docs

### Docs to update

| Doc | Current state | Required change |
|---|---|---|
| orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md | Lists update-confirm as "Missing frontend header" (row ~40) | Update to reflect Sprint 157: "Wired: client emits Idempotency-Key from update_proposal_freshness_id" |
| orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md | Paragraph ~90 lists update-confirm among deferred gaps | Update to note update-confirm is now wired; keep status/confirm, delete-confirm as remaining (already wired in Sprint 156) |

### Tests already passing (no new work)

| Test | What it proves |
|---|---|
| 	est_frontend_update_confirm_callers_emit_stable_headers | Both saveBooking update branch and handleMoveResize emit Idempotency-Key via updateConfirmIdempotencyKey with headers: confirmHeaders |
| 	est_frontend_remaining_confirm_callers_are_explicitly_tracked_as_missing_headers | confirmBernieToolIntentChange still lacks header (correctly) |

### Tests to add (blocking recommendation)

None blocking — the header inventory test already proves correct emission. But
the Sprint 156 pattern suggests these additive tests for parity:

| Recommended test | Rationale |
|---|---|
| 	est_frontend_update_confirm_fallback_to_random_key | Prove the fallback path (freshness ID absent) resolves via ensureProposalConfirmIdempotencyKey / generateClientIdempotencyKey. Matches status/delete confirm test pattern. |
| Expand 	est_frontend_header_preflight_keeps_closed_gates_closed | Add "update-confirm client header emission is no longer missing" and "confirmBernieToolIntentChange remains deferred" to the update-confirm section of the preflight doc assertions. |

These are additive — the header inventory test 	est_frontend_update_confirm_callers_emit_stable_headers
already asserted successful client emission and is passing.

### Smoke-mode review (	est_diary_smoke.py)

The update-confirm path is never exercised in smoke mode (proposal-only smoke
path), so no update-confirm header assertion is possible or needed in
	est_diary_smoke.py. The existing 	est_frontend* header inventory tests
provide the correct static analysis.

---

## 5. Remaining Sprint 157 Scope

### What Sprint 157 should do

1. Update orchestration/...diary_header_gap_preflight.md:
   - Change the update/confirm row from "Missing frontend header" to
     "Wired (Sprint 157)" or similar.
   - Move update-confirm out of the deferred-gap paragraph.
2. Update 	ests/test_api_spine_frontend_header_inventory.py:
   - Add 	est_frontend_update_confirm_fallback_to_random_key for parity.
   - Update 	est_frontend_remaining_confirm_callers_are_explicitly_tracked_as_missing_headers
     so confirm_update_proposal_route is no longer checked as "Missing frontend header"
     in the preflight doc (since it's now wired).
3. No changes to docs/diary/diary.js — both callers already emit the header.
4. No changes to eview/test_diary_smoke.py — smoke mode never reaches the
   update-confirm path.

### What must remain closed

- Raw PUT/PATCH/DELETE compatibility routes — header-free, unchanged.
- confirmBernieToolIntentChange — Bernie session-scoped deferral.
- Proposal-only backend header binding — deferred.
- OpenAPI minLength: 8 runtime enforcement — deferred.
- Provider calls, memory/RAG/GraphRAG, H15/H-series runtime imports,
  historical diary trove — all closed.
- Update-proposal call (POST .../proposals/update/{id}) — client header not
  wired (backend doesn't bind it yet); flag for the future proposal-only binding
  sprint.

---

## Summary

| Dimension | Verdict |
|---|---|
| Key derivation from update_proposal_freshness_id | ✅ Already correct, matches Sprint 156 pattern |
| Both call sites covered (modal + drag/resize) | ✅ Both confirmed with Idempotency-Key header |
| Raw PUT fallback header-free | ✅ Correctly scoped |
| confirmBernieToolIntentChange untouched | ✅ Correctly deferred |
| Gap preflight doc stale | ⚠️ Requires update — row still says "Missing frontend header" |
| Fallback test missing | ⚠️ Add for parity with status/delete confirm test suite |

The core implementation is done. Sprint 157 is a
**documentation-and-test-cleanup** sprint: update the gap preflight doc, add a
fallback test, and unlist update-confirm from the "missing" tracking. No JS
or backend changes required.
