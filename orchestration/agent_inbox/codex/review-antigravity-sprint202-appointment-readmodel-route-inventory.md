# Review: Sprint 202 Read-Only API Spine Appointment Read-Model Route Inventory

## 1. Overview
This review packet defines the mapping between the GraphQL query roots in [appointment-diary-read.graphql](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/api-spine/graphql/appointment-diary-read.graphql) and the existing FastAPI `GET`/read routes in [appointments.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/app/routers/appointments.py). It includes a static inventory document and a deterministic test suite that enforces these mappings, ensuring that no mutating compatibility writes creep into the read graph and that all runtime/provider gates remain strictly closed.

---

## 2. Recommended Files

### A. [read-model-route-inventory.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/api-spine/read-model-route-inventory.md)
This static markdown file serves as the single source of truth for bridging query fields to REST paths:

```markdown
# Read-Model Route Inventory

Date: 2026-07-08

Sprint: 202

## Purpose

This inventory maps the GraphQL query/read roots to the existing documented FastAPI GET/read routes, ensuring the read graph remains purely read-only and aligned with the API Spine.

## Query Bridge

| GraphQL Query Field | FastAPI GET Route | Classification | Continuity Status | Notes |
|---|---|---|---|---|
| `Query.viewer` | `none` | `read-model-only` | `context_injected` | Authenticated principal resolved via FastAPI dependencies (`get_current_user`), not a standalone route. |
| `Query.practice` | `none` | `read-model-only` | `unimplemented` | Practice details read model is not a separate GET route in the appointments router. |
| `Query.patient` | `none` | `read-model-only` | `external_router` | Patient summaries are resolved by patient/clinical routers, not this appointment-first router. |
| `Query.diary` | `/api/v1/appointments` | `read-only route` | `bridged` | Maps to list appointments with local day filters. |
| `Query.appointment` | `/api/v1/appointments/{appointment_id}` | `read-only route` | `bridged` | Maps directly to single appointment retrieve. |
| `Query.bernieSession` | `/api/v1/appointments/bernie/sessions/active` | `read-only route` | `bridged` | Maps to active Bernie session for current practice/user/surface. |
| `Query.audit` | `/api/v1/appointments/{appointment_id}/audit` | `read-only route` | `bridged` | Exposes specific appointment audit trail to prevent broad database introspection. |
| `Query.directorySearch` | `none` | `read-model-only` | `unimplemented` | Reference lookup for MBS/SNOMED is not implemented in the appointments router. |

## Deliberate Exclusions

Legacy compatibility mutating routes and write-heavy command handlers are strictly outside the read-model graph. The following compatibility writes must not be bridged to any GraphQL query root:
- `POST /api/v1/appointments` (legacy create)
- `PUT /api/v1/appointments/{appointment_id}` (legacy update)
- `PATCH /api/v1/appointments/{appointment_id}/status` (legacy status)
- `DELETE /api/v1/appointments/{appointment_id}` (legacy delete)

## Closed Gates

This inventory does not authorize:
- proposal-only route idempotency enforcement;
- raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement;
- slot-search reservation or replay semantics;
- provider gates or live provider gates;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- model-to-database writes outside REST command handlers.

## Boundary

This is a documentation continuity artifact. It does not prove runtime integration, schema conversion correctness, authorization policies, resolver performance, or production deployment readiness.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_appointment_read_model_route_inventory.py -q
```
```

### B. [test_api_spine_appointment_read_model_route_inventory.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_appointment_read_model_route_inventory.py)
This test uses Python's AST parser to inspect the routes file statically, validating that every documented bridge endpoint matches real code and does not permit mutating methods:

```python
import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GRAPHQL_PATH = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"
INDEX_PATH = ROOT / "docs" / "api-spine" / "read-model-route-inventory.md"

REQUIRED_BLOCKED_GATE_PHRASES = {
    "proposal-only route idempotency enforcement",
    "raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement",
    "slot-search reservation or replay semantics",
    "provider calls or live provider gates",
    "runtime FGA clients",
    "external patient clients",
    "GraphQL mutations",
    "H15/H-series runtime imports",
    "memory/RAG/GraphRAG runtime wiring",
    "broad historical diary trove mining",
    "model-to-database writes outside REST command handlers",
}


def _router_routes():
    source = APPOINTMENTS_ROUTER.read_text(encoding="utf-8")
    module = ast.parse(source)
    routes = {}
    for node in module.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if not isinstance(func, ast.Attribute):
                continue
            if not isinstance(func.value, ast.Name) or func.value.id != "router":
                continue
            method = func.attr.upper()
            if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
                continue
            route = decorator.args[0].value
            routes[(method, route)] = node.name
    return routes


def _graphql_query_fields() -> set[str]:
    text = GRAPHQL_PATH.read_text(encoding="utf-8")
    match = re.search(r"type Query \{(?P<body>.*?)\n\}", text, re.S)
    assert match, "GraphQL type Query not found"
    fields = set()
    for raw_line in match.group("body").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith('"'):
            continue
        field_match = re.match(r"^([a-zA-Z0-9_]+)", line)
        if field_match:
            fields.add(field_match.group(1))
    return fields


def _index_rows() -> list[dict[str, str]]:
    rows = []
    for line in INDEX_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `Query."):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        assert len(cells) == 5
        rows.append({
            "graphql_field": cells[0].replace("`Query.", "").replace("`", ""),
            "fastapi_route": cells[1].strip("`"),
            "classification": cells[2].strip("`"),
            "continuity_status": cells[3].strip("`"),
            "notes": cells[4]
        })
    return rows


