# Bernie UI Derived-State DAG D5 Router Import Guard Plan

Date: 2026-07-09

Status: approved first slice. The broad production-router import ban has narrowed
only for the reviewed Bernie response-delivery attachment point.

Current guard:
`tests/test_bernie_ui_view_model.py::test_only_approved_bernie_route_imports_selector_after_d5_approval`
asserts that only `app/routers/appointments.py` may import or reference
`app.services.bernie.ui_view_model`.

## Approved D5 First Slice

Do not delete the guard. Keep it as a finer-grained guard that:

- allows only the reviewed Bernie response-delivery attachment point, expected
  to be `app/routers/appointments.py`;
- keeps all non-Bernie production routers blocked from importing
  `app.services.bernie.ui_view_model`;
- keeps `app/routers/bernie_dev.py` blocked unless a separate dev-route review
  explicitly needs display-model delivery;
- asserts that any allowed `appointments.py` import is paired with the approved
  response schema test and no confirm-payload schema change;
- fails if a provider, memory, GraphQL, H15/H-series, historical diary, or
  external patient-client route imports the selector.

## Suggested Future Test Shape

```python
ALLOWED_ROUTE_IMPORTS_AFTER_D5_APPROVAL = {
    Path("app/routers/appointments.py"),
}

def test_only_approved_bernie_route_imports_ui_view_model_after_d5_approval():
    offenders = []
    for path in Path("app/routers").glob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        imports_selector = (
            "app.services.bernie.ui_view_model" in text
            or "build_bernie_ui_view_model" in text
        )
        if imports_selector and path not in ALLOWED_ROUTE_IMPORTS_AFTER_D5_APPROVAL:
            offenders.append(str(path))

    assert offenders == []
```

The test must live alongside response-delivery tests and must cite the approved
D5 gate commit. Any route beyond the reviewed `appointments.py` attachment point
requires a new approval.
