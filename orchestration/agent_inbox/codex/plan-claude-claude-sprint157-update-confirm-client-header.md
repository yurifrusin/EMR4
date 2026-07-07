# plan-claude-claude-sprint157-update-confirm-client-header

| Item | Value |
|---|---|
| From | claude |
| Branch | claude/current |
| Kind | Plan/review artifact (plan gate — no runtime wiring) |
| Programme | 2G — diary/API header discipline |
| Prior sprints | 152 (create-proposal minLength deferred-with-guard), 153 (create-proposal client header), 154 (confirm-surface preflight), 155 (create-confirm client header), 156 (status/delete confirm client header) |
| Files reviewed | docs/diary/diary.js, 	ests/test_api_spine_frontend_header_inventory.py, eview/test_diary_smoke.py, orchestration/api_spine_appointment_idempotency_update_confirm_client_header.md, orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md, AGENTS.md, orchestration/phase_programmes.md, docs/diary/diary.html |

## Packet Note

The Sprint 157 worker packet is orchestration/agent_inbox/claude/claude-sprint157-update-confirm-client-header.md.
The implementation (Sprint 157 changes) is **uncommitted** in the working tree on master.
The dispatch commit 8adf9d40 added only the two worker packets.

## Sprint 157 Implementation Summary

Three surfaces changed; one new orchestration doc; two existing docs updated.

### diary.js — updateConfirmIdempotencyKey() + call-site wiring

New function updateConfirmIdempotencyKey(proposal, confirmPayload) (line 7072) delegates to
confirmIdempotencyKeyFromFreshness("update-confirm", freshnessId, proposal), consistent with the
Sprint 156 status/delete pattern. Freshness is read from
confirmPayload?.update_proposal_freshness_id || proposal?.update_proposal_freshness_id, with
fallback to ensureProposalConfirmIdempotencyKey(proposal, "update-confirm") when absent or
prefix+key exceeds 128 characters.

Two call sites now send headers: confirmHeaders:

| Call site | Function | Header line | Raw PUT fallback still header-free? |
|---|---|---|---|
| Edit-modal detail update confirm | saveBooking() | diary.js:7584 | Yes (line 7588 same piFetch, no header) |
| Drag/move/resize confirm | handleMoveResize() | diary.js:8128 | Yes (line 8132 same piFetch, no header) |

confirmBernieToolIntentChange() remains header-free and is documented as the remaining ordinary
confirm-client gap.

### test_api_spine_frontend_header_inventory.py — structural guards

Three changes:

1. **	est_frontend_update_confirm_callers_emit_stable_headers()** — new test asserting both
   saveBooking() and handleMoveResize() update-confirm blocks contain
   updateConfirmIdempotencyKey(proposal, confirmPayload) and headers: confirmHeaders.

2. **	est_frontend_update_confirm_falls_back_to_proposal_scoped_key()** — new test asserting the
   update key function references "update-confirm", update_proposal_freshness_id, and the
   ensureProposalConfirmIdempotencyKey fallback.

3. **	est_frontend_remaining_confirm_callers_are_explicitly_tracked_as_missing_headers()** —
   removed the saveBooking update confirm branch block from the missing-headers dict and updated
   the expected preflight phrase check from "Missing frontend header" to
   "confirmBernieToolIntentChange". This correctly reflects that only the Bernie tool-intent path
   remains keyless.

### review/test_diary_smoke.py — route-intercepted idempotency-key assertions

	est_human_drag_resize_uses_signed_update_confirm_route and
	est_edit_modal_uses_signed_update_confirm_before_status_patch now capture the
idempotency-key header from intercepted confirm POSTs and assert exact expected values:

| Test | Expected header value |
|---|---|
| Human drag/resize | update-confirm-human-fresh-1 |
| Edit modal detail update | update-confirm-edit-fresh-1 |

Both tests re-structured captured_confirms entries from raw equest.post_data_json to
{body: ..., idempotency_key: ...} dicts, improving readability while maintaining backward
assertion coverage for body fields (confirmed, ppointment_id, duration_minutes, etc.).

### Preflight doc and supporting files

orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md:
- "Current Covered Callers" table now lists saveBooking update-confirm and drag/reschedule
  update-confirm as "Wired in Sprint 157" instead of "Missing frontend header".
- confirmBernieToolIntentChange is footnoted as remaining deferred.
- Follow-up recommendation changed from "Sprint 155 should wire create-confirm first" to
  "run a compact confirm-client surface checkpoint" before choosing the next slice.
- Sprint 155 Recommendation heading renamed to Follow-Up Recommendation.

AGENTS.md: Baton table updated — current track is Sprint 157; next work is the compact checkpoint.

orchestration/phase_programmes.md: Representative Sprints list extended with Sprint 157;
next-candidate sprints updated to the compact checkpoint.

docs/diary/diary.html: diary.js?v=177 bumped to =178.

## Command/Idempotency Boundary Assessment

### Implemented boundary is correct

- **Freshness-derived keys stay scoped to the proposal object.** The same update_proposal_freshness_id
  produces the same key on retry, so double-submits create a ledger replay rather than a double-write.
  This is the same contract as status/delete confirm (Sprint 156).
- **Raw PUT fallbacks are airtight.** Both saveBooking() and handleMoveResize() only fall to the
  PUT path when confirmEndpoint or confirmPayload is falsy. Those branches use piFetch
  without any header injection, preserving the header-free compatibility posture.
- **Prefix isolation.** update-confirm- prefix is distinct from create-confirm- (155),
  status-confirm- (156), delete-confirm- (156), and the proposal-level keys from Sprint 153.
- **Three-tier key sourcing** (confirmPayload → proposal → generated fallback) matches the
  status/delete confirm precedent identically.

### No new backend, OpenAPI, or ledger changes

The FastAPI confirm routes (confirm_update_proposal_route) already bind and normalize the header.
No route decorator, schema, or _normalize_idempotency_key changes were needed or made. This is
correct — Sprint 157 is exclusively client-side header emission.

## Deferrals

### Remaining tracked gap: confirmBernieToolIntentChange()

confirmBernieToolIntentChange() (diary.js:1716) still POSTs with only method: "POST" and
ody: JSON.stringify(confirmPayload) — no Idempotency-Key. This is the one remaining ordinary
confirm-client gap. The orchestration doc correctly defers it as a Bernie-specific surface:
- The function receives an envelope from Bernie's tool-intent flow, not a staged Diary proposal
- The key semantics would involve a server-session or tool-intent discriminator
- Best handled in a Bernie-specific sprint with its own key strategy doc

### Properly closed gaps

| Gap (from Sprint 154 preflight) | Sprint | Status |
|---|---|---|
| saveBooking create-proposal | 153 | ✅ Wired |
| saveBooking create-confirm | 155 | ✅ Wired |
| Bernie review confirm adapter (create-confirm-bernie) | 155 | ✅ Wired |
| pplySignedStatusProposal | 156 | ✅ Wired |
| pplySignedDeleteProposal | 156 | ✅ Wired |
| saveBooking update-confirm | 157 | ✅ Wired |
| drag/reschedule update-confirm | 157 | ✅ Wired |
| confirmBernieToolIntentChange | Deferred | ❌ Still header-free |
| Proposal-only backend binding | Deferred | ⏸️ No route changes |
| OpenAPI minLength: 8 runtime enforcement | Deferred | ⏸️ No backend changes |
| Raw PUT/PATCH/DELETE compatibility | Deferred | ⏸️ Header-free by design |

## Test Gap Found

**	est_frontend_header_preflight_keeps_closed_gates_closed** in
	ests/test_api_spine_frontend_header_inventory.py asserts that the preflight doc contains:

`python
assert "Sprint 155 should wire the create-confirm client header path first" in text
`

This phrase was **removed** from the updated preflight (replaced with a follow-up recommendation
about a compact checkpoint). The test will **fail** on the current working tree.

This is the only test gap identified. It is a test-side preflight assertion that references a stale
sentence, not a correctness issue with the diary.js or smoke test changes. The fix is to update the
assertion to match the current preflight text, e.g.:

