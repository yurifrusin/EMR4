# Raw Compatibility Consumer Signal Readiness

Date: 2026-07-08

Sprint: 206

## Purpose

This preflight follows the legacy compatibility write deprecation map and asks a
narrow question: are current consumers and signals ready for a future
`appointment_raw_compat_mode` move from `audit` to `header`?

Current answer: no mode change yet. The backend can emit `Deprecation` headers,
but the Diary frontend does not consume or surface that signal. The safe default
therefore remains `audit` until a later sprint wires deliberate frontend
deprecation awareness and verifies it.

## Consumer Signal Inventory

| Compatibility write | Handler | Raw compatibility tag | Backend signal site | Frontend consumer | Frontend raw call sites | Frontend condition | Header consumed | Readiness posture |
|---|---|---|---|---|---|---|---|---|
| `POST /api/v1/appointments` | `create_appointment` | `raw_compat_create` | `_raw_compat_evidence_and_headers("raw_compat_create")` | `docs/diary/diary.js` | `create_modal_raw_post` | create fallback when `confirmEndpoint` or `confirmPayload` is absent | `no` | `not_ready_for_header_mode` |
| `PUT /api/v1/appointments/{appointment_id}` | `update_appointment` | `raw_compat_update` | `_raw_compat_evidence_and_headers("raw_compat_update")` | `docs/diary/diary.js` | `edit_modal_raw_put`; `drag_resize_raw_put` | edit-modal or drag/resize fallback when `confirmEndpoint` or `confirmPayload` is absent | `no` | `not_ready_for_header_mode` |
| `PATCH /api/v1/appointments/{appointment_id}/status` | `update_appointment_status` | `raw_compat_status` | `_raw_compat_evidence_and_headers("raw_compat_status")` | `docs/diary/diary.js` | `edit_modal_raw_status_patch`; `create_modal_raw_status_patch`; `status_proposal_raw_patch` | status side-write after edit/create or fallback when signed status confirmation is unavailable | `no` | `not_ready_for_header_mode` |
| `DELETE /api/v1/appointments/{appointment_id}` | `cancel_appointment` | `raw_compat_delete` | `_raw_compat_evidence_and_headers("raw_compat_delete")` | `docs/diary/diary.js` | `delete_modal_raw_delete` | delete fallback when `confirmEndpoint` or `confirmPayload` is absent | `no` | `not_ready_for_header_mode` |

## Signal Baseline

- Backend setting remains
  `appointment_raw_compat_mode: Literal["audit", "header", "off"] = "audit"`.
- Backend helper remains `_raw_compat_evidence_and_headers()`.
- `audit` mode attaches `raw_compat_*` evidence only.
- `header` mode attaches `raw_compat_*` evidence and a `Deprecation` response
  header.
- `off` mode suppresses both raw compatibility evidence and deprecation
  headers and is not a migration target.
- `tests/test_appointment_raw_compat.py` already verifies backend response
  behavior for `audit`, `header`, and `off`.

## Consumer Baseline

- `docs/diary/diary.js` uses the shared `apiFetch()` helper and browser
  `fetch()`, so extra response headers should be tolerated by ordinary response
  handling.
- `docs/diary/diary.js` has no `Deprecation` or `deprecation` header consumer.
- No committed frontend JavaScript/HTML surface currently reads or displays a
  `Deprecation` response header.
- route-intercepted smoke tests in `review/test_diary_smoke.py` do not prove
  live backend header consumption.

## Header Mode Readiness Decision

The current decision is `keep_audit_mode`.

Do not change `appointment_raw_compat_mode` to `header` until a later sprint
adds and verifies at least one deliberate consumer of the `Deprecation` header,
preferably inside `apiFetch()` or an equivalent shared request boundary.

Do not change `appointment_raw_compat_mode` to `off` while any raw compatibility
write remains available to product clients or system compatibility paths.

## Future Preconditions For Header Mode

Before `header` mode can become a reviewed default, prove all of the following:

- every raw compatibility write still uses `_raw_compat_evidence_and_headers()`;
- every known frontend raw call site is inventoried with its fallback condition;
- frontend code deliberately observes or logs the `Deprecation` response header;
- route-intercepted tests that mock raw compatibility writes include a header
  tolerance check or explicitly remain outside header-readiness evidence;
- replacement proposal/confirm paths remain the preferred product flow;
- the raw compatibility deprecation map and this readiness preflight agree on
  the four compatibility write families.

## Closed Gates

This preflight does not authorize:

- changing `appointment_raw_compat_mode`;
- removing, renaming, blocking, or changing compatibility write routes;
- raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement;
- proposal-only route idempotency expansion;
- provider prompt wiring or live provider calls;
- provider dry-run wiring;
- memory/RAG/GraphRAG runtime wiring;
- H15/H-series runtime imports;
- historical diary material access;
- broad historical diary trove mining;
- external patient clients;
- runtime FGA clients;
- GraphQL mutations;
- direct database writes by model output;
- model-to-database writes outside REST command handlers.

## Boundary

This is a declaration-continuity artifact. It does not prove runtime client
behavior in a browser, production observability, route-removal safety, external
client readiness, provider readiness, or deployment readiness.

`tests/test_api_spine_raw_compat_consumer_signal_readiness.py` validates this
preflight by parsing only this markdown file, `app/config.py`,
`app/routers/appointments.py`, `docs/diary/diary.js`, selected committed
frontend files, `tests/test_appointment_raw_compat.py`, and the existing
legacy compatibility write deprecation map test.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_consumer_signal_readiness.py -q
```
