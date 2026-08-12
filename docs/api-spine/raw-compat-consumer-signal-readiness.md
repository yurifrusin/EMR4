# Raw Compatibility Consumer Signal Readiness

Date: 2026-07-08

Sprint: 211

## Purpose

This preflight follows the legacy compatibility write deprecation map and asks a
narrow question: are current consumers and signals ready for a future
`appointment_raw_compat_mode` move from `audit` to `header`?

Current answer: no mode change yet. The backend can emit `Deprecation` headers,
Sprint 207 added a shared Diary frontend console warning consumer for that
signal, Sprint 208 exposes the `Deprecation` response header through FastAPI
CORS and verifies a raw compatibility header-mode response also carries
`Access-Control-Expose-Headers: Deprecation`, and Sprint 209 adds a Playwright
browser execution proof that `apiFetch()` warns only when an exposed
`Deprecation` header is present. The safe default remains `audit` until a later
reviewed sprint decides whether any environment should emit the header by
default. Sprint 210 records that rollout decision surface in
`docs/api-spine/raw-compat-header-rollout-gate.json`, with decision `blocked`
and no environment allowed to default to `header`. Sprint 211 adds
`scripts/raw_compat_header_rollout_gate_check.py`, a safe aggregate checker that
reports the gate remains blocked without emitting route, payload, patient, or
consumer details.

The 2026-08-12 provider-free native-client parity descendant removes all seven
raw appointment mutation call sites from `docs/diary/diary.js`. The four
backend compatibility routes remain mounted for unidentified external,
recovery or migration consumers, so this result does not authorize a signal-
mode change or route retirement.

## Consumer Signal Inventory

| Compatibility write | Handler | Raw compatibility tag | Backend signal site | Frontend consumer | Frontend raw call sites | Frontend condition | Header consumed | Readiness posture |
|---|---|---|---|---|---|---|---|---|
| `POST /api/v1/appointments` | `create_appointment` | `raw_compat_create` | `_raw_compat_evidence_and_headers("raw_compat_create")` | `docs/diary/diary.js` | none | native create uses proposal plus signed confirm; missing evidence fails closed | `console_warn_proven` | `native_client_parity_proven_compat_route_mounted_keep_audit_mode` |
| `PUT /api/v1/appointments/{appointment_id}` | `update_appointment` | `raw_compat_update` | `_raw_compat_evidence_and_headers("raw_compat_update")` | `docs/diary/diary.js` | none | native edit and drag/resize use proposal plus signed confirm; missing evidence fails closed | `console_warn_proven` | `native_client_parity_proven_compat_route_mounted_keep_audit_mode` |
| `PATCH /api/v1/appointments/{appointment_id}/status` | `update_appointment_status` | `raw_compat_status` | `_raw_compat_evidence_and_headers("raw_compat_status")` | `docs/diary/diary.js` | none | native status, waiting-area and post-create/update status use proposal plus signed confirm | `console_warn_proven` | `native_client_parity_proven_compat_route_mounted_keep_audit_mode` |
| `DELETE /api/v1/appointments/{appointment_id}` | `cancel_appointment` | `raw_compat_delete` | `_raw_compat_evidence_and_headers("raw_compat_delete")` | `docs/diary/diary.js` | none | native delete uses delete or bounded status proposal plus signed confirm; missing evidence fails closed | `console_warn_proven` | `native_client_parity_proven_compat_route_mounted_keep_audit_mode` |

## Signal Baseline

- Backend setting remains
  `appointment_raw_compat_mode: Literal["audit", "header", "off"] = "audit"`.
- Backend helper remains `_raw_compat_evidence_and_headers()`.
- `audit` mode attaches `raw_compat_*` evidence only.
- `header` mode attaches `raw_compat_*` evidence and a `Deprecation` response
  header.
- `off` mode suppresses both raw compatibility evidence and deprecation
  headers and is not a migration target.
- FastAPI CORS now declares `expose_headers=["Deprecation"]`, so a cross-origin
  browser client can read the response header once a reviewed environment emits
  it.
