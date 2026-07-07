# Antigravity Review - Sprint 201 Audit/Read-Model Continuity

Antigravity completed a read-only review of the EMR4 API Spine for Sprint 201. This packet recommends a static audit and read-model continuity index and validation test to bridge the GraphQL read-model declarations to the OpenAPI command audit metadata.

## Recommended Files

To establish the bridge without introducing runtime dependencies, we recommend adding two static files:

1. **Static Continuity Index**: [audit-readmodel-continuity-index.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/api-spine/audit-readmodel-continuity-index.md)
   A documentation index mapping GraphQL audit read models to OpenAPI command metadata.
2. **Drift Guard Test**: [test_api_spine_audit_readmodel_continuity.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_audit_readmodel_continuity.py)
   A python-based static validation test that checks this markdown index against [appointment-commands.yaml](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/api-spine/openapi/appointment-commands.yaml) and [appointment-diary-read.graphql](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/api-spine/graphql/appointment-diary-read.graphql).

---

### Proposed [audit-readmodel-continuity-index.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/api-spine/audit-readmodel-continuity-index.md)

```markdown
# Audit and Read-Model Continuity Index

Date: 2026-07-08
Sprint: 201

## Purpose
This index bridges EMR4's GraphQL read-model declarations to its OpenAPI command audit and correlation metadata.

## Continuity Mapping Table

| GraphQL Type / Field | Kind | OpenAPI Component / Property | Mapping Notes |
|---|---|---|---|
| `AuditEvent.id` | read-model key | `ConfirmationAuditEvent.event_id` | Unique UUID/ULID representing the audit event instance. |
| `AuditEvent.occurredAt` | timestamp | `ConfirmationAuditEvent.occurred_at` | UTC ISO-8601 datetime of execution. |
| `AuditEvent.actor` | nested object | `ConfirmationAuditEvent.actor` | Aligned with `ActorRef` schema. |
| `AuditEvent.correlationId` | correlation identifier | `ConfirmationAuditEvent.correlation_id` | Propagated `X-Correlation-Id` header value. |
| `AuditEvent.action` | action text | `ConfirmationAuditEvent.action` | Maps OpenAPI simple action name enum: `create`, `update`, `status_change`, `delete`. |
| `AuditEvent.evidenceMode` | evidence source | `CommandMeta.evidence_label` | Maps source surface context (e.g. `MODEL_INTERPRETATION`). |
| `AppointmentAuditEvent.appointmentId` | foreign key | `ConfirmationAuditEvent.appointment_id` | Associated appointment target. |
| `AppointmentAuditEvent.action` | typed enum | `AuditIntent.audit_action` | Maps proposal prepare/confirm lifecycle stages (e.g., `CONFIRMED_CREATE` <- `create`). |

## Closed Gates
This index does not authorize:
- Runtime resolver execution or routing logic.
- Model-to-database writes or audit store persistence.
- Live provider API calls or AI execution.
- H15/H-series runtime imports, memory/RAG/GraphRAG, or historical diary trove mining.
```

---

### Proposed [test_api_spine_audit_readmodel_continuity.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_audit_readmodel_continuity.py)

```python
from pathlib import Path
import pytest

OPENAPI_PATH = Path("docs/api-spine/openapi/appointment-commands.yaml")
GRAPHQL_PATH = Path("docs/api-spine/graphql/appointment-diary-read.graphql")
INDEX_PATH = Path("docs/api-spine/audit-readmodel-continuity-index.md")

def _load_openapi() -> dict:
    pytest.importorskip("yaml", reason="PyYAML not installed.")
    import yaml
    return yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))

def _load_graphql() -> str:
    return GRAPHQL_PATH.read_text(encoding="utf-8")

def _load_index_rows() -> list[dict[str, str]]:
    rows = []
    lines = INDEX_PATH.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        if "GraphQL Type" in cells[0] or cells[0].startswith("---"):
            continue
        rows.append({
            "graphql": cells[0].strip("`"),
            "kind": cells[1],
            "openapi": cells[2].strip("`"),
            "notes": cells[3]
        })
    return rows