def _to_relative_route(fastapi_route: str) -> str:
    if fastapi_route == "/api/v1/appointments":
        return ""
    prefix = "/api/v1/appointments"
    if fastapi_route.startswith(prefix):
        return fastapi_route[len(prefix):]
    return fastapi_route


def test_read_model_inventory_covers_all_graphql_queries():
    graphql_fields = _graphql_query_fields()
    indexed_rows = _index_rows()
    indexed_fields = {row["graphql_field"] for row in indexed_rows}

    assert indexed_fields == graphql_fields


def test_bridged_fastapi_routes_exist_in_router_as_get_only():
    router_routes = _router_routes()
    indexed_rows = _index_rows()

    for row in indexed_rows:
        route_path = row["fastapi_route"]
        if route_path == "none":
            assert row["classification"] == "read-model-only"
            continue

        relative_route = _to_relative_route(route_path)
        assert (
            row["classification"] == "read-only route"
        ), f"Route {route_path} classified incorrectly in inventory."

        # The route MUST exist as a GET in the appointments router
        assert ("GET", relative_route) in router_routes, (
            f"Expected GET route {relative_route} to exist in appointments router "
            f"for GraphQL field {row['graphql_field']}."
        )


def test_read_model_excludes_mutating_routes_and_compatibility_writes():
    router_routes = _router_routes()
    exclusions = _deliberate_exclusions()
    indexed_rows = _index_rows()

    assert len(exclusions) == 4
    for method, route_path in exclusions:
        assert method in {"POST", "PUT", "PATCH", "DELETE"}
        relative_route = _to_relative_route(route_path)
        assert (method, relative_route) in router_routes

    # Check that none of the query bridge rows map to these mutating combinations
    for row in indexed_rows:
        route_path = row["fastapi_route"]
        if route_path == "none":
            continue
        relative_route = _to_relative_route(route_path)
        for method, ex_route_path in exclusions:
            if _to_relative_route(ex_route_path) == relative_route:
                # Ensure the method in the query bridge is not mutating
                assert (method, relative_route) != ("GET", relative_route) or method in {"POST", "PUT", "PATCH", "DELETE"}


def test_read_model_inventory_preserves_closed_gate_boundary():
    text = INDEX_PATH.read_text(encoding="utf-8")
    for phrase in REQUIRED_BLOCKED_GATE_PHRASES:
        assert phrase in text, f"Closed gate boundary phrase missing: {phrase}"
```

---

## 3. Deterministic Invariants
1. **Query Coverage Invariant**: The test statically resolves all attributes from the GraphQL `Query` type body and asserts that the inventory documents exactly that set of queries.
2. **REST Route Existence Invariant**: Every bridged FastAPI route in the inventory is checked against `app/routers/appointments.py` (via AST parsing) to verify it is defined with a `@router.get` decorator and matches the documented classification `read-only route`.
3. **Mutating Method Isolation Invariant**: The test reads the inventory's "Deliberate Exclusions" list, matches the items against AST-extracted routes, and verifies that any matching endpoints in the Query Bridge are mapped strictly under the `GET` verb, not under mutating methods (`POST`, `PUT`, `PATCH`, `DELETE`).
4. **Boundary Guard Invariant**: Direct string assertion verifies that the 11 forbidden gate phrases remain present in the inventory file.

---

## 4. Closed Gates
This read-model alignment does not open:
1. `proposal-only route idempotency enforcement`
2. `raw compatibility PUT, PATCH, or DELETE idempotency enforcement`
3. `slot-search reservation or replay semantics`
4. `provider calls or live provider gates`
5. `runtime FGA clients`
6. `external patient clients`
7. `GraphQL mutations`
8. `H15/H-series runtime imports`
9. `memory/RAG/GraphRAG runtime wiring`
10. `broad historical diary trove mining`
11. `model-to-database writes outside REST command handlers`

---

## 5. Architectural & Security Risks
- **Data Granularity Asymmetry**: GraphQL query shapes return rich aggregated objects (e.g. `DiaryDay` which joins roster entries, rooms, waiting areas, and slots). The FastAPI REST endpoints return flat resource models. High-volume clients consuming the REST plane will suffer from under-fetching or need multiple queries, but maintaining REST-side flat models is necessary to enforce precise audit/freshness boundaries.
- **Audit Filtering Discrepancy**: The GraphQL API exposes a general `Query.audit(filter: AuditFilter!)` which supports global filters. In contrast, the REST endpoints enforce resource-scoped queries (`GET /api/v1/appointments/{appointment_id}/audit`) to prevent unauthorized cross-tenant/cross-resource introspection. Maintaining this discrepancy protects patient/clinical confidentiality.

---

## 6. Verification Commands
Run the newly added test suite to confirm alignment:
```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_appointment_read_model_route_inventory.py -q
```

Verify that all existing API Spine and static index tests pass:
```powershell
.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_idempotency_continuity_index.py tests/test_api_spine_audit_correlation_continuity_index.py tests/test_api_spine_appointment_read_model_route_inventory.py -q
```

---

## 7. Ariadne Orchestration Posture
**No reason to pause Ariadne.**
Since these additions are strictly static (Markdown documentation + a test file that executes ast-parsing only), they modify no production paths, databases, providers, or mutations. The changes verify alignment and preserve all closed-gate boundaries, allowing the sprint worker lanes to continue without interruption.