- `tests/test_appointment_raw_compat.py` already verifies backend response
  behavior for `audit`, `header`, and `off`, including a header-mode raw
  compatibility response with both `Deprecation` and
  `Access-Control-Expose-Headers`.

## Consumer Baseline

- `docs/diary/diary.js` contains zero raw appointment mutation calls. It still
  uses shared `apiFetch()` for proposal/confirm and read requests.
- `docs/diary/diary.js` now reads the `Deprecation` response header inside the
  shared `apiFetch()` helper after the 401 branch and writes a developer-facing
  `console.warn()` when the header is present.
- `review/test_diary_deprecation_consumer.py` proves that browser-executed
  `apiFetch()` emits the warning for a routed response with `Deprecation` and
  `Access-Control-Expose-Headers: Deprecation`, and does not warn when the
  response has no `Deprecation` header.
- No committed frontend JavaScript/HTML surface currently displays a
  user-facing `Deprecation` response header message.
- Existing route-intercepted smoke tests in `review/test_diary_smoke.py` remain
  outside live backend header consumption evidence.

## Header Mode Readiness Decision

The current decision is `keep_audit_mode`.

Do not change `appointment_raw_compat_mode` to `header` until a later reviewed
sprint decides the operational purpose, rollout surface, and observability for
emitting that signal by default. The current authoritative rollout gate is
`docs/api-spine/raw-compat-header-rollout-gate.json`, and its current decision
is `blocked`.

Do not change `appointment_raw_compat_mode` to `off` while any raw compatibility
write remains available to unidentified external or system compatibility paths.

## Future Preconditions For Header Mode

Before `header` mode can become a reviewed default, prove all of the following:

- every raw compatibility write still uses `_raw_compat_evidence_and_headers()`;
- every known frontend raw call site is inventoried, including an explicit zero
  count after native-client parity;
- frontend code deliberately observes or logs the `Deprecation` response header;
- FastAPI CORS exposes the `Deprecation` response header to cross-origin
  browser JavaScript;
- a frontend execution check proves the shared `apiFetch()` consumer can read a
  raw compatibility response header after browser CORS filtering;
- route-intercepted tests that mock raw compatibility writes include a header
  tolerance check or explicitly remain outside header-readiness evidence;
- the raw compatibility header rollout gate records a reviewed non-blocked
  decision, a specific staged environment rollout plan, and observability/rollback
  evidence;
- replacement proposal/confirm paths remain the preferred product flow;
- the raw compatibility deprecation map and this readiness preflight agree on
  the four compatibility write families.

## Closed Gates

This preflight does not authorize:

- changing `appointment_raw_compat_mode`;
- removing, renaming, blocking, or changing compatibility write routes;
- raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement;
- backend proposal-only route idempotency expansion beyond the accepted
  syntactic bindings;
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

This is a declaration-continuity artifact plus bounded route-intercepted
browser execution proof. It proves native-client parity only and does not prove
external-consumer readiness, production observability,
route-removal safety, external client readiness, provider readiness, deployment
readiness, or that any environment should switch `appointment_raw_compat_mode`
away from `audit`.

`tests/test_api_spine_raw_compat_consumer_signal_readiness.py` validates this
preflight by parsing only this markdown file, `app/config.py`,
`app/routers/appointments.py`, `docs/diary/diary.js`, selected committed
frontend files, `tests/test_appointment_raw_compat.py`,
`review/test_diary_deprecation_consumer.py`, and the existing legacy
compatibility write deprecation map test. The separate
`tests/test_api_spine_raw_compat_header_rollout_gate.py` validates the blocked
rollout gate, and `tests/test_raw_compat_header_rollout_gate_check.py`
validates the safe aggregate checker.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_consumer_signal_readiness.py -q
.venv\Scripts\python.exe -m pytest review\test_diary_deprecation_consumer.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_header_rollout_gate.py -q
.venv\Scripts\python.exe scripts\raw_compat_header_rollout_gate_check.py
```
