# EMR4 Handover Topic Index

This index routes incoming agents from the compact live `AGENTS.md` to the
right historical and domain evidence. The live handover controls current
authority and boundaries. Closeout documents control accepted sprint results.
The immutable pre-compaction snapshot preserves every earlier handover byte.

| Topic | Current ledger | Primary authority |
|---|---|---|
| Current Baton historical/inactive acceptance lookup | `current-baton-acceptance-index.md` with `current-baton-acceptance-index.manifest.json` | Live `AGENTS.md` for authority; hash-bound ledger for artifact lookup only |
| Bernie language coverage and evaluation | `bernie-language-evaluation.md` | Current LC acceptance and reports |
| Ariadne, workers, receipts, and recovery | `orchestration-and-agent-runtime.md` | Live `AGENTS.md` authority table and Ariadne contracts |
| Historical diary trove and interpretation harness | `historical-diary-and-interpretation.md` | Approved H-series gate payloads and blocked runtime gates |
| Product platform, API Spine, security, and environment | `product-platform-api-and-security.md` | `implementation_plan.md`, API Spine docs, and live source/tests |
| Complete handover history before compaction | `../handover-archive/AGENTS-2026-07-15-pre-compaction.md` | Immutable manifest-verified snapshot |

Historical statements never override a newer live authority allocation,
protected-evidence rule, or explicit user decision.
