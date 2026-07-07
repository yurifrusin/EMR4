# Sprint 194 Review: Contract Tunnel Accounting

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `sprint194-contract-tunnel-accounting-review` |
| Status | review-only |

> This document is a review artifact only. As per Sprint 194 instructions, no
> production code, tests, migrations, or runtime documentation was modified.

## Verdict

Approved with recommendations.

The proposed additive change to
`scripts/appointment_route_inventory_preflight.py` to split out-of-contract rows
into documented and undocumented path/method counts is architecturally sound,
safe, and has zero runtime impact. It adheres to the intended safety boundary:
no network requests, database access, memory/RAG, or provider execution.

## Field And Test Recommendations

Add logic under `uncovered_rows = route_rows - contract_rows`:

```python
documented_path_rows = {
    (method, path) for method, path in uncovered_rows if path in contract_paths
}
undocumented_path_rows = uncovered_rows - documented_path_rows

out_of_contract_documented_paths = {path for _method, path in documented_path_rows}
out_of_contract_undocumented_paths = {path for _method, path in undocumented_path_rows}
```

Add aggregate fields:

```python
"out_of_contract_documented_path_count": len(out_of_contract_documented_paths),
"out_of_contract_documented_path_method_count": len(documented_path_rows),
"out_of_contract_undocumented_path_count": len(out_of_contract_undocumented_paths),
"out_of_contract_undocumented_path_method_count": len(undocumented_path_rows),
"documented_path_out_of_contract_rows_are_grammar_authority": False,
```

Add safety assertions:

```python
assert report["out_of_contract_documented_path_count"] >= 0
assert report["out_of_contract_documented_path_method_count"] >= report["out_of_contract_documented_path_count"]
assert report["out_of_contract_undocumented_path_count"] >= 0
assert report["out_of_contract_undocumented_path_method_count"] >= report["out_of_contract_undocumented_path_count"]
assert report["documented_path_out_of_contract_rows_are_grammar_authority"] is False

assert (
    report["out_of_contract_documented_path_method_count"]
    + report["out_of_contract_undocumented_path_method_count"]
) == report["out_of_contract_route_method_count"]

assert (
    report["out_of_contract_documented_path_count"]
    + report["out_of_contract_undocumented_path_count"]
) == report["out_of_contract_distinct_path_count"]
```

Update `tests/test_appointment_route_inventory_preflight.py` to assert the new
fields exist, add the new boolean to opened-boundary rejection tests, and keep
the report path-free.

## Risks

Path parameter naming divergence can move a row between documented-path and
undocumented-path buckets if FastAPI paths and `DIARY_ACTION_ROUTE_CONTRACTS`
paths drift. The existing `all_contract_paths_mounted` check mitigates this for
covered routes; newly undocumented paths should remain safely reported as
undocumented.

Strict literal path matching can be affected by slash or case changes. That is
acceptable here because the report inspects FastAPI's mounted route strings and
the contract should match those strings deliberately.

## Separation From POST Classification

This structural split should stay separate from out-of-contract POST
classification.

Documented/undocumented path splitting is a coverage hygiene metric.
Out-of-contract POST route classification is a security and authority review of
potential write-capable surfaces. Combining the two would blur the signal and
make future alerts less specific.
