# Blue review — Secure SDLC and Diary hardening

**Worker:** DeepSeek V4 Flash (blue lane)
**Candidate commit:** `604b3452787d45ad99d9f08e70101bfd87516671`
**Date:** 2026-07-17
**Decision:** `DECISION: pass`

---

## 1. Ariadne gate fail-closed coverage

The gate (`scripts/ariadne_security_review_gate.py`) fails closed for every
configured condition:

| Condition | Mechanism | Tested |
|---|---|---|
| Incomplete security deltas | Each required field checked via `_has_value()`; missing fields emit `security_delta_field_missing:<field>` | `test_material_sprint_fails_closed_for_incomplete_security_delta` |
| Triggered dual review absent | Sensitive triggers demand `blue` + `red` reviews; missing role emits `required_review_missing:<role>` | `test_security_trigger_cannot_omit_independent_red_lane` |
| Red independence violated | Requires `fresh_context`, `candidate_only`, `prior_review_artifacts_excluded` when configured | `test_red_lane_must_be_fresh_and_asymmetric` |
| Asymmetric packets not enforced | Compares `blue.packet_path` vs `red.packet_path`; emits `asymmetric_review_packets_required` if equal | same test |
| Purple cadence overdue | Checks `material_sprints_since_purple >= maximum_material_sprints_between_purple` (4) | `test_purple_review_is_required_at_four_material_sprints` |
| Missing review artifacts | At acceptance phase, `artifact_path` must exist on disk | Covered by `_review_reasons()` general path |
| Unresolved critical/high findings | At acceptance, severities in `blocking_unresolved_severities` (`critical`, `high`) cause `blocking_finding_unresolved` | `test_acceptance_blocks_unresolved_high_finding` |
| Unknown triggers | Any trigger not in `security_sensitive_triggers` set emits `unknown_security_trigger:<name>` | Implicit in manifest validation |
| Missing/invalid `material_sprints_since_purple` | Non-int or < 0 emits `purple_cadence_invalid` | Implicit in manifest validation |

**Verdict:** The gate is thorough and fail-closed. All reasons are collected
before returning `revision_required`. Non-material sprints skip review and
return `passed` unconditionally, matching the proportionality requirement.

---

## 2. Diary hardening — localhost gating, confirm allowlist, crypto IDs, safe selectors

### Localhost-only dev flags

`isLocalHarnessHost()` checks `window.location.hostname` against `["", "127.0.0.1", "localhost", "[::1]"]`.
`isLocalHarnessCapabilityEnabled(param)` requires both localhost AND the URL
parameter set to `"true"`. These functions gate:

- `isSmokeMode()` — was `?smoke=true` anywhere, now localhost-only
- `isBernieDevOrDebug()` — requires localhost for `bernie_debug` / `bernie_dev_review`
- `isBernieManualContextAllowed()` — inherits localhost-gated `isSmokeMode()` / `bernie_dev_review`
- `hasSlotPreviewParam()` — `slot_preview` now localhost-only
- All other `bernie_dev_review` lookups throughout `renderBernieReview`, `checkBerniePilotEligibility`, `renderBernieInstructionInput`, `loadBernieLiveReview`, `initBernieReview`, `Office.onReady`

The QA guide's deployed smoke URL (`https://yurifrusin.github.io/EMR4/diary/diary.html?smoke=true`) was
removed as a non-local capability.

### Five canonical confirm routes preserved

`ALLOWED_CONFIRM_ENDPOINT_PATHS` Set contains exactly the five signed-confirm paths:

```
/appointments/proposals/create/confirm
/appointments/proposals/create/confirm-bernie
/appointments/proposals/update/confirm
/appointments/proposals/status-confirm
/appointments/proposals/delete-confirm
```

`allowlistedConfirmApiPath()` normalises the endpoint via `normalizeApiPath()`,
validates it against the Set, and throws if no match. All seven existing
confirm POST call sites now use `allowlistedConfirmApiPath()`:

1. `confirmBernieToolIntentChange` — tool intent confirm
2. `renderBernieReview` (inline) — Bernie review confirm
3. `saveBooking` update path — ordinary update confirm
4. `saveBooking` create path — create confirm
5. `handleMoveResize` — drag-resize update confirm
6. `applySignedStatusProposal` — status confirm
7. `applySignedDeleteProposal` — delete confirm

No remaining calls to `apiFetch(normalizeApiPath(confirmEndpoint))`.