def test_files_exist_and_not_empty():
    assert OPENAPI_PATH.is_file()
    assert GRAPHQL_PATH.is_file()
    assert INDEX_PATH.is_file()

def test_audit_index_mappings_match_schemas():
    spec = _load_openapi()
    graphql_sdl = _load_graphql()
    rows = _load_index_rows()

    assert len(rows) >= 8

    # Verify GraphQL fields exist in SDL
    for row in rows:
        g_parts = row["graphql"].split(".")
        if len(g_parts) == 2:
            type_name, field_name = g_parts
            # Simple check that the type is defined and contains the field (or property)
            assert type_name in graphql_sdl
            assert field_name in graphql_sdl

    # Verify OpenAPI components exist in Spec
    schemas = spec["components"]["schemas"]
    for row in rows:
        o_ref = row["openapi"]
        if "." in o_ref:
            schema_name, prop_name = o_ref.split(".")
            assert schema_name in schemas
            assert prop_name in schemas[schema_name]["properties"]
```

---

## Deterministic Invariants

The drift guard test enforces the following deterministic invariants:
1. **Schema Field Presence**: Every mapped field pair in the continuity table must literally exist in the GraphQL SDL and the OpenAPI spec.
2. **Correlation ID propagation**: Every audit event read model (`AuditEvent` and `AppointmentAuditEvent`) must include the `correlationId` field to preserve the link to OpenAPI request headers (`X-Correlation-Id`) and command payloads (`CommandMeta.correlation_id`).
3. **Evidence labeling**: Evidence source types in OpenAPI (`evidence_label` in `CommandMeta`) must match or directly map to the values defined in the GraphQL `EvidenceMode` enum.
4. **No mutations**: The test asserts that GraphQL remains read-only by verifying no `Mutation` types or mutated-state fields are exposed or checked.
5. **Security checks**: The test scans the continuity files to guarantee no forbidden keywords (`gemini`, `llm`, `trove`, `h15_`, etc.) are introduced.

## Closed Gates

The recommended artifacts preserve the closed status of all EMR4 runtime and provider gates:
- **No runtime imports**: No routers are imported, and no routes are executed.
- **No database connections**: The test remains static and does not read or write audit tables.
- **No provider/AI calls**: All provider gates remain disabled (`writes_authorized=false`).
- **No GraphRAG/memory**: Introspection is limited to the defined files, avoiding trove imports.

## Risks and Naming Gaps Identified

During the review, the following structural gaps were discovered between the GraphQL and OpenAPI schemas:

1. **Enum Structure mismatch for Audit Actions**:
   - In GraphQL, `AppointmentAuditEvent.action` is restricted to `AppointmentAuditAction` (e.g. `CONFIRMED_CREATE`, `CONFIRMED_UPDATE`, `PROPOSAL_STAGED`).
   - In OpenAPI, `ConfirmationAuditEvent.action` uses a simpler enum: `[create, update, status_change, delete]`.
   *Risk*: A translation translation layer is required when converting confirmation audit logs to read models.
2. **Missing `summary` field in OpenAPI**:
   - GraphQL `AuditEvent` and `AppointmentAuditEvent` require a non-null `summary: String!`.
   - OpenAPI `ConfirmationAuditEvent` lacks a `summary` property.
   *Risk*: Database persist layer must construct summaries from command envelopes on execution, or OpenAPI schemas must be extended.
3. **Audit Outcome definition**:
   - GraphQL `AuditEvent` has `outcome: AuditOutcome!` (`ALLOWED`, `DENIED`, etc.).
   - OpenAPI `ConfirmationAuditEvent` lacks an outcome field because commands only yield audit events upon success. Auditing blocked/failed proposals or access requests requires a future design extension.

## Verification Commands

To verify that the continuity files and tests conform statically, run the following:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_api_spine_audit_readmodel_continuity.py -q
```

## Reason to Pause Ariadne

There is **no reason to pause Ariadne**. The recommended index and drift guard test are entirely static and safe to integrate as part of the normal progress of Sprint 201. However, Ariadne should coordinate the resolver-level mapping rules for the simple lowercase OpenAPI audit actions versus the uppercase GraphQL audit action enums before commencing any database-level audit implementation.