`python
assert "run a compact confirm-client surface checkpoint" in text
`

## Confirm-Client Checkpoint Assessment

### Should a checkpoint be next?

**Yes.** The preflight doc already recommends it, and the reasoning is sound:

1. **All ordinary Diary confirm surfaces now emit headers.** The six-table cell from Sprint 154's
   preflight is at 6/6 ordinary wires. The remaining gap (confirmBernieToolIntentChange) is
   tangibly different — it enters through Bernie's tool-intent path, not a staged Diary proposal.

2. **Three architecturally distinct next-slice candidates exist:**
   - **Bernie tool-intent confirm header** — requires a server-session/tool-intent key strategy doc
     before implementation. No route or backend changes needed.
   - **Proposal-only backend header binding** — requires FastAPI route handler changes for
     propose_update_appointment, propose_status_update, propose_waiting_area_update, and
     propose_delete_appointment. Frontend header emission is already in place for most proposal
     callers (Sprint 153). This is a backend change.
   - **Strict minLength: 8 runtime enforcement** — requires backend schema/guard changes.

3. **The checkpoint scope is bounded:**
   - Inventory the four remaining confirm-header-outstanding callers (Bernie tool-intent, the three
     proposal-only backend routes, raw compatibility paths)
   - Decide which slice to implement next
   - Confirm that no Sprint 155-157 regression was introduced (all preflight-deferred gates remain
     closed: no providers, no GraphQL, no H15/H-series, no memory/RAG/GraphRAG, no raw compatibility
     header pollution, no backend ledger/minLength changes)
   - Update the preflight doc and tests for the chosen next slice

### Recommended checkpoint scope

A compact confirm-client surface checkpoint should:

1. Verify the full confirm-header inventory is up-to-date in the preflight doc
2. Select one of the three deferred candidates for the next sprint
3. Update 	est_frontend_header_preflight_keeps_closed_gates_closed to match current preflight text
4. Preserve all other closed-gate assertions (raw compatibility, providers, H15/H-series, etc.)
5. Document the decision with rationale

## Sprint 157 Closeout Checklist

- [x] diary.js: updateConfirmIdempotencyKey() function present (line 7072)
- [x] diary.js: saveBooking() update-confirm branch sends headers: confirmHeaders (line 7584)
- [x] diary.js: handleMoveResize() update-confirm branch sends headers: confirmHeaders (line 8128)
- [x] diary.js: Raw PUT fallbacks in both call sites remain header-free
- [x] diary.js: confirmBernieToolIntentChange() remains deferred (no header)
- [x] diary.js: Existing statusConfirmIdempotencyKey/deleteConfirmIdempotencyKey/isCreateConfirmEndpoint unchanged
- [x] inventory test: 	est_frontend_update_confirm_callers_emit_stable_headers() new
- [x] inventory test: 	est_frontend_update_confirm_falls_back_to_proposal_scoped_key() new
- [x] inventory test: saveBooking update confirm branch removed from missing-headers block
- [x] inventory test: preflight phrase check updated to confirmBernieToolIntentChange
- [x] smoke test: drag/resize asserts update-confirm-human-fresh-1
- [x] smoke test: edit modal asserts update-confirm-edit-fresh-1
- [x] preflight doc: table updated, follow-up recommendation updated
- [x] AGENTS.md: baton table updated
- [x] phase_programmes.md: rep sprints and next-candidate updated
- [x] diary.html: cache bust v177→v178
- [ ] **test gap:** 	est_frontend_header_preflight_keeps_closed_gates_closed asserts stale phrase
      — update to match current preflight text
- [ ] **checkpoint:** Run 	est_frontend_header_preflight_keeps_closed_gates_closed fix together
      with the confirm-client surface checkpoint decision

## Boundary Confirmation

This artifact is plan/review only. No production code, tests, OpenAPI, diary UI, taskpane, or
migrations were edited; no runtime behaviour was wired. The review confirms Sprint 157 preserves
the deliberate 152-157 posture: backend stays non-blank-required with the existing ledger; raw
compatibility paths stay header-free; providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, and
historical diary trove gates remain closed.
