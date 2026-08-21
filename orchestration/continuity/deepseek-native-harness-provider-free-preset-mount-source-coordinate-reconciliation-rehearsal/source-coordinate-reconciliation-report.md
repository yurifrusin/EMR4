# Native Harness preset-mount source-coordinate reconciliation report

Date: 2026-08-22

Timestamp: 2026-08-22T04:49:02.031481+10:00 (Australia/Brisbane)

Candidate source: `2c0e24e6b59263129ec59e948f17a18203015b67`

Result: **pass**

The accepted terminal remains
`EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED`. Eight exact rc.7 source and
manifest bindings pass. The two preset rows require `tools`, `fs`,
`systemPrompt` and `subprocess`; the pinned host composition declares all four.

The source-reachable internal candidate set is:

- `PRESET_MOUNT_AGENT_SCOPE_ABSENT`
- `PRESET_MOUNT_COMPOSITION_STAMP_UNREADABLE`
- `PRESET_MOUNT_ROW_IMPORT_OR_APPLY_REJECTED`
- `PRESET_MOUNT_SUBTREE_PUBLICATION_ABSENT`
- `PRESET_MOUNT_ROW_INACTIVE_AFTER_AWAIT`
- `PRESET_MOUNT_ROOT_SERVICE_LEAK`

This is a finite static candidate set, not an observed internal runtime
coordinate. No raw error was recovered, no repair was selected, and no native
Harness process, turn, request, provider, target or product action occurred.
