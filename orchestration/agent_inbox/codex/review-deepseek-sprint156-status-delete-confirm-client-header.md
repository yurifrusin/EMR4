# Sprint 156 DeepSeek Adversarial Review — Status-Confirm / Delete-Confirm Client-Only `Idempotency-Key` Header Wiring

| Item | Value |
|---|---|
| **Review type** | Adversarial (DeepSeek) |
| **Sprint** | 156 |
| **Target** | `docs/diary/diary.js` — client-only `Idempotency-Key` header emission for `applySignedStatusProposal` and `applySignedDeleteProposal` |
| **Runtime behaviour changed** | No (review artifact only) |
| **Reviewer sprints** | 124 (idempotency gap), 154 (preflight), 155 (create-confirm client wiring), 156 (this review) |

---

## 1. Key Source: Prefer Proposal Freshness ID, Not Element-Bound Random

**Recommendation:** Use each proposal's server-generated `[status|delete]_proposal_freshness_id` as the idempotency key source, not an element-scoped random UUID.

### Current create-confirm pattern (Sprint 155)

The create-confirm path uses `ensureElementConfirmIdempotencyKey(saveBtn)` — a random UUID stored on `btn-booking-save.dataset.confirmIdempotencyKey`. This works because:
- The `saveBooking` function owns a long-lived button element.
- `resetProposalConfirmation()` clears it between new-booking cycles.
- The booking modal lifecycle matches one logical confirm attempt.

### Why status/delete confirm differ

1. **`applySignedStatusProposal`** is called from `setAppointmentStatus`, which is triggered by a `<select>` element on the diary grid — a reuse-scoped element. A dataset on a reused `<select>` risks stale keys across rapid status changes for different appointments.

2. **`applySignedDeleteProposal`** is called from `deleteBooking`, which owns `btn-booking-delete`. An element-bound key *could* work here (same lifecycle as create confirm), but using different key-source strategies for two structurally identical confirm paths adds cognitive overhead.

3. Both endpoints receive the full **proposal object** from the backend, which already carries a unique `[status|delete]_proposal_freshness_id` — a server-generated UUID scoped to that exact proposal. The backend `claim_appointment_command` hashes the raw key with `HMAC-SHA256(secret_key, raw_key)`, so the key does not need to be unpredictable or element-scoped. It needs to be **stable for the same confirm attempt** (retries of the same API call with same proposal must produce the same key) and **unique across logically distinct confirm attempts** (different proposals must produce different keys).

### Recommended key derivation

```javascript
// Inside applySignedStatusProposal and applySignedDeleteProposal:
const confirmKey = proposal.status_proposal_freshness_id   // or delete_proposal_freshness_id
  || generateClientIdempotencyKey();  // fallback for edge case
```

This approach:
- Is **deterministic from the proposal** — no element lifecycle dependency.
- Is **naturally stable** across retries (same proposal → same key).
- Is **naturally unique** across distinct confirm attempts (different proposals → different freshness IDs).
- **Avoids stale-key hazards** on reused grid elements.
- **Matches the claim_appointment_command design** — the backend already binds key to operation + body hash, and the freshness ID is the natural server-side proposal identifier.

### Alternative considered and rejected

| Option | Problem |
|---|---|
| Element-bound random on `btn-booking-delete` | Works for delete, but requires a different strategy for status confirm (no long-lived button). Asymmetric key sources for structurally identical paths. |
| Element-bound random on status `<select>` | Grid-level reuse hazard — same `<select>` element fires successive confirm calls for different appointments, retaining the old key. |
| Appointment-scoped (`appt.id + route`) | Not proposal-version-scoped. Two sequential proposals for the same appointment would collide. |
| Bernie session scoped (`getServerRouteIdempotencyKey`) | Created for Bernie session event replay, not staff workflow. Session reset clears all keys, which breaks the 10-minute stale-after window used by the backend. |

---

## 2. Call Sites and Tests for Sprint 156

### Call sites that must emit the header

| Function | Confirm branch | Endpoint | Action |
|---|---|---|---|
| `applySignedStatusProposal` (L8121) | `if (confirmEndpoint && confirmPayload)` | `POST … proposals/status-confirm` | Add `Idempotency-Key` header from `proposal.status_proposal_freshness_id` |
| `applySignedDeleteProposal` (L8165) | `if (confirmEndpoint && confirmPayload)` | `POST … proposals/delete-confirm` | Add `Idempotency-Key` header from `proposal.delete_proposal_freshness_id` |

### Call sites that must **not** emit the header

| Function | Branch | Reason |
|---|---|---|
| `applySignedStatusProposal` (L8143) | Raw fallback `PATCH /appointments/{id}/status` | Deferred per gap doc — compatibility write, not canonical confirm |
| `applySignedDeleteProposal` (L8183) | Raw fallback `DELETE /appointments/{id}` | Deferred per gap doc — compatibility write, not canonical confirm |
| `applySignedStatusProposal` (L8121) | confirm branch but no idempotency *outside* status prefix | Confirm not-scoped prefix must not get header |
| `applySignedDeleteProposal` (L8165) | Similar | Same guard |

### Explicit fixture gaps

No fixture currently proves the status-confirm or delete-confirm confirm endpoints accept the proposal freshness ID as an `Idempotency-Key`. The backend `claim_appointment_command` is route-family-agnostic for key binding, but the frontend test should synthetically assert:

