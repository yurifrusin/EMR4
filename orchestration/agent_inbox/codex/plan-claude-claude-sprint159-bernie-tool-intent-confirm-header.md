# Sprint 159 — `confirmBernieToolIntentChange` Idempotency-Key: API Spine Correctness Assessment

**Reviewer:** Codex (Claude lane replacement review)  
**Date:** 2026-07-07  
**Scope:** Assess API-spine correctness of wiring `confirmBernieToolIntentChange` to send HTTP `Idempotency-Key`. Compare freshness-derived vs. Bernie session-derived key approach. Focus on same backend update-confirm route consistency and closed gates.  
**Packet:** `orchestration/agent_inbox/codex/plan-claude-claude-sprint159-bernie-tool-intent-confirm-header.md`

---

## 1. Summary

The uncommitted Sprint 159 change in the working tree is **API-spine correct** and ready to commit. It wires `confirmBernieToolIntentChange` (`docs/diary/diary.js:1742-1743`) with the existing **freshness-derived** key helper `updateConfirmIdempotencyKey`, producing `Idempotency-Key: update-confirm-{update_proposal_freshness_id}`. This is the same key-derivation pattern used by ordinary Diary update-confirm callers (`saveBooking` edit-modal confirm, `handleMoveResize` drag/resize confirm) targeting the same backend route `POST /api/v1/appointments/proposals/update/confirm`.

| Caller | Key derivation | Key pattern | Backend route family |
|---|---|---|---|
| `saveBooking` edit-modal update confirm | `updateConfirmIdempotencyKey(proposal, confirmPayload)` | `update-confirm-{freshness}` | `update-confirm` |
| `handleMoveResize` drag/resize confirm | `updateConfirmIdempotencyKey(proposal, confirmPayload)` | `update-confirm-{freshness}` | `update-confirm` |
| `confirmBernieToolIntentChange` (Sprint 159) | `updateConfirmIdempotencyKey(envelope, confirmPayload)` | `update-confirm-{freshness}` | `update-confirm` |
| Bernie create-confirm adapter (separate route) | `bernieSession.getServerRouteIdempotencyKey("create-confirm-bernie", ...)` | `create-confirm-bernie\|{sessionId}\|{turn}\|{path}` | `create-confirm-bernie` |

---

## 2. Freshness-derived vs. Bernie session-derived: the key comparison

### 2.1 Freshness-derived (this change)

```
Idempotency-Key: update-confirm-{update_proposal_freshness_id}
```

**Source:** `compute_proposal_freshness_id()` in `app/services/bernie_turn_evidence.py:183` → deterministic SHA-256/32 hex of `{current_state, command, reference_date}`. The same value used for staleness gating inside `confirm_update_proposal()` at `app/routers/appointments.py:2034`.

**Flow through the Bernie tool-intent path:**
1. `propose_bernie_tool_intent()` (`appointments.py:1937-1942`) copies `proposal.update_proposal_freshness_id` into `BernieToolIntentOut.update_proposal_freshness_id`
2. `confirmBernieToolIntentChange(envelope)` receives the `BernieToolIntentOut` JSON
3. Line 1742: `updateConfirmIdempotencyKey(envelope, confirmPayload)` checks `confirmPayload?.update_proposal_freshness_id || envelope?.update_proposal_freshness_id`
4. Both paths have the freshness ID: `confirm_payload.update_proposal_freshness_id` from `proposal.confirm_payload`, and `envelope.update_proposal_freshness_id` from the `BernieToolIntentOut` top-level field

### 2.2 Bernie session-derived (used only by create-confirm-bernie)

```
Idempotency-Key: create-confirm-bernie|<serverSessionId>|<turnRef>|<discriminator>
```

**Source:** `bernieSession.getServerRouteIdempotencyKey("create-confirm-bernie", confirmEndpoint)` at `diary.js:5175-5178`. Generated once per session-turn combination with `this.serverRouteIdempotencyKeys` caching.

### 2.3 Why freshness-derived is correct here

| Dimension | Freshness-derived | Bernie session-derived | Verdict |
|---|---|---|---|
| **Route family** | `update-confirm` — matches the backend route family exactly | Would need a separate family like `update-confirm-bernie` to be distinguishable | ✅ Freshness-derived matches route family |
| **Ordinary caller consistency** | Identical to `saveBooking` and `handleMoveResize` update-confirm callers | Different pattern — no other update-confirm caller uses session-derived keys | ✅ Freshness-derived is consistent |
| **Backend ledger** | The ledger at `claim_appointment_command` hashes with route family `update-confirm` + secret. It does not decode the client key structure | Same — ledger doesn't care about internal key structure | ✅ Both work (backend is agnostic) |
| **Staleness alignment** | The freshness ID in the key matches the freshness ID re-validated inside `confirm_update_proposal()` at line 2034. Same values, same semantics | Session-derived key carries no proposal-evidence binding | ✅ Freshness-derived aligns with staleness gate |
| **Deterministic replay** | Same proposal + same appointment state → same key → cached replay from ledger (desired) | Different per turn even for same proposal → no replay cache (overcautious) | ✅ Freshness-derived has better replay semantics |
| **Session binding** | No session binding in the idempotency key itself; session binding is done via `session_binding` body field and `turn_ref` in the `BernieUpdateProposalConfirmationIn` payload | Session-derived key puts session identity in the HTTP header | ⚠️ Nuanced — session binding has separate body-level mechanism |

**Key insight:** The Bernie create-confirm route has its own dedicated route family `create-confirm-bernie` + separate `confirm_bernie_create_proposal` handler. That's why it uses session-derived keys. The update-confirm route shares route family `update-confirm` with ordinary callers, so freshness-derived keys are the consistent choice.

---

## 3. API-Spine contract verification

