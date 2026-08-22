# Factory fixture failure diagnosis

Date: 2026-08-22

Timestamp: 2026-08-22T19:03:10.320599+10:00 (Australia/Brisbane)

Result: `fixture_import_scope_path_mismatch`

The consumed fixture selected `node_modules` as the package scope, but both required rc.7 imports live under `node_modules/@deepseek-ai`. Both emitted targets were absent and both corrected targets are present. The process therefore stopped before the installed AgentRegistry or runner factory boundary. No raw stderr was read or retained.

This operation permits no retry. Its narrow successor must use `package_root.parent` and fail closed on both import-target existence checks before one separately identified process.
