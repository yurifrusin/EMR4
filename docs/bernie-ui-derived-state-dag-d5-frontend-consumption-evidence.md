# Bernie UI Derived-State DAG D5 Frontend Consumption Evidence

Date: 2026-07-09

Status: route-intercepted frontend consumption verified.

Sprint 252 adds a focused browser-smoke case proving the existing Diary
JavaScript consumes the post-D5 backend response shape where the display-only UI
view model lives under `staff_review.ui_view_model`. This is
route-intercepted Playwright evidence only: it does not call the production backend, providers,
Access AI, memory/RAG/GraphRAG, GraphQL, H15/H-series inputs, historical diary
inputs, or external patient clients.

## Evidence

- Frontend consumer:
  `docs/diary/diary.js::attachBernieUiViewModelToStaffReview`
- Existing source expression:
  `data?.staff_review?.ui_view_model`
- Route-intercepted browser test:
  `review/test_diary_smoke.py::test_bernie_ui_view_model_consumes_backend_staff_review_field_without_js_expansion`
- Safe aggregate companion:
  `docs/bernie-ui-derived-state-dag-d5-frontend-consumption-evidence.json`

The intercepted response intentionally omits a top-level `ui_view_model` field
and places the view model under `staff_review.ui_view_model`. The staff-review
panel renders the model's copy and confirm affordance, then the signed confirm
payload is checked to exclude view-model fields.

## Boundary

No production JavaScript changed in this sprint. No backend route/schema/service
behavior changed beyond the already-approved Sprint 249 first slice. No confirm
payload field, appointment write behavior, provider prompt, live-provider call,
GraphQL resolver, memory/RAG/GraphRAG path, H15/H-series runtime input,
historical diary runtime input, external patient-client exposure, additional
route delivery, or model-to-database write gate is opened.