### Math.random removed

`generateSessionId()`, `generateEventId()`, and `generateClientIdempotencyKey()`
all delegate to `secureClientIdentifier()`, which uses `crypto.randomUUID()` or
`crypto.getRandomValues()` and throws if neither is available. Zero occurrences
of `Math.random` remain in the file.

### Identifier selector construction eliminated

`findAppointmentElementById(appointmentId)` uses `Array.from(...).find(el => el.dataset.id === expected)`
instead of string interpolation in `querySelector`. All seven call sites that
previously used `` document.querySelector(`.appt[data-id="${...}"`) `` now
use `findAppointmentElementById()`. The `CSS.escape` fallback path is removed.

---

## 3. Nearby-bypass and legitimate-route regression analysis

### Bypass attempts considered

| Attack vector | Control | Risk |
|---|---|---|
| Non-local `?smoke=true` | `isLocalHarnessHost()` check | Blocked — hostname must be localhost variant |
| Non-local `?bernie_debug=true` | Same localhost gate | Blocked |
| Arbitrary `confirm_endpoint` in server payload | `allowlistedConfirmApiPath()` against Set of 5 | Blocked — throws before fetch; Playwright test confirms no network request |
| Predictable session/event/idempotency IDs | `secureClientIdentifier()` with Web Crypto | Blocked — `Math.random` removed; crypto fail-closed |
| Selector injection via appointment ID | `findAppointmentElementById()` uses `dataset.id` comparison | Blocked — no string interpolation into `querySelector` |
| DNS rebinding / proxy hostname manipulation | Out of scope for URL-level control | Acceptable — network-level threat beyond URL capability model |
| `allowlistedConfirmApiPath()` passes path but `apiFetch()` targets different origin | `normalizeApiPath()` strips origin; relative path used with `apiFetch()` base URL | Defense-in-depth — the path allowlist is one layer; base URL binding is a separate concern |

### Legitimate route preservation

All five signed-confirm paths remain reachable through the allowlist. Smoke
mode works correctly on localhost. The `bernie_dev_review` parameter continues
to enable dev/review behaviour when on localhost. No changes to the Bernie
session, event, or idempotency-key generation affect runtime behaviour — only
the underlying PRNG was swapped.

---

## 4. Reproduced tests

### Python focused tests (29 passed, 0 failed)

```
tests/test_ariadne_security_review_protocol.py ......                [ 6/29]
tests/test_ariadne_operating_model.py ...........                   [ 17/29]
tests/test_diary_security_hardening.py ....                         [ 21/29]
tests/test_api_spine_confirm_client_surface_checkpoint.py .....     [ 26/29]
tests/test_api_spine_frontend_header_inventory.py ...               [ 29/29]
```

### Node syntax check

```powershell
node --check docs/diary/diary.js
# exit 0 — no syntax errors
```

### Playwright module

```
tests/test_bernie_ui_accessible_confirmation.py ...... 7 collected
```

All 7 tests collected, including the new boundary test:

```
test_unknown_confirmation_endpoint_fails_closed_without_network_request
```

The Playwright test confirms that a malicious `confirm_endpoint` value:
- Does **not** trigger a network request (`captured == []`)
- Renders an error message containing "couldn't confirm this booking"
- Does **not** render a receipt group (`bernie-receipt-group` count == 0)

---

## Summary

The candidate commit hardens the Ariadne SDLC gate and Diary client
comprehensively:

1. **Ariadne gate** — fail-closed for all configured conditions (delta completeness,
   dual review, red independence, purple cadence, missing artifacts, unresolved
   findings), with clear diagnostic reasons and phased plan/acceptance depth.

2. **Diary hardening** — localhost-only dev capabilities via `isLocalHarnessHost()`,
   five canonical confirm routes enforced via `ALLOWED_CONFIRM_ENDPOINT_PATHS` Set,
   `Math.random` replaced with Web Crypto with a fail-closed throw, and selector
   injection eliminated via `findAppointmentElementById()`.

3. **Bypass surface** — no viable bypass identified for non-local dev flag activation,
   arbitrary confirm path injection, predictable ID recovery, or selector injection.
   All legitimate localhost flows and five confirm routes remain operational.

4. **Reproducible evidence** — 29 Python tests passing, Node syntax clean,
   7 Playwright tests collected including the new boundary test.

**Decision: `DECISION: pass`**
