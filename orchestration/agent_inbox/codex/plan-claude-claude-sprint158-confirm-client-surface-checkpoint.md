# Sprint 158 Review — Confirm Client Surface Checkpoint

| Item | Value |
|---|---|
| **Review type** | API-spine/idempotency checkpoint review |
| **Sprint** | 158 |
| **Target** | Confirm-client idempotency header posture after Sprints 153-157 |
| **Runtime behaviour changed** | No (review artifact only) |
| **Reviewer sprints** | 124 (idempotency gap), 153 (create-proposal client header), 154 (header gap preflight), 155 (create-confirm client header), 156 (status/delete confirm client header), 157 (update-confirm client header), 158 (this checkpoint) |

---

## 1. Current Wire Posture

Every ordinary Diary confirm caller now emits HTTP `Idempotency-Key` headers. The remaining tracked gap is `confirmBernieToolIntentChange`.

| Backend route | Diary caller(s) | Header status |
|---|---|---|
| `POST /proposals/create` | `saveBooking` create-proposal branch | Wired Sprint 153 |
| `POST /proposals/create/confirm` | `saveBooking` create-confirm branch | Wired Sprint 155 |
| `POST /proposals/create/confirm-bernie` | Bernie review confirm adapter | Wired Sprint 155 |
| `POST /proposals/update/confirm` | `saveBooking` update-confirm branch | Wired Sprint 157 |
| `POST /proposals/update/confirm` | Drag/resize confirm branch | Wired Sprint 157 |
| `POST /proposals/status-confirm` | `applySignedStatusProposal` | Wired Sprint 156 |
| `POST /proposals/delete-confirm` | `applySignedDeleteProposal` | Wired Sprint 156 |
| dynamic (`envelope.confirm_endpoint`) | `confirmBernieToolIntentChange` | Deferred — no header |

---

## 2. Three Candidate Next Slices — Assessment

### Slice A: Bernie tool-intent update confirm client header semantics

**What it is**: Wire `Idempotency-Key` emission for `confirmBernieToolIntentChange()` at `diary.js:1716-1753`.

**Key semantics challenge**: The tool-intent envelope flows through the Bernie backend session layer, which already carries `server_session_idempotency_key` in the body. But the confirmation routes read the HTTP `Idempotency-Key` header only; body-level fields do not satisfy them. The confirm endpoint is also dynamic (`envelope.confirm_endpoint`), so the key derivation must work across multiple possible route families.

**Risk**: Low — tool-intent confirm is a preview-only pilot surface, not wired to live providers or used outside Bernie session mode.

**Dependencies**: Bernie session discriminator semantics, understanding of how `confirm_endpoint` varies.

**Value**: Closes the last tracked confirm-client gap.

**Verdict**: Best handled in a Bernie-specific sprint after the session discriminator pattern and dynamic route routing are stable enough to commit to a key derivation strategy.

### Slice B: Proposal-only backend/header binding

**What it is**: Add `Header(None, alias="Idempotency-Key")` and `_normalize_idempotency_key()` to the four proposal-only FastAPI routes that are declared with `Idempotency-Key` in the OpenAPI spec but do not bind it at runtime.

| FastAPI handler | Current route | Header binding status |
|---|---|---|
| `propose_update_appointment` | `POST /proposals/update/{appointment_id}` | Not bound |
| `propose_status_update` | `POST /proposals/status/{appointment_id}` | Not bound |
| `propose_waiting_area_update` | `POST /proposals/waiting-area/{appointment_id}` | Not bound |
| `propose_delete_appointment` | `POST /proposals/delete/{appointment_id}` | Not bound |

**Key constraint**: These routes do not write appointments, so the idempotency key is a consistency and alignment concern rather than a safety concern. The preflight doc correctly records them as "must not inherit confirmation replay authority by accident."

**Risk**: Very low — no write authority means no replay risk. Adding header binding here is a defensive taxonomy marker, not a safety guard.

**Dependencies**: None — purely backend, purely additive.

**Value**: Moderate — aligns runtime with the OpenAPI contract (8 of 8 OpenAPI mutable-command routes now reference `IdempotencyKey`), but provides no safety benefit since proposal routes don't write.

