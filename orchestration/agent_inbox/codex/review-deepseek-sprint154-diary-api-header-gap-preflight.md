# DeepSeek Flash — Sprint 154 Diary API Header Gap Preflight

| Item | Value |
|---|---|
| Sprint | 154 |
| Worker | DeepSeek Flash |
| Programme | Programme 2G / EMR4 API Spine |
| Review date | 2026-07-07 |
| Files examined | docs/diary/diary.js, app/routers/appointments.py, orchestration/api_spine_appointment_idempotency_create_proposal_header_alignment.md, orchestration/api_spine_appointment_idempotency_create_proposal_minlength_readiness.md, orchestration/api_spine_appointment_idempotency_proposal_only_preflight.md, orchestration/api_spine_programme.md, tests/test_api_spine_create_proposal_header_alignment.py, tests/test_api_spine_create_proposal_idempotency_route_contract.py, review/test_diary_smoke.py, review/checks_diary.json |
| Status | Adversarial review (no runtime changes) |

## Scope

Sprint 154 is a preflight/inventory for remaining diary/API `Idempotency-Key` gaps after Sprint 153. Do not change runtime behavior. Do not wire providers, GraphQL mutations, H15/H-series imports, memory/RAG/GraphRAG, raw compatibility idempotency, or broad trove access.

---

## 1. Which diary frontend callers currently emit HTTP `Idempotency-Key` headers?

**Exactly one caller.** Sprint 153 (commit `9d7f9bda`) added `generateClientIdempotencyKey()` and wired it into the `saveBooking()` function's create-proposal path only — when `!editingAppointmentId` and the modal posts to `POST /appointments/proposals/create`. The key is scoped to `saveBtn.dataset.idempotencyKey`, generated lazily on first save, and cleared by `resetProposalConfirmation()` on modal reset.

**Every other apiFetch call site in diary.js emits NO `Idempotency-Key` header.** This includes all of:

- `saveBooking()` update-proposal path (`POST /proposals/update/{id}`)
- `saveBooking()` confirm path (both create and update, when `confirmEndpoint` is present)
- `confirmBernieToolIntentChange()` — Bernie envelope confirm endpoint
- `applySignedStatusProposal()` — status-confirm or raw PATCH fallback
- `applySignedDeleteProposal()` — delete-confirm or raw DELETE fallback
- `setAppointmentStatus()` — status-proposal and waiting-area-proposal endpoints
- `deleteBooking()` — delete-proposal endpoint
- All raw compatibility writes: `POST /appointments`, `PUT /{id}`, `PATCH /{id}/status`, `DELETE /{id}`
- All Bernie session, interpret, supervised-booking, slot-search, no-slot routes

**Key gap waterfall:** The backend now has 6 routes (all 4 confirm routes + create-proposal + Bernie create-confirm) that REQUIRE a non-blank `Idempotency-Key` via `_normalize_idempotency_key()` or `_normalize_create_proposal_idempotency_key()`. Only 1 of those 6 routes currently receives the header from diary.js.

---

## 2. Which confirm/proposal/status/delete appointment API surfaces require, document, or lack idempotency headers?

### Surfaces That REQUIRE `Idempotency-Key` (backend enforced, frontend missing)

| FastAPI route | Function | Frontend caller in diary.js | Header sent? | Will fail? |
|---|---|---|---|---|
| `POST /proposals/create` | `propose_create_appointment` | `saveBooking()` line 7397 | ✅ Yes (Sprint 153) | No |
| `POST /proposals/create/confirm` | `confirm_create_proposal_route` | `saveBooking()` line 7565 (when `confirmEndpoint` present) | ❌ No | **Yes** |
| `POST /proposals/create/confirm-bernie` | `confirm_bernie_create_proposal` | `confirmBernieToolIntentChange()` line 1734; Bernie confirm adapter line 5169 | ❌ No | **Yes** |
| `POST /proposals/update/confirm` | `confirm_update_proposal_route` | `saveBooking()` line 7530 (when update `confirmEndpoint` present) | ❌ No | **Yes** |
| `POST /proposals/status-confirm` | `confirm_status_proposal_route` | `applySignedStatusProposal()` lines 8089-8097 | ❌ No | **Yes** |
| `POST /proposals/delete-confirm` | `confirm_delete_proposal_route` | `applySignedDeleteProposal()` lines 8136-8144 | ❌ No | **Yes** |

### Surfaces That LACK Backend Header Binding (known proposal-only gaps, no rejection)

