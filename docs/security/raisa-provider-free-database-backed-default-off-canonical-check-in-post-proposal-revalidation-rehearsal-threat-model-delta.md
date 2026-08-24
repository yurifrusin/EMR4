# Threat-model delta: check-in post-proposal revalidation rehearsal

Date: 2026-08-24

Timestamp: 2026-08-24T17:48:07.2584918+10:00 (Australia/Brisbane)

Status: `frozen_two_scenario_delta`

## Changed surface

Two authored-synthetic repository tests only. Product route, adapter, schema,
configuration and client code remain unchanged unless the tests expose one
bounded defect and a separately frozen correction remains necessary.

## Threats and controls

| Threat | Control |
|---|---|
| A proposal-issued token preserves authority after the actor loses the Receptionist role | Persist the new role before confirmation and require the current HTTP authorization boundary to deny with zero command rows. |
| A proposal-issued token preserves a now-invalid waiting-area assignment | Deactivate the area before confirmation and require current database truth to produce `waiting_area_not_active` after evidence verification. |
| Denial leaves partial appointment, audit, event or command effects | Read back the appointment and exact row counts after each request. |
| Test-only feature enablement is mistaken for a default change | Retain exact source/config bytes and scope enablement to the existing authored-synthetic fixture monkeypatch. |
| A current-state denial changes the public API | Assert the existing HTTP status and typed block code; forbid schema/OpenAPI edits. |
| Shared test database execution races with another pytest process | Run all `tests/conftest.py`-loading profiles serially under the repository lock. |
| Synthetic rehearsal is promoted into ordinary-practice evidence | Preserve the non-admission product-assurance label and unchanged 11/0/1 external-fact boundary. |

## Residual risk

The rehearsal proves only two local authored-synthetic transitions through the
repository's HTTP/database test boundary. It does not prove external process
restart, production concurrency, real practice configuration, live secret
custody, operational freshness or ordinary-practice admission.

## Closed authority

No historical/trove data, external provider/network, real practice or product
data, ordinary activation, client change, production, deployment, release,
Pages or protected-ref movement is authorised.
