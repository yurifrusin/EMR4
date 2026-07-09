# Practitioner Directory Internal Runtime Consumer Approval

Sprint 263 records the approval boundary for the first runtime consumer of
`GET /api/v1/practice/practitioners`.

This does not wire the consumer. It authorizes Sprint 264 to wire exactly one
internal staff consumer: the Office add-in Command Center SPA Diary booking
practitioner selector/list in `docs/diary/diary.js` and `docs/diary/diary.html`.

This approval governs route-data consumption only. It does not change the
Sprint 261 readiness-status consumer boundary or the Sprint 262 static release
check: those artifacts remain static-only and must continue to report no runtime
consumers for readiness-status data.

## Approved Consumer

| Item | Value |
|---|---|
| Consumer ID | `office_addin_diary_booking_practitioner_selector` |
| Surface | Office add-in Command Center SPA Diary booking practitioner selector/list |
| Consumption mode | `http_through_existing_route` |
| Route | `GET /api/v1/practice/practitioners` |
| Default query | `activeOnly=true` |
| Scope | authenticated internal staff only |

The consumer must use the existing route and staff bearer-token flow. It must
not introduce a new route, a direct database/service bypass, a client-supplied
practice scope, or a default `activeOnly=false` request.

The consumer must render only inside the authenticated Diary booking dialog or
Office add-in taskpane flow. It must not create public-origin, external patient
client, kiosk, ngrok-header, or anonymous bypass behavior. It must not cache or
persist the practitioner list outside the active Diary session.

## Fields

The consumer may use only the display-safe route projection needed for the
selector: `id`, `display_name`, and `default_location_id`.

The consumer must not request, store, or display provider number, prescriber
number, AHPRA number, HPI-I, email, phone, or address fields. If later Diary
column mapping needs AHPRA-compatible behavior, it requires a separate reviewed
design rather than widening this approval.

## Closed Gates

This approval does not authorize:

- GraphQL SDL or resolver implementation;
- external read-model runtime readiness beyond the named consumer;
- provider, Access AI, memory, RAG, or GraphRAG use;
- H15, H-series, historical diary, or local_data runtime access;
- practitioner create, update, delete, or write authority;
- external patient-client, kiosk, anonymous, deployment, or production exposure.

Sprint 264 may wire only the named consumer. Sprint 265 must collect runtime
evidence before any GraphQL work begins. GraphQL is the likely next track only
if this REST route proves itself with focused auth, tenancy, no-write,
no-provider, and no-sensitive-field evidence.