| FastAPI route | Function | Frontend caller in diary.js | Header sent? | Will fail? | Documented? |
|---|---|---|---|---|---|
| `POST /proposals/update/{id}` | `propose_update_appointment` | `saveBooking()` line 7400 (when `editingAppointmentId`) | ❌ No | No (backend doesn't bind) | ✅ Sprint 152+ |
| `POST /proposals/status/{id}` | `propose_status_update` | `setAppointmentStatus()` line 8212 | ❌ No | No | ✅ Sprint 152+ |
| `POST /proposals/delete/{id}` | `propose_delete_appointment` | `deleteBooking()` line 7675 | ❌ No | No | ✅ Sprint 152+ |
| `POST /proposals/waiting-area/{id}` | `propose_waiting_area_update` | `setAppointmentStatus()` line 8205 | ❌ No | No | ✅ Sprint 152+ (part of status group) |

### Surfaces That LACK Backend Header Binding (compatibility raw writes)

| FastAPI route | Function | Frontend caller in diary.js | Header sent? | Documented? |
|---|---|---|---|---|
| `POST /appointments` | `create_appointment` | `saveBooking()` line 7569 (no confirm endpoint) | ❌ No | Deferred |
| `PUT /{appointment_id}` | `update_appointment` | `saveBooking()` line 7542 (no confirm endpoint) | ❌ No | Deferred |
| `PATCH /{id}/status` | `update_appointment_status` | `saveBooking()` line 7551, `setAppointmentStatus()` line 8246 | ❌ No | Deferred |
| `DELETE /{id}` | `cancel_appointment` | `applySignedDeleteProposal()` line 8155, `deleteBooking()` line 7697 | ❌ No | Deferred |

### Bernie Session/Non-Proposal Surfaces (out of scope for Proposal 2G)

These routes do not bind `Idempotency-Key` in FastAPI and diary.js does not send one. They use session-level idempotency via `server_session_idempotency_key` in the request body instead of an HTTP header:

| Route | Diary.js caller |
|---|---|
| `POST /bernie/sessions/new` | `BernieSession.refresh()` |
| `POST /bernie/sessions/{id}/events` | `BernieSession.appendEvent()` |
| `POST /proposals/bernie/interpret-booking-instruction` | `interpretBernieBookingInstruction()` |
| `POST /proposals/bernie/tool-intent` | Various Bernies callers |
| `POST /proposals/bernie/supervised-booking` | `handleSupervisedBernieBooking()` |
| `POST /proposals/bernie/no-slot-suggestion-selection` | `selectNoSlotSuggestion()` |
| `POST /proposals/slot-search` and variants | Various slot callers |
| `GET /appointments/bernie/sessions/active` | Various Bernies callers |

---

## 3. Which next slice is safest for Sprint 155 and why?

### Recommendation: Wire the create-confirm path (staff + Bernie)

The safest next slice is wiring `Idempotency-Key` on the **create-confirm callers** — both staff (`proposals/create/confirm`) and Bernie (`proposals/create/confirm-bernie`) — for these reasons:

1. **Continuity from Sprint 153.** The create-proposal path is already wired. The confirm path is the immediate next hop in the same modal flow. Same lifecycle, same `saveBtn.dataset.idempotencyKey`, same `generateClientIdempotencyKey()` function.

2. **Already broken.** All confirm routes already require a non-blank `Idempotency-Key` on the backend. The frontend does not send one. Every Bernie pilot flow that reaches the confirm stage WILL fail with `400 idempotency_key_required`. This is not a speculative gap — it's a runtime bug waiting to surface.

3. **Same-key reuse is correct.** The same modal-scoped key that identifies the `proposals/create` call should also identify the subsequent `proposals/create/confirm` call. They are part of the same logical "create appointment" operation. The backend's confirm-idempotency ledger already deduplicates by key, so reusing the proposal key gives free retry alignment: if the proposal succeeded and the confirm call fails with a network error, retrying with the same key replays the confirmation response rather than creating a duplicate appointment.

4. **Small surface area.** The confirm create staff route (`confirm_create_proposal_route`) and Bernie route (`confirm_bernie_create_proposal`) share the same `_normalize_idempotency_key()` and `claim_appointment_command()` semantics. Both need the same header. The fix is a few lines in `saveBooking()` and `confirmBernieToolIntentChange()`.

### Rejected alternatives

| Alternative | Risk |
|---|---|
| Wire update/status/delete proposal routes | These are the broader "3-of-4 unwired" gap from Sprint 152. But backends don't enforce the header yet, so there's no immediate breakage. Doing this first would add client-discipline boilerplate without fixing a real bug. |
| Wire the status-confirm path | Also broken. But the status-confirm flow (via `applySignedStatusProposal`) is structurally different from the create flow, uses a different lifecycle, and doesn't have the same connected-modal context. Higher complexity. |
| Wire the delete-confirm path | Same reasoning as status-confirm — structurally different caller path, different lifecycle. Also less commonly exercised than create-confirm. |
| Wire all confirm routes at once | Too broad for one sprint. Would touch 6 different caller paths with different modal/lifecycle contexts. Better to do create-confirm first (simplest) and extend patterns to other confirm routes in subsequent sprints. |

### Deferred to Sprint 156+

- Update/status/delete proposal-only header binding on the backend (address the "3-of-4" gap)
- Status-confirm and delete-confirm frontend header emission (extend the confirm pattern)
- Raw compatibility write idempotency (requires separate policy sprint per Sprint 147 preflight)
- minLength:8 enforcement on the backend (requires all 5 client-readiness preconditions from Sprint 152)

---

## 4. What tests should Ariadne add in Sprint 154 to keep this inventory from drifting?

The existing test suite (`test_api_spine_create_proposal_header_alignment.py`) tracks backend header binding gaps and OpenAPI alignment. It does not track frontend caller coverage. Sprint 154 should add:

### 4a. Frontend caller inventory guard (new test file)

Add `tests/test_api_spine_frontend_header_inventory.py` that parses `docs/diary/diary.js` and:

1. Counts all `apiFetch(` call sites and classifies them by known status (`wired_known`, `confirm_endpoint`, `proposal_only`, `raw_write`, `bernie_session`, `read_only`, `admin`).
2. Asserts that exactly 1 caller currently sends `Idempotency-Key` (the create-proposal path).
3. Asserts that the 5 confirm-route callers are explicitly documented as unwired (by function name: `saveBooking` confirm path, `confirmBernieToolIntentChange`, `applySignedStatusProposal`, `applySignedDeleteProposal`).
4. Asserts that the 4 proposal-only callers are explicitly documented as unwired (`saveBooking` update path, `setAppointmentStatus` status/waiting-area paths, `deleteBooking` delete path).
5. Lists the known unwired total as a safety counter that fails when new unwired callers appear without documentation.

### 4b. Confirm-route caller name test

Add to the existing `test_api_spine_create_proposal_header_alignment.py`:

1. Assert that every confirm route (`confirm_create_proposal_route`, `confirm_update_proposal_route`, `confirm_status_proposal_route`, `confirm_delete_proposal_route`, `confirm_bernie_create_proposal`) in `app/routers/appointments.py` is matched by an `UNWIRED_CONFIRM_CALLERS` tuple that names the frontend function expected to wire it.
2. If a new confirm route is added to the backend, the test fails until its frontend caller is documented as wired or unwired.

### 4c. Proposal-route gap cross-reference (strengthen existing test)

Extend `test_fastapi_proposal_header_binding_gap_is_explicitly_documented` to also cross-reference `propose_waiting_area_update` in the unwired set. The current `UNWIRED_PROPOSAL_HANDLERS` tuple covers update/status/delete but omits waiting-area, which is also a proposal-only route without header binding.

### 4d. Confirm-route will-fail documentation test

Add a test that lists all confirm routes and asserts a `docs/` or `orchestration/` document names which frontend callers currently do NOT send the required header. The Sprint 154 review artifact itself can serve as that documentation, but the test should fail if the document does not list all 5 broken confirm callers.

---

## Drift test pseudo-code (illustrative only, not a patch)

```
# tests/test_api_spine_frontend_header_inventory.py (illustrative shape)

WIRED_CREATE_PROPOSAL = "saveBooking_create_proposal"
KNOWN_UNWIRED_CONFIRM = [
    "saveBooking_confirm",
    "confirmBernieToolIntentChange",
    "applySignedStatusProposal",
    "applySignedDeleteProposal",
]
KNOWN_UNWIRED_PROPOSAL = [
    "saveBooking_update_proposal",
    "setAppointmentStatus_status_proposal",
    "setAppointmentStatus_waiting_proposal",
    "deleteBooking_delete_proposal",
]
KNOWN_UNWIRED_RAW_WRITE = ...

def test_frontend_confirms_are_explicitly_tracked():
    diary_source = DIARY_JS.read_text()
    confirm_refs = find_confirm_endpoint_calls(diary_source)
    known = WIRED_CREATE_PROPOSAL + KNOWN_UNWIRED_CONFIRM
    for ref in confirm_refs:
        assert ref in known, f"New unwired confirm caller: {ref}"

def test_frontend_proposals_are_explicitly_tracked():
    diary_source = DIARY_JS.read_text()
    proposal_refs = find_proposal_endpoint_calls(diary_source)
    known = [WIRED_CREATE_PROPOSAL] + KNOWN_UNWIRED_PROPOSAL
    for ref in proposal_refs:
        assert ref in known, f"New unwired proposal caller: {ref}"
```

---

## 5. Adversarial findings

### 5.1 Confirm-route Bernie envelope may carry the session key in body but not header

The `BernieSession` class has `getServerRouteIdempotencyKey()` which generates per-turn session-scoped keys. The Bernie envelope's `confirm_payload` sometimes carries `server_session_idempotency_key` in the body, but `confirmBernieToolIntentChange()` calls `apiFetch(normalizeApiPath(envelope.confirm_endpoint), ...)` with no `Idempotency-Key` header. The backend does not read the key from the body for confirm routes — it reads it exclusively from the `Idempotency-Key` **header**. This means even though the Bernie session generates a valid key, it is never delivered to the backend correctly.

**Fix option for Sprint 155:** Either the confirm endpoint callers should extract the session key from the Bernie envelope and pass it as `headers["Idempotency-Key"]`, or `confirmBernieToolIntentChange()` should generate a `crypto.randomUUID()` key (like the modal does) for the confirm call.

### 5.2 The waiting-area proposal route is not in the unwired handlers tuple

`test_api_spine_create_proposal_header_alignment.py` defines `UNWIRED_PROPOSAL_HANDLERS = ("propose_update_appointment", "propose_status_update", "propose_delete_appointment")` but omits `propose_waiting_area_update`. This is a minor gap: the waiting-area handler is also unwired, and the OpenAPI spec may document it under the same `proposeAppointmentStatus` operation. The existing test asserts that "4 canonical OpenAPI proposal operations" reference the shared parameter — waiting-area may share `proposeAppointmentStatus` with status proposals — but the handler-level inventory should include it.

### 5.3 The `saveBooking` confirm callers reuse the proposal key pattern but don't pass headers

The `saveBooking` function's confirm path (both create and update) constructs `confirmPayload` from the proposal response and calls `apiFetch(normalizeApiPath(confirmEndpoint), {method: "POST", body: ...})`. This is exactly the same pattern as the create-proposal call — but without the `headers: {"Idempotency-Key": key}` addition. The `saveBtn.dataset.idempotencyKey` is still available at this point (it was set by the preceding proposal call and cleared only by `resetProposalConfirmation()`). Passing the same key to the confirm call would give correct same-operation retry semantics.

### 5.4 No structural drift detection for the frontend

The existing test suite has strong backend drift detection (OpenAPI YAML, FastAPI AST parsing) but no equivalent for `diary.js`. A new `apiFetch` call site that touches a confirm or proposal route could be added to the frontend without any test noticing. Sprint 154 should add the structural frontend inventory guard described in section 4a.

---

## Verdict

**Sprint 154 completes its preflight mandate.** The landscape is:

- **1 caller wired** (create-proposal ✓)
- **5 confirm callers broken** (backend requires header, frontend doesn't send it)
- **4 proposal-only callers unwired but not enforced** (known Sprint 152 gap)
- **0 structural drift detection for the frontend** (gap)
- **1 handler miss in unwired tuple** (`propose_waiting_area_update`)

**Sprint 155 recommendation:** Wire the create-confirm path (staff + Bernie) using the same modal-scoped key and pattern from Sprint 153. This is the highest-impact, lowest-risk fix — it addresses an actual runtime breakage rather than a speculative gap.

**Sprint 154 closeout tasks:**
1. Add `tests/test_api_spine_frontend_header_inventory.py` (structural frontend caller guard)
2. Add confirm-route caller cross-reference test
3. Add `propose_waiting_area_update` to the existing UNWIRED_PROPOSAL_HANDLERS tuple
4. Merge this review artifact as `orchestration/agent_inbox/codex/review-deepseek-sprint154-diary-api-header-gap-preflight.md`

## Files changed (this review only)

- orchestration/agent_inbox/codex/review-deepseek-sprint154-diary-api-header-gap-preflight.md (created)

## Verification run

- Static inspection of all 40+ apiFetch call sites in `docs/diary/diary.js`
- Static inspection of all 18+ `@router.post/put/patch/delete` routes in `app/routers/appointments.py`
- Cross-referenced OpenAPI YAML parameter contract
- Cross-referenced Sprint 147/151/152/153 decisions and guard tests
- Verified no runtime behavior change, no provider/route/DB/memory/RAG/H15 wiring touched

## Remaining risks

See section 5 findings. The primary risk is that Sprint 155 attempts to wire all 5 broken confirm callers at once instead of starting with the create-confirm path. Wire the create-confirm path first (same function, same lifecycle, same modal), extend the pattern to status-confirm and delete-confirm in Sprint 156+.
