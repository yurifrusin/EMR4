# Bernie UI Derived-State View-Model Contract Cross-Reference

Date: 2026-07-09

Sprint 289 completes the approved Sprint 288-289 non-runtime checkpoint block.
Provide one reviewer-facing map across the D3 inventory, D4 preflight, D5
completion review, evidence consolidation, and API-spine boundary without
adding runtime behavior.

## Map

| Artifact | Role | Reviewer Question |
|---|---|---|
| `docs/bernie-ui-derived-state-dag-d3-inventory.md` | switch-point inventory | Which current Diary/Bernie switch points map to future view-model fields? |
| `docs/bernie-ui-derived-state-dag-d4-preflight.md` | route-intercepted UI preflight | Which UI fixture states and copy/confirm invariants must be preserved before any UI wiring? |
| `docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.json` | completed first-slice boundary | What was completed, and which expansion gates remain closed? |
| `docs/bernie-ui-derived-state-dag-evidence-consolidation.md` | evidence and write-authority summary | Which evidence is route-intercepted, what remains unproven, and why view-model fields are not write authority? |
| `orchestration/api_spine_adr.md` | API-spine boundary | Why may read models expose display hints while REST/OpenAPI commands own writes? |

## Review Use

This packet should let a reviewer answer four questions:

- Can every proposed display flag be traced back to D3 inventory or the D5
  completed response shape?
- Are D4 fixture expectations still route-intercepted rather than live-provider
  evidence?
- Do staff confirmation and appointment writes remain owned by signed REST
  confirm commands?
- Which next steps require separate approval before any runtime expansion?

## Boundary

This packet changes no runtime code. D5 expansion, additional backend response
attachment points, frontend JavaScript expansion, GraphQL delivery/readiness,
provider/live-provider wiring, Access AI, memory/RAG/GraphRAG runtime access,
H15/H-series runtime input, historical diary runtime input, external patient
client exposure, confirm payload or write behavior changes, model-to-database
writes, deployment claims, and production readiness claims remain closed.

## Next Step

Stop after Sprint 289 closeout for Yuri direction. The approved 288-289 block is
complete; any runtime expansion or D5 reopening requires separate approval.