- `proposal.status_proposal_freshness_id` is a non-empty string
- `proposal.delete_proposal_freshness_id` is a non-empty string
- The header value matches the freshness ID when present
- The header is `undefined`/absent when freshness ID is missing (fallback to `generateClientIdempotencyKey()`)

### Frontend header inventory test updates

In `tests/test_api_spine_frontend_header_inventory.py`:

1. **Promote** `test_frontend_remaining_confirm_callers_are_explicitly_tracked_as_missing_headers` — remove `applySignedStatusProposal` and `applySignedDeleteProposal` from the "missing" block; add them to a new passing block that asserts header emission.

2. **Add** `test_frontend_status_confirm_emits_header` — verify `applySignedStatusProposal` contains `"Idempotency-Key"` and the key source references `status_proposal_freshness_id`.

3. **Add** `test_frontend_delete_confirm_emits_header` — verify `applySignedDeleteProposal` contains `"Idempotency-Key"` and the key source references `delete_proposal_freshness_id`.

4. **Add** `test_frontend_status_delete_confirm_fallback_to_random_key` — verify the fallback path (freshness ID missing) uses `generateClientIdempotencyKey()`.

5. **Update** the `test_frontend_remaining_confirm_callers…` test: keep `saveBooking update confirm`, `confirmBernieToolIntentChange` as missing. Remove `applySignedStatusProposal` and `applySignedDeleteProposal`.

### Backend-side guard tests (already passing, no change needed)

- `test_api_spine_appointment_idempotency_gap.py` — already binds `Idempotency-Key` for `confirm_status_proposal_route` and `confirm_delete_proposal_route`.
- `test_api_spine_appointment_idempotency_route_integration_preflight.py` — already proves header parameter binding.
- `test_api_spine_appointment_idempotency_policy_packet.py` — already records both route families.

---

## 3. What Must Remain Deferred

### update-confirm client header

The `saveBooking` update branch (create-case fallback for `editingAppointmentId`), drag/reschedule (`handleMoveResize`), and the Bernie update confirm (`confirmBernieToolIntentChange`) all call the `confirm_update_proposal_route` endpoint which already requires `Idempotency-Key`. The client must not emit this header until a later sprint because:

- The update confirm caller (`saveBooking` update branch) uses a different proposal lifecycle (reuses `saveBtn` element, but the confirm endpoint is `update/confirm` not `create/confirm` — the `isCreateConfirmEndpoint` guard currently excludes it).
- Drag/resize uses a distinct flow with no proposal dialog at all (the `needsConfirm` flag is separate).
- The `confirmBernieToolIntentChange` function uses Bernie session event routing and requires Bernie-specific key scoping.

Sprint 156 must **not** change update-confirm callers. The preflight doc explicitly deferred them.

### Proposal-only backend header binding

The proposal routes (`propose_status_update`, `propose_delete_appointment`, `propose_update_appointment`, `propose_waiting_area_update`) do not bind `Idempotency-Key` on the backend. Sprint 156 must **not** add client headers for proposal routes. The backend `Header(None)` binding is a separate backend change that would need coordination, and the preflight doc explicitly deferred proposal-only binding.

### Bernie tool-intent confirm

`confirmBernieToolIntentChange` calls a Bernie-specific confirm flow. Its idempotency strategy should be Bernie session-scoped (like the Bernie review confirm path that uses `bernieSession.getServerRouteIdempotencyKey("create-confirm-bernie", ...)`), not proposal-freshness-scoped. Defer to a future sprint.

### `minLength: 8` enforcement

The OpenAPI spec documents `minLength: 8` for `Idempotency-Key`. The backend does not enforce this yet (accepts any non-empty string). Deferred.

### Raw compatibility routes

`PATCH /appointments/{id}/status` and `DELETE /appointments/{id}` must remain header-free in Sprint 156. The gap doc notes these are "not part of the canonical OpenAPI command `paths:`" and require a policy decision before implementation.

---

## 4. Boundaries That Must Remain Closed

| Boundary | Sprint 156 posture | Unchanged from |
|---|---|---|
| Live provider calls | Not wired | Sprint 154 preflight |
| Memory/RAG/GraphRAG runtime wiring | Not wired | Sprint 154 preflight |
| H15/H-series runtime imports | Not imported | H53 runtime gate |
| Broad historical diary trove mining | Not performed | Sprint 154 preflight |
| GraphQL mutations | Not wired | Sprint 154 preflight |
| Raw compatibility route headers | Not changed | Sprint 154 preflight |
| Bernie session route idempotency expansion | Not expanded | Sprint 154 preflight |
| Proposal-only backend header binding | Not changed | Sprint 124 gap doc |
| `minLength: 8` runtime enforcement | Not added | Sprint 124 gap doc |
| update-confirm client header | Not wired | Preflight doc, deferred |
| Model-to-database writes | Not changed | Sprint 124 gap doc |

---

## Summary of Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Stale key on reused status `<select>` element | Medium | Use proposal freshness ID, not element dataset |
| Asymmetric key strategy creates maintenance burden | Medium | Use same key source (freshness ID) for both status and delete confirm |
| Fallback to random key hides missing freshness ID | Low | Test asserts fallback is only taken when freshness ID is falsy |
| Accidental header emission in raw fallback branch | Low | Confirm-branch-only scope; test proves raw fallback has no header |
| Update-confirm accidentally wired with wrong key scope | Medium | Do not touch `saveBooking` update branch, drag/resize paths, or `confirmBernieToolIntentChange` |
