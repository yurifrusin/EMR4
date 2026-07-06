# H49 Interpretation Harness Contract Review

Date: 2026-07-06

Scope:

- `app/services/bernie/interpretation_harness.py`
- `tests/test_bernie_interpretation_harness.py`
- `tests/fixtures/bernie_interpretation_harness/`

## Boundary Reviewed

The review focused on provider-free projected-frame contracts after H48:

- Dispatch-to-frame invariants.
- Clarify-frame shape.
- Refusal reason kinds.
- Safe copy fragments.
- Fixture-backed contract matrix.

Out of scope: runtime routes, UI, database access, providers, raw diary trove
material, H15/H-series runtime use, RAG, GraphRAG, and memory persistence.

## Finding

Malformed external-style frames with an unknown `interpretation_dispatch` raised
`ValueError` through the enum constructor rather than the harness's assertion
contract. That did not grant authority or permit writes, but it made negative
contract failures less uniform for future callers/tests.

## Fix

`assert_interpretation_frame_consistency()` now converts unknown dispatch values
into `AssertionError`, matching the rest of the invariant API. A regression case
was added to the drifted-frame test matrix.

## Residual Risk

The harness remains deterministic and authored-fixture-only. It is not a parser
for arbitrary receptionist free text and is not a live provider validator. Live
provider or route wiring still needs separate gates and no-write dry-run proof.