**Slient gap**: The Diary frontend does not send headers on proposal calls either. The `saveBooking` proposal call at `POST /proposals/create` was wired in Sprint 153, but `propose_update_appointment` and the other three proposal-only callers in `diary.js` do not send headers. If backend binding were added without frontend emission, those routes would start rejecting ordinary Diary usage. This means Slice B is actually a two-sided change: backend binding + frontend emission for all four proposal callers.

**Verdict**: Feasible and low risk, but scope is wider than it appears because the Diary frontend must also emit on proposal calls. Best sequenced after `minLength: 8` enforcement.

### Slice C: Strict OpenAPI `minLength: 8` runtime enforcement

**What it is**: Add a length check to `_normalize_idempotency_key()` (and `_normalize_create_proposal_idempotency_key()`) that rejects keys shorter than 8 characters.

**Current posture**: The OpenAPI spec at `appointment-commands.yaml:406` declares `minLength: 8` and `maxLength: 128`. The backend `_normalize_idempotency_key()` only rejects blank/None; it accepts `"a"` as valid.

**Runtime impact**: All current Diary client keys safely exceed 8 characters:
- `crypto.randomUUID()` produces 36-character UUIDs
- Freshness-derived keys like `update-confirm-<uuid>` are ~50 characters
- The Math.random() fallback `evt-<8-char-random>` is ~12 characters
- Proposal-scoped fallback `confirm-<uuid>` is ~44 characters

No existing client would break.

**Risk**: Near zero for current clients. Adds defense-in-depth by catching misconfigured, truncated, or adversarial short keys before they reach the idempotency ledger.

**Dependencies**: None — purely backend, one function change plus a test assertion.

**Value**: High for the effort. Closes a declared OpenAPI contract gap, provides defense-in-depth with zero client risk.

**Verdict**: Safest next slice. A one-function change with parametrized test coverage.

---

## 3. Recommended Ordering

| Priority | Slice | Effort | Client risk | Safety value | Notes |
|---|---|---|---|---|---|
| **1** | **C: minLength: 8 enforcement** | ~1 function + tests | None (all keys exceed 8) | Real defense-in-depth | Closes OpenAPI contract gap |
| 2 | B: Proposal-only header binding | ~4 backend routes + 4 frontend callers | Low (non-mutating) | Taxonomy/alignment only | Actually two-sided (backend + frontend) |
| 3 | A: Bernie tool-intent confirm | ~1 frontend function | Low (pilot only) | Closes last gap | Best in Bernie-specific sprint |

---

## 4. Preflight Doc Check: Current Gaps Correctly Recorded

The preflight doc `api_spine_appointment_idempotency_diary_header_gap_preflight.md` correctly records:

- **Update-confirm**: Changed from "Missing" to "Wired (Sprint 157)"
- **`confirmBernieToolIntentChange`**: Listed under deferred surfaces
- **Proposal-only routes**: Listed as "deferred binding gap"
- **`minLength: 8` enforcement**: Listed as "deferred"
- **Raw compatibility paths**: Listed as "deferred" and "not changed"

---

## 5. Constraint Audit

This review does not touch:

- No provider calls or enablement
- No GraphQL mutations
- No memory/RAG/GraphRAG runtime wiring
- No H15/H-series runtime imports
- No historical diary material access
- No raw compatibility write changes
- No backend idempotency ledger changes
- No interpretation harness runtime wiring

---

## Summary

| Dimension | Verdict |
|---|---|
| Ordinary confirm surface | All 6 Diary confirm callers emit `Idempotency-Key` |
| Remaining tracked gap | `confirmBernieToolIntentChange` correctly deferred |
| OpenAPI/v1 proposal-binding gap | Recorded but two-sided; defer to after minLength |
| `minLength: 8` enforcement | OpenAPI declares it; runtime does not enforce |
| **Recommended next slice** | **Slice C: strict `minLength: 8` runtime enforcement** |

The compact confirm-client surface checkpoint shows a clean state:
- All ordinary Diary confirm flows are wired.
- The remaining gap (`confirmBernieToolIntentChange`) is correctly tracked as a Bernie-specific deferral.
- The most valuable next slice is the one with zero client risk and the highest defense-in-depth per line of code: backend `minLength: 8` enforcement.
- Proposal-only header binding should follow in a subsequent sprint, and the Diary frontend should emit headers on proposal calls at the same time.