### 3.1 Backend route contract

The backend `confirm_update_proposal_route` at `app/routers/appointments.py:1458` is already enforced:

```python
def confirm_update_proposal_route(
    body: BernieUpdateProposalConfirmationIn,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    ...
):
    normalized_idempotency_key = _normalize_idempotency_key(idempotency_key)
    decision = claim_appointment_command(
        ...
        operation_id="confirmAppointmentUpdateProposal",
        route_family="update-confirm",
        raw_idempotency_key=normalized_idempotency_key,
        secret=_staff_create_confirm_idempotency_secret(),
        stale_after=timedelta(minutes=10),
    )
```

The header `_normalize_idempotency_key` (`appointments.py:1240-1244`) strips whitespace and fails on empty. It does not validate structure, length, or prefix — any non-empty string passes normalization. This means both freshness-derived (`update-confirm-abc123`) and session-derived (`update-confirm|session|turn|path`) formats would work technically, but the freshness-derived approach is the intended and consistent choice.

### 3.2 Freshness ID dual-purpose check

The `update_proposal_freshness_id` already flows through the `BernieUpdateProposalConfirmationIn` body and is re-validated inside `confirm_update_proposal()` at line 2034. Using it as the idempotency key source means:

1. **Before ledger commit**: `_normalize_idempotency_key` accepts the freshness-derived key
2. **Body validation**: `_compute_update_proposal_freshness_id()` re-derives and compares against `body.update_proposal_freshness_id` (staleness gate)
3. **After commit**: The ledger stores the completed response; a retry with the same key replays the cached result because the freshness ID (and therefore the idempotency key) is deterministically recomputed

This is consistent with how ordinary update-confirm callers work — they all use the same `update_proposal_freshness_id` → `update-confirm-{freshness}` pattern and hit the same backend ledger.

### 3.3 Client-side derivation correctness

The working tree change at `diary.js:1742-1743`:

```javascript
const confirmHeaders = idempotencyHeadersFor(
    updateConfirmIdempotencyKey(envelope, confirmPayload)
);
```

**Variable naming note:** The first argument is `envelope` (the `BernieToolIntentOut` object), not `envelope.proposal` (the `AppointmentUpdateProposalOut`). This is fine because `updateConfirmIdempotencyKey` checks `confirmPayload?.update_proposal_freshness_id || proposal?.update_proposal_freshness_id`, and:

- `confirmPayload` = cloned `envelope.confirm_payload` (a `dict` with key `update_proposal_freshness_id`)
- `envelope` (the `proposal` parameter) = `BernieToolIntentOut` which has `update_proposal_freshness_id` at the top level

The freshness ID is available from either source. `confirmPayload.update_proposal_freshness_id` matches the pattern used by ordinary `updateConfirmIdempotencyKey(proposal, confirmPayload)` callers.

---

## 4. Closed gates verification

The change touches **no closed gates**:

| Gate | Status | Rationale |
|---|---|---|
| H15 semantic fixture promotion | ✅ Not touched | No H15 fixtures, no candidate builders, no local diary material |
| H43 runtime gate | ✅ Not touched | Header-only client change; no routes, providers, DB, or memory |
| H56 Bernie release gates | ✅ Not touched | No interpretation harness changes; no provider wiring |
| H57 runtime isolation | ✅ Not touched | Production `app/` Python unchanged |
| H65 memory boundary | ✅ Not touched | No Access AI, no practice knowledge, no memory |
| Proposal-only header binding | ✅ Untouched | `propose_update_appointment`, `propose_status_update`, `propose_waiting_area_update`, `propose_delete_appointment` remain header-free |
| Raw PUT compatibility | ✅ Untouched | `PUT /appointments/{id}` remains unchanged |
| Strict `minLength: 8` enforcement | ✅ Untouched | Backend `_normalize_idempotency_key` uses `strip()` only |

---

## 5. Risk assessment of the uncommitted change

| Risk | Assessment |
|---|---|
| **Backward compatibility** | ✅ Low — adds header to existing POST call; no existing clients break because `confirmBernieToolIntentChange` is the only caller |
| **Key collision with ordinary callers** | ✅ Low — the freshness ID is computed from different coordinates (Bernie tool-intent extension vs. ordinary edit), so `update-confirm-{freshness}` will differ |
| **Header already present** | ✅ None — current committed code has no `Idempotency-Key` header on this path |
| **Smoke mode** | ✅ Unaffected — `if (isSmokeMode())` returns early before the header code runs |
| **Error handling** | ✅ Unchanged — header is still just a request enhancement; errors come from response parsing as before |
| **Session binding** | ✅ Independent — session binding goes through `session_binding` body field (`BernieUpdateProposalConfirmationIn`), not the HTTP header |

---

## 6. Verdict

| Criterion | Verdict |
|---|---|
| API-spine correct | ✅ Yes — freshness-derived key matches route family `update-confirm` |
| Consistent with same-route callers | ✅ Yes — same `updateConfirmIdempotencyKey` helper as `saveBooking` and `handleMoveResize` |
| Backend ledger compatible | ✅ Yes — `claim_appointment_command` accepts any non-empty normalized key |
| Freshness-aligned with staleness gate | ✅ Yes — same `update_proposal_freshness_id` used for both key derivation and body-level staleness check |
| Closed gates respected | ✅ Yes — no gate-triggering surfaces touched |
| Ready to commit | ✅ Yes — the uncommitted working tree diff is the complete Sprint 159 fix |

**Recommendation:** This change is API-spine correct and does not require a session-derived key for the update-confirm route. The freshness-derived approach with `updateConfirmIdempotencyKey` is the right pattern for this route family. Commit the working tree diff as-is, bump the asset version in `diary.html`, and proceed to Sprint 160 (Bernie/Diary review-readiness packet).

