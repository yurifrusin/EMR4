# EMR4 Handover Archive

This directory preserves immutable historical snapshots of the live root
`AGENTS.md`. A snapshot is evidence, not the current operating instruction.
Incoming agents must read the live handover first and consult an archive only
through the live topic index or when reconstructing historical provenance.

## Snapshots

| Date | Snapshot | Manifest | Purpose |
|---|---|---|---|
| 2026-07-15 | `AGENTS-2026-07-15-pre-compaction.md` | `AGENTS-2026-07-15-pre-compaction.manifest.json` | Complete byte-identical record immediately before the first handover compaction |

Do not edit an archived snapshot or its manifest. Corrections belong in a new
snapshot, a new manifest, or the live handover.
